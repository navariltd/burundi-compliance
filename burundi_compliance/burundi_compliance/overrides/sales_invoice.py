from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from ..data.sale_invoice_data import prepare_invoice_data


from frappe import _
from frappe.model.document import Document

obr_integration_base = OBRAPIBase()
auth_details=obr_integration_base.get_auth_details()


def on_submit(doc, method=None):
    
    #token = obr_integration_base.authenticate()
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJveSIsImV4cCI6MTU4MjYyMDY1OX0.EMTwnke-M5PXV3LEEUveZLcvvi7pQmGUbWMAj2KeR94"
    obr_invoice_poster = SalesInvoicePoster(token)  # Implement get_obr_token() to obtain the OBR token
    invoice_data = prepare_invoice_data(doc)
    result = obr_invoice_poster.post_invoice(invoice_data)
    
    frappe.msgprint(f"Invoice data sent to OBR. Result: {result}")
    
