
from ..api_classes.base import OBRAPIBase
import requests

base_data=OBRAPIBase().get_auth_details()
import frappe
from ..utils.invoice_signature import create_invoice_signature


def get_invoice_data(doc):
    name = doc.name

    ct_motif = doc.get("custom_reason_for_creditcancel")
    if not ct_motif:
        frappe.throw(f"Unable to cancel invoice.\n Kindly set the Reason For Cancelling the Invoice for {name} invoice")

    # Fetch signature created
    invoice_signature = create_invoice_signature(doc)

    if not invoice_signature:
        return None

    data = {
       # "invoice_signature": invoice_signature,
       "invoice_signature":f'4001040247/ws400104024700648/20211206073022/{doc.name}',
        "cn_motif": ct_motif
    }

    return data
