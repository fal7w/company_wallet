# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import datetime
import frappe
from frappe import _
from company_wallet.connect_sdk.company import CompanySDK
from company_wallet.connect_sdk import init_default_sdk
from company_wallet.api.utils import unify_response


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def clean_and_parse_datetime(datetime_str):
	cleaned_datetime = datetime_str.replace(': ', ':')
	return datetime.datetime.strptime(cleaned_datetime,'%d/%m/%y %H:%M:%S')


@unify_response()
def get_data(filters):
	if filters.get("company_name"):
		wallet_company = filters.get("company_name")
	if filters.get("from_date"):
		start_date = filters.get("from_date")
	if filters.get("to_date"):
		end_date = filters.get("to_date")
	if filters.get("currency"):
		currency = filters.get("currency")
	
	return get_company_statement_response(start_date, end_date, currency, wallet_company)


def get_company_statement_response(start_date, end_date, currency, wallet_company, error_message=None):
	sdk = init_default_sdk(CompanySDK, wallet_company)
	sdk_res = sdk.get_agent_statement(start_date, end_date, currency, error_message=error_message)
	res = sdk_res.json
	if not res.get("status") or not res.get("data"):
		error_msg = res.get("error", _("An unknown error occurred."))
		frappe.throw(error_msg)

	statement_data = res["data"].get("statement")
	if not statement_data:
		frappe.throw(_("There is no statements data!"))

	for item in statement_data:
		item["createtime"] = clean_and_parse_datetime(item["createtime"])
		if "receiverData" in item:
			item["firstName"] = "{} {}".format(item["receiverData"].get("firstName", ""), item["receiverData"].get("familyName", ""))
			item["phone"] = item["receiverData"].get("phone")
		if "senderData" in item:
			item["sender_firstName"] = "{} {}".format(item["senderData"].get("firstName", ""), item["senderData"].get("familyName", ""))
		
	return statement_data


def get_columns(filters):
	return [
		{
			"fieldname": "issuerTrxRef",
			"label": _("Transaction Issuer Ref"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "createtime",
			"label": _("Transaction Date"),
			"fieldtype": "Datetime",
			"width": 200
		},
		{
			"fieldname": "accountNumber",
			"label": _("Account Number"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "accountName",
			"label": _("Account Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "transaction_type",
			"label": _("Transaction Type"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "DebitCredit",
			"label": _("Transaction D/C"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 180
		},
		{
			"fieldname": "commissionCredit",
			"label": _("Commission Credit"),
			"fieldtype": "Currency",
			"width": 200,
			"options": "currency"
		},
		{
			"fieldname": "commissionDebit",
			"label": _("Commission Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"fieldname": "remark",
			"label": _("Remark"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 200
		},
		{
			"fieldname": "firstName",
			"label": _("Receiver Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "phone",
			"label": _("Reciever Mobile"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "sender_firstName",
			"label": _("Sender Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "billRef",
			"label": _("Bill Ref"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "service",
			"label": _("Service"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "toMemberName",
			"label": _("Business partner"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "acquirerTrxRef",
			"label": _("Reference of Transaction"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "walletSrc",
			"label": _("Wallet Source"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "walletDest",
			"label": _("Wallet Destination"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "posid",
			"label": _("Point Of Service"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "status",
			"label": _("Transaction Status"),
			"fieldtype": "Data",
			"width": 200,
			"options": "currency"
		},
		{
			"fieldname": "internal_user",
			"label": _("Internal User"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "external_user",
			"label": _("External User"),
			"fieldtype": "Data",
			"width": 200
		},

	]
