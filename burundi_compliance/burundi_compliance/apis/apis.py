import datetime
import json

import frappe
from frappe import _

from ..apis.api_builder import OBRAPI
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..utils.build_headers import build_headers
from ..utils.utils import get_urls
from ..background_tasks.tasks import send_stock_movement_to_obr


@frappe.whitelist()
def get_invoice_from_obr(name: str, invoice_type: str):
	si_doc = frappe.get_doc(invoice_type, name)
	if si_doc.is_opening == "Yes":
		return

	if si_doc.doctype == "Sales Invoice" and si_doc.is_consolidated:
		return

	company_name = si_doc.company
	if not frappe.db.exists(SETTINGS_DOCTYPE_NAME, company_name):
		frappe.throw(
			_(
				f"eBMS Settings not found for company {company_name}. Please set up the settings to fetch invoice details from OBR."
			),
			title=_("Settings Not Found"),
		)

	settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company_name)

	if not settings_doc.is_active:
		frappe.throw(
			_(f"Please activate eBMS Settings for company {company_name}"),
			title=_("Integration Inactive"),
		)

	posting_date, start_date = si_doc.posting_date, settings_doc.start_date

	if isinstance(posting_date, str):
		posting_date = datetime.datetime.strptime(posting_date, "%Y-%m-%d").date()

	if isinstance(start_date, str):
		start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

	if posting_date < start_date:
		return

	environment = "sandbox" if settings_doc.sandbox else "production"
	headers = build_headers(company_name)

	request_url, server_url = get_urls(environment, "get_invoice")
	if headers and server_url and request_url:
		payload = {"invoice_identifier": si_doc.custom_invoice_identifier}
		url = f"{server_url}/{request_url}"
		obr_api = OBRAPI()
		obr_api.headers = headers
		obr_api.url = url
		obr_api.method = "POST"
		obr_api.payload = payload
		obr_api.service = "GetInvoice"
		response = obr_api.make_remote_request(
			si_doc.doctype, si_doc.name, require_handler=False
		)
		frappe.log_error("Get Invoice from OBR Response", response)
		return response


@frappe.whitelist()
def resubmit_invoice_to_obr(name: str, invoice_type: str):
	doc = frappe.get_doc(invoice_type, name)
	from ..overrides.sales_invoice import on_submit_invoice

	on_submit_invoice(doc, method=None)


@frappe.whitelist()
def bulk_submit_invoices_to_obr(doctype: str, invoice_list: str) -> None:
	invoice_list = json.loads(invoice_list)

	for invoice in invoice_list:
		try:
			from ..overrides.sales_invoice import on_submit_invoice

			doc = frappe.get_doc(doctype, invoice)
			if (
				doc.custom_submitted_to_obr or doc.docstatus != 1
			):  # Lock out draft and cancelled invoices
				continue

			on_submit_invoice(doc, method=None)
		except Exception as e:
			frappe.log_error(
				message=str(e),
				title=_("Error Submitting Invoice to OBR: {0}").format(invoice),
			)
			continue


@frappe.whitelist()
def cancel_invoice_in_obr(name: str, invoice_type: str):
	doc = frappe.get_doc(invoice_type, name)
	from ..overrides.sales_invoice import on_cancel

	on_cancel(doc, method=None)


@frappe.whitelist()
def trigger_stock_movement_to_obr() -> None:
	send_stock_movement_to_obr()


@frappe.whitelist()
def confirm_tin(company: str, tin: str, doctype: str, docname: str):
	if not company or not tin:
		frappe.throw(_("Company and TIN must be provided"), title=_("Missing Information"))

	if not frappe.db.exists(SETTINGS_DOCTYPE_NAME, company):
		frappe.throw(
			_(
				f"eBMS settings not found for company {company}. Please set up the settings to check TIN with OBR."
			),
			title=_("Settings Not Found"),
		)

	settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company)

	if not settings_doc.is_active:
		frappe.throw(
			_(f"Please activate eBMS settings for company {company}"),
			title=_("Integration Inactive"),
		)

	posting_date, start_date = frappe.utils.getdate(), settings_doc.start_date

	if isinstance(posting_date, str):
		posting_date = datetime.datetime.strptime(posting_date, "%Y-%m-%d").date()

	if isinstance(start_date, str):
		start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

	if posting_date < start_date:
		frappe.throw(
			_(f"Current date is before the start date for OBR integration: {start_date}"),
			title=_("Invalid Start Date"),
		)
		return

	environment = "sandbox" if settings_doc.sandbox else "production"
	headers = build_headers(company)

	request_url, server_url = get_urls(environment, "check_TIN")
	if headers and server_url and request_url:
		payload = {"tp_TIN": tin}
		url = f"{server_url}/{request_url}"
		obr_api = OBRAPI()
		obr_api.headers = headers
		obr_api.url = url
		obr_api.method = "POST"
		obr_api.payload = payload
		obr_api.service = "CheckTIN"
		response = obr_api.make_remote_request(doctype, docname, require_handler=False)

		if response and response.get("success") and doctype == "Customer":
			frappe.db.set_value(
				doctype, docname, "custom_tin_verified", True, update_modified=False
			)

		return response

	return None
