from datetime import datetime
from ..utils.system_tax_id import get_system_tax_id
import frappe
from ..utils.format_date_and_time import date_time_format

def get_movement_type(doc):
    '''
    Get the movement type based on stock entry type and custom movement type
    '''
    stock_entry_type = doc.stock_entry_type
    stock_movement_type = doc.custom_stock_movement_type

    if stock_entry_type == "Material Transfer":
        return "ET"
    elif stock_entry_type == "Material Receipt":
        return "EI"
    elif stock_entry_type == "Material Issue":
        if stock_movement_type == "Theft exits(SV)":
            return "SV"
        elif stock_movement_type == "Obsolete/expired or obsolete issues(SD)":
            return "SD"
        elif stock_movement_type == "Breakage Exits(SC)":
            return "SC"
        else:
            return "ST"
    elif stock_entry_type in ["Manufacture", "Repack", "Material Consumption for Manufacture",
                              "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return "SAU"
    else:
        return ""


# def get_stock_entry_items(doc):
#     '''
#     Get items from the stock entry which will update the stock
#     '''
#     date = date_time_format(doc)
#     formatted_date = date[0]
#     movement_type = get_movement_type(doc)

#     all_stock_items = []
#     stock_entry_data = doc.items
#     for item in stock_entry_data:
#         data = {
#             "system_or_device_id": get_system_tax_id(),
#             "item_code": item.item_code,
#             "item_designation": item.item_name,
#             "item_quantity": item.qty,
#             "item_measurement_unit": item.uom,
#             "item_purchase_or_sale_price": item.valuation_rate,
#             "item_purchase_or_sale_currency": doc.company_currency,
#             "item_movement_type": movement_type,
#             "item_movement_description": item.description if item.description else '',
#             "item_movement_date": formatted_date,
#         }

#         all_stock_items.append(data)

#     return all_stock_items

def get_stock_entry_items(doc):
    '''
    Get items from the stock entry which will update the stock
    '''
    date = date_time_format(doc)
    formatted_date = date[0]
    movement_type = get_movement_type(doc)
    all_stock_items = []
    stock_entry_data = doc.items

    for item in stock_entry_data:
        if doc.stock_entry_type == "Manufacture" and not item.is_finished_item:
            continue  # Skip items that do not have has_finished flag for Manufacture type
          
        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item.uom,
            "item_purchase_or_sale_price": item.valuation_rate,
            "item_purchase_or_sale_currency": doc.company_currency,
            "item_movement_type": movement_type,
            "item_movement_description": item.description if item.description else '',
            "item_movement_date": formatted_date,
        }

        all_stock_items.append(data)

    return all_stock_items
