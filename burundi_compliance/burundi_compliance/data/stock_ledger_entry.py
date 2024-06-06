
from ..utils.system_tax_id import get_system_tax_id
import frappe
from ..utils.format_date_and_time import date_time_format
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
import time
auth=OBRAPIBase()

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
    
    item_movement_invoice_ref=get_invoice_reference_number(voucher_type, voucher_no)
    
    
    item_designation=create_item_designation(specified_doc, item_code)
    
    data = {
            "system_or_device_id": get_system_tax_id(),
            "item_code": doc.item_code,
            "item_designation": item_designation,
            "item_quantity": abs(float(quantity_difference)) if voucher_type == "Stock Reconciliation" else abs(float(doc.actual_qty)),
            "item_measurement_unit": doc.stock_uom,
            "item_purchase_or_sale_price": int(valuation_rate),
            "item_purchase_or_sale_currency": frappe.get_value("Company", doc.company, "default_currency"),
            "item_movement_type": movement_type,
            "item_movement_invoice_ref": item_movement_invoice_ref,
            "item_movement_description":movement_description,
            "item_movement_date": formatted_date,
        }
    return data

def get_voucher_doc_details(stock_ledger_entry_doc, voucher_type, voucher_no, item_code):
    
    '''
    Get the details of the voucher document
    '''
    
    if voucher_type == "Stock Entry":
        doc = get_doc_details("Stock Entry", voucher_no)
        movement_type=get_stock_movement_type(stock_ledger_entry_doc, doc)
        movement_description=get_stock_movement_description(doc)
        return movement_type,movement_description
    
    elif voucher_type == "Purchase Receipt":
        doc = get_doc_details("Purchase Receipt", voucher_no)
        movement_type=get_item_movement_on_purchase_receipt_and_invoice_on_submit_and_cancel(stock_ledger_entry_doc,doc)
        movement_description=get_stock_movement_description(doc)
        return movement_type,movement_description
    
    elif voucher_type == "Delivery Note":
        doc = get_doc_details("Delivery Note", voucher_no)
        movement_type, movement_description=get_item_movement_on_delivery_note_and_sale_invoice_on_submit_and_cancel(stock_ledger_entry_doc,doc)
        return movement_type,movement_description
    
    elif voucher_type == "Sales Invoice":
        doc = get_doc_details("Sales Invoice", voucher_no)
        movement_type, movement_description=get_item_movement_on_delivery_note_and_sale_invoice_on_submit_and_cancel(stock_ledger_entry_doc,doc)
        return movement_type,movement_description
    
    elif voucher_type == "Purchase Invoice":
        doc = get_doc_details("Purchase Invoice", voucher_no)
        movement_type=get_item_movement_on_purchase_receipt_and_invoice_on_submit_and_cancel(stock_ledger_entry_doc,doc)
        movement_description=get_stock_movement_description(doc)
        return movement_type,movement_description
        
    elif voucher_type == "Stock Reconciliation":
        doc = get_doc_details("Stock Reconciliation", voucher_no)
        movement_type, quantity_difference=get_stock_recon_movement_type(stock_ledger_entry_doc,doc, item_code)
        movement_description=get_stock_movement_description(doc)
        return movement_type,quantity_difference, movement_description
    elif voucher_type == "Asset Capitalization" or voucher_type=="Asset Repair":
        doc = get_doc_details(voucher_type, voucher_no)
        movement_type=get_item_movement_asset_capitalisation_on_submit_and_cancel(stock_ledger_entry_doc,doc)
        movement_description=get_stock_movement_description(doc)
        return movement_type,movement_description
    else:
        return None
    
def get_doc_details(doc, voucher_no):
    try:
        doc=frappe.get_doc(doc, voucher_no)
        return doc
    except Exception as e:
        frappe.throw(f"No document found with {doc} and {voucher_no}")
    
