
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
    if doc.is_return:
        movement_type="ER"
    else:
        movement_type="SN"
    # Prepare stock movement data
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

    return data


