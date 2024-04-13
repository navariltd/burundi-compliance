

frappe.listview_settings["Stock Entry"].onload = function(listview) {
    listview.page.add_action_item(__("eBIMS Tracker"), function() {
    	submit_bulk_stock( listview, "Stock Entry" );
});
};


function submit_bulk_stock(listview, doctype){
    let names=[];
    $.each(listview.get_checked_items(), function(key, value) {
        names.push(value.name);
    });

    if (names.length === 0) {
        frappe.throw(__("No rows selected."));
    }
            
    frappe.call({
        method: "burundi_compliance.burundi_compliance.utils.bulk_transaction.bulk_stock_submission",
        args: {
            "stock_details": names,
            "doctype":doctype
        },
    })
}
