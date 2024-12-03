frappe.ui.form.on("Purchase Order", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
			frm.add_custom_button(
				__("View Budget Monitor"),
				function () {
					frappe.route_options = {
                        company: frm.doc.company,
                        entry_type: "Purchase Order",
                        voucher_no: frm.doc.name
					};
					frappe.set_route("query-report", "Budget Monitor");
				},
            );
        }
    }
});
