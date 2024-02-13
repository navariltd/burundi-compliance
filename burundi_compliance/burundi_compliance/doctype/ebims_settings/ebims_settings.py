# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import re
import frappe
# from ..custom_exceptions import AuthenticationError, InvoiceAdditionError
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
# from burundi_compliance.burundi_compliance.api_classes.add_invoices import SalesInvoicePoster
# from burundi_compliance.burundi_compliance.api_classes.check_tin import TinVerifier

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
	# def onload(self):
			
	# 	# Create an instance of OBRIntegrationBase
	# 	obr_integration = OBRAPIBase()
	# 	# Call the instance method get_api_from_ebims_settings
	# 	login_url = obr_integration.get_api_from_ebims_settings("login")
	# 	if login_url:
	# 		pass		
	# 	else:
	# 		pass
	# 	try:
	# 		token = obr_integration.authenticate()
	# 		frappe.msgprint(f"Authentication successful. Token: {token}")
	# 	except AuthenticationError as e:
	# 		frappe.msgprint(f"Authentication failed: {str(e)}")


	# def onload(self):
    # # Check Tin
	# 	obr_integration = OBRAPIBase()
	# 	tin = {"tp_TIN": "4001040247"}
	# 	token = obr_integration.authenticate()
	# 	frappe.msgprint(f"Authentication successful. Token: {token}")

	# 	tin_verifier = TinVerifier(token)
	# 	try:
	# 		result = tin_verifier.check_tin(tin)
	# 		frappe.msgprint(f"Check TIN result: {result}")
	# 	except Exception as e:
	# 		frappe.msgprint(f"Error checking TIN: {str(e)}")

		