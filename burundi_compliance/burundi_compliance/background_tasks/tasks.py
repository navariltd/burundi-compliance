from datetime import datetime
import frappe

# from frappe import _
from frappe.model.document import Document

from ..overrides.sales_invoice import on_submit_invoice, on_cancel
from ..apis.utils.get_stock_ledger_data import get_stock_ledger_data
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..apis.utils.build_headers import build_headers
from ..apis.utils.utils import get_urls
from ..apis.api_builder import OBRAPI
from ..handlers.stock_movement import (
	handle_stock_ledger_entry_submission,
	handle_stock_ledger_entry_failure,
)


def send_pending_sales_invoices() -> None:
	all_submitted_unsent: list[Document] = frappe.get_all(
		"Sales Invoice",
		{"docstatus": 1, "custom_submitted_to_obr": 0, "is_opening": "No"},
		["name"],
	)

	if all_submitted_unsent:
		for sales_invoice in all_submitted_unsent:
			doc = frappe.get_doc("Sales Invoice", sales_invoice.name, for_update=False)

			try:
				on_submit_invoice(doc, method=None)

			except TypeError:
				continue


def send_pending_pos_invoices() -> None:
	all_pending_pos_invoices: list[Document] = frappe.get_all(
		"POS Invoice", {"docstatus": 1, "custom_submitted_to_obr": 0}, ["name"]
	)

	if all_pending_pos_invoices:
		for pos_invoice in all_pending_pos_invoices:
			doc = frappe.get_doc(
				"POS Invoice", pos_invoice.name, for_update=False
			)  # Refetch to get the document representation of the record

			try:
				on_submit_invoice(
					doc, method=None
				)  # Delegate to the on_submit method for sales invoices

			except Exception:
				continue


def send_pending_cancelled_sales_invoices() -> None:
	all_cancelled_sales_invoices: list[Document] = frappe.get_all(
		"Sales Invoice",
		{"docstatus": 2, "custom_submitted_to_obr": 1, "is_opening": "No"},
		["name"],
	)

	if all_cancelled_sales_invoices:
		for sales_invoice in all_cancelled_sales_invoices:
			doc = frappe.get_doc("Sales Invoice", sales_invoice.name, for_update=False)

			try:
				on_cancel(doc, method=None)

			except Exception:
				continue


def send_pending_cancelled_pos_invoices() -> None:
	all_cancelled_pos_invoices: list[Document] = frappe.get_all(
		"POS Invoice",
		{"docstatus": 2, "custom_submitted_to_obr": 1, "is_opening": "No"},
		["name"],
	)

	if all_cancelled_pos_invoices:
		for pos_invoice in all_cancelled_pos_invoices:
			doc = frappe.get_doc("POS Invoice", pos_invoice.name, for_update=False)

			try:
				on_cancel(doc, method=None)

			except Exception:
				continue


# Add a function to apis.py that will execute this fn
def send_stock_movement_to_obr() -> None:
	# Get all stock ledger entries not sent to OBR - use SQL query to join items and check if it's being tracked
	SLE = frappe.qb.DocType("Stock Ledger Entry")
	Item = frappe.qb.DocType("Item")
	query = (
		frappe.qb.from_(SLE)
		.join(Item)
		.on(SLE.item_code == Item.item_code)
		.select(SLE.name)
		.where(
			(SLE.docstatus == 1)
			& (SLE.custom_etracker == 0)
			& (SLE.custom_queued == 0)
			& (Item.custom_allow_obr_to_track_stock_movement == 1),
		)
	)

	stock_ledger_entries = query.run(as_dict=True)
	# Determine stock movement type

	for sle in stock_ledger_entries:
		try:
			sle_doc = frappe.get_doc("Stock Ledger Entry", sle.name)

			company = sle_doc.company

			if not frappe.db.exists(SETTINGS_DOCTYPE_NAME, company):
				continue

			settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company)

			if not settings_doc.is_active or not settings_doc.allow_obr_to_track_stock_movement:
				continue

			posting_date, start_date = sle_doc.posting_date, settings_doc.start_date
			if isinstance(posting_date, str):
				posting_date = datetime.strptime(posting_date, "%Y-%m-%d").date()
			if isinstance(start_date, str):
				start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

			if posting_date < start_date:
				continue

			if sle_doc.custom_queued == 1:
				continue

			# Check if it's a material transfer, if yes, skip
			if (
				sle_doc.voucher_type == "Stock Entry"
				and frappe.get_doc("Stock Entry", sle_doc.voucher_no).stock_entry_type
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

			environment = "sandbox" if settings_doc.sandbox else "production"
			headers = build_headers(company)

			request_url, server_url = get_urls(environment, "add_stock_movement")

			if headers and server_url and request_url:
				url = f"{server_url}/{request_url}"
				payload = sle_data

				obr_api = OBRAPI()
				obr_api.headers = headers
				obr_api.url = url
				obr_api.method = "POST"
				obr_api.payload = payload
				obr_api.service = "AddStockMovement"
				obr_api.success_callback_handler = handle_stock_ledger_entry_submission
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

		except Exception as e:
			frappe.log_error(
				frappe.get_traceback(),
				"Error in sending stock ledger entry {0}".format(sle.name),
			)
			continue

	# loop through each, build payload, headers and make remote request to OBR
	# Item designation should be the item description, check the revision that was made
	# when making the request, mark at as queued and remove the queued mark when the response is received
