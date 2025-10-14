# Copyright (c) 2025, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum


gl = DocType("GL Entry")
a = DocType("Account")


def execute(filters=None):
    columns = get_columns(filters or {})
    data = get_data(filters or {})
    return columns, data


def get_data(filters):
    """
    Fetch production exercise accounts and return rows matching the report columns.
    Appends summary rows and computed metrics.
    """
    filters = filters or {}
    fiscal_year = filters.get("fiscal_year")

    rows = []

    production_exercise_accounts = get_accounts_by_group("Exercise Production", filters)
    pe_total = 0.0
    for acc in production_exercise_accounts:
        balance = float(acc.get("balance") or 0.0)
        pe_total += balance
        rows.append(
            {
                "account_name": acc.get("account_name"),
                "fiscal_year": fiscal_year,
                "amount": balance,
            }
        )

    # Exercise Production Summation row
    rows.append(
        {
            "account_name": "Exercise Production",
            "fiscal_year": filters.get("fiscal_year"),
            "amount": pe_total,
        }
    )

    consumption_exercise_accounts = get_accounts_by_group(
        "Exercise Consumption", filters
    )
    ce_total = 0.0
    for acc in consumption_exercise_accounts:
        balance = float(acc.get("balance") or 0.0)
        ce_total += balance
        rows.append(
            {
                "account_name": acc.get("account_name"),
                "fiscal_year": fiscal_year,
                "amount": balance,
            }
        )
    # Consumption Production Summation row
    rows.append(
        {
            "account_name": "Exercise Consumption",
            "fiscal_year": filters.get("fiscal_year"),
            "amount": ce_total,
        }
    )

    # Added Operation value calculation
    rows.append(
        {
            "account_name": "Added Operation Value",
            "fiscal_year": filters.get("fiscal_year"),
            "amount": pe_total - ce_total,
        }
    )

    gross_operation_surplus_accounts = get_accounts_by_group(
        "Gross Operation Surplus", filters
    )
    gos_total = 0.0
    for acc in gross_operation_surplus_accounts:
        balance = float(acc.get("balance") or 0.0)
        gos_total += balance
        rows.append(
            {
                "account_name": acc.get("account_name"),
                "fiscal_year": fiscal_year,
                "amount": balance,
            }
        )
    # Gross Operation Surplus Summation row
    rows.append(
        {
            "account_name": "Gross Operation Surplus",
            "fiscal_year": filters.get("fiscal_year"),
            "amount": ce_total - gos_total,
        }
    )

    operation_result_additions_accounts = get_accounts_by_group(
        "Operating Result (Additions)", filters
    )
    or_additions_total = 0.0
    for acc in operation_result_additions_accounts:
        balance = float(acc.get("balance") or 0.0)
        or_additions_total += balance
        rows.append(
            {
                "account_name": acc.get("account_name"),
                "fiscal_year": fiscal_year,
                "amount": balance,
            }
        )

    operation_result_deductions_accounts = get_accounts_by_group(
        "Operating Result (Deductions)", filters
    )
    or_deductions_total = 0.0
    for acc in operation_result_deductions_accounts:
        balance = float(acc.get("balance") or 0.0)
        or_deductions_total += balance
        rows.append(
            {
                "account_name": acc.get("account_name"),
                "fiscal_year": fiscal_year,
                "amount": balance,
            }
        )

    operation_result_summation = or_additions_total - or_deductions_total

    # Operating Result Summation row
    rows.append(
        {
            "account_name": "Operating Result",
            "fiscal_year": filters.get("fiscal_year"),
            "amount": operation_result_summation,
        }
    )
    
    # Ordinary Result Before Tax row
    ordinary_result_before_tax_accounts = get_accounts_by_group(
        "Ordinary Result Before Tax", filters
    )
    ordinary_result_before_tax_total = 0.0
    for acc in ordinary_result_before_tax_accounts:
        balance = float(acc.get("balance") or 0.0)
        ordinary_result_before_tax_total += balance
        rows.append(
            {
                "account_name": acc.get("account_name"),
                "fiscal_year": fiscal_year,
                "amount": balance,
            }
        )

    # Ordinary Result Before Tax Summation row
    rows.append(
        {
            "account_name": "Ordinary Result Before Tax",
            "fiscal_year": filters.get("fiscal_year"),
            "amount": operation_result_summation - ordinary_result_before_tax_total,
        }
    )
    
    net_year_result_accounts = get_accounts_by_group(
        "Net Year Result", filters
    )
    net_year_result_account_summation_total = 0.0
    for acc in net_year_result_accounts:
        balance = float(acc.get("balance") or 0.0)
        net_year_result_account_summation_total += balance
        rows.append(
            {
                "account_name": acc.get("account_name"),
                "fiscal_year": fiscal_year,
                "amount": balance,
            }
        )
    
    # Net Year Result Summation row
    rows.append(
        {
            "account_name": "Net Year Result",
            "fiscal_year": filters.get("fiscal_year"),
            "amount": operation_result_summation - ordinary_result_before_tax_total - net_year_result_account_summation_total,
        }
    )

    return rows


def get_columns(filters):
    columns = [
        {
            "label": "Account Name",
            "fieldname": "account_name",
            "fieldtype": "Link",
            "options": "Account",
            "width": 200,
        },
        {
            "label": "Year",
            "fieldname": "fiscal_year",
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "width": 150,
        },
        {
            "label": "Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]

    return columns


# Replace repeated functions with this single helper
def get_accounts_by_group(income_statement_account_group, filters=None):
    """
    Generic function to fetch accounts for a given income_statement_account_group.
    Returns list of dicts with keys: account_name, account_number, balance, fiscal_year
    """
    filters = filters or {}
    company = filters.get("company")
    fiscal_year = filters.get("fiscal_year")

    # Build base query
    q = (
        frappe.qb.from_(gl)
        .join(a)
        .on(gl.account == a.name)
        .select(
            a.name.as_("account_name"),
            a.account_number,
            Sum(gl.debit - gl.credit).as_("balance"),
            gl.fiscal_year,
        )
        .where(a.income_statement_account_group == income_statement_account_group)
        .where(a.disabled == 0)
    )

    if fiscal_year:
        q = q.where(gl.fiscal_year == fiscal_year)
    if company:
        q = q.where(gl.company == company)

    q = q.groupby(a.name, a.account_number, gl.fiscal_year).orderby(a.name)

    # Execute and return dict results; coerce balance to float
    results = q.run(as_dict=True)
    for r in results:
        r["balance"] = float(r.get("balance") or 0.0)
    return results
