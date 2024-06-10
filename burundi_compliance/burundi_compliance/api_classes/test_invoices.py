

import unittest
from unittest.mock import patch
import requests 

import frappe
from frappe.test_runner import make_test_objects
from frappe.tests.utils import FrappeTestCase
from frappe import _
from burundi_compliance.burundi_compliance.api_classes.add_invoices import SalesInvoicePoster
from burundi_compliance.burundi_compliance.api_classes.cancel_invoice import InvoiceCanceller
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from ..doctype.custom_exceptions import InvoiceAdditionError, AuthenticationError
from ..data.test_data import prepare_test_invoice_data

from ..api_classes.cancel_invoice import InvoiceCanceller
class TestAddInvoice(FrappeTestCase):

    def setUp(self):
        super().setUp()
        # Create a temporary Sales Invoice for testing
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test Customer",
            "posting_date": frappe.utils.now(),
            "due_date": frappe.utils.now(),
            "items": [
                {
                    "item_code": "Gloves Leather Dinqi 91006",
                    "qty": 1,
                    "rate": 10000,
                    "cost_center": "Masaka - S",  
                }
            ],
        })
        sales_invoice.insert(ignore_permissions=True)

    def tearDown(self):
        super().tearDown()

    def test_post_invoice_success(self):
        poster = SalesInvoicePoster(token="ValidToken")
        test_invoice_data = prepare_test_invoice_data()

        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.json.return_value = {"success": True, "result": {"invoice_number": "INV001"}}
            result = poster.post_invoice(invoice_data=test_invoice_data)

        self.assertEqual(result, {"invoice_number": "INV001"})
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}), "INV001")

        # Assert that correct API endpoint and data were used
        mock_post.assert_called_once_with(poster.BASE_ADD_INVOICE_API_URL, json=test_invoice_data, headers=poster._get_headers())

        frappe.delete_doc("Sales Invoice", "INV001", force=True)

    def test_post_invoice_failure_api_error(self):
        poster = SalesInvoicePoster(token="InvalidToken")
        test_invoice_data = prepare_test_invoice_data()

        with patch.object(requests, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("API error")
            with self.assertRaises(AuthenticationError):
                poster.post_invoice(test_invoice_data) 




    def test_update_sales_invoice_success(self):
        poster = SalesInvoicePoster(token="hvHjhvFGjhdtrdYTfytFGJfytFyuHJfUiYGFYghUFklUYF")

        response = {
            "success": True,
            "result": {
                "invoice_number": "INV001",
                "electronic_signature": "dummy_signature",
                "invoice_registered_number": "REG001",
                "invoice_registered_date": "2022-01-01"
            }
        }

        poster.update_sales_invoice(response=response)
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}, "custom_einvoice_signatures"), "dummy_signature")
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}, "custom_invoice_registered_no"), "REG001")
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}, "custom_invoice_registered_date"), "2022-01-01")
        
        
class TestCancelInvoice(FrappeTestCase):
    def setUp(self):
        super().setUp()
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test Customer",
            "posting_date": frappe.utils.now(),
            "due_date": frappe.utils.now(),
            "items": [
                {
                    "item_code": "Gloves Leather Dinqi 91006",
                    "qty": 1,
                    "rate": 10000,
                    "cost_center": "Masaka - S",  
                }
            ],
        })
        sales_invoice.insert(ignore_permissions=True)

    def tearDown(self):
        super().tearDown()

    def test_cancel_invoice_success(self):
        canceller = InvoiceCanceller(token="ValidToken")
        test_invoice_data = prepare_test_invoice_data()

        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.json.return_value = {"success": True, "result": {"invoice_number": "INV001"}}
            result = canceller.cancel_invoice(invoice_data=test_invoice_data)

        self.assertEqual(result, {"invoice_number": "INV001"})
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}), "INV001")

        # Assert that correct API endpoint and data were used
        mock_post.assert_called_once_with(canceller.BASE_CANCEL_INVOICE_API_URL, json=test_invoice_data, headers=canceller._get_headers())

        frappe.delete_doc("Sales Invoice", "INV001", force=True)

    def test_cancel_invoice_failure_api_error(self):
        canceller = InvoiceCanceller(token="InvalidToken")
        test_invoice_data = prepare_test_invoice_data()

        with patch.object(requests, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("API error")
            with self.assertRaises(AuthenticationError):
                canceller.cancel_invoice(test_invoice_data) 
                
                
class TestAuthentication(FrappeTestCase):
    def setUp(self):
        self.ebims_settings = frappe.get_doc({
            "doctype": "eBMS Settings",
            "username": "test_username",
            "password": "test_password",
            "sandbox": 1,
            "taxpayers_legal_form": "test_legal_form",
            "taxpayers_sector_of_activity": "test_activity_sector",
            "system_identification_given_by_obr": "test_system_identification",
            "the_taxpayers_commercial_register_number": "test_register_number",
            "the_taxpayers_tax_center": "DMC",
            "type_of_taxpayer": "pour personne morale",
            "subject_to_vat": "pour un non assujetti ou",
            "subject_to_consumption_tax": "pour un non assujetti ou",
            "subject_to_flatrate_withholding_tax": "pour un non assujetti ou",
            "allow_obr_to_track_sales": 1,
            "allow_obr_to_track_stock_movement": 1,
            "company": "Test Company"
        })
        self.ebims_settings.insert(ignore_permissions=True)
        
    def tearDown(self):
        super().tearDown()
        frappe.delete_doc("eBMS Settings", "Test Company", force=True)
            
        
    def test_authenticate_success(self):
        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.json.return_value = {"success": True, "result": {"token": "ValidToken"}}
            result = OBRAPIBase().authenticate()

        self.assertEqual(result, "ValidToken")

    def test_authenticate_failure(self):
        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.json.return_value = {"success": False, "msg": "Invalid credentials"}
            result=OBRAPIBase().authenticate()
            self.assertFalse(result)
            
    def test_enqueue_retry_task(self):
        with patch.object(frappe, 'enqueue') as mock_enqueue:
            OBRAPIBase().enqueue_retry_task()
            mock_enqueue.assert_called_once_with("burundi_compliance.burundi_compliance.utils.background_jobs.retry_authentication", queue='short', timeout=5, is_async=True, at_front=True)
            
    def test_get_auth_details(self):
        with patch.object(frappe, 'get_doc') as mock_get_doc:
            obr_api=OBRAPIBase()
            auth_details=obr_api.get_auth_details()
        
        with patch.object(frappe, 'get_doc') as mock_get_doc:
            mock_get_doc.return_value=self.ebims_settings
            obr_api=OBRAPIBase()
            auth_details=obr_api.get_auth_details()
            
            expected_auth_details={
                 "username": "test_username",
            "password": "test_password",
            "sandbox": 1,
            "tp_legal_form": "test_legal_form",
            "tp_activity_sector": "test_activity_sector",
            "system_identification_given_by_obr": "test_system_identification",
            "the_taxpayers_commercial_register_number": "test_register_number",
            "the_taxpayers_tax_center": "DMC",
            "type_of_taxpayer": "pour personne morale",
            "subject_to_vat": "pour un non assujetti ou",
            "subject_to_consumption_tax": "pour un non assujetti ou",
            "subject_to_flatrate_withholding_tax": "pour un non assujetti ou",
            "allow_obr_to_track_sales": 1,
            "allow_obr_to_track_stock_movement": 1,
            }
            self.assertDictEqual(auth_details, expected_auth_details)
            