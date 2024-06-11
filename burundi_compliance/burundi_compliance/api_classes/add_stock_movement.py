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
        if response.get("success"):
            frappe.publish_realtime("msgprint", f"Stock Movement for {stock_movement_data.get('item_code')} sent to OBR", user=frappe.session.user)
            self._update_integration_request(response, stock_movement_data,doc, status="Completed")
            return response
        else:
            raise StockMovementError(response["msg"])

    def _update_integration_request(self, response, stock_movement_data, doc, status="Completed"):
        integration_req = self.check_if_integration_request_exist(doc)

        if integration_req:

            try:
                doc = frappe.get_doc("Integration Request", doc.name)
                doc.status = status
                doc.output = str(response)
                doc.error = ""
                doc.save()
            except Exception as e:
                frappe.log_error(f"Error saving Integration Request: {str(e)}")
        else:
            self.create_integration_request(stock_movement_data, str(response),'Null',doc, status=status)

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def post_stock_movement(self, stock_movement_data, doc):
        doc_ = frappe.get_doc("Stock Ledger Entry", doc.name)
        try:
            response = requests.post(self.BASE_TRACK_STOCK_MOVEMENT_API_URL, json=stock_movement_data, headers=self._get_headers())
            try:
                response_data = response.json()
            except ValueError:
                error_message = f"Error during API request: No JSON object could be detected in response: {response.text}"
                frappe.log_error(error_message, "Add Stock Movement Request Error")
                raise StockMovementError("No JSON object could be detected")
            if response_data.get("success") == False:
                try:
                    self._update_integration_request(response_data, stock_movement_data, doc, status="Failed")
                except Exception as e:
                    frappe.log_error(f"Error while creating Integration Request: {str(e)}")
                raise requests.exceptions.RequestException("API request failed")  # Raise RequestException here
            else:
                return self._handle_response(response_data, stock_movement_data, doc_)
        except requests.exceptions.RequestException as e:
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, f"Add Stock Movement Request Error")
            raise StockMovementError(f"API request failed: {str(e)}")
           

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
