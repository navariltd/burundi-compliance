# tasks.py

from __future__ import unicode_literals
import frappe
from ..api_classes.base import OBRAPIBase
from frappe.utils.background_jobs import enqueue
import time as time
from ..utils.get_attemps_data import get_maximum_attempts
from ..doctype.custom_exceptions import AuthenticationError
base_auth = OBRAPIBase()
max_retries = int(get_maximum_attempts()["custom_maximum_attempts"])
retry_delay_seconds = int(get_maximum_attempts()["custom_retry_delay_seconds"])


'''RQ to post sales invoice'''
@frappe.whitelist(allow_guest=True)
def retry_sales_invoice_post(invoice_data, token, doc):
    from ..api_classes.add_invoices import SalesInvoicePoster
    retries = 0    

    while retries < max_retries:
        try:
            sales_invoice_poster = SalesInvoicePoster(token)
            result = sales_invoice_poster.post_invoice(invoice_data)
            frappe.msgprint(f"Invoice data sent to OBR successfully.")
            return
        except Exception as e:
            retries += 1
            frappe.log_error(f"Error during retry ({retries}/{max_retries}): {str(e)}")
            time.sleep(retry_delay_seconds)
            continue  

    frappe.log_error(f"Max retries reached. Unable to send invoice data to OBR.")
    
    '''send email to sales manager if max retries reached'''
    try:
        subject = f'Maximum retries reached. Unable to send invoice to OBR. '
        message="I hope this message finds you well.\n We regret to inform you that we have encountered difficulties in sending the sales invoice data to OBR (Office Burundais des Recettes).\nTo address this matter promptly, we kindly request that you reach out to OBR directly to confirm the issue and ensure a smooth resolution",
        send_max_retries_email("mania@navari.co.ke", subject, message, as_markdown=False)
    except Exception as e:
        frappe.msgprint(f"Error sending emails: {str(e)}")


'''RQ to Update stock'''
@frappe.whitelist(allow_guest=True)
def retry_stock_movement(data):
    from ..api_classes.add_stock_movement import TrackStockMovement
    retries = 0
    while retries < max_retries:
        try:
            token = base_auth.authenticate()
            stock_movement = TrackStockMovement(token)
            result = stock_movement.post_stock_movement(data)
            frappe.msgprint(f"Stock movement data sent to OBR")
            return 
        except Exception as e:
            frappe.log_error(f"Error during retry ({retries + 1}/{max_retries}): {str(e)}")
            retries += 1
            time.sleep(retry_delay_seconds)
            continue  # Continue to the next iteration of the loop
    frappe.log_error(f"Max retries reached. Unable to send invoice data to OBR.")
    
    '''send email to sales manager if max retries reached'''
    try:
        subject = f'Maximum retries reached. Unable to send invoice to OBR. '
        message="I hope this message finds you well.\n We regret to inform you that we have encountered difficulties in sending the sales invoice data to OBR (Office Burundais des Recettes).\nTo address this matter promptly, we kindly request that you reach out to OBR directly to confirm the issue and ensure a smooth resolution",
        send_max_retries_email("mania@navari.co.ke", subject, message, as_markdown=False)
    except Exception as e:
        frappe.msgprint(f"Error sending emails: {str(e)}")


'''RQ to cancel invoice'''
@frappe.whitelist(allow_guest=True)
def retry_cancel_invoice(invoice_number):
    from ..api_classes.cancel_invoice import CancelInvoice
    retries = 0

    while retries < max_retries:
        try:
            token = base_auth.authenticate()
            cancel_invoice = CancelInvoice(token)
            result = cancel_invoice.cancel_invoice(invoice_number)
            frappe.msgprint(f"Invoice cancellation request sent to OBR successfully.")
            return
        except Exception as e:
            frappe.log_error(f"Error during retry ({retries + 1}/{max_retries}): {str(e)}")
            retries += 1
            time.sleep(retry_delay_seconds)
            continue  # Continue to the next iteration of the loop

    frappe.log_error(f"Max retries reached. Unable to send invoice cancellation request to OBR.")
    
    '''send email to sales manager if max retries reached'''
    try:
        subject = f'Maximum retries reached. Unable to send invoice to OBR. '
        message="I hope this message finds you well.\n We regret to inform you that we have encountered difficulties in updating the stock to OBR (Office Burundais des Recettes).\nTo address this matter promptly, we kindly request that you reach out to OBR directly to confirm the issue and ensure a smooth resolution",
        send_max_retries_email("mania@navari.co.ke", subject, message, as_markdown=False)
    except Exception as e:
        frappe.msgprint(f"Error sending emails: {str(e)}")

def send_max_retries_email(recipient, subject, message, as_markdown=True):
    try:
        frappe.sendmail(
            recipients=recipient,
            sender="admin@sotb.bi",
            subject=subject,
            message=message,
            as_markdown=as_markdown,
            args=None 
        )
        frappe.msgprint("Email sent successfully!")
    except Exception as e:
        frappe.msgprint(f"Error sending email: {str(e)}")
        
# Example retry_authentication function
def retry_authentication(max_retries=2, retry_delay_seconds=3):
    retries = 0

    while retries < max_retries:
        try:
            obr_api = OBRAPIBase()
            obr_api.authenticate_with_retry()
            frappe.msgprint(f"Authentication successful after {retries+1} retry.")
            return  # Exit the loop if authentication is successful
        except AuthenticationError as auth_error:
            frappe.log_error(f"Retries {retries+1}")
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

def retry_cancel_invoice_post(invoice_data, token, doc):
    from ..api_classes.cancel_invoice import InvoiceCanceller
    retries = 0    

    while retries < max_retries:
        try:
            invoice_canceller = InvoiceCanceller(token)
            response = invoice_canceller.cancel_invoice(invoice_data)
            frappe.msgprint(f"Invoice data sent to OBR successfully.")
            return
        except Exception as e:
            retries += 1
            frappe.log_error(f"Error during retry ({retries}/{max_retries}): {str(e)}")
            time.sleep(retry_delay_seconds)
            continue  

    frappe.log_error(f"Max retries reached. Unable to send invoice data to OBR.")
    
    '''send email to sales manager if max retries reached'''
    try:
        subject = f'Maximum retries reached. Unable to send invoice to OBR. '
        message="I hope this message finds you well.\n We regret to inform you that we have encountered difficulties in Cancelling the sales invoice data to OBR (Office Burundais des Recettes).\nTo address this matter promptly, we kindly request that you reach out to OBR directly to confirm the issue and ensure a smooth resolution",
        send_max_retries_email("mania@navari.co.ke", subject, message, as_markdown=False)
    except Exception as e:
        frappe.msgprint(f"Error sending emails: {str(e)}")
'''enqueue stock'''
def enqueue_stock_movement(data):
    frappe.enqueue('burundi_compliance.burundi_compliance.utils.background_jobs.retry_stock_movement', data=data, queue='long', is_async=True)