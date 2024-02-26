# tasks.py

from __future__ import unicode_literals
import frappe
from ..api_classes.base import OBRAPIBase
from frappe.utils.background_jobs import enqueue

base_auth = OBRAPIBase()
@frappe.whitelist()
def retry_sales_invoice_post(invoice_data, token,doc):
    from ..api_classes.add_invoices import SalesInvoicePoster
    from ..api_classes.add_stock_movement import TrackStockMovement
    
    try:
        sales_invoice_poster = SalesInvoicePoster(token)
        result = sales_invoice_poster.post_invoice(invoice_data)
        frappe.msgprint(f"Invoice data sent to OBR")
    except Exception as e:
        frappe.log_error(f"Error during retry: {str(e)}")

        # Check if the document is submitted
        doc = frappe.get_doc("Sales Invoice", invoice_data.get("invoice_number"))
        if doc.docstatus == 1:  # Submitted
            frappe.log_error(f"Invoice {invoice_data.get('invoice_number')} submitted despite the error.")
            return

        # Continue with retry
        frappe.enqueue(
            method="your_app.module.retry_sales_invoice_post",  # Provide the correct path
            queue='long',
            timeout=3000,
            is_async=True,
            **{"invoice_data": invoice_data, "token": token}  # Pass additional parameters
        )


@frappe.whitelist()
def retry_stock_movement(data):
    from ..api_classes.add_invoices import SalesInvoicePoster
    from ..api_classes.add_stock_movement import TrackStockMovement
    try:
        token = base_auth.authenticate()
        stock_movement = TrackStockMovement(token)
        result = stock_movement.post_stock_movement(data)
        frappe.msgprint(f"Stock movement data sent to OBR")
    except Exception as e:
        frappe.log_error(f"Error during retry: {str(e)}")
