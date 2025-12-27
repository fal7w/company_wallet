// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Query Reference", {

	show_express_number: function(frm) {
		toggle_password_visibility(frm);
	},
	// refresh: function(frm) {
	// }
});
function toggle_password_visibility(frm) {
	frappe.call({
		method: "company_wallet.company_wallet.doctype.payment_query_reference.payment_query_reference.get_password",
		args: {
			docname: frm.doc.name,
			field: 'express_number'
		},
		callback: function(r) {
			if(r.message) {
				frm.set_df_property('express_number','fieldtype', 'Data'); 
				frm.set_value('express_number', r.message);						
			}
		}
	});
}