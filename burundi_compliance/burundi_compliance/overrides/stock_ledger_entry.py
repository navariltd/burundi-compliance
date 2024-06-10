import frappe 
from burundi_compliance.burundi_compliance.data.stock_ledger_entry import get_stock_ledger_data
from burundi_compliance.burundi_compliance.utils.background_jobs import enqueue_stock_movement
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase

obr_integration_base = OBRAPIBase()

auth_details=obr_integration_base.get_auth_details()
allow_obr_to_track_stock_movement=auth_details["allow_obr_to_track_stock_movement"]
import time


def on_update(doc, method=None):
    pass                
                
def send_data(doc):
    data = get_stock_ledger_data(doc)
    
    if doc.voucher_type == "Stock Entry":
        
        stock_movement_doc = frappe.get_doc("Stock Entry", doc.voucher_no)
        movement_type = stock_movement_doc.stock_entry_type
        if movement_type == "Material Transfer":
            pass 
            return
    
    item_code = data.get("item_code")
    item_doc = frappe.get_doc("Item", item_code)

    '''If the item is set to be tracked, then enqueue the stock movement'''
    if allow_obr_to_track_stock_movement == 1 and item_doc.custom_allow_obr_to_track_stock_movement == 1:
        try:
            enqueue_stock_movement(data, doc)
            frappe.msgprint(f"The transaction for {data.get('item_code')} queued successfully", alert=True)
        except Exception as e:
            frappe.msgprint(f"Error sending item {data.get('item_code')}: {str(e)}")
