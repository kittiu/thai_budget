# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document



class BudgetControlSheet(Document):

	def before_naming(self):
		self.naming_series = f"{self.analytic_account}./.{self.budget_period}/.##"

	def validate(self):
		self.validate_company_analytic()
		self.validate_company_budget_activity()

	def validate_company_analytic(self):
		analytic_company = frappe.db.get_value(self.analytic_type, self.analytic_account, "company", cache=True)
		if analytic_company and analytic_company != self.company:
			frappe.throw(
				_("Analytic account {0} does not belong to company {1}").format(self.analytic_account, self.company),
			)

	def validate_company_budget_activity(self):
		for line in self.budget_control_lines:
			activity_company = frappe.db.get_value("Budget Activity", line.budget_activity, "company", cache=True)
			if activity_company != self.company:
				frappe.throw(
					_("Budget activity {0} does not belong to company {1}").format(line.budget_activity, self.company),
				)

	def on_submit(self):
		self.make_budget_entries()
	
	def make_budget_entries(self):
		"""
		Debit: Budget Amount for each line
		Credit: Budget plan for whole document
		"""
		total_debit = 0
		for line in self.budget_control_lines:
			self.make_budget_entry("Budget Amount", line=line, debit=line.budget_amount)
			total_debit += line.budget_amount
		# Credit budget plan for all
		self.make_budget_entry("Budget Plan", credit=total_debit)

	def make_budget_entry(self, entry_type, line=None, debit=0, credit=0):
		entry_type_options = frappe.get_meta("Budget Entry").get_field("entry_type").options
		if entry_type not in entry_type_options:
			raise ValueError(
				f"Invalid entry_type {entry_type}. Allowed entry_type are {entry_type_options}"
			)
		# Create a new Budget Entry
		be = frappe.get_doc({
			"doctype": "Budget Entry",
			"voucher_type": "Budget Control Sheet",
			"voucher": self.name,
			"voucher_item": line.name if line else None,
			"analytic_type": self.analytic_type,
			"analytic_account": self.analytic_account,
			"entry_type": entry_type,
			"debit": debit,
			"credit": credit,
			"against_voucher_type": None,
			"against_voucher": None,
			"against_voucher_item": None,
		})
		be.insert()
		