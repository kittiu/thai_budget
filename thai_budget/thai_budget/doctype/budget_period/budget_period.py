# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form
import json


class BudgetPeriod(Document):

	def get_active_analytic_filter(self, analytic_type):
		if analytic_type == "Cost Center":
			return {"disabled": 0}
		if analytic_type == "Project":
			return {"is_active": "Yes"}
		return {}

	@frappe.whitelist()
	def create_budget_controls(
			self, analytic_type, all_accounts=False,
			analytic_accounts=[], budget_activities=[]
		):
		"""
		Creates budget controls for selected analytic accounts
		"""
		self.check_permission("write")

		filters = self.get_active_analytic_filter(analytic_type)
		filters["company"] = self.company
		if not all_accounts and analytic_accounts:
			filters["name"] = ["in", analytic_accounts]

		analytic_accounts = frappe.get_list(
			analytic_type,
			filters=filters,
			pluck="name",
		)

		if analytic_accounts:
			args = frappe._dict(
				{
					"doctype": "Budget Control",
					"company": self.company,
					"period_start_date": self.period_start_date,
					"period_end_date": self.period_end_date,
					"budget_period": self.name,
					"analytic_type": analytic_type,
					"analytic_account": None,  # To be filled
					"applicable_on_material_request": self.applicable_on_material_request,
					"applicable_on_purchase_order": self.applicable_on_purchase_order,
					"applicable_on_booking_actual_expenses": self.applicable_on_booking_actual_expenses,
					"action_if_annual_budget_exceeded_on_mr": self.action_if_annual_budget_exceeded_on_mr,
					"action_if_accumulated_monthly_budget_exceeded_on_mr": self.action_if_accumulated_monthly_budget_exceeded_on_mr,
					"action_if_annual_budget_exceeded_on_po": self.action_if_annual_budget_exceeded_on_po,
					"action_if_accumulated_monthly_budget_exceeded_on_po": self.action_if_accumulated_monthly_budget_exceeded_on_po,
					"action_if_annual_budget_exceeded": self.action_if_annual_budget_exceeded,
					"action_if_accumulated_monthly_budget_exceeded": self.action_if_accumulated_monthly_budget_exceeded,
					"items": [{"budget_activity": activity, "amount": 0} for activity in budget_activities]
				}
			)

			if len(analytic_accounts) > 1:
				self.db_set("create_budget_control_status", "Queued")
				frappe.enqueue(
					create_budget_controls_for_analytic_accounts,
					timeout=3000,
					analytic_accounts=analytic_accounts,
					args=args,
					publish_progress=False,
				)
				frappe.msgprint(
					_("Budget control creation is queued. It may take a few minutes"),
					alert=True,
					indicator="blue",
				)
			else:
				create_budget_controls_for_analytic_accounts(
					analytic_accounts, args, publish_progress=False
				)
			# since this method is called via frm.call this doc needs to be updated manually
			self.reload()


def create_budget_controls_for_analytic_accounts(analytic_accounts, args, publish_progress=True):
	budget_period = frappe.get_cached_doc("Budget Period", args.budget_period)
	try:
		existing_budget_controls = frappe.get_all(
            "Budget Control",
            filters={
				"company": args.company,
                "analytic_type": args.analytic_type,
                "analytic_account": ["in", analytic_accounts],
                "budget_period": budget_period.name,
                "docstatus": ["!=", 2],
            },
            fields=["analytic_account"]
		)
		existing_accounts = [bc.analytic_account for bc in existing_budget_controls]
		analytic_accounts = list(set(analytic_accounts) - set(existing_accounts))
		count = 0
		for account in analytic_accounts:
			args.update({"analytic_account": account})
			frappe.get_doc(args).insert()
			count += 1
			if publish_progress:
				frappe.publish_progress(
					count * 100 / len(analytic_accounts),
					title=_("Creating Budget Control..."),
				)

		budget_period.db_set({
			"create_budget_control_status": "",
			"error_message": ""
		})

		if existing_accounts:
			frappe.msgprint(
				_(
					"Budget Control already exist for {}, and will not be processed."
				).format(frappe.bold(", ".join(existing_accounts))),
				title=_("Message"),
				indicator="orange",
			)

	except Exception as e:
		frappe.db.rollback()
		log_budget_peroid_failure(budget_period, e)

	finally:
		frappe.db.commit()  # nosemgrep
		frappe.publish_realtime("completed_budget_control_creation", user=frappe.session.user)


def log_budget_peroid_failure(budget_period, error):
	error_log = frappe.log_error(
		title=_("Budget control creation failed for budget period {}").format(budget_period.name)
	)
	message_log = frappe.message_log.pop() if frappe.message_log else str(error)

	try:
		if isinstance(message_log, str):
			error_message = json.loads(message_log).get("message")
		else:
			error_message = message_log.get("message")
	except Exception:
		error_message = message_log

	error_message += "\n" + _("Check Error Log {0} for more details.").format(
		get_link_to_form("Error Log", error_log.name)
	)

	budget_period.db_set({
		"create_budget_control_status": "Failed",
		"error_message": error_message
	})