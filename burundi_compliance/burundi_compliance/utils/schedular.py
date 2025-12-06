import frappe

from burundi_compliance.burundi_compliance.overrides.stock_ledger_entry import send_data

# from burundi_compliance.burundi_compliance.overrides.sales_invoice import (
#     submit_invoice_request,
# )
import time
# from burundi_compliance.burundi_compliance.overrides.cancel_invoice import (
#     cancel_invoice,
# )


def check_and_send_pending_stock_ledger_entry():
    """
    Check and send unsend stock ledger entries
    """
    stock_ledger_entries = frappe.get_all(
        "Stock Ledger Entry",
        filters={"docstatus": 1, "custom_etracker": 0, "custom_queued": 0},
        fields=["name"],
        order_by="posting_time asc",
    )

    for stock_ledger_entry in stock_ledger_entries:
        try:
            stock_ledger_entry_doc = frappe.get_doc(
                "Stock Ledger Entry", stock_ledger_entry.name
            )
            if (
                stock_ledger_entry_doc.voucher_type == "Stock Reconciliation"
                and stock_ledger_entry_doc.has_batch_no == 1
                and stock_ledger_entry_doc.actual_qty < 0
            ):
                continue
            check_item = frappe.get_doc("Item", stock_ledger_entry_doc.item_code)
            if check_item.custom_allow_obr_to_track_stock_movement == 0:
                continue
            send_data(stock_ledger_entry_doc)
            frappe.db.set_value(
                "Stock Ledger Entry", stock_ledger_entry_doc.name, "custom_queued", 1
            )
            time.sleep(2)
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(),
                "Error in sending stock ledger entry {0}".format(
                    stock_ledger_entry.name
                ),
            )
            continue
