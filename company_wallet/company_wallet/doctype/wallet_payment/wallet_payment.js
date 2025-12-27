// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Wallet Payment", {
	setup: function(frm) {
		frm.trigger("set_filters");
	},

	refresh: function(frm) {
		if (frm.is_new()) {
			frm.set_value("fee_currency", null);
		}
		frm.trigger("add_buttons");
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
				frm.trigger("add_get_balance_button");}
	}
	},
	add_submit_buttons: function(frm){
		frm.add_custom_button(__("Create Query Reference"), function(){show_create_dialog(frm);});
		frm.add_custom_button(__("Check Status"), function(){check_status(frm);});
	},
	add_get_balance_button: function(frm){
		frm.add_custom_button(__("Check Balance"), function(){get_balance(frm);});
	},
	currency: function(frm){
		frm.trigger("set_dynamic_field_label");
	},
	set_dynamic_field_label: function(frm) {
		frm.set_df_property("currency", "label", __("Currency") + " - " + frm.doc.currency);
	},
	payment_channel: function(frm){
		frm.set_value("remittance_provider", null);
	},
	recipient_phone : function(frm){
		frm.set_value("customer", null);
		frm.set_value("recipient", null);
	},
	set_filters: function(frm) {
		frm.set_query("wallet_provider", function(doc) {
			return {
				filters: {
					service_type: doc.payment_channel
				}
			}
		});
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
		],
		primary_action_label: __("Search"),
		primary_action: function(values){
			create_query_reference(values["transaction_number"], function(){create_dialog.hide();});
		},
	});

	create_dialog.show();
	return create_dialog;
}
function create_query_reference(transaction_number, final_action){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.payment_query_reference.payment_query_reference.create_payment_query_reference",
		args: {
			transaction_number: transaction_number,
		},
		callback: function(r){
			final_action();
			if (r.message.name){
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

function check_status(frm){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.wallet_payment.wallet_payment.check_status",
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
