
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
	
	total_inss_map = create_total_inss(deduction_map)

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

		if currency == company_currency:
			row.update(
				{
					"gross_pay": flt(ss.gross_pay) * flt(ss.exchange_rate),
					"total_deduction": flt(ss.total_deduction) * flt(ss.exchange_rate),
					"net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
					"total_inss": total_inss_map.get(ss.name, {}).get("total_inss"),
				}
			)
		else:
			row.update(
				{
					"gross_pay": ss.gross_pay,
					"total_deduction": ss.total_deduction,
					"net_pay": ss.net_pay,
					"total_inss": total_inss_map.get(ss.name, {}).get("total_inss"),
				}
			)

		data.append(row)

	return columns, data

def create_total_inss(deduction_map):
    total_inss_map = {}

    for ss_name, components in deduction_map.items():
        total_inss = 0.0
        for key, value in components.items():
           
            if key in ["Employee INSS", "Employer INSS", "Risk"]:
                
                total_inss += value

        total_inss_map[ss_name] = {"total_inss": total_inss}

    return total_inss_map


def get_earning_and_deduction_types():
	deduction_types = ["Base INSS", "Employer INSS", "Employee INSS", "Risk Base", "Risk"]  # Add the desired earning types
	earning_types = ["Brut Patr Mens"]  # Add the desired deduction types
	return earning_types, deduction_types


def get_columns(earning_types, ded_types):
	columns = [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 150,
		},
		
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
		
	]

	for earning in earning_types:
		columns.append(
			{
				"label": earning,
				"fieldname": frappe.scrub(earning),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)
		

	columns.append(
		{
			"label": _("SAL BUT"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
	)

	for deduction in ded_types:
		columns.append(
			{
				"label": deduction,
				"fieldname": frappe.scrub(deduction),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)
	

	columns.extend(
		[
			{
				"label": _("Total"),
				"fieldname": "total_inss",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
	
		]
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
			key: value for key, value in components.items() if key in ["Base INSS", "Employer INSS", "Employee INSS", "Risk Base", "Risk"] 
		}
		if filtered_components:
			filtered_ss_ded_map[ss_name] = filtered_components

	return filtered_ss_earning_map, filtered_ss_ded_map


