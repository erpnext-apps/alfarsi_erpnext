from . import __version__ as app_version

app_name = "alfarsi_erpnext"
app_title = "Alfarsi ERPNext"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "A custom app for Alfarsi International"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "developers@frappe.io"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/alfarsi_erpnext/css/alfarsi_erpnext.css"
# app_include_js = "/assets/alfarsi_erpnext/js/alfarsi_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/alfarsi_erpnext/css/alfarsi_erpnext.css"
web_include_js = ["/assets/js/alfarsi-erpnext.min.js", "assets/js/dialog.min.js",
	"assets/js/control.min.js", "assets/js/form.min.js"]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "alfarsi_erpnext/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "alfarsi_erpnext.install.before_install"
# after_install = "alfarsi_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "alfarsi_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Lead": {
		"validate": "alfarsi_erpnext.alfarsi_erpnext.customer.create_user_on_lead_creation"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"alfarsi_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"alfarsi_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"alfarsi_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"alfarsi_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"alfarsi_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "alfarsi_erpnext.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "alfarsi_erpnext.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "alfarsi_erpnext.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"alfarsi_erpnext.auth.validate"
# ]

