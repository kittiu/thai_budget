from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from thai_budget.controllers.budget_controller import BudgetController


class PurchaseInvoiceTB(BudgetController, PurchaseInvoice):
    pass
