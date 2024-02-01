import requests
import time
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from .base import OBRAPIBase
from requests.exceptions import RequestException

class SalesInvoicePoster:

    MAX_RETRIES = 5
    RETRY_DELAY_SECONDS = 2

    def __init__(self, token, max_retries=5, retry_delay_seconds=2):
        obr_base = OBRAPIBase()
        self.BASE_ADD_INVOICE_API_URL = obr_base.get_api_from_ebims_settings("add_invoice")
        self.token = token
        self.MAX_RETRIES = max_retries
        self.RETRY_DELAY_SECONDS = retry_delay_seconds


    def _retry_request(self, data, retries):
        try:
            response = requests.post(self.BASE_ADD_INVOICE_API_URL, json=data, headers=self._get_headers())
            response.raise_for_status()

            '''Validate the response structure'''
            if not response.json().get("success"):
                raise InvoiceAdditionError(f"Unexpected API response format: {response.text}")

            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, "SalesInvoicePoster Request Error")
            
            '''Resend the e-invoice to OBR'''
            if retries > 0:
                frappe.logger().warning(f"Retrying in {self.RETRY_DELAY_SECONDS} seconds... ({self.MAX_RETRIES - retries + 1}/{self.MAX_RETRIES})")
                time.sleep(self.RETRY_DELAY_SECONDS)
                return self._retry_request(data, retries - 1)
            else:
                raise AuthenticationError(f"Max retries reached. {error_message}")


    def _send_request(self, data):
        try:
            return self._retry_request(data, self.MAX_RETRIES)
        except RequestException as e:
            frappe.log_error(f"Error during API request: {str(e)}", title="SalesInvoicePoster Request Error")
            raise AuthenticationError(f"Error during API request: {str(e)}")

    def _handle_response(self, response):
        if response.get("success"):
            self.update_sales_invoice(response)
            return response["result"]
        else:
            raise InvoiceAdditionError(response["msg"])

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def post_invoice(self, invoice_data):
        response = self._send_request(invoice_data)
        return self._handle_response(response)


    '''To be tested later'''
    def update_sales_invoice(response):
        try:
            # Update fields from the response
            electronic_signature = response.get("electronic_signature")
            result_data = response.get("result", {})
            
            invoice_number = result_data.get("invoice_number")
            invoice_registered_number = result_data.get("invoice_registered_number")
            
            sales_invoice = frappe.get_doc("Sales Invoice", invoice_number)

            # Update Sales Invoice fields, ensure to create this field in the app, once person install the app wil have it there sales invoice
            sales_invoice.custom_einvoice_signature = electronic_signature #

            sales_invoice.save()

            frappe.msgprint(f"Sales Invoice {invoice_number} updated successfully.")
        except Exception as e:
            frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")
    






































    '''
    def generate_qr_code(self, data, filename):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)'''