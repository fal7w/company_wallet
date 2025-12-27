import datetime
import uuid
from .connect_base import ConnectSDK


class CompanySDK(ConnectSDK):
	def create_company(self, agent_name, error_message):
		return self._request("POST", "create_company", {
				"name": agent_name,
			},
			error_message=error_message
		)

	def update_token(self, pwd, error_message):
		self.donet_update_token = True
		res = self._request("POST", "update_token", {
				"name": self.wallet_identifier,
				"pwd": pwd,
			},
			error_message=error_message,
		)
		self.donet_update_token = False
		return res

	def update_wallet_password(self, password, error_message):
		return self._request("POST", "update_wallet_password", {
				"agent_password": password,
			},
			error_message=error_message,
		)

	def update_api_user(self, wallet_identifier, org_id, username, password, error_message):
		return self._request("POST", "update_api_user", {
				"agent_wallet": wallet_identifier,
				"username": username,
				"password": password,
				"org_id": org_id
			},
			error_message=error_message,
		)
	
	def get_agent_balance(self, error_message):
		return self._request("POST", "get_agent_balance", {
				"refId": f"check_balance{int(uuid.uuid4().hex[:10], 16):010}"
			},
			error_message=error_message,
		)

	def get_agent_statement(self, start_date, end_date, currency, error_message):
		return self._request("POST", "get_wallet_statement", {
				"through": "1",
				"toMember": "14000",
				"from_date": datetime.datetime.strptime(str(start_date), '%Y-%m-%d').strftime("%d%m%Y"),
				"to": datetime.datetime.strptime(str(end_date), '%Y-%m-%d').strftime("%d%m%Y"),
				"refId":  f"company_statement{int(uuid.uuid4().hex[:10], 16):010}",
				"curreny": currency
			},
			error_message=error_message,
		)
	
	def check_ping_pong_connection(self, error_message):
		return self._request("POST", "check_ping_pong_connection", {},
			error_message=error_message,
		)


CompanySDK._update_action_url({
	"create_company": "/api/jawali-company/v1/create-agent",
	"update_token": "/api/jawali-company/v1/agent-token",
	"update_api_user": "/api/jawali-company/v1/update-agent",
	"update_wallet_password": "/api/jawali-company/v1/update-agent-pass",
	"get_wallet_statement": "/api/jawali-company/v1/statement",
	"get_agent_balance": "/api/jawali-company/v1/balance",
	"check_ping_pong_connection": "/api/check-connection",
})