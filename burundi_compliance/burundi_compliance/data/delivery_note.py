
from datetime import datetime
import frappe  # Assuming frappe is used to fetch data from the database
from ..utils.system_tax_id import get_system_tax_id
from datetime import datetime

from datetime import datetime, date

from datetime import datetime, date
from ..utils.system_tax_id import get_system_tax_id
from ..utils.format_date_and_time import date_time_format


   

def get_delivery_note_items(doc):

    '''
    Get items from the delivery note which will update the stock
    '''
    

    date_time=date_time_format(doc)
    formatted_date=date_time[0]
    if doc.is_return==0:
        movement_type="SN"
    else:
        movement_type="ER"
    # Prepare stock movement data
    all_d_note_items=[]
    delivery_note_data=doc.items
    for item in delivery_note_data:
        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item.uom,
            "item_purchase_or_sale_price": item.rate,
            "item_purchase_or_sale_currency": doc.currency,
            "item_movement_type":movement_type,
            "item_movement_invoice_ref": doc.name,
            "item_movement_description": item.description,
            "item_movement_date": formatted_date
        }
        all_d_note_items.append(data)
        
    return all_d_note_items



def get_delivery_note_items_on_cancel(doc):

    '''
    Get items from the delivery note which will update the stock
    '''
    

    date_time=date_time_format(doc)
    formatted_date=date_time[0]
    movement_type="ER"
    # Prepare stock movement data
    all_d_note_items=[]
    delivery_note_data=doc.items
    for item in delivery_note_data:
        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item.uom,
            "item_purchase_or_sale_price": item.rate,
            "item_purchase_or_sale_currency": doc.currency,
            "item_movement_type":movement_type,
            "item_movement_invoice_ref": doc.name,
            "item_movement_description": doc.custom_reason_for_sendingcancelling_delivery_note,
            "item_movement_date": formatted_date
        }
        all_d_note_items.append(data)
        
    return all_d_note_items
