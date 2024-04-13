
from ..api_classes.base import OBRAPIBase

base_data=OBRAPIBase().get_auth_details()
from bs4 import BeautifulSoup
import frappe

def get_invoice_data(doc):
    name = doc.name

    ct_motif = doc.custom_reason_for_creditcancel
    if not ct_motif:
        frappe.throw(f"Unable to cancel invoice.\n Kindly set the Reason For Cancelling the Invoice for {name} invoice")
    soup = BeautifulSoup(ct_motif, 'html.parser')
    ct_motif = soup.get_text()
    # Fetch signature created
    invoice_identifier= doc.custom_invoice_identifier

    if not invoice_identifier:
        return None

    data = {
       "invoice_signature":f'{invoice_identifier}',
        "cn_motif": ct_motif
    }

    return data

