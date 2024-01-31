# API_CLASSES/base.py

import requests
from frappe import _
import frappe
from ..doctype.custom_exceptions import AuthenticationError

class OBRIntegrationBase:
            
    def __init__(self):
        self.BASE_LOGIN_URL = self.get_api_from_ebims_settings("login")  # Move it here

    def authenticate(self):
        username, password, environment = self.get_auth_details()
        login_url = f"{self.BASE_LOGIN_URL}"  # Use self.BASE_LOGIN_URL
        headers = {"Content-Type": "application/json"}
        data = {"username": username, "password": password}

        try:
            response = requests.post(login_url, json=data, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            result = response.json()

            if result.get("success"):
                return result["result"]["token"]
            else:
                raise AuthenticationError(result["msg"])

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(_("Error during authentication: {0}").format(str(e)))

    def get_auth_details(self):
        ebims_settings = frappe.get_doc("EBIMS Settings")
        username=ebims_settings.username
        password=ebims_settings.password
        environment=ebims_settings.environment
        return username,password, environment

    def get_api_from_ebims_settings(self, method_name):
        ebims_settings = frappe.get_doc("EBIMS Settings")
        for api_row in ebims_settings.get("testing_apis"):
            if api_row.get("method_name") == method_name:
                return api_row.get("api")
        return None


