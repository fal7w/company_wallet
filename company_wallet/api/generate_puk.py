import frappe
import pyotp
from frappe import _
from company_wallet.api.utils import unify_response


@unify_response()
def generate_puk(user):
	"""
	Generates a PUK (Personal Unlocking Key) for the user.
	:param user: The user for whom the PUK is generated.
	"""
	puk = pyotp.TOTP(pyotp.random_base32()).now()
	new_puk = frappe.new_doc("User Puk")
	new_puk.user = user
	new_puk.puk = puk
	new_puk.save()
	recipient_email = frappe.db.get_value("Wallet User", {"user": user}, "email")

	email_subject = _("Add New Device")
	email_content = _(f"Your PUK for new device is: {puk}.")

	if recipient_email:
		frappe.sendmail(
			recipients=recipient_email,
			subject=email_subject,
			message=email_content,
			send_priority=1,
			retry=3,
		)
	else:
		frappe.throw(_("Email address not found for Wallet User."))

	frappe.db.commit()  # nosemgrep
	frappe.msgprint(_("Check your mail inbox."))