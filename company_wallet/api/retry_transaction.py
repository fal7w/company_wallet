import frappe
from company_wallet.company_wallet.doctype.wallet_payment_log.wallet_payment_log import _publish_payment_log
from .confirm_password_transaction import confirm_password_transaction
from .utils import unify_response


@unify_response()
def publish_payment_log(docs, password, parent=None, retry=True):
	"""
	This function publishes a payment log for a wallet transaction.
	Parameters:
		- docs: The document ID for the wallet payment log.
		- password: The password for confirming the transaction.
		- parent: The parent document for the payment log (default is None).
		- retry: A boolean indicating whether to retry the transaction (default is True).
	"""
	confirm_password_transaction(password)
	if not parent:
		log = frappe.get_doc("Wallet Payment Log", docs)
		parent = frappe.get_doc(log.voucher_type, log.voucher_no)

	_publish_payment_log(docs, parent, retry)