import requests
import urllib
import frappe
from frappe import _
from frappe.utils import cint
from requests.auth import HTTPBasicAuth
from requests.exceptions import JSONDecodeError
import sys
from urllib.parse import urlparse
from frappe.translate import get_language


def get_password(network_settings, field):
	try:
		return network_settings.get_password(field)
	except BaseException:
		return network_settings.get(field)


def return_response(func):
	def innerfn(*args, **kwargs):
		try:
			res = frappe._dict(parse_response(func(*args, **kwargs)))
			if res.json and isinstance(res.json.get("error"), dict):
				error_code = res.json.get("error").get("error_code")
				if args and hasattr(args[0], 'auto_update_token') and not getattr(args[0], "donet_update_token", False) and cint(error_code) == 401 :
					args[0].auto_update_token()
					res = frappe._dict(parse_response(func(*args, **kwargs)))
			return res
		except ConnectionError as ce:
			# get method's path of `func`
			if args and hasattr(args[0], '__class__'):
				method_name = f"{args[0].__class__.__name__}.{func.__name__}"
			else:
				method_name = func.__name__
			# Log all error info in `Error Log` DocType
			frappe.log_error(f"{method_name} {ce.__class__.__name__}", ce)
			# Extracting host and port information from the underlying exception
			host = None

			# Checking if the underlying exception has the necessary information
			if hasattr(ce, 'request') and hasattr(ce.request, 'url'):
				parsed_url = urlparse(ce.request.url)
				host = parsed_url.hostname

				frappe.throw(frappe._("Failed to connect to server {server}").format(
					server=frappe.bold(host),
				), exc=ce)
	return innerfn


def call_api_method(func):
	return return_response(func)


def parse_response(response):
	res = frappe._dict()
	if response.status_code:
		res.update({
			"status_code": response.status_code,
			"failed": not (200 <= response.status_code < 300),
			"response": response,
			"json": frappe._dict(),
			"content": response.text
		})
		try:
			res["json"] = frappe.parse_json(response.json())
		except JSONDecodeError:
			res["failed"] = True

	return res


class NetworkError(frappe.ValidationError): pass


