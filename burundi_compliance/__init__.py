import frappe
from frappe.utils.user import is_website_user

__version__ = "0.0.1"


def check_app_permission():
    """Show Burundi Compliance to authorized Desk users."""
    if is_website_user():
        return False

    return any(
        frappe.has_permission(doctype, "read")
        for doctype in (
            "eBMS Settings",
            "eBMS API Methods",
            "eBMS Endpoint URLs",
        )
    )
