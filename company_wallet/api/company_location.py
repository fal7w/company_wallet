import frappe
from frappe import _
from company_wallet.api.utils import unify_response


# @unify_response()
@frappe.whitelist(allow_guest=True)
def get_location_list():
	"""
	Retrieves a list of company locations.
	:return: A list of company locations.
	:rtype: List[Dict[str, Any]]
	:raises frappe.DoesNotExistError: If no locations are found.
	"""
	doc = frappe.get_list("Company Location",
							fields=["subject", "address", "type", "area", "latitude", "longitude"],)
	if doc:
		return doc
	else:
		frappe.throw(_("No Data Found!"))