import frappe

FIELDS_TO_DELETE = {
    "Sales Invoice": [
        "custom_etracker",
        "custom_differ_submission_to_obr",
    ],
    "POS Invoice": ["custom_etracker", "custom_differ_submission_to_obr"],
    "Delivery Note": [
        "custom_etracker",
    ],
    "Purchase Receipt": [
        "custom_etracker",
    ],
    "Purchase Invoice": [
        "custom_etracker",
    ],
    "Stock Reconciliation": [
        "custom_etracker",
    ],
    "Stock Entry": [
        "custom_etracker",
    ],
}


def execute():
    for doctype, fields in FIELDS_TO_DELETE.items():
        for fieldname in fields:
            try:
                if frappe.db.exists(
                    "Custom Field", {"dt": doctype, "fieldname": fieldname}
                ):
                    frappe.delete_doc("Custom Field", fieldname, force=True)
                    frappe.db.commit()

            except Exception as e:
                frappe.log_error("Error deleting custom field", e)
                frappe.db.rollback()

    frappe.db.commit()
