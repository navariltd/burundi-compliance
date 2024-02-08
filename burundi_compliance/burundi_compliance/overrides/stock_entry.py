
from ..api_classes.add_stock_movement import TrackStockMovement
from ..data.stock_entry_data import get_stock_entry_items
from ..api_classes.base import OBRAPIBase
import frappe

from datetime import datetime

auth_base = OBRAPIBase()

def on_submit(doc, method=None):
    token = auth_base.authenticate()
    
    track_stock_movement = TrackStockMovement(token)
    items_data = get_stock_entry_items(doc)
    frappe.throw(f"items_data: {items_data}")
    results = track_stock_movement.post_stock_movement(items_data)
    frappe.msgprint("Stock Entry items added to stock successfully")
