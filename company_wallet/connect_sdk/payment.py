import uuid
from frappe.utils.data import flt
from .connect_base import ConnectSDK


class PaymentSDK(ConnectSDK):
	def send_payment_request(self, bene_list, total_amount, currency, commission_amount, name, type, remittance_provider, dummy_flag, remark, error_message):
		return self._request("POST", "send_payment_request", {
			"dummy": dummy_flag,
			"total": total_amount,
			"currency": currency,
			"commission_total": commission_amount,
			"type": type.lower(),
			"network_name": remittance_provider,
			"refId": name,
			"beneficiaries": bene_list,
			"purpose": remark,
			}, error_message=error_message)

	def get_commission(self, currency, amount, name, transaction_type, remittance_provider, error_message):
		name = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{name}{uuid.uuid1()}").hex)
		return self._request("POST", "get_commission", {
			"transactionType": transaction_type,
			"assMember": remittance_provider,
			"txnamount": flt(amount),
			"walletProduct": "Corp_Dflt_product",
			"currency": currency,
			"associationIden": "AMA",
			"refId": name,
			"direction": "out"
		}, error_message=error_message)

	def get_customer_info(self, name, recipient_phone, error_message):
		return self._request("POST", "get_customer_info", {
			"refId": f"customer_info{int(uuid.uuid4().hex[:10], 16):010}",
			"walletIden": recipient_phone,
		}, error_message=error_message)
	
	def check_status_bulk(self, name, error_message):
		return self._request("POST", "check_status_bulk", {
			"refId": name
		}, error_message=error_message)
	
	def check_status_single(self, name, wallet_payment_log, error_message):
		return self._request("POST", "check_status_single", {
			"parentRef": name,
			"refId": wallet_payment_log
		}, error_message=error_message)


PaymentSDK._update_action_url({
	"send_payment_request": "/api/jawali-company/v1/payment",
	"get_commission": "/api/jawali-company/v1/commission",
	"get_customer_info": "/api/jawali-company/v1/customer-info",
	"check_status_single": "/api/jawali-company/v1/checkstatus-single",
	"check_status_bulk": "/api/jawali-company/v1/checkstatus-bulk"
})