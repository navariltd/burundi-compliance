// Copyright (c) 2025, Navari Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Custom Income Statement Balance Sheet Report"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      reqd: 1,
    },
    {
      fieldname: "fiscal_year",
      label: __("Fiscal Year"),
      fieldtype: "Link",
      options: "Fiscal Year",
      reqd: 1,
    },
  ],
};
