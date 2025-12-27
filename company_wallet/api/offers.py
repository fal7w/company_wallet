import frappe
from frappe import _
from .utils import unify_response , get_list_with_count
import frappe.client


OFFER_Detail_DOCTYPE = "Offer Detail"
OFFER_Seen_LOG = "Offer Seen Log"


@unify_response()
def create_offer_seen_log(offer, user):
	"""
	Create a new offer seen log.
	"""
	if not frappe.db.exists(OFFER_Seen_LOG, {"offer": offer, "user": user}):
		log = frappe.get_doc({
			"doctype": OFFER_Seen_LOG,
			"offer": offer,
			"user": user
		})
		log.save()
		handle_common_doc_operations(log)
		return log
	# else:
	# 	frappe.throw(_("Already Seen!"))


@unify_response(allow_guest=True)
def get_offer_by_type(type):
	"""
	Get offer details by type.
	:param type: The type of the offer.
	:return: List of offer details matching the type.
	"""
	docs = frappe.get_list(OFFER_Detail_DOCTYPE, filters={"type": type},
							fields=["subject", "text", "type", "from_date", "to_date"])
	if docs:
		return docs
	else:
		frappe.throw(_("No Data Offers Found!"))
		

@unify_response(allow_guest=True)
def get_offers(fields=None, filters=None, limit_start=None, limit=None, order_by=None, or_filters=None):
	"""
	Get a list of offers with count based on the specified filters and options.
	:param fields: (optional) A list of fields to include in the result. Default is None.
	:param filters: (optional) A dictionary of filters to apply to the query. Default is None.
	:param limit_start: (optional) The index of the first result to return. Default is None.
	:param limit: (optional) The maximum number of results to return. Default is 20.
	:param order_by: (optional) The field to order the results by. Default is None.
	:param or_filters: (optional) A list of dictionaries representing OR filters. Default is None.
	:return: A dictionary containing the count and result of the query.
	"""
	return get_list_with_count(OFFER_Detail_DOCTYPE, fields, filters, limit_start=limit_start, limit=limit, order_by=order_by, or_filters=or_filters)


@unify_response()
def get_offer_seen(fields=None, filters=None, limit_start=None, limit=None, order_by=None, or_filters=None):
	"""
	Get the list of offers that have been seen by the user.

	:param fields: (optional) A list of fields to include in the result. Default is None.
	:param filters: (optional) A dictionary of filters to apply to the query. Default is None.
	:param limit_start: (optional) The index of the first result to return. Default is None.
	:param limit: (optional) The maximum number of results to return. Default is 20.
	:param order_by: (optional) The field to order the results by. Default is None.
	:param or_filters: (optional) A list of dictionaries representing OR filters. Default is None.
	:return: A list of offer documents with an additional field indicating if they have been seen or not.
	"""
	offer_docs = frappe.get_list(OFFER_Detail_DOCTYPE, filters={"docstatus": 1}, fields=["name"])
	logs = frappe.client.get_list(OFFER_Seen_LOG, fields, filters, limit_start=limit_start, limit_page_length=limit, order_by=order_by, or_filters=or_filters)
	if logs:
		for d in offer_docs:
			if d.get("name") in [o.get("offer") for o in logs]:
				d["seen"] = "seen"
			else:
				d["seen"] = "not seen"
			
		return offer_docs
	else:
		frappe.throw(_("No offers have been seen yet!"))


def handle_common_doc_operations(doc):
	keys_to_delete = ["creation", "owner", "modified", "modified_by", "docstatus", "idx", "naming_series"]
	for key in keys_to_delete:
		doc.delete_key(key)