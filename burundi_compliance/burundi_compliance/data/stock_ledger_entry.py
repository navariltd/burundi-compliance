
from ..utils.system_tax_id import get_system_tax_id
import frappe
from ..utils.format_date_and_time import date_time_format


def get_stock_ledger_data(doc):
    
    '''
    Prepare data from stock ledger entry for further processing
    '''
    
    voucher_type = doc.voucher_type
    voucher_no = doc.voucher_no
    item_code=doc.item_code
    specified_doc=frappe.get_doc(voucher_type, voucher_no)
    
    valuation_rate=get_valuation_rate(voucher_type, specified_doc, item_code)
    if voucher_type == "Stock Reconciliation":
        movement_type, quantity_difference, movement_description = get_voucher_doc_details(doc, voucher_type, voucher_no, item_code)
    else:
        movement_type, movement_description = get_voucher_doc_details(doc, voucher_type, voucher_no, item_code)
    date = date_time_format(doc)
    formatted_date = date[0]
    
    data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": doc.item_code,
            "item_designation": doc.item_code,
            "item_quantity": quantity_difference if voucher_type == "Stock Reconciliation" else doc.actual_qty,
            "item_measurement_unit": doc.stock_uom,
            "item_purchase_or_sale_price": valuation_rate,
            "item_purchase_or_sale_currency": frappe.get_value("Company", doc.company, "default_currency"),
            "item_movement_type": movement_type,
            "item_movement_description":movement_description,
            "item_movement_date": formatted_date,
        }
    
    return data


def get_voucher_doc_details(stock_ledger_entry_doc, voucher_type, voucher_no, item_code):
    
    '''
    Get the details of the voucher document
    '''
    
    if voucher_type == "Stock Entry":
        doc = frappe.get_doc("Stock Entry", voucher_no)
        movement_type=get_stock_movement_type(stock_ledger_entry_doc, doc)
        movement_description=get_stock_movement_description(doc)
        
        return movement_type,movement_description
    
    elif voucher_type == "Purchase Receipt":
        doc = frappe.get_doc("Purchase Receipt", voucher_no)
        movement_type="EI"
        if doc.is_return:
            movement_type="SAU"
        
        movement_description="Normal Purchase of goods"
        return movement_type,movement_description
    
    elif voucher_type == "Delivery Note":
        doc = frappe.get_doc("Delivery Note", voucher_no)
        movement_type="SN"
        if doc.is_return:
            movement_type="ER"
            
        movement_description="Normal sale of goods"
        return movement_type,movement_description
    
    elif voucher_type == "Sales Invoice":
        doc = frappe.get_doc("Sales Invoice", voucher_no)
        movement_description=get_stock_movement_description(doc)
        movement_type="SN"
        return movement_type,movement_description
    
    elif voucher_type == "Purchase Invoice":
        doc = frappe.get_doc("Purchase Invoice", voucher_no)
        movement_type="EN"
        movement_description="Normal Purchase of goods"
        return movement_type,movement_description
        
    elif voucher_type == "Stock Reconciliation":
        doc = frappe.get_doc("Stock Reconciliation", voucher_no)
        movement_type, quantity_difference=get_stock_recon_movement_type(stock_ledger_entry_doc,doc, item_code)
        movement_description=get_stock_movement_description(doc)
        return movement_type,quantity_difference, movement_description
    
    else:
        return None
    
def get_stock_movement_type(stock_ledger_entry_doc, doc):
    '''
    Get the movement type based on stock entry type and custom movement type
    '''
    stock_entry_type = doc.stock_entry_type
    stock_movement_type = doc.custom_stock_movement_type
    
    if stock_ledger_entry_doc.actual_qty>0 and stock_entry_type in ["Material Receipt", "Manufacture"] or stock_ledger_entry_doc.actual_qty<0 and stock_entry_type in  ["Material Issue", "Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return get_stock_movement_on_submit(stock_entry_type, stock_movement_type)
    
    elif stock_ledger_entry_doc.actual_qty<0 and stock_entry_type in ["Material Receipt", "Manufacture"] or stock_ledger_entry_doc.actual_qty>0 and stock_entry_type in  ["Material Issue", "Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return get_stock_movement_on_cancel(stock_entry_type)
    
    elif stock_entry_type=="Repack":
        return get_item_movement_on_repack_on_submit_and_cancel(stock_ledger_entry_doc,doc)
       
    
    
        
def get_stock_movement_on_submit(stock_entry_type, stock_movement_type):
    if stock_entry_type == "Material Receipt":
            return "EI"
    elif stock_entry_type == "Material Issue":
        if stock_movement_type == "Theft exits(SV)":
            return "SV"
        elif stock_movement_type == "Obsolete/expired or obsolete issues(SD)":
            return "SD"
        elif stock_movement_type == "Breakage Exits(SC)":
            return "SC"
        elif stock_movement_type=="Loss Outflows(SP)":
            return "SP"
        else:
            return "ST"
    elif stock_entry_type == "Manufacture":
        return "EN"
    elif stock_entry_type in ["Repack", "Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return "SAU"
    else:
        return "UAE"
    
def get_stock_movement_on_cancel(stock_entry_type):
    if stock_entry_type == "Material Receipt":
            return "SAU"
    elif stock_entry_type == "Material Issue":
        return "ER"
    elif stock_entry_type == "Manufacture":
        return "SAU"
    elif stock_entry_type in ["Repack", "Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return "ER"
    else:
        return "UAE"
        
        
def get_stock_movement_description(doc):
    stock_movement_description=doc.custom_stock_movement_description if doc.custom_stock_movement_description else ''
    return stock_movement_description
    
def get_stock_recon_movement_type(stock_ledger_entry_doc,doc, item_code):
    '''
    Get the movement type for stock reconciliation
    '''
    
    if doc.purpose == "Opening Stock":
        for item in doc.items:
            if item.item_code==item_code:
                quantity_difference=item.quantity_difference
        if stock_ledger_entry_doc.actual_qty==0:
            movement_type = "EI"  # Opening Stock
        else:
            movement_type="SAU"
    
    elif doc.purpose=="Stock Reconciliation":
        for item in doc.items:
            if item.item_code==item_code:
                quantity_difference=item.quantity_difference
                if stock_ledger_entry_doc.actual_qty==0:
                
                    if float(quantity_difference)>0.0:
                        movement_type = "EAJ"
                    elif float(quantity_difference)<0.0:
                        movement_type = "SAJ"
                else:
                    if float(quantity_difference)>0.0:
                        movement_type = "SAJ"
                    elif float(quantity_difference)<0.0:
                        movement_type = "EAJ"
    
    return movement_type, quantity_difference


def get_valuation_rate(voucher_type, doc, item_code):
    '''
    Get the valuation rate for the item for Stock Reconciliation, Purchase Receipt, Delivery Note, Sales Invoice, Purchase Invoice
    '''
    for item in doc.items:
        if item.item_code==item_code:
            if voucher_type == "Stock Entry" or voucher_type == "Stock Reconciliation":
                return item.valuation_rate
            else:
                return item.rate
        

def get_item_movement_on_repack_on_submit_and_cancel(stock_ledger_entry_doc,doc):
    '''
    Get the movement type for repack
    '''
    item_code=stock_ledger_entry_doc.item_code
    for item in doc.items:
        if item.item_code==item_code:
            if stock_ledger_entry_doc.actual_qty>0:
                return "EN"
            else:
                return "SAU"
            

