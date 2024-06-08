import frappe
from frappe import _
from frappe.model.document import Document


class BudgetController(Document):

    @property
    def budget_balance(self):
        entries = frappe.get_all(
            "Budget Entry",
            filters={
                "entry_type": self.doctype,
                "voucher_type": self.doctype,
                "voucher": self.name
            },
            pluck="balance",
        )
        against = frappe.get_all(
            "Budget Entry",
            filters={
                "entry_type": self.doctype,
                "against_voucher_type": self.doctype,
                "against_voucher": self.name
            },
            pluck="balance",
        )
        return sum(entries + against)

    def on_submit(self):
        make_budget_entries(self)
        on_submit_check_budget(self)

    def on_cancel(self):
        clear_budget_entries(self)


def make_budget_entries(doc, method=None):
    """
    Debit: Budget Amount for each line
    Credit: Budget plan for whole document
    """
    if doc.docstatus != 1:
        return
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
            against, budget_balance = get_against_voucher(doc, line)
            entry_type = against.get("against_voucher_type", "Budget Control")
            # Credit against voucher item, if over budget, split to Budget Control
            credit_against = line.amount if line.amount <= budget_balance else budget_balance
            credit_budget = line.amount - credit_against
            if credit_against:
                make_budget_entry(doc, entry_type, line=line, against=against, credit=credit_against)  # Credit
            if credit_budget:
                make_budget_entry(doc, "Budget Control", line=line, credit=credit_budget)


def return_budget_balance(doc, method=None):
    """
    This function is called when stop the document and want to return budget.
    1. Find all budget entries for this document
    2. Reverse all budget entries with budget balance
    """
    budget_entries = get_budget_entries(doc, is_consume=True)
    for be in budget_entries:
        # Credit remaining
        doc = frappe.get_doc("Budget Entry", be)
        return_amount = doc.budget_balance
        if not return_amount:
            continue
        new_doc = frappe.new_doc("Budget Entry")
        new_doc.update(doc.as_dict())
        new_doc.name = None
        new_doc.credit = return_amount
        new_doc.debit = 0
        new_doc.insert(ignore_permissions=True)
        # Debit remaining back to Budget Control
        new_doc.name = None
        new_doc.debit = return_amount
        new_doc.credit = 0
        new_doc.entry_type = "Budget Control"
        new_doc.insert(ignore_permissions=True)


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
        "company": doc.company,
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


def get_budget_entries(doc, is_consume=False):
    filters = {
        "voucher_type": doc.doctype,
        "voucher": doc.name
    }
    # To return only consumed budget entries of this doc
    if is_consume:
        filters.update({"entry_type": doc.doctype})
    res = frappe.get_all(
        "Budget Entry",
        filters=filters,
        pluck="name"
    )
    return res


def clear_budget_entries(doc, method=None):
    frappe.db.delete("Budget Entry", {
        "name": ["in", get_budget_entries(doc)]
    })


def reset_budget_entries(doc, method=None):
    clear_budget_entries(doc)
    make_budget_entries(doc)


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
    # Finally, get budget_balance of the against voucher item
    against_voucher_budget_balance = 0
    if against_voucher_dict:
        budget_entry = frappe.get_doc(
            "Budget Entry",
            {
                "entry_type": against_voucher_dict["against_voucher_type"],
                "voucher_type": against_voucher_dict["against_voucher_type"],
                "voucher": against_voucher_dict["against_voucher"],
                "voucher_item": against_voucher_dict["against_voucher_item"]
            },
            ignore_permissions=True
        )
        against_voucher_budget_balance = budget_entry.budget_balance
    return (against_voucher_dict, against_voucher_budget_balance)


def get_analytic(doc, line):
    analytic_type = None
    analytic_account = None
    # Budget Control
    if doc.doctype == "Budget Control":
        analytic_type = doc.analytic_type
        analytic_account = doc.analytic_account
    # Other docs
    if doc.doctype in ["Material Request", "Purchase Order", "Purchase Invoice"]:
        if line.cost_center and line.project:
            frappe.throw(_("Selecting both Cost Center and Project is not allowed when create Budget Entry"))
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


def get_matched_budget_controls(doc):
    """
    This method find matched budget controls for from all budget entries
    """
    # Get all budget entries for this document
    budget_entries = frappe.get_all(
        "Budget Entry",
        filters={
            "voucher_type": doc.doctype,
            "voucher": doc.name
        },
        fields=["entry_date", "analytic_type", "analytic_account"]
    )
    # Find unique set of {entry_date, analytic_type, analytic_account}
    unique_sets = {(i["entry_date"], i["analytic_type"], i["analytic_account"]): i for i in budget_entries}.values()
    # Get all budget controls for criteria in unique_set
    budget_controls = []
    unmatched_sets = []
    for unique_set in unique_sets:
        budget_control = frappe.get_all(
            "Budget Control",
            filters={
                "docstatus": 1,
                "period_start_date": ["<=", unique_set["entry_date"]],
                "period_end_date": [">=", unique_set["entry_date"]],
                "analytic_type": unique_set["analytic_type"],
                "analytic_account": unique_set["analytic_account"],
            },
            pluck="name"
        )
        if budget_control:
            budget_controls.extend(budget_control)
        else:
            unmatched_sets.append(unique_set)
    return (budget_controls, unmatched_sets)


def on_submit_check_budget(doc):
    budget_controls, unmatched_sets = get_matched_budget_controls(doc)
    over_budget_controls = []
    for bc in budget_controls:
        budget_control = frappe.get_doc("Budget Control", bc)
        if budget_control.budget_balance < 0:
            over_budget_controls.append(budget_control)
    show_error_message(unmatched_sets, over_budget_controls)


def show_error_message(unmatched_sets, over_budget_controls):
    error_list = []
    for budget_control in over_budget_controls:
        error_list.append(
            _("<li><b>{0}</b> will be <b>{1:,.2f}</b> over budget - {2}</li>").format(
            budget_control.analytic_account,
            -budget_control.budget_balance,
            frappe.utils.get_link_to_form("Budget Control", budget_control.name)
        ))
    for unmatched_set in unmatched_sets:
        error_list.append(
            _("<li><b>{0}</b> has no budget allocated and cannot continue</li>").format(
                unmatched_set["analytic_account"]
            )
        )
    if over_budget_controls or unmatched_sets:
        errors = "".join(error_list)
        error_message = _("After submit this document,<ul>{0}</ul>").format(errors)
        frappe.throw(error_message)
