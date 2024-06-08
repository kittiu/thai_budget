from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from thai_budget.controllers.budget_controller import BudgetController, reset_budget_entries, return_budget_balance


class PurchaseOrderTB(BudgetController, PurchaseOrder):

	def update_status(self, status):
		super().update_status(status)
		if self.docstatus != 1:
			return
		if self.status == "Closed":
			return_budget_balance(self)
		else:
			reset_budget_entries(self)