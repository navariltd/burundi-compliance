import frappe
from .format_date_and_time import date_time_format
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME

from frappe import _


def get_stock_ledger_data(doc):
	"""
	Prepare data from stock ledger entry for further processing
	"""
	voucher_type = doc.voucher_type
	voucher_no = doc.voucher_no
	item_code = doc.item_code
	mov_doc = frappe.get_doc(voucher_type, voucher_no)

	valuation_rate = get_valuation_rate(voucher_type, mov_doc, item_code)

	if voucher_type == "Stock Reconciliation":
		mov_type, qty_diff, mov_desc = get_voucher_doc_details(doc)
	else:
		mov_type, mov_desc = get_voucher_doc_details(doc)

	date = date_time_format(doc)
	formatted_date = date[0]

	item_mov_inv_ref = get_invoice_reference_number(doc)

	item_designation = create_item_designation(mov_doc, item_code)

	system_tax_id = get_system_tax_id(doc)

	data = {
		"system_or_device_id": system_tax_id,
		"item_code": doc.item_code,
		"item_designation": item_designation,
		"item_quantity": (
			abs(float(qty_diff))
			if voucher_type == "Stock Reconciliation"
			else abs(float(doc.actual_qty))
		),
		"item_measurement_unit": doc.stock_uom,
		"item_cost_price": abs(float(valuation_rate)),
		"item_cost_price_currency": frappe.get_value(
			"Company", doc.company, "default_currency"
		),
		"item_movement_type": mov_type,
		"item_movement_invoice_ref": item_mov_inv_ref,
		"item_movement_description": mov_desc,
		"item_movement_date": formatted_date,
	}

	return data


def get_valuation_rate(voucher_type, doc, item_code):
	"""
	Get the valuation rate for the item for Stock Reconciliation,
	Purchase Receipt, Delivery Note, Sales Invoice, Purchase Invoice
	"""
	for item in doc.items:
		if item.item_code == item_code:
			if voucher_type == "Stock Entry" or voucher_type == "Stock Reconciliation":
				return item.valuation_rate
			else:
				return item.rate


def get_voucher_doc_details(doc):
	"""
	Get the movement type, quantity difference and movement description for Stock Reconciliation
	"""
	match doc.voucher_type:
		case "Stock Entry":
			voucher_doc = frappe.get_doc("Stock Entry", doc.voucher_no)
			mov_type = get_stock_movement_type_for_stock_entry(doc, voucher_doc)
			mov_desc = get_stock_movement_description(voucher_doc)
			return mov_type, mov_desc

		case "Purchase Receipt":
			voucher_doc = frappe.get_doc("Purchase Receipt", doc.voucher_no)
			mov_type = get_item_movement_for_purchase_receipt_and_invoice_on_submit_and_cancel(
				doc, voucher_doc
			)

			mov_desc = get_stock_movement_description(voucher_doc)

			return mov_type, mov_desc

		case "Delivery Note":
			voucher_doc = frappe.get_doc("Delivery Note", doc.voucher_no)
			(
				mov_type,
				mov_desc,
			) = get_item_movement_for_delivery_note_and_sale_invoice_on_submit_and_cancel(
				doc, voucher_doc
			)
			return mov_type, mov_desc

		case "Sales Invoice":
			voucher_doc = frappe.get_doc("Sales Invoice", doc.voucher_no)
			(
				mov_type,
				mov_desc,
			) = get_item_movement_for_delivery_note_and_sale_invoice_on_submit_and_cancel(
				doc, voucher_doc
			)
			return mov_type, mov_desc

		case "Purchase Invoice":
			voucher_doc = frappe.get_doc("Purchase Invoice", doc.voucher_no)
			mov_type = get_item_movement_for_purchase_receipt_and_invoice_on_submit_and_cancel(
				doc, voucher_doc
			)
			mov_desc = get_stock_movement_description(voucher_doc)
			return mov_type, mov_desc

		case "Stock Reconciliation":
			voucher_doc = frappe.get_doc("Stock Reconciliation", doc.voucher_no)
			mov_type, qty_diff = get_stock_recon_movement_type(doc, voucher_doc)
			mov_desc = get_stock_movement_description(voucher_doc)
			return mov_type, qty_diff, mov_desc

		case "Asset Capitalization":
			voucher_doc = frappe.get_doc("Asset Capitalization", doc.voucher_no)
			mov_type = get_item_movement_asset_capitalisation_on_submit_and_cancel(
				doc, voucher_doc
			)
			mov_desc = get_stock_movement_description(voucher_doc)
			return mov_type, mov_desc

		case "Asset Repair":
			voucher_doc = frappe.get_doc("Asset Repair", doc.voucher_no)
			mov_type = get_item_movement_asset_capitalisation_on_submit_and_cancel(
				doc, voucher_doc
			)
			mov_desc = get_stock_movement_description(voucher_doc)
			return mov_type, mov_desc

		case _:
			return None


