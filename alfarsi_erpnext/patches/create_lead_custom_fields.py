from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	df = {
		"fieldname": "create_user",
		"label": "Create a New User",
		"fieldtype": "Check",
		"insert_after": "campaign_name",
		"default": 1
	}
	create_custom_field("Lead", df)
