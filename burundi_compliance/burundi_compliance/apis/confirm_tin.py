import datetime


import frappe
from frappe import _

from ..apis.api_builder import OBRAPI
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..utils.build_headers import build_headers
from ..utils.utils import get_urls


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
