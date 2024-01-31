from ..api_classes.add_invoices import OBRInvoicePoster
from ..api_classes.base import OBRIntegrationBase

import frappe


from frappe import _
from frappe.model.document import Document


def prepare_invoice_data(doc):
    invoice_data= {
         "invoice_number": doc.name,
        "invoice_date": doc.posting_date,
        "invoice_type": "FN",
        "tp_type": "2",#check on this
        "tp_name": doc.company,#check on this
        "tp_tin": "1000000000001",#check on this
        "tp_address": doc.company_address_name,
        "tp_phone_number": doc.company_phone,
        "tp_address_commune": doc.company_address,
        "tp_address_quartier": doc.company_address,#check on this
        "tp_trade_number": "3333",#check on this
        "tp_email": doc.company_email,
        "tp_bank_account": "123456789",#check on this
        "vat_taxpayer": "1",#check on this
        "ct_taxpayer": "0",#check on this
        "tl_taxpayer": "0",#check on this
        "tp_fiscal_year": frappe.defaults.get_user_default("fiscal_year"),#check on this
        "tp_fiscal_center": "DGC",#check on this
        "tp_activity_sector": "SERVICE MARCHAND",#check on this
        "tp_legal_form": "surp",#check on this
        "payment_type": "1",#check on this
        "invoice_currency":frappe.defaults.get_user_default("currency"),#check on this
        
        "customer_name": doc.customer_name,
        "customer_TIN": doc.customer.tax_id,
        "customer_address": doc.customer_address,
        "vat_customer_payer": "1",#check on this
        "invoice_signature":"1000000000001/ws100000000000100000/20211206073022/0001/2021",#check on this
        "invoice_signature_date": "2021-12-06 07:30:22",#check on this
        "invoice_items": get_invoice_items(doc)
    }
    
    return invoice_data
    
def get_invoice_items(doc):
    items = []
    for item in doc.items:
        items.append({
            "item_code": item.item_code,
            "item_description": item.item_description,
            "item_quantity": item.qty,
            "item_price": item.rate,
            "item_total_amount": item.amount,
            "vat": item.tax_amount,
            "item_ct": item.ct,
            "item_tl": item.tl,
            "item_price_nvat": item.price_nvat,
            "item_price_wvat": item.price_wvat,
        })
    return items

def on_submit(doc, method=None):
    obr_integration_base = OBRIntegrationBase()
    token = obr_integration_base.authenticate()

    obr_invoice_poster = OBRInvoicePoster(token)  # Implement get_obr_token() to obtain the OBR token
    invoice_data = prepare_invoice_data(doc)
    result = obr_invoice_poster.post_invoice(invoice_data)
    
    frappe.msgprint(f"Invoice data sent to OBR. Result: {result}")
    
def on_cancel(doc, method=None):
    frappe.msgprint("Invoice cancelled")
    
def on_load(doc):
    frappe.msgprint("Invoice loaded")
