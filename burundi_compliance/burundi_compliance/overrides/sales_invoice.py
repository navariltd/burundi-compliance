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

# def on_submit(doc, method=None):
#     token = obr_integration_base.authenticate()
#     sales_invoice_data_processor = InvoiceDataProcessor(doc)
#     obr_invoice_poster = SalesInvoicePoster(token)
	
#     invoice_data=sales_invoice_data_processor.prepare_invoice_data()
#     # frappe.throw(str(invoice_data))
#     if doc.is_return:
		
#         invoice_data =sales_invoice_data_processor.prepare_credit_note_data(invoice_data)
		
#         if doc.custom_creating_payment_entry == 1:
#             invoice_data = sales_invoice_data_processor.prepare_reimbursement_deposit_data(invoice_data)
		  
#     result = obr_invoice_poster.post_invoice(invoice_data)
#     on_submit_update_stock(doc)
#     frappe.msgprint(f"Invoice data sent to OBR")
				#frappe.throw(F"Moment {item}")
				
def on_submit(doc, method=None):
	token = obr_integration_base.authenticate()
	sales_invoice_data_processor = InvoiceDataProcessor(doc)
	obr_invoice_poster = SalesInvoicePoster(token)

	invoice_data = sales_invoice_data_processor.prepare_invoice_data()

	if doc.is_return:
		invoice_data = sales_invoice_data_processor.prepare_credit_note_data(invoice_data)

		if doc.custom_creating_payment_entry == 1:
			invoice_data = sales_invoice_data_processor.prepare_reimbursement_deposit_data(invoice_data)


	# Enqueue background job only if the result is unsuccessful
	job_id = frappe.enqueue(
		"burundi_compliance.burundi_compliance.utils.background_jobs.retry_sales_invoice_post",
		invoice_data=invoice_data,
		token=token,
		doc=doc.name,
		queue="long",
		timeout=1500,
		is_async=True,
		at_front=False,
	)

	if job_id:
		frappe.msgprint(f"Job enqueued successfully with ID: {job_id}")
	else:
		frappe.msgprint("Job enqueue failed.")
	
	doc.submit()
	doc.reload()


def get_items(doc):
	token = obr_integration_base.authenticate()
	sales_invoice_data_processor = InvoiceDataProcessor(doc)
	items_data = sales_invoice_data_processor.get_sales_data_for_stock_update()
	
	for item in items_data:
			try:
				#frappe.throw(F"Moment {item}")
				track_stock_movement = TrackStockMovement(token)
				result = track_stock_movement.post_stock_movement(item)
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

def after_save(doc, method=None):
	
	invoice_identifier = create_invoice_signature(doc)
	doc.custom_invoice_identifier = invoice_identifier
	doc.db_set('custom_invoice_identifier', invoice_identifier, commit=True)
	   
	