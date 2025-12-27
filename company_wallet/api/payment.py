import frappe
from frappe import _

from company_wallet.company_wallet.doctype.wallet_bulk_payment.wallet_bulk_payment import call_bulk_payment_beneficiary
from .utils import unify_response, get_list_with_count
import frappe.client
from .confirm_password_transaction import confirm_password_transaction
from company_wallet.connect_sdk import init_default_sdk, PaymentSDK, NetworkError

payment_doctype = "Wallet Payment"
bulk_payment_doctype = "Wallet Bulk Payment"


@unify_response()
def create_wallet_payment(with_submit=False, **kwargs):
	"""
	Create a wallet payment.
	:param with_submit: Whether to submit the wallet payment immediately after creation. Default is False.
	:type with_submit: bool
	:param kwargs: Keyword arguments containing the fields and values for the wallet payment.
	:type kwargs: dict
	:return: The created wallet payment document.
	:rtype: frappe.model.document.Document
	"""
	# TODO: kwargs must replaced with model 
	wallet_payment = frappe.get_doc({
		**kwargs,
		"doctype": payment_doctype,
	})
	wallet_payment.save()
	if with_submit:
		confirm_password_transaction(kwargs.get("password"))
		wallet_payment.submit()
	return wallet_payment


@unify_response()
def submit_wallet_payment(name, password):
	"""
	Submits a wallet payment.

	:param name: The name of the wallet payment to submit.
	:type name: str
	:param password: The password to confirm the transaction.
	:type password: str
	:return: The submitted wallet payment document.
	:rtype: frappe.model.document.Document
	"""
	wallet_payment = frappe.get_doc(payment_doctype, name)
	confirm_password_transaction(password)
	wallet_payment.submit()
	return wallet_payment


@unify_response()
def get_wallet_payment(name):
	"""
	Get a wallet payment by its name.

	:param name: The name of the wallet payment to retrieve.
	:type name: str
	:return: The wallet payment document.
	:rtype: dict
	"""
	return frappe.client.get(payment_doctype, name)


@unify_response()
def update_wallet_payment(name, **kwargs):
	"""
	Update a wallet payment by its name with the given keyword arguments.

	:param name: The name of the wallet payment to update.
	:type name: str
	:param kwargs: Keyword arguments containing the fields to update and their new values.
	:type kwargs: dict
	:return: The updated wallet payment document.
	:rtype: frappe.model.document.Document
	"""
	wallet_payment = frappe.get_doc(payment_doctype, name)
	wallet_payment.update(kwargs)
	wallet_payment.save()
	return wallet_payment


@unify_response()
def get_list_wallet_payment(fields=None, filters=None, limit_start=None, limit=20, order_by=None, or_filters=None):
	"""
	Get a list of wallet payments with optional filtering, sorting, and pagination.
	:param fields: A list of fields to include in the result. If not provided, all fields will be returned.
	:type fields: list[str]
	:param filters: A dictionary of filters to apply to the query.
	:type filters: dict[str, Any]
	:param limit_start: The index of the first result to return.
	:type limit_start: int
	:param limit: The maximum number of results to return. Default is 20.
	:type limit: int
	:param order_by: A string specifying the field to sort the results by.
	:type order_by: str
	:param or_filters: A list of dictionaries representing OR filters to apply to the query.
	:type or_filters: list[dict[str, Any]]
	:return: A dictionary containing the count of results and a list of the matching wallet payments.
	:rtype: dict[str, Union[int, list[dict[str, Any]]]]
	"""
	return get_list_with_count(payment_doctype, fields, filters, limit_start=limit_start, limit=limit, order_by=order_by, or_filters=or_filters)


