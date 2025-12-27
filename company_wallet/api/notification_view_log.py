import frappe
from company_wallet.api.utils import unify_response
import frappe.client


@unify_response()
def notification_log(user=None):
    """
    Retrieves a list of notification logs for a given user.
    Args:
    user (str, optional): The username of the user. If not provided, the current user session will be used.
    Returns:
    list: A list of dictionaries containing the subject and email content of the notification logs.
    """
    user = frappe.session.user
    return frappe.client.get_list("Notification Log", fields=["subject", "email_content"], filters={"for_user": user})