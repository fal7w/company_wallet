// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.query_reports["Wallet Company Balance"] = {
	"filters": [
		{
			"fieldname": "company_name",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Wallet Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("wallet_company")
		},
	]
};
