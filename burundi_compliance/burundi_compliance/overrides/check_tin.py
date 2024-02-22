from ..api_classes.check_tin import TinVerifier
import frappe
from ..api_classes.base import OBRAPIBase

@frappe.whitelist(allow_guest=True)
def before_save(doc, method=None):
    if doc.tax_id is not None:
        obr_integration_base = OBRAPIBase()
        token = obr_integration_base.authenticate()
        
        tin_verifier = TinVerifier(token)
        customer_tin = doc.tax_id
        data = {"tp_TIN": f"{customer_tin}"}
        results = tin_verifier.check_tin(data)
        
        #frappe.msgprint(str(results))
        
        if results.get("success", False) is False:
            frappe.throw("NIF du contribuable inconnu.")
        else:
            frappe.response["message"] = results["result"]
            frappe.msgprint(f"NIF du contribuable connu.\n{results['result']}")
        

        
    