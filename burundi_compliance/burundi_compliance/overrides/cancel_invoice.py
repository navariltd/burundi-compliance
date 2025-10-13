import frappe
from frappe import _
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase

from burundi_compliance.burundi_compliance.data.cancel_invoice_data import (
    get_invoice_data,
)
from burundi_compliance.burundi_compliance.utils.background_jobs import (
    enqueue_cancel_invoice,
)


import datetime

base = OBRAPIBase()
auth_details = base.get_auth_details()


def cancel_invoice(doc, method=None):
    posting_date = doc.posting_date
    start_date = auth_details.get("start_date")

    if isinstance(posting_date, str):
        posting_date = datetime.datetime.strptime(doc.posting_date, "%Y-%m-%d").date()

    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

    if posting_date < start_date:
        return

    if not doc.custom_submitted_to_obr:
        return

    invoice_data = get_invoice_data(doc)
    base.authenticate()

    enqueue_cancel_invoice(invoice_data, doc)
    frappe.msgprint(_("Invoice cancellation job queued successfully!"), alert=True)
