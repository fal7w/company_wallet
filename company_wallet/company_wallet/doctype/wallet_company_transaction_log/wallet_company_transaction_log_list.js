// Copyright (c) 2024, Fintechsys and contributors
// For license information, please see license.txt

frappe.listview_settings["Wallet Company Transaction Log"] = {
	get_indicator(doc) {
		if ( doc.status == "REJECTED"){ 
			return [__("REJECTED"), "red", "status,=,REJECTED|docstatus,=,1"];
		}
		if (doc.status == "ACCEPTED") {
			return [__("ACCEPTED"), "green", "docstatus,=,1"];
		}
		if (doc.status == "PENDING") {
			return [__("PENDING"), "orange", "docstatus,=,1"];
		}
		if (doc.status == "INIT") {
			return [__("INIT"), "yellow", "docstatus,=,1"];
		}
		if (doc.status == "CANCELLED") {
			return [__("CANCELLED"), "grey", "docstatus,=,1"];
		}
		if (doc.status == "EXPIRED") {
			return [__("EXPIRED"), "grey", "docstatus,=,1"];
		}
		if (doc.status == "REVERSED") {
			return [__("REVERSED"), "blue", "docstatus,=,1"];
		}
	},
	has_indicator_for_draft: true,
}