def get_stock_movement_type_for_stock_entry(doc, voucher_doc):
	"""
	Get the stock movement type based on stock entry type and custom movement type
	"""
	entry_type = voucher_doc.stock_entry_type
	custom_mov_type = voucher_doc.custom_stock_movement_type

	if (doc.actual_qty > 0 and entry_type in ["Material Receipt", "Manufacture"]) or (
		doc.actual_qty < 0
		and entry_type
		in [
			"Material Issue",
			"Material Consumption for Manufacture",
			"Material Transfer for Manufacture",
			"Send to Subcontractor",
		]
	):
		return get_stock_movement_on_submit(entry_type, custom_mov_type, voucher_doc)

	elif (
		doc.actual_qty < 0
		and entry_type in ["Material Receipt", "Manufacture"]
		or doc.actual_qty > 0
		and entry_type
		in [
			"Material Issue",
			"Material Consumption for Manufacture",
			"Material Transfer for Manufacture",
			"Send to Subcontractor",
		]
	):
		return get_stock_movement_on_cancel(entry_type)

	elif entry_type == "Repack":
		return get_item_movement_for_repack_on_submit_and_cancel(doc, voucher_doc)


def get_stock_movement_on_submit(entry_type, mov_type, voucher_doc):
	if entry_type == "Material Receipt" and voucher_doc.is_opening == "Yes":
		return "EI"
	elif entry_type == "Material Receipt" and voucher_doc.is_opening == "No":
		return "EAU"
	elif entry_type == "Material Issue":
		if mov_type == "Theft exits(SV)":
			return "SV"
		elif mov_type == "Obsolete/expired or obsolete issues(SD)":
			return "SD"
		elif mov_type == "Breakage Exits(SC)":
			return "SC"
		elif mov_type == "Loss Outflows(SP)":
			return "SP"
		else:
			return "ST"
	elif entry_type == "Manufacture":
		return "EN"
	elif entry_type in [
		"Material Consumption for Manufacture",
		"Material Transfer for Manufacture",
		"Send to Subcontractor",
	]:
		return "SAU"
	else:
		return "EAU"


def get_stock_movement_on_cancel(entry_type):
	if entry_type == "Material Receipt":
		return "SAU"
	elif entry_type == "Material Issue":
		return "EAU"
	elif entry_type == "Manufacture":
		return "SAU"
	elif entry_type in [
		"Repack",
		"Material Consumption for Manufacture",
		"Material Transfer for Manufacture",
		"Send to Subcontractor",
	]:
		return "ER"
	else:
		return "EAU"


def get_item_movement_for_repack_on_submit_and_cancel(doc, voucher_doc):
	"""
	Get the movement type for repack
	"""

	# get the item_code from stock ledger entry
	item_code = doc.item_code

	for item in voucher_doc.items:
		if item.item_code == item_code:
			if doc.actual_qty > 0.0:
				return "EAU"
			else:
				return "SAU"


def get_stock_movement_description(voucher_doc):
	stock_movement_description = (
		voucher_doc.custom_stock_movement_description
		if voucher_doc.custom_stock_movement_description
		else ""
	)
	return stock_movement_description


def get_item_movement_for_purchase_receipt_and_invoice_on_submit_and_cancel(
	doc, voucher_doc
):
	"""
	Get the movement type for purchase receipt
	"""
	movement_type = "EN"
	item_code = doc.item_code

	for item in voucher_doc.items:
		if item.item_code == item_code:
			if doc.actual_qty > 0.0:
				return movement_type
			else:
				movement_type = "SAU"
				return movement_type


