
from ..api_classes.base import OBRAPIBase
from ..utils.background_jobs import enqueue_retry_posting_sales_invoice
import frappe
from ..data.sale_invoice_data import InvoiceDataProcessor
from frappe import _
from ..utils.background_jobs import enqueue_stock_movement

obr_integration_base = OBRAPIBase()

auth_details=obr_integration_base.get_auth_details()
				
def on_submit(doc, method=None):
	submit_invoice_request(doc)
	doc.submit()
	doc.reload()
	if doc.doctype == "Sales Invoice":
	 	on_submit_update_stock(doc)


def get_items(doc):
	sales_invoice_data_processor = InvoiceDataProcessor(doc)
	items_data = sales_invoice_data_processor.get_sales_data_for_stock_update()
	
	for item in items_data:
			try:
				enqueue_stock_movement(item, doc)
				frappe.msgprint(f"The transaction for {item.get('item_designation')} was queued successfully!", alert=True)
			except Exception as e:
				frappe.msgprint(f"Error sending item {item}: {str(e)}")
		

def on_submit_update_stock(doc, method=None):
	if doc.update_stock==1 or doc.is_return==1:
		try:
			get_items(doc)
		except Exception as e:
			frappe.msgprint(f"Error during submission: {str(e)}")


def submit_invoice_request(doc):
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