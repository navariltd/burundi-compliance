
import frappe 
from ..utils.system_tax_id import get_system_tax_id

from ..utils.system_tax_id import get_system_tax_id
from ..utils.format_date_and_time import date_time_format

def single_stock_data(doc, method=None):
    '''
    Get items from the purchase receipt which will update the stock
    '''
        
    date_time=date_time_format(doc)
    formatted_date=date_time[0]

    # Prepare stock movement data
    purchase_invoice_items = doc.items
    stock_movement_data=[]
    for item in purchase_invoice_items:
        item_doc = frappe.get_doc("Item", item.item_code)
        check_br_permission=item_doc.custom_allow_obr_to_track_purchase
        if not check_br_permission:
            continue
        
        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item.uom,
            "item_purchase_or_sale_price": item.valuation_rate,
            "item_purchase_or_sale_currency": doc.company_currency,
            "item_movement_type": "EN",
            "item_movement_description":'Purchased goods',
            "item_movement_date": formatted_date,
        }

        stock_movement_data.append(data)

    return stock_movement_data



