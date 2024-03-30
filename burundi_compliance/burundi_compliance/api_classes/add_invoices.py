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
    def _update_integration_request(self, response, invoice_data):
        success = response.get("success")
        status="Failed"
        if success:
            status="Completed"
        integration_req = self.check_if_integration_request_exist(invoice_data)
        
        if integration_req:
            try:
                doc = frappe.get_doc("Integration Request", invoice_data.get('invoice_number'))
                doc.status = status
                doc.output = str(response)
                doc.error = ""
                doc.save()
            except Exception as e:
                frappe.publish_realtime("msgprint", f"Error while saving Integration Request: {str(e)}", user=frappe.session.user)
                frappe.log_error(f"Error saving Integration Request: {str(e)}")

    def _handle_response(self, response, invoice_data):
        success = response.get("success")
        if success:
            self.update_sales_invoice(response)
            self._update_integration_request(response, invoice_data)
        else:
            create_request_log(invoice_data,
                integration_type=None,
                service_name="eBMS Invoice",
                name=invoice_data.get("invoice_number"),
                error="",
                url=self.BASE_ADD_INVOICE_API_URL,
                request_headers=self._get_headers(),
                output=response,
                reference_doctype="Sales Invoice",
                reference_docname=invoice_data.get("invoice_number"),
                status="Completed"
            )
        return response
    
    def check_if_integration_request_exist(self, invoice_data):
        integration_request = frappe.db.exists("Integration Request", {
            "reference_doctype": "Sales Invoice",
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
            #make_post_request doesn't seem to work well here
            #It doesn't give me the freedom to handle the response
            response = requests.post(
                self.BASE_ADD_INVOICE_API_URL,
                json=invoice_data,
                headers=self._get_headers()
            )
            response_data = json.loads(response.text)
            msg=response_data.get("msg")
            success=response_data.get("success")
            doc=frappe.get_doc("Sales Invoice", invoice_data.get("invoice_number"))
            if success==False:
                integration_req = self.check_if_integration_request_exist(invoice_data)
                if integration_req:
                    try:
                        self.update_(response_data,msg, invoice_data)
                    except Exception as e:
                        frappe.log_error(f"Error saving Integration Request: {str(e)}")
                else:
                    create_request_log(invoice_data,
                                            integration_type=None,
                                            service_name="eBMS Invoice",
                                            error=msg,
                                            name=invoice_data.get("invoice_number"),
                                            request_headers=self._get_headers(),
                                            output=response_data,
                                            reference_doctype="Sales Invoice",
                                            reference_docname=invoice_data.get("invoice_number"),
                                            status="Failed",
                                            url=self.BASE_ADD_INVOICE_API_URL
                                            )
            elif success==True:
                return self._handle_response(response_data, invoice_data)
        except Exception as e:
            frappe.log_error(f"Error during API request: {str(e)}")
        

    def update_sales_invoice(self, response):
        try:
            invoice_number = response.get("result", {}).get("invoice_number")
            electronic_signature = response.get("electronic_signature")
            invoice_registered_no = response.get("result", {}).get("invoice_registered_number")
            invoice_registered_date = response.get("result", {}).get("invoice_registered_date")

            # Check the doctype directly
            invoice_type = "POS Invoice" if frappe.db.exists("POS Invoice", invoice_number) else "Sales Invoice"
            sales_invoice = frappe.get_doc(invoice_type, invoice_number)

            # Update Sales Invoice fields
            sales_invoice.custom_einvoice_signatures = electronic_signature
            sales_invoice.custom_invoice_registered_no = invoice_registered_no
            sales_invoice.custom_invoice_registered_date = invoice_registered_date
            sales_invoice.custom_submitted_to_obr = 1

            # Save the Sales Invoice
            sales_invoice.save()
            frappe.db.commit()
            frappe.publish_realtime("msgprint", f"Sales Invoice {invoice_number} sent successfully", user=frappe.session.user)
        except Exception as e:
            # Log the error
            frappe.log_error(f"Error updating Sales Invoice {invoice_number}: {str(e)}")

            # Create Integration Request document for failure
            self.create_integration_request(response, False, str(e))

    def update_(self, response_data,msg, invoice_data):
        try:
            doc = frappe.get_doc("Integration Request", invoice_data.get('invoice_number'))
            doc.status = "Failed"
            doc.output = str(response_data)
            doc.error = msg
            doc.save()
        except Exception as e:
            frappe.publish_realtime("msgprint", f"Error while saving Integration Request: {str(e)}", user=frappe.session.user)
            frappe.log_error(f"Error saving Integration Request: {str(e)}")
            