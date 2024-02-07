from ..api_classes.base import OBRAPIBase
from ..data.purchase_receipt_date import purchase_receipt_data
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import StockMovementError, AuthenticationError
import frappe


obr_details=OBRAPIBase()

auth_token=obr_details.authenticate()

def on_submit(doc, method=None):
    token = auth_token
    #token="djab8778asdbjabddjankjbJBAFSY787GDSHJBVJDSVRDTRDhbsbdajb*&"
    receive_goods = TrackStockMovement(token)
    items_data = purchase_receipt_data(doc)
    if items_data:
        frappe.msgprint(f"Data available is: {items_data}")
    results=receive_goods.post_stock_movement(items_data)
    frappe.msgprint("Items added to stock successfully")
    