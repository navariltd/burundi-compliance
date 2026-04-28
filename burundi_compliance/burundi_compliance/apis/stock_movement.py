import frappe


from ..background_tasks.stock_movement import send_stock_movement_to_obr


@frappe.whitelist()
def trigger_stock_movement_to_obr() -> None:
	send_stock_movement_to_obr()
