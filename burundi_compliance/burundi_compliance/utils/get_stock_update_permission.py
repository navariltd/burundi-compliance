
import frappe

def get_stock_update_permissions():
    doc=frappe.get_doc("EBIMS Settings")
    permissions={
    "allow_obr_to_track_purchase_receipts":doc.allow_obr_to_track_purchase_receipts,
    "allow_obr_to_track_all_stock_reconciliation":doc.allow_obr_to_track_all_stock_reconciliation,
    "material_issue":doc.material_issue,
    "material_transfer":doc.material_transfer,
    "repack":doc.repack,
    "material_transfer_for_manufacture":doc.material_transfer_for_manufacture,
    "material_consumption_for_manufacture":doc.material_consumption_for_manufacture,
    "allow_obr_to_track_all_stock_entries":doc.allow_obr_to_track_all_stock_entries
        
    }
    
    return permissions
    
    
    