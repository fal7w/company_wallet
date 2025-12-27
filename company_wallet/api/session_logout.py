import frappe
from company_wallet.api.utils import unify_response
from frappe.sessions import clear_sessions


@unify_response()
def session_logout(user):
	"""
	Logs out a user session and clears all related sessions from the system.
	Args:
		user (str): The user to be logged out.
	Returns:
		dict: Response indicating success or failure of the logout operation.
	"""
	user = find_user_by_identifier(user)
	if not user:
		frappe.log_error(f"Attempted to log out non-existing user: {user}", "Logout Error")
		return {"message": "User does not exist.", "success": False}

	if frappe.session.user != user and not frappe.session.user == "Administrator":
		frappe.log_error(f"Unauthorized logout attempt by {frappe.session.user} for user {user}", "Logout Error")
		return {"message": "Unauthorized logout attempt.", "success": False}

	try:
		frappe.local.login_manager.logout(user=user)
		clear_sessions(user)

		frappe.logger().info(f"User {user} logged out successfully.")
		return {"message": "Logged out successfully.", "success": True}
	except Exception as e:
		frappe.log_error(f"Error during logout for user {user}: {str(e)}", "Logout Error")
		return {"message": "Failed to log out due to an internal error.", "success": False}


def find_user_by_identifier(identifier):
	user = frappe.db.get_value("User", {"full_name": identifier}, "name")
	if not user:
		user = frappe.db.get_value("User", {"email": identifier}, "name")
	if not user:
		user = frappe.db.get_value("User", {"mobile_no": identifier}, "name")
	return user