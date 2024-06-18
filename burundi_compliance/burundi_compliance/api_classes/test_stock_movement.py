import unittest
from unittest.mock import patch, MagicMock
import requests 

import frappe
from frappe.test_runner import make_test_objects
from frappe.tests.utils import FrappeTestCase
from frappe import _
from burundi_compliance.burundi_compliance.api_classes.add_invoices import SalesInvoicePoster
from burundi_compliance.burundi_compliance.api_classes.add_stock_movement import TrackStockMovement
from burundi_compliance.burundi_compliance.api_classes.cancel_invoice import InvoiceCanceller
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from ..doctype.custom_exceptions import InvoiceAdditionError, AuthenticationError, StockMovementError


class TestTrackStockMovement(FrappeTestCase):
    def setUp(self):
        self.token="ValidToken"
        self.max_retries=5
        self.track_stock_movement=TrackStockMovement(self.token, self.max_retries)
        
        
        self.company = frappe.get_list("Company", filters={"company_name": "Test Company_1"})
        if not self.company:
            self.company = frappe.get_doc({
                "doctype": "Company",
                "company_name": "Test Company_1",
                "abbr": "TC",
                "country": "Burundi",
                "default_currency": "BIF",
            })
            self.company.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            self.company = frappe.get_doc("Company", self.company[0].name)
        
        # Get the existing Fiscal Year document for 2024
        self.fiscal_year = frappe.get_doc("Fiscal Year", "2024")
        company_exists = False
        for company in self.fiscal_year.companies:
            if company.company == "Test Company_1":
                company_exists = True
                break
        
        # If the company doesn't exist in the Fiscal Year, add it to the companies list
        if not company_exists:
            self.fiscal_year.append("companies", {
                "company": "Test Company_1"
            })
            self.fiscal_year.save(ignore_permissions=True)
        
        # Check if the warehouse already exists
        self.warehouse = frappe.get_list("Warehouse", filters={"warehouse_name": "Test Warehouse"})
        if not self.warehouse:
            self.warehouse = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "Test Warehouse",
                "company": "Test Company_1"
            })
            self.warehouse.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            self.warehouse = frappe.get_doc("Warehouse", self.warehouse[0].name)
        
        # Check if the item already exists
        self.item = frappe.get_list("Item", filters={"item_code": "Test Item"})
        if not self.item:
            self.item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "Test Item",
                "item_name": "Test Item",
                "stock_uom": "Nos",
                "is_stock_item": 1,
                "default_warehouse": "Test Warehouse - TC",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
            })
            self.item.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            self.item = frappe.get_doc("Item", self.item[0].name)
        
        self.stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "company": "Test Company_1",
            "custom_stock_movement_description": "Test Stock Movement",
            "items": [
                {
                    "item_code": "Test Item",
                    "qty": 5,
                    "t_warehouse": "Test Warehouse - TC",
                    "basic_rate" : 100
                }
            ]
        })
        self.stock_entry.insert(ignore_permissions=True)
        frappe.db.commit()
        self.stock_movement_data={
            "item_code":"Test Item",
            "warehouse":"Test Warehouse - TC",
            #"posting_date":"2021-05-05",
            "posting_time":"12:00:00",
            "actual_qty":5,
            "company":"Test Company_1",
            "voucher_type":"Stock Entry",
            "voucher_no":self.stock_entry.name,
        }
        self.doc=frappe.get_doc({
            "doctype":"Stock Ledger Entry",
            "item_code":"Test Item",
            "company":"Test Company_1",
            "warehouse":"Test Warehouse - TC",
            "posting_date":frappe.utils.nowdate(),
            "posting_time":"12:00:00",
            "actual_qty":5,
             "voucher_type":"Stock Entry",
             "voucher_no":self.stock_entry.name,
        })
        self.doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        self.doc = MagicMock()
        self.doc.name = 'Test Doc Name'
        self.integration_request_doc = MagicMock()
        self.integration_request_doc.name = 'Integration Request Doc'
        self.integration_request_doc.status = 'Pending'
        self.track_stock_movement = TrackStockMovement(token="dummy_token")

    def tearDown(self):
        super().tearDown()
        frappe.delete_doc("Company", "Test Company_1", force=True)
        frappe.delete_doc("Warehouse", "Test Warehouse", force=True)
        frappe.delete_doc("Stock Entry", self.stock_entry.name, force=True)
        frappe.delete_doc("Stock Ledger Entry", self.doc.name, force=True)
        frappe.delete_doc("Item", "Test Item", force=True)
        
    @patch.object(frappe, "get_doc")
    @patch.object(requests, "post")
    def test_post_stock_movement_success(self, mock_post, mock_get_doc):
        mock_get_doc.return_value = self.doc
        mock_post.return_value.json.return_value={"success":"True"}
        response=self.track_stock_movement.post_stock_movement(self.stock_movement_data, self.doc)
        self.assertEqual(response, {"success":"True"})    
    
    
    @patch.object(frappe, 'get_doc')
    @patch.object(frappe, 'db')
    @patch.object(frappe.model.document.Document, 'save', MagicMock())
    def test_update_integration_request(self, mock_db, mock_get_doc):
        mock_db.exists.return_value = True
        # Ensure get_doc returns the correct document instance
        def side_effect(doctype, name=None):
            if doctype == "Integration Request":
                return self.integration_request_doc
            else:
                return self.doc

        mock_get_doc.side_effect = side_effect
        self.track_stock_movement._update_integration_request({"success": True}, self.stock_movement_data, self.doc, status="Completed")
        self.assertEqual(self.integration_request_doc.status, "Completed")
        self.integration_request_doc.save.assert_called_once()
    
    @patch.object(requests, "post")
    @patch.object(frappe, 'get_doc')
    def test_post_stock_movement_non_json_response(self, mock_get_doc, mock_post):
        mock_get_doc.return_value = self.doc
        mock_post.return_value.json.side_effect = ValueError("No JSON object could be detected")
        with self.assertRaises(StockMovementError):
            self.track_stock_movement.post_stock_movement(self.stock_movement_data, self.doc)
