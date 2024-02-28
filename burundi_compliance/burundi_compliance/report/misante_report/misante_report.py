


import frappe
from frappe import _
from frappe.utils import flt

import erpnext

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")


def execute(filters=None):
	if not filters:
		filters = {}

	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))

	salary_slips = get_salary_slips(filters, company_currency)

	if not salary_slips:
		return [], []

	earning_types, ded_types = get_earning_and_deduction_types()
	columns = get_columns(earning_types, ded_types)
		
	earning_map, deduction_map = filter_salary_slip_details(salary_slips, currency, company_currency)
	
	doj_map = get_employee_doj_map()

	data = []
	for ss in salary_slips:
		row = {
			"salary_slip_id": ss.name,
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"data_of_joining": doj_map.get(ss.employee),
			"branch": ss.branch,
			"department": ss.department,
			"designation": ss.designation,
			"company": ss.company,
			"start_date": ss.start_date,
			"end_date": ss.end_date,
			"leave_without_pay": ss.leave_without_pay,
			"payment_days": ss.payment_days,
			"currency": currency or company_currency,
			"total_loan_repayment": ss.total_loan_repayment,
		}

		for e in earning_types:
			row.update({frappe.scrub(e): earning_map.get(ss.name, {}).get(e)})

		for d in ded_types:
			row.update({frappe.scrub(d): deduction_map.get(ss.name, {}).get(d)})

		data.append(row)

	return columns, data



def get_earning_and_deduction_types():
	deduction_types =  ["Employer NHIF", "Employee NHIF", "NHIF"]  # Add the desired earning types
	earning_types = ["Brut Patr Mens"]  # Add the desired deduction types
	return earning_types, deduction_types


def get_columns(earning_types, ded_types):
	columns = [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 200,
		},
		
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 200,
		},
		
	]

	for deduction in ded_types:
		columns.append(
			{
				"label": deduction,
				"fieldname": frappe.scrub(deduction),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 200,
			}
		)
	

	return columns

def get_salary_components(salary_slips):
	return (
		frappe.qb.from_(salary_detail)
		.where((salary_detail.amount != 0) & (salary_detail.parent.isin([d.name for d in salary_slips])))
		.select(salary_detail.salary_component)
		.distinct()
	).run(pluck=True)


def get_salary_component_type(salary_component):
	return frappe.db.get_value("Salary Component", salary_component, "type", cache=True)


def get_salary_slips(filters, company_currency):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = frappe.qb.from_(salary_slip).select(salary_slip.star)

	if filters.get("docstatus"):
		query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])

	if filters.get("from_date"):
		query = query.where(salary_slip.start_date >= filters.get("from_date"))

	if filters.get("to_date"):
		query = query.where(salary_slip.end_date <= filters.get("to_date"))

	if filters.get("company"):
		query = query.where(salary_slip.company == filters.get("company"))

	if filters.get("employee"):
		query = query.where(salary_slip.employee == filters.get("employee"))

	if filters.get("currency") and filters.get("currency") != company_currency:
		query = query.where(salary_slip.currency == filters.get("currency"))

	salary_slips = query.run(as_dict=1)

	return salary_slips or []


def get_employee_doj_map():
	employee = frappe.qb.DocType("Employee")

	result = (frappe.qb.from_(employee).select(employee.name, employee.date_of_joining)).run()

	return frappe._dict(result)


def get_salary_slip_details(salary_slips, currency, company_currency, earnings=None, deductions=None):
	salary_slips = [ss.name for ss in salary_slips]
	if earnings:
		result = (
			frappe.qb.from_(salary_slip)
			.join(salary_detail)
			.on(salary_slip.name == salary_detail.parent)
			.where((salary_detail.parent.isin(salary_slips)) & (salary_detail.parentfield == earnings))
			.select(
				salary_detail.parent,
				salary_detail.salary_component,
				salary_detail.amount,
				salary_slip.exchange_rate,
			)
		).run(as_dict=1)
  
	elif deductions:
		result = (
			frappe.qb.from_(salary_slip)
			.join(salary_detail)
			.on(salary_slip.name == salary_detail.parent)
			.where((salary_detail.parent.isin(salary_slips)) & (salary_detail.parentfield == deductions))
			.select(
				salary_detail.parent,
				salary_detail.salary_component,
				salary_detail.amount,
				salary_slip.exchange_rate,
			)
		).run(as_dict=1)
		

	ss_map = {}

	for d in result:
		ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_map



