from ..api_classes.base import OBRAPIBase
from ..data.stock_data import single_stock_data
from ..doctype.custom_exceptions import StockMovementError
import frappe
from ..utils.background_jobs import enqueue_stock_movement
from ..overrides.stock_ledger_entry import send_data

obr_details=OBRAPIBase()


def get_items(doc):
    items_data = single_stock_data(doc)   
    
    
    for item in items_data:
            try:
                
                #get the stock ledger entry for the item
                stock_ledger_entry = frappe.get_all("Stock Ledger Entry", filters={"item_code": item.get("item_code"), "voucher_no": doc.name}, fields=["*"])
                for stock_ledger in stock_ledger_entry:
                    stock_ledger_doc = frappe.get_doc("Stock Ledger Entry", stock_ledger.name)
                    send_data(stock_ledger_doc)
                    # frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully", alert=True)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
                raise StockMovementError(f"Error sending item {item}: {str(e)}")   