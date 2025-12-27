import frappe
from .utils import unify_response
from frappe import _

# TODO: model of parm of api


@unify_response()
def update_transaction_status(ref_id, express_number, status, message):
	"""
	Update the transaction status.

	:param ref_id: The reference ID of the transaction.
	:type ref_id: str
	:param express_number: The express number of the transaction.
	:type express_number: str
	:param status: The new status of the transaction.
	:type status: str
	:param message: The message associated with the transaction status update.
	:type message: str
	:return: True if the transaction status is successfully updated, False otherwise.
	:rtype: bool
	"""
	log = frappe.get_doc("Wallet Payment Log", {"request_payment_ref_id": ref_id})
	log.db_set({
		"express_number": express_number,
		"status": status,
		"message": message
	})
	if log.voucher_type == "Wallet Payment":
		frappe.db.set_value("Wallet Payment", log.voucher_no, "status", status)
		wallet_payment = frappe.get_doc("Wallet Payment", log.voucher_no)
		wallet_payment.run_method("on_change")

	elif log.voucher_type == "Wallet Bulk Payment":
		update_bulk_payment_status(log.voucher_no)
		
	return True


def update_bulk_payment_status(voucher_no):
	logs = frappe.get_all("Wallet Payment Log", filters={"voucher_no": voucher_no}, fields=["status"])
	status_count = {"Failed": 0, "Success": 0}
	for log in logs:
		status_count[log.status] = status_count.get(log.status, 0) + 1

	formatted_status = ", ".join([f"{count} {_(status)}" for status, count in status_count.items() if count > 0])
	frappe.db.set_value("Wallet Bulk Payment", voucher_no, "status", formatted_status)
	wallet_bulk_payment = frappe.get_doc("Wallet Bulk Payment", voucher_no)
	wallet_bulk_payment.run_method("on_change")
