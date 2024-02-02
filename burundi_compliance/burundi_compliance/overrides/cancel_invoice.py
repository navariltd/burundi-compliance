
import frappe
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from burundi_compliance.burundi_compliance.api_classes.cancel_invoice import InvoiceCanceller
from burundi_compliance.burundi_compliance.data.cancel_invoice_data import get_invoice_data

def cancel_invoice(doc, method=None):
    obr_base = OBRAPIBase()
    #token = obr_base.authenticate()
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJveSIsImV4cCI6MTU4MjYyMDY1OX0.EMTwnke-M5PXV3LEEUveZLcvvi7pQmGUbWMAj2KeR94"
    invoice_data = get_invoice_data(doc)
    if invoice_data:
        frappe.msgprint(f"Cancelling invoice {invoice_data}")
    invoice_canceller = InvoiceCanceller(token)
    response = invoice_canceller.cancel_invoice(invoice_data)
    frappe.msgprint(response)