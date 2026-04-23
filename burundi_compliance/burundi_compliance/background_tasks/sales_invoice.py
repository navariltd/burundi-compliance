import frappe
from frappe.model.document import Document

from ..overrides.sales_invoice import on_submit_invoice, on_cancel


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
