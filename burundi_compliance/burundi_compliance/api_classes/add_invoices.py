import requests
import time
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from .base import OBRAPIBase
from requests.exceptions import RequestException

from PIL import Image

class SalesInvoicePoster:

    MAX_RETRIES = 1
    RETRY_DELAY_SECONDS = 1

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
            
            if not response.json().get("success"):
                frappe.log_error(f"Unexpected API response format: {response.text}")
                raise InvoiceAdditionError(f"Unexpected API response format: {response.text}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, "SalesInvoicePoster Request Error")
            frappe.log_error(f"Response content: {response.text}")
            
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
            raise InvoiceAdditionError(f"Error during API request: {str(e)}")

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

 

    def update_sales_invoice(self, response):
        try:
            invoice_number = response.get("result", {}).get("invoice_number")
            electronic_signature = response.get("electronic_signature")
            invoice_registered_no=response.get("result", {}).get("invoice_registered_number")
            invoice_registered_date=response.get("result", {}).get("invoice_registered_date")
            sales_invoice = frappe.get_doc("Sales Invoice", invoice_number)

            # Update Sales Invoice fields
            sales_invoice.custom_einvoice_signatures = electronic_signature
            sales_invoice.custom_invoice_registered_no = invoice_registered_no
            sales_invoice.custom_invoice_registered_date = invoice_registered_date
            
            sales_invoice.save()

            frappe.msgprint(f"Sales Invoice {invoice_number} updated successfully.{sales_invoice.custom_einvoice_signatures}")
        except Exception as e:
            frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")


    def generate_qr_code(data, file_path):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)

    # def update_sales_invoice(self, response):
    #     try:
    #         invoice_number = response.get("result", {}).get("invoice_number")
    #         electronic_signature = response.get("electronic_signature")
    #         invoice_registered_no = response.get("result", {}).get("invoice_registered_number")
    #         invoice_registered_date = response.get("result", {}).get("invoice_registered_date")
    #         sales_invoice = frappe.get_doc("Sales Invoice", invoice_number)

    #         # Update Sales Invoice fields
    #         sales_invoice.custom_einvoice_signatures = electronic_signature
    #         sales_invoice.custom_invoice_registered_no = invoice_registered_no
    #         sales_invoice.custom_invoice_registered_date = invoice_registered_date

    #         # Generate QR code and save it to a file
    #         qr_code_data = f"Invoice Number: {invoice_number}\nSignature: {electronic_signature}"
    #         file_path = f"/path/to/store/qr_codes/{invoice_number}_qr.png"
    #         self.generate_qr_code(qr_code_data, file_path)

    #         # Upload the QR code image to the 'custom_qr_code' field
    #         sales_invoice.custom_qr_code = frappe.attach_file(file_path)

    #         sales_invoice.save()

    #         frappe.msgprint(f"Sales Invoice {invoice_number} updated successfully with QR code.")
    #     except Exception as e:
    #         frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")
