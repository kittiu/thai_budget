frappe.views.calendar["Budget Entry"] = {
    fields: ["analytic_account", "entry_date", "voucher_no", "name"],
	field_map: {
		"start": "entry_date",
		"end": "entry_date",
		"id": "name",
		"title": "voucher_no",
		"allDay": "allDay",
		"progress": "progress"
	}
};
