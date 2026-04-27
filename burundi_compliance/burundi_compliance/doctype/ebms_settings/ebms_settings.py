# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

from croniter import croniter, CroniterBadCronError

import frappe
from frappe import _
from frappe.model.document import Document


class eBMSSettings(Document):
	def validate(self):
		if self.invoice_event_frequency == "Cron":
			if not self.invoice_cron_format:
				frappe.throw("Cron Format is required when Invoice Event Frequency is set to Cron")

			self.validate_cron_format(self.invoice_cron_format)

		if self.stock_movement_event_frequency == "Cron":
			if not self.stock_movement_cron_format:
				frappe.throw(
					"Cron Format is required when Stock Movement Event Frequency is set to Cron"
				)

			self.validate_cron_format(self.stock_movement_cron_format)

	@staticmethod
	def validate_cron_format(cron_format):
		try:
			croniter(cron_format)
		except CroniterBadCronError:
			frappe.throw(
				_("{0} is not a valid Cron expression.").format(f"<code>{cron_format}</code>"),
				title=_("Bad Cron Expression"),
			)

	def before_save(self):
		old_doc = self.get_doc_before_save()
		invoice_methods = [
			"burundi_compliance.burundi_compliance.background_tasks.sales_invoice.send_pending_cancelled_pos_invoices",
			"burundi_compliance.burundi_compliance.background_tasks.sales_invoice.send_pending_cancelled_sales_invoices",
			"burundi_compliance.burundi_compliance.background_tasks.sales_invoice.send_pending_pos_invoices",
			"burundi_compliance.burundi_compliance.background_tasks.sales_invoice.send_pending_sales_invoices",
		]

		stock_movement_methods = [
			"burundi_compliance.burundi_compliance.background_tasks.stock_movement.send_stock_movement_to_obr",
		]

		if self.has_invoice_schedule_changed(old_doc):
			self.update_scheduled_job(invoice_methods, "Sales Invoice")

		if self.has_stock_schedule_changed(old_doc):
			self.update_scheduled_job(stock_movement_methods, "Stock Movement")

	def has_invoice_schedule_changed(self, old_doc):
		if not old_doc:
			return True

		return (
			self.invoice_event_frequency != old_doc.invoice_event_frequency
			or self.invoice_cron_format != old_doc.invoice_cron_format
		)

	def has_stock_schedule_changed(self, old_doc):
		if not old_doc:
			return True

		return (
			self.stock_movement_event_frequency != old_doc.stock_movement_event_frequency
			or self.stock_movement_cron_format != old_doc.stock_movement_cron_format
		)

	def update_scheduled_job(self, method_list, method_type):
		schedule_type = None
		cron_format = None
		if method_type == "Sales Invoice":
			schedule_type = self.invoice_event_frequency
			cron_format = self.invoice_cron_format
		elif method_type == "Stock Movement":
			schedule_type = self.stock_movement_event_frequency
			cron_format = self.stock_movement_cron_format

		for method in method_list:

			try:
				job_name = frappe.db.get_value("Scheduled Job Type", {"method": method}, "name")

				job = frappe.get_doc("Scheduled Job Type", job_name)

				if schedule_type == "Hourly":
					job.frequency = "Hourly"
					job.cron_format = None

				elif schedule_type == "Daily":
					job.frequency = "Daily"
					job.cron_format = None

				elif schedule_type == "Weekly":
					job.frequency = "Weekly"
					job.cron_format = None

				elif schedule_type == "Monthly":
					job.frequency = "Monthly"
					job.cron_format = None

				elif schedule_type == "Yearly":
					job.frequency = "Yearly"
					job.cron_format = None

				elif schedule_type == "Cron":
					job.frequency = "Cron"
					job.cron_format = cron_format

				job.save()

			except Exception as e:
				frappe.throw(_(f"Error fetching Scheduled Job for method {method}: {str(e)}"))
				continue
