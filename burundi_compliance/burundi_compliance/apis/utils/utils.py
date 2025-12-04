import frappe
import json
import base64
import jwt

from frappe import _

from ...doctype.doctype_names_mapping import (
    ENDPOINT_URL_DOCTYPE_NAME,
)


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


def get_urls(environment: str, request_type: str) -> tuple[str, str]:
    """Return the base URL for OBR API based on the environment setting."""
    if environment == "sandbox":
        endpoint_doc = frappe.get_doc(ENDPOINT_URL_DOCTYPE_NAME, "SandBox")

        for url in endpoint_doc.apis:
            if url.method_name == request_type:
                return url.api, endpoint_doc.server_url.strip("/")

    else:
        endpoint = frappe.get_doc(ENDPOINT_URL_DOCTYPE_NAME, "Production")
        for url in endpoint.apis:
            if url.method_name == request_type:
                return url.api, endpoint.server_url.strip("/")
