// Copyright (c) 2024, Navari Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("eBMS Settings", {
	refresh(frm) {
        $("[data-fieldname='event_frequency'").attr("title", "This determines how often the system will automatically send invoices to OBR.\nSelect the appropriate frequency based on the volume of sales and your preferred schedule for invoice submission to OBR.");
        $("[data-fieldname='stock_movement_event_frequency'").attr("title", "This determines how often the system will automatically send stock movement to OBR.");
        $("[data-fieldname='cron_format'").attr("title", "Use this field to specify the exact time of day when the system should send invoices to OBR.\n Check here https://crontab.guru/");
        $("[data-fieldname='stock_movement_cron_format'").attr("title", "Use this field to specify the exact time of day when the system should send stock movement to OBR.\n Check here https://crontab.guru/");
        $("[data-fieldname='maximum_attempts'").attr("title", "This determines the number of times the system will attempt to send invoices to OBR when serve is down before stopping.\n");
        $("[data-fieldname='retry_delay_seconds'").attr("title", "This determines the number of seconds the system will wait before attempting to send invoices to OBR again after a failed attempt.");

        
	},
});
