frappe.provide("erpnext.public");
frappe.provide("erpnext.controllers");

erpnext.taxes_and_totals.prototype.calculate_item_values = function() {
    let me = this;
    $.each(this.frm.doc["items"] || [], function(i, item) {
        frappe.model.round_floats_in(item);
        item.net_rate = item.rate;

        // Check if the item is "Or (Gold)"
        if (item.item_code === "Or (Gold)") {
            let custom_fixing_de_londre = item.custom_fixing_de_londre;
            let item_qty = item.qty;
            let custom_teneur_ = item.custom_teneur_;
            let custom_fixing_de_londres_par_once = item.custom_fixing_de_londres_par_once;

            let new_custom_teneur_ = custom_teneur_ / 100;
            let denominator = new_custom_teneur_ * custom_fixing_de_londre;
            let accumulatedValue = denominator / custom_fixing_de_londres_par_once;

            // Set the accumulatedValue for the current item
            frappe.model.set_value(item.doctype, item.name, 'custom_prix_par_gr_dor_fondu_a_gr_en_usd', 200);

            // Calculate the rate for the current item
            let custom_cours_moyen_du_jour_ = item.custom_cours_moyen_du_jour_;
            let new_rate = custom_cours_moyen_du_jour_ * accumulatedValue;

            // Update the rate field for the current item in the child table
            frappe.model.set_value(item.doctype, item.name, 'rate', new_rate);

            // Calculate and update the amount for the current item
            item.amount = flt(new_rate * item_qty, precision("amount", item));
        }

        item.net_amount = item.amount;
        item.item_tax_amount = 0.0;
        item.total_weight = flt(item.weight_per_unit * item.stock_qty);

        me.set_in_company_currency(item, ["price_list_rate", "rate", "amount", "net_rate", "net_amount"]);
    });
}
