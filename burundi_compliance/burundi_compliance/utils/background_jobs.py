from __future__ import unicode_literals
import frappe
from ..api_classes.base import OBRAPIBase
import time as time
from ..utils.get_attemps_data import get_maximum_attempts
from ..doctype.custom_exceptions import AuthenticationError
from ..data.sale_invoice_data import InvoiceDataProcessor

base_auth = OBRAPIBase()
token=base_auth.authenticate()
max_retries = int(get_maximum_attempts()["maximum_attempts"])
retry_delay_seconds = int(get_maximum_attempts()["retry_delay_seconds"])

######################################################################################################
###########Enqueue the background job to send invoice data to OBR#####################################
######################################################################################################
@frappe.whitelist(allow_guest=True)
def retry_sales_invoice_post(invoice_data, doc):
    from ..api_classes.add_invoices import SalesInvoicePoster
    retries = 0
    invoice_type = "POS Invoice" if frappe.db.exists("POS Invoice", invoice_data.get("invoice_number")) else "Sales Invoice"
    doc = frappe.get_doc(invoice_type, invoice_data.get("invoice_number"))
    while retries < max_retries:
        try:
            sales_invoice_poster = SalesInvoicePoster(token)
            result = sales_invoice_poster.post_invoice(invoice_data)
            if result.get("success")==True:
                frappe.publish_realtime("msgprint", f"Invoice sent to OBR", user=doc.owner)
                return
            else:
                frappe.log_error(f"Error during retry ({retries + 1}/{max_retries}): {result.text}", reference_doctype=doc.doctype, reference_name=doc)
                time.sleep(retry_delay_seconds)
                retries += 1
                continue
            
        except Exception as e:
            retries += 1
            frappe.log_error(f"Error during retry ({retries}/{max_retries}): {str(e)}", reference_doctype=doc.doctype, reference_name=doc)
            time.sleep(retry_delay_seconds)
            continue  

    frappe.log_error(f"Max retries reached. Unable to send invoice data to OBR.")
    frappe.publish_realtime("msgprint", "Max retries reached. Unable to send invoice data to OBR.", user=doc.owner)
    
    '''send email to sales manager if max retries reached'''
    try:
        subject = f'Maximum retries reached. Unable to send invoice to OBR. '
        message="I hope this message finds you well. We regret to inform you that we have encountered difficulties in sending the sales invoice data to OBR (Office Burundais des Recettes). To address this matter promptly, we kindly request that you reach out to OBR directly to confirm the issue and ensure a smooth resolution",
        send_max_retries_email(get_user_email(doc), subject, message, as_markdown=False)
    except Exception as e:
        frappe.msgprint(f"Error sending emails: {str(e)}")


def enqueue_retry_posting_sales_invoice(invoice_data, doc_name):
    job_id = frappe.enqueue(
        "burundi_compliance.burundi_compliance.utils.background_jobs.retry_sales_invoice_post",
        invoice_data=invoice_data,
      
        doc=doc_name,
        queue="short",
        timeout=30,
        is_async=True,
        at_front=False,
    )

    return job_id

######################################################################################################
###########Enqueue the background job to track stock movement#########################################
######################################################################################################

@frappe.whitelist(allow_guest=True)
def retry_stock_movement(data, doc):

    from ..api_classes.add_stock_movement import TrackStockMovement
    retries = 0
    doc=frappe.get_doc(doc.doctype, doc.name)
    while retries < max_retries:
        try:
            stock_movement = TrackStockMovement(token)
            result = stock_movement.post_stock_movement(data, doc)
            if result.get('success')==True:
                frappe.db.set_value(doc.doctype, doc.name, 'custom_etracker', 1)
                if doc.doctype == "Stock Ledger Entry":
                    frappe.db.set_value(doc.voucher_type, doc.voucher_no, 'custom_etracker', 1)
                return
            else:
                frappe.db.set_value(doc.doctype, doc.name, 'custom_queued', 0)
                frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Error during retry ({retries + 1}/{max_retries}): {str(e)}", reference_doctype=doc.doctype, reference_name=doc.name)
            frappe.db.set_value("Stock Ledger Entry", doc.name, 'custom_queued', 0)
            frappe.db.commit()
             
            retries += 1
            time.sleep(retry_delay_seconds)
            continue
    frappe.log_error(f"Max retries reached. Unable to send invoice data to OBR.")

def enqueue_stock_movement(data, doc):
    frappe.enqueue('burundi_compliance.burundi_compliance.utils.background_jobs.retry_stock_movement', data=data, doc=doc, queue='short',timeout=10, is_async=True)
    

