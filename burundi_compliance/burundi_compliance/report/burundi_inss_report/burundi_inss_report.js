// Copyright (c) 2024, Navari Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Burundi INSS Report"] = {
	// "filters": [
	// 	{
	// 		"fieldname":"company",
	// 		"label": __("Company"),
	// 		"fieldtype": "Link",
	// 		"options": "Company",
	// 		"default": frappe.defaults.get_user_default("Company"),
	// 		"width": "100px",
	// 		"reqd": 1
	// 	},
	// 	{
	// 		"fieldname":"from_date",
	// 		"label": __("Start Date"),
	// 		"fieldtype": "Date",
	// 		"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
	// 		"reqd": 1,
	// 		"width": "100px"
	// 	},
	// 	{
	// 		"fieldname":"to_date",
	// 		"label": __("End Date"),
	// 		"fieldtype": "Date",
	// 		"default": frappe.datetime.get_today(),
	// 		"reqd": 1,
	// 		"width": "100px"
	// 	},
	// 	{ 
	// 		"fieldname":"salary_component",
	// 		"label": __("Salary Component"),
	// 		"fieldtype": "Link",
	// 		"options": "Salary Component",
	// 		'default': "Base INSS",
	// 		"width": "100",
	// 		"reqd": 1
	// 	},
	// 	{
	// 		"fieldname": "currency",
	// 		"fieldtype": "Link",
	// 		"options": "Currency",
	// 		"label": __("Currency"),
	// 		"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
	// 		"width": "50px"
	// 	},
	// 	{
	// 		"fieldname":"docstatus",
	// 		"label":__("Document Status"),
	// 		"fieldtype":"Select",
	// 		"options":["Draft", "Submitted", "Cancelled"],
	// 		"default": "Submitted",
	// 		"width": "100px"
	// 	}
	// ]

	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"label": __("Currency"),
			"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
			"width": "50px"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default": "Submitted",
			"width": "100px"
		}
	]
};

// Path: burundi_compliance/burundi_compliance/burundi_compliance/report/burundi_inss_report/burundi_inss_report.py