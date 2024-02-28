from ..api_classes.add_invoices import SalesInvoicePoster
from ..api_classes.base import OBRAPIBase
from ..api_classes.add_stock_movement import TrackStockMovement
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from ..utils.invoice_signature import create_invoice_signature
from ..data.sale_invoice_data import InvoiceDataProcessor
from frappe import _
from ..utils.background_jobs import enqueue_stock_movement

obr_integration_base = OBRAPIBase()

auth_details=obr_integration_base.get_auth_details()
				
def on_submit(doc, method=None):
	token = obr_integration_base.authenticate()
	sales_invoice_data_processor = InvoiceDataProcessor(doc)
	obr_invoice_poster = SalesInvoicePoster(token)

	invoice_data = sales_invoice_data_processor.prepare_invoice_data()

	if doc.is_return:
		invoice_data = sales_invoice_data_processor.prepare_credit_note_data(invoice_data)

		if doc.custom_creating_payment_entry == 1:
			invoice_data = sales_invoice_data_processor.prepare_reimbursement_deposit_data(invoice_data)

	# Enqueue background job to send invoice data to OBR
	job_id = enqueue_retry_job(invoice_data, token, doc.name)
	if job_id:
		frappe.msgprint(f"Sending data to OBR....{job_id}")
	else:
		frappe.msgprint("Job enqueue failed.")
	
	doc.submit()
	doc.reload()
	on_submit_update_stock(doc)


def get_items(doc):
	token = obr_integration_base.authenticate()
	sales_invoice_data_processor = InvoiceDataProcessor(doc)
	items_data = sales_invoice_data_processor.get_sales_data_for_stock_update()
	
	for item in items_data:
			try:
				enqueue_stock_movement(item)
				frappe.msgprint(f"The transaction for {item.get('item_designation')} was added successfully!")
			except Exception as e:
				frappe.msgprint(f"Error sending item {item}: {str(e)}")
		

def on_submit_update_stock(doc, method=None):
	if doc.update_stock==1:
		try:
			get_items(doc)
			frappe.msgprint("The transaction was added successfully!")
		except Exception as e:
			frappe.msgprint(f"Error during submission: {str(e)}")

    
######################################################################################################
# This is the new function that will be used to enqueue the background job to send invoice data to OBR
######################################################################################################
def enqueue_retry_job(invoice_data, token, doc_name):
    job_id = frappe.enqueue(
        "burundi_compliance.burundi_compliance.utils.background_jobs.retry_sales_invoice_post",
        invoice_data=invoice_data,
        token=token,
        doc=doc_name,
        queue="long",
        timeout=300,
        is_async=True,
        at_front=False,
    )

    return job_id

