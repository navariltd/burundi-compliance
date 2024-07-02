
app_name = "burundi_compliance"
app_title = "Navari Burundian Revenue Authority Integration"
app_publisher = "Navari Limited"
app_description = "Burundian Revenue Authority (OBR) Integration with ERPNext by Navari Ltd"
app_email = "mania@navari.co.ke"
app_license = "GNU Affero General Public License v3.0"
required_apps = ["frappe/erpnext"]

fixtures=[
   "eBMS API Methods",
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/burundi_compliance/css/burundi_compliance.css"
app_include_js = [
    "burundi_compliance/public/js/taxes_and_totals.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/burundi_compliance/css/burundi_compliance.css"
# web_include_js = "/assets/burundi_compliance/js/burundi_compliance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "burundi_compliance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_js = {
    "Sales Invoice":"burundi_compliance/client_scripts/e_invoicing.js",
    "POS Invoice":"burundi_compliance/client_scripts/e_invoicing.js",
    "Company":"burundi_compliance/client_scripts/customer_supplier_check_tin.js",
    "Customer":"burundi_compliance/client_scripts/customer_supplier_check_tin.js",
    "Supplier":"burundi_compliance/client_scripts/customer_supplier_check_tin.js",
    "Purchase Invoice":"burundi_compliance/client_scripts/add_stock_movement.js",
    "Purchase Receipt":"burundi_compliance/client_scripts/add_stock_movement.js",
    "Delivery Note":"burundi_compliance/client_scripts/add_stock_movement.js",
    "Stock Entry":"burundi_compliance/client_scripts/add_stock_movement.js",
    "doctype" : "public/js/doctype.js"}


doctype_list_js = {
    "Sales Invoice" : "burundi_compliance/client_scripts/sales_invoice_list.js",
     "POS Invoice" : "burundi_compliance/client_scripts/pos_invoice_list.js",
    "Stock Ledger Entry" : "burundi_compliance/client_scripts/stock_list.js",
    "Stock Entry" : "burundi_compliance/client_scripts/stock_list.js",
    "Stock Reconciliation" : "burundi_compliance/client_scripts/stock_recon_list.js",
                   }


# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "burundi_compliance/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
    
	"methods": "burundi_compliance.burundi_compliance.utils.qr_code_generator.get_qr_code",
	#"filters": "burundi_compliance.utils.jinja_filters"
}

# Installation
# ------------

# before_install = "burundi_compliance.install.before_install"
# after_install = "burundi_compliance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "burundi_compliance.uninstall.before_uninstall"
# after_uninstall = "burundi_compliance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "burundi_compliance.utils.before_app_install"
# after_app_install = "burundi_compliance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "burundi_compliance.utils.before_app_uninstall"
# after_app_uninstall = "burundi_compliance.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "burundi_compliance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice":{
        
       "on_submit": "burundi_compliance.burundi_compliance.overrides.sales_invoice.on_submit",
        "before_cancel": "burundi_compliance.burundi_compliance.overrides.cancel_invoice.cancel_invoice",
        #"before_save": "burundi_compliance.burundi_compliance.overrides.sales_invoice.after_save",
        
    },
 "POS Invoice":{
        
       "on_submit": "burundi_compliance.burundi_compliance.overrides.sales_invoice.on_submit",
        "before_cancel": "burundi_compliance.burundi_compliance.overrides.cancel_invoice.cancel_invoice",
        #"before_save": "burundi_compliance.burundi_compliance.overrides.sales_invoice.after_save",
        
    },
    
    "Customer":{
        "before_save":"burundi_compliance.burundi_compliance.overrides.check_tin.customer_or_supplier_before_save"
    },
    "Supplier":{
        #use similar function with customer_check_tin
        "before_save":"burundi_compliance.burundi_compliance.overrides.check_tin.customer_or_supplier_before_save"
    },
    "Stock Ledger Entry":{
        "on_update":"burundi_compliance.burundi_compliance.overrides.stock_ledger_entry.on_update"
    }
    
}

# Scheduled Tasks minor changes
# ---------------

##################################################################################################################
##############################Remember to change the cron job to the correct time#################################
##################################################################################################################
# from burundi_compliance.burundi_compliance.utils.event_frequency_schedular import get_event_frequency
# invoice_frequency, stock_movement_frequency = get_event_frequency()

scheduler_events = {

 "cron":{
      "*/5 * * * *":["burundi_compliance.burundi_compliance.utils.schedular.check_and_send_pending_sales_invoices"],
        "*/2 * * * *":["burundi_compliance.burundi_compliance.utils.schedular.check_and_send_pending_stock_ledger_entry"], 
         "*/7 * * * *":["burundi_compliance.burundi_compliance.utils.schedular.check_and_send_pending_cancelled_sales_invoices"],
         "*/6 * * * *":["burundi_compliance.burundi_compliance.utils.schedular.check_and_send_submitted_invoice_which_were_cancelled"],
         "0 0 * * *":["burundi_compliance.burundi_compliance.utils.schedular.check_and_send_pending_cancelled_invoice_from_integration_request"]    
 },
 
}

# import frappe
# frappe.throw(f"{invoice_frequency} {stock_movement_frequency}")

# 	"daily": [
# 		"burundi_compliance.tasks.daily"
# 	],
# 	"hourly": [
# 		"burundi_compliance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"burundi_compliance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"burundi_compliance.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "burundi_compliance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "burundi_compliance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "burundi_compliance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["burundi_compliance.utils.before_request"]
# after_request = ["burundi_compliance.utils.after_request"]

# Job Events
# ----------
# before_job = ["burundi_compliance.utils.before_job"]
# after_job = ["burundi_compliance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"burundi_compliance.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

