# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.permissions import copy_perms


def after_install():
	add_wallet_company_to_session_defaults()
	create_payment_channel()
	# add_phone_validation_settings()
	create_remittance_providers()
	initials_currency_list()
	# set_role_profiles()
	add_wallet_company_field_to_user()
	# initialize_allowed_file_extensions()
	# add_default_version_url_settings()


def after_migrate():
	add_wallet_company_to_session_defaults()
	create_payment_channel()
	initials_currency_list()
	set_role_profiles()
	create_remittance_providers()
	add_phone_validation_settings()
	# initialize_email_account()
	initialize_allowed_file_extensions()
	add_default_settings()
	make_email_content_translatable()
	set_permissions()


def add_wallet_company_field_to_user():
	create_custom_field("User", {
		"fieldname": "wallet_company",
		"label": "Wallet Company",
		"fieldtype": "Link",
		"options": "Wallet Company",
		"insert_after": "username",
		"read_only": 1,
		"no_copy": 1
	})


def create_remittance_providers():
	providers_dict = {
		"WeCash": {"provider_id": "14000", "service_type": "Wallet Transfer"},
		"Al-emtiyaz": {"provider_id": "16000", "service_type": "Remittance"},
		"Al-najm": {"provider_id": "15000", "service_type": "Remittance"},
		"YemenExpress": {"provider_id": "17000", "service_type": "Remittance"},
	}
	
	for provider_name, details in providers_dict.items():
		existing_provider = frappe.db.exists('Remittance Provider', {'remittance_provider_name': provider_name})
		if not existing_provider:
			new_provider = frappe.get_doc({
				"doctype": "Remittance Provider",
				"remittance_provider_name": provider_name,
				"remittance_provider_id": details['provider_id'],
				"service_type": details['service_type']
			})
			new_provider.save(ignore_permissions=True)


def create_payment_channel():
	channel_dict = {
		"Wallet Transfer": "40",
		"Remittance": "49",
	}

	for trans_type, trans_id in channel_dict.items():
		existing_provider = frappe.db.exists('Payment Channel', {'transaction_type': trans_type})
		if not existing_provider:
			new_type = frappe.get_doc({
				"doctype": "Payment Channel",
				"transaction_type": trans_type,
				"transaction_id": trans_id
			})
			new_type.save(ignore_permissions=True)


def ensure_default_settings(settings_doc, default_values):
	for setting, default_value in default_values.items():
		if not getattr(settings_doc, setting, None):
			setattr(settings_doc, setting, default_value)


def ensure_child_docs(settings_doc, child_doctype, child_table_field, child_entries, unique_field):
	has_changes = False
	for entry in child_entries:
		existing_entry = frappe.get_all(
			child_doctype,
			filters={
				unique_field: entry[unique_field],
				"parent": settings_doc.name,
				"parenttype": settings_doc.doctype,
				"parentfield": child_table_field
			}
		)
		if not existing_entry:
			settings_doc.append(child_table_field, entry)
			has_changes = True
	
	if has_changes:
		settings_doc.save(ignore_permissions=True)


def add_phone_validation_settings():
	settings_doc = frappe.get_single("Wallet Company Settings")
	ensure_default_settings(settings_doc, {"phone_length": 9})
	ensure_default_settings(settings_doc, {"default_wallet_provider": "WeCash"})

	phone_prefixes = [{"prefix": prefix} for prefix in ["77", "78", "73", "71", "70"]]
	for prefix in phone_prefixes:
		prefix["parentfield"] = "services_setting_phone_prefix"
	ensure_child_docs(settings_doc, "Phone Prefix Settings", "services_setting_phone_prefix", phone_prefixes, "prefix")

	settings_doc.save(ignore_permissions=True)


def initials_currency_list():
	# set default currency
	default_currencies = ['USD', 'SAR', 'YER']
	currencies = frappe.get_all("Currency", fields=["name"])
	for currency in currencies:
		currency_default = frappe.get_doc("Currency", currency.name)
		if currency.name in default_currencies:
			if not currency_default.enabled:
				currency_default.db_set("enabled", True)
		else:
			currency_default.db_set("enabled", False)


