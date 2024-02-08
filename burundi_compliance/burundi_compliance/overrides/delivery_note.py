from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from ..data.delivery_note import get_delivery_note_items


from frappe import _
from frappe.model.document import Document

obr_integration_base = OBRAPIBase()



def on_submit(doc, method=None):
    
    token = obr_integration_base.authenticate()
    post_stock_class=TrackStockMovement(token)
    data=get_delivery_note_items(doc)
    result = post_stock_class.post_stock_movement(data)
    frappe.msgprint(f"Items tracked by OBR successfully")
    
    
    
