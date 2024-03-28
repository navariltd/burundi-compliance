# import requests
# from ..doctype.custom_exceptions import StockMovementError
# import frappe
# from .base import OBRAPIBase
# class TrackStockMovement:

#     MAX_RETRIES = 2
#     RETRY_DELAY_SECONDS = 2

#     def __init__(self, token, max_retries=5, retry_delay_seconds=2):
#         obr_base = OBRAPIBase()
#         self.BASE_TRACK_STOCK_MOVEMENT_API_URL = obr_base.get_api_from_ebims_settings("add_stock_movement")
#         self.token = token
#         self.MAX_RETRIES = max_retries
#         self.RETRY_DELAY_SECONDS = retry_delay_seconds

#     def _retry_request(self, data, retries):
#         try:
#             response = requests.post(self.BASE_TRACK_STOCK_MOVEMENT_API_URL, json=data, headers=self._get_headers())
#             response.raise_for_status()
            
#             # Validate the response structure
#             if not response.json().get("success"):
#                 frappe.log_error(f"Unexpected API response format: {response.text}")
#                 raise StockMovementError(f"Unexpected API response format: {response.text}")

#             return response.json()
#         except requests.exceptions.RequestException as e:
#             error_message = f"Error during API request: {str(e)}"
#             frappe.log_error(error_message, "Add Stock Movement Request Error")
#             frappe.log_error(f"Response content: {response.text}")
           
#     def _send_request(self, data):
#         return self._retry_request(data, self.MAX_RETRIES)
        

#     def _handle_response(self, response):
#         # frappe.throw(str(response))
#         if response.get("success"):
#             # Handle successful stock movement response, if needed
#             return response.get('msg')
#         else:
#             raise StockMovementError(response["msg"])

#     def _get_headers(self):
#         return {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.token}"
#         }

#     def post_stock_movement(self, stock_movement_data):
#         response = self._send_request(stock_movement_data)
#         return self._handle_response(response)


import requests
import frappe
from ..doctype.custom_exceptions import StockMovementError
from .base import OBRAPIBase
from frappe.integrations.utils import make_post_request, make_get_request, create_request_log

class TrackStockMovement:
    RETRY_DELAY_SECONDS = 2

    def __init__(self, token, max_retries=5):
        obr_base = OBRAPIBase()
        self.BASE_TRACK_STOCK_MOVEMENT_API_URL = obr_base.get_api_from_ebims_settings("add_stock_movement")
        self.token = token
        self.MAX_RETRIES = max_retries

    def _handle_response(self, response, stock_movement_data, doc):
        self._update_integration_request(response, stock_movement_data,doc, status="Completed")
        return response.get('msg')

    def _update_integration_request(self, response, stock_movement_data, doc, status="Failed"):
        integration_req = self.check_if_integration_request_exist(doc)
        error=response.text
        if integration_req:
            try:
                doc = frappe.get_doc("Integration Request", doc.name)
                doc.status = "Completed"
                doc.output = response
                doc.error = ""
                doc.save()
            except Exception as e:
                frappe.publish_realtime("msgprint", f"How while saving Integration Request: {str(e)}", user=frappe.session.user)
                frappe.log_error(f"Error saving Integration Request: {str(e)}")
        else:
            self.create_integration_request(stock_movement_data, response,'Null',doc, status="Completed")

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def post_stock_movement(self, stock_movement_data, doc):
        doc_=frappe.get_doc("Stock Ledger Entry", doc.name)
        try:
            #make_post_request(self.BASE_TRACK_STOCK_MOVEMENT_API_URL, stock_movement_data, headers=self._get_headers())
            #I am against this method because it does not allow me to handle the response
            response = requests.post(self.BASE_TRACK_STOCK_MOVEMENT_API_URL, json=stock_movement_data, headers=self._get_headers())
            response_data = response.json()
            if response_data.get("success")==False:
                try:
                    self._update_integration_request(response, stock_movement_data,doc, status="Failed")
                except Exception as e:
                    frappe.publish_realtime("msgprint", f"Error while creating Integration Request 1: {str(e)}", user=frappe.session.user)
                    frappe.log_error(f"Error while creating Integration Request: {str(e)}")
            else:
                frappe.publish_realtime("msgprint", f"Pased", user=frappe.session.user)
                return self._handle_response(response_data,stock_movement_data, doc_)
        except requests.exceptions.RequestException as e:
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, "Add Stock Movement Request Error")
            frappe.log_error(f"Response content: {response.text}")
           

    def check_if_integration_request_exist(self, doc):
        integration_request = frappe.db.exists("Integration Request", {
            "reference_doctype": "Stock Ledger Entry",
            "reference_docname": doc.name
        })
        return integration_request

    def create_integration_request(self, stock_movement_data, response, error_msg, doc, status="Failed"):
        create_request_log(stock_movement_data,
            integration_type=None,
            service_name="eBMS Stock Movement",
            name=doc.name,
            error=error_msg,
            url=self.BASE_TRACK_STOCK_MOVEMENT_API_URL,
            request_headers=self._get_headers(),
            output=response,
            reference_doctype="Stock Ledger Entry",
            reference_docname=doc.name,
            status=status
        )
