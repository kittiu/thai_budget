# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from thai_budget.controllers.budget_controller import BudgetController, reset_budget_entries


class BudgetControl(BudgetController):

    @property
    def budget_available(self):
        return self.get_budget_entries_amount("available")

    @property
    def budget_consumed(self):
        return self.get_budget_entries_amount("consumed")

    @property
    def budget_balance(self):
        return self.get_budget_entries_amount()

    def get_budget_entries_amount(self, type="balance"):
        filters = {
            "entry_type": self.doctype,
            "entry_date": ["between", (self.period_start_date, self.period_end_date)],
            "analytic_type": self.analytic_type,
            "analytic_account": self.analytic_account,
        }
        if type == "available":
            filters.update({
                "voucher_type": self.doctype,
                "voucher": self.name
            })
        if type == "consumed":
            filters.update({
                "voucher_type": ["!=", self.doctype],
                "voucher": ["!=", self.name]
            })
        entries = frappe.get_all("Budget Entry", filters=filters, pluck="balance")
        return sum(entries)

    def before_naming(self):
        self.naming_series = f"{self.analytic_account}./.{self.budget_period}/.##"

    def validate(self):
        self.validate_company_analytic()
        self.validate_company_budget_activity()
        self.update_budget_control()

    def validate_company_analytic(self):
        analytic_company = frappe.db.get_value(self.analytic_type, self.analytic_account, "company", cache=True)
        if analytic_company and analytic_company != self.company:
            frappe.throw(
				_("Analytic account {0} does not belong to company {1}").format(self.analytic_account, self.company),
			)

    def validate_company_budget_activity(self):
        for line in self.items:
            activity_company = frappe.db.get_value("Budget Activity", line.budget_activity, "company", cache=True)
            if activity_company != self.company:
                frappe.throw(
                    _("Budget activity {0} does not belong to company {1}").format(line.budget_activity, self.company),
                )

    def update_budget_control(self):
        self.amount = sum([line.amount for line in self.items])
    
    @frappe.whitelist()
    def reset_budget_entries(self):
        reset_budget_entries(self)
