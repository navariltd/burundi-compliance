import frappe
from ..api_classes.base import OBRAPIBase
base_data=OBRAPIBase().get_auth_details()

import frappe
from ..api_classes.base import OBRAPIBase
from datetime import datetime, timedelta


base_data = OBRAPIBase().get_auth_details()

from datetime import datetime
from datetime import datetime, timedelta
import frappe.utils

def create_invoice_signature(doc):
    system_identification = base_data['system_identification_given_by_obr']

    TIN_ = frappe.get_value("Company", doc.company, "tax_id")
    if TIN_ is None:
        frappe.throw("Taxpayer Identification Number (TIN) is not available. Unable to create invoice signature.\n Kindly set that in Company Settings")

    # Convert posting_date to datetime object
    posting_date = frappe.utils.get_datetime(doc.posting_date)

    billing_date = posting_date.strftime("%Y%m%d")

    # Parse string time to timedelta
    posting_time = frappe.utils.get_timedelta(doc.posting_time)

    # Convert timedelta to datetime for posting time
    posting_datetime = datetime.combine(posting_date.date(), datetime.min.time()) + posting_time
    posting_time = posting_datetime.strftime("%H%M%S")

    invoice_number = doc.name
    if not system_identification:
        frappe.throw("System identification number is not available. Unable to create invoice signature.\n Kindly set that in EBIMS Settings")

    invoice_signature = f"{TIN_}/{system_identification}/{billing_date}{posting_time}/{invoice_number}"

    return invoice_signature
