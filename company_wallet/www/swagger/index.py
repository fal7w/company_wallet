# Copyright (c) 2021, mituldavid and Contributors
# See license.txt
import os.path
import frappe
from company_wallet.generate_swagger import generate_openapi_spec
import json
import frappe.sessions

no_cache = 1


def get_context(context):
	openai_file_path = frappe.get_app_path("company_wallet", *frappe.get_hooks("CW_OPENAPI_OUTPUT_FILE"))
	openapi_spec = None
	try:
		with open(openai_file_path, "r") as openai_file:
			openapi_spec = openai_file.read()
	except:
		api_directory = frappe.get_app_path("company_wallet", *frappe.get_hooks("CW_OPENAPI_DIR"))
		openapi_spec = json.dumps(generate_openapi_spec(api_directory))

	if openapi_spec:
		context.openapi_spec = frappe.render_template(openapi_spec, {"csrf_token": frappe.sessions.get_csrf_token()})
	return context
