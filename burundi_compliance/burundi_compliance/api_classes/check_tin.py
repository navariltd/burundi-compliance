import requests
import frappe
from .base import OBRAPIBase

class TinVerifier:
    def __init__(self, api_key):
        obr_base = OBRAPIBase()
        self.api_key = api_key
        self.BASE_API_FOR_CHECK_TIN ="https://ebms.obr.gov.bi:9443/ebms_api/checkTIN/" #obr_base.get_api_from_ebims_settings("check_TIN")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def check_tin(self, tin):
        """
        This method checks whether the TIN (Tax Identification Number) is valid and known by the OBR.

        Args:
            tin (str): The TIN (Tax Identification Number) to be verified.

        Returns:
            dict: A dictionary containing the verification result.
        """
        # Declare the response variable outside the try block
        response = None

        try:
            # Make a POST request to the API
            response = requests.post(self.BASE_API_FOR_CHECK_TIN, json=tin, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            # Parse the JSON response
            result = response.json()
            return result

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues)
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, "CheckTin Request Error")
            frappe.log_error(f"Response content: {response.text}")
            # Check if response is available before logging
            if response:
                frappe.log_error(f"Response content: {response.text}")
            return {"success": False, "msg": f"Request error: {str(e)}"}


obr_base_auth=OBRAPIBase()
token=obr_base_auth.authenticate()

@frappe.whitelist(allow_guest=True)
def confirm_tin():
    company_tin=frappe.form_dict.get("company_tin")
    tin_verifier=TinVerifier(token)

    data={"tp_TIN": f"{company_tin}"}
    results=tin_verifier.check_tin(data)
    frappe.response["message"] = results
    
    