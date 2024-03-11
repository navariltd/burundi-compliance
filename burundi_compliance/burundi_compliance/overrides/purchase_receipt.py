from ..api_classes.base import OBRAPIBase
from ..data.purchase_receipt_date import purchase_receipt_data
from ..doctype.custom_exceptions import StockMovementError
import frappe
from ..utils.background_jobs import enqueue_stock_movement

obr_details=OBRAPIBase()


def get_items(doc):
    token=obr_details.authenticate()
    items_data = purchase_receipt_data(doc)
    for item in items_data:
            try:
                enqueue_stock_movement(item, doc)
                frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully", alert=True)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
                raise StockMovementError(f"Error sending item {item}: {str(e)}")        
   
def on_submit(doc, method=None):
	try:
		get_items(doc)
	except Exception as e:
		frappe.msgprint(f"Error during submission: {str(e)}")

