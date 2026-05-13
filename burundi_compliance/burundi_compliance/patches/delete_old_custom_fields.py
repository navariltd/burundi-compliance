import frappe
from frappe.custom.doctype.custom_field.custom_field import delete_custom_fields

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
        existing_fields = [
            field
            for field in fields
            if frappe.db.exists(
                "Custom Field",
                {
                    "dt": doctype,
                    "fieldname": field,
                },
            )
        ]

        if existing_fields:
            delete_custom_fields(doctype, existing_fields)
