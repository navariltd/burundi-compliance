import frappe
from ..utils.system_tax_id import get_system_tax_id
from ..utils.format_date_and_time import date_time_format
from ..utils.invoice_signature import create_invoice_signature
from ..api_classes.base import OBRAPIBase
import time as time



def get_purchase_data_for_stock_update(doc, method=None, movement_type="EN"):
    formatted_date_data = date_time_format(doc)
    formatted_date = formatted_date_data[0]

    sale_return_items_list = []
    sales_return_items = doc.items
    for item in sales_return_items:

        item_doc = frappe.get_doc("Item", item.item_code)
        item_uom = item_doc.stock_uom if item_doc else None
        check_br_permission=item_doc.custom_allow_obr_to_track_purchase
        if not check_br_permission:
            continue

        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item_uom,
            "item_purchase_or_sale_price": item.rate, 
            "item_purchase_or_sale_currency": doc.currency,
            "item_movement_type": movement_type,
            "item_movement_invoice_ref": doc.name,
            "item_movement_description": '',
            "item_movement_date": formatted_date
        }
        
        sale_return_items_list.append(data)

    return sale_return_items_list

