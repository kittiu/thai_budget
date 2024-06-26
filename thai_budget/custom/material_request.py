import frappe
from erpnext.stock.doctype.material_request.material_request import MaterialRequest
from thai_budget.controllers.budget_controller import BudgetController, reset_budget_entries, return_budget_balance

class MaterialRequestTB(BudgetController, MaterialRequest):

	def on_submit(self):
		frappe.flags.doc_budget_check = frappe._dict({
			"overall": "applicable_on_material_request",
			"annually": "action_if_annual_budget_exceeded_on_mr",
			"monthly": "action_if_accumulated_monthly_budget_exceeded_on_mr"
		})
		super().on_submit()

	def update_status(self, status):
		super().update_status(status)
		if self.docstatus != 1:
			return
		if self.status == "Stopped":
			return_budget_balance(self)
		else:
			reset_budget_entries(self)