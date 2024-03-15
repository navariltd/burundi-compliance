

frappe.listview_settings['Stock Ledger Entry'].onload = function(listview) {
    
    listview.page.add_action_item(__("eBIMS Tracker"), function() {
    	frappe.msgprint("eBIMS Tracker");
});
};
