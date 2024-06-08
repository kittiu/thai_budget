from erpnext.stock.doctype.material_request.material_request import MaterialRequest
from thai_budget.controllers.budget_controller import BudgetController, reset_budget_entries, return_budget_balance

class MaterialRequestTB(BudgetController, MaterialRequest):

	def update_status(self, status):
		super().update_status(status)
		if self.docstatus != 1:
			return
		if self.status == "Stopped":
			return_budget_balance(self)
		else:
			reset_budget_entries(self)