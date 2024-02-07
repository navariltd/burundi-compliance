from datetime import datetime
from ..utils.system_tax_id import get_system_tax_id
import frappe

def get_stock_entry_items(doc):
    '''
    Get items from the stock entry which will update the stock
    '''
    
    # Mapping of stock entry types to item movement types
    stock_entry_type_mapping = {
        'Material Issue': 'ST',
        'Material Transfer': 'ET',
        'Material Receipt': 'EI',
        'Repack': 'SAU',
        'Material Consumption for Manufacture': 'SAU',
        'Material Transfer for Manufacture': 'SAU',
        'Send to Subcontractor': 'SAU',
        'Manufacture':'EI'
    }
    
    # Get the item movement type based on stock entry type
    stock_entry_type = doc.stock_entry_type
    movement_type = stock_entry_type_mapping.get(stock_entry_type, '')

    if not movement_type:
        # Handle unknown stock entry types
        frappe.msgprint(f"Unknown stock entry type: {stock_entry_type}")
        return []

    # Prepare stock movement data
    stock_entry_items = []
    stock_entry_data = doc.items
    for item in stock_entry_data:
        data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": item.item_code,
            "item_designation": item.item_name,
            "item_quantity": item.qty,
            "item_measurement_unit": item.uom,
            "item_purchase_or_sale_price": item.valuation_rate,  # Assuming valuation rate is used for price
            "item_purchase_or_sale_currency": doc.company_currency,
            "item_movement_type": movement_type,
  "item_movement_description": item.description if item.description else '',
            "item_movement_date": str(doc.posting_date),
        }

        stock_entry_items.append(data)

    return stock_entry_items
