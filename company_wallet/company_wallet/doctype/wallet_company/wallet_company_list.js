// Copyright (c) 2024, fintechsys and contributors
// For license information, please see license.txt


frappe.listview_settings['Wallet Company'] = {
	onload: function(listview){
		// if(frappe.perm.has_perm("Wallet Company",0, "create")){
			listview.page.add_inner_button(__("Create Company"), function(){show_create_dialog();});
	// }
}
}


function show_create_dialog(){
	let create_dialog = new frappe.ui.Dialog({
		size: "extra-large",
		title: __("Create Wallet Company"),
		fields:[
			{
				fieldtype: "Section Break",
				label: __("Company"),
			},
			{
				label: __("Company Name"),
				fieldname: "company_name",
				fieldtype: "Data",
				reqd: 1,
			},
			{
				label: __("Wallet Identifier"),
				fieldname: "wallet_identifier",
				fieldtype: "Data",
				reqd: 1,
			},
			{
				label: __("Organization ID"),
				fieldname: "org_id",
				fieldtype: "Data",
				reqd: 1,
			},
			{
				label: __("User Mobile No"),
				fieldname: "user_mobile_no",
				fieldtype: "Data",
				reqd: 1,
				option: "Phone",
			},
			{
				label: __("User Email"),
				fieldname: "user_email",
				fieldtype: "Data",
				option: "Email",
				reqd: 1,
			},
			{
				fieldtype: "Column Break",
			},
			{
				label: __("User Firstname"),
				fieldname: "user_firstname",
				fieldtype: "Data",
				reqd: 1,
			},
			{
				label: __("User Lastname"),
				fieldname: "user_lastname",
				fieldtype: "Data",
			},
			{
				label: __("Creating Date From Wallet Provider"),
				fieldname: "creating_date_from_wallet_provider",
				fieldtype: "Datetime",
				reqd: 1,
			},
			{
				label: __("Company Prefix"),
				fieldname: "company_prefix",
				fieldtype: "Data",
				reqd: 1,
			},
			{
				fieldtype: "Section Break",
				label: __("More"),
				collapsible: 1,
			},
			{
				label: __("Company Description"),
				fieldname: "company_description",
				fieldtype: "Text Editor",
				height: "200px",
			},
			
			
		],
		primary_action_label: __("Create"),
		primary_action: function(values){
			create_company(values, function(){create_dialog.hide();});
		},
	});

	create_dialog.show();
	return create_dialog;
}


function create_company(data, final_action){
	frappe.call({
		method: "company_wallet.company_wallet.doctype.wallet_company.wallet_company.create_company_with_user",
		args: data,
		callback: function(r){
			final_action();
			if (r?.message?.name){
				route_to_company(r.message["name"])
			}
		},
		freeze: 1,
	});
}

function route_to_company(company){
	frappe.set_route("Form", "Wallet Company", company);
}
