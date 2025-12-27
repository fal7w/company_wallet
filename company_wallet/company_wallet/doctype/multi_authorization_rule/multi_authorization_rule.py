# Copyright (c) 2023, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, comma_or
from frappe.utils.data import now_datetime


class MultiAuthorizationRule(Document):
	def check_duplicate_entry(self):
		exists = frappe.db.exists(self.doctype, {
			"transaction": self.transaction,
			"based_on": self.based_on,
			"system_user": cstr(self.system_user),
			"system_role": cstr(self.system_role),
			"approving_user": cstr(self.approving_user),
			"approving_role": cstr(self.approving_role),
			"name": ["!=", self.name],
		})
		if exists:
			frappe.throw(_("Duplicate Entry. Please check Authorization Rule {0}").format(exists))

	def validate_rule(self):
		if not self.approving_role and not self.approving_user:
			frappe.throw(_("Please enter Approving Role or Approving User"))
		elif self.system_user and self.system_user == self.approving_user:
			frappe.throw(_("Approving User cannot be same as user the rule is Applicable To"))
		elif self.system_role and self.system_role == self.approving_role:
			frappe.throw(_("Approving Role cannot be same as role the rule is Applicable To"))
		# if self.approving_user:
		# 	user_roles = frappe.get_roles(self.approving_user)
		# 	if self.system_role in user_roles:
		# 		frappe.throw(_("Approving User cannot be same as role the rule is Applicable To (Role)"))

		doc_type = self.transaction
		meta = frappe.get_meta(doc_type)
		field = meta.get_field(self.based_on)
		if not field or (field and field.fieldtype != "Currency"):
			frappe.throw(_("Choose Currency Field"))

	def validate(self):
		self.check_duplicate_entry()
		self.validate_rule()


def _get_currency_of_field(doc, field):
	options = cstr(doc.meta.get_field(field).options)
	if options:
		if ":" in options:
			tokens = options.split(":")
			if len(tokens) > 2:
				doctype, field_of_name, currency_field = tokens
				currency = frappe.get_value(doctype, doc.get(field_of_name), currency_field)
				return currency
			else:
				frappe.throw(_("Cannot get currency review option of {field} in customize").format(
					field=field
				))
		else:
			return doc.get(options)
	else:
		if doc.get("company"):
			from erpnext import get_company_currency
			return get_company_currency(doc.get("company"))
		else:
			return frappe.defaults.get_user_default("currency")


def _applied_to_currency(test_currency, target_currency):
	return not test_currency or test_currency == target_currency


def validate_transaction(doc, method=None):
	transaction_type = doc.doctype
	user_roles = frappe.get_roles()
	user = frappe.session.user

	# TODO: check if doctype has role to be check in otherwise exsit

	auth_rules = frappe.get_all("Multi Authorization Rule", fields=[
			"name",
			"wallet_company as company",
			"approving_role",
			"approving_user",
			"based_on",
			"value",
			"all_currencies",
			"currency",
		],
		filters={
			"disabled": 0,
			"transaction": transaction_type,
			"per": "Transaction",
		},
		or_filters={
			"system_role": ["in", user_roles],
			"system_user": user
		}
	)
	
	for i in auth_rules:
		if flt(doc.get(i["based_on"])) > flt(i["value"]):
			if not doc.get("wallet_company") or doc.get("wallet_company") == i["company"]:
				if i["all_currencies"] or _applied_to_currency(_get_currency_of_field(doc, i["based_on"]), i["currency"]):
					approver = []
					if cstr(i["approving_role"]) not in user_roles and i["approving_user"] != user:
						if cstr(i["approving_role"]) and cstr(i["approving_role"]) not in user_roles:
							approver.append(i["approving_role"])
						if i["approving_user"] and i["approving_user"] != user:
							approver.append(i["approving_user"])
						frappe.throw(_("Not authorized since {0} exceeds limits ,but can be approved by {1}")
							.format(_(i["based_on"]), comma_or(approver)))


def validate_day(doc, method=None):
	transaction_type = doc.doctype
	user_roles = frappe.get_roles()
	user = frappe.session.user

	auth_rules = frappe.get_all(
		"Multi Authorization Rule",
		fields=[
			"name",
			"wallet_company as company",
			"approving_role",
			"approving_user",
			"based_on",
			"value",
			"all_currencies",
			"currency",
		],
		filters={
			"disabled": 0,
			"transaction": transaction_type,
			"per": "Day",
		},
		or_filters={
			"system_role": ["in", user_roles],
			"system_user": user,
		}
	)

	for rule in auth_rules:
		field_currency = _get_currency_of_field(doc, rule["based_on"])
		if rule["all_currencies"] or _applied_to_currency(field_currency, rule["currency"]):
			today = now_datetime().date()

			amount = frappe.db.get_value(
				doc.doctype,
				{
					"docstatus": 1,
					"currency": field_currency,
					"modified_by": user,
					"modified": ["between", [today, today]],
					"name": ["!=", doc.name],
				},
				f"sum({rule['based_on']})"
			)

			if amount is None:
				amount = 0

			amount += flt(doc.get(rule["based_on"]))
			
			if amount > flt(rule["value"]):
				if not doc.get("wallet_company") or doc.get("wallet_company") == rule["company"]:
					approver = []
					if cstr(rule["approving_role"]) not in user_roles and rule["approving_user"] != user:
						if cstr(rule["approving_role"]) and cstr(rule["approving_role"]) not in user_roles:
							approver.append(rule["approving_role"])
						if rule["approving_user"] and rule["approving_user"] != user:
							approver.append(rule["approving_user"])
						frappe.throw(_("Not authorized since {0} exceeds limits ,but can be approved by {1}")
							.format(_(rule["based_on"]), comma_or(approver)))