import frappe


def handle_stock_ledger_entry_submission(
	response: dict, document_name: str, doctype: str
) -> None:
	try:
		data_to_update = {
			"custom_sent_to_obr": 1,
		}
		if doctype == "Stock Ledger Entry":
			data_to_update["custom_etracker"] = 1

		frappe.db.set_value(doctype, document_name, data_to_update)
		frappe.db.commit()

	except Exception as e:
		frappe.log_error(f"Error updating {doctype} {document_name}: {str(e)}")


def handle_stock_ledger_entry_failure(
	response: dict, document_name: str, doctype: str
) -> None:
	try:
		data_to_update = {
			"custom_queued": 0,
		}

		frappe.db.set_value(doctype, document_name, data_to_update)
		frappe.db.commit()

	except Exception as e:
		frappe.log_error(f"Error updating {doctype} {document_name}: {str(e)}")
