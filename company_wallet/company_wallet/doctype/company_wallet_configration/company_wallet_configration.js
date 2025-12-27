// Copyright (c) 2024, fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company Wallet Configration', {
	refresh: function(frm) {
		frm.trigger("change_password_label");
		frm.trigger("change_user_name_label");
		frm.trigger("add_buttons");
	},
	authentication_type: function(frm){
		frm.set_value("password", null);
		frm.set_value("user_name", null);
		frm.trigger("change_password_label");
		frm.trigger("change_user_name_label");
	},
	change_password_label: function(frm){
		if (frm.doc.authentication_type == "Basic"){
			frm.set_df_property("password", "label", __("Password"));
		}
		else{
			frm.set_df_property("password", "label", __("Token"));
		}
	},
	change_user_name_label: function(frm){
		if (frm.doc.authentication_type == "Basic"){
			frm.set_df_property("user_name", "label", __("User Name"));
		}
		else{
			frm.set_df_property("user_name", "label", __("Key"));
		}
	},
	add_buttons: function(frm){
		frm.trigger("add_check_button");
	},
	add_check_button: function(frm){
		frm.add_custom_button(__("Check Connection"), function(){check_ping_pong_api(frm);});
	},
});
function check_ping_pong_api(frm){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.company_wallet_configration.company_wallet_configration.check_ping_pong",
		args: {
			docname: frm.doc.name
		},
		freeze: true,
		freeze_message: __("Checking status, please wait..."),
		callback: function(r) {
			if (!r.exc) {
				frappe.msgprint(__("Connection checked successfully."));
			}
		}
	});
}