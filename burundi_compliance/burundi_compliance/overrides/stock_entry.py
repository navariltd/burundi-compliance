
from ..api_classes.add_stock_movement import TrackStockMovement
from ..data.stock_entry_data import get_stock_entry_items
from ..api_classes.base import OBRAPIBase
import frappe
from ..utils.background_jobs import enqueue_stock_movement


auth_base = OBRAPIBase()

def get_items(doc):
    data = get_stock_entry_items(doc)
    token = auth_base.authenticate()
    send_data = TrackStockMovement(token)
    if data:
        for item in data:
            try:
                # auth_base.authenticate()
                # send_data.post_stock_movement(item)
                
                enqueue_stock_movement(item, doc)
                frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully", alert=True)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
   

            

def on_submit(doc, method=None):
   # if stock_permission==1 or doc.custom_allow_obr_to_track_stock_movement or doc.stock_entry_type=="Manufacture":
    get_items(doc)
        
