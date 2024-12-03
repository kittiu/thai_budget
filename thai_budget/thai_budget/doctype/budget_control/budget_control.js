// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Control", {

    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
			frm.add_custom_button(
				__("View Budget Monitor"),
				function () {
					frappe.route_options = {
                        company: frm.doc.company,
                        entry_type: "Budget Control",
                        voucher_no: frm.doc.name
					};
					frappe.set_route("query-report", "Budget Monitor");
				},
            );
			frm.add_custom_button(
				__("Reset Budget Entries"),
				function () {
					return frappe.call({
						doc: frm.doc,
						method: "reset_budget_entries",
						callback: function () {
							frm.refresh();
						},
					});
				},
            );
        }
    },

    setup: function (frm) {
        frm.set_query("analytic_account", function () {
            return {
                filters: {
                    company: frm.doc.company,
                },
            };
        });
        frm.set_query("analytic_type", function () {
            return {
                filters: {
                    name: ["in", ["Project", "Cost Center"]],
                },
            };
        });
        frm.set_query("budget_activity", "items", function () {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
    },

    company: function (frm) {
        frm.set_value("analytic_account", null);
    },

    analytic_type: function (frm) {
        frm.set_value("analytic_account", null);
    },



});
