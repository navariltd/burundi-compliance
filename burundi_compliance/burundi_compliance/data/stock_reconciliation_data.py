from datetime import datetime
import frappe
from ..utils.system_tax_id import get_system_tax_id
from ..utils.format_date_and_time import date_time_format

def get_stock_reconciliation_items(doc):
    '''
    Get items from the stock reconciliation for updating stock
    '''
    if doc.purpose == "Opening Stock":
        movement_type = "EI"  # Opening Stock
    else:
        movement_type = "EAJ"  # Adjustment Entries for Stock Reconciliation
        
    date_time = date_time_format(doc)
    formatted_date = date_time[0]
    # Prepare stock movement data for Stock Reconciliation
    reconciliation_items = doc.items
    all_items=[]
    for item in reconciliation_items:
        # Fetch the uom from the Item doctype
        item_doc = frappe.get_doc("Item", item.item_code)
        item_uom = item_doc.stock_uom if item_doc else None

        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item_uom,
            "item_purchase_or_sale_price": item.valuation_rate,  # Assuming valuation rate is the purchase price
            "item_purchase_or_sale_currency": 'BIF',
            "item_movement_type": movement_type,  # Adjustment Entries for Stock Reconciliation
            "item_movement_date": formatted_date
        }
        
        all_items.append(data)

    return all_items
