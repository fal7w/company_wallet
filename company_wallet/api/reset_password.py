import frappe
from .utils import unify_response
from company_wallet.company_wallet.doctype.wallet_user.wallet_user import (
	generate_otp_and_send_mail,
	set_new_password
)


@unify_response(allow_guest=True)
def reset_password(user):
	"""
	Reset the password for a user.

	:param user: The user for whom the password is being reset.
	:type user: str
	:return: The result of generating and sending an OTP to the user's email.
	:rtype: bool
	"""
	return generate_otp_and_send_mail(user)


@unify_response(allow_guest=True)
def set_new_password_otp(user, otp, new_password):
	"""
	Set a new password for a user using an OTP.

	:param user: The user for whom the password is being set.
	:type user: str
	:param otp: The one-time password for password reset.
	:type otp: str
	:param new_password: The new password for the user.
	:type new_password: str
	:return: The result of setting the new password for the user.
	:rtype: bool
	"""
	return set_new_password(user, otp, new_password)