import frappe

from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from thai_budget.controllers.budget_controller import BudgetController, reset_budget_entries, return_budget_balance


class PurchaseOrderTB(BudgetController, PurchaseOrder):

	def on_submit(self):
		frappe.flags.doc_budget_check = frappe._dict({
			"overall": "applicable_on_purchase_order",
			"annually": "action_if_annual_budget_exceeded_on_po",
			"monthly": "action_if_accumulated_monthly_budget_exceeded_on_po"
		})
		super().on_submit()
	
	def update_status(self, status):
		super().update_status(status)
		if self.docstatus != 1:
			return
		if self.status == "Closed":
			return_budget_balance(self)
		else:
			reset_budget_entries(self)