from frappe import _


def get_data():
	return {
		"fieldname": "budget_period",
		"transactions": [
			{"label": _("Budgeting"), "items": ["Budget Control"]},
		],
	}
