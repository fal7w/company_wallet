# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PaymentQueryReference(Document):
	pass


@frappe.whitelist()
def create_payment_query_reference(transaction_number, mobile_number=None):
	wallet_payment_log = frappe.get_doc("Wallet Payment Log",
									get_filters(transaction_number, mobile_number),
									["name", "voucher_type", "recipient", "recipient_phone", "status", "express_number"]
										)
	if wallet_payment_log:
		query_reference = frappe.get_doc(
			{
				"doctype": "Payment Query Reference",
				"transaction_number": wallet_payment_log.get("name"),
				"wallet_company": wallet_payment_log.get("wallet_company"),
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


@frappe.whitelist()
def get_password(docname, field):
	try:
		doc = frappe.get_doc("Payment Query Reference", docname)
		if frappe.session.user != doc.owner:
			frappe.throw(_("You are not authorized to view this information."))
		decrypted_value = doc.get_password(field)
		return decrypted_value
	except BaseException:
		return doc.get(field)