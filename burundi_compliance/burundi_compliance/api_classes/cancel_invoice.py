# import requests
# from ..doctype.custom_exceptions import AuthenticationError, InvoiceCancellationError
# import frappe
# from .base import OBRAPIBase
# from requests.exceptions import RequestException
# import time as time
# from frappe.integrations.utils import make_post_request, make_get_request, create_request_log

# class InvoiceCanceller:

#     MAX_RETRIES = 1000
#     RETRY_DELAY_SECONDS = 10
    
#     def __init__(self, token):
#         obr_base = OBRAPIBase()
#         self.BASE_CANCEL_INVOICE_API_URL = obr_base.get_api_from_ebims_settings("cancel_invoice")
#         self.token = token

#     def _retry_request(self, data, retries):
#         try:
#             response = requests.post(self.BASE_CANCEL_INVOICE_API_URL, json=data, headers=self._get_headers())
#             response.raise_for_status()

#             '''Validate the response structure'''
#             if not response.json().get("success"):
#                 raise InvoiceCancellationError(f"Unexpected API response format: {response.text}")

#             return response.json()
#         except requests.exceptions.RequestException as e:
#             error_message = f"Error during API request: {str(e)}"
#             frappe.log_error(error_message, "InvoiceCanceller Request Error")
#             frappe.log_error(f"Response content: {response.text}")

#             '''Resend the cancel invoice request to OBR'''
#             if retries > 0:
#                 frappe.logger().warning(f"Retrying cancel invoice in {self.RETRY_DELAY_SECONDS} seconds... ({self.MAX_RETRIES - retries + 1}/{self.MAX_RETRIES})")
#                 time.sleep(self.RETRY_DELAY_SECONDS)
#                 return self._retry_request(data, retries - 1)
#             else:
#                 raise AuthenticationError(f"Max retries reached. {error_message}")
    
#     def _send_request(self, data):
#         try:
#             return self._retry_request(data, self.MAX_RETRIES)
#         except RequestException as e:
#             frappe.log_error(f"Error during API request: {str(e)}", title="InvoiceCanceller Request Error")
#             raise AuthenticationError(f"Error during API request: {str(e)}")

#     def _handle_response(self, response):
#         if response.get("success"):
#             return response["msg"]
#         else:
#             raise InvoiceCancellationError(response["msg"])

#     def _get_headers(self):
#         return {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.token}"
#         }

#     def cancel_invoice(self, data):
#         cancel_invoice_data = data
#         response = self._send_request(cancel_invoice_data)
#         return self._handle_response(response)
    
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
        invoice_identifier= data.get('invoice_identifier')
        get_invoices=frappe.get_all('Sales Invoice', filters={'custom_invoice_identifier': invoice_identifier}, fields=['name'])
        for get_invoice in get_invoices:
            doc=frappe.get_doc('Sales Invoice', get_invoice.get('name'))
            return doc
        
    