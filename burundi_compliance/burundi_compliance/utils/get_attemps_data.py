
import frappe

def get_maximum_attempts():
    doc=frappe.get_doc("eBIMS Setting", frappe.defaults.get_user_default("Company"))
    permissions={
    "maximum_attempts":doc.maximum_attempts,
    "retry_delay_seconds":doc.retry_delay_seconds,
        
    }
    
    return permissions
    