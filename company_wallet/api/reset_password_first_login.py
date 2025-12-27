from company_wallet.custom_settings import FirstLoginError, find_user_by_identifier
import frappe
from frappe import STANDARD_USERS, _
from company_wallet.api.utils import unify_response
from frappe.utils.password import update_password


@unify_response(allow_guest=True)
def force_reset_password(user, new_password, old_password, device_id):
	"""
	Force reset password for a user.

	:param user: The user for whom the password is being reset.
	:type user: str
	:param new_password: The new password for the user.
	:type new_password: str
	:param old_password: The old password for the user.
	:type old_password: str
	:param device_id: The device ID of the user.
	:type device_id: str
	:return: True if the password is successfully reset, False otherwise.
	:rtype: bool
	:raises FirstLoginError: If the user is not the first login and cannot reset the password using this method.
	:raises FirstLoginError: If the device ID is not found for the user.
	:raises FirstLoginError: If the old password is incorrect.
	"""
	if user in STANDARD_USERS:
		frappe.throw(_("Not allowed to update standard user's password"))

	user = find_user_by_identifier(user)

	wallet_user = frappe.get_value("Wallet User", {"email": user}, ["first_login", "name", "user"], as_dict=True)
	
	user_device_id = frappe.get_value("User Device", {"user": user, "device_id": device_id}, "name")
	try:
		user_old_password = frappe.local.login_manager.check_password(user, old_password)

		if wallet_user and wallet_user.first_login and user_device_id and user_old_password:
			if new_password == old_password:
				frappe.throw(_("New password cannot be the same as the old password"))
			update_password(user, new_password)
			frappe.db.set_value("Wallet User", wallet_user.name, "first_login", 0)
			frappe.db.commit()
			return True
		
	except frappe.AuthenticationError:
			frappe.db.rollback()
			frappe.throw(_("Failed to update the password."), FirstLoginError)
	else:
		if not wallet_user or not wallet_user.first_login:
			frappe.throw(_("This is NOT your first login, and you cannot reset the password using this method."))
		if not user_device_id:
			frappe.throw(_("Device ID not found for this user! check it and try again."))
		if old_password != user_old_password:
			frappe.throw(_("Incorrect old password!"))
		return False