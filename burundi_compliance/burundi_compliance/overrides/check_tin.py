from ..api_classes.check_tin import TinVerifier
import frappe
from ..api_classes.base import OBRAPIBase

# @frappe.whitelist(allow_guest=True)
# def customer_before_save(doc, method=None):
    
#     '''Check if the customer's TIN is valid and known by the OBR.'''
#     if doc.custom_gst_category=="Registered" and doc.tax_id is None:
#         frappe.throw("Le NIF est obligatoire pour les contribuables enregistrés.")
        
#     elif doc.custom_gst_category=="Registered" and doc.tax_id is not None and doc.custom_tin_verified==0:
#         obr_integration_base = OBRAPIBase()
#         token = obr_integration_base.authenticate()
        
#         tin_verifier = TinVerifier(token)
#         customer_tin = doc.tax_id
#         data = {"tp_TIN": f"{customer_tin}"}
#         results = tin_verifier.check_tin(data)
                
#         if results.get("success", False) is False:
#             frappe.throw("NIF du contribuable inconnu.")
            
#         else:
#             frappe.response["message"] = results["result"]
#             doc.custom_tin_verified=1
#             frappe.msgprint(f"NIF du contribuable connu.\n{results['result']}")
            

# def supplier_before_save(doc, method=None):
    
#     '''Check if the supplier's TIN is valid and known by the OBR.'''
     
#     if doc.tax_id is not None and doc.custom_tin_verified==0:
#         obr_integration_base = OBRAPIBase()
#         token = obr_integration_base.authenticate()
        
#         tin_verifier = TinVerifier(token)
#         customer_tin = doc.tax_id
#         data = {"tp_TIN": f"{customer_tin}"}
#         results = tin_verifier.check_tin(data)
                
#         if results.get("success", False) is False:
#             frappe.throw("NIF du contribuable inconnu.")
            
#         else:
#             frappe.response["message"] = results["result"]
#             doc.custom_tin_verified=1
#             frappe.msgprint(f"NIF du contribuable connu.\n{results['result']}")
            
          
def check_and_verify_tin(doc):
    if doc.tax_id is not None and doc.custom_tin_verified == 0:
        obr_integration_base = OBRAPIBase()
        token = obr_integration_base.authenticate()

        tin_verifier = TinVerifier(token)
        customer_or_supplier_tin = doc.tax_id
        data = {"tp_TIN": f"{customer_or_supplier_tin}"}
        results = tin_verifier.check_tin(data)

        if results.get("success", False) is False:
            frappe.throw("NIF du contribuable inconnu.")
        else:
            frappe.response["message"] = results["result"]
            doc.custom_tin_verified = 1
            frappe.msgprint(f"NIF du contribuable connu.\n{results['result']}")
            
@frappe.whitelist(allow_guest=True)
def customer_before_save(doc, method=None):
    '''Check and verify the customer's TIN if applicable.'''
    if doc.custom_gst_category == "Registered" and doc.tax_id is None:
        frappe.throw("Le NIF est obligatoire pour les contribuables enregistrés.")
    elif doc.custom_gst_category == "Registered" and doc.tax_id is not None and doc.custom_tin_verified == 0:
        check_and_verify_tin(doc)

@frappe.whitelist(allow_guest=True)
def supplier_before_save(doc, method=None):
    '''Check and verify the supplier's TIN if applicable.'''
    if doc.tax_id is not None and doc.custom_tin_verified == 0:
        check_and_verify_tin(doc)