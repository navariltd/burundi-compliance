from ..api_classes.add_stock_movement import TrackStockMovement
from ..data.stock_reconciliation_data import get_stock_reconciliation_items
import frappe
from ..api_classes.base import OBRAPIBase
from ..utils.background_jobs import enqueue_stock_movement
from datetime import datetime
from ..utils.system_tax_id import get_system_tax_id

auth_base=OBRAPIBase()

def get_items(doc):
    items_data = get_stock_reconciliation_items(doc)
    if items_data:
        for item in items_data:
                try:
                    auth_base.authenticate()
                    enqueue_stock_movement(item, doc)
                    frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully", alert=True)
                except Exception as e:
                    frappe.msgprint(f"Error sending item {item}: {str(e)}")
        
def on_submit(doc, method=None):
    try:
        get_items(doc)
    except Exception as e:
        frappe.msgprint(f"Error during submission: {str(e)}")
