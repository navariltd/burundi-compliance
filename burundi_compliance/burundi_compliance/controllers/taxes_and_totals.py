from frappe.utils import flt
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals


def calculate_item_values(self):

    for item in self.doc.get("items"):
        self.doc.round_floats_in(item)

        # Updated logic for custom item
        if item.item_code == "Or (Gold)":
            
            if item.doctype in [
                
                "Sales Order Item",
                
            ]:
                custom_fixing_de_londre = item.custom_fixing_de_londres_par_gr_en_usd
                item_qty = item.qty
                custom_teneur_ = item.custom_teneur
                custom_fixing_de_londres_par_once = item.custom_fixing_de_londres_par_once

                new_custom_teneur_ = custom_teneur_ / 100
                denominator = new_custom_teneur_ * custom_fixing_de_londre
                accumulated_value = denominator / custom_fixing_de_londres_par_once

                # Set the accumulated value for the current item
                item.custom_prix_par_gr_dor_fondu_a_gr_en_usd = accumulated_value

                # Calculate the rate for the current item
                custom_cours_moyen_du_jour_ = item.custom_cours_moyen_du_jour_
                new_rate = custom_cours_moyen_du_jour_ * accumulated_value

                # Update the rate field for the current item
                item.rate=new_rate
                # Calculate and update the amount for the current item
                item.amount = flt(new_rate * item_qty, item.precision("amount"))


        item.net_amount = item.amount

        self._set_in_company_currency(
            item, ["price_list_rate", "rate", "net_rate", "amount", "net_amount"]
        )

        item.item_tax_amount = 0.0

def calculate_item_values_override():
    calculate_taxes_and_totals.calculate_item_values = calculate_item_values
