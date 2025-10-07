import requests
import frappe
from frappe import _
from .base import OBRAPIBase
from frappe.integrations.utils import make_post_request


class InvoiceVerifier:
    def __init__(self, api_key):
        obr_base = OBRAPIBase()
        self.api_key = api_key
        self.BASE_API_FOR_CHECK_TIN = obr_base.get_api_from_ebims_settings(
            "get_invoice"
        )
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def get_invoice(self, invoice_verifier):
        """
        This method checks whether the invoice has been added to OBR database.

        Args:
            invoice_verifier (str): The Invoice number to be verified.

        Returns:
            dict: A dictionary containing the verification result.
        """
        response = None
        try:
            # NOTE: eBMS server is currently returning a 401 Unauthorized status code
            # hence the below request will always throw an execption if the invoice is not found
            response = make_post_request(
                self.BASE_API_FOR_CHECK_TIN, json=invoice_verifier, headers=self.headers
            )

            if hasattr(response, "json"):
                return response.json()
            return response

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues)
            title = _("Get Invoice Request Error")
            err_msg = f"Error during API request: {str(e)}"
            frappe.log_error(
                title,
                err_msg,
            )

            return {"success": False, "msg": f"Request error: {str(e)}"}


obr_integration_base = OBRAPIBase()
token = obr_integration_base.authenticate()


@frappe.whitelist(allow_guest=True)
def confirm_invoice():
    invoice_identifier = frappe.form_dict.get("invoice_identifier")
    data = {"invoice_identifier": f"{invoice_identifier}"}

    invoice_verifier = InvoiceVerifier(token)
    result = invoice_verifier.get_invoice(data)
    frappe.response["message"] = result
