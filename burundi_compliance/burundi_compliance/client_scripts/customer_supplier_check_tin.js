/*
Declare function that will be used to get the TIN of the customer or supplier
*/
function get_tin(frm){
    frm.add_custom_button(__('Confirm TIN'), function() {
    frappe.call({
        method: 'burundi_compliance.burundi_compliance.api_classes.check_tin.confirm_tin',
        args: {
            "company_tin": frm.doc.tax_id
        },
        callback: function(response) {
            if (response.message) {
                showInvoiceDetailsDialog(response.message.result, frm.doc.doctype);
            } else {
                frappe.msgprint("The TIN is not registered in the Burundi Revenue Authority system. Please verify the TIN and try again or contact the Burundi Revenue Authority for more detail");
            }
        }
    });
});

}

function showInvoiceDetailsDialog(result, doctype) {
    let details = result.taxpayer[0];

    let dialog = new frappe.ui.Dialog({
        title: __(`The ${doctype} is registered`),
        fields: [
            {
                label: __('TaxPayer Name'),
                fieldname: 'tp_name',
                fieldtype: 'Data',
                default: details.tp_name,
                read_only: true
            }
           
           
        ]
    });


    dialog.set_primary_action(__('Close'), function() {
        dialog.hide();
    });

    dialog.show();
}

frappe.ui.form.on('Customer', {
    refresh: function(frm){
        get_tin(frm)
    }})

frappe.ui.form.on('Supplier', {
   
        refresh: function(frm){
            get_tin(frm)
        }})

frappe.ui.form.on('Company', {

    refresh: function(frm){
        get_tin(frm)
    }})