// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Wallet Bulk Payment", {
	refresh: function(frm) {
		if (frm.is_new()) {
			frm.set_value("fee_currency", null);
			frm.trigger("get_currency_categories");
		}
		frm.trigger("add_buttons");
		
	},
	setup: function(frm) {
		frm.trigger("show_progress");
		frm.trigger("set_filters");
	},
	show_progress: function(frm){
		frappe.realtime.on('wallet_bulk_payment_process', data => {
			let timeoutID;
			clearTimeout(timeoutID);
			// frm.import_in_progress = true;
			if (data.docname !== frm.doc.name) {
				return;
			}
			let percent = Math.floor((data.current * 100) / data.total);
			let message;
			if (data.success) {
				let message_args = [data.current, data.total, /* eta_message */];
				message = __(data.message, message_args);
			}

			frm.dashboard.show_progress(__('Submit Progress'), percent, message);
			frm.page.set_indicator(__('In Progress'), 'orange');

			// hide progress when complete
			if (data.current === data.total) {
				timeoutID = setTimeout(() => {
						frm.dashboard.hide();
						frm.refresh();
					}, 4000);
			}
		});
	},
	before_submit: function(frm){
		return new Promise((resolve) => {
			frappe.prompt(
				{
					fieldname: "password",
					label: __("Enter your password"),
					fieldtype: "Password",
					reqd: 1
				},
				function(data) {
					frappe.call({
						method: "company_wallet.company_wallet.doctype.wallet_payment.wallet_payment.check_user_password",
						args: {
							password: data.password
						},
						callback: function(r) {
							if (!r.exc) {
								resolve();
							}
						}
					});
				},
				__("Verify Password"),
				__("Verify")
			);
		});
		},
	add_buttons: function(frm){
		if (frm.doc.docstatus >= 1 && frm.doc.status != "Rejected") {
			frm.trigger("add_submit_buttons");
		}
		if (!frm.is_new()){
			if (frm.doc.status == "Draft" || frm.doc.docstatus == 0){
			frm.trigger("add_get_balance_button");
			frm.trigger("add_get_customer_button");
			frm.trigger("add_get_commission_amounts");
			}
		}
	},
	add_submit_buttons: function(frm){
		frm.add_custom_button(__("Create Query Reference"), function(){show_create_dialog(frm);});
		frm.add_custom_button(__("Check Status"), function(){check_status(frm);});
	},
	add_get_balance_button: function(frm){
		frm.add_custom_button(__("Check Balance"), function(){get_balance(frm);});
	},
	add_get_customer_button: function(frm){
		frm.add_custom_button(__("Get Customer Info"), function(){get_bulk_payment_beneficiary(frm);});
	},
	add_get_commission_amounts: function(frm){
		frm.add_custom_button(__("Get Commissions"), function(){get_commissions(frm);});
	},
	currency: function(frm){
		frm.trigger("set_dynamic_field_label");
	},
	set_dynamic_field_label: function(frm) {
		frm.set_df_property("currency", "label", __("Currency") + " - " + frm.doc.currency);
	},
	bulk_payment_template: function(frm){
		frm.trigger("set_bulk_payment_template");
	},
	set_bulk_payment_template: function(frm){
		frm.set_value("wallet_bulk_payment_transactions", null);
		frm.call("import_bulk_template");
	},
	get_bulk_payment_template: async function(frm){
		await frappe.call({
			doc: frm.doc,
			method: "import_bulk_template",
		});
		frm.refresh_field("wallet_bulk_payment_transactions");
	},
	payment_channel: function(frm){
		frm.set_value("remittance_provider", null);
	},
	set_filters: function(frm) {
		frm.set_query("wallet_provider", function(doc) {
			return {
				filters: {
					service_type: doc.payment_channel
				}
			}
		});
	},
	total_fee: function(frm){
		frm.trigger("calculate_total_fee");
	},
	calculate_total_fee: function(frm) {
		let total_fee = 0;
		frm.doc.wallet_bulk_payment_transactions.forEach(function(d) {
			total_fee += d.fee_amount || 0;
		});
		frm.set_value('total_fee', total_fee);
	}
});

function show_create_dialog(frm){
	let create_dialog = new frappe.ui.Dialog({
		title: __("Create Query Payment"),
		autofocus: true,
		fields:[
			{
				fieldtype: "Section Break",
				label: __("Query Details"),
			},
			{
				label: __("Transaction Number"),
				fieldname: "transaction_number",
				fieldtype: "Data",
				reqd: 1,
				default: frm.doc.name
			},
			{
				label: __("Mobile Number"),
				fieldname: "mobile_number",
				fieldtype: "Data",
				reqd: 1,
				option: "Phone",
			},
		],
		primary_action_label: __("Search"),
		primary_action: function(values){
			create_query_reference(values["transaction_number"],values["mobile_number"], function(){create_dialog.hide();});
		},
	});

	create_dialog.show();
	return create_dialog;
}

function create_query_reference(transaction_number,mobile_number, final_action){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.payment_query_reference.payment_query_reference.create_payment_query_reference",
		args: {
			transaction_number: transaction_number,
			mobile_number: mobile_number
		},
		callback: function(r){
			final_action();
			if (r.message.name){
				console.log(r.message.name)
				route_to_query(r.message["name"])
			}
		},
		freeze: 1,
	});
}

function route_to_query(query){
	frappe.set_route("Form", "Payment Query Reference", query);
}

function get_balance(frm){
	frm.call({
		method: "get_balance",
		doc: frm.doc,
		freeze: true,
		freeze_message: __("Checking balance, please wait..."),
		callback: function(r) {
			if (!r.exc) { 
				frappe.msgprint(__("Balance checked successfully."));
			}
		}
	});

}

function get_bulk_payment_beneficiary(frm){
	frappe.call({
		method: "company_wallet.api.payment.get_bulk_payment_beneficiary",
		args: {
			name: frm.doc.name
		},
		// freeze: true,
		// freeze_message: __("Get Customers Names, please wait..."),
		callback: function(r) {
			if (!r.exc) { 
				frm.refresh_fields();
				// frappe.msgprint(__("Successfully retrieved customer info."));
			}
		}
	});
}




function get_commissions(frm){
	frm.call({
		method: "get_commission_amount",
		doc: frm.doc,
		args: {
			docname: frm.doc.name,
			wallet_company: frm.doc.wallet_company,
			payment_channel: frm.doc.payment_channel, 
			currency: frm.doc.currency, 
			remittance_provider: frm.doc.remittance_provider
		},
		// freeze: true,
		// freeze_message: __("Get Commissions, please wait..."),
		callback: function(r) {
			if (!r.exc) { 
				frm.refresh_fields();
				// frappe.msgprint(__("Successfully Done."));
			}
		}
	});
}

function check_status(frm){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.wallet_bulk_payment.wallet_bulk_payment.check_status",
		args: {
			docname: frm.doc.name
		},
		freeze: true,
		freeze_message: __("Checking status, please wait..."),
		callback: function(r) {
			if (!r.exc) {
				frm.reload_doc();
				// frappe.msgprint(__("Status checked successfully."));
			}
		}
	});
}
