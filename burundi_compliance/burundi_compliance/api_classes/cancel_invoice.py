import requests
import json
import frappe
from frappe.integrations.utils import make_post_request, create_request_log
from .base import OBRAPIBase

class InvoiceCanceller:

    def __init__(self, token: str):
        obr_base = OBRAPIBase()
        self.BASE_CANCEL_INVOICE_API_URL = obr_base.get_api_from_ebims_settings("cancel_invoice")
        self.token = token

    def _create_integration_request(self, response,data, status):
        create_request_log(data,
                integration_type=None,
                service_name="eBMS Invoice Cancellation",
                error=response.get("msg"),
                url=self.BASE_CANCEL_INVOICE_API_URL,
                request_headers=self._get_headers(),
                output=response,
                reference_doctype="Sales Invoice",
                reference_docname=self.get_invoice(data),
                status=status
            )
    
    def _handle_response(self, response, data):
        success = response.get("success")
        if success:
            self._create_integration_request(response, data, status="Completed")
            self.update_invoice(data)
        else:
            self._create_integration_request(response, data, status="Failed")
        return response
            
    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def cancel_invoice(self, data) -> dict:
        try:
            response = requests.post(
                self.BASE_CANCEL_INVOICE_API_URL,
                json=data,
                headers=self._get_headers()
            ).json()
            return self._handle_response(response, data)
            
        except Exception as e:
            frappe.log_error(f"Error during API request: {str(e)}")

    def get_invoice(self, data):
        invoice_identifier= data.get('invoice_signature')
        _invoices=frappe.get_all('Sales Invoice', filters={'custom_invoice_identifier': invoice_identifier}, fields=['name'])
        for _invoice in _invoices:
            doc=frappe.get_doc('Sales Invoice', _invoice.get('name'))
            return doc
        
    def update_invoice(self, data):
        doc=self.get_invoice(data)
        frappe.db.set_value('Sales Invoice', doc.name, 'custom_ebms_invoice_cancelled',1)
        frappe.db.commit()