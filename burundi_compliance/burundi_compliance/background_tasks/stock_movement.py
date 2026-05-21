from datetime import datetime

import frappe

from ..apis.api_builder import OBRAPI
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..handlers.stock_movement import (
    handle_stock_ledger_entry_failure,
    handle_stock_ledger_entry_submission,
)
from ..utils.build_headers import build_headers
from ..utils.get_stock_ledger_data import get_stock_ledger_data
from ..utils.utils import get_urls, in_configured_timeslot


def send_stock_movement_to_obr() -> None:
    # Get all stock ledger entries not sent to OBR - use SQL query to join items and check if it's being tracked
    SLE = frappe.qb.DocType("Stock Ledger Entry")
    Item = frappe.qb.DocType("Item")
    query = (
        frappe.qb.from_(SLE)
        .join(Item)
        .on(SLE.item_code == Item.item_code)
        .select(SLE.name, SLE.company)
        .where(
            (SLE.docstatus == 1)
            & (SLE.custom_etracker == 0)
            & (SLE.custom_queued == 0)
            & (Item.custom_allow_obr_to_track_stock_movement == 1)
            & (Item.is_stock_item == 1),
        )
    )

    stock_ledger_entries = query.run(as_dict=True)

    if not stock_ledger_entries:
        return

    entries_by_company = {}
    for sle in stock_ledger_entries:
        company = sle.company
        if company not in entries_by_company:
            entries_by_company[company] = []
        entries_by_company[company].append(sle)

    for company, entries in entries_by_company.items():
        if not frappe.db.exists(SETTINGS_DOCTYPE_NAME, company):
            continue

        settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company)

        if not (
            settings_doc.is_active and settings_doc.allow_obr_to_track_stock_movement
        ):
            continue

        if not in_configured_timeslot(settings_doc, "stock"):
            continue

        start_date = settings_doc.start_date

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        environment = "sandbox" if settings_doc.sandbox else "production"
        request_url, server_url = get_urls(environment, "add_stock_movement")

        for sle_entry in entries:
            try:
                sle_doc = frappe.get_doc("Stock Ledger Entry", sle_entry.name)
                posting_date = sle_doc.posting_date

                if isinstance(posting_date, str):
                    posting_date = datetime.strptime(posting_date, "%Y-%m-%d").date()

                if posting_date < start_date:
                    continue

                if sle_doc.custom_queued == 1:
                    continue

                if (
                    sle_doc.voucher_type == "Stock Entry"
                    and frappe.db.get_value(
                        "Stock Entry",
                        sle_doc.voucher_no,
                        "purpose",
                    )
                    == "Material Transfer"
                ):
                    continue

                if (
                    sle_doc.voucher_type == "Stock Reconciliation"
                    and sle_doc.has_batch_no == 1
                    and sle_doc.actual_qty < 0
                ):
                    continue

                sle_data = get_stock_ledger_data(sle_doc)

                if not sle_data:
                    continue

                headers = build_headers(company)

                if headers and server_url and request_url:
                    url = f"{server_url}/{request_url}"
                    payload = sle_data

                    obr_api = OBRAPI()
                    obr_api.headers = headers
                    obr_api.url = url
                    obr_api.method = "POST"
                    obr_api.payload = payload
                    obr_api.service = "AddStockMovement"
                    obr_api.success_callback_handler = (
                        handle_stock_ledger_entry_submission
                    )
                    obr_api.error_callback_handler = handle_stock_ledger_entry_failure

                    frappe.enqueue(
                        obr_api.make_remote_request,
                        is_async=True,
                        queue="default",
                        timeout=600,
                        job_name=f"obr_stock_movement_submission_{sle_doc.name}",
                        doctype="Stock Ledger Entry",
                        document_name=sle_doc.name,
                    )

                    sle_doc.db_set("custom_queued", 1)
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "Error in sending stock ledger entry {0}".format(sle.name),
                )
                continue
