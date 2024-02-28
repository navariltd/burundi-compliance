
import frappe

def get_maximum_attempts():
    doc=frappe.get_doc("eBIMS Setting", frappe.defaults.get_user_default("Company"))
    permissions={
    # "allow_obr_to_track_purchase_receipts":doc.allow_obr_to_track_purchase_receipts,
    # "allow_obr_to_track_all_stock_reconciliation":doc.allow_obr_to_track_all_stock_reconciliation,
    # "material_issue":doc.material_issue,
    # "material_transfer":doc.material_transfer,
    # "repack":doc.repack,
    # "material_transfer_for_manufacture":doc.material_transfer_for_manufacture,
    # "material_consumption_for_manufacture":doc.material_consumption_for_manufacture,
    # "allow_obr_to_track_all_stock_entries":doc.allow_obr_to_track_all_stock_entries,
    "custom_maximum_attempts":doc.custom_maximum_attempts,
    "custom_retry_delay_seconds":doc.custom_retry_delay_seconds,
        
    }
    
    return permissions
    
    
    