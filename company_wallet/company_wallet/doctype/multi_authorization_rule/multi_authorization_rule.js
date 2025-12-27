// Copyright (c) 2023, Fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on('Multi Authorization Rule', {
	refresh: function(frm) {
		frm.trigger("fields_filter");
		frm.trigger("transaction");
	},
	fields_filter: function(frm){
		frm.set_query("transaction", function(doc){
			return {
				filters: {
					is_submittable: 1,
					istable: 0,
					issingle: 0,
					is_virtual: 0,
					name: ["in", ["Wallet Payment", "Wallet Bulk Payment"]]
				}
				// filters: [
				// 	["DocType", "is_submittable", "=", 1],
				// 	["DocType", "istable", "=", 0],
				// 	["DocType", "issingle", "=", 0],
				// 	["DocType", "is_virtual", "=", 0],
				// 	["DocField", "fieldtype", "=", "Currency"],
				// ]
			};
		});
	},
	transaction: function(frm){
		frm.set_fields_as_options("based_on", frm.doc.transaction, (df) => df.fieldtype == "Currency").then(
			(options) => {
				options.forEach(function(i, index){
					i.label = __(i.label) + " (" + i.value + ") " ;
				});

				frm.set_df_property(
					"based_on",
					"options",
					[""].concat(options)
				);
			}
		);
	},
});
