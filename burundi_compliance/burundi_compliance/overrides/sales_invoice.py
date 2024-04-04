
from ..api_classes.base import OBRAPIBase
from ..utils.background_jobs import enqueue_retry_posting_sales_invoice
import frappe
from ..data.sale_invoice_data import InvoiceDataProcessor
from frappe import _
from ..utils.background_jobs import enqueue_stock_movement
from burundi_compliance.burundi_compliance.utils.get_stock_items import get_items

obr_integration_base = OBRAPIBase()

auth_details=obr_integration_base.get_auth_details()
allow_obr_to_track_sales=auth_details["allow_obr_to_track_sales"]
allow_obr_to_track_stock_movement=auth_details["allow_obr_to_track_stock_movement"]
				
def on_submit(doc, method=None):
    obr_integration_base.authenticate()

    if doc.doctype == "Sales Invoice" and doc.is_consolidated == 0:
        submit_invoice_request(doc)
    elif doc.doctype == "POS Invoice":
        submit_invoice_request(doc)
    
    doc.submit()
    doc.reload()


	# if doc.doctype == "Sales Invoice":
	#  	on_submit_update_stock(doc)

# def on_submit_update_stock(doc, method=None):
# 	if allow_obr_to_track_stock_movement==1:
# 		if doc.update_stock==1 or doc.is_return==1:
# 				# Check if the flag is set before queuing stock movements
# 				if not doc.get("__stock_movement_queued"):
# 					frappe.publish_realtime('update_stock 1', {"message": "Updating stock"}, user=frappe.session.user)
# 					get_items(doc)
# 					# Set the flag to indicate that stock movement has been queued
# 					doc.set("__stock_movement_queued", True)

def submit_invoice_request(doc):
	if allow_obr_to_track_sales==1:
		sales_invoice_data_processor = InvoiceDataProcessor(doc)
		
		invoice_data = sales_invoice_data_processor.prepare_invoice_data()

		if doc.is_return:
			invoice_data = sales_invoice_data_processor.prepare_credit_note_data(invoice_data)

			if doc.custom_creating_payment_entry == 1:
				invoice_data = sales_invoice_data_processor.prepare_reimbursement_deposit_data(invoice_data)
		# Enqueue background job to send invoice data to OBR
		if doc.custom_differ_submission_to_obr == 0:
			job_id = enqueue_retry_posting_sales_invoice(invoice_data, doc)
			if job_id:
				frappe.msgprint(f"Sending data to OBR. Job queued", alert=True)
			else:
				frappe.msgprint("Job enqueue failed.")
	
	
	