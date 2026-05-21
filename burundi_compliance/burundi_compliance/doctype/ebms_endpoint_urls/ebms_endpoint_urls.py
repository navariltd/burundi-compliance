# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class eBMSEndpointURLs(Document):
    def before_insert(self):
        if frappe.db.exists("eBMS Endpoint URLs", self.environment):
            frappe.throw(
                f"Endpoint URLs for environment '{self.environment}' already exists. Please update the existing record instead of creating a new one.",
                title="Duplicate Environment",
            )
