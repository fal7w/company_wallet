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

from company_wallet.api.webhook import update_bulk_payment_status

from company_wallet.company_wallet.doctype.company_wallet_configration.company_wallet_configration import check_ping_pong


class WalletBulkPayment(Document):	
	def on_cancel(self):
		frappe.throw(_("Can't cancel bulk payments after submit"))

	# def before_submit(self):
	# 	self.get_commission_amount()
	# 	self.set_status()
	# 	self.get_balance()

	def submit(self):
		self.set_status()
		if self.transaction_number >= 3:
			# frappe.publish_progress(0, title=_("Creating Remittance..."))
			self.queue_action('submit', queue="long", job_name=f"Submit {self.name}")
		else:

			return super().submit()

	def on_submit(self):
		if self.status == "Approved":
			check_ping_pong()
			fetch_commission_amounts(self.name, self.wallet_company, self.payment_channel, self.currency, self.remittance_provider, publish=True)
			self.reload()
			self.set_real_amount()
			self.get_balance()
			logs = []
			for index, i in enumerate(self.wallet_bulk_payment_transactions, 1):
				log = create_payment_log(i, self)
				logs.append(log)
				frappe.publish_realtime(
								"wallet_bulk_payment_process",
								{
									"current": index,
									"total": self.transaction_number,
									"docname": self.name,
									"success": True,
									"message": '{0}/{1}, Submiting Transaction',
									"eta": 0,
								},
								doctype=self.doctype,
								docname=self.name
							)
			publish_payment_log(logs, self)
			create_device_log(self)
			
		elif self.status == "Draft":
			frappe.throw(_("Set Status to Approved first!, please."))

	def validate(self):
		validate_wallet_company(self)
		self.validate_recipient_names_in_bulk_payment()
		self.set_missing_value()
		self.validate_phone()

	def set_missing_value(self):
		self.import_bulk_template()
		self.set_totals()
		self.set_real_amount()
		self.transaction_number = len(self.wallet_bulk_payment_transactions) if self.wallet_bulk_payment_transactions else 0

	def set_totals(self):
		total_amount = 0
		total_fee = 0
		for i in self.wallet_bulk_payment_transactions:
			total_amount += flt(i.get("amount"))
			total_fee += flt(i.get("fee_amount"))
		self.total = total_amount
		self.total_fee = total_fee
		self.total_in_words = money_in_words(self.total, self.currency)

	def set_real_amount(self):
		total_real_amount = 0
		if self.deduct_commission_from_amount:
			for i in self.wallet_bulk_payment_transactions:
				i.real_amount = flt(i.get("amount")) - flt(i.get("fee_amount"))
				total_real_amount += flt(i.get("real_amount"))
			self.total_real_amount = total_real_amount

		else:
			for i in self.wallet_bulk_payment_transactions:
				i.real_amount = flt(i.get("amount"))
				total_real_amount += flt(i.get("real_amount"))
			self.total_real_amount = total_real_amount

	def set_status(self):
		if not self.status:
			frappe.throw(_("Status field is mandatory!"))
		if self.status == "Draft":
			frappe.throw(_("Cannot set status to Draft when submitting!"))

	def validate_recipient_names_in_bulk_payment(self):
		if self.payment_channel == "Remittance":
			recipient_name_length_settings = frappe.db.get_single_value("Wallet Company Settings", "recipient_name_length")
			for transaction in self.wallet_bulk_payment_transactions:
				if transaction.recipient:
					names = transaction.recipient.strip().split()
					if len(names) < int(recipient_name_length_settings):
						frappe.throw(_("Recipient Name in transaction {0} must contain at least {1} names.").
							format(frappe.bold(transaction.idx), frappe.bold(recipient_name_length_settings)))

	def before_save(self):
		self.check_child_amount_changes()

	def check_child_amount_changes(self):
		amount_changed = False
		if self.is_new():
			amount_changed = True
		else:
			db_doc = frappe.get_doc(self.doctype, self.name)
			db_children = {d.name: d.amount for d in db_doc.wallet_bulk_payment_transactions}
			
			for child in self.wallet_bulk_payment_transactions:
				if child.name in db_children and child.amount != db_children[child.name]:
					amount_changed = True
					break

		# flag on the document to indicate if the commission calculation should be re-triggered
		frappe.flags.commission_calculation_required = amount_changed

	def deduct_commission_from_send_amount(self):
		amount = flt(self.total_real_amount) + flt(self.total_fee)
	
		return amount

	@frappe.whitelist()
	def get_commission_amount(self):
		if self.transaction_number >= 3:
			frappe.enqueue(
					fetch_commission_amounts,
					# queue='long',
					timeout=600,
					is_async=True,
					job_name=f'fetch_commission_amounts_{self.name}',
					docname=self.name,
					wallet_company=self.wallet_company,
					payment_channel=self.payment_channel,
					currency=self.currency,
					remittance_provider=self.remittance_provider,
					)
			# self.db_set('commission_process_queued', 1)
			frappe.flags.commission_calculation_required = False
			frappe.msgprint(
					_("Get commission creation is queued. It may take a few minutes"),
					alert=True,
					indicator="blue",
				)
		else:
			fetch_commission_amounts(self.name, self.wallet_company, self.payment_channel, self.currency, self.remittance_provider)
			# self.db_set('commission_process_queued', 1)
			frappe.flags.commission_calculation_required = False
		
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
			
			total_amount = self.deduct_commission_from_send_amount()
			
			if current_balance < total_amount:
				frappe.publish_realtime("msgprint", {"message": _("Insufficient balance. Required: {0}, Available: {1}").format(total_amount, current_balance)})
				frappe.throw(_("Insufficient balance. Required: {0}, Available: {1}").format(total_amount, current_balance))
				# raise frappe.ValidationError

	@frappe.whitelist()
	def import_bulk_template(self):
		if self.has_value_changed('bulk_payment_template') and self.bulk_payment_template:
			self.set('wallet_bulk_payment_transactions', [])
			template = frappe.get_doc("Bulk Payment Template", self.bulk_payment_template)
			self.currency = template.currency
			self.payment_channel = template.payment_channel
			if self.payment_channel == "Remittance":
				self.remittance_provider = template.remittance_provider
			for i in template.bulk_payment_detail:
				data = {
					"recipient": i.get("full_name"),
					"recipient_phone": i.get("phone_number"),
					"amount": i.get("amount"),
				}
				self.append("wallet_bulk_payment_transactions", data)

	def validate_phone(self):
		for row in self.wallet_bulk_payment_transactions:
			phone_number = cstr(row.get("recipient_phone"))
			self._validate_phone(phone_number)

	def _validate_phone(self, phone):
		phone_numbers = self.wallet_bulk_payment_transactions
		setting_doc = frappe.get_single("Wallet Company Settings")
		phone_length = cint(setting_doc.phone_length)
		url = get_url_to_form(setting_doc.doctype, setting_doc.name)

		if not setting_doc.services_setting_phone_prefix:
			url = get_url_to_form(setting_doc.doctype, setting_doc.name)
			error_message = _(
				"There is no phone prefix in <a href='{url}' target='_blank'>{name}</a> doctype").format(url=url, name=setting_doc)
			frappe.throw(error_message)

		prefixes = tuple(cstr(p.prefix) for p in setting_doc.services_setting_phone_prefix)

		for idx, contact in enumerate(phone_numbers, start=1):
			phone = cstr(contact.recipient_phone)
			if len(phone) != phone_length:
				frappe.throw(_("Row #{idx}: Phone number length must be {phone_length} digits").format(
					idx=idx, phone_length=phone_length))

			if not phone.startswith(prefixes):
				frappe.throw(_("Row #{idx}: Phone number must start with {prefixes}").format(
					idx=idx, prefixes=prefixes))
							