def set_role_profiles():
	"""
	Set role profiles based on the predefined mappings in the 'role_profiles' dictionary.
	Check if each Role Profile already exists, create it if it doesn't, 
	and add the corresponding roles to it.
	"""
	role_profiles = {
		"Wallet Main User": {"Wallet Checker", "Dashboard Manager", "Accounts Manager", "Accounts User", "Wallet Reviewer", "Wallet Admin", "Wallet User Role Profile", "Prepared Report User"},
		"Wallet Reviewer": {"Wallet Reviewer", "Prepared Report User"},
		"Wallet Checker": {"Wallet Checker", "Accounts User", "Accounts Manager"},
		"Wallet Maker": {"Wallet Maker", "Accounts User", "Accounts Manager"},
	}

	for profile_name, roles_set in role_profiles.items():
		if not frappe.get_all("Role Profile", or_filters={"name": profile_name, "role_profile": profile_name}, limit=1):
			new_profile_doc = frappe.get_doc({
				"doctype": "Role Profile",
				"role_profile": profile_name,
			})
			for role_name in roles_set:
				if frappe.db.exists("Role", {"name": role_name}):
					new_profile_doc.append("roles", {
						"role": role_name
					})
			new_profile_doc.save(ignore_permissions=True, ignore_version=True)


def add_wallet_company_to_session_defaults():
	default_settings = frappe.get_single("Session Default Settings")
	if not next(filter(lambda i: i.ref_doctype == "Wallet Company", default_settings.session_defaults), None):  # nosemgrep
		default_settings.append("session_defaults", {"ref_doctype": "Wallet Company"})
		default_settings.save(ignore_permissions=True)


def initialize_email_account():
	data = {
		"name": "Fintechsys",
		"email_id": "r.dalal@fintechsys.net",
		"email_account_name": "Fintechsys",
		"auth_method": "Basic",
		"password": "fp&StuAC=R2R",
		"awaiting_password": 0,
		"ascii_encode_password": 1,
		"login_id_is_different": 0,
		"enable_incoming": 1,
		"default_incoming": 1,
		"use_imap": 1,
		"use_ssl": 1,
		"use_starttls": 0,
		"email_server": "mail.fintechsys.net",
		"incoming_port": "993",
		"attachment_limit": 25,
		"email_sync_option": "UNSEEN",
		"initial_sync_count": "250",
		"create_contact": 1,
		"notify_if_unreplied": 0,
		"unreplied_for_mins": 30,
		"enable_outgoing": 1,
		"use_ssl_for_outgoing": 1,
		"smtp_server": "mail.fintechsys.net",
		"smtp_port": "465",
		"default_outgoing": 1,
		"send_unsubscribe_message": 1,
		"track_email_status": 1,
		"uidnext": 2764,
		"doctype": "Email Account",
		"imap_folder": [{
			"name": "d9708cdcce",
			"folder_name": "INBOX",
			"uidvalidity": "1654421549",
			"uidnext": "2762",
			"parent": "Fintechsys",
			"parentfield": "imap_folder",
			"parenttype": "Email Account",
			"doctype": "IMAP Folder"
			}],
			}
	
	if frappe.db.exists('Email Account', data.get('email_id')):
		return 'Email Account with this ID already exists.'
	
	email_account = frappe.new_doc('Email Account')
	
	email_account.update({
		'email_id': data.get('email_id'),
		'email_account_name': data.get('email_account_name'),
		'auth_method': data.get('auth_method'),
		'password': data.get('password'),
		'enable_incoming': data.get('enable_incoming'),
		'default_incoming': data.get('default_incoming'),
		'use_imap': data.get('use_imap'),
		'use_ssl': data.get('use_ssl'),
		'email_server': data.get('email_server'),
		'incoming_port': data.get('incoming_port'),
		'attachment_limit': data.get('attachment_limit'),
		'email_sync_option': data.get('email_sync_option'),
		'initial_sync_count': data.get('initial_sync_count'),
		'enable_outgoing': data.get('enable_outgoing'),
		'use_ssl_for_outgoing': data.get('use_ssl_for_outgoing'),
		'smtp_server': data.get('smtp_server'),
		'smtp_port': data.get('smtp_port'),
		'default_outgoing': data.get('default_outgoing'),
		'track_email_status': data.get('track_email_status'),
		"create_contact": data.get("create_contact"),
		"unreplied_for_mins": data.get("unreplied_for_mins"),
		"send_unsubscribe_message": data.get("send_unsubscribe_message")
	})
	
	if 'imap_folder' in data and isinstance(data['imap_folder'], list):
		for folder in data['imap_folder']:
			email_account.append('imap_folder', {
				'folder_name': folder.get('folder_name'),
				'uidvalidity': folder.get('uidvalidity'),
				'uidnext': folder.get('uidnext')
			})
	
	email_account.save(ignore_permissions=True)


