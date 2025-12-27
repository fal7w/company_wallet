import frappe
from .utils import unify_response


@unify_response()
def confirm_password_transaction(password):
    """
    Confirm a password transaction for the current user.
    Args:
        password (str): The password to be confirmed.
    Returns:
        bool: True if the password is confirmed successfully, False otherwise.
    """
    user = frappe.session.user
    frappe.local.login_manager.check_password(user, password)
    return True