# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from company_wallet.connect_sdk.company import CompanySDK
from company_wallet.connect_sdk import init_default_sdk
from company_wallet.api.utils import unify_response


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


@unify_response()
def get_data(filters):
	if filters.get("company_name"):
		wallet_company = filters.get("company_name")
		return get_agent_balance_response(wallet_company=wallet_company)


def get_agent_balance_response(error_message=None, wallet_company=None):
	sdk = init_default_sdk(CompanySDK, wallet_company)
	sdk_res = sdk.get_agent_balance(error_message=error_message)
	if sdk_res:
		res = sdk_res.json
		balance_data = res.get("data", [])
		if balance_data:
			for i in balance_data:
				i["accountNumber"] = i.get("accountNumber")
				i["accountName"] = i.get("accountName")
				i["balance"] = i.get("balance")
				i["currency"] = i.get("currency")
		else:
			frappe.throw(_(res["error"]))
			
		return balance_data


def get_columns(filters):
	return [
		{
			"fieldname": "accountName",
			"label": _("Account Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "accountNumber",
			"label": _("Account Number"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "balance",
			"label": _("Balance"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 200
		},
	]

# def get_user