class ConnectSDK():
	action_url = {}
	POST = "POST"
	GET = "GET"
	PUT = "PUT"

	@classmethod
	def _update_action_url(cls, action_url):
		cls.action_url.update(action_url)

	def __init__(self, network_settings):
		self.server_url = network_settings.get('server_url')
		self.auth_type = network_settings.get("auth_type")
		self.user_name = network_settings.get("user_name")
		self.password = get_password(network_settings, "password")
		self.path = get_password(network_settings, "path")
		self.token = get_password(network_settings, "token")
		self.wallet_identifier = get_password(network_settings, "wallet_identifier")
		self.wallet_company = network_settings.get("wallet_company")
		self._verify_ssl = network_settings.get("ssl_verify", True)

	def _update_headers(self, headers):
		if not headers:
			headers = {}
		headers["Accept-Language"] = get_language()
		auth = None

		if self.auth_type == "Basic":
			auth = HTTPBasicAuth(self.user_name, self.password)
		elif self.auth_type == "Token":
			headers["Authentication"] = f"Bearer {self.password}"
		elif self.auth_type == "API Key":
			headers[self.user_name] = self.password

		return headers, auth

	@call_api_method
	def _network_request(self, method, action, json: dict, headers=None):
		url = self._get_url(action)
		transaction_url = urllib.parse.urljoin(self.server_url, url)
		headers, auth = self._update_headers(headers)
		added_data = self._get_defualt_data()

		if isinstance(added_data, dict):
			added_data.update(json)
			json = added_data

		res = frappe._dict()
		try:
			res = requests.request(method, transaction_url, json=json, headers=headers, verify=self._verify_ssl, auth=auth)
		finally:
			if frappe.conf.get("log_outgoing_request"):
				title = f"received request to: {transaction_url}"
				if len(title) >= 140:
					title = title[0:136] + "..."
				log_message = {
					"action": action,
					"method": method,
					"headers": headers,
					"auth": auth,
					"json": json,
					"result": res,
					"verify": self._verify_ssl,
				}
				if res.content:
					log_message["response_headers"] = res.headers
					log_message["response_history"] = res.history
					log_message["request"] = {
						"url": res.request.url,
						"method": res.request.method,
						"headers": res.request.headers,
						"body": res.request.body,
					}
					log_message["traceback"] = frappe.get_traceback()
				frappe.log_error(title, log_message, defer_insert=True)
		return res

	def _request(self, method, action, json, error_message=None, headers=None):
		res = self._network_request(method, action, json, headers=headers)
		self.raise_network_error(res, error_message)
		return res

	def raise_network_error(self, response, faild_msg, raise_exception=NetworkError):
		"""
		raise error if response status_code from network is >= 400
		"""
		errors_msg = [(_("Server Code"), response.status_code)]
		# Check if response is None
		if response is None or response == {}:
			errors_msg.append((_("Content"), "No response received from the server"))
			sys.stdin = None
			frappe.msgprint(errors_msg, faild_msg, as_table=True, raise_exception=raise_exception)
			return

		try:
			response_json = response.json
		except ValueError:
			errors_msg.append((_("Content"), "Response is not a valid JSON"))
			sys.stdin = None
			frappe.msgprint(errors_msg, faild_msg, as_table=True, raise_exception=raise_exception)
			return
		
		# Check if the response failed or the status is not present or false
		if response.failed or not response_json.get("status"):
			if response_json:
				error = response_json.get("error", response_json)
				error = self._parse_error(error)
				errors_msg += self._get_error_message(error)
			else:
				errors_msg.append((_("Content"), response.content))

			sys.stdin = None
			frappe.msgprint(errors_msg, faild_msg, as_table=True, raise_exception=raise_exception)

	def _parse_error(self, error):
		parsed_error = {}
		if isinstance(error, (list, tuple)):
			for i in error:
				if isinstance(i, dict):
					for k, v in i.items():
						parsed_error[k] = v
				else:
					parsed_error.setdefault("", [])
					parsed_error[""].append(i)
		elif isinstance(error, dict):
			parsed_error = error
		else:
			parsed_error[""] = error
		return parsed_error

	def _get_error_message(self, error):
		errors_msg = []
		for key, msg in error.items():
			if isinstance(msg, (tuple, list)):
				for i in msg:
					errors_msg.append((key, _(i)))
			elif isinstance(msg, dict):
				for k, v in msg.items():
					errors_msg.append((k, v))
			else:
				errors_msg.append((key, _(msg)))
		return errors_msg

	def _get_defualt_data(self):
		return {
			"secret_path": self.path,
			"token": self.token,
			"agent_wallet": self.wallet_identifier,
		}

	def auto_update_token(self):
		wallet_company = frappe.get_doc("Wallet Company", self.wallet_company)
		res = wallet_company.update_auth_token(show_message=False)
		return res

	def _get_url(self, action):
		if isinstance(self.action_url, dict):
			return self.action_url.get(action, action)  # get the value for key action or get action itself
		else:
			return action


def init_default_sdk(cls: type[ConnectSDK], wallet_company=None):
	provider = frappe.get_cached_doc('Company Wallet Configration')
	wallet_company_data = {}

	if wallet_company:
		if isinstance(wallet_company, str):
			wallet_company = frappe.get_cached_doc("Wallet Company", wallet_company)

		wallet_company_data["path"] = get_password(wallet_company, "path")
		wallet_company_data["token"] = get_password(wallet_company, "token")
		wallet_company_data["wallet_identifier"] = wallet_company.get("wallet_identifier")
		wallet_company_data["wallet_company"] = wallet_company.get("name")

	return cls({
		"server_url": provider.server_url,
		"auth_type": provider.authentication_type,
		"user_name": provider.user_name,
		"password": get_password(provider, "password"),
		"ssl_verify": not provider.get("skip_ssl_verify"),
		**wallet_company_data
	})
