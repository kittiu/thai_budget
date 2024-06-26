import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from thai_budget.controllers.budget_controller import BudgetController


class PurchaseInvoiceTB(BudgetController, PurchaseInvoice):

	def on_submit(self):
		frappe.flags.doc_budget_check = frappe._dict({
			"overall": "applicable_on_booking_actual_expenses",
			"annually": "action_if_annual_budget_exceeded",
			"monthly": "action_if_accumulated_monthly_budget_exceeded"
		})
		super().on_submit()
