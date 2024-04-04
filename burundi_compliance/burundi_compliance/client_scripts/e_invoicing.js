frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {
            addInvoiceButtons(frm, 'Sales Invoice');
        }
    },
});

frappe.ui.form.on('POS Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {
            addInvoiceButtons(frm, 'POS Invoice');
        }
    },
});

function addInvoiceButtons(frm, invoiceType) {
    frm.add_custom_button(__('Get Invoice'), function() {
        callBackendFunction(frm, invoiceType, 'api_classes.get_invoices.confirm_invoice');
    }, __('eBIMS Actions'));

    if (frm.doc.custom_einvoice_signatures == null) {
        frm.add_custom_button(__('Re-Submit'), function() {
          
            callBackendFunction(frm, invoiceType, 'utils.background_jobs.retry_sending_invoice');
        }, __('eBIMS Actions'));
    }
}

function callBackendFunction(frm, invoiceType, method) {
    frappe.call({
        method: `burundi_compliance.burundi_compliance.${method}`,
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
}

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
        ]
    });

    dialog.set_primary_action(__('Close'), function() {
        dialog.hide();
    });

    dialog.show();
}
