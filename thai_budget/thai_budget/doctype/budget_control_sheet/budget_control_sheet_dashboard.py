from frappe import _


def get_data():
	return {
		"fieldname": "voucher",
		"transactions": [
			{
				"label": _("Reference"),
				"items": ["Budget Entry"],
			},
		],
	}
