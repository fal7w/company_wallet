# Copyright (c) 2024, fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_link_to_form
from company_wallet.connect_sdk import init_default_sdk, CompanySDK

wallet_company_doctype = "Wallet Company"


class CreateThroughApiError(frappe.ValidationError): pass


class WalletCompany(Document):
	def validate(self):
		self.validate_wallet_identifier()
		if self.has_value_changed("disabled"):
			self.enable_disable_wallet_users()

	def validate_wallet_identifier(self):
		if not self.is_new() and not self.flags.allow_change_wallet_identifier and self.has_value_changed("wallet_identifier"):
			frappe.throw(_("Wallet Identifier can't be changed"))
	
	def enable_disable_wallet_users(self):
		wallet_users = frappe.get_all("Wallet User", filters={"wallet_company": self.name})
		for wallet_user in wallet_users:
			frappe.db.set_value("User", wallet_user.get("name"), "enabled", not self.disabled)
			frappe.db.set_value("Wallet User", wallet_user.get("name"), "disabled", self.disabled)

	def before_insert(self):
		if not self.flags.create_through_api:
			frappe.throw(_("Not allowed to create {doctype} directly, create through api"), exc=CreateThroughApiError)

		self._create_on_network()

	def _create_on_network(self):
		self.validate_unique_company_name()
		sdk = init_default_sdk(CompanySDK)
		res = sdk.create_company(self.wallet_identifier, _("Error Creating Wallet Company on network"))
		data = res.json.get("data", {})
		self.path = data.get("secret_path")
		self.token = data.get("token")
		self.password = data.get("password")

	def validate_unique_company_name(self):
		if frappe.db.exists(self.doctype, {"company_name": self.company_name}):
			frappe.throw(_("Company Name already exists"))

	def update_auth_token(self, show_message=True):
		sdk = init_default_sdk(CompanySDK, self)
		res = sdk.update_token(self.get_password("password"), _("Error Updating Auth Token on network"))
		data = res.json.get("data")
		if data and data.get("token"):
			self.token = data.get("token")
			self.save(ignore_permissions=True)
			frappe.db.commit()
			if show_message:
				frappe.msgprint(_("Token Updated successfully"))
		return True
	

@frappe.whitelist()
def create_company_with_user(company_name, company_description, wallet_identifier, org_id, user_mobile_no, user_firstname, user_email, creating_date_from_wallet_provider, company_prefix, user_lastname=None):
	try:
		user = frappe.get_doc({
			"doctype": "Wallet User",
			"mobile_no": user_mobile_no,
			"first_name": user_firstname,
			"last_name": user_lastname,
			"type": "Main User",
			"wallet_identifier": wallet_identifier,
			"email": user_email,
			"role": frappe.db.get_single_value("Wallet Company Settings", "main_user_role"),
			"first_login": 1
			})

		user.flags.first_login = True
		user.insert(ignore_mandatory=True)

		company = frappe.get_doc({
			"doctype": wallet_company_doctype,
			"company_name": company_name,
			"description": company_description,
			"wallet_identifier": wallet_identifier.replace(" ", ""),
			"organization_id": org_id.replace(" ", ""),
			"creating_date_from_wallet_provider": creating_date_from_wallet_provider,
			"company_prefix": company_prefix,
			"wallet_provider": frappe.db.get_single_value("Wallet Company Settings", "default_wallet_provider"),
			})

		company.flags.create_through_api = True
		company.insert(ignore_mandatory=True)
		company.db_set("main_user", user.name)
		user.db_set("wallet_company", company.name)
		company.save()
		user.save()
		return company
	except Exception as e:
		frappe.db.rollback()
		frappe.db.commit()
		frappe.throw(_("Error: {0}").format(str(e)))


@frappe.whitelist()
def update_api_user(wallet_company, wallet_identifier, org_id, username, password):
	configration_doctype = "Company Wallet Configration"
	role_allowed = frappe.db.get_single_value(configration_doctype, "role_allowed_to_update_api_wallet")
	if role_allowed:
		frappe.only_for(role_allowed)
	else:
		meta = frappe.get_meta(configration_doctype)
		frappe.throw(_("Set {field} in {doctype} first").format(
			field=frappe.bold(_(meta.get_label("role_allowed_to_update_api_wallet"))),
			doctype=frappe.bold(_(frappe.utils.get_link_to_form(configration_doctype, configration_doctype)))
		))

	wallet_company = frappe.get_doc(wallet_company_doctype, wallet_company)
	sdk = init_default_sdk(CompanySDK, wallet_company)
	sdk.update_api_user(wallet_identifier, org_id, username, password, _("Error Updating API User on network"))
	wallet_company.wallet_identifier = wallet_identifier
	wallet_company.organization_id = org_id
	wallet_company.flags.allow_change_wallet_identifier = True
	wallet_company.save()


@frappe.whitelist()
def update_wallet_password(wallet_company, password):
	sdk = init_default_sdk(CompanySDK, wallet_company)
	sdk.update_wallet_password(password, _("Error Updating Wallet User on network"))


@frappe.whitelist()
def update_auth_token(wallet_company, show_message=True):
	wallet_company: WalletCompany = frappe.get_doc(wallet_company_doctype, wallet_company)
	return wallet_company.update_auth_token(show_message)


def validate_disabled_company(doc, method=None):
	wallet_company = doc.get("wallet_company")
	if doc.doctype == "Wallet User" and not doc.has_value_changed(wallet_company):
		if doc.meta.has_field("wallet_company") and wallet_company:
			disabled = frappe.db.get_value(wallet_company_doctype, wallet_company, "disabled")
			if disabled:
				frappe.throw(_("Wallet Company {0} is disabled").format(frappe.bold(get_link_to_form(wallet_company_doctype, wallet_company))))


def set_user_wallet_company(doc, method=None):
	wallet_company = get_user_wallet_company()
	if wallet_company:
		doc.wallet_company = wallet_company


def get_user_wallet_company(user=None):
	if not user:
		user = frappe.session.user
	if user:
		wallet_company = frappe.db.get_value("Wallet User", {"user": user}, "wallet_company")
		return wallet_company


def validate_wallet_company(doc, method=None):
	wallet_company_doc = doc.get("wallet_company")
	wallet_company_user = frappe.db.get_value("Wallet User", {"user": frappe.session.user}, "wallet_company")
	if wallet_company_doc != wallet_company_user:
		frappe.throw(_("Wallet User not belong to Wallet Company {0}").format(frappe.bold(get_link_to_form(wallet_company_doctype, wallet_company_doc))))


@frappe.whitelist()
def copy_paths(docname):
	if docname:
		frappe.only_for("System Manager")
		wallet_company = frappe.get_doc("Wallet Company", docname)
		if wallet_company.get("path"):
			path_copy = wallet_company.get_password("path")
			return path_copy
