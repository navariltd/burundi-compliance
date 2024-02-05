
from datetime import datetime
import frappe  # Assuming frappe is used to fetch data from the database
from ..utils.system_tax_id import get_system_tax_id
from datetime import datetime

from datetime import datetime, date


def get_delivery_note_items(doc):

    '''
    Get items from the delivery note which will update the stock
    '''
    
    # posting_date_object = datetime.strptime(doc.posting_date, "%Y-%m-%d").date()
    # try:
    #     posting_datetime = datetime.combine(posting_date_object, datetime.strptime(doc.posting_time, "%H:%M:%S").time())
    # except ValueError:
    #     posting_datetime = datetime.combine(posting_date_object, datetime.strptime(doc.posting_time, "%H:%M:%S.%f").time())

    # # Format the datetime as a string
    # formatted_date = posting_datetime.strftime("%Y-%m-%d %H:%M:%S")

    if doc.is_return:
        movement_type="ER"
    else:
        movement_type="SN"
    # Prepare stock movement data
    delivery_note_items = []
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
            "item_movement_date": str(doc.posting_date)
        }

        delivery_note_items.append(data)
        
    return delivery_note_items


