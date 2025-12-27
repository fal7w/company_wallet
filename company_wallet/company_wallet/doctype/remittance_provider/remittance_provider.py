# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class RemittanceProvider(Document):
	def on_trash(self):
		if self.enable:
			frappe.throw(_("Cann't delete Remittance Provider!"))

