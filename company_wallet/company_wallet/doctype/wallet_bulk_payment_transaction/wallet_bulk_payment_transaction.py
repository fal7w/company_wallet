# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WalletBulkPaymentTransaction(Document):
	@property
	def wallet_payment_log(self):
		if not self.flags.cache_wallet_payment_log:
			wallet_payment_log = frappe.db.exists("Wallet Payment Log", {
				"voucher_type": self.parenttype,
				"voucher_no": self.parent,
				"bulk_transaction": self.name
			})
			self.flags.cache_wallet_payment_log = wallet_payment_log
		return self.flags.cache_wallet_payment_log

	@property
	def status(self):
		if not self.flags.cache_status and self.wallet_payment_log:
			status = frappe.db.get_value("Wallet Payment Log", self.wallet_payment_log, "status")
			self.flags.cache_status = status
		return self.flags.cache_status

	@property
	def express_number(self):
		if not self.flags.cache_express_number and self.wallet_payment_log:
			express_number = frappe.db.get_value("Wallet Payment Log", self.wallet_payment_log, "express_number")
			self.flags.cache_express_number = express_number
		return self.flags.cache_express_number
