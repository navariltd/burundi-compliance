
from ..api_classes.base import OBRAPIBase
import requests

base_data=OBRAPIBase().get_auth_details()
import frappe
from ..utils.invoice_signature import create_invoice_signature

def get_invoice_data(doc):
    
    doc = frappe.get_doc("Sales Invoice", doc)
    name=doc.name
    frappe.msgprint(doc)
    ct_motif=doc.get("custom_reason_for_cancel")
    if ct_motif is None:
        frappe.msgprint(f"Unable to cancel invoice.\n Kindly set the Reason For Cancelling the Invoice the {name} invoice")
        
        '''fetch signature created'''
    invoice_signature=create_invoice_signature(doc)
    if invoice_signature:
        frappe.msgprint(invoice_signature)
    if not invoice_signature:
        return None
    data={
        "invoice_signature": invoice_signature,
        "cn_motif": ct_motif
    }
        
    return data

