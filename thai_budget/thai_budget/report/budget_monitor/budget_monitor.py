import frappe
from frappe import _
from frappe.utils import formatdate
import pandas as pd


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
	if not filters.get("pivot_table"):
		return columns_normal()
	return columns_pivot(filters)


def columns_normal():
	return	[
		{
			"label": _("ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Budget Entry",
		},
		{
			"label": _("Entry Type"),
			"fieldname": "entry_type",
			"fieldtype": "Select",
			"options": "Budget Plan\nBudget Control\nMaterial Request\nPurchase Order\nPurchase Invoice",
		},
		{
			"fieldtype": _("Entry Date"),
			"fieldname": "entry_date",
			"label": "Entry Date",
			"width": 120,
		},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "entry_type",
		},
		{
			"label": _("Analytic Type"),
			"fieldname": "analytic_type",
			"fieldtype": "Select",
			"options": "Project\nCost Center",
		},
		{
			"label": _("Analytic Account"),
			"fieldname": "analytic_account",
			"fieldtype": "Dynamic Link",
			"options": "analytic_type",
		},
		{
			"label": _("Budget Activity"),
			"fieldname": "budget_activity",
			"fieldtype": "Link",
			"options": "Budget Activity",
			"width": 120,
		},
		{
			"label": _("Debit"),
			"fieldname": "debit",
			"fieldtype": "Currency",
			"width": 120,
			"hidden": 1,
		},
		{
			"label": _("Credit"),
			"fieldname": "credit",
			"fieldtype": "Currency",
			"width": 120,
			"hidden": 1,
		},
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Currency",
			"width": 120,
		},
	]


def columns_pivot(filters):
	columns = []
	for group_by in filters.get("group_by"):
		if frappe.scrub(group_by) == "analytic_type":
			columns.append({
				"label": _("Analytic Type"),
				"fieldname": "analytic_type",
				"fieldtype": "Select",
				"options": "Project\nCost Center",
			})
		if frappe.scrub(group_by) == "analytic_account":
			columns.append({
				"label": _("Analytic Account"),
				"fieldname": "analytic_account",
				"fieldtype": "Dynamic Link",
				"options": "analytic_type",
			})
		if frappe.scrub(group_by) == "voucher_no":
			columns.append({
				"label": _("Voucher No"),
				"fieldname": "voucher_no",
				"fieldtype": "Data",
			})
		if frappe.scrub(group_by) == "budget_activity":
			columns.append({
				"label": _("Budget activity"),
				"fieldname": "budget_activity",
				"fieldtype": "Link",
				"options": "Budget Activity",
			})
	
	for column in filters.get("show_columns"):
		columns.append({
			"label": _(column),
			"fieldname": column,
			"fieldtype": "Currency",
			"width": 150,
		})
	return columns


def get_data(filters):
	f_list = ["company", "entry_type", "voucher_no", "analytic_type", "analytic_account", "budget_activity"]
	data = frappe.get_list(
		"Budget Entry",
		filters={
			k: v for k, v in filters.items() if k in f_list
		},
		fields=["*"],
		order_by="creation ASC",
	)
	data = prepare_data(data)
	if filters.get("pivot_table"):
		data, gb_columns = prepare_pivot_data(data, filters)
	return data


def prepare_data(data):
	# Remove item from data where entry_type is Budget Plan
	data = [d for d in data if d.get("entry_type") != "Budget Plan"]
	# Remove item from data where (entry_type == Budget Control and voucher_type != Budget Control)
	data = [d for d in data if not (d.get("entry_type") == "Budget Control" and d.get("voucher_type") != "Budget Control")]
	# For each item in data that entry_type != Budget Control, negate balance
	for d in data:
		if d.get("entry_type") != "Budget Control":
			d["balance"] = -d.get("balance")
	# Format date
	for d in data:
		d["entry_date"] = formatdate(d.get("entry_date"))
		d.pop("creation")
		d.pop("modified")
	# None data change to "-"
	for d in data:
		for k in d.keys():
			d[k] = d[k] or "-"
	# Refresh dict, to ensure compatibility with pd.DataFrame
	format_data = []
	for d in data:
		format_data.append(dict(d))
	return format_data


def prepare_pivot_data(data, filters):
	if not filters.get("pivot_table"):
		return data
	df = pd.DataFrame(data)
	gb_columns = [frappe.scrub(x) for x in filters.get("group_by", [])]
	pivot_table = pd.pivot_table(
		df, values="balance", index=["entry_type"],
		columns=gb_columns,
		aggfunc="sum", fill_value=0
	)
	data = []
	# Transform result from pivot_table to list of dict
	for k, v in pivot_table.to_dict().items():
		v["Budget Balance"] = sum(v.values())
		gb_vals = {}
		for idx, gb in enumerate(gb_columns):
			gb_vals[gb] = k[idx] if isinstance(k, tuple) else k
		v.update(gb_vals)
		data.append(v)
	return (data, gb_columns)
