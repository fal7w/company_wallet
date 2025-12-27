# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
import base64

from frappe.core.doctype.data_import.importer import INVALID_VALUES, Header, Row, INSERT, MAX_ROWS_IN_PREVIEW
from frappe.utils.csvutils import read_csv_content
from frappe.utils.xlsxutils import read_xls_file_from_attached_file, read_xlsx_file_from_attached_file


@frappe.whitelist()
def get_child_table_as_array(file_data, type, doctype):
	b64_data = base64.urlsafe_b64decode(file_data)
	data = []
	if type == "xlsx":
		data = read_xlsx_file_from_attached_file(fcontent=b64_data)
	elif type == "xls":
		data = read_xls_file_from_attached_file(b64_data)
	elif type == "csv":
		data = read_csv_content(b64_data)

	res = parse_data_from_template(data, doctype)
	res["data"] = data[1:]
	return res


def parse_data_from_template(raw_data, doctype):
	header = None
	data = []

	for i, row in enumerate(raw_data):
		if all(v in INVALID_VALUES for v in row):
			# empty row
			continue

		if not header:
			header = Header(i, row, doctype, raw_data[1:], frappe._dict())
		else:
			row_obj = Row(i, row, doctype, header, INSERT)
			data.append(row_obj)

	columns = header.columns

	if len(data) < 1:
		frappe.throw(
			frappe._("Import template should contain a Header and atleast one row."),
			title=frappe._("Template Error"),
		)
	return get_data_for_import_preview(columns, data)


def get_data_for_import_preview(used_columns, data):
	"""Adds a serial number column as the first column"""

	columns = [col.as_dict() for col in used_columns]
	for col in columns:
		# only pick useful fields in docfields to minimise the payload
		if col.df:
			col.df = {
				"fieldtype": col.df.fieldtype,
				"fieldname": col.df.fieldname,
				"label": col.df.label,
				"options": col.df.options,
				"parent": col.df.parent,
				"reqd": col.df.reqd,
				"default": col.df.default,
				"read_only": col.df.read_only,
			}

	data = [[row.row_number, *row.as_list()] for row in data]

	out = frappe._dict()
	out.data = data
	out.columns = columns
	total_number_of_rows = len(out.data)
	if total_number_of_rows > MAX_ROWS_IN_PREVIEW:
		out.data = out.data[:MAX_ROWS_IN_PREVIEW]
		out.max_rows_exceeded = True
		out.max_rows_in_preview = MAX_ROWS_IN_PREVIEW
		out.total_number_of_rows = total_number_of_rows

	return out


@frappe.whitelist()
def download_template(*args, **kwargs):
	import frappe.permissions
	if not hasattr(frappe.permissions, "overwrite_can_export") or not frappe.permissions.overwrite_can_export:
		frappe.permissions.overwrite_can_export = True
		old_can_export = frappe.permissions.can_export

		def can_export(doctype, *args, **kwargs):
			meta = frappe.get_meta(doctype)
			return meta.istable or old_can_export(doctype, *args, **kwargs)

		frappe.permissions.can_export = can_export

	if not hasattr(frappe.db, "overwrite_get_list") or not frappe.db.overwrite_get_list:
		frappe.db.overwrite_get_list = True
		old_get_list = frappe.db.get_list

		def get_list(doctype, *args, **kwargs):
			meta = frappe.get_meta(doctype)
			if meta.istable:
				kwargs["ignore_permissions"] = True
			return frappe.get_list(doctype, *args, **kwargs)

		frappe.db.get_list = get_list

	from frappe.core.doctype.data_import.data_import import download_template


	frappe.call(download_template, *args, **kwargs)

	frappe.permissions.overwrite_can_export = False
	frappe.permissions.can_export = old_can_export

	frappe.db.overwrite_get_list = False
	frappe.db.get_list = old_get_list
