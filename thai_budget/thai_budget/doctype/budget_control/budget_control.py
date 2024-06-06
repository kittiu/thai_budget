# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class BudgetControl(Document):


	def before_naming(self):
		self.naming_series = f"{self.analytic_account}./.{self.budget_period}/.##"

	def validate(self):
		self.validate_company_analytic()
		self.validate_company_budget_activity()
		self.update_budget_control()

	def validate_company_analytic(self):
		analytic_company = frappe.db.get_value(self.analytic_type, self.analytic_account, "company", cache=True)
		if analytic_company and analytic_company != self.company:
			frappe.throw(
				_("Analytic account {0} does not belong to company {1}").format(self.analytic_account, self.company),
			)

	def validate_company_budget_activity(self):
		for line in self.items:
			activity_company = frappe.db.get_value("Budget Activity", line.budget_activity, "company", cache=True)
			if activity_company != self.company:
				frappe.throw(
					_("Budget activity {0} does not belong to company {1}").format(line.budget_activity, self.company),
				)

	def update_budget_control(self):
		self.amount = sum([line.amount for line in self.items])