import frappe

default_company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")

def get_event_frequency():
    if default_company:
        setting_doc = frappe.get_doc("eBMS Settings", default_company)
        event_frequency = setting_doc.event_frequency
        if event_frequency != "Cron":
            return event_frequency
        return "Cron"
    else:
        frappe.throw("Default company not set for the user.")
    

def get_cron_frequency():
    setting_doc=frappe.get_doc("eBMS Settings", default_company)
    cron_frequency=setting_doc.event_frequency
    if cron_frequency=="Cron":
        cron_forrmat=setting_doc.cron_format
        if cron_forrmat is not None:
            return cron_forrmat
        else:
            return "*/2 * * * *"