import frappe
from frappe import _
from .utils import unify_response


BULK_PAYMENT_TEMPLATE_DOCTYPE = "Bulk Payment Template"


@unify_response()
def retrieve_bulk_payment_template(name=None):
	"""
	Retrieve details of a Bulk Payment Template by its name if not returned all.
	"""
	try:
		if name:
			bulk_payment_template = frappe.get_doc(BULK_PAYMENT_TEMPLATE_DOCTYPE, name)
			return bulk_payment_template, handle_common_doc_operations(bulk_payment_template)
		else:
			bulk_payment_template = frappe.get_list(BULK_PAYMENT_TEMPLATE_DOCTYPE, fields=["posting_date", "name", "title", "total_amount", "currency", "notes"])
			for template in bulk_payment_template:
				template["beneficiaries_count"] = frappe.get_value(
					"Bulk Payment Detail",
					filters={"parent": template.name},
					fieldname="count(name)"
				)
			return bulk_payment_template
		
	except frappe.DoesNotExistError:
		raise frappe.DoesNotExistError(_("Bulk Payment Template not found"))


@unify_response()
def create_bulk_payment_template(**kwargs):
	"""
	Create a Bulk Payment Template.
	"""
	wallet_bulk_payment_template = frappe.get_doc({
		**kwargs,
		"doctype": BULK_PAYMENT_TEMPLATE_DOCTYPE,
	})
	wallet_bulk_payment_template.save()
	handle_common_doc_operations(wallet_bulk_payment_template)
	return wallet_bulk_payment_template


@unify_response()
def update__bulk_payment_template(name, **kwargs):
	"""
	Update a bulk payment template by its name with the given keyword arguments.
	:param name: The name of the bulk payment template to update.
	:type name: str
	:param kwargs: Keyword arguments containing the fields to update and their new values.
	:type kwargs: dict
	:return: The updated bulk payment template.
	:rtype: frappe.model.document.Document
	"""
	wallet_bulk_payment_template = frappe.get_doc(BULK_PAYMENT_TEMPLATE_DOCTYPE, name)
	wallet_bulk_payment_template.update(kwargs)
	wallet_bulk_payment_template.save()
	handle_common_doc_operations(wallet_bulk_payment_template)
	return wallet_bulk_payment_template


@unify_response()
def delete_bulk_payment_template(name):
	"""
	Delete a Bulk Payment Template by its name.
	"""
	doc = frappe.get_doc(BULK_PAYMENT_TEMPLATE_DOCTYPE, name)
	doc.cancel()
	return _("Cancel {name} done successfully").format(name=name)


def handle_common_doc_operations(doc):
	count = 0
	keys_to_delete = ["creation", "owner", "modified", "modified_by", "docstatus", "idx", "naming_series", "__unsaved"]
	for key in keys_to_delete:
		doc.delete_key(key)
	for detail in doc.get("bulk_payment_detail", []):
		for key in keys_to_delete:
			detail.delete_key(key)
		count += 1
	return {"beneficiaries_count": count}