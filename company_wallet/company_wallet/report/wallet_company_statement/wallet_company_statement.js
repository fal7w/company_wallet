// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.query_reports["Wallet Company Statement"] = {
	"filters": [
		{
			"fieldname": "company_name",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Wallet Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("wallet_company")
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname": "currency",
			"label": __("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"reqd": 1,
			"default": frappe.defaults.get_default("Currency")
		},
	]
};
