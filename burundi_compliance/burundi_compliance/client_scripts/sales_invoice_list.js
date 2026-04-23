frappe.listview_settings['Sales Invoice'].onload = function (listview) {
  listview.page.add_action_item(__('Submit to EBMS'), function () {
    submit_bulk_invoice(listview, 'Sales Invoice')
  })
}

function submit_bulk_invoice(listview, doctype) {
  let names = []
  $.each(listview.get_checked_items(), function (key, value) {
    names.push(value.name)
  })

  if (names.length === 0) {
    frappe.throw(__('No rows selected.'))
  }

  frappe.call({
    method:
      'burundi_compliance.burundi_compliance.apis.sales_invoice.bulk_submit_invoices_to_obr',
    args: {
      doctype: doctype,
      invoice_list: names,
    },
    freeze: true,
    freeze_message: __('Submitting invoices to EBMS...'),
  })
}
