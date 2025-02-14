from ..api_classes.base import OBRAPIBase
from ..utils.background_jobs import enqueue_retry_posting_sales_invoice
import frappe
from ..data.sale_invoice_data import InvoiceDataProcessor
from frappe import _
from ..utils.background_jobs import enqueue_stock_movement
from burundi_compliance.burundi_compliance.utils.get_stock_items import get_items

import datetime

obr_integration_base = OBRAPIBase()

auth_details = obr_integration_base.get_auth_details()
allow_obr_to_track_sales = auth_details["allow_obr_to_track_sales"]
allow_obr_to_track_stock_movement = auth_details["allow_obr_to_track_stock_movement"]


def on_submit(doc, method=None):
    obr_integration_base.authenticate()

    if doc.doctype == "Sales Invoice" and doc.is_consolidated == 0:
        submit_invoice_request(doc)
    elif doc.doctype == "POS Invoice":
        submit_invoice_request(doc)

    doc.submit()
    doc.reload()


def submit_invoice_request(doc):
    posting_date = doc.posting_date
    start_date = auth_details.get("start_date")

    if isinstance(posting_date, str):
        posting_date = datetime.datetime.strptime(doc.posting_date, "%Y-%m-%d").date()

    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

    if posting_date < start_date:
        return

    if allow_obr_to_track_sales == 1:
        sales_invoice_data_processor = InvoiceDataProcessor(doc)

        invoice_data = sales_invoice_data_processor.prepare_invoice_data()

        if doc.is_return:
            invoice_data = sales_invoice_data_processor.prepare_credit_note_data(
                invoice_data
            )

            if doc.custom_creating_payment_entry == 1:
                invoice_data = (
                    sales_invoice_data_processor.prepare_reimbursement_deposit_data(
                        invoice_data
                    )
                )
        # Enqueue background job to send invoice data to OBR
        if doc.custom_differ_submission_to_obr == 0:
            job_id = enqueue_retry_posting_sales_invoice(invoice_data, doc)
            if job_id:
                frappe.msgprint(f"Sending data to OBR. Job queued", alert=True)
            else:
                frappe.msgprint("Job enqueue failed.")
