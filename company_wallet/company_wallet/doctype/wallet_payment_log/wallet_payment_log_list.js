// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.listview_settings["Wallet Payment Log"] = {
	get_indicator(doc) {
		if ( doc.status == "Failed"){ 
			return [__("Failed"), "red", "status,=,Failed|docstatus,=,1"];
		}
		else if (doc.status == "Success") {
			return [__("Success"), "green", "docstatus,=,1"];
		}
	},
	has_indicator_for_draft: true,
	onload(listview) {
		listview.page.add_action_item(__('Retry Transaction'), function() {
		const selected_docs = listview.get_checked_items();
		if (selected_docs.length > 0) {
			if (selected_docs.some(doc => doc.status === "Success")){
				frappe.throw(__('Please select only failed documents.'));
			}
				frappe.confirm(
					__('Are you sure you want to retry transaction for the selected documents?'),
					function() {
						frappe.call({
							method: 'company_wallet.company_wallet.doctype.wallet_payment_log.wallet_payment_log.retry_transactions',
							args: {
								docs: selected_docs.map(doc => doc.name)
							},
							freeze: true,
							freeze_message: __("Retry send transaction, please wait..."),
							callback: function(response) {
								if (!response.exc) {
									frappe.msgprint(__('Transactions retried successfully.'));
									listview.reload();
								}
							}
						});
					}
				);
		} else {
			frappe.msgprint(__('Please select at least one document.'));
		}
	});
	}
	}
