
// frappe.ui.form.on('Customer', {
//     refresh: function(frm) {
        
//                 frappe.call({
//                     method: 'burundi_compliance.burundi_compliance.overrides.customer.before_save',
//                     args: {
//                         "company_tin": frm.doc.tax_id
//                     },
//                     callback: function(response) {
//                        frappe.throw("Nothing to show");
//                         if (response.message) {
//                            showInvoiceDetailsDialog(response.message.result);
//                         } else {
//                             frappe.msgprint("Failed to confirm Details");
//                         }
//                     }
//                 });
          
        
//     }
// });

// function showInvoiceDetailsDialog(result) {
//     let details = result.taxpayer[0];

//     let dialog = new frappe.ui.Dialog({
//         title: __('Company is registered'),
//         fields: [
//             {
//                 label: __('TaxPayer Name'),
//                 fieldname: 'tp_name',
//                 fieldtype: 'Data',
//                 default: details.tp_name,
//                 read_only: true
//             }
           
          
           
//         ]
//     });


//     dialog.set_primary_action(__('Close'), function() {
//         dialog.hide();
//     });

//     dialog.show();
// }
