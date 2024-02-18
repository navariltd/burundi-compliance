from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from ..utils.invoice_signature import create_invoice_signature
from ..data.sale_invoice_data import InvoiceDataProcessor
from frappe import _
from frappe.model.document import Document


obr_integration_base = OBRAPIBase()
auth_details=obr_integration_base.get_auth_details()
token = obr_integration_base.authenticate()
def on_submit(doc, method=None):
  
    sales_invoice_data_processor = InvoiceDataProcessor(doc)
    obr_invoice_poster = SalesInvoicePoster(token)  # Implement get_obr_token() to obtain the OBR token
    
    invoice_data=sales_invoice_data_processor.prepare_invoice_data()
    
    if doc.is_return:
       
        invoice_data =sales_invoice_data_processor.prepare_credit_note_data(invoice_data)
        
        if doc.custom_creating_payment_entry == 1:
            invoice_data = sales_invoice_data_processor.prepare_reimbursement_deposit_data(invoice_data)
    result = obr_invoice_poster.post_invoice(invoice_data)
    on_submit_update_stock(doc)
    frappe.msgprint(f"Invoice data sent to OBR")


def get_items(doc):
    
    sales_invoice_data_processor = InvoiceDataProcessor(doc)
    items_data = sales_invoice_data_processor.get_sales_data_for_stock_update()
    
    for item in items_data:
            try:
                track_stock_movement = TrackStockMovement(token)
                result = track_stock_movement.post_stock_movement(item)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        

def on_submit_update_stock(doc, method=None):
    if doc.update_stock==1:
        try:
            get_items(doc)
            frappe.msgprint("The transaction was added successfully!")
        except Exception as e:
            frappe.msgprint(f"Error during submission: {str(e)}")
