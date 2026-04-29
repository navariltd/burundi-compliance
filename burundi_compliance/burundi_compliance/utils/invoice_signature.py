import frappe

from .format_date_and_time import date_time_format


def create_invoice_signature(doc, system_identification):
	company_tax_id = frappe.get_value("Company", doc.company, "tax_id")
	if company_tax_id is None:
		frappe.throw(
			"Taxpayer Identification Number (TIN) is not available.\n Kindly set that in Company Settings"
		)

	formatted_date = date_time_format(doc)
	identity_date = formatted_date[1]
	invoice_number = doc.name
	if not system_identification:
		frappe.throw(
			"System identification number is not available. Unable to create invoice signature.\n Kindly set that in EBMS Settings"
		)
	invoice_signature = (
		f"{company_tax_id}/{system_identification}/{identity_date}/{invoice_number}"
	)
	return invoice_signature
