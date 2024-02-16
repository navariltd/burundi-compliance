import frappe
from frappe.test_runner import make_test_objects
from frappe.tests.utils import FrappeTestCase
from frappe import _
from burundi_compliance.burundi_compliance.api_classes.add_invoices import SalesInvoicePoster
from ..doctype.custom_exceptions import InvoiceAdditionError
from ..data.test_data import prepare_test_invoice_data

class TestAddInvoice(FrappeTestCase):
    def setUp(self):
   
        # Create a dummy Sales Invoice for testing
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
                    "cost-center": "Masaka - S",
                }
            ],
        })
        sales_invoice.insert(ignore_permissions=True)


    def tearDown(self):
        # Cleanup after the tests
        frappe.db.rollback()
        

    def test_post_invoice_success(self):
        poster = SalesInvoicePoster(token="hjbJKdKjIsa0989080980asadnIkjnYTF9897tFio(*uhTRDhTR")
        test_invoice_data = prepare_test_invoice_data()

        # Call the post_invoice method with the test data
        result = poster.post_invoice(invoice_data=test_invoice_data)
        
        # Assertions
        self.assertEqual(result, {"invoice_number": "INV001"})
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}), "INV001")
        
    def test_post_invoice_failure(self):
        poster = SalesInvoicePoster(token="bfjdsbTRDDYTDYTDYDYTbhjbhdFYT7t687CFTjbjHVHG")

        # Prepare the test data for a failure scenario
        invoice_data = prepare_test_invoice_data()
        invoice_data["invoice_number"] = "INV002" 
        invoice_data["invoice_items"][0]["item_quantity"] = "0"  

        # Call the post_invoice method and expect an InvoiceAdditionError
        with self.assertRaises(InvoiceAdditionError):
            poster.post_invoice(invoice_data=invoice_data)
            


    def test_update_sales_invoice_success(self):
        poster = SalesInvoicePoster(token="hvjhvjhdtrdYTfytfytFyufUYGFYUFUYF")

        # Prepare the test data for an update success scenario
        response = {
            "success": True,
            "result": {
                "invoice_number": "INV001",
                "electronic_signature": "dummy_signature",
                "invoice_registered_number": "REG001",
                "invoice_registered_date": "2022-01-01"
            }
        }

        # Call the update_sales_invoice method
        poster.update_sales_invoice(response=response)
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}, "custom_einvoice_signatures"), "dummy_signature")
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}, "custom_invoice_registered_no"), "REG001")
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": "INV001"}, "custom_invoice_registered_date"), "2022-01-01")
        
