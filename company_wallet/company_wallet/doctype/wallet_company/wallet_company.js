// Copyright (c) 2024, fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on('Wallet Company', {
	setup: function(frm) {
		if(frappe.user_roles.includes("System Manager")){
			frappe.call({
				method: "company_wallet.company_wallet.doctype.wallet_company.wallet_company.copy_paths",
				args: {
					docname: frm.doc.name,
				},
				callback: function(r) {
					frm.set_value("path_copy", r.message);
					frm.refresh()

			}
			});
	}
	},
	refresh: function(frm) {
		if(frappe.perm.has_perm("Wallet Company",0, "write")){
			frm.trigger("add_buttons");
		}
	},
	add_buttons: function(frm) {
		frm.add_custom_button(__("Update Wallet Password"), function(){update_wallet_user(frm)}, __("Action"))
		frm.add_custom_button(__("Update API User"), function(){update_api_user(frm)}, __("Action"))
		frm.add_custom_button(__("Update Authentication Token"), function(){update_auth_token(frm)}, __("Action"))
	},
});


function update_wallet_user(frm){
	_update_user_dialog(frm, "update_wallet_password");
}


function update_api_user(frm){
	_update_user_dialog(frm, "update_api_user");
}


function update_auth_token(frm){
	_update_wallet_company(frm, "update_auth_token");
}

function _update_user_dialog(frm, action){
	let dialog = new frappe.ui.Dialog({
		title: action == "update_api_user"? __("Update API User") : __("Update Wallet Password"),
		fields:[
			{
				label: __("Wallet Identifier"),
				fieldname: "wallet_identifier",
				fieldtype: "Data",
				reqd: action == "update_api_user",
				// read_only: action == "update_api_user",
				hidden: action != "update_api_user",
				default: frm.doc.wallet_identifier
			},
			{
				label: __("Orginaztion ID"),
				fieldname: "org_id",
				fieldtype: "Data",
				reqd: action == "update_api_user",
				// read_only: action == "update_api_user",
				hidden: action != "update_api_user",
				default: frm.doc.organization_id
			},
			{
				label: __("Username"),
				fieldname: "username",
				fieldtype: "Data",
				reqd: action == "update_api_user",
				read_only: action != "update_api_user",
				hidden: action != "update_api_user",
			},
			{
				label: __("Password"),
				fieldname: "password",
				fieldtype: "Password",
				reqd: 1,
			},
		],
		primary_action_label: __("Update"),
		primary_action: function(values){
			_update_wallet_company(frm, action, values).then(function(){dialog.hide();});
		},
	});

	dialog.show();
	return dialog;
}


function _update_wallet_company(frm, action, args=null){
	return frappe.call({
		"method": `company_wallet.company_wallet.doctype.wallet_company.wallet_company.${action}`,
		args: {
			...args,
			"wallet_company": frm.doc.name,
		},
		freeze: 1,
		callback: function(){
			frm.reload_doc();
		},
	});
}
