# Copyright (c) 2024, fintechsys and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document


class OfferDetail(Document):
	
	def validate(self):
		self.validate_dates()

	def validate_dates(self):
		if self.from_date > self.to_date:
			frappe.throw(_("From Date cannot be greater than To Date"))
