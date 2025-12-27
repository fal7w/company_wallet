# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import datetime
import traceback
from company_wallet.api.settings import get_list_currency
from company_wallet.connect_sdk.company import CompanySDK
from company_wallet.connect_sdk import init_default_sdk
from company_wallet.api.utils import unify_response
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import timedelta
from frappe.utils import add_months, now_datetime, getdate


class WalletCompanyTransactionLog(Document):
	def insert(self, *args, **kwargs):
		exist_transaction = frappe.db.exists("Wallet Company Transaction Log", {
			"wallet_company": self.wallet_company,
			"issuertrxref": self.issuertrxref,
			"currency": self.currency
		})

		if exist_transaction:
			return

		super().insert(*args, **kwargs)


@unify_response()
def create_account_statement_log(doc=None, method=None, error_message=None):
	wallet_companies = frappe.get_all("Wallet Company", filters={"disabled": 0}, fields=["name", "creating_date_from_wallet_provider"])
	currencies = get_list_currency()
	for wallet_company in wallet_companies:
		try:
			start_date = get_last_create_time(wallet_company.get("name"))
			if not start_date:
				start_date = frappe.get_value("Wallet Company", wallet_company.get("name"), "creating_date_from_wallet_provider")
			end_date = now_datetime()

			periods = calculate_periods(start_date, end_date)
			
			sdk = init_default_sdk(CompanySDK, wallet_company.get("name"))
			for start_date, end_date in periods:
				for currency in currencies:
					try:
						sdk_res = sdk.get_agent_statement(getdate(start_date), getdate(end_date), currency, error_message=error_message)
						process_statement_data(sdk_res, wallet_company.get("name"))
					except Exception as e:
						error_details = {
							"error_message": str(e),
							"stack_trace": traceback.format_exc(),
							"wallet_company": wallet_company.get("name"),
							"start_date": start_date,
							"end_date": end_date,
							"currency": currency
						}
						frappe.log_error(frappe.as_json(error_details), _("Failed to fetch or process statement data"))
		except Exception as e:
			error_details = {
				"error_message": str(e),
				"stack_trace": traceback.format_exc(),
				"wallet_company": wallet_company.get("name")
			}
			frappe.log_error(frappe.as_json(error_details), _("Failed to process wallet company"))


def calculate_periods(start_date, end_date):
	periods = []
	current_start = start_date
	while current_start < end_date:
		current_end = min(add_months(current_start, 3) - timedelta(days=1), end_date)
		periods.append((current_start, current_end))
		current_start = add_months(current_start, 3)
	return periods


def process_statement_data(response, wallet_company):
	response = response.json
	data = response.get('data', {})
	if not response.get("status") or not data:
		frappe.log_error("error", _("An unknown error occurred, status is false or data is empty."))

	statement_data = data.get('statement', [])
	if not statement_data:
		frappe.log_error(_("No statement data found."), _("Data Processing Error"))
		return

	for item in statement_data:
		add_statement_data(item, wallet_company)


def get_last_create_time(wallet_company_name):
	last_create_time = frappe.db.get_value("Wallet Company Transaction Log",
										filters={"wallet_company": wallet_company_name},
										fieldname="createtime",
										order_by="createtime desc")

	return last_create_time


def clean_and_parse_datetime(datetime_str):
	cleaned_datetime = datetime_str.replace(': ', ':')
	return datetime.datetime.strptime(cleaned_datetime,'%d/%m/%y %H:%M:%S')


def add_statement_data(json_obj, wallet_payment):
	try:
		doc = frappe.get_doc({
			"doctype": "Wallet Company Transaction Log",
			"wallet_company": wallet_payment,
			"createtime": clean_and_parse_datetime(json_obj.get("createtime")),
			"debit_amount": json_obj.get("amount") if json_obj.get("DebitCredit") == 'D' else 0,
			"credit_amount": json_obj.get("amount") if json_obj.get("DebitCredit") == 'C' else 0,
			"commission_debit": json_obj.get("commissionDebit"),
			"commission_credit": json_obj.get("commissionCredit"),
			"remark": json_obj.get("remark"),
			"currency": json_obj.get("currency"),
			"transaction_type": json_obj.get("transaction_type"),
			"issuertrxref": json_obj.get("issuerTrxRef"),
			"refid": json_obj.get("refId"),
			"walletdest": json_obj.get("walletDest"),
			"walletsrc": json_obj.get("walletSrc"),
			"status": json_obj.get("status"),
			"r_firstname": json_obj.get("receiverData").get("firstName"),
			"r_fathername": json_obj.get("receiverData").get("fatherName") if json_obj.get("receiverData").get("fatherName") else "",
			"r_grandfathername": json_obj.get("receiverData").get("grandFatherName") if json_obj.get("receiverData").get("grandFatherName") else "",
			"r_familyname": json_obj.get("receiverData").get("familyName"),
			"receiver_phone_number": json_obj.get("receiverData").get("phone"),
			"s_firstname": json_obj.get("senderData").get("firstName"),
			"s_fathername": json_obj.get("senderData").get("fatherName") if json_obj.get("senderData").get("fatherName") else "",
			"s_grandfathername": json_obj.get("senderData").get("grandFatherName") if json_obj.get("senderData").get("grandFatherName") else "",
			"s_familyname": json_obj.get("senderData").get("familyName"),
		})
		doc.flags.ignore_permissions = True
		doc.submit()
		return doc
	except Exception:
		frappe.log_error(frappe.get_traceback(), _("Error adding statement data"))