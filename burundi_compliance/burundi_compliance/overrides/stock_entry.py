
from ..api_classes.add_stock_movement import TrackStockMovement
from ..data.stock_entry_data import get_stock_entry_items
from ..api_classes.base import OBRAPIBase
import frappe

from ..utils.get_stock_update_permission import get_stock_update_permissions
from datetime import datetime

auth_base = OBRAPIBase()

stock_update=get_stock_update_permissions()
stock_permission=stock_update["allow_obr_to_track_all_stock_entries"]

def get_items(doc):
    token = auth_base.authenticate()
    data = get_stock_entry_items(doc)
    

    for item in data:
            try:
                track_stock_movement = TrackStockMovement(token)
                result = track_stock_movement.post_stock_movement(item)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        

def on_submit(doc, method=None):
    if stock_permission==1 or doc.custom_allow_obr_to_track_stock_movement or doc.stock_entry_type=="Manufacture":
        get_items(doc)
        frappe.msgprint("The transaction was added successfully!")
        
