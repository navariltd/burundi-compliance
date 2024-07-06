import requests
import json
import frappe
from frappe.integrations.utils import make_post_request, create_request_log
from .base import OBRAPIBase

class InvoiceCanceller:

    def __init__(self, token: str):
        obr_base = OBRAPIBase()
        self.BASE_CANCEL_INVOICE_API_URL = obr_base.get_api_from_ebims_settings("cancel_invoice")
        self.token = token

    def _create_or_update_integration_request(self, response, data):
        success = response.get("success")
        status = "Failed"
        if success:
            status = "Completed"
        integration_req = self.check_if_integration_request_exist(data)
        doc = self.get_invoice(data)
        if integration_req:
            try:
                integration_docs=frappe.get_all("Integration Request", filters={"reference_doctype": "Sales Invoice", "reference_docname": doc.name, "integration_request_service": "eBMS Invoice Cancellation"})
                for integration_doc in integration_docs:
                    doc = frappe.get_doc("Integration Request", integration_doc.name)
                    doc.status = status
                    doc.output = str(response)
                    doc.error = response.get("msg", "")
                    doc.save()
            except Exception as e:
                frappe.log_error(f"Error saving Integration Request: {str(e)}")
        else:
            create_request_log(data,
                                integration_type=None,
                                service_name="eBMS Invoice Cancellation",
                                error=response.get("msg", ""),
                                url=self.BASE_CANCEL_INVOICE_API_URL,
                                request_headers=self._get_headers(),
                                output=response,
                                reference_doctype="Sales Invoice",
                                reference_docname=doc.name,
                                status=status
                                )

    def _handle_response(self, response, data):
        success = response.get("success")
        self._create_or_update_integration_request(response, data)
        if success:
            self.update_invoice(data)
        return response

    def check_if_integration_request_exist(self, data):
        doc = self.get_invoice(data)
        integration_request = frappe.db.exists("Integration Request", {
            "reference_doctype": "Sales Invoice",
            "integration_request_service": "eBMS Invoice Cancellation",
            "reference_docname": doc.name
        })
        return integration_request

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def cancel_invoice(self, data) -> dict:
        try:
            response = requests.post(
                self.BASE_CANCEL_INVOICE_API_URL,
                json=data,
                headers=self._get_headers()
            ).json()
            return self._handle_response(response, data)
        except Exception as e:
            frappe.log_error(f"Error during API request: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_invoice(self, data):
        invoice_identifier = data.get('invoice_signature')
        _invoices = frappe.get_all('Sales Invoice', filters={'custom_invoice_identifier': invoice_identifier}, fields=['name'])
        for _invoice in _invoices:
            doc = frappe.get_doc('Sales Invoice', _invoice.get('name'))
            return doc

    def update_invoice(self, data):
        doc = self.get_invoice(data)
        frappe.db.set_value('Sales Invoice', doc.name, 'custom_ebms_invoice_cancelled', 1)
        frappe.db.commit()
