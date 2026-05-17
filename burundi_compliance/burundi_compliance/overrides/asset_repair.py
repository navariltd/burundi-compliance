import frappe
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
)
from erpnext.assets.doctype.asset_repair.asset_repair import AssetRepair
from frappe import _


class CustomAssetRepair(AssetRepair):
    def decrease_stock_quantity(self):
        if not self.get("stock_items"):
            return

        if not self.custom_stock_movement_description:
            frappe.throw(_("Please set Stock Movement Description"))

        stock_entry = frappe.get_doc(
            {
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Issue",
                "company": self.company,
                "asset_repair": self.name,
                "custom_stock_movement_type": "Other Output(SAU)",
                "custom_stock_movement_description": self.custom_stock_movement_description,
            }
        )

        accounting_dimensions = {
            "cost_center": self.cost_center,
            "project": self.project,
            **{
                dimension: self.get(dimension)
                for dimension in get_accounting_dimensions()
            },
        }

        for stock_item in self.get("stock_items"):
            self.validate_serial_no(stock_item)

            stock_entry.append(
                "items",
                {
                    "s_warehouse": stock_item.warehouse,
                    "item_code": stock_item.item_code,
                    "qty": stock_item.consumed_quantity,
                    "basic_rate": stock_item.valuation_rate,
                    "serial_and_batch_bundle": stock_item.serial_and_batch_bundle,
                    **accounting_dimensions,
                },
            )

        stock_entry.insert()
        stock_entry.submit()
