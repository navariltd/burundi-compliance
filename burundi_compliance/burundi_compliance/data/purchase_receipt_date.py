from datetime import datetime
import frappe  # Assuming frappe is used to fetch data from the database
from ..utils.system_tax_id import get_system_tax_id
from datetime import datetime

from datetime import datetime, date


def purchase_receipt_data(doc, method=None):

    '''
    Get items from the purchase receipt which will update the stock
    '''
    
    posting_date_object = datetime.strptime(doc.posting_date, "%Y-%m-%d").date()
    try:
        posting_datetime = datetime.combine(posting_date_object, datetime.strptime(doc.posting_time, "%H:%M:%S").time())
    except ValueError:
        posting_datetime = datetime.combine(posting_date_object, datetime.strptime(doc.posting_time, "%H:%M:%S.%f").time())

    # Format the datetime as a string
    formatted_date = posting_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Prepare stock movement data
    stock_movement_data = []
    purchase_invoice_items=doc.items
    for item in purchase_invoice_items:
        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item.uom,
            "item_purchase_or_sale_price": item.rate,
            "item_purchase_or_sale_currency": doc.currency,
            "item_movement_type": "EN",
            "item_movement_invoice_ref": doc.name,
            "item_movement_description": item.description,
            "item_movement_date": formatted_date
        }

        stock_movement_data.append(data)
    return stock_movement_data


