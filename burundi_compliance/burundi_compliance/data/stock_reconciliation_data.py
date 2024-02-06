from datetime import datetime
import frappe
from ..utils.system_tax_id import get_system_tax_id

def get_stock_reconciliation_items(doc):
    '''
    Get items from the stock reconciliation for updating stock
    '''
    posting_date_object = datetime.strptime(doc.posting_date, "%Y-%m-%d").date()
    try:
        posting_datetime = datetime.combine(posting_date_object, datetime.strptime(doc.posting_time, "%H:%M:%S").time())
    except ValueError:
        posting_datetime = datetime.combine(posting_date_object, datetime.strptime(doc.posting_time, "%H:%M:%S.%f").time())

    # Format the datetime as a string
    formatted_date = posting_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Prepare stock movement data for Stock Reconciliation
    stock_movement_data = []
    reconciliation_items = doc.items

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
            "item_movement_type": "EAJ",  # Adjustment Entries for Stock Reconciliation
            "item_movement_date": formatted_date
        }

        stock_movement_data.append(data)

    return stock_movement_data
