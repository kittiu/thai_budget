frappe.ui.form.on("Purchase Invoice", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
			frm.add_custom_button(
				__("View Budget Monitor"),
				function () {
					frappe.route_options = {
                        company: frm.doc.company,
                        entry_type: "Purchase Invoice",
                        voucher_no: frm.doc.name
					};
					frappe.set_route("query-report", "Budget Monitor");
				},
            );
        }
    }
});