def get_stock_movement_type(stock_ledger_entry_doc, doc):
    '''
    Get the movement type based on stock entry type and custom movement type
    '''
    stock_entry_type = doc.stock_entry_type
    stock_movement_type = doc.custom_stock_movement_type
    
    if stock_ledger_entry_doc.actual_qty>0 and stock_entry_type in ["Material Receipt", "Manufacture"] or stock_ledger_entry_doc.actual_qty<0 and stock_entry_type in  ["Material Issue", "Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return get_stock_movement_on_submit(stock_entry_type, stock_movement_type, doc)
    
    elif stock_ledger_entry_doc.actual_qty<0 and stock_entry_type in ["Material Receipt", "Manufacture"] or stock_ledger_entry_doc.actual_qty>0 and stock_entry_type in  ["Material Issue", "Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return get_stock_movement_on_cancel(stock_entry_type)
    
    elif stock_entry_type=="Repack":
        return get_item_movement_on_repack_on_submit_and_cancel(stock_ledger_entry_doc,doc)
       
    
def get_stock_movement_on_submit(stock_entry_type, stock_movement_type, doc):
    if stock_entry_type == "Material Receipt" and doc.is_opening == "Yes":
            return "EI"
    elif stock_entry_type == "Material Receipt" and doc.is_opening == "No":
        return "EAU"
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
    elif stock_entry_type in ["Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return "SAU"
    else:
        return "EAU"
    
def get_stock_movement_on_cancel(stock_entry_type):
    if stock_entry_type == "Material Receipt":
            return "SAU"
    elif stock_entry_type == "Material Issue":
        return "EAU"
    elif stock_entry_type == "Manufacture":
        return "SAU"
    elif stock_entry_type in ["Repack", "Material Consumption for Manufacture",
                            "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return "ER"
    else:
        return "EAU"
        
        
def get_stock_movement_description(doc):
    stock_movement_description=doc.custom_stock_movement_description if doc.custom_stock_movement_description else ''
    return stock_movement_description
    
def get_stock_recon_movement_type(stock_ledger_entry_doc,doc, item_code):
    '''
    Get the movement type for stock reconciliation
    '''
    has_batch=check_if_item_has_batches(item_code)
    warehouse=stock_ledger_entry_doc.warehouse
    if doc.purpose == "Opening Stock":
        for item in doc.items:
            if item.item_code==item_code and item.warehouse==warehouse:
                quantity_difference=item.quantity_difference
        if stock_ledger_entry_doc.is_cancelled==0:
            movement_type = "EI"  # Opening Stock
        else:
            movement_type="SAU"
    
    elif doc.purpose == "Stock Reconciliation":
        for item in doc.items:
            item_batch = None
            if has_batch:
                item_batch = get_specified_batch(stock_ledger_entry_doc)
            
            # Check if item matches the criteria
            if (item.item_code == item_code and item.warehouse == warehouse and 
                (not has_batch or item.batch_no == item_batch)):
                
                quantity_difference = item.quantity_difference
                is_cancelled = stock_ledger_entry_doc.is_cancelled
                
                if is_cancelled == 0:
                    if float(quantity_difference) > 0.0:
                        movement_type = "EAJ"
                    elif float(quantity_difference) < 0.0:
                        movement_type = "SAJ"
                elif is_cancelled == 1:
                    if float(quantity_difference) > 0.0:
                        movement_type = "SAJ"
                    elif float(quantity_difference) < 0.0:
                        movement_type = "EAJ"
                else:
                    movement_type = "SAU"
    
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
    
    #get the item_code from stock ledger entry
    item_code=stock_ledger_entry_doc.item_code
    
    for item in doc.items:
        if item.item_code==item_code:
            if stock_ledger_entry_doc.actual_qty > 0.0:
                return "EAU"
            else:
                return "SAU"
            
            
def get_item_movement_on_delivery_note_and_sale_invoice_on_submit_and_cancel(stock_ledger_entry_doc,doc):
    '''
    Get the movement type for delivery note
    '''
    movement_description="Normal Sale of Goods"
    movement_type="SN"
    item_code=stock_ledger_entry_doc.item_code
    
    for item in doc.items:
        if item.item_code==item_code:
            if stock_ledger_entry_doc.actual_qty < 0.0:
                return movement_type,movement_description
            else:
                movement_description="Normal Return of goods"
                movement_type="ER"
                return movement_type, movement_description
            
            
def get_item_movement_on_purchase_receipt_and_invoice_on_submit_and_cancel(stock_ledger_entry_doc,doc):
    '''
    Get the movement type for purchase receipt
    '''
    movement_type="EN"
    item_code=stock_ledger_entry_doc.item_code

    for item in doc.items:
        if item.item_code==item_code:
            if stock_ledger_entry_doc.actual_qty>0.0:
                return movement_type
            else:
                movement_type="SAU"
                return movement_type
            
def get_item_movement_asset_capitalisation_on_submit_and_cancel(stock_ledger_entry_doc,doc):
    '''
    Get the movement type for asset capitalisation
    '''
    movement_type="EN"
    # movement_description="Asset Capitalization"
    item_code=stock_ledger_entry_doc.item_code
    
    for item in doc.items:
        if item.item_code==item_code:
            if stock_ledger_entry_doc.actual_qty > 0.0:
                return movement_type
            else:
                # movement_description="Asset De-capitalization"
                movement_type="SAU"
                return movement_type
            
            
def get_invoice_reference_number(voucher_type, voucher_no):
    item_invoice_ref=""
    if voucher_type=="Purchase Invoice":
        purchase_doc=frappe.get_doc("Purchase Invoice", voucher_no)
        item_invoice_ref=purchase_doc.bill_no
    elif voucher_type=="Sales Invoice":
        sales_doc=frappe.get_doc("Sales Invoice", voucher_no)
        item_invoice_ref=sales_doc.name
    return item_invoice_ref


def create_item_designation(specified_doc, item_code):
    items=specified_doc.items
    for item in items:
        if item.item_code==item_code:
            if item.batch_no:
                return item.item_code + " - "+item.batch_no
            else:
                return item.item_code
            
def get_specified_batch(specified_doc):
    # Get the serial and batch bundle linked to the specified document
    serial_and_batch = specified_doc.serial_and_batch_bundle
    
    # Fetch the Serial and Batch Bundle document
    serial_and_batch_doc = frappe.get_doc("Serial and Batch Bundle", serial_and_batch)
    
    # Get the list of entries (batches) from the Serial and Batch Bundle document
    batches = serial_and_batch_doc.entries
    
    # Pick the first entry's batch number
    if batches:
        first_batch_no = batches[0].batch_no
        return first_batch_no
    else:
        frappe.throw("No batches found in the specified Serial and Batch Bundle.")

    
def check_if_item_has_batches(item_code):
    '''
    Check if the item has batches
    '''
    item_doc=frappe.get_doc("Item", item_code)
    return item_doc.has_batch_no