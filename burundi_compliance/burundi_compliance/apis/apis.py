import datetime

import frappe
from frappe import _

from ..apis.api_builder import OBRAPI
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..apis.utils.build_headers import build_headers
from ..apis.utils.utils import get_urls


@frappe.whitelist()
def get_invoice_from_obr(name: str, invoice_type: str):
    si_doc = frappe.get_doc(invoice_type, name)
    if si_doc.is_opening == "Yes":
        return

    if si_doc.doctype == "Sales Invoice" and si_doc.is_consolidated:
        return

    company_name = si_doc.company
    settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company_name)

    if not settings_doc.is_active:
        return

    posting_date, start_date = si_doc.posting_date, settings_doc.start_date

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
        return response


@frappe.whitelist()
def resubmit_invoice_to_obr(name: str, invoice_type: str):
    doc = frappe.get_doc(invoice_type, name)
    from ..overrides.sales_invoice import on_submit_invoice

    on_submit_invoice(doc, method=None)
