# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from company_wallet.api.utils import unify_response
from frappe.utils.data import cint


TRANSACTION_TYPE_MAP = {
	"Fund transfer": "تحويل لمشترك جوالي",
	"Cash In": "ايداع نقدي",
	"Cash out": "سحب نقدي",
	"Cashwithdrawal": "سحب نقدي",
	"Bill payment": "سداد فواتير",
	"Mobile etopup": "شحن باقات",
	"incoming remitance": "ارسال حوالة",
	"Adjustment": "تسوية",
	"Registration/approval": "تسجيل عميل / تفعيل",
	"Depot sur wallet": "ايداع نقدي",
}


def map_transaction_type(transaction_type):
	return TRANSACTION_TYPE_MAP.get(transaction_type, transaction_type)


def execute(filters=None):
	validate_filters(filters)
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_qb_tables():
	return dict(
		statement_account_tb=frappe.qb.DocType("Wallet Company Transaction Log")
		)


def validate_filters(filters):
	if filters.get("from_date") > filters.get("to_date"):
		frappe.throw(_("From Date cannot be greater than To Date"))


@unify_response()
def get_data(filters):
	return get_company_statement_response(filters)


def get_company_statement_response(filters):
	opening_balance = _get_opening_balance(filters)

	balance = opening_balance

	transactions = _get_transactions(filters)

	results = []
	
	results.append({
		'createtime': '',
		'transaction_type': frappe.bold(_('Opening Balance')),
		'issuerTrxRef': '',
		'debit': opening_balance if opening_balance > 0 else 0,
		'credit': opening_balance if opening_balance < 0 else 0,
		'balance': opening_balance
	})
	
	total_debit = opening_balance if opening_balance > 0 else 0
	total_credit = - opening_balance if opening_balance < 0 else 0
	# total_commission = 0
	# total_balance = opening_balance


	for trx in transactions:
		# commission_debit = cint(trx.get("commission_debit", 0))
		debit = cint(trx.get("debit", 0))
		credit = cint(trx.get("credit", 0))

		balance += debit - credit
		total_debit += debit
		total_credit += credit
		# total_commission += commission_debit
		# total_balance += balance

		results.append({
			'issuerTrxRef': trx.get("issuerTrxRef"),
			'createtime': trx.get("createtime"),
			'name': trx.get("name"),
			'transaction_type': map_transaction_type(trx.get("transaction_type")),
			'remark': trx.get("remark"),
			'receiver_phone_number': trx.get("receiver_phone_number"),
			# 'commission_debit': commission_debit,
			'amount': debit if debit else credit,
			# 'debit': debit + commission_debit if debit else 0,
			'debit': debit,
			'credit': credit,
			'balance': balance,
		})

	results.append({
		'createtime': '',
		'transaction_type': frappe.bold(_('Total')),
		'issuerTrxRef': '',
		# 'commission_debit': total_commission,
		'amount': total_debit + total_credit,
		'debit': total_debit,
		'credit': total_credit,
		'balance': total_debit - total_credit,
	})	

	return results


def _get_opening_balance(filters):
	from frappe.query_builder.functions import Sum, Coalesce
	tb = get_qb_tables()
	locals().update(tb)
	query = (
		frappe.qb.from_(tb['statement_account_tb'])
		.select(Sum(Coalesce(tb['statement_account_tb'].debit_amount, 0) - Coalesce(tb['statement_account_tb'].credit_amount, 0)).as_("opening_balance"))
		.where(
			(tb['statement_account_tb'].createtime <= filters.get("from_date"))
			# | (tb['statement_account_tb'].createtime <= filters.get("to_date"))
			& (tb['statement_account_tb'].status == 'ACCEPTED')
			& (tb['statement_account_tb'].wallet_company == filters.get("wallet_company"))
			& (tb['statement_account_tb'].currency == filters.get("currency"))
		)
		.orderby(tb['statement_account_tb'].createtime)
	)
	result = query.run(as_dict=True)
	return result[0]['opening_balance'] if result and result[0]['opening_balance'] is not None else 0


def _get_transactions(filters):
	tb = get_qb_tables()
	locals().update(tb)
	query = (
		frappe.qb.from_(tb['statement_account_tb'])
		.select(tb['statement_account_tb'].name)
		.select(tb['statement_account_tb'].currency)
		.select(tb['statement_account_tb'].remark)
		.select(tb['statement_account_tb'].transaction_type)
		.select(tb['statement_account_tb'].createtime)
		.select((tb['statement_account_tb'].issuertrxref).as_("issuerTrxRef"))
		.select(tb['statement_account_tb'].debit_amount.as_("debit"))
		.select(tb['statement_account_tb'].credit_amount.as_("credit"))
		.select(tb['statement_account_tb'].commission_debit)
		.select(tb['statement_account_tb'].receiver_phone_number)
		.where(
			(tb['statement_account_tb'].createtime >= filters.get("from_date"))
			& (tb['statement_account_tb'].createtime <= filters.get("to_date"))
			& (tb['statement_account_tb'].status == 'ACCEPTED')
			& (tb['statement_account_tb'].wallet_company == filters.get("wallet_company"))
			& (tb['statement_account_tb'].currency == filters.get("currency"))
		)
		.orderby(tb['statement_account_tb'].createtime)
	)
	return query.run(as_dict=1)


def get_columns(filters):
	columns = [
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 200,
			"hidden": 1
		},
		{
			"fieldname": "createtime",
			"label": _("Transaction Date"),
			"fieldtype": "Datetime",
			"width": 200
		},
		{
			"fieldname": "name",
			"label": _("Transaction ID"),
			"fieldtype": "Link",
			"width": 200,
			"options": "Wallet Company Transaction Log"
		},
		{
			"fieldname": "transaction_type",
			"label": _("Transaction Type"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "issuerTrxRef",
			"label": _("Transaction Issuer Ref"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "receiver_phone_number",
			"label": _("Receiver Phone Number"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "remark",
			"label": _("Remark"),
			"fieldtype": "Data",
			"width": 200
		},
		# {
		# 	"fieldname": "commission_debit",
		# 	"label": _("Commission"),
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 200
		# },
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"fieldname": "balance",
			"label": _("Balance"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
	]
	return columns