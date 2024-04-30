# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _, throw
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum
from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate

import erpnext
from erpnext.accounts.deferred_revenue import validate_service_stop_date
from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
from erpnext.accounts.doctype.repost_accounting_ledger.repost_accounting_ledger import (
	validate_docs_for_deferred_accounting,
	validate_docs_for_voucher_types,
)
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	check_if_return_invoice_linked_with_payment_entry,
	get_total_in_party_account_currency,
	is_overdue,
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import (
	get_party_tax_withholding_details,
)
from thai_budget.thai_budget.budget_ledger import(
	# get_round_off_account_and_cost_center,
	make_bl_entries,
	make_reverse_bl_entries,
	# merge_similar_entries,
)
from erpnext.accounts.party import get_due_date, get_party_account
from erpnext.accounts.utils import get_account_currency, get_fiscal_year
from erpnext.assets.doctype.asset.asset import is_cwip_accounting_enabled
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.buying.utils import check_on_hold_or_closed_status
from erpnext.controllers.accounts_controller import validate_account_head
from erpnext.controllers.buying_controller import BuyingController
from erpnext.stock import get_warehouse_account_map
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import (
	get_item_account_wise_additional_cost,
	update_billed_amount_based_on_po,
)
from erpnext.controllers.accounts_controller import AccountsController




class BudgetControlSheet(AccountsController):
	def before_naming(self):
		self.naming_series = f"{{{frappe.scrub(self.budget_against)}}}./.{self.fiscal_year}/.##"

	def on_submit(self):
		super().on_submit()
		self.make_bl_entries()

	def make_bl_entries(self, bl_entries=None, from_repost=False):
		if not bl_entries:
			bl_entries = self.get_bl_entries()

		if bl_entries:
			if self.docstatus == 1:
				make_bl_entries(
					bl_entries,
					update_outstanding=update_outstanding,
					merge_entries=False,
					from_repost=from_repost,
				)
				self.make_exchange_gain_loss_journal()
			elif self.docstatus == 2:
				pass
		# 		provisional_entries = [a for a in bl_entries if a.voucher_type == "Purchase Receipt"]
		# 		make_reverse_bl_entries(voucher_type=self.doctype, voucher_no=self.name)
		# 		if provisional_entries:
		# 			for entry in provisional_entries:
		# 				frappe.db.set_value(
		# 					"GL Entry",
		# 					{
		# 						"voucher_type": "Purchase Receipt",
		# 						"voucher_detail_no": entry.voucher_detail_no,
		# 					},
		# 					"is_cancelled",
		# 					1,
		# 				)

		# 	if update_outstanding == "No":
		# 		update_outstanding_amt(
		# 			self.credit_to,
		# 			"Supplier",
		# 			self.supplier,
		# 			self.doctype,
		# 			self.return_against if cint(self.is_return) and self.return_against else self.name,
		# 		)

		# elif self.docstatus == 2 and cint(self.update_stock) and self.auto_accounting_for_stock:
		# 	make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)


	def get_bl_entries(self):
		# BL Entries as the total budget allocation for this budget control sheet
		# -----------------------------------------------------------------------
		# Dr: Budget Allocation for Activity & Costcenter/Project on Month 1 = 10 (alloc 120 on month 1 if no distribution)
		# Dr: Budget Allocation for Activity & Costcenter/Project on Month 2 = 10
		# ....
		# Dr: Budget Allocation for Activity & Costcenter/Project on Month 12 = 10
		# 	Cr: Budget Allocation - 120
		gl_entries = []

		self.make_budget_gl_entry(gl_entries)
		self.make_budget_distribute_gl_entries(gl_entries)
		return gl_entries

	def make_budget_gl_entry(self, gl_entries):
		if self.budget_amount:
			gl_entries.append(
				self.get_gl_dict(
					{
						"account": self.budget_period.budget_account,
						"against": self.budget_period.budget_account,
						"credit": self.budget_amount,
						"against_voucher": self.name,
						"against_voucher_type": self.doctype,
						"project": self.project,
						"cost_center": self.cost_center,
					}
				)
			)

	def make_budget_distribute_gl_entries(self, gl_entries):

		for bl in self.get("budget_control_lines"):
			gl_entries.append(
				self.get_gl_dict(
					{
						"account": self.budget_period.budget_account,
						"against": self.budget_period.budget_account,
						"debit": bl.budget_amount,
						"remarks": self.get("remarks") or _("Budget Allocation for {}").format(self.name),
						"cost_center": self.cost_center,
						"project": self.project,
					},
					item=bl,
				)
			)


