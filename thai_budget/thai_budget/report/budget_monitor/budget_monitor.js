frappe.query_reports["Budget Monitor"] = {
	filters: [
		{
			label: __("Company"),
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			label: __("Entry Type"),
			fieldname: "entry_type",
			fieldtype: "Select",
			options: [
				"",
				"Budget Control",
				"Material Request",
				"Purchase Order",
				"Purchase Invoice",
			],
		},
		{
			label: __("Voucher No"),
			fieldname: "voucher_no",
			fieldtype: "Data",
		},
		{
			label: __("Analytic Type"),
			fieldname: "analytic_type",
			fieldtype: "Select",
			options: [
				"",
				"Cost Center",
				"Project",
			],
		},
		{
			label: __("Analytic Account"),
			fieldname: "analytic_account",
			fieldtype: "Dynamic Link",
			get_query: () => ({
				filters: {
					company: frappe.query_report.get_filter_value("company"),
				},
			}),
			get_options: function () {
				var analytic_type = frappe.query_report.get_filter_value("analytic_type");
				var analytic_account = frappe.query_report.get_filter_value("analytic_account");
				if (analytic_account && !analytic_type) {
					frappe.throw(__("Please select Analytic Type first"));
				}
				return analytic_type;
			},
		},
		{
			label: __("Budget Activity"),
			fieldname: "budget_activity",
			fieldtype: "Link",
			options: "Budget Activity",
			get_query: () => ({
				filters: {
					company: frappe.query_report.get_filter_value("company"),
				},
			}),
		},
		{
			label: __("Pivot Table"),
			fieldname: "pivot_table",
			fieldtype: "Check",
		},
		{
			label: __("Group By"),
			fieldname: "group_by",
			fieldtype: "MultiSelectList",
			depends_on: "eval:doc.pivot_table",
			default: [
				"Analytic Account",
			],
			get_data: function () {
				return [
					{ value: "Analytic Type", description: "Group By" },
					{ value: "Analytic Account", description: "Group By" },
					{ value: "Voucher No", description: "Group By" },
					{ value: "Budget Activity", description: "Group By" },
				];
			},
		},
		{
			label: __("Show Columns"),
			fieldname: "show_columns",
			fieldtype: "MultiSelectList",
			depends_on: "eval:doc.pivot_table",
			default: [
				"Budget Control",
				"Material Request",
				"Purchase Order",
				"Purchase Invoice",
				"Budget Balance",
			],
			get_data: function () {
				return [
					{ value: "Budget Control", description: "Show Columns" },
					{ value: "Material Request", description: "Show Columns" },
					{ value: "Purchase Order", description: "Show Columns" },
					{ value: "Purchase Invoice", description: "Show Columns" },
					{ value: "Budget Balance", description: "Show Columns" },
				];
			},
		},
	],
};
