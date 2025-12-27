frappe.provide("frappe.boot.export_child_table_format");

$(function(){
	let NewControlTable = class NewControlTable extends frappe.ui.form.ControlTable {
		refresh_input() {
			super.refresh_input();
			this.setup_allow_excel_bulk_edit()
		}

		setup_allow_excel_bulk_edit(){
			let child_table_format = frappe.boot.export_child_table_format;
			if (this?.frm?.get_docfield(this.df.fieldname)?.allow_bulk_edit) {
				if (child_table_format["cvs"] == "remove"){
					$(this.wrapper).find(".grid-upload, .grid-download").addClass("hidden");
				}
				if (child_table_format["excel"]){
					if (! $(this.wrapper).find(".grid-bulk-actions .grid-excel-download").length){
						$(this.wrapper).find(".grid-bulk-actions").append(`
							<button class="grid-excel-download btn btn-xs btn-secondary">
								${__("Download Excel")}
							</button>
							<button class="grid-excel-upload btn btn-xs btn-secondary">
								${__("Upload Excel")}
							</button>
						`)
					}

					$(this.wrapper).find(".grid-excel-upload, .grid-excel-download").removeClass("hidden");

					this.setup_upload_excel();
					this.setup_download_excel();
				}
			}
		}

		setup_upload_excel(){
			let me = this;
			$(this.wrapper).find(".grid-excel-upload").off("click");
			$(this.wrapper).find(".grid-excel-upload").click(function(){
				me.setup_data_importer();
			});
		}

		setup_data_importer() {
			let me = this;
			me.excel_data = null;
			me.excel_map_fields = null;

			me.file_uploader = new frappe.ui.FileUploader({
				as_dataurl: true,
				allow_multiple: false,
				restrictions: {
					allowed_file_types: [".xlsx", ".xls"],
				},
				on_success(file) {
					let type = null;

					if (file.file_obj.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"){
						type = "xlsx"
					}
					else if (file.file_obj.type == "application/vnd.ms-excel"){
						type = "xls"
					}
					else{
						type = `${file.file_obj.name}`.split(".").pop()
					}

					let table_field = me?.frm.get_docfield(me.df.fieldname);
					let doctype = table_field.options;
					frappe.call({
						method: "company_wallet.importer.get_child_table_as_array",
						args: {
							file_data: file.dataurl,
							type: type,
							doctype: doctype,
						},
						callback: function(r){
							if (r?.message?.columns){
								let data = r.message;
								me.excel_data = data
								me.excel_map_fields = me.get_map_fields(data.columns);
								me.map_dialog = new frappe.ui.Dialog(me.get_dialog_data(data.columns, doctype, me.excel_map_fields));
								for (let i in me.map_dialog.fields_dict){
									me.map_dialog.set_value(i, me.map_dialog.get_value(i));
								}
								me.map_dialog.show();
							}
						}
					})
				}
			});
		}

		upload_excel_data(values){
			let data = this.excel_data.data
			this.frm.clear_table(this.df.fieldname);
			const formatter_map = {
				Date: (val) => (val ? frappe.datetime.user_to_str(val) : val),
				Int: (val) => cint(val),
				Check: (val) => cint(val),
				Float: (val) => flt(val),
				Currency: (val) => flt(val),
			};
			$.each(data, (i, row) => {
				let d = this.frm.add_child(this.df.fieldname);
				$.each(row, (ci, field_value) => {
					if (values[ci] && values[ci] != "name") {
						let fieldtype = this.frm.get_field(this.df.fieldname).grid.get_docfield(values[ci]).fieldtype;
						d[values[ci]] = formatter_map[fieldtype]? formatter_map[fieldtype](field_value): cstr(field_value);
					}
				});
			});
			this.frm.refresh_field(this.df.fieldname);

		}

		setup_download_excel(){
			let me = this;
			$(this.wrapper).find(".grid-excel-download").off("click");
			$(this.wrapper).find(".grid-excel-download").click(function(){
				me.setup_data_exporter();
			});
		}
		setup_data_exporter(){
			frappe.require("data_import_tools.bundle.js", () => this._build_data_exporter_dialog());
		}

		_build_data_exporter_dialog(){
			const me = this;
			const table_field = me?.frm.get_docfield(me.df.fieldname);
			const doctype = table_field.options;
			let ChildDataExporter = class ChildDataExporter extends frappe.data_import.DataExporter {
				make_dialog() {
					super.make_dialog();
					me._add_template_field(this, table_field, doctype);

					this.dialog.set_value("file_type", "Excel");
					this.dialog.set_df_property("export_records", "read_only", 1);
					this.dialog.set_df_property("export_records", "hidden", 1);
					this.dialog.set_df_property("filter_area", "hidden", 1);
					this.dialog.set_value("export_records", "by_filter");
				}
				get_filters() {
					let res = super.get_filters();
					res.push([this.doctype, "parent", "=", me.frm.docname]);
					res.push([this.doctype, "parenttype", "=", me.frm.doctype]);
					res.push([this.doctype, "parentfield", "=", me.df.fieldname]);
					return res;
				}
				update_record_count_message() {
					let old_db_count = frappe.db.count;
					frappe.db.count = function(){return me.count(...arguments)}
					super.update_record_count_message();
					frappe.db.count = old_db_count;
				}

				export_records() {
					let method = "/api/method/company_wallet.importer.download_template";

					let multicheck_fields = this.dialog.fields
						.filter((df) => df.fieldtype === "MultiCheck")
						.map((df) => df.fieldname);

					let values = this.dialog.get_values();

					let doctype_field_map = {...values};
					for (let key in doctype_field_map) {
						if (!multicheck_fields.includes(key)) {
							delete doctype_field_map[key];
						}
					}

					let filters = null;
					if (values.export_records === "by_filter") {
						filters = this.get_filters();
					}

					open_url_post(method, {
						doctype: this.doctype,
						file_type: values.file_type,
						export_records: values.export_records,
						export_fields: doctype_field_map,
						export_filters: filters,
					});
				}
			};

			me.data_exporter = new ChildDataExporter(
				doctype,
				"Insert New Records"
			);
		}

		_add_template_field(data_exporter, table_field, doctype){
			data_exporter._template_select = frappe.ui.form.make_control({
			df: {
				label: __("Download Template"),
				fieldname: "download_template",
				fieldtype: "Autocomplete",
				insert_after: "file_type",
				change: () => {
					let value = data_exporter._template_select.get_value();
					if (value){
						frappe.db.get_value("Bulk Edit Download Template", value, "fields").then((r) => {
							data_exporter.dialog.$wrapper.find(":checkbox").prop("checked", 0).trigger("change");
							let fields = r?.message?.fields || "[]";
							fields = JSON.parse(fields || "[]");
							let selector = [];
							$.each(fields, (i, field) => {
								selector.push(`[data-unit=${field}]:checkbox`)
							});

							data_exporter.dialog.$wrapper.find(selector.join(",")).prop("checked", 1).trigger("change");
						});
					}

				}
			},
			parent: data_exporter.dialog.fields_dict.file_type.$wrapper,
			render_input: 1
		});
		frappe.db.get_list("Bulk Edit Download Template", {
			filters : {document_type: doctype},
			fields: ["name", "template_name"]
		}).then((r) => {
			data_exporter._template_select.df.options = r.map((i) => {return {value: i.name, label: i.template_name}});
			data_exporter._template_select.set_options();
		});
		}

		get_dialog_data(columns, doctype, map_fields){
			const me = this;
			let fields = [
				{
						fieldtype: "HTML",
						fieldname: "heading",
						options: `
							<div class="margin-top text-muted">
							${__("Map columns from {0} to fields in {1}", [__("Imported File"), __(doctype)])}
							</div>
						`,
					},
					{
						fieldtype: "Section Break",
					},
			];
			fields = fields.concat(this.get_dialog_map_fields(map_fields, doctype));

			return {
				title: __("Map Columns"),
				fields: fields,
				size: "extra-large",
				primary_action_label: __("Upload"),
				primary_action: function(values){
					me.upload_excel_data(values);
					this.hide();
				}
			}
		}

		get_dialog_map_fields(map_fields, doctype, MAX_ON_ROW=2){
			let fields = [];
			let index = 0;
			const fields_options = this.get_fields_options(doctype);
			for (let i in map_fields){
				fields = fields.concat([
						{
							label: "",
							fieldtype: "Data",
							default: map_fields[i].header_title,
							fieldname: `Column ${i}`,
							read_only: 1,
						},
						{
							fieldtype: "Column Break",
						},
						{
							fieldtype: "Autocomplete",
							fieldname: `${i}`,
							label: "",
							max_items: Infinity,
							options: [
								{
									label: __("Don't Import"),
									value: "",
								},
							].concat(fields_options),
							default: map_fields[i].fieldname != "name"?  (map_fields[i].fieldname || "") : "",
						},
					]);
				if (++index % MAX_ON_ROW ){
					fields.push({
						fieldtype: "Column Break",
					});

					fields.push({
						fieldtype: "Column Break",
					});
				}
				else{
					fields.push({
						fieldtype: "Section Break",
						collapsible: 1,
					});
				}
			}
			while (index % MAX_ON_ROW){
				fields.push({
						fieldtype: "Column Break",
					});
					++index;
			}

			return fields;
		}

		get_fields_options(doctype){
			let no_value_fields = ["Section Break", "Column Break", "Tab Break", "HTML", "Table", "Table MultiSelect", "Button", "Image", "Fold", "Heading"]
			let meta = frappe.get_meta(doctype);
			let fields_options = [];
			for (let i in meta.fields){
				if (! no_value_fields.includes(meta.fields[i].fieldtype)){
					fields_options.push({value: meta.fields[i].fieldname, label: meta.fields[i].label, description: meta.fields[i].fieldname});
				}
			}
			return fields_options;
		}

		get_map_fields(columns){
			let map_fields = {};

			$.each(columns, (i, row) => {
				if (row.header_title != "Sr. No"){
					map_fields[i] = {fieldname: row.df.fieldname, label: row.df.label, header_title: row.header_title, meta: row};
				}
			});
			return map_fields;
		}

		count(doctype, args = {}) {
			let filters = args.filters || {};

			// has a filter with childtable?
			const distinct =
				Array.isArray(filters) &&
				filters.some((filter) => {
					return filter[0] !== doctype;
				});

			const fields = [];

			return frappe.xcall("frappe.desk.reportview.get_count", {
				doctype,
				filters,
				fields,
				distinct,
				parent_doctype: this.doctype,
			});
		}
	};

	frappe.ui.form.ControlTable = NewControlTable;
});