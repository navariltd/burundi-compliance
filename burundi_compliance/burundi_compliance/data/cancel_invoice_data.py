
from ..api_classes.base import OBRAPIBase
import requests

base_data=OBRAPIBase().get_auth_details()
import frappe
from ..utils.invoice_signature import create_invoice_signature


def get_invoice_data(doc):
    name = doc.name

    ct_motif = doc.custom_reason_for_creditcancel
    if not ct_motif:
        frappe.throw(f"Unable to cancel invoice.\n Kindly set the Reason For Cancelling the Invoice for {name} invoice")

    # Fetch signature created
    invoice_identifier= doc.custom_invoice_identifier

    if not invoice_identifier:
        return None

    data = {
       # "invoice_signature": invoice_signature,
       "invoice_signature":f'{invoice_identifier}',
        "cn_motif": ct_motif
    }

    return data

