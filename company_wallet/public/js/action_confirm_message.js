// Copyright (c) 2023, Fintechsys and contributors
// For license information, please see license.txt

frappe.provide("frappe.boot.action_confirm_message");

for (let k in frappe.boot.action_confirm_message){
	frappe.ui.form.on(k, {
		onload: function(frm){
			let message = frappe.boot.action_confirm_message[k];
			if (typeof(message) == "object"){
				_overwrite_action(frm, message, "submit", "savesubmit");
			}
		},
	});
}


function _overwrite_action(frm, message, action_key, action_fun){
	let action_message = message[action_key];

	if (action_message){
		let old_action = frm[action_fun];

		frm[action_fun] = function(){
			let old_confirm = frappe.confirm;
			frappe.confirm = function(){
				arguments[0] = frappe.render_template(action_message, {doc: frm.doc});
				old_confirm.apply(this, arguments);
			}
			old_action.apply(this, arguments);
			frappe.confirm = old_confirm;
		}
	}
}