import datetime
from bs4 import BeautifulSoup

import frappe
from frappe import _
from frappe.model.document import Document

from ..apis.api_builder import OBRAPI

# from ..api_classes.base import OBRAPIBase
# from ..utils.background_jobs import enqueue_retry_posting_sales_invoice
# from ..data.sale_invoice_data import InvoiceDataProcessor
from ..apis.utils.utils import get_urls
from ..apis.utils.build_headers import build_headers
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..apis.utils.build_invoice_payload import build_invoice_payload
from ..handlers.sales_invoice import (
    handle_sales_invoice_submission,
    handle_sales_invoice_cancellation,
)


obr_api = OBRAPI()


def on_submit_invoice(doc: Document, method: str | None = None) -> None:
    if doc.is_opening == "Yes":
        return

    if doc.doctype == "Sales Invoice" and doc.is_consolidated:
        return

    if doc.custom_submitted_to_obr:
        return

    generic_invoice_on_submit_override(doc, doc.doctype)


def generic_invoice_on_submit_override(doc: Document, invoice_type: str):
    company_name = doc.company
    settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company_name)

    if not settings_doc.is_active:
        return

    if not settings_doc.allow_obr_to_track_sales:
        return

    posting_date, start_date = doc.posting_date, settings_doc.start_date
    if isinstance(posting_date, str):
        posting_date = datetime.datetime.strptime(posting_date, "%Y-%m-%d").date()

    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

    if posting_date < start_date:
        return

    environment = "sandbox" if settings_doc.sandbox else "production"
    headers = build_headers(company_name)

    request_url, server_url = get_urls(environment, "add_invoice")

    if headers and server_url and request_url:
        url = f"{server_url}/{request_url}"
        payload = build_invoice_payload(doc, settings_doc)

        obr_api.headers = headers
        obr_api.url = url
        obr_api.method = "POST"
        obr_api.payload = payload
        obr_api.service = "AddCreditNote" if doc.is_return else "AddInvoice"
        obr_api.success_callback_handler = handle_sales_invoice_submission
        # obr_api.error_callback_handler = handler

        frappe.enqueue(
            obr_api.make_remote_request,
            is_async=True,
            queue="default",
            timeout=600,
            job_name=f"obr_invoice_submission_{doc.name}",
            doctype=invoice_type,
            document_name=doc.name,
        )


def on_cancel(doc: Document, method: str | None = None) -> None:
    company_name = doc.company
    settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company_name)

    if not settings_doc.is_active:
        return

    posting_date, start_date = doc.posting_date, settings_doc.start_date

    if isinstance(posting_date, str):
        posting_date = datetime.datetime.strptime(doc.posting_date, "%Y-%m-%d").date()

    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

    if posting_date < start_date:
        return

    if not doc.custom_submitted_to_obr:
        return

    if not doc.custom_reason_for_creditcancel:
        frappe.throw(
            _(
                "Please provide a reason for invoice cancellation before cancelling the invoice."
            )
        )

    soup = BeautifulSoup(doc.custom_reason_for_creditcancel, "html.parser")
    ct_motif = soup.get_text()

    invoice_identifier = doc.custom_invoice_identifier
    if not invoice_identifier:
        return
    invoice_data = {
        "invoice_signature": f"{invoice_identifier}",
        "cn_motif": ct_motif,
    }

    environment = "sandbox" if settings_doc.sandbox else "production"
    headers = build_headers(company_name)

    request_url, server_url = get_urls(environment, "cancel_invoice")

    if headers and server_url and request_url:
        url = f"{server_url}/{request_url}"
        payload = invoice_data

        obr_api.headers = headers
        obr_api.url = url
        obr_api.method = "POST"
        obr_api.payload = payload
        obr_api.service = "CancelInvoice"
        obr_api.success_callback_handler = handle_sales_invoice_cancellation
        # obr_api.error_callback_handler = handler

        frappe.enqueue(
            obr_api.make_remote_request,
            is_async=True,
            queue="default",
            timeout=600,
            job_name=f"obr_invoice_cancellation_{doc.name}",
            doctype=doc.doctype,
            document_name=doc.name,
        )


def handler(response, document_name, doctype):
    pass


def before_save(doc: Document, method: str | None = None) -> None:
    if doc.is_return:
        data_to_update = {
            "custom_einvoice_signatures": "",
            "custom_invoice_registered_no": "",
            "custom_invoice_registered_date": "",
            "custom_submitted_to_obr": 0,
        }

        frappe.db.set_value(doc.doctype, doc.name, data_to_update)
        frappe.db.commit()
