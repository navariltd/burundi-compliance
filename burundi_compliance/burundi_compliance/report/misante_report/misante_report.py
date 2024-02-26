# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _


def execute(filters=None):

	company_currency = erpnext.get_company_currency(filters.get("company"))
	columns = get_columns()
	data = get_data(filters,company_currency)

	return columns, data

def get_columns():
	columns = [			
		{
		'label': _('Payroll Entry'),
		'fieldname': 'employee',
		'fieldtype': 'Link',
		'options': 'Employee',
		'width': 200
		},
		
		{
		'label': _('Names'),
		'fieldname': 'other_name',
		'fieldtype': 'Data',
		'width': 250
		},
				
		{
		'label': _('Employee MISANTE'),
		'fieldname': 'employee_nhif',
		'fieldtype': 'Data',
		'width': 150
		},
  {
		'label': _('Employer MISANTE'),
		'fieldname': 'employer_misante',
		'fieldtype': 'Data',
		'width': 150
		},

		{
		'label': _('Amount'),
		'fieldname': 'amount',
		'fieldtype': 'Currency',		
		'width': 200
		}
	]
		
	return columns

def get_data(filters,company_currency,conditions=""):
	if filters.from_date > filters.to_date:
		frappe.throw(_("To Date cannot be before From Date. {}").format(filters.to_date))
  
	employee = frappe.qb.DocType("Employee")
	salary_slip = frappe.qb.DocType("Salary Slip")
	salary_details = frappe.qb.DocType("Salary Detail")
	
	query = frappe.qb.from_(employee) \
		.inner_join(salary_slip) \
		.on(employee.name == salary_slip.employee) \
		.inner_join(salary_details) \
		.on(salary_slip.name == salary_details.parent) \
		.select(
			salary_slip.employee,
			employee.last_name if (employee.last_name) else "",
			employee.first_name,
			employee.middle_name,
			
			salary_details.amount,
			
		).where(salary_details.amount != 0)
	
	query = apply_filters(query, filters, company_currency, salary_slip, salary_details)
	data = query.run(as_dict=True)
	for entry in data:
		entry["other_name"] = (
			f"{entry['middle_name']} {entry['first_name']} {entry['last_name']}"
			if entry.get("middle_name")
			else entry["first_name"]
		)
	return data

def apply_filters(query, filters, company_currency, salary_slip, salary_detail):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	for filter_key, filter_value in filters.items():
		if filter_key == "from_date":
			query = query.where(salary_slip.start_date == filter_value)
		elif filter_key == "to_date":
			query = query.where(salary_slip.end_date == filter_value)
		elif filter_key == "company":
			query = query.where(salary_slip.company == filter_value)
		elif filter_key == "salary_component":
			query = query.where(salary_detail.salary_component == filter_value)
		elif filter_key == "currency" and filter_value != company_currency:
			query = query.where(salary_slip.currency == filter_value)
		elif filter_key == "docstatus":
			query = query.where(salary_slip.docstatus == doc_status.get(filter_value, 0))
	return query