def fetch_commission_amounts(docname, wallet_company, payment_channel, currency, remittance_provider=None, publish=False):
	doc = frappe.get_doc('Wallet Bulk Payment', docname)

	payment = init_default_sdk(PaymentSDK, wallet_company)
	transaction_type = frappe.db.get_value("Payment Channel", payment_channel, "transaction_id")

	if remittance_provider:
		remittance_provider_id = frappe.db.get_value("Remittance Provider", remittance_provider, "remittance_provider_id")
	else:
		remittance_provider_id = frappe.db.get_value("Remittance Provider", doc.wallet_provider, "remittance_provider_id")
	
	for index, transaction in enumerate(doc.wallet_bulk_payment_transactions, 1):
		commission_res = payment.get_commission(currency, transaction.amount, doc.name, str(transaction_type), remittance_provider_id, _("Can't get commission"))
		commission_res = commission_res.json
		if commission_res["status"]:
			transaction.fee_amount = commission_res["data"]["txnamount"]
			transaction.db_update()
			
		if publish:
			frappe.publish_realtime(
								"wallet_bulk_payment_process",
								{
									"current": index,
									"total": doc.transaction_number,
									"docname": doc.name,
									"success": True,
									"message": '{0}/{1}, Get Commission',
									"eta": 0,
								},
								doctype=doc.doctype,
								docname=doc.name
							)
	doc.fee_currency = commission_res["data"]["commissionCurrency"]
	# doc.commission_process_queued = True
	doc.save()


