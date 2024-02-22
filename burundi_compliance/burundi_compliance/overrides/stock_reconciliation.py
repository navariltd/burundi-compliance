from ..api_classes.add_stock_movement import TrackStockMovement
from ..data.stock_reconciliation_data import get_stock_reconciliation_items
import frappe
from ..api_classes.base import OBRAPIBase
from ..utils.get_stock_update_permission import get_stock_update_permissions
# Import necessary modules
from datetime import datetime
from ..utils.system_tax_id import get_system_tax_id

auth_base=OBRAPIBase()
token=auth_base.authenticate()

stock_update=get_stock_update_permissions()
stock_permission=stock_update["allow_obr_to_track_all_stock_reconciliation"]
def get_items(doc):
    
    items_data = get_stock_reconciliation_items(doc)
    frappe.throw(str(items_data))
    for item in items_data:
            try:
                track_stock_movement = TrackStockMovement(token)
                result = track_stock_movement.post_stock_movement(item)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        
def on_submit(doc, method=None):
    if stock_permission==1 or doc.custom_allow_obr_to_track_the_items:
        try:
            get_items(doc)
            frappe.msgprint("The transaction was added successfully!")
        except Exception as e:
            frappe.msgprint(f"Error during submission: {str(e)}")