######################################################################################################
###########Enqueue the background job to Cancel sales invoice#####################################
######################################################################################################
def retry_cancel_invoice(invoice_data, doc):
    from ..api_classes.cancel_invoice import InvoiceCanceller
    retries = 0    

    while retries < max_retries:
        try:
            invoice_canceller = InvoiceCanceller(token)
            response = invoice_canceller.cancel_invoice(invoice_data)
            # frappe.db.set_value(doc.doctype, doc.name, 'custom_ebms_invoice_cancelled', 1)
            frappe.publish_realtime("msgprint", f"Invoice cancelled successful!{response}", user=frappe.session.user)
            return
        except Exception as e:
            retries += 1
            frappe.log_error(f"Error during retry ({retries}/{max_retries}): {str(e)}", reference_doctype="Sales Invoice", reference_name=doc.name)
            time.sleep(retry_delay_seconds)
            continue  

    frappe.log_error(f"Max retries reached. Unable to send invoice data to OBR.")
    
    '''send email to sales manager if max retries reached'''
    try:
        subject = f'Maximum retries reached. Unable to send invoice to OBR. '
        message="I hope this message finds you well.\n We regret to inform you that we have encountered difficulties in Cancelling the sales invoice data to OBR (Office Burundais des Recettes).\nTo address this matter promptly, we kindly request that you reach out to OBR directly to confirm the issue and ensure a smooth resolution",
        send_max_retries_email(get_user_email(doc), subject, message, as_markdown=False)
    except Exception as e:
        frappe.msgprint(f"Error sending emails: {str(e)}")
        
def enqueue_cancel_invoice(invoice_data, doc):
    frappe.enqueue('burundi_compliance.burundi_compliance.utils.background_jobs.retry_cancel_invoice', invoice_data=invoice_data,doc=doc,queue='short',timeout=10, is_async=True)
    
    
#######################################################################################################
###########Enqueue the background job for Authentication#####################################
######################################################################################################
def retry_authentication(max_retries=max_retries, retry_delay_seconds=retry_delay_seconds):
    retries = 0

    while retries < max_retries:
        try:
            obr_api = OBRAPIBase()
            obr_api.authenticate_with_retry()
            return  # Exit the loop if authentication is successful
        except AuthenticationError as auth_error:
            frappe.log_error(f"Retries {retries+1} {str(auth_error)}")
            retries += 1
            
            time.sleep(retry_delay_seconds)
            continue 
    frappe.log_error("Max retries reached. Unable to authenticate.")
    try:
        subject = f'Maximum retries reached. Unable to send data to OBR. '
        message="I hope this message finds you well.\n We regret to inform you that we have encountered difficulties in sending the data to OBR (Office Burundais des Recettes).\nTo address this matter promptly, we kindly request that you reach out to OBR directly to confirm the issue and ensure a smooth resolution",
        send_max_retries_email("mania@navari.co.ke", subject, message, as_markdown=False)
    except Exception as e:
        frappe.msgprint(f"Error sending emails: {str(e)}")
        

  ########################Send email to sales manager if max retries reached################################  
def send_max_retries_email(recipient, subject, message, as_markdown=True):
    try:
        frappe.sendmail(
            recipients=recipient,
            sender="erp@sotb.bi",
            subject=subject,
            message=message,
            as_markdown=as_markdown,
            args=None 
        )
        frappe.msgprint("Email sent successfully!")
    except Exception as e:
        frappe.msgprint(f"Error sending email: {str(e)}")
        
    
######################################################################################################################
###########Enqueue the background job to send invoice data to OBR on retry button#####################################
######################################################################################################################
@frappe.whitelist(allow_guest=True)
def retry_sending_invoice(invoice_identifier):
    base_auth.authenticate()
    invoice_name = invoice_identifier.split('/')[-1].split()[0]
    invoice_type = "POS Invoice" if frappe.db.exists("POS Invoice", invoice_name) else "Sales Invoice"
    doc = frappe.get_doc(invoice_type, invoice_name)
    
    sales_invoice_data_processor = InvoiceDataProcessor(doc)
    invoice_data = sales_invoice_data_processor.prepare_invoice_data()

    if doc.is_return:
        invoice_data = sales_invoice_data_processor.prepare_credit_note_data(invoice_data)

        if doc.custom_creating_payment_entry == 1:
            invoice_data = sales_invoice_data_processor.prepare_reimbursement_deposit_data(invoice_data)

    if not doc.custom_einvoice_signatures:
        job_id = enqueue_retry_posting_sales_invoice(invoice_data, doc.name)
        return job_id
    else:
        frappe.throw("E-invoice already created for this invoice. Cannot retry sending invoice data to OBR.")
    doc.reload()

######################################################################################################################
###########Enqueue the background job to track stock movement on retry button#########################################
######################################################################################################################

@frappe.whitelist(allow_guest=True)
def retry_stock_movement_after_failure(doc_type, doc_name):

    doc = frappe.get_doc(doc_type, doc_name)
    
    frappe.msgprint(f"Retrying sending stock movement data to OBR for {doc.name}", alert=True)
    
    if doc.custom_etracker == 0:
        get_stock_ledger_send_data(doc_type, doc_name)
    else:
        frappe.throw("Stock movement already recorded by OBR")

def get_stock_ledger_send_data(doctype, doc_name):
    this_doc = frappe.get_doc(doctype, doc_name)
    for item in this_doc.items:
        stock_ledger_entry = frappe.get_all("Stock Ledger Entry", filters={"item_code": item.item_code, "voucher_no": doc_name}, fields=["*"])
        for stock_ledger in stock_ledger_entry:
            stock_ledger_doc = frappe.get_doc("Stock Ledger Entry", stock_ledger.name)
            from ..overrides.stock_ledger_entry import send_data
            send_data(stock_ledger_doc)

def get_user_email(doc):
    doc_owner=doc.owner
    user=frappe.get_doc("User", doc_owner)
    email=user.email
    return email
