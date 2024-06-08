from erpnext.stock.doctype.material_request.material_request import MaterialRequest
from thai_budget.controllers.budget_controller import BudgetController


class MaterialRequestTB(BudgetController, MaterialRequest):
    pass