import frappe
from .utils import unify_response
from frappe import _


@unify_response()
def create_payment_query_reference(transaction_number, mobile_number=None):
	"""
	Create a payment query reference.

	:param transaction_number: The transaction number.
	:type transaction_number: str
	:param mobile_number: (Optional) The mobile number. Default is None.
	:type mobile_number: str, optional
	:return: The created payment query reference.
	:rtype: frappe.model.document.Document
	"""
	wallet_payment_log = frappe.get_doc("Wallet Payment Log",
									get_filters(transaction_number, mobile_number),
									["name", "voucher_type", "recipient", "recipient_phone", "status", "express_number"]
										)
	if wallet_payment_log:
		query_reference = frappe.get_doc(
			{
				"doctype": "Payment Query Reference",
				"transaction_number": wallet_payment_log.get("name"),
				"remittance_type": wallet_payment_log.get("voucher_type"),
				"mobile_number": wallet_payment_log.get("recipient_phone"),
				"beneficiary_name": wallet_payment_log.get("recipient"),
				"status": wallet_payment_log.get("status"),
				"express_number": wallet_payment_log.get("express_number"),
			}
		)
		query_reference.flags.ignore_permissions = True
		query_reference.save()

		return query_reference


def get_filters(transaction_number, mobile_number=None):
	if mobile_number:
		return {"recipient_phone": mobile_number, "voucher_no": transaction_number}
	else:
		return {"voucher_no": transaction_number}


@unify_response()
def get_password(docname, field):
	"""
	Get the password for a given document name and field.
	:param docname: The document name to retrieve the password for.
	:type docname: str
	:param field: The field for which the password is to be retrieved.
	:type field: str
	:return: The decrypted password value if the document has an express number, otherwise an error message.
	:rtype: str
	"""
	# try:
	doc = frappe.get_doc("Payment Query Reference", docname)
	if frappe.session.user != doc.owner:
		frappe.throw(_("You are not authorized to view this information."), frappe.ValidationError)

	if doc.express_number:
		try:
			decrypted_value = doc.get_password(field)
			return decrypted_value
		
		except Exception:
			return doc.get(field)
	else:
		return frappe.throw(_("There is no express number for this query maybe it's failed or still in progress!"))