def initialize_allowed_file_extensions():
	settings_doc = frappe.get_single("Wallet Company Settings")
	ensure_default_settings(settings_doc, {"allowed_file_extensions": "gif\ncsv\njpeg\njpg\npng\ndocx\npdf\ndoc\nxlsx\nxls\nzip\nodt\nods\nodp"})
	settings_doc.save(ignore_permissions=True)


def add_default_settings():
	settings_doc = frappe.get_single("Wallet Company Settings")
	ensure_default_settings(settings_doc, {"version": "1.0.0"})
	ensure_default_settings(settings_doc, {"version_matched_number": "1"})
	ensure_default_settings(settings_doc, {"url_store": "https://fintechsys.net"})
	ensure_default_settings(settings_doc, {"allow_consecutive_login_attempts": 3})
	ensure_default_settings(settings_doc, {"allow_login_after_fail": 10})
	ensure_default_settings(settings_doc, {"recipient_name_length": 4})
	settings_doc.save(ignore_permissions=True)


def make_email_content_translatable():
	if not frappe.db.exists('Property Setter', {
		'doctype_or_field': 'DocField',
		'doc_type': 'Notification Log',
		'field_name': 'email_content',
		'property': 'translatable'
	}):
		property_setter = frappe.get_doc({
			'doctype': 'Property Setter',
			'doctype_or_field': 'DocField',
			'doc_type': 'Notification Log',
			'field_name': 'email_content',
			'property': 'translatable',
			'value': 1,
			'property_type': 'Check'
		})
		property_setter.save()


def set_permissions():
	"""Set permissions for User and Role Profile doctypes for Wallet Admin role."""
	role = "Wallet Admin"
	add_permission("User", role, {"select": 1, "read": 1, "write": 1, "create": 1, "delete": 0})
	add_permission("Role Profile", role, {"select": 1, "read": 1, "write": 0, "create": 0, "delete": 0})
	add_permission("Role", role, {"select": 1, "read": 1, "write": 0, "create": 0, "delete": 0})


def add_permission(doctype_name, role, permissions):
	"""Set or update permissions for a specific role on a given doctype."""
	try:
		doctype = frappe.get_doc("DocType", doctype_name)
		existing_perm = frappe.get_all("DocPerm", limit=1, filters={
							"parent": doctype_name,
							"role": role,
							"parenttype": "DocType",
							"parentfield": "permissions"})
		if existing_perm:
			for key, value in permissions.items():
				# frappe.db.set_value("DocPerm", existing_perm[0].name, key, value)
				perm = frappe.get_doc({
					"doctype": "DocPerm",
					"role": role,
					key: value,
					"parent": doctype_name,
					"parenttype": "DocType",
					"parentfield": "permissions"
				})
				perm.insert(ignore_permissions=True)
				frappe.log_error(
					message=f"Updated permissions for role '{role}' on doctype '{doctype_name}'.",
					title=f"Permission Update: {role} on {doctype_name}")
		else:
			doctype.append("permissions", {"role": role, **permissions})
			frappe.log_error(
				message=f"Added permissions for role '{role}' on doctype '{doctype_name}'.",
				title=f"Permission Addition: {role} on {doctype_name}"
			)
		doctype.save(ignore_permissions=True)
		frappe.clear_cache(doctype=doctype_name)
		copy_perms(doctype_name)
	except frappe.DoesNotExistError:
		frappe.log_error(
			message=f"Doctype '{doctype_name}' does not exist.",
			title=f"Error: Doctype {doctype_name} Not Found"
		)
	except Exception:
		frappe.log_error(
			message=frappe.get_traceback(),
			title=f"Error setting permissions for {doctype_name}"
		)
