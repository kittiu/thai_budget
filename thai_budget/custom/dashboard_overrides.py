from frappe import _


def add_budget_entry_link(data):
    data["non_standard_fieldnames"].update({"Budget Entry": "voucher"})
    data["transactions"].append(
        {"label": _("Budgeting"), "items": ["Budget Entry"]}
    )

def get_dashboard_data_for_material_request(data):
	add_budget_entry_link(data)
	return data


def get_dashboard_data_for_purchase_order(data):
	add_budget_entry_link(data)
	return data

def get_dashboard_data_for_purchase_invoice(data):
	add_budget_entry_link(data)
	return data
