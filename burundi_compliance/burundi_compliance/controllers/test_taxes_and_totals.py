import frappe
from frappe.utils import flt
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
from frappe.tests.utils import FrappeTestCase

from .taxes_and_totals import calculate_item_values_override

class TestCalculateItemValues(FrappeTestCase):
    def setUp(self):
        # Set up any necessary data before running the tests
        pass

    def tearDown(self):
        frappe.db.rollback()

    def test_calculate_item_values_normal_case(self):
        test_doc = frappe.get_doc({
            "doctype": "Sales Order",
            "is_consolidated": False,
            "items": [
                {"item_code": "Or(Gold)", "qty": 2, "rate": 10.0},
                {"item_code": "Item2", "qty": 3, "rate": 15.0},
            ]
        })

        sales_order = frappe.get_doc(test_doc)
        calculate_taxes_and_totals.calculate_item_values(sales_order)

        self.assertEqual(sales_order.items[0].net_amount, 20.0)
        self.assertEqual(sales_order.items[1].net_amount, 45.0)

    def test_calculate_item_values_custom_logic(self):
        test_doc = frappe.get_doc({
            "doctype": "Sales Order",
            "is_consolidated": False,
            "items": [
                {"item_code": "Or (Gold)", "qty": 1, "custom_fixing_de_londre": 10.0,
                 "custom_teneur": 50.0, "custom_fixing_de_londres_par_once": 5.0,
                 "custom_cours_moyen_du_jour_": 20.0}
            ]
        })

        sales_order = frappe.get_doc(test_doc)
        calculate_taxes_and_totals.calculate_item_values(sales_order)

        self.assertAlmostEqual(sales_order.items[0].custom_prix_par_gr_dor_fondu_a_gr_en_usd, 4.0, delta=0.001)
        self.assertAlmostEqual(sales_order.items[0].rate, 80.0, delta=0.001)
        self.assertAlmostEqual(sales_order.items[0].amount, 80.0, delta=0.001)
