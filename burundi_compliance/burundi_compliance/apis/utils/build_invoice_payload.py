from bs4 import BeautifulSoup


import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data

from ...utils.format_date_and_time import date_time_format
from ...utils.invoice_signature import create_invoice_signature


def build_invoice_payload(doc: Document, settings_doc: Document) -> dict:
	company = frappe.get_doc("Company", doc.company)
	company_address = get_company_address_details(doc)
	company_tax_id = company.tax_id
	tp_phone_no = company.phone_no
	tp_email = company.email
	formatted_date_data = date_time_format(doc)
	invoice_signature = create_invoice_signature(
		doc, settings_doc.system_identification_given_by_obr
	)

	frappe.db.set_value(
		doc.doctype,
		doc.name,
		"custom_invoice_identifier",
		invoice_signature,
		update_modified=False,
	)

	confirm_tin_verified(doc.customer)
	if doc.doctype == "POS Invoice":
		exempt_from_sales_tax = 0
	else:
		exempt_from_sales_tax = doc.exempt_from_sales_tax

	invoice_data = {
		"invoice_number": doc.name,
		"invoice_date": formatted_date_data[0],
		"invoice_type": "FN",
		"tp_type": (1 if settings_doc.type_of_taxpayer == "pour personne physique et" else 2),
		"tp_name": doc.company,
		"tp_TIN": company_tax_id,
		"tp_address_province": company_address.get("tp_address_province"),
		"tp_phone_number": tp_phone_no,
		"tp_address_commune": company_address.get("tp_address_commune"),
		"tp_address_avenue": company_address.get("tp_address_avenue"),
		"tp_address_quartier": company_address.get("tp_address_quartier"),
		"tp_address_rue": company_address.get("tp_address_rue"),
		"tp_address_number": company_address.get("tp_address_number"),
		"tp_trade_number": settings_doc.the_taxpayers_commercial_register_number,
		"tp_email": tp_email,
		"vat_taxpayer": (
			0 if settings_doc.subject_to_vat == "pour un non assujetti ou" else 1
		),
		"ct_taxpayer": (
			0 if settings_doc.subject_to_consumption_tax == "pour un non assujetti ou" else 1
		),
		"tl_taxpayer": (
			0
			if settings_doc.subject_to_flatrate_withholding_tax == "pour un non assujetti ou"
			else 1
		),
		"tp_fiscal_center": settings_doc.the_taxpayers_tax_center,
		"tp_activity_sector": settings_doc.taxpayers_sector_of_activity,
		"tp_legal_form": settings_doc.taxpayers_legal_form,
		"payment_type": get_payment_method(doc.custom_payment_types),
		"invoice_currency": doc.currency,
		"customer_name": doc.customer_name,
		"customer_TIN": doc.tax_id if doc.tax_id else "",
		"customer_address": doc.customer_address if doc.customer_address else "",
		"vat_customer_payer": exempt_from_sales_tax,
		"invoice_ref": "",
		"cn_motif": "",
		"invoice_identifier": invoice_signature,
		"invoice_items": get_invoice_items(doc),
	}

	if doc.is_return:
		if not doc.custom_reason_for_creditcancel:
			frappe.throw(
				_(
					"Please provide a reason for credit note in the 'Reason for Credit/Cancellation' field."
				)
			)

		soup = BeautifulSoup(doc.custom_reason_for_creditcancel, "html.parser")
		ct_motif = soup.get_text()
		invoice_data.update(
			{
				"invoice_ref": doc.return_against,
				"cn_motif": ct_motif,
				"invoice_type": "FA",
			}
		)

	return invoice_data


def get_company_address_details(doc: Document) -> dict:
	address_details = {}
	links = frappe.get_all(
		"Dynamic Link",
		filters={
			"link_doctype": "Company",
			"link_name": doc.company,
			"parenttype": "Address",
		},
		fields=["parent"],
	)
	if links:
		address = frappe.get_doc("Address", links[0].parent)
		address_details = {
			"tp_address_province": address.state,
			"tp_address_commune": address.custom_commune,
			"tp_address_quartier": address.custom_quartier,
			"tp_address_avenue": address.custom_avenue,
			"tp_address_rue": address.custom_rue,
			"tp_address_number": address.custom_numero,
		}
	return address_details


def confirm_tin_verified(customer: str):
	customer = frappe.get_doc("Customer", customer)

	if customer.custom_gst_category == "Registered":
		if not customer.custom_tin_verified:
			frappe.throw(
				"Please Verify the TIN number of this customer on <b>Customer</b> doctype"
			)
			frappe.log_error(
				"TIN Verification Error",
				f"TIN number for customer {customer.name} is not verified.",
			)


def get_payment_method(payment_type: str) -> str:
	if payment_type == "Bank":
		return "2"
	elif payment_type == "Cash":
		return "1"
	elif payment_type == "Credit":
		return "3"
	else:
		return "4"


def get_invoice_items(doc):
	items = []
	itemised_tax_data = get_itemised_tax_breakup_data(doc)

	for item in doc.items:
		tax_data = next(
			(data for data in itemised_tax_data if data["item"] == item.item_code),
			None,
		)
		total_vat = 0

		if tax_data:
			# Check if VAT exists, if not, check for other tax details
			if "VAT" in tax_data:
				total_vat = tax_data["VAT"]["tax_amount"]
			else:
				total_vat = 0
		else:
			total_vat = 0
		item_designation = (
			item.item_code + "-" + item.batch_no if item.batch_no else item.item_code
		)
		items.append(
			{
				"item_code": item.item_code,
				"item_designation": item_designation,
				"item_quantity": abs(item.qty),
				"item_price": item.rate,
				"item_total_amount": item.amount,
				"vat": abs(int(total_vat)),
				"item_ct": "0",
				"item_tl": "0",
				"item_price_nvat": abs(int(item.amount)),
				"item_price_wvat": abs(int(item.amount + total_vat)),
			}
		)
	return items
