from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from ..data.sale_invoice_data import prepare_invoice_data, get_sales_return_items


from frappe import _
from frappe.model.document import Document

obr_integration_base = OBRAPIBase()
auth_details=obr_integration_base.get_auth_details()


def on_submit(doc, method=None):
    
    #token = obr_integration_base.authenticate()
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJveSIsImV4cCI6MTU4MjYyMDY1OX0.EMTwnke-M5PXV3LEEUveZLcvvi7pQmGUbWMAj2KeR94"
    obr_invoice_poster = SalesInvoicePoster(token)  # Implement get_obr_token() to obtain the OBR token
    
    post_sales_return=TrackStockMovement(token)
    if doc.is_return:
        invoice_reference_number = doc.return_against
        invoice_data = prepare_invoice_data(doc, is_credit_note=True, credit_note_reference=invoice_reference_number)
    else:
        invoice_data = prepare_invoice_data(doc)
    
    # if doc.is_return and doc.update_stock:
    #     sales_return_data = get_sales_return_items(doc)
    #     frappe.msgprint(f"Sa;les returns data: {sales_return_data}")
    #     update_stock_result= post_sales_return.post_stock_movement(doc)       

    result = obr_invoice_poster.post_invoice(invoice_data)
    
    frappe.msgprint(f"Invoice data sent to OBR. Result: {result}")
    
