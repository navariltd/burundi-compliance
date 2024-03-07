// Copyright (c) 2024, Navari Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Labaratory Result Report"] = {
	"filters": [

		{
			"fieldname":"preparation_sheet",
			"label": __("Preparation Sheet"),
			"fieldtype": "Link",
			"options": "Preparation Sheet",
			"width": "100px",
		},
		{
			"fieldname":"dispatch",
			"label": __("Dispatch"),
			"fieldtype": "Link",
			"options": "Dispatch",
			"width": "100px",
		},

		{
		"fieldname":"from_date",
		"label": __("Start Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
		

		},
		{
		"fieldname":"to_date",
		"label": __("End Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.get_today(),
	

		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default": "Submitted",
			"width": "100px"
		}

	],

    // Add the button in the report
	"onload": function (report) {
        // Add a click event listener to handle the "View Results" button click
        report.wrapper.on("click", ".button-view-results", function () {
            var row = $(this).closest("tr");
            var preparationSheet = row.find("[data-fieldname='name']").text();

            fetchAndDisplayResults(preparationSheet);
        });
    }
};

function fetchAndDisplayResults(preparationSheet) {
    frappe.call({
        method: "your_module.your_module.doctype.labaratory_result_report.labaratory_result_report.get_child_results",
        args: {
            preparation_sheet: preparationSheet
        },
        callback: function (response) {
            if (response.message) {
                showResultsDialog(response.message);
            } else {
                frappe.msgprint(__("No results found for the selected preparation sheet."));
            }
        }
    });
}

function showResultsDialog(results) {
    var dialog = new frappe.ui.Dialog({
        title: __("Results for Preparation Sheet"),
        fields: [
            {
                fieldtype: "HTML",
                options: results
            }
        ]
    });

    dialog.show();
}