from ..api_classes.add_stock_movement import TrackStockMovement
from ..data.stock_reconciliation_data import get_stock_reconciliation_items
import frappe

# Import necessary modules
from datetime import datetime
from ..utils.system_tax_id import get_system_tax_id

def on_submit(doc, method=None):
    # Assuming you have the authentication token
    token = "djab8778asdbjabddjankjbJBAFSY787GDSHJBVJDSVRDTRDhbsbdajb*&"
    
    # Create an instance of TrackStockMovement class
    track_stock_movement = TrackStockMovement(token)

    # Get stock reconciliation items data
    items_data = get_stock_reconciliation_items(doc)

    if items_data:
        frappe.msgprint(f"Data available is: {items_data}")

    # Post stock movement to OBR
    results = track_stock_movement.post_stock_movement(items_data)

    # Display success message
    frappe.msgprint("Stock Reconciliation items added to stock successfully")
