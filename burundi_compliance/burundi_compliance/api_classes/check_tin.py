import requests
import frappe
from frappe import _
from .base import OBRAPIBase
from frappe.integrations.utils import make_post_request


class TinVerifier:
    def __init__(self, api_key):
        obr_base = OBRAPIBase()
        self.api_key = api_key
        self.BASE_API_FOR_CHECK_TIN = obr_base.get_api_from_ebims_settings("check_TIN")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
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
            response = make_post_request(
                self.BASE_API_FOR_CHECK_TIN, json=tin, headers=self.headers
            )

            result = response
            return result

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues)
            title = _("CheckTin Request Error")
            err_msg = f"Error during API request: {str(e)}"
            frappe.log_error(title, err_msg)
            response = {"success": False}
            return response


obr_base_auth = OBRAPIBase()
token = obr_base_auth.authenticate()


@frappe.whitelist(allow_guest=True)
def confirm_tin():
    company_tin = frappe.form_dict.get("company_tin")

    if not company_tin:
        frappe.throw(_("Please set the Tax ID/TIN Number."))

    tin_verifier = TinVerifier(token)
    data = {"tp_TIN": f"{company_tin}"}
    result = tin_verifier.check_tin(data)
    frappe.response["message"] = result
