import frappe
from frappe import _
from company_wallet.api.utils import unify_response
from company_wallet.connect_sdk import init_default_sdk, PaymentSDK, NetworkError


@unify_response()
def get_list_currency():
	"""
	Get a list of enabled currency names.

	:return: A list of strings representing the names of enabled currencies.
	:rtype: list[str]
	"""
	return [_(i.get("name")) for i in frappe.client.get_list("Currency", fields=["name"], filters={"enabled": True})]


@unify_response()
def get_providers_currency_list():
	"""
	Get a list of enabled remittance providers and their associated currencies.

	:return: A dictionary containing the following keys:
	- "remittance_providers": A list of dictionaries representing remittance providers, each with the following keys:
		- "name": The name of the remittance provider.
		- "translated_name": The translated name of the remittance provider.
		- "remittance_provider_id": The ID of the remittance provider.
		- "service_type": The service type of the remittance provider.
	- "currencies": A list of strings representing the names of enabled currencies.
	- "currency_translation": A list of dictionaries representing currency translations, each with the following keys:
		- "code": The code of the currency.
		- "label": The translated label of the currency.
	:rtype: dict
	"""
	wallet_data = {}
	try:
		providers_list = frappe.get_list("Remittance Provider", fields=["name", "remittance_provider_id", "service_type"], filters={"enabled": 1})
		wallet_data["remittance_providers"] = [{ 
			"name": i.get("name"),
			"translated_name": _(i.get("name")),
			"remittance_provider_id": i.get("remittance_provider_id"),
			"service_type": _(i.get("service_type"))} for i in providers_list]

		currencies = frappe.client.get_list("Currency", fields=["name"], filters={"enabled": True})
		wallet_data["currencies"] = [_(i.get("name")) for i in currencies]
		wallet_data["currency_translation"] = [{
			"code": i.get("name"), "label": _(i.get("name"))} for i in currencies]

		return wallet_data

	except frappe.DoesNotExistError:
		return
	

@unify_response()
def get_customer_commission(currency, amount, payment_channel, recipient_phone, remittance_provider=None):
	"""
	API method to get commission amount and customer information.

	:param currency: The currency of the transaction.
	:param amount: The amount of the transaction.
	:param payment_channel: The payment channel used for the transaction.
	:param recipient_phone: The phone number of the recipient.
	:param remittance_provider: The remittance provider (optional).

	:return: A dictionary containing the commission amount and customer information.
	- "fee_amount": The commission amount.
	- "fee_currency": The currency of the commission.
	- "customer": The customer information.

	:rtype: dict
	"""
	result = {}
	user = frappe.session.user
	wallet_company = frappe.db.get_value("Wallet User", {"email": user}, "wallet_company")
	
	try:
		payment = init_default_sdk(PaymentSDK, wallet_company)

		# Get transaction type
		transaction_type = frappe.db.get_value("Payment Channel", payment_channel, "transaction_id")
		remittance_provider_id = frappe.db.get_value("Remittance Provider", {"service_type": payment_channel, "enabled": 1}, "remittance_provider_id") if not remittance_provider else frappe.db.get_value("Remittance Provider", remittance_provider, "remittance_provider_id")

		# Get commission
		commission_res = payment.get_commission(currency, amount, frappe.generate_hash(length=10), str(transaction_type), remittance_provider_id, _("Can't get commission"))   # nosemgrep
		commission_res = commission_res.json
		if commission_res["status"]:
			result["fee_amount"] = commission_res["data"]["txnamount"]
			result["fee_currency"] = commission_res["data"]["commissionCurrency"]

		# Get customer info
		customer_res = payment.get_customer_info(frappe.generate_hash(length=10), recipient_phone, _("Can't get customer info"))  # nosemgrep
		customer_res = customer_res.json
		customer_name = customer_res["data"]["customer"]
		if customer_name:
			result["customer"] = f"{customer_name.get('name', '')} {customer_name.get('middleName', '')} {customer_name.get('grandfatherName', '')} {customer_name.get('familyName', '')}".strip()

		return result
	except NetworkError:
		pass

	