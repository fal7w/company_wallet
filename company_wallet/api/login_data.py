import frappe
from company_wallet.api.utils import unify_response
from frappe.permissions import get_role_permissions


@unify_response()
def get_roles_list(user):
	"""
	Get the list of roles for a given user.
	:param user: The email of the user.
	:type user: str
	:return: A list of dictionaries representing the roles and their permissions for the user.
	:rtype: List[Dict[str, Any]]
	"""
	wallet_roles = []
	try:
		wallet_user_role = frappe.db.get_value("Wallet User", {"email": user}, "role")
		role_profile = frappe.get_all("Role Profile", filters={"name": wallet_user_role}, fields=["name"])
		if role_profile:
			
			roles = frappe.get_all("Has Role", filters={"parent": role_profile[0].get('name')}, fields=["role"])
			profile_details = {
				"profile_name": role_profile[0].get('name'),
				"roles": []
			}
			for role in roles:
				role_name = role['role']

				# list of DocTypes for which the role has permissions
				doctypes_with_perms = frappe.get_all("DocPerm", filters={"role": role_name}, fields=["parent"])
				distinct_doctypes = list({doctype['parent'] for doctype in doctypes_with_perms})

				# Fetch permissions for each doctype
				role_permissions = []
				for doctype in distinct_doctypes:
					perms = get_role_permissions(doctype)
					role_permissions.append({
						"doctype_name": doctype,
						**perms
					})

				# Add to role details
				profile_details['roles'].append({
					"role_name": role_name,
					"permissions": role_permissions
				})
				
			wallet_roles.append(profile_details)

		return wallet_roles
	except frappe.DoesNotExistError:
		return


@unify_response()
def get_wallet_company_info(user):
	"""
	Get the company information for a given user.
	:param user: The email of the user.
	:type user: str
	:return: A dictionary containing the company information, or None if the user does not exist.
	:rtype: dict or None
	"""
	try:
		wallet_user_company = frappe.db.get_value("Wallet User", {"email": user}, "wallet_company")
		# get company info
		info = ['company_name', 'main_user', 'company_logo', 'description', 'wallet_provider']
		wallet_company_info = frappe.db.get_value("Wallet Company", wallet_user_company, info, as_dict=True)
		return wallet_company_info
	except frappe.DoesNotExistError:
		return
	

@unify_response()
def get_wallet_user_info(user):
	"""
	Get the wallet user information for a given user.

	:param user: The email of the user.
	:type user: str
	:return: A dictionary containing the wallet user information, or None if the user does not exist.
	:rtype: dict or None
	"""
	try:
		wallet_user = frappe.db.get_value("Wallet User", {"email": user}, "*", as_dict=True)
		return wallet_user
	except frappe.DoesNotExistError:
		return
	
	
@unify_response()
def get_role_profile_list(user=None):
	"""
	Get the list of role profiles.
	:param user: (optional) The user for whom to retrieve the role profiles. Defaults to None.
	:type user: str or None
	:return: A list of dictionaries representing the role profiles. Each dictionary contains the name of the role profile.
	:rtype: list[dict]
	"""
	try:
		return frappe.get_all("Role Profile", fields=["name"])
	except frappe.DoesNotExistError:
		return