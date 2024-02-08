from ..api_classes.add_stock_movement import TrackStockMovement
from ..data.stock_reconciliation_data import get_stock_reconciliation_items
import frappe
from ..api_classes.base import OBRAPIBase
# Import necessary modules
from datetime import datetime
from ..utils.system_tax_id import get_system_tax_id

auth_base=OBRAPIBase()
def on_submit(doc, method=None):
    
    token=auth_base.authenticate()
    
    track_stock_movement = TrackStockMovement(token)
    items_data = get_stock_reconciliation_items(doc)

    results = track_stock_movement.post_stock_movement(items_data)

    # Display success message
    frappe.msgprint("Stock Reconciliation items added to stock successfully, tracked by OBR")
