# # API_CLASSES/base.py

# import requests
# from frappe import _
# import frappe
# from ..doctype.custom_exceptions import AuthenticationError

# class OBRAPIBase:
            
#     def __init__(self):
#         self.BASE_LOGIN_URL = self.get_api_from_ebims_settings("login")  # Move it here


#     '''generate token for other methods'''
#     def authenticate(self):
        
#         auth_details = self.get_auth_details()
#         login_url = f"{self.BASE_LOGIN_URL}"  # Use self.BASE_LOGIN_URL
#         headers = {"Content-Type": "application/json"}
#         data = {"username": auth_details["username"], "password": "|7:%AnXy"}
        
#         try:
#             response = requests.post(login_url, json=data, headers=headers)
#             response.raise_for_status()  # Raise an HTTPError for bad responses
#             result = response.json()
           
#             if result.get("success"):
#                 return result["result"]["token"]
#             else:
#                 raise AuthenticationError(result["msg"])

#         except requests.exceptions.RequestException as e:
#             error_message = f"Error during authentication: {str(e)}"
#             frappe.log_error(error_message, "OBRAPIBase Authentication Error")
#             raise AuthenticationError(error_message)


#     def get_auth_details(self):
#         ebims_settings = frappe.get_doc("EBIMS Settings")
#         auth_details = {
#             "username": ebims_settings.username,
#             "password": ebims_settings.password,
#             "environment": ebims_settings.environment,
#             "tp_legal_form": ebims_settings.taxpayers_legal_form,
#             "tp_activity_sector": ebims_settings.taxpayers_sector_of_activity,
#             "system_identification_given_by_obr":ebims_settings.system_identification_given_by_obr
#         }
#         return auth_details


#     def get_api_from_ebims_settings(self, method_name):
#         ebims_settings = frappe.get_doc("EBIMS Settings")
#         for api_row in ebims_settings.get("testing_apis"):
#             if api_row.get("method_name") == method_name:
#                 return api_row.get("api")
#         return None


# API_CLASSES/base.py
# API_CLASSES/base.py


# import requests
# import frappe
# from ..doctype.custom_exceptions import AuthenticationError
# import time
# import socket

# class NetworkError(Exception):
#     pass

# class OBRAPIBase:

#     def __init__(self):
#         self.BASE_LOGIN_URL = self.get_api_from_ebims_settings("login")
#         self.MAX_RETRIES = 1
#         self.RETRY_DELAY_SECONDS = 2

#     def authenticate(self):
#         auth_details = self.get_auth_details()
#         login_url = f"{self.BASE_LOGIN_URL}"
#         headers = {"Content-Type": "application/json"}
#         data = {"username": auth_details["username"], "password": "|7:%AnXy"}

#         for retry in range(self.MAX_RETRIES):
#             try:
#                 # Check network connection before making the request
#                 self._check_network_connection(login_url)

#                 token = self._retry_request(login_url, data, headers)
#                 frappe.throw(str(token))
#                 return token

#             except AuthenticationError as e:
#                 frappe.logger().warning(f"{str(e)}. Retrying in {self.RETRY_DELAY_SECONDS} seconds... "
#                                         "({}/{})".format(retry + 1, self.MAX_RETRIES))
#                 time.sleep(self.RETRY_DELAY_SECONDS)

#             except NetworkError as ne:
#                 frappe.logger().warning(f"{str(ne)}. Retrying in {self.RETRY_DELAY_SECONDS} seconds... "
#                                         "({}/{})".format(retry + 1, self.MAX_RETRIES))
#                 time.sleep(self.RETRY_DELAY_SECONDS)

#         raise AuthenticationError(f"Max retries reached. Unable to establish network connection.")

#     def _check_network_connection(self, url):
#         # Use socket to check if the host is reachable
#         host = url.split("//")[1].split("/")[0]
#         try:
#             socket.create_connection((host, 80), timeout=1)
#         except OSError:
#             raise NetworkError("Network connection error: Host is not reachable.")

#     def _retry_request(self, url, data, headers):
#         for retry in range(self.MAX_RETRIES):
#             try:
#                 response = requests.post(url, json=data, headers=headers)
#                 response.raise_for_status()
#                 result = response.json()
#                 if result.get("success"):
#                     return result["result"]["token"]
#                 else:
#                     raise AuthenticationError(result["msg"])

#             except requests.exceptions.RequestException as e:
#                 error_message = f"Error during request: {str(e)}"
#                 frappe.log_error(error_message, "OBRAPIBase Request Error")
#                 if retry < self.MAX_RETRIES - 1:
#                     frappe.logger().warning(f"Retrying in {self.RETRY_DELAY_SECONDS} seconds... "
#                                             "({}/{})".format(retry + 1, self.MAX_RETRIES))
#                     time.sleep(self.RETRY_DELAY_SECONDS)
#                 else:
#                     raise NetworkError(f"Max retries reached. {error_message}")

#     def get_auth_details(self):
#         ebims_settings = frappe.get_doc("EBIMS Settings")
#         auth_details = {
#             "username": ebims_settings.username,
#             "password": ebims_settings.password,
#             "environment": ebims_settings.environment,
#             "tp_legal_form": ebims_settings.taxpayers_legal_form,
#             "tp_activity_sector": ebims_settings.taxpayers_sector_of_activity,
#             "system_identification_given_by_obr": ebims_settings.system_identification_given_by_obr
#         }
#         return auth_details

#     def get_api_from_ebims_settings(self, method_name):
#         ebims_settings = frappe.get_doc("EBIMS Settings")
#         for api_row in ebims_settings.get("testing_apis"):
#             if api_row.get("method_name") == method_name:
#                 return api_row.get("api")
#         return None

import requests
import time  # Import the time module
from frappe import _
import frappe
from ..doctype.custom_exceptions import AuthenticationError

class OBRAPIBase:
            
    def __init__(self):
        self.BASE_LOGIN_URL = self.get_api_from_ebims_settings("login")

    def check_internet_connection(self):
        try:
            requests.get("http://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def authenticate(self, max_retries=1000):
        retries = 0
        while retries < max_retries:
            if self.check_internet_connection():
                try:
                    frappe.msgprint('Network available')
                    return self.authenticate_with_retry()
                except AuthenticationError as auth_error:
                    # Handle authentication error, if needed
                    frappe.log_error(str(auth_error), "Authentication Error")
                    retries += 1
            else:
                frappe.msgprint(f"No internet Retrying...{retries} times")
                frappe.log_error("No internet connection. Retrying...", "Connection Error")
                self.wait_for_internet(delay=5)  # Introduce a delay of 10 seconds
                retries += 1

        raise AuthenticationError("Maximum retries reached. Network issues.")

    def authenticate_with_retry(self):
        auth_details = self.get_auth_details()
        login_url = f"{self.BASE_LOGIN_URL}"
        headers = {"Content-Type": "application/json"}
        data = {"username": auth_details["username"], "password": "|7:%AnXy"}

        try:
            response = requests.post(login_url, json=data, headers=headers)
            response.raise_for_status()
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
            "system_identification_given_by_obr": ebims_settings.system_identification_given_by_obr
        }
        return auth_details

    def get_api_from_ebims_settings(self, method_name):
        ebims_settings = frappe.get_doc("EBIMS Settings")
        for api_row in ebims_settings.get("testing_apis"):
            if api_row.get("method_name") == method_name:
                return api_row.get("api")
        return None

    def wait_for_internet(self, delay=10):
        time.sleep(delay)  # Introduce a delay before checking internet connection again
