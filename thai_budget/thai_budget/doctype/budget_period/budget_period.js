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

    refresh(frm) {
        if (frm.doc.enqueue_status === undefined) {
            frm.add_custom_button(
                __("Create Budget Controls"),
                function () {
                    frm.trigger("create_budget_controls");
                },
            );
        }
    },

    onload(frm) {
		frappe.realtime.off("completed_budget_control_creation");
		frappe.realtime.on("completed_budget_control_creation", function () {
			frm.reload_doc();
		});
    },

    create_budget_controls: function (frm) {
        var d = new frappe.ui.Dialog({
            title: __("Select Analytic Type / Analytic Accounts"),
            fields: [
                {
                    label: "Analytic Type",
                    fieldname: "analytic_type",
                    fieldtype: "Select",
                    options: "Cost Center\nProject"
                },
                {
                    label: "Create for all accounts",
                    fieldname: "all_accounts",
                    fieldtype: "Check",
                    default: 1,
                },
                {
                    fieldname: "analytic_accounts",
                    label: __("Analytic Accounts"),
                    fieldtype: "MultiSelectList",
                    get_data: function (txt) {   
                        let analytic_type = d.fields_dict.analytic_type.get_value();
                        if (!analytic_type) return;
                        return frappe.db.get_link_options(analytic_type, txt, {
                            company: frm.doc.company
                        });
                    },
                    depends_on: "eval: !doc.all_accounts",
                },
                {
                    fieldname: "budget_activities",
                    label: __("Default Budget Activities"),
                    fieldtype: "MultiSelectList",
                    get_data: function (txt) {
                        return frappe.db.get_link_options("Budget Activity", txt, {
                            company: frm.doc.company
                        });
                    },
                    reqd: 1,
                },
            ],
            primary_action: function () {
                var data = d.get_values();
                frappe.call({
                    doc: frm.doc,
                    method: "create_budget_controls",
                    args: {
                        analytic_type: data.analytic_type,
                        all_accounts: data.all_accounts,
                        analytic_accounts: data.analytic_accounts,
                        budget_activities: data.budget_activities
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            if (r.message) {
                                frappe.set_route("Form", "Account", r.message);
                            }
                            d.hide();
                        }
                    },
                });
            },
            primary_action_label: __("Create Budget Control(s)"),
        });
        d.show();

        // Clear accounts on change
        d.fields_dict["analytic_type"].$input.on("change", function() {
            d.set_value("analytic_accounts", []);
        });        
        d.fields_dict["all_accounts"].$input.on("change", function() {
            d.set_value("analytic_accounts", []);
        });

    
    },



});
