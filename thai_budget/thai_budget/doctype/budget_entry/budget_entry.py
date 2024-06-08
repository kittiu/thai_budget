# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BudgetEntry(Document):

	def validate(self):
		self.update_balance()
		self.update_date()
		self.update_voucher_no()

	def update_balance(self):
		self.balance = self.debit - self.credit

	def update_date(self):
		# Entry date is based on transaction date of the voucher
		DATES = {
			"Budget Control": "period_start_date",
			"Material Request": "transaction_date",
			"Purchase Order": "transaction_date",
			"Purchase Invoice": "posting_date",
		}
		self.entry_date = frappe.db.get_value(
			self.voucher_type, self.voucher, DATES[self.voucher_type]
		)

	def update_voucher_no(self):
		self.voucher_no = self.voucher if not self.against_voucher else self.against_voucher

	@property
	def budget_balance(self):
		"""
          This method assume positive balance as budget
          and find the consumed balance and result in budget balance.
          Normally balance should be 0, if not, it means over budget.
        """
		if self.entry_type in ["Budget Plan", "Budget Control"]:  # Not applicable
			return None
		budgeted = frappe.get_all(
			"Budget Entry",
			filters={
				"entry_type": self.voucher_type,
				"voucher_type": self.voucher_type,
				"voucher": self.voucher,
				"voucher_item": self.voucher_item,
			},
			pluck="balance",
		)
		consumed = frappe.get_all(
			"Budget Entry",
			filters={
				"against_voucher_type": self.voucher_type,
				"against_voucher": self.voucher,
				"against_voucher_item": self.voucher_item,
			},
			pluck="balance",
		)
		return sum(budgeted + consumed)
