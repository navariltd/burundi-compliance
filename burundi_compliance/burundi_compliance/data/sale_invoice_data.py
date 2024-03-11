from datetime import datetime
import frappe
from ..utils.system_tax_id import get_system_tax_id
from ..utils.format_date_and_time import date_time_format
from ..utils.invoice_signature import create_invoice_signature
from ..api_classes.base import OBRAPIBase
import time as time


class InvoiceDataProcessor:
    obr_base = OBRAPIBase()
    auth_details = obr_base.get_auth_details()
    
    def __init__(self, doc):
        self.doc = doc

    def prepare_invoice_data(self):
        company = frappe.get_doc("Company", self.doc.company)
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
        invoice_data = {
            "invoice_number": self.doc.name,
            "invoice_date": formatted_date_data[0],
            "invoice_type": "FN",
            "tp_type": self.auth_details["type_of_taxpayer"],
            "tp_name": self.doc.company,
            "tp_TIN": self.doc.company_tax_id,
            "tp_address_province":self.doc.company_address[:50],
            "tp_phone_number": tp_phone_no,
            "tp_address_commune": self.doc.company_address_display[:50],
            "tp_address_quartier": self.doc.company_address[:50],
            "tp_trade_number": self.auth_details["the_taxpayers_commercial_register_number"],
            "tp_email": tp_email,
            "vat_taxpayer": self.auth_details["subject_to_vat"],
            "ct_taxpayer": self.auth_details["subject_to_consumption_tax"],
            "tl_taxpayer": self.auth_details["subject_to_flatrate_withholding_tax"],
            "tp_fiscal_center": self.auth_details["the_taxpayers_tax_center"],
            "tp_activity_sector": self.auth_details["tp_activity_sector"],
            "tp_legal_form": self.auth_details["tp_legal_form"],
            "payment_type": self.get_payment_method(self.doc),
            "invoice_currency": frappe.defaults.get_user_default("currency"),
            "customer_name": self.doc.customer_name,
            "customer_TIN": '' if self.doc.tax_id is None else self.doc.tax_id,
            "customer_address": self.doc.customer_address,
            "vat_customer_payer": self.doc.exempt_from_sales_tax,
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

    def calculate_item_vat(self, item):
        total_tax_amount = 0.0
        if self.doc.taxes_and_charges:
            for taxes in self.doc.taxes:
                tax_percentage = taxes.rate
                total_tax_amount += tax_percentage / 100 * item.qty * item.rate

        return total_tax_amount

    def get_invoice_items(self):
        items = []

        for item in self.doc.items:
            
            total_vat = self.calculate_item_vat(item)

            items.append({
                "item_designation": item.item_code,
                "item_quantity": abs(item.qty),
                "item_price": item.rate,
                "item_total_amount": item.amount,
                "vat": abs(total_vat),
                "item_ct": "0",
                "item_tl": "0",
                "item_price_nvat": abs(item.amount),
                "item_price_wvat": abs(item.amount + total_vat)
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
            # Set item movement type to "ER" for credit notes
                item_movement_type = "ER"
            data = {
                "system_or_device_id": get_system_tax_id(),
                "item_code": item.item_code,
                "item_designation": item.item_name,
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
