from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from ..utils.invoice_signature import create_invoice_signature
from ..data.sale_invoice_data import InvoiceDataProcessor
from frappe import _
from frappe.model.document import Document
from ..data.purchase_invoice_data import get_purchase_data_for_stock_update
from ..utils.background_jobs import enqueue_stock_movement
obr_integration_base = OBRAPIBase()
auth_details=obr_integration_base.get_auth_details()


def get_items(doc, movement_type="EN"):
    token = obr_integration_base.authenticate()
    items_data = get_purchase_data_for_stock_update(doc, movement_type=movement_type)
    if items_data:
        frappe.throw(str(items_data))
        for item in items_data:
                try:
                
                    enqueue_stock_movement(item)
                    frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully")
                except Exception as e:
                    frappe.msgprint(f"Error sending item {item}: {str(e)}")

def on_submit_update_stock(doc, method=None):
    if doc.update_stock==1:
        try:
            get_items(doc)
        except Exception as e:
            frappe.msgprint(f"Error during submission: {str(e)}")
            
def on_cancel_update_stock(doc, method=None):
    if doc.update_stock==1:
        try:
            get_items(doc, movement_type="SAU")
        except Exception as e:
            frappe.msgprint(f"Error during cancellation: {str(e)}")
