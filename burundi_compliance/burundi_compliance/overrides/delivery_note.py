from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from ..data.sale_invoice_data import prepare_invoice_data, get_sales_return_items
from ..data.delivery_note import get_delivery_note_items


from frappe import _
from frappe.model.document import Document

obr_integration_base = OBRAPIBase()



def on_submit(doc, method=None):
    
    #token = obr_integration_base.authenticate()
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJveSIsImV4cCI6MTU4MjYyMDY1OX0.EMTwnke-M5PXV3LEEUveZLcvvi7pQmGUbWMAj2KeR94"
    post_stock_class=TrackStockMovement(token)
    data=get_delivery_note_items(doc)
    if data:
        frappe.msgprint(f"Data is going great: {data}")
    result = post_stock_class.post_stock_movement(data)
    
    frappe.msgprint(f"Invoice data sent to OBR. Result: {result}")
    
