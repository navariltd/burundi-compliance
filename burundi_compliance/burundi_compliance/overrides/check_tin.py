from ..api_classes.check_tin import TinVerifier
import frappe
from frappe import _
from ..api_classes.base import OBRAPIBase

obr_integration_base = OBRAPIBase()

auth_details = obr_integration_base.get_auth_details()
allow_obr_to_track_sales = auth_details["allow_obr_to_track_sales"]


def check_and_verify_tin(doc):
    if doc.tax_id is not None and not doc.custom_tin_verified:
        token = obr_integration_base.authenticate()

        try:
            tin_verifier = TinVerifier(token)
            customer_or_supplier_tin = doc.tax_id
            data = {"tp_TIN": f"{customer_or_supplier_tin}"}
            results = tin_verifier.check_tin(data)

            if not results.get("success"):
                frappe.throw("NIF du contribuable inconnu.")
            else:
                frappe.response["message"] = results["result"]
                doc.custom_tin_verified = 1
                frappe.msgprint(
                    f"NIF du contribuable connu - {results['result']['taxpayer'][0]['tp_name']}"
                )
        except Exception as e:
            title = _("Error in TIN Verification")
            msg = _(str(e))
            frappe.log_error(title, msg)
            frappe.throw(_("An error occurred while verifying the TIN."))


@frappe.whitelist(allow_guest=True)
def customer_or_supplier_before_save(doc, method=None):
    """Check and verify the customer's TIN if applicable."""
    if allow_obr_to_track_sales:
        if doc.custom_gst_category == "Registered" and doc.tax_id is None:
            frappe.throw(
                _("Le NIF est obligatoire pour les contribuables enregistrés.")
            )

        elif (
            doc.custom_gst_category == "Registered"
            and doc.tax_id is not None
            and not doc.custom_tin_verified
        ):
            check_and_verify_tin(doc)


@frappe.whitelist(allow_guest=True)
def supplier_before_save(doc, method=None):
    """Check and verify the supplier's TIN if applicable."""
    if allow_obr_to_track_sales:
        if doc.tax_id is not None and not doc.custom_tin_verified:
            check_and_verify_tin(doc)