@unify_response()
def create_wallet_bulk_payment(with_submit=False, **kwargs):
	"""
	Create a wallet bulk payment.

	:param with_submit: (Optional) Flag indicating whether to submit the bulk payment after creation. Default is False.
	:type with_submit: bool
	:param **kwargs: Keyword arguments containing the fields to set on the bulk payment document.
	:type **kwargs: dict
	:return: The created wallet bulk payment document.
	:rtype: frappe.model.document.Document
	"""
	wallet_bulk_payment = frappe.get_doc({
		**kwargs,
		"doctype": bulk_payment_doctype,
	})
	wallet_bulk_payment.save()
	if with_submit:
		confirm_password_transaction(kwargs.get("password"))
		wallet_bulk_payment.reload()
		wallet_bulk_payment.submit()
	return wallet_bulk_payment


@unify_response()
def submit_wallet_bulk_payment(name, password):
	"""
	Submits a wallet bulk payment.

	:param name: The name of the wallet bulk payment to submit.
	:type name: str
	:param password: The password to confirm the transaction.
	:type password: str
	:return: The submitted wallet bulk payment document.
	:rtype: frappe.model.document.Document
	"""
	wallet_bulk_payment = frappe.get_doc(bulk_payment_doctype, name)
	confirm_password_transaction(password)
	wallet_bulk_payment.submit()
	return wallet_bulk_payment


@unify_response()
def get_wallet_bulk_payment(name):
	"""
	Get the wallet bulk payment document with the given name.

	:param name: The name of the wallet bulk payment to retrieve.
	:type name: str
	:return: The wallet bulk payment document.
	:rtype: dict
	"""
	return frappe.client.get(bulk_payment_doctype, name)


@unify_response()
def update_wallet_bulk_payment(name, **kwargs):
	"""
	Update a wallet bulk payment by its name with the given keyword arguments.

	:param name: The name of the wallet bulk payment to update.
	:type name: str
	:param kwargs: Keyword arguments containing the fields to update and their new values.
	:type kwargs: dict
	:return: The updated wallet bulk payment document.
	:rtype: frappe.model.document.Document
	"""
	wallet_bulk_payment = frappe.get_doc(bulk_payment_doctype, name)
	wallet_bulk_payment.update(kwargs)
	wallet_bulk_payment.save()
	return wallet_bulk_payment


@unify_response()
def get_list_wallet_bulk_payment(fields=None, filters=None, limit_start=None, limit=20, order_by=None, or_filters=None):
	"""
	Get a list of wallet bulk payment documents with optional filtering, ordering, and pagination.

	:param fields: (Optional) A list of fields to include in the response. Default is None.
	:type fields: list[str] or None
	:param filters: (Optional) A dictionary of filters to apply to the query. Default is None.
	:type filters: dict or None
	:param limit_start: (Optional) The index of the first result to return. Default is None.
	:type limit_start: int or None
	:param limit: (Optional) The maximum number of results to return. Default is 20.
	:type limit: int
	:param order_by: (Optional) The field to order the results by. Default is None.
	:type order_by: str or None
	:param or_filters: (Optional) A list of dictionaries representing OR filters to apply to the query. Default is None.
	:type or_filters: list[dict] or None
	:return: A dictionary containing the list of wallet bulk payment documents and the total count of matching documents.
	:rtype: dict
	"""
	return get_list_with_count(bulk_payment_doctype, fields, filters, limit_start=limit_start, limit=limit, order_by=order_by, or_filters=or_filters)


@unify_response()
def get_list_currency():
	"""
	Get a list of enabled currency names.

	:return: A list of strings representing the names of enabled currencies.
	:rtype: list[str]
	"""
	return [i.get("name") for i in frappe.client.get_list("Currency", fields="name", filters={"enabled": True},  limit_page_length=None)]


