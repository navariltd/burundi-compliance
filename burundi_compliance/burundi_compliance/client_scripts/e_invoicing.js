frappe.ui.form.on('Sales Invoice', {
  onload: function (frm) {
    if (frm.is_new()) {
      frm.set_value('custom_submitted_to_obr', 0)
      frm.set_value('custom_einvoice_signatures', '')
      frm.set_value('custom_invoice_registered_no', '')
      frm.set_value('custom_invoice_registered_date', '')
      frm.set_value('custom_invoice_identifier', '')
    }
  },
  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      addInvoiceButtons(frm, 'Sales Invoice')
    }
  },
})

frappe.ui.form.on('POS Invoice', {
  onload: function (frm) {
    if (frm.is_new()) {
      frm.set_value('custom_submitted_to_obr', 0)
      frm.set_value('custom_einvoice_signatures', '')
      frm.set_value('custom_invoice_registered_no', '')
      frm.set_value('custom_invoice_registered_date', '')
      frm.set_value('custom_invoice_identifier', '')
    }
  },

  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      addInvoiceButtons(frm, 'POS Invoice')
    }
  },
})

function addInvoiceButtons(frm, invoiceType) {
  if (frm.doc.custom_submitted_to_obr) {
    frm.add_custom_button(
      __('Get Invoice'),
      function () {
        callBackendFunction(
          frm,
          'apis.apis.get_invoice_from_obr',
          'GET',
          __('Getting Invoice...'),
          invoiceType
        )
      },
      __('eBIMS Actions')
    )
  }

  if (!frm.doc.custom_einvoice_signatures) {
    frm.add_custom_button(
      __('Re-Submit'),
      function () {
        callBackendFunction(
          frm,
          'apis.apis.resubmit_invoice_to_obr',
          'POST',
          __('Resubmitting Invoice...'),
          invoiceType
        )
      },
      __('eBIMS Actions')
    )
  }
}

// TODO: Display correct Message when an Invoice is resubmitted
function callBackendFunction(
  frm,
  method,
  action,
  freeze_message = null,
  invoiceType = null
) {
  frappe.call({
    method: `burundi_compliance.burundi_compliance.${method}`,
    args: {
      name: frm.doc.name,
      invoice_type: invoiceType,
    },
    callback: function (response) {
      if (response) {
        if (action === 'GET') {
          if (response.message) {
            showInvoiceDetailsDialog(response.message.result)
          } else {
            frappe.msgprint(__('Failed to Retrieve Invoice details'))
          }
        }

        if (action === 'POST') {
          frappe.msgprint(__('Invoice Resubmission has been Queued'))
        }
      }
    },
    freeze: true,
    freeze_message: freeze_message || __('Processing...'),
  })
}

function showInvoiceDetailsDialog(result) {
  let invoice = result.invoices[0]

  let dialog = new frappe.ui.Dialog({
    title: __('Invoice Retrieved successfully'),
    fields: [
      {
        label: __('Invoice Number'),
        fieldname: 'invoice_number',
        fieldtype: 'Data',
        default: invoice.invoice_number,
        read_only: true,
      },
      {
        label: __('Invoice Date'),
        fieldname: 'invoice_date',
        fieldtype: 'Data',
        default: invoice.invoice_date,
        read_only: true,
      },
      {
        label: __('TP Type'),
        fieldname: 'tp_type',
        fieldtype: 'Data',
        default: invoice.tp_type,
        read_only: true,
      },
      {
        label: __('TP Name'),
        fieldname: 'tp_name',
        fieldtype: 'Data',
        default: invoice.tp_name,
        read_only: true,
      },
      {
        label: __('TP TIN'),
        fieldname: 'tp_TIN',
        fieldtype: 'Data',
        default: invoice.tp_TIN,
        read_only: true,
      },
      {
        label: __('Customer Name'),
        fieldname: 'customer_name',
        fieldtype: 'Data',
        default: invoice.customer_name,
        read_only: true,
      },
      {
        label: __('Customer TIN'),
        fieldname: 'customer_TIN',
        fieldtype: 'Data',
        default: invoice.customer_TIN,
        read_only: true,
      },
    ],
  })

  dialog.set_primary_action(__('Close'), function () {
    dialog.hide()
  })

  dialog.show()
}
