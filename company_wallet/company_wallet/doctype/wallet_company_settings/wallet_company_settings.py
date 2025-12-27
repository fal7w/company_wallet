# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import STANDARD_USERS, _
import frappe.defaults
from frappe.model.document import Document
from frappe.utils.data import cint


class WalletCompanySettings(Document):
	def validate(self):
		self.validate_prefix_duplicate()
		self.link_company_with_system_settings()
		self.link_company_logo_with_website_settings()
		self.link_module_profile()

	def link_company_logo_with_website_settings(self):
		website_settings = frappe.get_single("Website Settings")
		website_settings.app_name = self.app_name
		website_settings.app_logo = self.app_logo
		website_settings.banner_image = self.banner_image
		website_settings.splash_image = self.splash_image
		website_settings.favicon = self.favicon
		website_settings.save()

	def link_module_profile(self):
		module_profile = self.module_profile
		if module_profile:
			wallet_users = frappe.get_all("Wallet User", filters={"user": ["!=", ""], "disabled": 0}, fields=["user"])
			for user in wallet_users:
				try:
					frappe.set_value("User", user.user, "module_profile", module_profile)
				except Exception as e:
					frappe.log_error(_("Error in link user with module profile"), e)
					continue			

	def validate_prefix_duplicate(self):
		"""
		Validate if there are any duplicate values in the "doc_type" column of the doctypes child table.
		Raises:
			frappe.ValidationError: If duplicate entries are found in the child table.
		"""
		child_table_values = {}
		duplicates_found = False

		# Iterate through each row of the child table
		for idx, row in enumerate(self.services_setting_phone_prefix, start=1):
			key = row.prefix

			# Check if the key value already exists in the dictionary
			if key in child_table_values:
				duplicates_found = True
				child_table_values[key].append(idx)
			else:
				child_table_values[key] = [idx]

		# Collect the duplicate row numbers
		duplicated_row_numbers = [row_numbers for row_numbers in child_table_values.values() if len(row_numbers) > 1]
		duplicated_row_numbers = [row_number for row_numbers in duplicated_row_numbers for row_number in row_numbers]

		# Display an error message with the duplicated row numbers
		if duplicates_found and duplicated_row_numbers:
			error_message = _("Duplicate entries found in the child table at row(s): {rows}").format(
				rows=frappe.bold(", ".join(str(row_number) for row_number in duplicated_row_numbers))
			)
			frappe.throw(error_message)

	def on_update(self):
		frappe.db.set_default("currency", self.default_currency)
		return frappe.defaults.get_defaults()
	
	def link_company_with_system_settings(self):
		system_settings = frappe.get_single("System Settings")
		system_settings.apply_strict_user_permissions = self.apply_strict_user_permissions
		system_settings.session_expiry_idle_timeout = self.session_expiry_idle_timeout
		system_settings.allow_only_one_session_per_user = self.allow_only_one_session_per_user
		system_settings.disable_document_sharing = self.disable_document_sharing
		system_settings.allow_login_using_mobile_number = self.allow_login_using_mobile_number
		system_settings.allow_login_using_user_name = self.allow_login_using_user_name
		system_settings.login_with_email_link = self.login_with_email_link
		system_settings.login_with_email_link_expiry_in_minutes = self.login_with_email_link_expiry_in_minutes
		system_settings.enable_password_policy = self.enable_password_policy
		system_settings.minimum_password_score = self.minimum_password_score
		system_settings.allow_guests_to_upload_files = self.allow_guests_to_upload_files
		system_settings.force_web_capture_mode_for_uploads = self.force_web_capture_mode_for_uploads
		system_settings.strip_exif_tags_from_uploaded_images = self.strip_exif_tags_from_uploaded_images
		system_settings.allowed_file_extensions = self.allowed_file_extensions
		system_settings.enable_two_factor_auth = self.enable_two_factor_auth
		if self.enable_two_factor_auth:
			system_settings.bypass_2fa_for_retricted_ip_users = self.bypass_2fa_for_retricted_ip_users
			system_settings.bypass_restrict_ip_check_if_2fa_enabled = self.bypass_restrict_ip_check_if_2fa_enabled
			system_settings.two_factor_method = self.two_factor_method
			system_settings.lifespan_qrcode_image = self.lifespan_qrcode_image
			system_settings.otp_issuer_name = self.otp_issuer_name
		system_settings.save(ignore_permissions=True)


@frappe.whitelist()
def validate_app_version():
	user = frappe.session.user
	if user not in STANDARD_USERS:
		app_version = frappe.request.headers.get("App-Version")
		if not app_version:
			frappe.throw(_("App version is required"))

		system_settings = frappe.get_single("Wallet Company Settings")
		minimum_version_no = system_settings.version_matched_number

		if cint(app_version) < cint(minimum_version_no):
			url_store = system_settings.url_store
			frappe.throw(_("Your app version {0} is too old. Please update the app. {1}").format(app_version, url_store), exc=frappe.ValidationError)
		else:
			frappe.local.response["app_version"] = str(app_version)
			frappe.local.response["url_store"] = system_settings.url_store
		

def load_bulk_edit_child_table_settings(bootinfo):
	export_child_table_format = get_bulk_edit_child_table_settings()
	bootinfo.export_child_table_format = export_child_table_format


def get_bulk_edit_child_table_settings():
	export_child_table_format = frappe.db.get_single_value("Wallet Company Settings", "bulk_edit_child_table")
	res = {
		"cvs": "not-remove",    # `remove` to remove existing buttons for csv bulk edit
		"excel": False      # to not show excel buttons
	}

	if export_child_table_format in {"EXCEL & CSV", "EXCEL"}:
		res["excel"] = True
		if export_child_table_format == "EXCEL":
			res["cvs"] = "remove"

	return res