@unify_response()
def get_bulk_commission(name):
	"""
	Get the commission amounts for a bulk payment.

	:param name: The name of the wallet bulk payment.
	:type name: str
	:return: A dictionary with a message indicating that the commission creation is queued.
	:rtype: dict
	"""
	wallet_bulk_payment = frappe.get_doc("Wallet Bulk Payment", name)
	frappe.enqueue(
					fetch_commission_amounts,
					# queue='long',
					timeout=600,
					is_async=True,
					job_name=f'fetch_commission_amounts_from_mobile{wallet_bulk_payment.name}',
					name=wallet_bulk_payment.name
					)
	return {"message": _("Get commission creation is queued. It may take a few minutes")}


def fetch_commission_amounts(name):
	"""
	Fetches commission amounts for a bulk payment.

	:param name: The name of the wallet bulk payment.
	:type name: str
	:raises NetworkError: If there is a network error while fetching commission amounts.
	"""
	wallet_bulk_payment_doc = frappe.get_doc("Wallet Bulk Payment", name)
	try:
		payment = init_default_sdk(PaymentSDK, wallet_bulk_payment_doc.wallet_company)

		# Get transaction type
		transaction_type = frappe.db.get_value("Payment Channel", wallet_bulk_payment_doc.payment_channel, "transaction_id")
		remittance_provider_id = frappe.db.get_value("Remittance Provider", {"service_type": wallet_bulk_payment_doc.payment_channel, "enabled": 1}, "remittance_provider_id") if not wallet_bulk_payment_doc.remittance_provider else frappe.db.get_value("Remittance Provider", wallet_bulk_payment_doc.remittance_provider, "remittance_provider_id")

		# Get commission
		for transaction in wallet_bulk_payment_doc.wallet_bulk_payment_transactions:
			commission_res = payment.get_commission(wallet_bulk_payment_doc.currency, transaction.amount, frappe.generate_hash(length=10), str(transaction_type), remittance_provider_id, _("Can't get commission"))
			commission_res = commission_res.json
			
			if commission_res["status"]:
				transaction.fee_amount = commission_res["data"]["txnamount"]
				transaction.db_update()
		wallet_bulk_payment_doc.fee_currency = commission_res["data"]["commissionCurrency"]
		wallet_bulk_payment_doc.save()
	except NetworkError:
		pass


@unify_response()
def get_bulk_customer_info(recipient_phone):
	"""
	Get the customer information for a bulk payment.

	:param recipient_phone: The phone number of the recipient.
	:type recipient_phone: str
	:return: A list of dictionaries containing the recipient phone number and the recipient's name.
	:rtype: list[dict]
	"""
	result = []
	user = frappe.session.user
	wallet_company = frappe.db.get_value("Wallet User", {"email": user}, "wallet_company")
	
	try:
		payment = init_default_sdk(PaymentSDK, wallet_company)
		# Get customer name
		customer_res = payment.get_customer_info(frappe.generate_hash(length=10), recipient_phone, _("Can't get customer info"))
		customer_name = customer_res.json
		if customer_name["status"]:
			customer_name = customer_name.get("data", {}).get("customer", {})
			transaction_details = {
			"recipient_phone": recipient_phone,
			"recipient": " ".join([
				customer_name.get('name', ''),
				customer_name.get('middleName', ''),
				customer_name.get('grandfatherName', ''),
				customer_name.get('familyName', '')
			]).strip()
			}
			result.append(transaction_details)
				
		return result
	except NetworkError:
		pass


@frappe.whitelist()
@unify_response()
def get_bulk_payment_beneficiary(name):
	"""
	Get the beneficiary information for a bulk payment.
	:param name: The name of the wallet bulk payment.
	:type name: str
	:return: A dictionary with a message indicating that the beneficiary Name creation is queued.
	:rtype: dict
	"""
	wallet_bulk_payment = frappe.get_doc("Wallet Bulk Payment", name)
	frappe.enqueue(
					call_bulk_payment_beneficiary,
					# queue='long',
					timeout=600,
					is_async=True,
					job_name=f'get bulk customer info{wallet_bulk_payment.name}',
					name=wallet_bulk_payment.name
					)
	return {"message": _("Get beneficiary Name creation is queued. It may take a few minutes")}