# Copyright (c) 2024, Fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DeviceInfoLog(Document):
	pass


def create_device_log(obj, method=None):
	device_id = frappe.form_dict.get('device_id', '')
	device_type = "Mobile-app" if device_id else "Web-browser"
	os_info = "Unavailable"
	ip_address = "Unknown"

	if hasattr(frappe.local, 'request') and frappe.local.request:
		os_info = frappe.local.request.headers.get("User-Agent", "Unavailable")
		ip_address = getattr(frappe.local, 'request_ip', 'Unknown')
		
	doc = frappe.get_doc({
		"doctype": "Device Info Log",
		"transaction_type": obj.get("doctype"),
		"transaction_link": obj.get("name"),
		"modified_date": obj.get("modified"),
		"device_id": device_id,
		"device_type": device_type,
		"os": os_info,
		"user_owner": obj.get("owner"),
		"modified_by1": frappe.session.user,
		"ip_address": ip_address,
		"wallet_company": obj.get("wallet_company"),
	})
	doc.flags.ignore_permissions = True
	doc.submit()
	return doc