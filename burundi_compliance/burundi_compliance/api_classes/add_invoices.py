import requests
from ..doctype.custom_exceptions import AuthenticationError, InvoiceAdditionError
import frappe
from .base import OBRIntegrationBase


class OBRInvoicePoster:

    def __init__(self, token):
        obr_integration_base = OBRIntegrationBase()
        self.BASE_ADD_INVOICE_API_URL = obr_integration_base.get_api_from_ebims_settings("add_invoice")
        self.token = token

    def _send_request(self, data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        try:
            response = requests.post(f"{self.BASE_ADD_INVOICE_API_URL}", json=data, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Error during API request: {str(e)}")

    def _handle_response(self, response):
        if response.get("success"):
            return response["result"]
        else:
            raise InvoiceAdditionError(response["msg"])

    def post_invoice(self, invoice_data):
        response = self._send_request(invoice_data)
        return self._handle_response(response)

