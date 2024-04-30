// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Control Sheet", {
	setup(frm) {
        frm.set_query("cost_center", function () {
            return {
                filters: {
                    company: frm.doc.company,
                },
            };
        });
        frm.set_query("project", function () {
            return {
                filters: {
                    company: frm.doc.company,
                },
            };
        });
	},
});
