// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

 frappe.ui.form.on("Wallet User", {
	 before_load: function (frm) {
		let update_tz_options = function () {
			frm.fields_dict.time_zone.set_data(frappe.all_timezones);
		};

		if (!frappe.all_timezones) {
			frappe.call({
				method: "frappe.core.doctype.user.user.get_timezones",
				callback: function (r) {
					frappe.all_timezones = r.message.timezones;
					update_tz_options();
				},
			});
		} else {
			update_tz_options();
		}
	},
 	refresh(frm) {
 		if (frm.is_new()) {
			frm.set_value("time_zone", frappe.sys_defaults.time_zone);
		}
		else{
			frm.add_custom_button(
				__("Reset Password"),
				function () {
					frappe.call({
						method: "company_wallet.company_wallet.doctype.wallet_user.wallet_user.generate_otp_and_send_mail",
						args: {
							user: frm.doc.user,
							email: frm.doc.email,
						},
						callback: function () {
							location.reload();
						  },
					});
				},
				__("Password")
			);
			if (frm.doc.otp){
				frm.add_custom_button(__("Create New Password"), function(){show_create_dialog(frm);});
			}
			if (frm.doc.first_login){
				frm.add_custom_button(__("Initialize Password"), function(){
					frappe.call({
						method: "company_wallet.company_wallet.doctype.wallet_user.wallet_user.initialize_password",
						args: {
							user: frm.doc.user,
						},
						callback: function () {
						  },
					});
				});
			}
		}
		
		frm.trigger("time_zone");
 	},
 	time_zone: function (frm) {
		if (frm.doc.time_zone && frm.doc.time_zone.startsWith("Etc")) {
			frm.set_df_property(
				"time_zone",
				"description",
				__("Note: Etc timezones have their signs reversed.")
			);
		}
	},
 	after_save: function (frm) {
		/**
		 * Checks whether the effective value has changed.
		 *
		 * @param {Array.<string>} - Tuple with new override, previous override,
		 *   and optionally fallback.
		 * @returns {boolean} - Whether the resulting value has effectively changed
		 */
		const has_effectively_changed = ([new_override, prev_override, fallback = undefined]) => {
			const prev_effective = prev_override || fallback;
			const new_effective = new_override || fallback;
			return new_override !== undefined && prev_effective !== new_effective;
		};

		const doc = frm.doc;
		const boot = frappe.boot;
		const attr_tuples = [
			[doc.language, boot.user.language, boot.sysdefaults.language],
			[doc.time_zone, boot.time_zone.user, boot.time_zone.system],
		];

		if (doc.name === frappe.session.user && attr_tuples.some(has_effectively_changed)) {
			frappe.msgprint(__("Refreshing..."));
			window.location.reload();
		}

	let input_name = frm.doc.email
	let docname = frm.doc.name

	const reload_form = (input_name) => {
	$(document).trigger("rename", [frm.doctype, docname, input_name]);
	if (locals[frm.doctype] && locals[frm.doctype][docname])
		delete locals[frm.doctype][docname];
	frm.reload_doc();
	};
	if (input_name != docname) {
		frm.rename_notify(frm.doctype, input_name, docname);
		reload_form(input_name);
		// frappe.show_alert({
		// 	message: __("Document renamed from {0} to {1}", [
		// 		docname.bold(),
		// 		input_name.bold(),
		// 	]),
		// 	indicator: "success",
		// });
		frm.refresh();
	 }
	},

 });
 function show_create_dialog(frm){
	let create_dialog = new frappe.ui.Dialog({
		title: __("Create New Password"),
		fields:[
			{
				fieldtype: "Section Break",
				label: __("Set New Password"),
			},
			{
				label: __("New Password"),
				fieldname: "new_password",
				fieldtype: "Password",
				reqd: 1,
			},
			{
				label: __("Confirm Password"),
				fieldname: "confirm_password",
				fieldtype: "Password",
				reqd: 1,
			},
			{
				label: __("OTP"),
				fieldname: "otp",
				fieldtype: "Data",
				reqd: 1,
			},
			{
				label: __("username"),
				fieldname: "username",
				fieldtype: "Data",
				read_only: 1,
				default: frm.doc.user
			},
		],
		primary_action_label: __("Save"),
		primary_action: function(values){
			if (values.new_password !== values.confirm_password) {
				frappe.msgprint(__("Passwords do not match"));
				return;
			}
			save_new_password(values["username"],values["new_password"],values["otp"], function(){create_dialog.hide();});
		},
	});

	create_dialog.show();
	return create_dialog;
}

function save_new_password(user, new_password, otp, final_action){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.wallet_user.wallet_user.set_new_password",
		args: {
			user: user,
			new_password: new_password,
			otp: otp,
		},
		callback: function(r) {
			final_action();
			if (!r.exc) {
				location.reload();
		}
	}
	});
}