from . import __version__ as app_version

app_name = "company_wallet"
app_title = "Company Wallet"
app_publisher = "Fintechsys"
app_description = "This app for make a company wallet make bulk payments"
app_email = "info@fintechsys.net"
app_license = "MIT"


on_session_creation = "company_wallet.on_session_creation"

on_login = "company_wallet.custom_settings.on_login"


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/company_wallet/css/company_wallet.css"
# app_include_js = "/assets/company_wallet/js/company_wallet.js"

# include js, css files in header of web template
# web_include_css = "/assets/company_wallet/css/company_wallet.css"
# web_include_js = "/assets/company_wallet/js/company_wallet.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "company_wallet/public/scss/website"

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
app_include_js = [
				"/assets/company_wallet/js/desk_navbar.js",
				"/assets/company_wallet/js/table_controller.js",
				"/assets/company_wallet/js/action_confirm_message.js"
				]
web_include_js = "/assets/company_wallet/js/set_first_login.js"

# Home Pages
# ----------
website_route_rules = [
	{"from_route": "/swagger", "to_route": "swagger/index.html"},
]

CW_OPENAPI_DIR = "api"
CW_OPENAPI_OUTPUT_FILE = ["www", "swagger", "swagger.json"]


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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "company_wallet.utils.jinja_methods",
#	"filters": "company_wallet.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "company_wallet.install.before_install"
after_install = "company_wallet.install.after_install"
after_migrate = "company_wallet.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "company_wallet.uninstall.before_uninstall"
# after_uninstall = "company_wallet.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "company_wallet.utils.before_app_install"
# after_app_install = "company_wallet.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "company_wallet.utils.before_app_uninstall"
# after_app_uninstall = "company_wallet.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "company_wallet.notifications.get_notification_config"

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
doc_events = {
	"Wallet Payment": {
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
	"Wallet Bulk Payment": {
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
	"Wallet Payment Log": {
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
	"Payment Query Reference": {
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
	"Bulk Edit Download Template": {
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
	"Device Info Log": {
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
    "Bulk Payment Template": {
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
        
	"User": {
		"before_save": [
			"company_wallet.custom_settings.reset_user_login_attempts"
		]
	},
	"Activity Log": {
		"after_insert": [
			"company_wallet.custom_settings.check_login_attempts"
			],
	},
	"Wallet Company": {
		"after_save": [
			"company_wallet.company_wallet.doctype.statement_account.statement_account.create_account_statement_log"
		],
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	},
	"Wallet User": {
		"after_save": [
			"company_wallet.company_wallet.doctype.walllet_user.walllet_user.initialize_password"
		],
		"before_validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.set_user_wallet_company"
		],
		"validate": [
			"company_wallet.company_wallet.doctype.wallet_company.wallet_company.validate_disabled_company",
		],
		"before_submit": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"before_save": [
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_transaction",
			"company_wallet.company_wallet.doctype.multi_authorization_rule.multi_authorization_rule.validate_day",
		],
		"on_submit": [
			"company_wallet.notification_settings.send_fcm_notification",
		],
	}
}
# Hook on document methods and events

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"company_wallet.notification_settings.process_offers_notifications",
	],
	# "cron": {
	# 		"* * * * *": [
	# 			"company_wallet.notification_settings.process_offers_notifications",
	# 		],
	# }
	"daily_long": [
		"company_wallet.company_wallet.doctype.wallet_company_transaction_log.wallet_company_transaction_log.create_account_statement_log"
	],
#	"weekly": [
#		"company_wallet.tasks.weekly"
#	],
#	"monthly": [
#		"company_wallet.tasks.monthly"
#	],
}

extend_bootinfo = [
	"company_wallet.company_wallet.doctype.action_confirm_message.action_confirm_message.load_boot_messages",
	"company_wallet.company_wallet.doctype.wallet_company_settings.wallet_company_settings.load_bulk_edit_child_table_settings",
]
# Testing
# -------

# before_tests = "company_wallet.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "company_wallet.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "company_wallet.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["company_wallet.utils.before_request"]
# after_request = ["company_wallet.utils.after_request"]

# Job Events
# ----------
# before_job = ["company_wallet.utils.before_job"]
# after_job = ["company_wallet.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"company_wallet.auth.validate"
# ]

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [{
				"name": ["in", [
					"Notification-custom_firebase_notification",
				]],
		}],
	},
	{
		"dt": "Letter Head",
		"filters": [{
				"name": ["in", [
					"WBP- Details",
					"WP"
				]],
		}],
	}
]

# Permissions
# -----------
# Permissions evaluated in scripted ways
permission_query_conditions = {
	"Wallet Bulk Payment": "company_wallet.custom_settings.get_permission_query",
	"Wallet Payment": "company_wallet.custom_settings.get_permission_query",
	"Wallet User": "company_wallet.custom_settings.get_permission_query",
	"Bulk Payment Template": "company_wallet.custom_settings.get_permission_query",
	"Wallet Payment Log": "company_wallet.custom_settings.get_permission_query",
	"Wallet Company": "company_wallet.custom_settings.get_permission_query_wallet_company"
}
has_permission = {
	"Wallet Bulk Payment": "company_wallet.custom_settings.has_permission",
	"Wallet Payment": "company_wallet.custom_settings.has_permission",
	"Wallet User": "company_wallet.custom_settings.has_permission",
	"Bulk Payment Template": "company_wallet.custom_settings.has_permission",
	"Wallet Payment Log": "company_wallet.custom_settings.has_permission",
	"Wallet Company": "company_wallet.custom_settings.has_permission"
}