// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Control", {

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
