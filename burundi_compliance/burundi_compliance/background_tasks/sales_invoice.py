from datetime import datetime
from bs4 import BeautifulSoup

import frappe
from frappe.model.document import Document

from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..utils.utils import get_urls, in_configured_timeslot
from ..utils.build_headers import build_headers
from ..utils.build_invoice_payload import build_invoice_payload
from ..apis.api_builder import OBRAPI
from ..handlers.sales_invoice import (
	handle_sales_invoice_cancellation,
	handle_sales_invoice_submission,
)


def send_pending_sales_invoices() -> None:
	all_submitted_unsent: list[Document] = frappe.get_all(
		"Sales Invoice",
		{"docstatus": 1, "custom_submitted_to_obr": 0, "is_opening": "No"},
		["name", "company"],
	)

	if all_submitted_unsent:
		send_pending_invoices(all_submitted_unsent, "Sales Invoice")


def send_pending_pos_invoices() -> None:
	all_pending_pos_invoices: list[Document] = frappe.get_all(
		"POS Invoice",
		{"docstatus": 1, "custom_submitted_to_obr": 0},
		["name", "company"],
	)

	if all_pending_pos_invoices:
		send_pending_invoices(all_pending_pos_invoices, "POS Invoice")


def send_pending_cancelled_sales_invoices() -> None:
	all_cancelled_sales_invoices: list[Document] = frappe.get_all(
		"Sales Invoice",
		{"docstatus": 2, "custom_submitted_to_obr": 1, "is_opening": "No"},
		["name"],
	)

	if all_cancelled_sales_invoices:
		send_pending_cancelled_invoices(all_cancelled_sales_invoices, "Sales Invoice")


def send_pending_cancelled_pos_invoices() -> None:
	all_cancelled_pos_invoices: list[Document] = frappe.get_all(
		"POS Invoice",
		{"docstatus": 2, "custom_submitted_to_obr": 1, "is_opening": "No"},
		["name", "company"],
	)

	if all_cancelled_pos_invoices:
		send_pending_cancelled_invoices(all_cancelled_pos_invoices, "POS Invoice")


def send_pending_invoices(invoice_list: list, doctype: str) -> None:
	invoices_by_company = {}
	for invoice in invoice_list:
		company = invoice.company
		if company not in invoices_by_company:
			invoices_by_company[company] = []
		invoices_by_company[company].append(invoice)

	for company, invoices in invoices_by_company.items():
		if not frappe.db.exists(SETTINGS_DOCTYPE_NAME, company):
			continue
		settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company)

		if not settings_doc.is_active or not settings_doc.allow_obr_to_track_sales:
			continue

		if not in_configured_timeslot(settings_doc, "invoice"):
			continue

		start_date = settings_doc.start_date
		if isinstance(start_date, str):
			start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

		environment = "sandbox" if settings_doc.sandbox else "production"
		request_url, server_url = get_urls(environment, "add_invoice")

		for invoice in invoices:
			try:
				doc = frappe.get_doc(doctype, invoice.name, for_update=False)
				if doc.is_opening == "Yes":
					continue

				if doc.custom_defer_submission_to_obr:
					continue

				if doc.doctype == "Sales Invoice" and doc.is_consolidated:
					continue

				if doc.custom_submitted_to_obr:
					continue

				posting_date = doc.posting_date
				if isinstance(posting_date, str):
					posting_date = datetime.strptime(posting_date, "%Y-%m-%d").date()

				if posting_date < start_date:
					continue

				headers = build_headers(company)

				if headers and server_url and request_url:
					url = f"{server_url}/{request_url}"
					payload = build_invoice_payload(doc, settings_doc)

					obr_api = OBRAPI()
					obr_api.headers = headers
					obr_api.url = url
					obr_api.method = "POST"
					obr_api.payload = payload
					obr_api.service = "AddCreditNote" if doc.is_return else "AddInvoice"
					obr_api.success_callback_handler = handle_sales_invoice_submission
					# obr_api.error_callback_handler = handler

					frappe.enqueue(
						obr_api.make_remote_request,
						is_async=True,
						queue="default",
						timeout=600,
						job_name=f"obr_invoice_submission_{doc.name}",
						doctype="Sales Invoice",
						document_name=doc.name,
					)
			except Exception as e:
				frappe.log_error(
					message=f"Error processing {doctype} {invoice.name} for OBR submission: {str(e)}",
					title="OBR Invoice Submission Error",
				)
				continue


def send_pending_cancelled_invoices(invoice_list: list, doctype: str) -> None:
	invoices_by_company = {}
	for invoice in invoice_list:
		company = invoice.company
		if company not in invoices_by_company:
			invoices_by_company[company] = []
		invoices_by_company[company].append(invoice)

	for company, invoices in invoices_by_company.items():
		if not frappe.db.exists(SETTINGS_DOCTYPE_NAME, company):
			continue
		settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company)

		if not settings_doc.is_active or not settings_doc.allow_obr_to_track_sales:
			continue

		if not in_configured_timeslot(settings_doc, "invoice"):
			continue

		start_date = settings_doc.start_date
		if isinstance(start_date, str):
			start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

		environment = "sandbox" if settings_doc.sandbox else "production"
		request_url, server_url = get_urls(environment, "cancel_invoice")

		for invoice in invoices:
			try:
				doc = frappe.get_doc(doctype, invoice.name, for_update=False)

				if doc.custom_submitted_to_obr:
					continue

				posting_date = doc.posting_date
				if isinstance(posting_date, str):
					posting_date = datetime.strptime(posting_date, "%Y-%m-%d").date()

				if posting_date < start_date:
					continue

				if not doc.custom_reason_for_creditcancel:
					frappe.log_error(
						message=f"Sales Invoice {doc.name} is missing reason for cancellation/credit note. Skipping OBR submission.",
						title="OBR Invoice Cancellation Error",
					)
					continue

				soup = BeautifulSoup(doc.custom_reason_for_creditcancel, "html.parser")
				ct_motif = soup.get_text()

				invoice_identifier = doc.custom_invoice_identifier
				if not invoice_identifier:
					return
				invoice_data = {
					"invoice_signature": f"{invoice_identifier}",
					"cn_motif": ct_motif,
				}

				headers = build_headers(company)

				if headers and server_url and request_url:
					url = f"{server_url}/{request_url}"
					payload = invoice_data

					obr_api = OBRAPI()
					obr_api.headers = headers
					obr_api.url = url
					obr_api.method = "POST"
					obr_api.payload = payload
					obr_api.service = "CancelInvoice"
					obr_api.success_callback_handler = handle_sales_invoice_cancellation
					# obr_api.error_callback_handler = handler

					frappe.enqueue(
						obr_api.make_remote_request,
						is_async=True,
						queue="default",
						timeout=600,
						job_name=f"obr_invoice_cancellation_{doc.name}",
						doctype=doc.doctype,
						document_name=doc.name,
					)
			except Exception as e:
				frappe.log_error(
					message=f"Error processing {doctype} {invoice.name} for OBR cancellation: {str(e)}",
					title="OBR Invoice Cancellation Error",
				)
				continue
