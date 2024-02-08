
import frappe
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from burundi_compliance.burundi_compliance.api_classes.cancel_invoice import InvoiceCanceller
from burundi_compliance.burundi_compliance.data.cancel_invoice_data import get_invoice_data

def cancel_invoice(doc, method=None):
    obr_base = OBRAPIBase()
    token = obr_base.authenticate()
    invoice_data = get_invoice_data(doc)
    
    if invoice_data:
        frappe.msgprint(f"Cancelling invoice {invoice_data}")
    invoice_canceller = InvoiceCanceller(token)
    response = invoice_canceller.cancel_invoice(invoice_data)
    frappe.msgprint(response)
    
    