def filter_salary_slip_details(salary_slips, currency, company_currency):
	ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

	filtered_ss_earning_map = {}
	for ss_name, components in ss_earning_map.items():
		filtered_components = {
			key: value for key, value in components.items() if key in ['Brut Patr Mens']
		}
		if filtered_components:
			filtered_ss_earning_map[ss_name] = filtered_components

	filtered_ss_ded_map = {}
	for ss_name, components in ss_ded_map.items():
		filtered_components = {
			key: value for key, value in components.items() if key in ["Employer NHIF", "Employee NHIF", "NHIF"] 
		}
		if filtered_components:
			filtered_ss_ded_map[ss_name] = filtered_components

	return filtered_ss_earning_map, filtered_ss_ded_map



# # Copyright (c) 2024, Navari Limited and contributors
# # For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe, erpnext
# from frappe import _


# def execute(filters=None):

# 	company_currency = erpnext.get_company_currency(filters.get("company"))
# 	columns = get_columns()
# 	data = get_data(filters,company_currency)

# 	return columns, data

# def get_columns():
# 	columns = [			
# 		{
# 		'label': _('Payroll Entry'),
# 		'fieldname': 'employee',
# 		'fieldtype': 'Link',
# 		'options': 'Employee',
# 		'width': 200
# 		},
		
# 		{
# 		'label': _('Names'),
# 		'fieldname': 'other_name',
# 		'fieldtype': 'Data',
# 		'width': 250
# 		},
				
# 		{
# 		'label': _('Employee MISANTE'),
# 		'fieldname': 'employee_nhif',
# 		'fieldtype': 'Data',
# 		'width': 150
# 		},
#   {
# 		'label': _('Employer MISANTE'),
# 		'fieldname': 'employer_misante',
# 		'fieldtype': 'Data',
# 		'width': 150
# 		},

# 		{
# 		'label': _('Amount'),
# 		'fieldname': 'amount',
# 		'fieldtype': 'Currency',		
# 		'width': 200
# 		}
# 	]
		
# 	return columns

# def get_data(filters,company_currency,conditions=""):
# 	if filters.from_date > filters.to_date:
# 		frappe.throw(_("To Date cannot be before From Date. {}").format(filters.to_date))
  
# 	employee = frappe.qb.DocType("Employee")
# 	salary_slip = frappe.qb.DocType("Salary Slip")
# 	salary_details = frappe.qb.DocType("Salary Detail")
	
# 	query = frappe.qb.from_(employee) \
# 		.inner_join(salary_slip) \
# 		.on(employee.name == salary_slip.employee) \
# 		.inner_join(salary_details) \
# 		.on(salary_slip.name == salary_details.parent) \
# 		.select(
# 			salary_slip.employee,
# 			employee.last_name if (employee.last_name) else "",
# 			employee.first_name,
# 			employee.middle_name,
			
# 			salary_details.amount,
			
# 		).where(salary_details.amount != 0)
	
# 	query = apply_filters(query, filters, company_currency, salary_slip, salary_details)
# 	data = query.run(as_dict=True)
# 	for entry in data:
# 		entry["other_name"] = (
# 			f"{entry['middle_name']} {entry['first_name']} {entry['last_name']}"
# 			if entry.get("middle_name")
# 			else entry["first_name"]
# 		)
# 	return data

# def apply_filters(query, filters, company_currency, salary_slip, salary_detail):
# 	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

# 	for filter_key, filter_value in filters.items():
# 		if filter_key == "from_date":
# 			query = query.where(salary_slip.start_date == filter_value)
# 		elif filter_key == "to_date":
# 			query = query.where(salary_slip.end_date == filter_value)
# 		elif filter_key == "company":
# 			query = query.where(salary_slip.company == filter_value)
# 		elif filter_key == "salary_component":
# 			query = query.where(salary_detail.salary_component == filter_value)
# 		elif filter_key == "currency" and filter_value != company_currency:
# 			query = query.where(salary_slip.currency == filter_value)
# 		elif filter_key == "docstatus":
# 			query = query.where(salary_slip.docstatus == doc_status.get(filter_value, 0))
# 	return query
