# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import re
import frappe
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
import requests
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


	# def onload(self):
		
	# 		# initializing URL
	# 	url = "https://www.geeksforgeeks.org"
	# 	timeout = 30
	# 	try:
	# 		# requesting URL
	# 		request = requests.get(url,
	# 							timeout=timeout)
	# 		frappe.msgprint("Internet is on")
		
	# 	# catching exception
	# 	except (requests.ConnectionError,
	# 			requests.Timeout) as exception:
	# 		frappe.msgprint("Internet is off")