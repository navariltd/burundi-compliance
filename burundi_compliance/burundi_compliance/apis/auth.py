import json
import requests
import datetime

import frappe
from frappe import _
from frappe.integrations.utils import create_request_log


from burundi_compliance.burundi_compliance.apis.utils.utils import (
	get_urls,
	decode_jwt_token,
)
from ..doctype.doctype_names_mapping import SETTINGS_DOCTYPE_NAME


class OBRAuthService:
	@staticmethod
	def authenticate(
		auth_server_url: str,
		request_url: str,
		username: str,
		password: str,
		docname: str | None = None,
	) -> dict:
		AUTH_URL = f"{auth_server_url}/{request_url}"
		payload = {"username": username, "password": password}
		headers = {"Content-Type": "application/json"}

		integration_request = create_request_log(
			data=json.dumps(payload),
			request_description="OBR Authentication Request",
			is_remote_request=1,
			service_name="OBR Authentication",
			url=AUTH_URL,
			reference_doctype=SETTINGS_DOCTYPE_NAME,
			reference_docname=docname,
		)

		try:
			response = requests.post(
				AUTH_URL, data=json.dumps(payload), headers=headers, timeout=30
			)

			response.raise_for_status()
			if response.ok:
				data = response.json()
				frappe.db.set_value(
					"Integration Request",
					integration_request.name,
					{
						"output": json.dumps(data),
						"status": "Completed",
					},
					update_modified=False,
				)

				token = data.get("result").get("token")

				if not token:
					frappe.throw(
						_("Authentication failed. No access token received from OBR."),
					)
				decoded_token = decode_jwt_token(token)
				return {**decoded_token, "auth_token": token}

		except requests.exceptions.RequestException as e:
			frappe.db.set_value(
				"Integration Request",
				integration_request.name,
				{
					"output": str(e),
					"status": "Failed",
				},
				update_modified=False,
			)
			frappe.log_error(
				_("OBR Authentication Error"),
				f"Failed to Authenticate with OBR: {str(e)}",
			)
			frappe.throw(
				_("Failed to Authenticate with OBR. Please check the logs."),
			)

		except Exception as e:
			frappe.db.set_value(
				"Integration Request",
				integration_request.name,
				{
					"output": str(e),
					"status": "Failed",
				},
				update_modified=False,
			)
			frappe.log_error(
				_("OBR Authentication Error"),
				f"An error occurred during OBR authentication: {str(e)}",
			)
			frappe.throw(
				_("An error occurred during OBR authentication. Please check the logs.")
			)


@frappe.whitelist()
def authenticate(settings_name):
	settings_doc = frappe.get_doc(SETTINGS_DOCTYPE_NAME, settings_name)
	request_url, auth_server_url = get_urls(
		"sandbox" if settings_doc.sandbox else "production", "login"
	)
	result = OBRAuthService.authenticate(
		auth_server_url=auth_server_url,
		request_url=request_url,
		username=settings_doc.username,
		password=settings_doc.get_password(fieldname="password"),
		docname=settings_name,
	)
	result = frappe._dict(result)

	settings_doc.authorization_token = result.auth_token
	settings_doc.expires_at = datetime.datetime.fromtimestamp(result.exp)
	settings_doc.save(ignore_permissions=True)
	return settings_doc
