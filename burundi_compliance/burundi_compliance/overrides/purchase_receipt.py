from ..api_classes.base import OBRAPIBase
from ..data.purchase_receipt_date import purchase_receipt_data
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import StockMovementError, AuthenticationError
import frappe


obr_details=OBRAPIBase()

token=obr_details.authenticate()
def get_items(doc):
    items_data = purchase_receipt_data(doc)
    
    for item in items_data:
            try:
                track_stock_movement = TrackStockMovement(token)
                result = track_stock_movement.post_stock_movement(item)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        

def on_submit(doc, method=None):
	try:
		get_items(doc)
		frappe.msgprint("The transaction was added successfully!")
	except Exception as e:
		frappe.msgprint(f"Error during submission: {str(e)}")

