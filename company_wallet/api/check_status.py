from company_wallet.api.utils import unify_response
from company_wallet.connect_sdk import init_default_sdk, PaymentSDK
from company_wallet.company_wallet.doctype.wallet_payment.wallet_payment import check_status as wallet_payment_check_status_single
from company_wallet.company_wallet.doctype.wallet_payment_log.wallet_payment_log import check_status as wallet_payment_check_status_log
from company_wallet.company_wallet.doctype.wallet_bulk_payment.wallet_bulk_payment import check_status as wallet_bulk_payment_check_status


@unify_response()
def check_status_wallet_payment(parentRef, error_msg=None):
	"""
	Check the status of a wallet payment.

	:param parentRef: The reference ID of the parent wallet payment.
	:type parentRef: str
	:param error_msg: An optional error message to include in the response.
	:type error_msg: str, optional
	:return: The status of the wallet payment.
	:rtype: dict
	"""
	return wallet_payment_check_status_single(parentRef)


@unify_response()
def check_status_wallet_payment_log(refId, error_msg=None):
	"""
	Check the status of a wallet payment log.

	:param refId: The reference ID of the wallet payment log.
	:type refId: str
	:param error_msg: An optional error message to include in the response.
	:type error_msg: str, optional
	:return: The status of the wallet payment log.
	:rtype: dict
	"""
	return wallet_payment_check_status_log(refId)


@unify_response()
def check_status_bulk(refId, error_msg=None):
	"""
	Check the status of a bulk payment.

	:param refId: The reference ID of the bulk payment.
	:type refId: str
	:param error_msg: An optional error message to include in the response.
	:type error_msg: str, optional
	:return: The status of the bulk payment.
	:rtype: dict
	"""
	return wallet_bulk_payment_check_status(refId)