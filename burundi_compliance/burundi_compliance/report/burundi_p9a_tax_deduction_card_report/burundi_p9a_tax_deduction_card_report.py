# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import calendar
import frappe
import erpnext
from frappe import _
from frappe.utils import (flt, cstr, getdate, get_year_start, get_year_ending, get_first_day, get_last_day)

def execute(filters=None):
    if not filters:
        filters = {}
    currency = None

    if filters.get('currency'):
        currency = filters.get('currency')     
    company_currency = erpnext.get_company_currency(filters.get("company"))

    if not filters.fiscal_year:
        frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

    fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)

    if not fiscal_year:
        frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    else:
        fiscal_year_start_date = getdate(fiscal_year.year_start_date)
        p9a_year_start_date = getdate(get_year_start(fiscal_year_start_date))
        p9a_year_end_date = getdate(get_year_ending(fiscal_year_start_date))
        validate_dates(p9a_year_start_date, p9a_year_end_date)
        p9a_tdc_year_name = filters.fiscal_year
        p9a_tdc_year = p9a_tdc_year_name[0:4] # for cases where fiscal year starts between the year
        no_of_months = get_months(p9a_year_start_date, p9a_year_end_date)

    columns = get_columns()

    employees = get_employees(filters)
    if not employees:
        return [], []

    p9a_tax_deduction_card_type = ("Salaire de base",
                                    "Benefits NonCash",
                                    "Value of Quarters",
                                    "Total Gross Pay",
                                    "E1 Defined Contribution Retirement Scheme",
                                    "E2 Defined Contribution Retirement Scheme",
                                    "E3 Defined Contribution Retirement Scheme",
                                    "Owner Occupied Interest",
                                    "Retirement Contribution and Owner Occupied Interest",
                                    "Chargeable Pay",
                                    "Tax Charged",
                                    "Personal Relief",
                                    "Insurance Relief",
                                    "PAYE Tax")

    data = []
    for emp in employees:        
        for month_idx in range(1, no_of_months):                
            month_date_string = cstr(p9a_tdc_year) + "-" + cstr(month_idx) + "-" + cstr(1)
            month_date_obj = getdate(month_date_string)
            month_start_date = get_first_day(month_date_obj)
            month_end_date = get_last_day(month_start_date)

            month_name = calendar.month_name[month_idx]

            basic_salary_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[0],
                                                              currency, company_currency)
            benefits_non_cash_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[1],
                                                              currency, company_currency)
            value_of_quarters_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[2],
                                                              currency, company_currency)
            total_gross_pay_amt = get_p9a_tax_deduction_card_gross_pay(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              currency, company_currency)
            e1_defined_contribution_retirement_scheme_amt = flt((30/100) * basic_salary_amt)

            e2_defined_contribution_retirement_scheme_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[5],
                                                              currency, company_currency)
            if (basic_salary_amt > 0):
                e3_defined_contribution_retirement_scheme_amt = get_p9a_tax_deduction_card_fixed_component_amt(
                                                              p9a_tax_deduction_card_type[6])
            else:
                e3_defined_contribution_retirement_scheme_amt = 0
            lowest_of_column_e = min(e1_defined_contribution_retirement_scheme_amt, 
                                     e2_defined_contribution_retirement_scheme_amt,
                                     e3_defined_contribution_retirement_scheme_amt)
            owner_occupied_interest_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[7],
                                                              currency, company_currency)
            retirement_contribution_and_owner_occupied_interest_amt = (lowest_of_column_e 
                                                                       + owner_occupied_interest_amt)
            chargeable_pay_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[9],
                                                              currency, company_currency)
            tax_charged_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[10],
                                                              currency, company_currency)
            personal_relief_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[11],
                                                              currency, company_currency)
            insurance_relief_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[12],
                                                              currency, company_currency)
            paye_tax_amt = get_p9a_tax_deduction_card_amt(filters, emp.name,
                                                              month_start_date, month_end_date,
                                                              p9a_tax_deduction_card_type[13],
                                                              currency, company_currency)

            row = [month_name,
                    basic_salary_amt,
                    benefits_non_cash_amt,
                    value_of_quarters_amt,
                    total_gross_pay_amt,
                    e1_defined_contribution_retirement_scheme_amt,
                    e2_defined_contribution_retirement_scheme_amt,
                    e3_defined_contribution_retirement_scheme_amt,
                    owner_occupied_interest_amt,
                    retirement_contribution_and_owner_occupied_interest_amt,
                    chargeable_pay_amt,
                    tax_charged_amt,
                    personal_relief_amt,
                    insurance_relief_amt,
                    paye_tax_amt]

            data.append(row)

    return columns, data

