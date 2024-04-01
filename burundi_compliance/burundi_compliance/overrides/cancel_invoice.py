
import frappe
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from burundi_compliance.burundi_compliance.data.sale_invoice_data import InvoiceDataProcessor
from burundi_compliance.burundi_compliance.data.cancel_invoice_data import get_invoice_data
from burundi_compliance.burundi_compliance.utils.background_jobs import enqueue_cancel_invoice, enqueue_stock_movement
from burundi_compliance.burundi_compliance.utils.get_stock_items import get_items

base=OBRAPIBase()
def cancel_invoice(doc, method=None):
    invoice_data = get_invoice_data(doc)  
    base.authenticate()
    enqueue_cancel_invoice(invoice_data, doc)
    frappe.msgprint("Invoice cancellation job queued successfully!", alert=True)
    # on_cancel_update_stock(doc)
        
# def on_cancel_update_stock(doc, method=None):
#     if doc.update_stock==1:
#         get_items(doc)
    