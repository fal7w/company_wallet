# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BulkEditDownloadTemplate(Document):
	pass


def after_doctype_insert():
	frappe.db.add_unique("Bulk Edit Download Template", ("template_name", "document_type"))