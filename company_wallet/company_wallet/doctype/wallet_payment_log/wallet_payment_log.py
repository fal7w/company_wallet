# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
import pyotp
from company_wallet.connect_sdk import init_default_sdk, PaymentSDK
from frappe import _
from frappe.utils import sbool


class WalletPaymentLog(Document):
	pass


def create_payment_log(obj, parent=None):
	if not parent:
		parent = obj

	recipient = obj.get("recipient")
	if not recipient:
		recipient = obj.get("customer")
	
	doc = frappe.get_doc({
		"doctype": "Wallet Payment Log",
		"recipient": recipient,
		"recipient_phone": obj.get("recipient_phone"),
		"amount": obj.get("real_amount"),
		"currency": parent.get("currency"),
		"fee_amount": obj.get("fee_amount"),
		"fee_currency": parent.get("fee_currency"),
		"payment_channel": parent.get("payment_channel"),
		"service_provider": parent.get("remittance_provider") if parent.get("remittance_provider") else parent.get("wallet_provider"),
		"voucher_type": parent.get("doctype"),
		"voucher_no": parent.get("name"),
		"wallet_company": parent.get("wallet_company"),
		"bulk_transaction": obj.get("name") if obj.get("name") != parent.get("name") else None,
		"status": "In progress",
		"remark": obj.get("remark") if obj.get("remark") else parent.get("note") or parent.get("remark")
	})
	doc.flags.ignore_permissions = True
	doc.submit()
	frappe.db.commit()
	return doc


def _publish_payment_log(docs, parent, retry):
	retry = sbool(retry)
	prefix = get_wallet_company_prefix(parent.get("wallet_company"))
	
	if not isinstance(docs, (list, tuple, set)):
		docs = [docs]
  
	transactions = []
	request_ref_id = prefix + "-" + parent.get("name") if not retry else prefix + "-" + parent.get("name") + "-" + pyotp.TOTP(pyotp.random_base32()).now()
	
	for i in docs:
		if isinstance(i, str):
			i = frappe.get_doc("Wallet Payment Log", i)
			
		transactions.append(get_payment_request_info(i, prefix, retry))
		frappe.db.set_value("Wallet Payment Log", i.get("name"), "parent_ref_id", request_ref_id, update_modified=True)

	payment = init_default_sdk(PaymentSDK, parent.get("wallet_company"))

	if remittance_provider := parent.get("remittance_provider"):
		remittance_provider = frappe.db.get_value("Remittance Provider", remittance_provider, "remittance_provider_id")
	else:
		remittance_provider = frappe.db.get_value("Remittance Provider", parent.get("wallet_provider"), "remittance_provider_id")

	if dummy_flag := frappe.db.get_value("Wallet Company", parent.get("wallet_company"), "dummy"):
		dummy_flag = True
	else:
		dummy_flag = False

	if parent.get("total_fee") is not None:
		fee = parent.get("total_fee")
	else:
		fee = parent.get("fee_amount")

	remark = parent.get("remark") if parent.get("remark") else parent.get("note")
	
	payments = payment.send_payment_request(
		transactions,
		parent.get("total_real_amount") or parent.get("real_amount"),
		parent.get("currency"),
		fee,
		request_ref_id,
		parent.get("payment_channel"),
		remittance_provider,
		dummy_flag,
		remark,
		_("Can't send payment request")
	)
	payments_res = payments.json
	if payments_res["status"]:
		payments_res = payments_res["result"]
		if payments_res:
			doc = frappe.get_all("Wallet Payment Log", filters={"voucher_no": parent.get("name")}, fields=["name"])
			if not doc:
				doc = frappe.get_all("Wallet Payment Log", filters={"voucher_no": parent.get("voucher_no")}, fields=["name"])
			for i in doc:
				log = frappe.get_doc("Wallet Payment Log", i["name"])
				log.db_set("ref_id", payments_res)
	else:
		frappe.throw(_(payments_res["result"]))


@frappe.whitelist()
def publish_payment_log(docs, parent, retry=False):
	if isinstance(parent, str):
		parent = frappe._dict(frappe.parse_json(parent))
		
	_publish_payment_log(docs, parent, retry)
	frappe.db.commit()
  

def get_payment_request_info(doc, prefix, retry):
	if isinstance(doc, str):
		doc = frappe.get_doc("Wallet Payment Log", doc)
		
	ref_id_log = prefix+"-"+doc.get("name") if not retry else prefix + "-" + doc.get("name") + "-" + pyotp.TOTP(pyotp.random_base32()).now()
	frappe.db.set_value("Wallet Payment Log", doc.get("name"), "request_payment_ref_id", ref_id_log, update_modified=True)
	return {
		"id": ref_id_log,
		"name": doc.get("recipient"),
		"phone": doc.get("recipient_phone"),
		"amount": doc.get("amount"),
		"commission_amount": doc.get("fee_amount"),
		"remark": doc.get("remark") or doc.get("note")
	}


def get_wallet_company_prefix(wallet_company_name):
	return frappe.db.get_value("Wallet Company", wallet_company_name, "company_prefix")


@frappe.whitelist()
def check_status(docname):
	doc = frappe.get_doc('Wallet Payment Log', docname)
	payment = init_default_sdk(PaymentSDK, doc.wallet_company)
	payment_res = payment.check_status_single(doc.parent_ref_id, doc.request_payment_ref_id, _("Can't get payment status"))
	payment_res = payment_res.json
	if payment_res["status"]:
		doc.db_set({
				"status": payment_res["data"].get("status"),
				"message": payment_res["data"].get("message", ""),
				"express_number": payment_res["data"].get("express_number", "")
			},
			update_modified=True, commit=True
		)


@frappe.whitelist()
def retry_transactions(docs):
	docs = frappe.parse_json(docs)
	for doc_name in docs:
		try:
			doc = frappe.get_doc("Wallet Payment Log", doc_name)
			publish_payment_log([doc.name], doc)
			# doc.save()
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(message=str(e), title=_("Retry Transaction Error for {0}").format(doc_name))
			frappe.throw(_("Failed to retry transaction for {0}: {1}").format(doc_name, str(e)))