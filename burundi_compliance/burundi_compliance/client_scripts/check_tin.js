function get_tin(frm) {
  frm.add_custom_button(__('Confirm TIN'), async function () {
    let company
    if (frm.doc.doctype === 'Customer' || frm.doc.doctype === 'Supplier') {
      company = await new Promise((resolve) => {
        showSettingsSelectorDialog(frm, resolve)
      })
    } else {
      company = frm.doc.name
    }

    frappe.call({
      method:
        'burundi_compliance.burundi_compliance.apis.confirm_tin.confirm_tin',
      args: {
        company: company,
        tin: frm.doc.tax_id,
        doctype: frm.doc.doctype,
        docname: frm.doc.name,
      },
      callback: function (response) {
        if (response.message.success) {
          showTinDetailsDialog(response.message.result, frm.doc.doctype)
        } else {
          frappe.msgprint({
            title: __('Notification'),
            indicator: 'red',
            message: __(`${response.message.msg}`),
          })
        }
      },
      freeze: true,
      freeze_message: __('Checking TIN...'),
    })
  })
}

function showTinDetailsDialog(result, doctype) {
  let details = result.taxpayer[0]

  let dialog = new frappe.ui.Dialog({
    title: __(`The ${doctype} is registered`),
    fields: [
      {
        label: __('TaxPayer Name'),
        fieldname: 'tp_name',
        fieldtype: 'Data',
        default: details.tp_name,
        read_only: true,
      },
    ],
  })

  dialog.set_primary_action(__('Close'), function () {
    dialog.hide()
  })

  dialog.show()
}

function set_gst_category_query(frm) {
  if (
    frm.doc.customer_type === 'Company' ||
    frm.doc.supplier_type === 'Company'
  ) {
    frm.set_query('custom_gst_category', function () {
      return {
        filters: {
          name: ['!=', 'Unregistered'],
        },
      }
    })
  } else {
    frm.set_query('custom_gst_category', function () {
      return {
        filters: {
          name: ['!=', 'UN'],
        },
      }
    })
  }
}

function showSettingsSelectorDialog(frm, resolve) {
  let dialog = new frappe.ui.Dialog({
    title: __('Select eBMS Settings'),
    fields: [
      {
        label: __('eBMS Settings'),
        fieldname: 'company',
        fieldtype: 'Link',
        options: 'eBMS Settings',
        reqd: 1,
      },
    ],
    size: 'small',
  })

  dialog.set_primary_action(__('Select'), function () {
    let data = dialog.get_values()
    if (data && data.company) {
      resolve(data.company)
    }
    dialog.hide()
  })

  // Handle dialog close without selection
  dialog.$wrapper.on('hidden.bs.modal', function () {
    if (!dialog.get_values()?.company) {
      resolve(null)
    }
  })

  dialog.show()
}

frappe.ui.form.on('Customer', {
  refresh: function (frm) {
    get_tin(frm)
    set_gst_category_query(frm)
  },
  customer_type: function (frm) {
    set_gst_category_query(frm)
  },
})

frappe.ui.form.on('Supplier', {
  refresh: function (frm) {
    get_tin(frm)
    set_gst_category_query(frm)
  },
  supplier_type: function (frm) {
    set_gst_category_query(frm)
  },
})

frappe.ui.form.on('Company', {
  refresh: function (frm) {
    get_tin(frm)
  },
})
