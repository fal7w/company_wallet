# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.jinja import validate_template


class ActionConfirmMessage(Document):
	def validate(self):
		validate_template(self.submit_message)


def load_boot_messages(bootinfo):
	messages = frappe.get_all("Action Confirm Message", fields=["document_type", "submit_message"])
	res = {}
	for i in messages:
		res[i.get("document_type")] = {"submit": i.get("submit_message")}
	bootinfo.action_confirm_message = res
