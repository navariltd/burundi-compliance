
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if(frm.doc.docstatus==1) {
            
            frm.add_custom_button(__('Get Invoice'), function() {
                
                // Call the backend function when the button is clicked
                frappe.call({
                    method: 'burundi_compliance.burundi_compliance.api_classes.get_invoices.confirm_invoice',
                    args: {
                        "invoice_identifier": frm.doc.custom_invoice_identifier
                    },
                    callback: function(response) {
                       
                        if (response.message) {
                
                            showInvoiceDetailsDialog(response.message.result);
                        } else {
                            frappe.msgprint("Failed to get invoice details");
                        }
                    }
                });
            });
        }
    }
});

function showInvoiceDetailsDialog(result) {
    let invoice = result.invoices[0];

    let dialog = new frappe.ui.Dialog({
        title: __('Invoice Retrieved successfully'),
        fields: [
            {
                label: __('Invoice Number'),
                fieldname: 'invoice_number',
                fieldtype: 'Data',
                default: invoice.invoice_number,
                read_only: true
            },
            {
                label: __('Invoice Date'),
                fieldname: 'invoice_date',
                fieldtype: 'Data',
                default: invoice.invoice_date,
                read_only: true
            },
            {
                label: __('TP Type'),
                fieldname: 'tp_type',
                fieldtype: 'Data',
                default: invoice.tp_type,
                read_only: true
            },
            {
                label: __('TP Name'),
                fieldname: 'tp_name',
                fieldtype: 'Data',
                default: invoice.tp_name,
                read_only: true
            },
            {
                label: __('TP TIN'),
                fieldname: 'tp_TIN',
                fieldtype: 'Data',
                default: invoice.tp_TIN,
                read_only: true
            },
            {
                label: __('Customer Name'),
                fieldname: 'customer_name',
                fieldtype: 'Data',
                default: invoice.customer_name,
                read_only: true
            },
            {
                label: __('Customer TIN'),
                fieldname: 'customer_TIN',
                fieldtype: 'Data',
                default: invoice.customer_TIN,
                read_only: true
            },
            // {
            //     label:_('Tp Activity Sector'),
            //     fieldname:'tp_activity_sector',
            //     fieldtype:'Data',
            //     default:invoice.tp_activity_sector,
            //     read_only:true
            // },
            
            // {
            //     label:_('Tp Trade Number'),
            //     fieldname:'tp_trade_number',
            //     fieldtype:'Data',
            //     default:invoice.tp_trade_number,
            //     read_only:true
            // }
            // ,
            // {
            //     label:_('Tp Address Quartier'),
            //     fieldname:'tp_address_quartier',
            //     fieldtype:'Data',
            //     default:invoice.tp_address_quartier,
            //     read_only:true
            // }
            // ,
            // {
            //     label:_('Tp Legal Form'),
            //     fieldname:'tp_legal_form',
            //     fieldtype:'Data',
            //     default:invoice.tp_legal_form,
            //     read_only:true
            // }
            // ,
            // {
            //     label:_('Tp Fiscal Center'),
            //     fieldname:'tp_fiscal_center',
            //     fieldtype:'Data',
            //     default:invoice.tp_fiscal_center,
            //     read_only:true
            // }
            // ,
            // {
            //     label:_('Vat Taxpayer'),
            //     fieldname:'vat_taxpayer',
            //     fieldtype:'Data',
            //     default:invoice.vat_taxpayer,
            //     read_only:true
            // }
            // ,
           
        ]
    });


    // Add a 'Close' button
    dialog.set_primary_action(__('Close'), function() {
        dialog.hide();
    });

    // Show the dialog
    dialog.show();
}
