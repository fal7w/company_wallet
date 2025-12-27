# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt
from company_wallet.company_wallet.doctype.device_info_log.device_info_log import create_device_log
import frappe
from frappe import _
from frappe.model.document import Document
from company_wallet.company_wallet.doctype.wallet_payment_log.wallet_payment_log import create_payment_log, publish_payment_log
from frappe.utils import get_url_to_form, cint, cstr, flt, money_in_words
from company_wallet.connect_sdk import init_default_sdk, PaymentSDK, NetworkError, CompanySDK
from company_wallet.company_wallet.doctype.wallet_company.wallet_company import validate_wallet_company

from company_wallet.company_wallet.doctype.company_wallet_configration.company_wallet_configration import check_ping_pong


class WalletPayment(Document):
	@property
	def wallet_payment_log(self):
		if not self.flags.cache_wallet_payment_log:
			wallet_payment_log = frappe.db.exists("Wallet Payment Log", {"voucher_type": self.doctype, "voucher_no": self.name})
			self.flags.cache_wallet_payment_log = wallet_payment_log
		return self.flags.cache_wallet_payment_log

	@property
	def express_number(self):
		if not self.flags.cache_express_number and self.wallet_payment_log:
			express_number = frappe.db.get_value("Wallet Payment Log", self.wallet_payment_log, "express_number")
			self.flags.cache_express_number = express_number
		return self.flags.cache_express_number
	
	def on_submit(self):
		self.set_status()
		if self.status == "Approved":
			check_ping_pong()
			if not self.fee_currency:
				frappe.throw(_("Can't send payment request without fee currency"))

			self.get_balance()
			log = create_payment_log(self)
			publish_payment_log(log, self)
			create_device_log(self)

		elif self.status == "Draft":
			frappe.throw(_("Set Status to Approved first!, please."))

	def set_status(self):
		if not self.status:
			frappe.throw(_("Status field is mandatory!"))
		if self.status == "Draft":
			frappe.throw(_("Cannot set status to Draft when submitting!"))
		if self.status == "Approved":
			frappe.db.set_value("Wallet Payment", self.name, "status", "In progress")

	def get_commission_amount(self):
		if self.status != "Rejected":
			payment = init_default_sdk(PaymentSDK, self.wallet_company)

			transaction_type = frappe.db.get_value("Payment Channel", self.payment_channel, "transaction_id")
			
			if remittance_provider := self.remittance_provider:
				remittance_provider = frappe.db.get_value("Remittance Provider", self.remittance_provider, "remittance_provider_id")
			else:
				remittance_provider = frappe.db.get_value("Remittance Provider", self.wallet_provider, "remittance_provider_id")

			commission_res = payment.get_commission(self.get("currency"), self.get("amount"), self.name, str(transaction_type), remittance_provider, _("Can't get commission"))
			commission_res = commission_res.json
			if commission_res["status"]:
				self.fee_amount = commission_res["data"]["txnamount"]
				self.fee_currency = commission_res["data"]["commissionCurrency"]

	def call_customer_info(self):
		if self.status != "Rejected":
			if self.recipient_phone and self.has_value_changed('recipient_phone'):
				try:
					payment = init_default_sdk(PaymentSDK, self.wallet_company)
					customer_res = payment.get_customer_info(self.name, self.get("recipient_phone"), _("Can't get customer info"))
					customer_name = customer_res.json["data"]["customer"]
					if customer_name:
						self.customer = f"{customer_name.get('name', '')} {customer_name.get('middleName', '')} {customer_name.get('grandfatherName', '')} {customer_name.get('familyName', '')}".strip()
				except NetworkError:
					pass

	def on_cancel(self):
		frappe.throw(_("Can't cancel payment after submit"))

	def validate(self):
		validate_wallet_company(self)
		self.set_amount_in_words()
		self.call_customer_info()
		self.validate_recipient_name()
		self.validate_phone()
		self.get_commission_amount()
		self.deduct_commission_from_send_amount()

	def set_amount_in_words(self):
		self.amount_in_words = money_in_words(self.amount, self.currency)	

	def validate_recipient_name(self):
		if self.customer:
			self.recipient = self.customer
		if self.recipient:
			names = self.recipient.strip().split()
			recipient_name_length_settings = frappe.db.get_single_value("Wallet Company Settings", "recipient_name_length")
			if len(names) < int(recipient_name_length_settings):
				frappe.throw(_("Recipient Name must contains at least {0} names").
					format(frappe.bold(recipient_name_length_settings)))

	def validate_phone(self):
		self._validate_phone(cstr(self.get("recipient_phone")))

	def _validate_phone(self, phone):
		setting_doc = frappe.get_single("Wallet Company Settings")
		phone_length = cint(setting_doc.phone_length)

		if not setting_doc.services_setting_phone_prefix:
			url = get_url_to_form(setting_doc.doctype, setting_doc.name)
			error_message = _(
				"There is no phone prefix in <a href='{url}' target='_blank'>{name}</a> doctype").format(url=url, name=setting_doc)
			frappe.throw(error_message)
		if len(phone) != phone_length:
			frappe.throw(_("Phone number length must be {phone_length} numbers").format(
				phone_length=phone_length))

		prefixes = tuple(cstr(p.prefix) for p in setting_doc.services_setting_phone_prefix)
		if not phone.startswith(prefixes):
			frappe.throw(
				_("Phone number must start with {prefixs}").format(prefixs=prefixes))
			
	def deduct_commission_from_send_amount(self):
		if self.deduct_commission_from_amount:
			amount = flt(self.amount) - flt(self.fee_amount)
		else:
			amount = flt(self.amount)

		self.real_amount = amount

		return amount

	@frappe.whitelist()
	def get_balance(self):
		total_amount = 0
		payment = init_default_sdk(CompanySDK, self.wallet_company)
		payment_res = payment.get_agent_balance(_("Can't get balance"))
		payment_res = payment_res.json
		if payment_res["status"]:
			current_balance = None
			for balance_entry in payment_res["data"]:
				if balance_entry["currency"] == self.currency:
					current_balance = flt(balance_entry["balance"])
					break

			if current_balance is None:
				frappe.throw(_("Currency balance not found."))
			
			total_amount = flt(self.real_amount) + flt(self.fee_amount)

			if current_balance < total_amount:
				frappe.throw(_("Insufficient balance. Required: {0}, Available: {1}").format(total_amount, current_balance))


@frappe.whitelist()
def check_user_password(password):
	from frappe.utils.password import check_password
	try:
		user = frappe.session.user
		check_password(user, password)
		return True
	except frappe.AuthenticationError:
		frappe.throw(_("Incorrect password"))


@frappe.whitelist()
def check_status(docname):
	doc = frappe.get_doc('Wallet Payment', docname)
	log = frappe.get_doc('Wallet Payment Log', doc.wallet_payment_log)
	payment = init_default_sdk(PaymentSDK, log.wallet_company)
	payment_res = payment.check_status_single(log.parent_ref_id, log.request_payment_ref_id, _("Can't get payment status"))
	payment_res = payment_res.json
	if payment_res["status"]:
		log.db_set(
			{
				"status": payment_res["data"]["status"],
				"express_number":  payment_res["data"].get("express_number", ""),
				"message": payment_res["data"].get("message", "")
			},
			update_modified=True, commit=True)
		
		frappe.db.set_value("Wallet Payment", docname, "status", payment_res["data"]["status"], update_modified=True)
	
	return doc