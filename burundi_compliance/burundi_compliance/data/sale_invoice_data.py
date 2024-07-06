from datetime import datetime
import frappe
from ..utils.system_tax_id import get_system_tax_id
from ..utils.format_date_and_time import date_time_format
from ..utils.invoice_signature import create_invoice_signature
from ..api_classes.base import OBRAPIBase
from bs4 import BeautifulSoup

import time as time
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data

class InvoiceDataProcessor:
    obr_base = OBRAPIBase()
    auth_details = obr_base.get_auth_details()
    
    def __init__(self, doc):
        self.doc = doc

    def prepare_invoice_data(self):
        company = frappe.get_doc("Company", self.doc.company)
        company_address = self.get_company_address_details()
        company_tax_id=company.tax_id
        tp_phone_no = company.phone_no
        tp_email = company.email
        formatted_date_data = date_time_format(self.doc)
        invoice_signature = create_invoice_signature(self.doc)
        self.doc.custom_invoice_identifier=invoice_signature
        if self.doc.is_return==0:
            self.doc.db_set('custom_invoice_identifier', invoice_signature, commit=True)
        else:
            self.doc.db_set('custom_invoice_identifier', invoice_signature, commit=True)
            
        self.confirm_tin_verified(self.doc)
        if self.doc.doctype=="POS Invoice":
            exempt_from_sales_tax=0
        else:
            exempt_from_sales_tax=self.doc.exempt_from_sales_tax
            
        invoice_data = {
            "invoice_number": self.doc.name,
            "invoice_date": formatted_date_data[0],
            "invoice_type": "FN",
            "tp_type": 1 if self.auth_details["type_of_taxpayer"]=="pour personne physique et" else 2,
            "tp_name": self.doc.company,
            "tp_TIN": company_tax_id,
            "tp_address_province": company_address.get("tp_address_province"),
            "tp_phone_number": tp_phone_no,
            "tp_address_commune": company_address.get("tp_address_commune"),
            "tp_address_avenue": company_address.get("tp_address_avenue"),
            "tp_address_quartier": company_address.get("tp_address_quartier"),
            "tp_address_rue": company_address.get("tp_address_rue"),
            "tp_address_number": company_address.get("tp_address_number"),
            "tp_trade_number": self.auth_details["the_taxpayers_commercial_register_number"],
            "tp_email": tp_email,
            "vat_taxpayer": 0 if self.auth_details["subject_to_vat"]=="pour un non assujetti ou" else 1,
            "ct_taxpayer": 0 if self.auth_details["subject_to_consumption_tax"]=="pour un non assujetti ou" else 1,
            "tl_taxpayer": 0 if self.auth_details["subject_to_flatrate_withholding_tax"]=="pour un non assujetti ou" else 1,
            "tp_fiscal_center": self.auth_details["the_taxpayers_tax_center"],
            "tp_activity_sector": self.auth_details["tp_activity_sector"],
            "tp_legal_form": self.auth_details["tp_legal_form"],
            "payment_type": self.get_payment_method(self.doc),
            "invoice_currency": frappe.defaults.get_user_default("currency"),
            "customer_name": self.doc.customer_name,
            "customer_TIN": '' if self.doc.tax_id is None else self.doc.tax_id,
            "customer_address": self.doc.customer_address,
            "vat_customer_payer": exempt_from_sales_tax,
            "invoice_ref":'',
            "cn_motif":'',
            "invoice_identifier": invoice_signature,
            "invoice_items": self.get_invoice_items()
        }
        return invoice_data
    

    def prepare_credit_note_data(self, invoice_data):
        
        reason_for_cancel = self.doc.custom_reason_for_creditcancel
        if not reason_for_cancel:
            frappe.throw("Reason for creating note is mandatory. Kindly fill it.")
        # Use BeautifulSoup to parse HTML and extract plain text
        soup = BeautifulSoup(reason_for_cancel, 'html.parser')
        reason_for_cancel = soup.get_text()
        invoice_data.update({
            "invoice_type": "FA",
            "cn_motif": reason_for_cancel,
            "invoice_ref": self.doc.return_against,
        })

        return invoice_data

    def prepare_reimbursement_deposit_data(self, invoice_data):
        invoice_data.update({
            "invoice_type": "RC",
        })

        return invoice_data


    def get_invoice_items(self):
        items = []
        itemised_tax_data=get_itemised_tax_breakup_data(self.doc)
        # frappe.throw(f"Itemised tax data: {itemised_tax_data}")

        for item in self.doc.items:
            
            tax_data = next((data for data in itemised_tax_data if data['item'] == item.item_code), None)

            
            if tax_data:
                # Check if VAT exists, if not, check for other tax details
                if 'VAT' in tax_data:
                    total_vat = tax_data['VAT']['tax_amount']
                else:
                 
                    total_vat = 0
            else:
                total_vat = 0
            item_designation=item.item_code +"-" + item.batch_no if item.batch_no else item.item_code
            items.append({
                "item_code": item.item_code,
                "item_designation": item_designation,
                "item_quantity": abs(item.qty),
                "item_price": item.rate,
                "item_total_amount": item.amount,
                "vat": abs(int(total_vat)),
                "item_ct": "0",
                "item_tl": "0",
                "item_price_nvat": abs(int(item.amount)),
                "item_price_wvat": abs(int(item.amount + total_vat))
            })
        return items

    def get_sales_data_for_stock_update(self, method=None):
        formatted_date_data = date_time_format(self.doc)
        formatted_date = formatted_date_data[0]

        sale_return_items_list = []
        sales_return_items = self.doc.items
        for item in sales_return_items:

            item_doc = frappe.get_doc("Item", item.item_code)
            item_uom = item_doc.stock_uom if item_doc else None
            check_br_permission=item_doc.custom_allow_obr_to_track_stock_movement
            if not check_br_permission:
                continue
            item_movement_type = "SN"
            if self.doc.is_return==1:
                item_movement_type = "ER"
                
            item_designation = item.item_code + " - " + item.batch_no if item.batch_no else item.item_code
            data = {
                "system_or_device_id": get_system_tax_id(),
                "item_code": item.item_code,
                "item_designation": item_designation,
                "item_quantity": item.qty,
                "item_measurement_unit": item_uom,
                "item_purchase_or_sale_price": item.rate, 
                "item_purchase_or_sale_currency": self.doc.currency,
                "item_movement_type": item_movement_type,
                "item_movement_invoice_ref": self.doc.name,
                "item_movement_description": '',
                "item_movement_date": formatted_date
            }
            
            sale_return_items_list.append(data)
        return sale_return_items_list
    

    def get_payment_method(self, doc):
        payment_type = self.doc.custom_payment_types
        if payment_type=="Bank":
            return "2"
        elif payment_type=="Cash":
            return "1"
        elif payment_type=="Credit":
            return "3"
        else:
            return "4"
        
    def confirm_tin_verified(self, doc):
        customer = frappe.get_doc("Customer", doc.customer)

        if customer.custom_gst_category=="Registered":
            if not customer.custom_tin_verified:
                frappe.throw(f"Kindly go and verify the Tin number of this customer on <b>customer</b> doctype")

    def get_company_address_details(self):
        address_details = {}
        links = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': self.doc.company, 'parenttype': 'Address'}, fields=['parent'])
        if links:
            address = frappe.get_doc("Address", links[0].parent)
            address_details = {
                "tp_address_province": address.state,
                "tp_address_commune": address.custom_commune,
                "tp_address_quartier": address.custom_quartier,
                "tp_address_avenue": address.custom_avenue,
                "tp_address_rue": address.custom_rue,
                "tp_address_number": address.custom_numéro
            }
        return address_details
    
