// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.listview_settings['Wallet Payment'] = {
	get_indicator(doc) {
		if (doc.docstatus == 0 && doc.status != "Approved") {
			return [__("Draft"), "yellow", "docstatus,=,0"];
		}
		else if (doc.docstatus == 0 && doc.status == "Approved") {
			return [__("Pending"), "orange", "docstatus,=,0"];
		}
		else if (doc.status == "Approved" || doc.status == "In progress" && doc.docstatus == 1) {
			return [__("In progress"), "blue", "status,=,In progress|docstatus,=,1"];
		}
		else if (doc.status == "Failed" && doc.docstatus == 1) {
			return [__("Failed"), "red", "status,=,Failed|docstatus,=,1"];
		}
		else if (doc.status == "Success" && doc.docstatus == 1) {
			return [__("Success"), "green", "docstatus,=,1"];
		}
		else if (doc.status == "Rejected" && doc.docstatus == 1) {
			return [__("Rejected"), "red", "status,=,Rejected|docstatus,=,2"];
		}
	},
	has_indicator_for_draft: true,

}    