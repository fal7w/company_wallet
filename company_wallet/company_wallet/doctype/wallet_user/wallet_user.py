# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import cstr
from frappe.utils.data import add_to_date, cint, get_url_to_form, now, now_datetime
import frappe.defaults
from frappe.utils.password import update_password
import pyotp


class DiffrentUserWalletCompanyError(frappe.LinkValidationError): pass


class WalletUser(Document):
	def validate(self):
		self.validate_wallet_company()
		self.set_user_type()
		# self.set_user_email()
		self.set_fullname()
		self.validate_phone()
		if self.has_value_changed("disabled"):
			self.enable_disable_user()

	def validate_phone(self):
		self._validate_phone(cstr(self.get("mobile_no")))

	def _validate_phone(self, phone):
		setting_doc = frappe.get_single("Wallet Company Settings")
		phone_length = cint(setting_doc.phone_length)

		if not setting_doc.services_setting_phone_prefix:
			url = get_url_to_form(setting_doc.doctype, setting_doc.name)
			error_message = _("There is no phone prefix in <a href='{url}' target='_blank'>{name}</a> doctype").format(url=url, name=setting_doc)
			frappe.throw(error_message)
		if len(phone) != phone_length:
			frappe.throw(_("Phone number length must be {phone_length} numbers").format(
				phone_length=phone_length))

		prefixes = tuple(cstr(p.prefix) for p in setting_doc.services_setting_phone_prefix)
		if not phone.startswith(prefixes):
			frappe.throw(_("Phone number must start with {prefixs}").format(prefixs=prefixes))

	def validate_wallet_company(self):
		creator_wallet_company = frappe.db.get_value("Wallet User", {"user": frappe.session.user}, "wallet_company")
		if self.wallet_company and creator_wallet_company and (self.wallet_company != creator_wallet_company):
			frappe.throw(_("User can't be on different Wallet Company {wallet_company} from creater's wallet company {creator_wallet_company}").format(
					wallet_company=frappe.bold(self.wallet_company),
					creator_wallet_company=frappe.bold(creator_wallet_company),
				),
				exc=DiffrentUserWalletCompanyError
			)
		elif creator_wallet_company:
			self.wallet_company = creator_wallet_company

	def autoname(self):
		self.name = self.email

	def enable_disable_user(self):
		frappe.db.set_value("User", self.user, "enabled", not self.disabled)
		
	def set_user_type(self):
		if self.wallet_company:
			company_main_user = frappe.db.get_value("Wallet Company", self.wallet_company, "main_user")
			if company_main_user == self.name:
				self.type = "Main User"
			else:
				self.type = "Sub User"
		else:
			self.type = ""

	def set_fullname(self):
		self.full_name = self.first_name
		if self.last_name:
			self.full_name += " " + self.last_name

	def before_insert(self):
		self.first_login = True

	def set_user_module_profile(self):
		module_profile = frappe.db.get_single_value("Wallet Company Settings", "module_profile")
		if module_profile:
			frappe.set_value("User", self.user, "module_profile", module_profile)

	def after_insert(self):
		user_data = self._get_user_data()
		try:
			user = frappe.get_doc(user_data)
			user.insert(ignore_permissions=True, ignore_mandatory=True)
			self.db_set("user", user.name, update_modified=False)
			
		except Exception:
			self.db_set("user", self.email, update_modified=False)

	def on_update(self):
		user_data = self._get_user_data()
		user = frappe.get_doc("User", self.user)
		if "email" in user_data and user_data["email"] != user.name:
			new_email = user_data["email"]
			self.rename(new_email)
			renamed = frappe.rename_doc("User", user.name, new_email)  # nosemgrep
			self.db_set("user", renamed, update_modified=False)
			user = frappe.get_doc("User", renamed)
		user.update(user_data)
		user.save(ignore_permissions=True)  # nosemgrep
		on_update_user_doctype(self, method=None)
		self.set_user_module_profile()

	def _get_user_data(self):
		exclude_fields = [
			"name", "modified", "modified_by",
			"idx", "docstatus", "owner", "creation",
			"type", "wallet_company",
			]
		user_data = {k: v for k, v in self.as_dict().items() if k not in exclude_fields}
		user_data["role_profile_name"] = user_data.pop("role", None)
		user_data["doctype"] = "User"
		user_data["send_welcome_email"] = 0
		return user_data