def validate_dates(p9a_year_start_date, p9a_year_end_date):
    if not p9a_year_start_date or not p9a_year_end_date:
        frappe.throw("P9A Year Start Date and P9A Year End Date are mandatory")
    if p9a_year_end_date < p9a_year_start_date:
        frappe.throw("P9A Year End Date cannot be less than P9A Year Start Date")

def get_months(period_start_date, period_end_date):
    start_date = getdate(period_start_date)
    end_date = getdate(period_end_date)

    diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)

    return diff + 2

def get_columns():
    columns = [{
        "fieldname": "month",
        "label": _("Month"),
        "fieldtype": "Data",
        "width": 150
    },
        {
        "fieldname": "basic_salary",
        "label": _("Salaire de base"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "benefits_non_cash",
        "label": _("Benefits NonCash | B"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "value_of_quarters",
        "label": _("Value of Quarters | C"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "total_gross_pay",
        "label": _("Total Gross Pay | D"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "e1_defined_contribution_retirement_scheme",
        "label": _("Defined Contribution Retirement Scheme | E1"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "e2_defined_contribution_retirement_scheme",
        "label": _("Defined Contribution Retirement Scheme | E2"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "e3_defined_contribution_retirement_scheme",
        "label": _("Defined Contribution Retirement Scheme | E3"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "owner_occupied_interest",
        "label": _("Owner Occupied Interest | F"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "retirement_contribution_and_owner_occupied_interest",
        "label": _("Retirement Contribution and Owner Occupied Interest | G"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "chargeable_pay",
        "label": _("Chargeable Pay | H"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "tax_charged",
        "label": _("Tax Charged | I"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "personal_relief",
        "label": _("Personal Relief | K"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "insurance_relief",
        "label": _("Assurance"),
        "fieldtype": "Currency",
        "width": 150
    },
        {
        "fieldname": "paye_tax",
        "label": _("PAYE Tax | L"),
        "fieldtype": "Currency",
        "width": 150
    }]

    return columns

def get_employees(filters):
    employees_doc=frappe.qb.DocType("Employee")
    employee_query=frappe.qb.from_(employees_doc).select(employees_doc.name,employees_doc.company)\
        .where(
            (employees_doc.name==filters.get("employee")) &
            (employees_doc.company==filters.get("company"))
        ).orderby(
            (employees_doc.name) & (employees_doc.company)
        )
    employees=employee_query.run(as_dict=True)
       
    return employees

    
def get_p9a_tax_deduction_card_amt(filters, employee, month_start_date, month_end_date, p9a_tax_deduction_card_type, currency, company_currency): 
    currency_filter = ''
    if filters.get("currency") and filters.get("currency") != company_currency:
        currency_filter = currency
    else:
        currency_filter = filters.get("currency")
    
    salary_slip_doc=frappe.qb.DocType("Salary Slip")
    salary_detail_doc=frappe.qb.DocType("Salary Detail")
    salary_component_doc=frappe.qb.DocType("Salary Component")
    salary_slip_query=frappe.qb.from_(salary_slip_doc)\
                        .inner_join(salary_detail_doc)\
                        .on(salary_slip_doc.name==salary_detail_doc.parent)\
                        .inner_join(salary_component_doc)\
                        .on(salary_detail_doc.salary_component==salary_component_doc.name)\
                    .select(salary_slip_doc.employee,salary_slip_doc.docstatus,
                        salary_slip_doc.currency,salary_slip_doc.start_date,
                        salary_slip_doc.end_date,salary_slip_doc.company,
                        (salary_detail_doc.amount.as_("amt") if salary_detail_doc.amount else 0).as_("amt"),salary_slip_doc.exchange_rate,
                        salary_component_doc.custom_p9a_tax_deduction_card_type)\
                    .where(
                        (salary_slip_doc.docstatus==1) &
                        (salary_component_doc.custom_p9a_tax_deduction_card_type==p9a_tax_deduction_card_type) &
                        (salary_slip_doc.employee==employee) &
                        (salary_slip_doc.company==filters.get("company")) &
                        (salary_slip_doc.start_date==month_start_date) &
                        (salary_slip_doc.end_date==month_end_date) &
                        (salary_slip_doc.currency==currency_filter)
                        
                    ).orderby(
                        (salary_slip_doc.employee) & (salary_slip_doc.start_date)
                    )
                    
    ss_p9a_tax_deduction_card_component_=salary_slip_query.run(as_dict=True)
    
    p9a_tax_deduction_card_amount = 0
    for d in ss_p9a_tax_deduction_card_component_:
        if currency != company_currency:
            p9a_tax_deduction_card_amount += flt(d.amt) * flt(d.exchange_rate if d.exchange_rate else 1)
        else:
            p9a_tax_deduction_card_amount += flt(d.amt)

    return p9a_tax_deduction_card_amount

def get_p9a_tax_deduction_card_gross_pay(filters, employee, month_start_date, month_end_date, currency, company_currency): 
    currency_filter = ''
    if filters.get("currency") and filters.get("currency") != company_currency:
        currency_filter = currency
    else:
        currency_filter = filters.get("currency")
    
    salary_slip_doc=frappe.qb.DocType("Salary Slip")
    salary_slip_query=frappe.qb.from_(salary_slip_doc)\
                    .select(salary_slip_doc.employee,salary_slip_doc.docstatus,
                        salary_slip_doc.currency,salary_slip_doc.start_date,
                        salary_slip_doc.end_date,salary_slip_doc.company,
                        (salary_slip_doc.gross_pay.as_("amt") if salary_slip_doc.gross_pay else 0).as_("amt"),salary_slip_doc.exchange_rate)\
                    .where(
                        (salary_slip_doc.docstatus==1) &
                        (salary_slip_doc.employee==employee) &
                        (salary_slip_doc.company==filters.get("company")) &
                        (salary_slip_doc.start_date==month_start_date) &
                        (salary_slip_doc.end_date==month_end_date) &
                        (salary_slip_doc.currency==currency_filter)
                        
                    ).orderby(
                        (salary_slip_doc.employee) & (salary_slip_doc.start_date)
                    
                    )
    ss_p9a_tax_deduction_card_gross_pay_=salary_slip_query.run(as_dict=True)
    
    p9a_tax_deduction_card_gross_pay = 0
    for d in ss_p9a_tax_deduction_card_gross_pay_:
        if currency != company_currency:
            p9a_tax_deduction_card_gross_pay += flt(d.amt) * flt(d.exchange_rate if d.exchange_rate else 1)
        else:
            p9a_tax_deduction_card_gross_pay += flt(d.amt)

    return p9a_tax_deduction_card_gross_pay

def get_p9a_tax_deduction_card_fixed_component_amt(p9a_tax_deduction_card_type):
    salary_component_doc=frappe.qb.DocType("Salary Component")
    salary_component_query=frappe.qb.from_(salary_component_doc)\
        .select((salary_component_doc.amount.as_("amt") if salary_component_doc.amount else 0).as_('amt'))\
        .where(
            (salary_component_doc.custom_p9a_tax_deduction_card_type==p9a_tax_deduction_card_type)
        )
    p9a_tax_deduction_card_fixed_component=salary_component_query.run(as_dict=True)

    p9a_tax_deduction_card_fixed_component_amt = 0
    for d in p9a_tax_deduction_card_fixed_component:
        p9a_tax_deduction_card_fixed_component_amt += flt(d.amt)

    return p9a_tax_deduction_card_fixed_component_amt

