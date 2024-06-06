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
        make_budget_entry(doc, doc.doctype, line=line, debit=line.amount)  # Debit
        total_debit += line.amount
    # For budget control, credit budget plan for all
    if doc.doctype == "Budget Control":
        make_budget_entry(doc, "Budget Plan", credit=total_debit)  # Credit
    # For other document, credit budget for every line
    else:
        for line in doc.items:
            against = get_against_voucher(doc, line)
            entry_type = against.get("against_voucher_type", "Budget Control")
            make_budget_entry(doc, entry_type, line=line, against=against, credit=line.amount)  # Credit


def make_budget_entry(doc, entry_type, line=None, against={}, debit=0, credit=0):
    if debit == 0 and credit == 0:
        return
    entry_type_options = frappe.get_meta("Budget Entry").get_field("entry_type").options
    if entry_type not in entry_type_options:
        raise ValueError(
            f"Invalid entry_type {entry_type}. Allowed entry_type are {entry_type_options}"
        )
    analytic_type, analytic_account = get_analytic(doc, line)
    # Create a new Budget Entry
    be_dict = {
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
    }
    # For follow docs, i.e. PO after MR, set against voucher
    be_dict.update(against)
    be = frappe.get_doc(be_dict)
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


def get_against_voucher(doc, line):
    against_voucher_dict = {}
    if not line:
        against_voucher_dict = {}
    # PO after MR
    if doc.doctype == "Purchase Order" and line.material_request:
        against_voucher_dict = {
            "against_voucher_type": "Material Request",
            "against_voucher": line.material_request,
            "against_voucher_item": line.material_request_item
        }
    # INV after PO
    if doc.doctype == "Purchase Invoice" and line.purchase_order:
        against_voucher_dict = {
            "against_voucher_type": "Purchase Order",
            "against_voucher": line.purchase_order,
            "against_voucher_item": line.po_detail
        }
    return against_voucher_dict


def get_analytic(doc, line):
    analytic_type = None
    analytic_account = None
    # Budget Control
    if doc.doctype == "Budget Control":
        analytic_type = doc.analytic_type
        analytic_account = doc.analytic_account
    # Other docs
    if doc.doctype in ["Material Request", "Purchase Order", "Purchase Invoice"]:
        if line.cost_center:
            analytic_type = "Cost Center"
            analytic_account = line.cost_center
        if line.project:
            analytic_type = "Project"
            analytic_account = line.project
    # No analytic account
    if not analytic_type:
        frappe.throw(_("Analytic type is not set"))
    return (analytic_type, analytic_account)
