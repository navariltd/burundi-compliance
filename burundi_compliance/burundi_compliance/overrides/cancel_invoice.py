
import frappe
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from burundi_compliance.burundi_compliance.api_classes.add_stock_movement import TrackStockMovement
from burundi_compliance.burundi_compliance.data.sale_invoice_data import InvoiceDataProcessor
from burundi_compliance.burundi_compliance.api_classes.cancel_invoice import InvoiceCanceller
from burundi_compliance.burundi_compliance.data.cancel_invoice_data import get_invoice_data

obr_integration_base = OBRAPIBase()

def cancel_invoice(doc, method=None):
    obr_base = OBRAPIBase()
    token = obr_base.authenticate()
    invoice_data = get_invoice_data(doc)
    
    if invoice_data:
        pass
        #frappe.msgprint(f"Cancelling invoice {invoice_data}")
    invoice_canceller = InvoiceCanceller(token)
    response = invoice_canceller.cancel_invoice(invoice_data)
    on_cancel_update_stock(doc)
    frappe.msgprint(response)
    
    

def get_items(doc):
    
    token = obr_integration_base.authenticate()
    sales_invoice_data_processor = InvoiceDataProcessor(doc)
    items_data = sales_invoice_data_processor.get_sales_data_for_stock_update()
    
    for item in items_data:
            item.update({"item_movement_type":"ER"})
            try:
                track_stock_movement = TrackStockMovement(token)
                result = track_stock_movement.post_stock_movement(item)
                frappe.msgprint(f"Result: {result}")
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        

def on_cancel_update_stock(doc, method=None):
    if doc.update_stock==1:
        try:
            get_items(doc)
            frappe.msgprint("The transaction was added successfully!")
        except Exception as e:
            frappe.msgprint(f"Error during submission: {str(e)}")
    
    