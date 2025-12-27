import frappe
from frappe.model.base_document import BaseDocument
import frappe.client


def unify_response(*args, **kwargs):
	def inner_fun(fun):
		@frappe.whitelist(*args, **kwargs)
		def wrapper_fun(*wp_args, **wp_kwargs):
			frappe.response.update({
				"status": None,
				"data": None,
				"errors": None,
				"messages": None,
			})
			try:
				res = frappe.call(fun, *wp_args, **wp_kwargs)
				frappe.response["status"] = True
				if isinstance(res, (dict, list, tuple, set, BaseDocument)):
					frappe.response["data"] = res
				else:
					frappe.response["data"] = {"result": res}

			except BaseException as e:
				frappe.response["status"] = False
				message = [i for i in frappe.message_log if i.raise_exception]
				frappe.response["errors"] = [{
					"message": message[0] if message else str(e),
					"error": e.__class__.__name__,
					"error_code": getattr(e, "http_status_code", 500)
				}]
				raise

			finally:
				frappe.response["messages"] = [i for i in frappe.message_log if not i.raise_exception]
				if frappe.conf.get("log_received_request"):
					if hasattr(frappe.local, 'request') and frappe.local.request:
						frappe.log_error(f"received request to: {fun.__name__}", {
							"fun": fun,
							"args": {
								"args": wp_args,
								"kw_args": wp_kwargs,
							},
							"result": frappe.response,
							"traceback": frappe.get_traceback(),
							"request": {
								"method": frappe.request.method,
								"url": frappe.request.url,
								"data": frappe.form_dict,
								"body": frappe.request.data,
								"headers": dict(frappe.request.headers),
							}
						}, defer_insert=True)
					else:
						frappe.log_error(f"function called without HTTP request context: {fun.__name__}", {
							"fun": fun,
							"args": {
								"args": wp_args,
								"kw_args": wp_kwargs,
							},
							"result": frappe.response,
							"traceback": frappe.get_traceback(),
						}, defer_insert=True)
			return res
		return wrapper_fun
	return inner_fun


def get_list_with_count(doctype, fields=None, filters=None, limit_start=None, limit=20, order_by=None, or_filters=None):
	count = frappe.client.get_count(doctype, filters)
	res = frappe.client.get_list(doctype, fields, filters, limit_start=limit_start, limit_page_length=limit, order_by=order_by, or_filters=or_filters)
	return {"count": count, "result": res}