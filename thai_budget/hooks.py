app_name = "thai_budget"
app_title = "Thai Budget"
app_publisher = "Ecosoft"
app_description = "Budgeting for Thai Government"
app_email = "kittiu@ecosoft.co.th"
app_license = "mit"
# required_apps = []
fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				[
					"Purchase Order Item-budget_activity",
                    "Material Request Item-budget_activity",
                    "Purchase Invoice Item-budget_activity",
                    "Material Request-budget_status",
                    "Material Request-budget_balance",
                    "Purchase Order-budget_status",
                    "Purchase Order-budget_balance",
                    "Purchase Invoice-budget_status",
                    "Purchase Invoice-budget_balance",
                    "Material Request-custom_procurement_method",
                    "Material Request-custom_purchase_type",
                    "Material Request-custom_column_break_gr4nl",
                    "Material Request-custom_column_break_xx6cp",
                    "Material Request-custom_procurement_type",
                    "Material Request-custom_procurement",
                    "Material Request-custom_work_acceptance_committees",
                    "Material Request-custom_work_acceptance",
                    "Material Request-custom_procurement_committees",
                    "Material Request-custom_procurement",
                    "Material Request-custom_committee",
                ]
            ]
        ]
    }
]


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/thai_budget/css/thai_budget.css"
# app_include_js = "/assets/thai_budget/js/thai_budget.js"

# include js, css files in header of web template
# web_include_css = "/assets/thai_budget/css/thai_budget.css"
# web_include_js = "/assets/thai_budget/js/thai_budget.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "thai_budget/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Material Request": "public/js/material_request.js",
    "Purchase Order": "public/js/purchase_order.js",
    "Purchase Invoice": "public/js/purchase_invoice.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "thai_budget/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "thai_budget.utils.jinja_methods",
# 	"filters": "thai_budget.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "thai_budget.install.before_install"
# after_install = "thai_budget.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "thai_budget.uninstall.before_uninstall"
# after_uninstall = "thai_budget.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "thai_budget.utils.before_app_install"
# after_app_install = "thai_budget.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "thai_budget.utils.before_app_uninstall"
# after_app_uninstall = "thai_budget.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "thai_budget.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Material Request": "thai_budget.custom.material_request.MaterialRequestTB",
	"Purchase Order": "thai_budget.custom.purchase_order.PurchaseOrderTB",
	"Purchase Invoice": "thai_budget.custom.purchase_invoice.PurchaseInvoiceTB",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "Budget Control": {
    #     "on_submit": [
    #         "thai_budget.controllers.budget_controller.make_budget_entries",
    #     ],
    #     "on_cancel": [
    #         "thai_budget.controllers.budget_controller.clear_budget_entries",
    #     ]
	# },
	# "Material Request": {
    #     "on_submit": [
    #         "thai_budget.controllers.budget_controller.make_budget_entries",
    #     ],
    #     "on_cancel": [
    #         "thai_budget.controllers.budget_controller.clear_budget_entries",
    #     ]
	# },
	# "Purchase Order": {
    #     "on_submit": [
    #         "thai_budget.controllers.budget_controller.make_budget_entries",
    #     ],
    #     "on_cancel": [
    #         "thai_budget.controllers.budget_controller.clear_budget_entries",
    #     ]
	# },
	# "Purchase Invoice": {
    #     "on_submit": [
    #         "thai_budget.controllers.budget_controller.make_budget_entries",
    #     ],
    #     "on_cancel": [
    #         "thai_budget.controllers.budget_controller.clear_budget_entries",
    #     ]
	# }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"thai_budget.tasks.all"
# 	],
# 	"daily": [
# 		"thai_budget.tasks.daily"
# 	],
# 	"hourly": [
# 		"thai_budget.tasks.hourly"
# 	],
# 	"weekly": [
# 		"thai_budget.tasks.weekly"
# 	],
# 	"monthly": [
# 		"thai_budget.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "thai_budget.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "thai_budget.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "thai_budget.task.get_dashboard_data"
# }

override_doctype_dashboards = {
	"Material Request": "thai_budget.custom.dashboard_overrides.get_dashboard_data_for_material_request",
	"Purchase Order": "thai_budget.custom.dashboard_overrides.get_dashboard_data_for_purchase_order",
	"Purchase Invoice": "thai_budget.custom.dashboard_overrides.get_dashboard_data_for_purchase_invoice",
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["thai_budget.utils.before_request"]
# after_request = ["thai_budget.utils.after_request"]

# Job Events
# ----------
# before_job = ["thai_budget.utils.before_job"]
# after_job = ["thai_budget.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"thai_budget.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
