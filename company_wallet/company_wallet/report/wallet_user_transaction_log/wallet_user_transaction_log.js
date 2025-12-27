// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.query_reports["Wallet User Transaction Log"] = {
	"filters": [
		{
			"fieldname": "wallet_company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Wallet Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("wallet_company"),
			"on_change": function() {
                frappe.query_report.set_filter_value('user', null);
                frappe.query_report.refresh();
            }
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
			"default": frappe.defaults.get_default("Currency")
		},
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "Wallet User",
			"get_query": function() {
                let wallet_company = frappe.query_report.get_filter_value('wallet_company');
                if(wallet_company) {
                    return {
                        filters: {
                            "wallet_company": wallet_company
                        }
                    }
				}
			}
		},
		{
			"fieldname": "transaction_type",
			"label": __("Transaction Type"),
			"fieldtype": "Select",
			"options": [
				"",
				"Wallet Payment",
				"Wallet Bulk Payment",
			]
		},
		{
			"fieldname": "payment_channel",
			"label": __("Payment Channel"),
			"fieldtype": "Link",
			"options": "Payment Channel",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": [
				"",
				"In progress",
				"Approved",
				"Success",
				"Rejected",
				"Failed",
				"Draft",
				"Not Found"
			]
		},
		{
			"fieldname": "remittance_provider",
			"label": __("Remittance Provider"),
			"fieldtype": "Link",
			"options": "Remittance Provider",
			"depends_on": "eval: doc.payment_channel == 'Remittance'"
		}
	]
};
