from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe

from frappe import _
from frappe.model.document import Document
from ..data.delivery_note import get_delivery_note_items

obr_integration_base = OBRAPIBase()
auth_details=obr_integration_base.get_auth_details()


def get_items(doc):
    token = obr_integration_base.authenticate()
    items_data = get_delivery_note_items(doc)
    
    for item in items_data:
            try:
                track_stock_movement = TrackStockMovement(token)
                result = track_stock_movement.post_stock_movement(item)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        

def on_submit_update_stock(doc, method=None):
    try:
        get_items(doc)
        frappe.msgprint("The transaction was added successfully!")
    except Exception as e:
        frappe.msgprint(f"Error during submission: {str(e)}")
        
    
