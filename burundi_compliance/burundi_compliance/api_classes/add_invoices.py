import requests
import time
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from .base import OBRAPIBase
from requests.exceptions import RequestException
from ..utils.base_api import full_api_url

import time
import requests
from requests.exceptions import RequestException, ConnectionError
class SalesInvoicePoster:


    def __init__(self, token, max_retries=1, retry_delay_seconds=2):
        obr_base = OBRAPIBase()
        self.BASE_ADD_INVOICE_API_URL = full_api_url(obr_base.get_api_from_ebims_settings("add_invoice"))
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

    def _send_request(self, data):
        try:
            return self._retry_request(data, self.MAX_RETRIES)
        except RequestException as e:
            frappe.log_error(f"Error during API request: {str(e)}", title="SalesInvoicePoster Request Error")
            raise InvoiceAdditionError(f"Error during API request: {str(e)}")

    def _handle_response(self, response):
        if response.get("success"):
            self.update_sales_invoice(response)
            return response
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
# from ..utils.background_jobs import retry_sales_invoice_post
# from frappe.utils.background_jobs import enqueue

# from ..utils.base_api import full_api_url

# import time
# import requests
# from requests.exceptions import RequestException, ConnectionError
# class SalesInvoicePoster:


# 	def __init__(self, token, max_retries=1, retry_delay_seconds=2):
# 		obr_base = OBRAPIBase()
# 		self.BASE_ADD_INVOICE_API_URL = full_api_url(obr_base.get_api_from_ebims_settings("add_invoice"))
# 		self.token = token
# 		self.MAX_RETRIES = max_retries
# 		self.RETRY_DELAY_SECONDS = retry_delay_seconds

# 	def _retry_request(self, data, retries):
# 		# response = None
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
# 			# frappe.log_error(f"Response content: {response.text}")
		   		   
# 			if retries > 0:
# 				frappe.logger().warning(f"Retrying in {self.RETRY_DELAY_SECONDS} seconds... ({self.MAX_RETRIES - retries + 1}/{self.MAX_RETRIES})")
# 				time.sleep(self.RETRY_DELAY_SECONDS)
# 				return self._retry_request(data, retries - 1)
# 			else:
# 				raise AuthenticationError(f"Max retries reached. {error_message}")

# 	def _send_request(self, data):
# 		try:
# 			return self._retry_request(data, self.MAX_RETRIES)
# 		except RequestException as e:
# 			frappe.log_error(f"Error during API request: {str(e)}", title="SalesInvoicePoster Request Error")
# 			frappe.msgprint("Server down. Retrying in the background.")
# 			self.enqueue_retry_job(data)
# 			raise AuthenticationError(f"Error during API request: {str(e)}")

# 	def enqueue_retry_job(self, data):
# 		frappe.enqueue(
#             method="your_app.module.retry_sales_invoice_post",  # Provide the correct path
#             queue='long',
#             timeout=3000,
#             is_async=True,
#             **{"invoice_data": data, "token": self.token}  # Pass additional parameters
#         )


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

 
# 	'''Update Sales Invoice with the electronic signature 
# 		and the registered number and date of the invoice.'''
		
# 	def update_sales_invoice(self, response):
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
# 		except Exception as e:
# 			frappe.db.rollback()
# 			frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")
