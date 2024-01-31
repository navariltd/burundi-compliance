from frappe.utils import now
from frappe.test_runner import make_test_objects
from frappe.tests.utils import FrappeTestCase
from frappe import _
import frappe
class TestEBIMSSettings(FrappeTestCase):

    def setUp(self):
        '''Create a new EBIMSSettings document for testing'''
        self.ebims_settings = frappe.get_doc({
            "doctype": "EBIMS Settings",
            "testing_apis": [
                {"api": "https://www.example.com/api", "method_name": "login"},
                {"api": "", "method_name": "add_invoice"}
            ],
            "environment": "Testing",
        })
        self.ebims_settings.insert()

    def tearDown(self):
        '''Delete the test EBIMSSettings document'''
        frappe.delete_doc("EBIMS Settings", self.ebims_settings.name, force=True)

    def test_valid_urls(self):
        '''Valid URLs should not raise an exception'''
        self.assertTrue(self.ebims_settings.is_valid_url("https://www.example.com/api"))

    def test_invalid_urls(self):
        '''Invalid URLs should raise a validation exception'''
        with self.assertRaises(frappe.ValidationError):
            self.ebims_settings.testing_apis[1].api = "invalid_url"
            self.ebims_settings.save()

    