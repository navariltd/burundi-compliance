import frappe
from frappe import _

from ...doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME
from ..auth import authenticate


def build_headers(company_name: str):
    settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, company_name)
    if not settings_doc.is_active:
        frappe.throw(_("eBMS Integration is disabled in settings."))

    # if (
    #     settings_doc.expires_at
    #     and settings_doc.expires_at < frappe.utils.now_datetime()
    # ):
    # settings_doc = authenticate(company_name)
    settings_doc = authenticate(company_name)

    if settings_doc:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings_doc.authorization_token}",
        }

        return headers

    frappe.throw(_("Failed to build headers for eBMS API."))
