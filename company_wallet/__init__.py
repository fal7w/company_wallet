from __future__ import unicode_literals
import frappe
from frappe.utils import cint

__version__ = '0.0.1'


def on_session_creation(login_manager):
	from company_wallet.api.login_data import get_roles_list, get_wallet_company_info, get_wallet_user_info
	from company_wallet.custom_settings import on_login_success, add_user_device_token
	from company_wallet.company_wallet.doctype.wallet_company_settings.wallet_company_settings import validate_app_version
	on_login_success(login_manager.user)
	is_mobile_app = 'X-App-Login' in frappe.request.headers or frappe.form_dict.get('is_mobile_app')
	if is_mobile_app:
		validate_app_version()

	if frappe.form_dict.get('use_jwt') and cint(frappe.form_dict.get('use_jwt')):
		add_user_device_token(login_manager.user, frappe.form_dict.get('device_id'))
		frappe.local.response['user_role_profile_details'] = get_roles_list(user=login_manager.user)
		frappe.local.response['company_info'] = get_wallet_company_info(user=login_manager.user)
		frappe.local.response['user_info'] = get_wallet_user_info(user=login_manager.user)
		if frappe.local.response['company_info']:
			frappe.defaults.set_user_default("wallet_company", frappe.local.response['company_info']['company_name'])