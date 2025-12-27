# Copyright (c) 2024, fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from company_wallet.connect_sdk import init_default_sdk, CompanySDK


class CompanyWalletConfigration(Document):
	def validate(self):
		if self.authentication_type != "Token" and not self.user_name:
			frappe.throw(_("Error: Value missing for {0}: {1}").format(
					_(self.doctype),
					_(self.get_label_from_fieldname("user_name"))
				),
				exc=frappe.MandatoryError
			)

	def before_save(self):
		if self.authentication_type == "Token":
			self.user_name = None


@frappe.whitelist()
def check_ping_pong():
	connection_config = init_default_sdk(CompanySDK)
	result_connection = connection_config.check_ping_pong_connection(_("Error Connecting to Server"))
	return result_connection