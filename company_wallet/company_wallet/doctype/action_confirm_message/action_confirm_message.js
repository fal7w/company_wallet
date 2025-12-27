// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Action Confirm Message", {
	setup: function(frm) {
		frm.set_query("document_type", function(doc) {
			return {
				filters: {
					issingle: 0,
					is_submittable: 1,
					istable: 0,
				}
			};
		});
	},
	view_properties: function (frm) {
		frappe.set_route("Form", "Customize Form", { doc_type: frm.doc.document_type });
	},
});
