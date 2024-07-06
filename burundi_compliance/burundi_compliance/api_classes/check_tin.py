import requests
import frappe
from .base import OBRAPIBase
from frappe.integrations.utils import make_post_request


class TinVerifier:
    def __init__(self, api_key):
        obr_base = OBRAPIBase()
        self.api_key = api_key
        self.BASE_API_FOR_CHECK_TIN =F"https://ebms.obr.gov.bi:9443/ebms_api/checkTIN/"
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
        response = None

        try:
            response = make_post_request(self.BASE_API_FOR_CHECK_TIN, json=tin, headers=self.headers)

            result = response
            return result

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues)
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, "CheckTin Request Error")
            frappe.log_error(f"Response content: {response}")
            frappe.throw(f"{tin} Not registered")
        

obr_base_auth=OBRAPIBase()
token=obr_base_auth.authenticate()

@frappe.whitelist(allow_guest=True)
def confirm_tin():
    company_tin=frappe.form_dict.get("company_tin")
    tin_verifier=TinVerifier(token)
    data={"tp_TIN": f"{company_tin}"}
    results=tin_verifier.check_tin(data)
    frappe.response["message"] = results
    
    