import frappe
from .utils import unify_response, get_list_with_count
import frappe.client


wallet_user_doctype = "Wallet User"


@unify_response()
def create_wallet_user(**kwargs):
	"""
	Create a wallet user.

	:param kwargs: Keyword arguments containing the fields and values for the wallet user.
	:type kwargs: dict
	:return: The created wallet user document.
	:rtype: frappe.model.document.Document
	"""
	# TODO: I think we need to add a defualt values here for client creations 
	# TODO: role profile - wallet campany base on users or it is passing by default
	
	wallet_user = frappe.get_doc({
		**kwargs,
		"doctype": wallet_user_doctype,
	})
	wallet_user.save()
	return wallet_user


@unify_response()
def get_wallet_user(name):
	
	"""
	Get a wallet user by its name.

	:param name: The name of the wallet user to retrieve.
	:type name: str
	:return: The wallet user document.
	:rtype: dict
	"""
	return frappe.client.get(wallet_user_doctype, name)


@unify_response()
def update_wallet_user(name, **kwargs):
	"""
	Update a wallet user by its name with the given keyword arguments.

	:param name: The name of the wallet user to update.
	:type name: str
	:param kwargs: Keyword arguments containing the fields to update and their new values.
	:type kwargs: dict
	:return: The updated wallet user document.
	:rtype: frappe.model.document.Document
	"""
	wallet_user = frappe.get_doc(wallet_user_doctype, name)
	wallet_user.update(kwargs)
	wallet_user.save()
	return wallet_user


@unify_response()
def get_list_wallet_user(fields=None, filters=None, limit_start=None, limit=20, order_by=None, or_filters=None):
	"""
	Get a list of wallet users with optional filtering, ordering, and pagination.

	:param fields: (Optional) A list of fields to include in the response. Default is None.
	:type fields: list[str] or None
	:param filters: (Optional) A dictionary of filters to apply to the query. Default is None.
	:type filters: dict or None
	:param limit_start: (Optional) The index of the first result to return. Default is None.
	:type limit
	"""
	return get_list_with_count(wallet_user_doctype, fields, filters, limit_start=limit_start, limit=limit, order_by=order_by, or_filters=or_filters)