def call_bulk_payment_beneficiary(name):
	try:
		doc = frappe.get_doc('Wallet Bulk Payment', name)
		payment = init_default_sdk(PaymentSDK, doc.wallet_company)
		
		total_transactions = len(doc.wallet_bulk_payment_transactions)

		for index, transaction in enumerate(doc.wallet_bulk_payment_transactions, 1):
			customer_res = payment.get_customer_info(transaction.name, transaction.recipient_phone, _("Can't get customer info"))
			customer_name = customer_res.json.get("data", {}).get("customer", {})
			if customer_name:
				transaction.recipient = " ".join([
					customer_name.get('name', ''),
					customer_name.get('middleName', ''),
					customer_name.get('grandfatherName', ''),
					customer_name.get('familyName', '')
				]).strip()
			transaction.db_update()
			
			frappe.publish_realtime(
				"wallet_bulk_payment_process",
				{
					"current": index,
					"total": total_transactions,
					"docname": doc.name,
					"success": True,
					"message": f'{index}/{total_transactions}, Updated beneficiary Name for transaction',
					"eta": 0,
				},
				doctype=doc.doctype,
				docname=doc.name
			)
		doc.get_bulk_customer_info = True
		doc.save()

	except NetworkError:
		pass


@frappe.whitelist()
def check_status(docname):
	doc = frappe.get_doc('Wallet Bulk Payment', docname)
	if doc.wallet_bulk_payment_transactions:
		payment_log = doc.wallet_bulk_payment_transactions[0].wallet_payment_log
	else:
		return doc
	parent_ref_id = frappe.get_value("Wallet Payment Log", payment_log, "parent_ref_id")
	payment = init_default_sdk(PaymentSDK, doc.wallet_company)
	payment_res = payment.check_status_bulk(parent_ref_id, _("Can't get bulk payment status")).json
	if payment_res["status"]:
		bulk_details = payment_res["data"].get("bulk_detail")

		if bulk_details is None:
			status = payment_res["data"].get("status")
			message = payment_res["data"].get("message", None)
			if isinstance(status, str):
				for transaction in doc.wallet_bulk_payment_transactions:
					frappe.db.set_value("Wallet Payment Log", transaction.wallet_payment_log, "status", status, update_modified=True)
					frappe.db.set_value("Wallet Payment Log", transaction.wallet_payment_log, "message", message, update_modified=True)
		else:
			for transaction, detail in zip(doc.wallet_bulk_payment_transactions, bulk_details):
				status = detail['status'] if isinstance(detail, dict) else detail
				message = detail['message'] if isinstance(detail, dict) else None
				frappe.db.set_value("Wallet Payment Log", transaction.wallet_payment_log, "status", status, update_modified=True)
				frappe.db.set_value("Wallet Payment Log", transaction.wallet_payment_log, "message", message, update_modified=True)
	
	update_bulk_payment_status(docname)
	
	return doc

