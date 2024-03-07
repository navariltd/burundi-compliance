# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt
import frappe, erpnext


def execute(filters=None):
	
	columns = get_columns()
	data = get_data(filters)
	get_child_results()
	return columns, data


def get_columns():
	columns=[
		{
			"label": "Preparation Sheet",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Preparation Sheet",
			"width": 250
		},
		{
			"label": "Dispatch",
			"fieldname": "reference_dispatch",
			"fieldtype": "Link",
			"options": "Dispatch",
			"width": 250
		},
  {
	  		"label":"Date",
			"fieldname":"date",
			"fieldtype":"Date",
			"width": 250
  },
  
		{
			"label": "View Results",
			"fieldname": "view_results",
			"fieldtype": "Button",
			"width": 150,
			"click": "erpnext.show_results"  # Replace with the actual function to handle button click
		},
]
	
	return columns
	

def get_data(filters):
	if filters.from_date > filters.to_date:
		frappe.throw(_("To Date cannot be before From Date. {}").format(filters.to_date))
  
	dispatch=frappe.qb.DocType("Dispatch")
	prep_sheet=frappe.qb.DocType("Preparation Sheet")
 
	query=frappe.qb.from_(prep_sheet)\
	 .inner_join(dispatch)\
		 .on(prep_sheet.reference_dispatch==dispatch.name)\
			 .select(prep_sheet.name,prep_sheet.reference_dispatch, prep_sheet.date, prep_sheet.docstatus)
  
	query = get_conditions(query, filters, prep_sheet)
	data=query.run(as_dict=True)
 
	# Add a "View Results" button for each row
	for row in data:
		row['view_results'] = 'View Results'
 
	return data

def get_conditions(query, filters, prep_sheet):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	
	for filter_key, filter_value in filters.items():
		if filter_key == "from_date":
			query = query.where(prep_sheet.date >= filter_value)
		elif filter_key == "to_date":
			query = query.where(prep_sheet.date <= filter_value)
		elif filter_key=="preparation_sheet":
			query=query.where(prep_sheet.name==filter_value)
		elif filter_key=="dispatch":
			query = query.where(prep_sheet.reference_dispatch == filter_value)
		
		elif filter_key == "docstatus":
			query = query.where(prep_sheet.docstatus == doc_status.get(filter_value, 0))
	return query


def get_child_results():
	sheet_item=frappe.qb.DocType("Sheet Item")
	prep_sheet=frappe.qb.DocType("Preparation Sheet")
	
	query=frappe.qb.from_(sheet_item)\
			 .inner_join(prep_sheet)\
		 .on(sheet_item.parent==prep_sheet.name)\
			 .select(sheet_item.aas_reading_auppm, sheet_item.aas_reading_cuppm)
	
	data=query.run(as_dict=True)
	frappe.throw(str(data))
	return data