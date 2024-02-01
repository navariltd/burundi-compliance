
import frappe 
from ..api_classes.base import OBRAPIBase

obr_base=OBRAPIBase()
obr_base.get_auth_details()
auth_details=obr_base.get_auth_details()

def prepare_invoice_data(doc):
    invoice_data= {
         "invoice_number": doc.name,
        "invoice_date": doc.posting_date,
        "invoice_type": "FN",
        "tp_type": "2",#check on this
        "tp_name": doc.company,#check on this
        "tp_tin": "1000000000001",#check on this
        "tp_address": doc.company_address,
        "tp_phone_number": "0740743521",#check on this
        "tp_address_commune": doc.company_address_display,
        "tp_address_quartier": doc.company_address,#check on this
        "tp_trade_number": frappe.defaults.get_user_default("phone_no"),
        "tp_email": frappe.defaults.get_user_default("email"),#check on this
        "tp_bank_account": "123456789",#check on this
        "vat_taxpayer": "1",#check on this
        "ct_taxpayer": "0",#check on this
        "tl_taxpayer": "0",#check on this
        "tp_fiscal_year": frappe.defaults.get_user_default("fiscal_year"),#check on this
        "tp_fiscal_center": "DMC",#check on this
        "tp_activity_sector": auth_details["tp_activity_sector"],#Have a field to enter this
        "tp_legal_form": auth_details["tp_legal_form"],#cKeeps on changing, discuss with Loui.  Have a field to enter this. Automatically on 
        "payment_type": "1",#check on this
        "invoice_currency":frappe.defaults.get_user_default("currency"),#check on this
        
        "customer_name": doc.customer_name,
        "customer_TIN": "23124324",#Have sales invoice to fetch customer tin
        "customer_address": doc.customer_address,
        "vat_customer_payer": "1",
        "invoice_signature":"1000000000001/ws100000000000100000/20211206073022/0001/2021",#check on this
        "invoice_signature_date": "2021-12-06 07:30:22",#check on this
        "invoice_items": get_invoice_items(doc)
    }
    
    return invoice_data
    
import time as time
def get_invoice_items(doc):
    items = []
    for item in doc.items:
        items.append({
            "item_code": item.item_code,
            "item_designation": item.description,
            "item_quantity": item.qty,
            "item_price": item.rate,
            "item_total_amount": item.amount,
            "vat": item.item_tax_rate,
            "item_ct": "0",#Check on this for taxable and non-taxable persons, 
            "item_tl": "0",#Subject to flat-rate withholding tax Value: “0” for a non-taxable person or “1” for a taxable person
            "item_price_nvat": item.item_tax_rate, #Check on this
            "item_price_wvat": item.item_tax_rate, #Check on this
        })
    return items