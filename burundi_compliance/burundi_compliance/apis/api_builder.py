import jwt
import json
import base64
import requests


from typing import Literal, Callable, Union, Optional


from frappe.model.document import Document
import frappe
from frappe import _
from frappe.integrations.utils import create_request_log


class OBRAPI:
    def __init__(self) -> None:
        self._url: str | None = None
        self._payload: dict | None = None
        self._headers: dict | None = None
        self._method: Literal["GET", "POST", "PUT"] | None = None
        self._settings: dict | None = None
        self._success_callback_handler: callable | None = None
        self._error_callback_handler: callable | None = None

    @property
    def method(self) -> Literal["GET", "POST", "PUT"] | None:
        return self._method

    @method.setter
    def method(self, method: Literal["GET", "POST", "PUT"]) -> None:
        self._method = method

    @property
    def url(self) -> str | None:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def payload(self) -> dict | None:
        return self._payload

    @payload.setter
    def payload(self, payload: dict) -> None:
        self._payload = payload

    @property
    def headers(self) -> dict | None:
        return self._headers

    @headers.setter
    def headers(self, headers: dict) -> None:
        self._headers = headers

    @property
    def settings(self) -> dict | None:
        return self._settings

    @settings.setter
    def settings(self, settings: dict) -> None:
        self._settings = settings

    @property
    def success_callback_handler(self) -> Callable | None:
        return self._success_callback_handler

    @success_callback_handler.setter
    def success_callback_handler(self, handler: Callable) -> None:
        self._success_callback_handler = handler

    @property
    def error_callback_handler(self) -> Callable | None:
        return self._error_callback_handler

    @error_callback_handler.setter
    def error_callback_handler(self, handler: Callable) -> None:
        self._error_callback_handler = handler

    @property
    def service(self) -> str | None:
        return self._service

    @service.setter
    def service(self, service: str) -> None:
        self._service = service

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        """Decode a JWT token without verification and return its payload as a dictionary."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT token format")

            payload_encoded = parts[1]
            padding = 4 - (len(payload_encoded) % 4)
            if padding != 4:
                payload_encoded += "=" * padding
            decode_bytes = base64.urlsafe_b64decode(payload_encoded)

            payload = json.loads(decode_bytes)
            return payload
        except jwt.DecodeError as e:
            frappe.log_error(
                _("JWT Decoding Error"),
                f"Failed to decode JWT token: {str(e)}",
            )
            frappe.throw(_("Failed to decode JWT token"), frappe.AuthenticationError)

        except Exception as e:
            frappe.log_error(
                _("JWT Decoding Error"),
                f"An error occurred while decoding JWT token: {str(e)}",
            )
            frappe.throw(
                _("An error occurred while decoding JWT token"),
                frappe.AuthenticationError,
            )

    def make_remote_request(
        self,
        doctype: Document | str | None = None,
        document_name: str | None = None,
        retrying: bool = False,
        require_handler: bool = True,
    ) -> str | None:
        """Handles communication to OBR servers"""
        if (
            self._url is None
            or self._method is None
            or (self._success_callback_handler is None and require_handler)
        ):
            frappe.throw(
                _(
                    "Please set all required parameters (URL, method, and success callback handler)"
                ),
                title="Setup Error",
                is_minimizable=True,
            )

        if not retrying:
            try:
                self.integration_request = create_request_log(
                    data=self._payload,
                    is_remote_request=True,
                    service_name=self._service,
                    request_headers=self._headers,
                    url=self._url,
                    reference_doctype=doctype,
                    reference_docname=document_name,
                )
            except frappe.LinkValidationError:
                self.integration_request = create_request_log(
                    data=self._payload,
                    is_remote_request=True,
                    service_name=self._service,
                    request_headers=self._headers,
                    url=self._url,
                    reference_doctype=doctype,
                )

        try:
            if self._method == "POST":
                response = requests.post(
                    self._url, json=self._payload, headers=self._headers
                )

            elif self.method == "GET":
                response = requests.get(
                    self._url, headers=self._headers, params=self._payload
                )

            response_data = get_response_data(response)

            if response.status_code in [200, 201]:
                update_integration_request(
                    self.integration_request.name,
                    status="Completed",
                    output=str(response_data),
                    request_description="Request completed successfully.",
                )

                if not require_handler:
                    return response_data

                self._success_callback_handler(
                    response=response_data, document_name=document_name, doctype=doctype
                )

            else:
                if isinstance(response_data, str):
                    error = response_data
                elif isinstance(response_data, list):
                    error = response_data[0]
                else:
                    error = str(response_data)

                update_integration_request(
                    self.integration_request.name,
                    status="Failed",
                    error=error,
                    request_description="Request failed.",
                )

                if self._error_callback_handler:
                    self._error_callback_handler(
                        response=response_data,
                        document_name=document_name,
                        doctype=doctype,
                    )

            return response_data

        except Exception as e:
            frappe.log_error(
                title="OBR API Request Error",
                message=f"An error occurred during the API request: {str(e)}",
            )
            return None


def get_response_data(response: requests.Response) -> Optional[Union[dict, str, bytes]]:
    content_type = response.headers.get("Content-Type", "").lower()

    if "application/json" in content_type or content_type == "application/json":
        return response.json()
    elif "text/plain" in content_type or "text/html" in content_type:
        return response.text if response.text.strip() else None
    elif "application/xml" in content_type or "text/xml" in content_type:
        return response.text if response.text.strip() else None
    elif (
        "application/octet-stream" in content_type
        or "application/pdf" in content_type
        or "application/zip" in content_type
    ):
        return response.content

    return None


def update_integration_request(
    integration_request: str,
    status: Literal["Completed", "Failed"],
    output: str | None = None,
    error: str | None = None,
    request_description: str | None = None,
) -> None:
    """Updates the given integration request record silently without creating a version.

    Args:
        integration_request (str): The provided integration request.
        status (Literal["Completed", "Failed"]): The new status of the request.
        output (str | None, optional): The response message, if any. Defaults to None.
        error (str | None, optional): The error message, if any. Defaults to None.
        request_description (str | None, optional): Additional description for the request.
    """
    update_fields = {"status": status}

    if error:
        current_error = frappe.db.get_value(
            "Integration Request", integration_request, "error"
        )
        if current_error == "null" or not current_error:
            update_fields["error"] = error[:5000] if len(error) > 5000 else error
        elif error not in current_error:
            new_error = current_error + "\n" + error
            update_fields["error"] = (
                new_error[:5000] if len(new_error) > 5000 else new_error
            )

    if output:
        current_output = frappe.db.get_value(
            "Integration Request", integration_request, "output"
        )
        if current_output == "null" or not current_output:
            update_fields["output"] = output[:5000] if len(output) > 5000 else output
        elif output not in current_output:
            new_output = current_output + "\n" + output
            update_fields["output"] = (
                new_output[:5000] if len(new_output) > 5000 else new_output
            )

    if request_description:
        current_desc = frappe.db.get_value(
            "Integration Request", integration_request, "request_description"
        )
        if current_desc == "null" or not current_desc:
            update_fields["request_description"] = (
                request_description[:5000]
                if len(request_description) > 5000
                else request_description
            )
        elif request_description not in current_desc:
            new_desc = current_desc + " - " + request_description
            update_fields["request_description"] = (
                new_desc[:5000] if len(new_desc) > 5000 else new_desc
            )

    frappe.db.set_value(
        "Integration Request", integration_request, update_fields, update_modified=False
    )


# def decode_jwt_token(
#     token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IndzNDAwMDM4NzM5MTAwNzQyIiwiZXhwIjoxNzYzMDI4OTE4fQ.-LdylQ9xyblZ1qUej5CiXePuyKF2Xd1AAZ72cVsQLvQ",
# ) -> dict:
#     """Decode a JWT token without verification and return its payload as a dictionary."""
#     try:
#         parts = token.split(".")
#         if len(parts) != 3:
#             raise ValueError("Invalid JWT token format")
#         payload_encoded = parts[1]
#         padding = 4 - (len(payload_encoded) % 4)
#         if padding != 4:
#             payload_encoded += "=" * padding
#         decode_bytes = base64.urlsafe_b64decode(payload_encoded)
#         payload = json.loads(decode_bytes)
#         return payload
#     except jwt.DecodeError as e:
#         raise ValueError(f"Failed to decode JWT token: {str(e)}")
#     except Exception as e:
#         raise ValueError(f"An error occurred while decoding JWT token: {str(e)}")


# payload = decode_jwt_token()
# print(payload)
