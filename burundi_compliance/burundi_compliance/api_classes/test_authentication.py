from unittest.mock import patch
import requests 

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import _

from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
               
class TestAuthentication(FrappeTestCase):
    def setUp(self):
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
            
        self.ebims_settings=frappe.get_list("eBMS Settings", filters={"company": "Test Company_1"})
        if not self.ebims_settings:
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
                    "company": "Test Company_1"
                })
            self.ebims_settings.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            self.ebims_settings = frappe.get_doc("eBMS Settings", self.ebims_settings[0].name)   
    def tearDown(self):
        super().tearDown()
        frappe.delete_doc("eBMS Settings", "Test Company_1", force=True)
        
        
    def test_authenticate_success(self):
        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.json.return_value = {"success": True, "result": {"token": "ValidToken"}}
            result = OBRAPIBase().authenticate()

        self.assertEqual(result, "ValidToken")
        frappe.delete_doc("eBMS Settings", "Test Company_1", force=True)
        

    def test_authenticate_failure(self):
        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.json.return_value = {"success": False, "msg": "Invalid credentials"}
            result=OBRAPIBase().authenticate()
            self.assertFalse(result)
        frappe.delete_doc("eBMS Settings", "Test Company_1", force=True)
            
    def test_enqueue_retry_task(self):
        with patch.object(frappe, 'enqueue') as mock_enqueue:
            OBRAPIBase().enqueue_retry_task()
            mock_enqueue.assert_called_once_with("burundi_compliance.burundi_compliance.utils.background_jobs.retry_authentication", queue='short', timeout=5, is_async=True, at_front=True)
        frappe.delete_doc("eBMS Settings", "Test Company_1", force=True)
            
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
        frappe.delete_doc("eBMS Settings", "Test Company_1", force=True)
            
    def test_authentication_non_json_response(self):
        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.json.side_effect=ValueError("No JSON object could be decoded")
            result=OBRAPIBase().authenticate()
            self.assertFalse(result)
        frappe.delete_doc("eBMS Settings", "Test Company_1", force=True)
            
    def test_authenticate_invalid_url(self):
        with patch.object(requests, 'post', side_effect=requests.ConnectionError):
            result=OBRAPIBase().authenticate()
            self.assertFalse(result)
        frappe.delete_doc("eBMS Settings", "Test Company_1", force=True)
  