# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from company_wallet.api.utils import unify_response


def execute(filters=None):
	validate_filters(filters)
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def validate_filters(filters):
	if filters.get("from_date") > filters.get("to_date"):
		frappe.throw(_("From Date cannot be greater than To Date"))


@unify_response()
def get_data(filters):
	data = []
	filters_query = prepare_filters(filters)
	if filters.get("transaction_type") == 'Wallet Payment':
		data = _get_payments(filters_query)

	elif filters.get("transaction_type") == 'Wallet Bulk Payment':
		data = _get_bulk_payments(filters_query)
		
	else:  # no type has selected
		data = _get_all_payments(filters_query)
		
	return data


def prepare_filters(filters):
	allowed_filters = {
		"owner": filters.get("user"),
		"payment_channel": filters.get("payment_channel"),
		"remittance_provider": filters.get("remittance_provider"),
		"status": filters.get("status"),
		"currency": filters.get("currency"),
		"wallet_company": filters.get("wallet_company"),
		"docstatus": 1,
		"posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]]
	}

	return {k: v for k, v in allowed_filters.items() if v is not None}


def _get_payments(filters):
	wallet_payments = frappe.get_list("Wallet Payment", fields="*", filters=filters, order_by="creation desc")
	return wallet_payments


def _get_bulk_payments(filters):
	wallet_bulk_payments = frappe.get_list("Wallet Bulk Payment", fields="*", filters=filters, order_by="creation desc")
	return wallet_bulk_payments


def _get_all_payments(filters):
	combined_entries = []
	payments = _get_payments(filters)
	bulk_payments = _get_bulk_payments(filters)
	for payment in payments:
		payment["t_type"] = "Wallet Payment"
		payment["real_amount"] = payment["real_amount"] if payment["real_amount"] > 0 else payment["amount"]

	for bulk_payment in bulk_payments:
		bulk_payment["t_type"] = "Wallet Bulk Payment"
		bulk_payment["total_real_amount"] = bulk_payment["total_real_amount"] if bulk_payment["total_real_amount"] > 0 else bulk_payment["total"]

	combined_entries = payments + bulk_payments

	combined_entries.sort(key=lambda x: x["creation"], reverse=True)

	return combined_entries


def get_type_specific_columns(transaction_type):
	type_specific_columns = []
	if transaction_type == "Wallet Payment":
		type_specific_columns.append({"fieldname": "recipient", "label": _("Recipient Name"), "fieldtype": "Link", "options": "Currency", "width": 160})
		type_specific_columns.append({"fieldname": "recipient_phone", "label": _("Recipient Phone"), "fieldtype": "Data", "width": 180})
		type_specific_columns.append({"fieldname": "real_amount", "label": _("Amount"), "fieldtype": "Currency", "options": "currency", "width": 160})
		type_specific_columns.append({"fieldname": "fee_amount", "label": _("Fee Amount"), "fieldtype": "Currency", "options": "fee_currency", "width": 160})
		
	elif transaction_type == "Wallet Bulk Payment":
		type_specific_columns.append({"fieldname": "transaction_number", "label": _("Transaction Number"), "fieldtype": "Data", "options": "Wallet Bulk Payment", "width": 160})
		type_specific_columns.append({"fieldname": "total_real_amount", "label": _("Total Amount"), "fieldtype": "Currency", "options": "currency", "width": 160})
		type_specific_columns.append({"fieldname": "total_fee", "label": _("Total Fee Amount"), "fieldtype": "Currency", "options": "fee_currency", "width": 160})
	elif transaction_type == "generic":
		type_specific_columns.append({"label": _("Transaction Type"), "fieldname": "t_type", "fieldtype": "Select", "width": 100})
		type_specific_columns.append({"fieldname": "recipient", "label": _("Recipient Name"), "fieldtype": "Link", "options": "Currency", "width": 160})
		type_specific_columns.append({"fieldname": "recipient_phone", "label": _("Recipient Phone"), "fieldtype": "Data", "width": 180})
		type_specific_columns.append({"fieldname": "real_amount", "label": _("Amount"), "fieldtype": "Currency", "options": "currency", "width": 160})
		type_specific_columns.append({"fieldname": "fee_amount", "label": _("Fee Amount"), "fieldtype": "Currency", "options": "fee_currency", "width": 160})
		type_specific_columns.append({"fieldname": "transaction_number", "label": _("Transaction Number"), "fieldtype": "Data", "options": "Wallet Bulk Payment", "width": 160})
		type_specific_columns.append({"fieldname": "total_real_amount", "label": _("Total Amount"), "fieldtype": "Currency", "options": "currency", "width": 160})
		type_specific_columns.append({"fieldname": "total_fee", "label": _("Total Fee Amount"), "fieldtype": "Currency", "options": "fee_currency", "width": 160})
	return type_specific_columns


def get_columns(filters):
	columns = [
		{
			"fieldname": "creation",
			"label": _("Posting Date"),
			"fieldtype": "Datetime",
			"width": 160,
		},
		{
			"fieldname": "name",
			"label": _("Voucher No"),
			"fieldtype": "Dynamic Link",
			"width": 200,
			"options": "t_type"
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Select",
			"width": 160,
		},
		{
			"fieldname": "payment_channel",
			"label": _("Payment Channel"),
			"fieldtype": "Select",
			"width": 200,
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 160,
		},
		{
			"fieldname": "fee_currency",
			"label": _("Fee Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 160,
		},
		{
			"fieldname": "owner",
			"label": _("User Name"),
			"fieldtype": "Link",
			"options": "Wallet User",
			"width": 160,
		},
	]
	if filters.get("transaction_type"):
		columns += get_type_specific_columns(filters["transaction_type"])
	else:
		# If no specific type, consider adding columns for all types or a generic option
		columns += get_type_specific_columns("generic")

	return columns