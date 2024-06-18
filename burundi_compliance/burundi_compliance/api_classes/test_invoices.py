import unittest
from unittest.mock import patch
import requests
import frappe
from frappe.test_runner import make_test_objects
from frappe.tests.utils import FrappeTestCase
from frappe import _
from burundi_compliance.burundi_compliance.api_classes.add_invoices import SalesInvoicePoster
from burundi_compliance.burundi_compliance.api_classes.cancel_invoice import InvoiceCanceller
from burundi_compliance.burundi_compliance.doctype.custom_exceptions import AuthenticationError
from ..data.test_data import prepare_test_invoice_data

class TestAddInvoice(FrappeTestCase):

    def setUp(self):
        super().setUp()
        
        # Create a temporary Sales Invoice for testing
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
            
        # Check if the customer already exists
        self.customer = frappe.get_list("Customer", filters={"customer_name": "Test Customer_1"})
        if not self.customer:
            self.customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer_1",
                "customer_group": "All Customer Groups",
                "territory": "All Territories",
                "customer_type": "Company",
                "custom_gst_category": "Unregistered",
            })
            self.customer.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            self.customer = frappe.get_doc("Customer", self.customer[0].name)
        
        # Check if the cost center already exists
        self.cost_center = frappe.get_list("Cost Center", filters={"name": "Test Cost_Center_1 - TC"})
        if not self.cost_center:
            self.cost_center = frappe.get_doc({
                "doctype": "Cost Center",
                "cost_center_name": "Test Cost_Center_1",
                "company": "Test Company_1",
                "is_group": 0,
                "parent_cost_center": "Test Company_1 - TC",
            })
            self.cost_center.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            self.cost_center = frappe.get_doc("Cost Center", self.cost_center[0].name)

        # Create Sales Invoice for testing
        self.sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": "Test Company_1",
            "customer": "Test Customer_1",
            "posting_date": frappe.utils.nowdate(),
            "due_date": frappe.utils.nowdate(),
            "cost_center": "Test Cost_Center_1 - TC",
            "custom_payment_types": "Cash",
            "items": [
                {
                    "item_code": "Test Item",
                    "qty": 1,
                    "rate": 10000,
                }
            ],
        })
        self.sales_invoice.insert(ignore_permissions=True)
        
      
        self.sales_invoice_data={
            "invoice_number": self.sales_invoice.name,
            "invoice_date": "2021-12-06 07:30:22",
            "invoice_type": "FN",
            "tp_type": "1",
            "tp_name": "NDIKUMANA JEAN MARIE",
            "tp_TIN": "4400773244",
            "tp_trade_number": "3333",
            "tp_postal_number": "3256",
        }

    def tearDown(self):
        frappe.delete_doc("Sales Invoice", self.sales_invoice.name, force=True)
        super().tearDown()

    @patch.object(requests, 'post')
    def test_post_invoice_success(self, mock_post):
        poster = SalesInvoicePoster(token="ValidToken")
        # test_invoice_data = prepare_test_invoice_data()

        # Mock the API response
        mock_post.return_value.json.return_value = {
            "success": True,
            "result": {
                "invoice_number": self.sales_invoice.name,
                "electronic_signature": "SampleSignature",
                "invoice_registered_number": "12345",
                "invoice_registered_date": "2024-01-01"
            }
        }
        mock_post.return_value.status_code = 200

        result = poster.post_invoice(invoice_data=self.sales_invoice_data)

        # Verify the result
        self.assertTrue(result.get("success"))
        self.assertEqual(result["result"]["invoice_number"], self.sales_invoice.name)
        # Assert that correct API endpoint and data were used
        mock_post.assert_called_once_with(poster.BASE_ADD_INVOICE_API_URL, json=self.sales_invoice_data, headers=poster._get_headers())

    def test_update_sales_invoice_success(self):
        poster = SalesInvoicePoster(token="hvHjhvFGjhdtrdYTfytFGJfytFyuHJfUiYGFYghUFklUYF")

        response = {
            "electronic_signature": "dummy_signature",
            "msg": "La facture a \u00e9t\u00e9 ajout\u00e9e avec succ\u00e8s!",
            "result": {
            "invoice_number": self.sales_invoice.name,
            "invoice_registered_date": "2024-06-10 14:54:17",
            "invoice_registered_number": "REG001"
            },
            "success":True
            }

        poster.update_sales_invoice(response=response)
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": self.sales_invoice.name}, "custom_einvoice_signatures"), "dummy_signature")
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": self.sales_invoice.name}, "custom_invoice_registered_no"), "REG001")
        self.assertEqual(frappe.get_value("Sales Invoice", {"name": self.sales_invoice.name}, "custom_invoice_registered_date"), "2024-06-10 14:54:17")
        
  
    def test_get_doc(self):
        poster = SalesInvoicePoster(token="ValidToken")
        
        #verify correct doc is being retrieved
        doc = poster.get_doc(self.sales_invoice_data)
        self.assertEqual(doc.doctype, "Sales Invoice")
        self.assertEqual(doc.name, self.sales_invoice.name)