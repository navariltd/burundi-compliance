import requests
from ..doctype.custom_exceptions import InvoiceAdditionError
import json
import frappe
from frappe.integrations.utils import make_post_request, make_get_request, create_request_log
from .base import OBRAPIBase

class SalesInvoicePoster:

    def __init__(self, token: str):
        obr_base = OBRAPIBase()
        self.BASE_ADD_INVOICE_API_URL = obr_base.get_api_from_ebims_settings("add_invoice")
        self.token = token
        
    def _create_or_update_integration_request(self, response, invoice_data):
        success = response.get("success")
        status="Failed"
        if success:
            status="Completed"
        integration_req = self.check_if_integration_request_exist(invoice_data)
        doc=self.get_doc(invoice_data)
        if integration_req:
            try:
                doc = frappe.get_doc("Integration Request", invoice_data.get('invoice_number'))
                doc.status = status
                doc.output = str(response)
                doc.error = ""
                doc.save()

            except Exception as e:
                frappe.log_error(f"Error saving Integration Request: {str(e)}")
        else:
            create_request_log(invoice_data,
                                integration_type=None,
                                service_name="eBMS Invoice",
                                error="",
                                name=invoice_data.get("invoice_number"),
                                request_headers=self._get_headers(),
                                output=response,
                                reference_doctype=doc.doctype,
                                reference_docname=invoice_data.get("invoice_number"),
                                status=status,
                                url=self.BASE_ADD_INVOICE_API_URL
                                )

    def _handle_response(self, response, invoice_data):
        success = response.get("success")
        if success:
            self.update_sales_invoice(response)
            self._create_or_update_integration_request(response, invoice_data)
        
        return response
    
    def check_if_integration_request_exist(self, invoice_data):
        doc=self.get_doc(invoice_data)
        integration_request = frappe.db.exists("Integration Request", {
            "reference_doctype": doc.doctype,
            "reference_docname": invoice_data.get("invoice_number")
        })
        if integration_request:
            return True
        else:
            return False

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def post_invoice(self, invoice_data) -> dict:
        try:
            # Make the POST request
            response = requests.post(
                self.BASE_ADD_INVOICE_API_URL,
                json=invoice_data,
                headers=self._get_headers()
            )
            
            response_data = response.json()
            success = response_data.get("success")      
                
            if success:
                return self._handle_response(response_data, invoice_data)
            else:
                self._create_or_update_integration_request(response_data, invoice_data)
                return response_data
        except Exception as e:
            frappe.log_error(f"Error during API request: {str(e)}")
            return {"success": False, "error": str(e)}

        

    def update_sales_invoice(self, response):
        try:
            invoice_number = response.get("result", {}).get("invoice_number")
            electronic_signature = response.get("electronic_signature")
            invoice_registered_no = response.get("result", {}).get("invoice_registered_number")
            invoice_registered_date = response.get("result", {}).get("invoice_registered_date")

            # Check the doctype directly
            invoice=self.get_doc({"invoice_number": invoice_number})

            # Update Sales Invoice fields
            invoice.custom_einvoice_signatures = electronic_signature
            invoice.custom_invoice_registered_no = invoice_registered_no
            invoice.custom_invoice_registered_date = invoice_registered_date
            invoice.custom_submitted_to_obr = 1

            # Save the Sales Invoice
            invoice.save()
            frappe.db.commit()
            frappe.publish_realtime("msgprint", f"Sales Invoice {invoice_number} sent successfully", user=frappe.session.user)
        except Exception as e:
            # Log the error
            frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")

            # Create Integration Request document for failure
            self._create_or_update_integration_request(response, {"invoice_number": invoice_number})


    def get_doc(self, invoice_data):
        invoice_type = "POS Invoice" if frappe.db.exists("POS Invoice", invoice_data.get("invoice_number")) else "Sales Invoice"
        doc = frappe.get_doc(invoice_type, invoice_data.get("invoice_number"))
        return doc