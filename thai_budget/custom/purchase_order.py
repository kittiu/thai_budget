from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from thai_budget.controllers.budget_controller import BudgetController


class PurchaseOrderTB(BudgetController, PurchaseOrder):
    pass
