// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Wallet Payment Log", {
	refresh(frm) {
		frm.trigger("add_buttons");
	},
	add_buttons: function(frm){
		if (frm.doc.docstatus >= 1 && frm.doc.status != "Rejected") {
			frm.trigger("add_submit_buttons");
		}
		if (frm.doc.status != "Success") {
		frm.trigger("add_retry_send_transaction_button");
		}
		
	},
	add_submit_buttons: function(frm){
		frm.add_custom_button(__("Check Status"), function(){check_status(frm);});
	},
	add_retry_send_transaction_button: function(frm){
		frm.add_custom_button(__("Retry Send Transaction"), function(){publish_payment_log(frm);});
	},
});
function check_status(frm){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.wallet_payment_log.wallet_payment_log.check_status",
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
	
function publish_payment_log(frm){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.wallet_payment_log.wallet_payment_log.publish_payment_log",
		args: {
			docs: frm.doc.name,
			parent: JSON.stringify({
				name: frm.doc.voucher_no,
				wallet_company: frm.doc.wallet_company,
				remittance_provider: frm.doc.service_provider,
				total_real_amount: frm.doc.total,
				real_amount: frm.doc.amount,
				currency: frm.doc.currency,
				total_fee: frm.doc.total_fee,
				fee_amount: frm.doc.fee_amount,
				payment_channel: frm.doc.payment_channel
			}),
			retry: true
		},
		freeze: true,
		freeze_message: __("Retry send transaction, please wait..."),
		callback: function(r) {
			console.log(r)
			if (!r.exc) {
				frm.reload_doc();
				// frappe.msgprint(__("Status checked successfully."));
			}
		}
		
	}
);
		
}	