// Reusable function to add a custom button for retrying sending invoices
function addRetrySendingButton(frm, doc_type) {
    if (frm.doc.docstatus == 1) {
        if(frm.doc.custom_etracker===0){
            frm.add_custom_button(__('Re-Submit'), function() {
                frappe.call({
                      method: 'burundi_compliance.burundi_compliance.utils.background_jobs.retry_stock_movement_after_failure',
                      args: {
                          "doc_type": doc_type,
                          "doc_name": frm.doc.name,
                      },
                      callback: function(response) {
                          if (response.message) {
                              frappe.msgprint("Invoice sent successfully");
                          } else {
                              frappe.msgprint("Failed to send invoice");
                          }
                      }
                  });
              }, __('E-Tracking'));
        }
       
    }
}

frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        addRetrySendingButton(frm, "Stock Entry");
    }
});

frappe.ui.form.on('Stock Reconciliation', {
    refresh: function(frm) {
        addRetrySendingButton(frm, "Stock Reconciliation");
    }
});

frappe.ui.form.on('Purchase Invoice', {
    refresh: function(frm) {
        addRetrySendingButton(frm, "Purchase Invoice");
    }
});

frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        addRetrySendingButton(frm, "Purchase Receipt");
    }
});

frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        addRetrySendingButton(frm, "Delivery Note");
    }
});