// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Activity", {

	setup(frm) {
        frm.set_query("account", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    report_type: "Profit and Loss",
                    is_group: 0,
                },
            };
        });
	},

});
