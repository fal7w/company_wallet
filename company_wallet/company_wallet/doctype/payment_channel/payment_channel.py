# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PaymentChannel(Document):
	def on_trash(self):
		frappe.throw(_("Can't delete payment channel"))
