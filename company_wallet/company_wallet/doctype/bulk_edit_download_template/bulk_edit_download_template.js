// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Edit Download Template", {
	refresh: function(frm) {
		frm.set_query("document_type", {istable: 1});

		frm.trigger("add_multi_check_field");
	},
	document_type: function (frm) {
		frm.trigger("add_multi_check_field");
	},

	add_multi_check_field: function(frm) {
		frm.fields_dict.fields_html.$wrapper.html("");
		if (frm.doc.document_type){
			frappe.model.with_doctype(frm.doc.document_type, function() {
				frm._multi_select = frappe.ui.form.make_control({
					df: {
						label: __(frm.doc.document_type),
						fieldname: "select_fields",
						fieldtype: "MultiCheck",
						reqd: 1,
						columns: 3,
						options: get_multicheck_options(frm.doc.document_type),
						select_all: 1,
					},
					parent: frm.fields_dict.fields_html.$wrapper,
					render_input: true
				});
				let fields = JSON.parse(frm.doc.fields || "[]");
				let selector = [];

				$.each(fields, (i, field) => {
					selector.push(`[data-unit=${field}]:checkbox`)
				});

				frm._multi_select.$checkbox_area.find(selector.join(",")).prop("checked", true).trigger("change")
			});
		}
	},
	before_save: function (frm) {
		let fields = frm._multi_select?.get_value() || [];
		fields = fields?.length ? fields : undefined;
		frm.set_value("fields", JSON.stringify(fields));
	}
});

function get_multicheck_options(doctype, child_fieldname = null) {
	let column_map = get_columns_for_picker(doctype);

	let autoname_field = null;
	let meta = frappe.get_meta(doctype);
	if (meta.autoname?.startsWith("field:")) {
		let fieldname = meta.autoname.slice("field:".length);
		autoname_field = frappe.meta.get_field(doctype, fieldname);
	}

	let fields = child_fieldname ? column_map[child_fieldname] : column_map[doctype];

	let is_field_mandatory = (df) => {
		if (df.reqd) {
			return true;
		}
		else if (autoname_field && df.fieldname == autoname_field.fieldname) {
			return true;
		}
		else {
			return df.fieldname === "name";
		}
	};

	return fields
		.filter((df) => {
			return ! (autoname_field && df.fieldname === "name")
		})
		.map((df) => {
			return {
				label: __(df.label, null, df.parent),
				value: df.fieldname,
				danger: is_field_mandatory(df),
				checked: false,
				description: `${df.fieldname} ${df.reqd ? __("(Mandatory)") : ""}`,
			};
		});
}


function get_columns_for_picker(doctype) {
	let out = {};

	const exportable_fields = (df) => {
		let keep = true;
		if (frappe.model.no_value_type.includes(df.fieldtype)) {
			keep = false;
		}
		if (["lft", "rgt"].includes(df.fieldname)) {
			keep = false;
		}
		if (df.is_virtual) {
			keep = false;
		}
		return keep;
	};

	// parent
	let doctype_fields = frappe.meta.get_docfields(doctype).filter(exportable_fields);

	out[doctype] = [
		{
			label: __("ID"),
			fieldname: "name",
			fieldtype: "Data",
			reqd: 1,
		},
	].concat(doctype_fields);

	// children
	const table_fields = frappe.meta.get_table_fields(doctype);
	table_fields.forEach((df) => {
		const cdt = df.options;
		const child_table_fields = frappe.meta.get_docfields(cdt).filter(exportable_fields);

		out[df.fieldname] = [
			{
				label: __("ID"),
				fieldname: "name",
				fieldtype: "Data",
				reqd: 1,
			},
		].concat(child_table_fields);
	});

	return out;
}