def get_item_movement_for_delivery_note_and_sale_invoice_on_submit_and_cancel(
	doc, voucher_doc
):
	"""
	Get the movement type for delivery note and sales invoice
	"""
	movement_description = _("Normal Sale of Goods")
	movement_type = "SN"
	item_code = doc.item_code

	for item in voucher_doc.items:
		if item.item_code == item_code:
			if doc.actual_qty < 0.0:
				return movement_type, movement_description
			else:
				movement_description = _("Normal Return of goods")
				movement_type = "ER"
				return movement_type, movement_description


def get_stock_recon_movement_type(doc, voucher_doc):
	"""
	Get the movement type for stock reconciliation
	"""
	has_batch = check_if_item_has_batches(doc.item_code)
	warehouse = doc.warehouse
	if voucher_doc.purpose == "Opening Stock":
		for item in voucher_doc.items:
			if item.item_code == doc.item_code and item.warehouse == warehouse:
				quantity_difference = item.quantity_difference
		if voucher_doc.is_cancelled == 0:
			movement_type = "EI"  # Opening Stock
		else:
			movement_type = "SAU"

	elif voucher_doc.purpose == "Stock Reconciliation":
		for item in voucher_doc.items:
			item_batch = None
			if has_batch:
				item_batch = get_specified_batch(doc)

			# Check if item matches the criteria
			if (
				item.item_code == doc.item_code
				and item.warehouse == warehouse
				and (not has_batch or item.batch_no == item_batch)
			):
				quantity_difference = item.quantity_difference
				is_cancelled = doc.is_cancelled

				if is_cancelled == 0:
					if float(quantity_difference) > 0.0:
						movement_type = "EAJ"
					elif float(quantity_difference) < 0.0:
						movement_type = "SAJ"
				elif is_cancelled == 1:
					if float(quantity_difference) > 0.0:
						movement_type = "SAJ"
					elif float(quantity_difference) < 0.0:
						movement_type = "EAJ"
				else:
					movement_type = "SAU"

	return movement_type, quantity_difference


def get_invoice_reference_number(doc):
	item_invoice_ref = ""
	if doc.voucher_type == "Purchase Invoice":
		purchase_doc = frappe.get_doc("Purchase Invoice", doc.voucher_no)
		item_invoice_ref = purchase_doc.bill_no
	elif doc.voucher_type == "Sales Invoice":
		sales_doc = frappe.get_doc("Sales Invoice", doc.voucher_no)
		item_invoice_ref = sales_doc.name
	return item_invoice_ref


def create_item_designation(specified_doc, item_code):
	items = specified_doc.items
	for item in items:
		if item.item_code == item_code:
			if item.batch_no:
				return item.item_code + " - " + item.batch_no
			else:
				return item.item_code


def get_specified_batch(specified_doc):
	# Get the serial and batch bundle linked to the specified document
	serial_and_batch = specified_doc.serial_and_batch_bundle

	# Fetch the Serial and Batch Bundle document
	serial_and_batch_doc = frappe.get_doc("Serial and Batch Bundle", serial_and_batch)

	# Get the list of entries (batches) from the Serial and Batch Bundle document
	batches = serial_and_batch_doc.entries

	# Pick the first entry's batch number
	if batches:
		first_batch_no = batches[0].batch_no
		return first_batch_no
	else:
		frappe.throw("No batches found in the specified Serial and Batch Bundle.")


def check_if_item_has_batches(item_code):
	"""
	Check if the item has batches
	"""
	item_doc = frappe.get_doc("Item", item_code)
	return item_doc.has_batch_no


def get_item_movement_asset_capitalisation_on_submit_and_cancel(doc, voucher_doc):
	"""
	Get the movement type for asset capitalisation
	"""
	movement_type = "EN"
	# movement_description="Asset Capitalization"
	item_code = doc.item_code

	for item in voucher_doc.items:
		if item.item_code == item_code:
			if doc.actual_qty > 0.0:
				return movement_type
			else:
				# movement_description="Asset De-capitalization"
				movement_type = "SAU"
				return movement_type


def get_system_tax_id(doc):
	settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, doc.company)
	return settings_doc.system_identification_given_by_obr
