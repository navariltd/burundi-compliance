import requests
import time
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from .base import OBRAPIBase
from requests.exceptions import RequestException
import socket


import time
import requests
from requests.exceptions import RequestException, ConnectionError
class SalesInvoicePoster:


    def __init__(self, token, max_retries=100, retry_delay_seconds=2):
        obr_base = OBRAPIBase()
        self.BASE_ADD_INVOICE_API_URL = obr_base.get_api_from_ebims_settings("add_invoice")
        self.token = token
        self.MAX_RETRIES = max_retries
        self.RETRY_DELAY_SECONDS = retry_delay_seconds

    def _retry_request(self, data, retries):
        response = None
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
    # ...

    # def _retry_request(self, data, retries):
    #     response = "Many"
    #     try:
    #         response = requests.post(self.BASE_ADD_INVOICE_API_URL, json=data, headers=self._get_headers())
    #         response.raise_for_status()

    #         if not response.json().get("success"):
    #             frappe.log_error(f"Unexpected API response format: {response.text}")
    #             raise InvoiceAdditionError(f"Unexpected API response format: {response.text}")

    #         return response.json()
    #     except ConnectionError as ce:
    #         # Handle connection errors specifically
    #         frappe.logger().warning("Connection error. Retrying in {} seconds... "
    #                                 "({}/{})".format(self.RETRY_DELAY_SECONDS,
    #                                                 self.MAX_RETRIES - retries + 1,
    #                                                 self.MAX_RETRIES))
    #     except RequestException as e:
    #         # Catching more general RequestException to handle other errors
    #         error_message = f"Error during API request: {str(e)}"
    #         frappe.log_error(error_message, "SalesInvoicePoster Request Error")
    #         frappe.log_error(f"Response content: {response.text}")

    #         if isinstance(e, socket.gaierror):
    #             # Handle DNS resolution errors
    #             frappe.logger().warning("Name resolution error. Retrying in {} seconds... "
    #                                     "({}/{})".format(self.RETRY_DELAY_SECONDS,
    #                                                     self.MAX_RETRIES - retries + 1,
    #                                                     self.MAX_RETRIES))
    #         elif retries > 0:
    #             frappe.logger().warning("Retrying in {} seconds... ({}/{})".format(self.RETRY_DELAY_SECONDS,
    #                                                                                 self.MAX_RETRIES - retries + 1,
    #                                                                                 self.MAX_RETRIES))
    #             time.sleep(self.RETRY_DELAY_SECONDS)
    #             return self._retry_request(data, retries - 1)
    #         else:
    #             raise AuthenticationError(f"Max retries reached. {error_message}")
    #             # Ensure the retry continues even for non-DNS resolution errors
               



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

 
    '''Update Sales Invoice with the electronic signature 
        and the registered number and date of the invoice.'''
		
    def update_sales_invoice(self, response):
        try:
            invoice_number = response.get("result", {}).get("invoice_number")
            electronic_signature = response.get("electronic_signature")
            invoice_registered_no = response.get("result", {}).get("invoice_registered_number")
            invoice_registered_date = response.get("result", {}).get("invoice_registered_date")
            sales_invoice = frappe.get_doc("Sales Invoice", invoice_number)

            # Update Sales Invoice fields
            sales_invoice.custom_einvoice_signatures = electronic_signature
            sales_invoice.custom_invoice_registered_no = invoice_registered_no
            sales_invoice.custom_invoice_registered_date = invoice_registered_date

            # Save the Sales Invoice
            sales_invoice.save()
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
            frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")

# import requests
# import time
# from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
# import frappe
# from .base import OBRAPIBase
# from requests.exceptions import RequestException

# from PIL import Image
# import qrcode
# import io
# import sys
# class SalesInvoicePoster:


# 	def __init__(self, token, max_retries=1, retry_delay_seconds=1):
# 		obr_base = OBRAPIBase()
# 		self.BASE_ADD_INVOICE_API_URL = obr_base.get_api_from_ebims_settings("add_invoice")
# 		self.token = token
# 		self.MAX_RETRIES = max_retries
# 		self.RETRY_DELAY_SECONDS = retry_delay_seconds

# 	def _retry_request(self, data, retries):
# 		'''Retry the request if it fails. If the request fails after the maximum number of retries,'''
  
# 		try:
# 			response = requests.post(self.BASE_ADD_INVOICE_API_URL, json=data, headers=self._get_headers())
# 			response.raise_for_status()
			
# 			if not response.json().get("success"):
# 				frappe.log_error(f"Unexpected API response format: {response.text}")
# 				raise InvoiceAdditionError(f"Unexpected API response format: {response.text}")
			
# 			return response.json()
# 		except requests.exceptions.RequestException as e:
# 			error_message = f"Error during API request: {str(e)}"
# 			frappe.log_error(error_message, "SalesInvoicePoster Request Error")

			
# 			if retries > 0:
# 				frappe.logger().warning(f"Retrying in {self.RETRY_DELAY_SECONDS} seconds... ({self.MAX_RETRIES - retries + 1}/{self.MAX_RETRIES})")
# 				time.sleep(self.RETRY_DELAY_SECONDS)
# 				return self._retry_request(data, retries - 1)
# 			else:
# 				if isinstance(e, requests.exceptions.HTTPError):
# 					raise AuthenticationError(f"Max retries reached. {error_message}")
# 				else:
# 					raise InvoiceAdditionError(f"Unexpected error during API request: {str(e)}")

# 	def _send_request(self, data):
# 		'''Send the request to the API and handle any errors that occur.'''
# 		try:
# 			return self._retry_request(data, self.MAX_RETRIES)
# 		except RequestException as e:
# 			frappe.log_error(f"Error during API request: {str(e)}", title="SalesInvoicePoster Request Error")
# 			raise InvoiceAdditionError(f"Error during API request: {str(e)}")

# 	def _handle_response(self, response):
# 		if response.get("success"):
# 			self.update_sales_invoice(response)
# 			return response["result"]
# 		else:
# 			raise InvoiceAdditionError(response["msg"])

# 	def _get_headers(self):
# 		return {
# 			"Content-Type": "application/json",
# 			"Authorization": f"Bearer {self.token}"
# 		}

# 	def post_invoice(self, invoice_data):
# 		response = self._send_request(invoice_data)
# 		return self._handle_response(response)


		
# 	def update_sales_invoice(self, response):
     
		
# 		'''Update Sales Invoice with the electronic signature'''
# 		try:
# 			invoice_number = response.get("result", {}).get("invoice_number")
# 			electronic_signature = response.get("electronic_signature")
# 			invoice_registered_no = response.get("result", {}).get("invoice_registered_number")
# 			invoice_registered_date = response.get("result", {}).get("invoice_registered_date")
# 			sales_invoice = frappe.get_doc("Sales Invoice", invoice_number)

# 			# Update Sales Invoice fields
# 			sales_invoice.custom_einvoice_signatures = electronic_signature
# 			sales_invoice.custom_invoice_registered_no = invoice_registered_no
# 			sales_invoice.custom_invoice_registered_date = invoice_registered_date

# 			# Save the Sales Invoice
# 			sales_invoice.save()
# 			frappe.db.commit()
   
# 			'''reload the page to show the updated invoice'''
# 			sales_invoice.reload()
# 			return sales_invoice
# 		except Exception as e:
# 			frappe.db.rollback()
# 			frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")

