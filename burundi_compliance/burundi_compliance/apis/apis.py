import frappe
from frappe import _


def get_ebims_settings():
    settings = frappe.get_s("EBIMS Settings")
    if not settings.is_active:
        frappe.throw(_("EBIMS Integration is disabled in settings."))
    return settings
