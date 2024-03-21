from ..api_classes.base import OBRAPIBase
from ..data.stock_data import single_stock_data
from ..doctype.custom_exceptions import StockMovementError
import frappe
from ..utils.background_jobs import enqueue_stock_movement

obr_details=OBRAPIBase()


def get_items(doc):
    items_data = single_stock_data(doc)
    for item in items_data:
            try:
                enqueue_stock_movement(item, doc)
                frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully", alert=True)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
                raise StockMovementError(f"Error sending item {item}: {str(e)}")   