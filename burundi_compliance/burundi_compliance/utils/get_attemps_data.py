
import frappe

def get_maximum_attempts():
    doc=frappe.get_doc("eBMS Settings", frappe.defaults.get_user_default("Company"))
    permissions={
    "maximum_attempts":doc.maximum_attempts,
    "retry_delay_seconds":doc.retry_delay_seconds,
        
    }
    if not permissions["maximum_attempts"]:
        frappe.throw("Please set the maximum attempts in eBMS Setting")
    elif not permissions["retry_delay_seconds"]:
        frappe.throw("Please set the retry delay seconds in eBMS Setting")
    
    return permissions
    