import frappe
from frappe import _
from frappe.model.document import Document


class BudgetController(Document):
    pass


def make_budget_entries(doc, method=None):
    """
    Debit: Budget Amount for each line
    Credit: Budget plan for whole document
    """
    total_debit = 0
    for line in doc.items:
        make_budget_entry(doc, get_debit_entry_type(doc), line=line, debit=line.amount)
        total_debit += line.amount
    # For budget control sheet, credit budget plan for all
    if doc.doctype == "Budget Control Sheet":
        make_budget_entry(doc, get_credit_entry_type(doc), credit=total_debit)
    # For other document, credit budget for every line
    else:
        for line in doc.items:
            make_budget_entry(doc, get_credit_entry_type(doc), line=line, credit=line.amount)


def make_budget_entry(doc, entry_type, line=None, debit=0, credit=0):
    if debit == 0 and credit == 0:
        return
    entry_type_options = frappe.get_meta("Budget Entry").get_field("entry_type").options
    if entry_type not in entry_type_options:
        raise ValueError(
            f"Invalid entry_type {entry_type}. Allowed entry_type are {entry_type_options}"
        )
    analytic_type, analytic_account = get_analytic(doc, line)
    # Create a new Budget Entry
    be = frappe.get_doc({
        "doctype": "Budget Entry",
        "entry_type": entry_type,
        "voucher_type": doc.doctype,
        "voucher": doc.name,
        "voucher_item": line.name if line else None,
        "analytic_type": analytic_type,
        "analytic_account": analytic_account,
        "budget_activity": line.budget_activity if line else None,
        "debit": debit,
        "credit": credit,
        "balance": debit-credit,
        "against_voucher_type": None,
        "against_voucher": None,
        "against_voucher_item": None,
    })
    be.insert(ignore_permissions=True)


def get_budget_entries(doc):
    res = frappe.get_all(
        "Budget Entry",
        filters={
            "voucher_type": doc.doctype,
            "voucher": doc.name
        },
        pluck="name")
    return res


def clear_budget_entries(doc, method=None):
    frappe.db.delete("Budget Entry", {
        "name": ["in", get_budget_entries(doc)]
    })


def get_debit_entry_type(doc):
    entry_types = {
        "Budget Control Sheet": "Budget Amount",
        "Material Request": "MR Commit",
        "Purchase Order": "PO Commit",
    }
    return entry_types[doc.doctype]


def get_credit_entry_type(doc):
    entry_types = {
        "Budget Control Sheet": "Budget Plan",
        "Purchase Order": "Budget Amount",
        "Material Request": "Budget Amount",
    }
    return entry_types[doc.doctype]

def get_analytic(doc, line):
    analytic_type = None
    analytic_account = None
    # BCS
    if doc.doctype == "Budget Control Sheet":
        analytic_type = doc.analytic_type
        analytic_account = doc.analytic_account
    # MR, PO
    if doc.doctype in ["Material Request", "Purchase Order"]:
        if line.cost_center:
            analytic_type = "Cost Center"
            analytic_account = line.cost_center
        if line.project:
            analytic_type = "Project"
            analytic_account = line.project
    # INV
    if not analytic_type:
        frappe.throw(_("Analytic type is not set"))
    return (analytic_type, analytic_account)
