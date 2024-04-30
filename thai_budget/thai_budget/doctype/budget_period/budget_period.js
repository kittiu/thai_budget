// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Period", {
	setup(frm) {
        frm.set_query("budget_account", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    root_type: "Liability",
                    is_group: 0,
                },
            };
        });
	},

});
