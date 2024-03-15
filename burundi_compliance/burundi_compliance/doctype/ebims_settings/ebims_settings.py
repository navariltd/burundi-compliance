# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ...api_classes.base import OBRAPIBase
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase

from ...utils.base_api import full_api_url

obr_base=OBRAPIBase()
class eBIMSSettings(Document):
	pass

	# def onload(self):
	# 	frappe.throw(obr_base.authenticate())
 
		
