# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import re
import frappe
from ..custom_exceptions import AuthenticationError, InvoiceAdditionError
from burundi_compliance.burundi_compliance.api_classes.base import OBRIntegrationBase
from burundi_compliance.burundi_compliance.api_classes.add_invoices import OBRInvoicePoster
class EBIMSSettings(Document):
	
	'''validate before saving the record'''
	def validate(self):
		for api_row in self.get("testing_apis"):
			api_url = api_row.get("api")
			api_method= api_row.get("method_name")
   
			'''Allow empty URLs without raising an exception'''
			if api_url and not self.is_valid_url(api_url):
				frappe.throw(f"Please enter a valid URL for the {api_method}")
			
	def is_valid_url(self, url):
		
		url_pattern = re.compile(
        r"^((https?|ftp|file):\/\/)?"
        + r"((([a-zA-Z\d]([a-zA-Z\d-]*[a-zA-Z\d])*)\.)+[a-zA-Z]{2,}|"
        + r"((\d{1,3}\.){3}\d{1,3}))"
        + r"(:\d+)?(\/[-a-zA-Z\d%_.~+]*)*"
        + r"(\?[;&a-z\d%_.~+=-]*)?"
        + r"(\#[-a-z\d_]*)?$",
        re.IGNORECASE,)

		if re.match(url_pattern, url):
			return True
		else:
			return False


# 	'''Test the API Classes'''
# # 	def onload(self):
			
# # 		# Create an instance of OBRIntegrationBase
# # 		obr_integration = OBRIntegrationBase()
# # 		# Call the instance method get_api_from_ebims_settings
# # 		login_url = obr_integration.get_api_from_ebims_settings("login")
# # 		if login_url:
# # 			pass		
# #    #frappe.msgprint(f"Login URL from EBIMS Settings: {login_url}")
# # 		else:
# # 			#frappe.msgprint("No login URL found in EBIMS Settings")
# # 			pass
# # 		# Test the authenticate method
# # 		try:
# # 			token = obr_integration.authenticate()
# # 			frappe.msgprint(f"Authentication successful. Token: {token}")
# # 		except AuthenticationError as e:
# # 			frappe.msgprint(f"Authentication failed: {str(e)}")

	def onload(self):
    # Create an instance of OBRIntegrationBase
		obr_integration_base = OBRIntegrationBase()

		# Example usage:
		try:
			# Assume token is obtained from OBRIntegrationBase.authenticate() method
			token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJveSIsImV4cCI6MTU4MjYyMDY1OX0.EMTwnke-M5PXV3LEEUveZLcvvi7pQmGUbWMAj2KeR94"
			obr_invoice_poster = OBRInvoicePoster(token)

			# Sample invoice data
			invoice_data = {
				"invoice_number": "0001/2021",
				"invoice_date": "2021-12-06 07:30:22",
				"invoice_type": "FN",
				"tp_type": "1",
				"tp_name": "NDIKUMANA JEAN MARIE",
				"tp_TIN": "4400773244",
				"tp_trade_number": "3333",
				"tp_phone_number": "70959595",
				"tp_address_commune": "BUJUMBURA",
				"tp_address_quartier": "GIKUNGU",
				"vat_taxpayer": "1",
				"ct_taxpayer": "0",
				"tl_taxpayer": "0",
				"tp_fiscal_center": "DGC",
				"tp_activity_sector": "SERVICE MARCHAND",
				"tp_legal_form": "suprl",
				"payment_type": "1",
				"invoice_currency": "BIF",
				"customer_name": "NGARUKIYINTWARI WAKA",
				"customer_TIN": "4100022020",
				"customer_address": "KIRUNDO",
				"vat_customer_payer": "1",
				"invoice_signature": "4400773244/ws440077324400027/20211206073022/0001/2021",
				"invoice_signature_date": "2021-12-06 07:30:22",
				"invoice_items": [
					{
						"item_designation": "ARTICLE ONE",
						"item_quantity": "10",
						"item_price": "500",
						"item_ct": "789",
						"item_tl": "123",
						"item_price_nvat": "5789",
						"vat": "1042.02",
						"item_price_wvat": "6831.02",
						"item_total_amount": "6954.02",
					},
					{
						"item_designation": "ARTICLE TWO",
						"item_quantity": "10",
						"item_price": "900",
						"item_ct": "0",
						"item_tl": "0",
						"item_price_nvat": "9000",
						"vat": "1620",
						"item_price_wvat": "10620",
						"item_total_amount": "10620",
					}
				]
			}

			result = obr_invoice_poster.post_invoice(invoice_data)
			frappe.msgprint(f"Invoice posted successfully! Result: {result}")
		except InvoiceAdditionError as e:
			frappe.msgprint(f"Error posting invoice: {str(e)}")
		except AuthenticationError as e:
			frappe.msgprint(f"Authentication failed: {str(e)}")

