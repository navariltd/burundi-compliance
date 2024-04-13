# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika import Case
from functools import reduce

def execute(filters=None):
    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date"))
    return get_columns(), get_p10_report_data(filters)

def get_columns():
    columns = [
        {
            "fieldname": "custom_tax_id",
            "label": _("PIN of Employee"), 
            "fieldtype": "Link", 
            "options": "Employee", 
            "width": 150
        },
        
        {   
            "fieldname": "employee_name", 
            "label": _("Nom & Prenoms"),
            "fieldtype": "Data", 
            "read_only": 1,
            "width": 150
        },
        
           {
            "fieldname": "base_imposable", 
            "label": _("Base imposable"), 
            "fieldtype": "Currency", 
            "width": 150
         },
           
        
          {
            "fieldname": "base_ire_0%", 
            "label": _("Base IRE 0%"), 
            "fieldtype": "Currency", 
            "width": 150
         },

           {
            "fieldname": "base_ire_20%", 
            "label": _("Base IRE 20%"), 
            "fieldtype": "Currency", 
            "width": 150
         },

           {
            "fieldname": "base_ire_30%", 
            "label": _("Base IRE 30%"), 
            "fieldtype": "Currency", 
            "width": 150
         },
        
         {
            "fieldname": "ire_0%", 
            "label": _("IRE 0%"), 
            "fieldtype": "Currency", 
            "width": 150
         },
         
          {
            "fieldname": "ire_20%", 
            "label": _("IRE 20%"), 
            "fieldtype": "Currency", 
            "width": 150
         },
          
           {
            "fieldname": "ire_30%", 
            "label": _("IRE 30%"), 
            "fieldtype": "Currency", 
            "width": 150
         },
        
        {
            "fieldname": "impot_a_payer", 
            "label": _("Impot a payer"), 
            "fieldtype": "Currency",
            "width": 150
        },
    ]

    return columns

def get_p10_report_data(filters):
    employee = frappe.qb.DocType("Employee")
    salary_slip = frappe.qb.DocType("Salary Slip")
    salary_detail = frappe.qb.DocType("Salary Detail")

    conditions = [ salary_slip.docstatus == 1]
    if filters.get("company"):
        conditions.append(salary_slip.company == filters.get("company"))
    if filters.get("employee"):
        conditions.append(salary_slip.employee == filters.get("employee"))
    if filters.get("from_date"):
        conditions.append(salary_slip.start_date >= filters.get("from_date"))
    if filters.get("to_date"):
        conditions.append(salary_slip.end_date <= filters.get("to_date"))

    salary_components = [
        'Salaire de base', 'Indemnité de logement', 'Indemnité de déplacement',
        'Leave Allowance', 'Heures supplementaire', 'Commissions','Base imposable', 'Impot a payer','Base IRE 0%','Base IRE 20%','Base IRE 30%', 'IRE 0%', 'IRE 20%','IRE 30%']

    query = frappe.qb.from_(salary_slip) \
        .inner_join(employee) \
        .on(employee.name == salary_slip.employee) \
        .inner_join(salary_detail) \
        .on(salary_slip.name == salary_detail.parent) \
        .select(
            employee.custom_tax_id,
            salary_slip.employee_name,
            salary_slip.posting_date,
            salary_detail.salary_component,
            Case()
            .when(salary_detail.amount.isnull(), 0)
            .else_(salary_detail.amount)
            .as_('amount')
        ).where(salary_detail.salary_component.isin(salary_components)& 
                reduce(lambda x, y: x & y, conditions)).orderby(salary_slip.employee)
    
    data = query.run(as_dict=True)
    
    employee_data = {}
    for row in data:
        employee_pin = row["custom_tax_id"]
        employee_name = row["employee_name"]
        salary_component = row["salary_component"]
        amount = row["amount"]

        if salary_component is not None and amount is not None:
            employee_key = f"{employee_pin}-{employee_name}"

            if employee_key not in employee_data:
                employee_data[employee_key] = {"employee_name": employee_name, "custom_tax_id": employee_pin}

            if salary_component is not None:
                employee_data[employee_key][salary_component.lower().replace(" ", "_")] = amount

    report_data = []
    for employee_key, components in employee_data.items():
        employee_pin, employee_name = employee_key.rsplit("-", 1)
        row = {"custom_tax_id": employee_pin, "employee_name": employee_name}
        row.update(components)
        report_data.append(row)
 
    return report_data
