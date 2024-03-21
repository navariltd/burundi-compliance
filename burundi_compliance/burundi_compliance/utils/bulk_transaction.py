
from burundi_compliance.burundi_compliance.utils.background_jobs import enqueue_retry_posting_sales_invoice
from burundi_compliance.burundi_compliance.data.sale_invoice_data import InvoiceDataProcessor
from burundi_compliance.burundi_compliance.overrides.sales_invoice import on_submit_update_stock
# from burundi_compliance.burundi_compliance.overrides.purchase_receipt import get_items
from burundi_compliance.burundi_compliance.utils.get_stock_items import get_items
import frappe
import ast

@frappe.whitelist(allow_guest=True)
def bulk_invoice_submission():
	
	'''Bulk submission of sales invoices to OBR. 
	This function is called from the bulk submission button in the sales invoice list view.
	It takes the list of sales invoices selected by the user and sends them to OBR. It also updates the stock for the submitted invoices.'''
 
	sales_invoices_str = frappe.form_dict.get("sales_invoices")
	doctype = frappe.form_dict.get("doctype")
	sales_invoices = ast.literal_eval(sales_invoices_str)
	
	for invoice in sales_invoices:
		
		try:
			doc=frappe.get_doc(doctype, invoice)
		except Exception as e:
			frappe.msgprint("No document found for the selected invoice")
			continue

		sales_invoice_data_processor = InvoiceDataProcessor(doc)
		
		invoice_data = sales_invoice_data_processor.prepare_invoice_data()

		if doc.is_return:
			invoice_data = sales_invoice_data_processor.prepare_credit_note_data(invoice_data)

			if doc.custom_creating_payment_entry == 1:
				invoice_data = sales_invoice_data_processor.prepare_reimbursement_deposit_data(invoice_data)

		if doc.custom_differ_submission_to_obr == 0:
			job_id = enqueue_retry_posting_sales_invoice(invoice_data, doc)
			if job_id:
				frappe.msgprint(f"Sending data to OBR. Job queued", alert=True)
			else:
				frappe.msgprint("Job enqueue failed.")
		if doctype == "Sales Invoice":
			on_submit_update_stock(doc)
  

@frappe.whitelist(allow_guest=True)
def bulk_stock_submission():
	
	'''Bulk update of stock for sales invoices. 
	This function is called from the bulk stock update button in the sales invoice list view.
	It takes the list of sales invoices selected by the user and updates the stock for the submitted invoices.'''
 
	stock_docs = frappe.form_dict.get("stock_details")
	stock_docs_list = ast.literal_eval(stock_docs)
	doctype=frappe.form_dict.get("doctype")
 
	for stock_doc in stock_docs_list:
		try:
			doc=frappe.get_doc(doctype, stock_doc)

		except Exception as e:
			frappe.msgprint("No document found for the selected stock reconciliation")
			continue
		get_items(doc)
		doc.reload()
  