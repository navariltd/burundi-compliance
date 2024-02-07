# API_CLASSES/base.py

import requests
from frappe import _
import frappe
from ..doctype.custom_exceptions import AuthenticationError

class OBRAPIBase:
            
    def __init__(self):
        self.BASE_LOGIN_URL = self.get_api_from_ebims_settings("login")  # Move it here


    '''generate token for other methods'''
    def authenticate(self):
        auth_details = self.get_auth_details()
        login_url = f"{self.BASE_LOGIN_URL}"  # Use self.BASE_LOGIN_URL
        headers = {"Content-Type": "application/json"}
        data = {"username": auth_details["username"], "password": ""}
         #data = {"username": auth_details["username"], "password": auth_details["password"]}

        try:
            response = requests.post(login_url, json=data, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            result = response.json()

            if result.get("success"):
                return result["result"]["token"]
            else:
                raise AuthenticationError(result["msg"])

        except requests.exceptions.RequestException as e:
            error_message = f"Error during authentication: {str(e)}"
            frappe.log_error(error_message, "OBRAPIBase Authentication Error")
            raise AuthenticationError(error_message)


    def get_auth_details(self):
        ebims_settings = frappe.get_doc("EBIMS Settings")
        auth_details = {
            "username": ebims_settings.username,
            "password": ebims_settings.password,
            "environment": ebims_settings.environment,
            "tp_legal_form": ebims_settings.taxpayers_legal_form,
            "tp_activity_sector": ebims_settings.taxpayers_sector_of_activity,
            "system_identification_given_by_obr":ebims_settings.system_identification_given_by_obr
        }
        return auth_details


    def get_api_from_ebims_settings(self, method_name):
        ebims_settings = frappe.get_doc("EBIMS Settings")
        for api_row in ebims_settings.get("testing_apis"):
            if api_row.get("method_name") == method_name:
                return api_row.get("api")
        return None


