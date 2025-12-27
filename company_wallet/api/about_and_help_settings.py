# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from company_wallet.api.utils import unify_response
from frappe.utils import cstr


@frappe.whitelist(allow_guest=True)
def get_content_text(subject):
	"""
	Get the content text for a given subject.
	:param subject: The subject for which to retrieve the content text.
	:type subject: str
	:return: The content text for the given subject.
	:rtype: str
	:raises frappe.exceptions.ValidationError: If the content text is not found for the given subject.
	"""
	try:
		settings = frappe.db.get_single_value("Wallet Company Settings", subject)
		return settings
	except frappe.exceptions.ValidationError:
		return cstr(_("Content not found for the subject: {subject}").format(subject=subject))