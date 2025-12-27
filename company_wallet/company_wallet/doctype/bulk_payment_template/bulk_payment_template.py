# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url_to_form, cint, cstr, flt


class BulkPaymentTemplate(Document):
	def validate(self):
		self.set_amount_field()
		self.validate_phone()

	def set_amount_field(self):
		total_amount = 0
		for i in self.bulk_payment_detail:
			total_amount += flt(i.amount)
		self.total_amount = total_amount

	def validate_phone(self):
		for row in self.bulk_payment_detail:
			phone_number = cstr(row.get("recipient_phone"))
			self._validate_phone(phone_number)

	def _validate_phone(self, phone):
		phone_numbers = self.bulk_payment_detail
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