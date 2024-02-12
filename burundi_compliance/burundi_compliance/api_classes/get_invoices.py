
import requests
import frappe
from .base import OBRAPIBase

class InvoiceVerifier:
    def __init__(self, api_key):
        obr_base = OBRAPIBase()
        self.api_key = api_key
        self.BASE_API_FOR_CHECK_TIN = obr_base.get_api_from_ebims_settings("get_invoice")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_invoice(self, invoice_verifier):
        """
        This method checks whether the invoice has been added to OBR database.

        Args:
            invoice_verifier (str): The Invoice number to be verified.

        Returns:
            dict: A dictionary containing the verification result.
        """
        # Declare the response variable outside the try block
        response = None

        try:
            # Make a POST request to the API
            response = requests.post(self.BASE_API_FOR_CHECK_TIN, json=invoice_verifier, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            # Parse the JSON response
            result = response.json()
            return result

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues)
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, "get Invoice Request Error")
            frappe.log_error(f"Response content: {response.text}")
            # Check if response is available before logging
            if response:
                frappe.log_error(f"Response content: {response.text}")
            return {"success": False, "msg": f"Request error: {str(e)}"}


obr_integration_base = OBRAPIBase()
token=obr_integration_base.authenticate()

@frappe.whitelist(allow_guest=True)
def confirm_invoice():
    invoice_identifier=frappe.form_dict.get("invoice_identifier")
    data = {"invoice_identifier": f"{invoice_identifier}"}

    invoice_verifier = InvoiceVerifier(token)
    results = invoice_verifier.get_invoice(data)
    frappe.msgprint(str(results))
    frappe.response["message"] = results
    
    
    
