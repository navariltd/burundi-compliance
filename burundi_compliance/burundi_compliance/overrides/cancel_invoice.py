
import frappe
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from burundi_compliance.burundi_compliance.data.sale_invoice_data import InvoiceDataProcessor
from burundi_compliance.burundi_compliance.data.cancel_invoice_data import get_invoice_data
from burundi_compliance.burundi_compliance.utils.background_jobs import enqueue_cancel_invoice, enqueue_stock_movement

base=OBRAPIBase()
def cancel_invoice(doc, method=None):
    invoice_data = get_invoice_data(doc)  
    base.authenticate()
    enqueue_cancel_invoice(invoice_data, doc)
    frappe.msgprint("Invoice cancellation job queued successfully!", alert=True)
    on_cancel_update_stock(doc)
        
        
def get_items(doc):
    sales_invoice_data_processor = InvoiceDataProcessor(doc)
    items_data = sales_invoice_data_processor.get_sales_data_for_stock_update()
    
    for item in items_data:
            item.update({"item_movement_type":"ER"})
            try:
                enqueue_stock_movement(item, doc)
                frappe.msgprint(f"The transaction for {item.get('item_designation')} was queued successfully!", alert=True)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        

def on_cancel_update_stock(doc, method=None):
    if doc.update_stock==1:
        try:
            get_items(doc)
        except Exception as e:
            frappe.msgprint(f"Error during submission: {str(e)}")
    
    