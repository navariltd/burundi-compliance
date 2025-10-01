from ..api_classes.base import OBRAPIBase
from bs4 import BeautifulSoup

import frappe
from frappe import _

base_data = OBRAPIBase().get_auth_details()


def get_invoice_data(doc):
    name = doc.name

    ct_motif = doc.custom_reason_for_creditcancel
    if doc.custom_submitted_to_obr and not ct_motif:
        frappe.throw(
            _(
                f"Unable to cancel invoice.\n Kindly set the Reason For Cancelling the Invoice for {name} invoice"
            )
        )

        soup = BeautifulSoup(ct_motif, "html.parser")
        ct_motif = soup.get_text()

    # Fetch signature created
    invoice_identifier = doc.custom_invoice_identifier

    if not invoice_identifier:
        return

    if not doc.custom_submitted_to_obr:
        return

    data = {"invoice_signature": f"{invoice_identifier}", "cn_motif": ct_motif}

    return data
