import frappe

default_company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")

def get_event_frequency():
    if default_company:
        setting_doc = frappe.get_doc("eBMS Settings", default_company)
        invoice_event_frequency = setting_doc.event_frequency
        stock_movement_event_frequency = setting_doc.stock_movement_event_frequency
        if invoice_event_frequency != "Cron" or stock_movement_event_frequency != "Cron":
            invoice_cron_format = convert_frequency_to_cron(invoice_event_frequency)
            stock_movement_cron_format = convert_frequency_to_cron(stock_movement_event_frequency)
            return invoice_cron_format, stock_movement_cron_format
        else:
            invoice_cron_format = setting_doc.cron_format
            stock_movement_cron_format = setting_doc.stock_movement_cron_format
            return invoice_cron_format, stock_movement_cron_format
    else:
        frappe.throw("Default company not set for the user.")

def convert_frequency_to_cron(frequency):
    if frequency == "All":
        return "* * * * *"
    elif frequency == "Hourly":
        return "0 * * * *"
    elif frequency == "Hourly Long":
        return "0 */2 * * *"
    elif frequency == "Daily":
        return "0 0 * * *"
    elif frequency == "Daily Long":
        return "0 0 */2 * *"
    elif frequency == "Weekly":
        return "0 0 * * 0"
    elif frequency == "Monthly":
        return "0 0 1 * *"
    elif frequency == "Yearly":
        return "0 0 1 1 *"
    else:
        return "*/59 * * * *"