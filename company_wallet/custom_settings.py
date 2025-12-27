from datetime import timedelta
from company_wallet.company_wallet.doctype.wallet_company.wallet_company import get_user_wallet_company
import frappe
from frappe.utils.data import cint, now_datetime
from frappe import STANDARD_USERS, _


def get_permission_query(user=None):
	wallet_company = get_user_wallet_company(user)
	if wallet_company:
		return f"(`wallet_company` = '{wallet_company}')"


def get_permission_query_wallet_company(user=None):
	if not user:
		user = frappe.session.user
	wallet_user_company = frappe.db.get_value("Wallet User", {"email": user}, "wallet_company")
	if wallet_user_company:
		return f"(`company_name` = '{wallet_user_company}')"
	else:
		return

	
def has_permission(doc, ptype, user):
	wallet_company = get_user_wallet_company(user)
	system_roles = frappe.get_roles(user)
	if "System Manager" in system_roles:
		return True
	if wallet_company:
		if doc.get("doctype") == "Wallet Company":
			return doc.get("company_name") == wallet_company
		else:
			return doc.get("wallet_company") == wallet_company
	else:
		return None  # if System manager then access all docs
	

class FirstLoginError(frappe.AuthenticationError):
	http_status_code = 410


class UserDeviceIDError(frappe.ValidationError):
	http_status_code = 411


def on_login(login_manager):
	is_mobile_app = 'X-App-Login' in frappe.request.headers or frappe.form_dict.get('is_mobile_app')
	if is_mobile_app:
		add_user_device_id(login_manager.user, frappe.form_dict.get('device_id'))
		check_user_device_id(login_manager.user, frappe.form_dict.get('device_id'))
		if is_first_login(login_manager.user):
			frappe.throw(_("This is your first login, please login from mobile app"), exc=FirstLoginError)


def is_first_login(user):
	"""Check if the user is logging in for the first time based on the 'first_login' flag."""
	if not user:
		frappe.log_error(f"Non-existing user: {user}", "Login Error")
		return {"message": "User does not exist.", "success": False}
	
	first_login = frappe.db.get_value("Wallet User", {"email": user}, "first_login")
	return cint(first_login) == 1


def is_last_login(user):
	"""Check if the user is logging in for the first time based on the 'last_login' flag."""
	if not user:
		frappe.log_error(f"Non-existing user: {user}", "Login Error")
		return {"message": "User does not exist.", "success": False}
	
	last_login = frappe.db.get_value("User", user, "last_login")
	return last_login


def add_user_device_id(user, device_id):
	if not frappe.db.exists("User Device", {"user": user, "device_id": device_id}) and is_first_login(user):
		create_user_device(user, device_id)
	
	if frappe.form_dict.get('puk'):
		process_user_puk(user, device_id)


def create_user_device(user, device_id):
	user_device = frappe.new_doc("User Device")
	user_device.user = user
	user_device.device_name = frappe.form_dict.get('device_name') or user
	user_device.device_id = device_id
	user_device.device_token = frappe.form_dict.get('device_token')
	user_device.save(ignore_permissions=True)
	frappe.db.commit()


def process_user_puk(user, device_id):
	get_puk = frappe.db.get_value("User Puk", {"user": user}, "puk")
	if get_puk == frappe.form_dict.get('puk'):
		if not frappe.db.exists("User Device", {"user": user, "device_id": device_id}):
			create_user_device(user, device_id)


def check_user_device_id(user, device_id):
	if user not in STANDARD_USERS and not frappe.form_dict.get('puk'):
		if not frappe.db.exists("User Device", {"user": user, "device_id": device_id}):
			frappe.throw(_("Device ID not found for this user! check it and try again."), exc=UserDeviceIDError)


def add_user_device_token(user, device_id):
	user_device_id = frappe.db.exists("User Device", {"user": user, "device_id": device_id})
	if user_device_id:
		frappe.db.set_value("User Device", user_device_id, "device_token", frappe.form_dict.get('device_token'))
		

def find_user_by_identifier(identifier):
	user = frappe.db.get_value("User", {"full_name": identifier}, "name")
	if not user:
		user = frappe.db.get_value("User", {"email": identifier}, "name")
	if not user:
		user = frappe.db.get_value("User", {"mobile_no": identifier}, "name")
	return user
	

def check_login_attempts(doc, method=None):
	user = frappe.get_doc("User", doc.user)
	max_attempts = cint(frappe.db.get_single_value('Wallet Company Settings', 'allow_consecutive_login_attempts'))

	# Skip standard users and users without a wallet company
	if not user.enabled or not user.get('wallet_company') or user.name in STANDARD_USERS:
		return

	# Calculate the timestamp for 24 hours ago
	time_limit = now_datetime() - timedelta(hours=24)

	# Count the number of failed login attempts in the last 24 hours
	failed_attempts = frappe.get_all("Activity Log", filters={
		'user': doc.user,
		'creation': ['>=', time_limit],
		'operation': 'login',
		'status': 'Failed'
	})
	if len(failed_attempts) > max_attempts:
		user.db_set('enabled', 0)
		frappe.db.commit()
		frappe.throw(_("Your account has been disabled after {0} consecutive failed login attempts.").format(max_attempts))


def reset_login_attempts(user):
	time_limit = now_datetime() - timedelta(hours=24)
	frappe.db.delete("Activity Log", {"user": user, "creation": ['>=', time_limit], "operation": "login", "status": "Failed"})


def on_login_success(user):
	if user in STANDARD_USERS:
		reset_login_attempts(user)


def reset_user_login_attempts(doc, method=None):
	# Clear failed login attempts for the user in the last 24 hours
	time_limit = now_datetime() - timedelta(hours=24)
	frappe.db.delete("Activity Log", {"user": doc.name, "creation": ['>=', time_limit], "operation": "login", "status": "Failed"})