def on_update_user_doctype(wallet_user: Document, method=None):
	if wallet_user.get("wallet_company"):
		pref_employee = wallet_user.get_doc_before_save()
		if pref_employee and pref_employee.get("wallet_company") != wallet_user.get("wallet_company"):
			remove_wallet_company_perm(pref_employee.get("user"), pref_employee.get("wallet_company"))

		add_wallet_company_perm(wallet_user.get("user"), wallet_user.get("wallet_company"))
		if wallet_user.get("user"):
			frappe.db.set_value("User", wallet_user.get("user"), "wallet_company", wallet_user.get("wallet_company"))
			frappe.defaults.set_user_default("wallet_company", wallet_user.get("wallet_company"), wallet_user.user)


def remove_wallet_company_perm(user, wallet_company):
	if user and wallet_company:
		frappe.db.delete("User Permission", {
			'user': user,
			'allow': 'Wallet Company',
			'for_value': wallet_company,
		})


def add_wallet_company_perm(user, wallet_company):
	if user and wallet_company:
		perm = frappe.db.exists("User Permission", {
			'user': user,
			'allow': 'Wallet Company',
			'for_value': wallet_company,
		})
		if perm:
			perm = frappe.get_doc("User Permission", perm)
		else:
			perm = frappe.get_doc({
				'doctype': 'User Permission',
				'user': user,
				'allow': 'Wallet Company',
				'for_value': wallet_company,
			})

		frappe.db.set_value("User Permission", {'user': user, 'allow': 'Wallet Company', 'is_default': 1,"name":["!=",perm.name]}, "is_default", 0)
		perm.is_default = 1
		perm.save(ignore_permissions=True)


@frappe.whitelist()
def generate_otp_and_send_mail(user=None, email=None):
	otp = pyotp.TOTP(pyotp.random_base32()).now()

	wallet_user_name = frappe.db.get_value("Wallet User", {"user": user}, "name")

	if wallet_user_name:
		frappe.db.set_value("Wallet User", wallet_user_name, "otp", otp)
		frappe.db.set_value("Wallet User", wallet_user_name, "otp_expiry_time", add_to_date(now(), minutes=5))
	else:
		frappe.throw(_("Wallet User not found for the specified user."))

	update_password(user, otp, logout_all_sessions=True)

	email_subject = _("Reset Password OTP")
	email_content = _(f"Your OTP for reset password is: {otp}. It will expire in 5 minutes!")
	recipient_email = frappe.db.get_value("Wallet User", wallet_user_name, "email") or email

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


@frappe.whitelist()
def set_new_password(user, otp, new_password):
	wallet_user = frappe.get_doc("Wallet User", {"user": user})

	if wallet_user.otp == otp and now_datetime() <= wallet_user.otp_expiry_time:

		frappe.db.set_value("Wallet User", wallet_user.name, "otp", None)
		frappe.db.set_value("Wallet User", wallet_user.name, "otp_expiry_time", None)

		update_password(user, new_password, logout_all_sessions=True)
		
		frappe.db.commit()  # nosemgrep
		frappe.msgprint(_("Password set successfully."))

	else:
		frappe.throw(_("Invalid OTP or OTP has expired"))


@frappe.whitelist()
def initialize_password(user):
	wallet_user = frappe.get_doc("Wallet User", {"user": user})
	if wallet_user.first_login:
		pwd = pyotp.TOTP(pyotp.random_base32()).now()
		try:
			update_password(user, pwd, logout_all_sessions=True)

			frappe.db.commit()  # nosemgrep

			email_subject = _("Initial Password For {0}").format(user)
			email_content = _("Your Initial Password: {0}, Please change your password after login").format(frappe.bold(pwd))
			frappe.sendmail(
				recipients=wallet_user.name,
				subject=email_subject,
				message=email_content,
				send_priority=1,
				now=True,
				retry=3,
			)

			frappe.msgprint(_("Check your mail inbox."))

		except Exception:
			frappe.throw(_("Failed to update the password or send mail."))