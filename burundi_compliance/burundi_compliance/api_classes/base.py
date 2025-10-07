import requests
import time
from frappe import _
import frappe
from ..doctype.custom_exceptions import AuthenticationError


class OBRAPIBase:
    def authenticate(self, max_retries=1):
        for attempt in range(max_retries + 1):
            try:
                return self.authenticate_with_retry()
            except AuthenticationError as auth_error:
                if attempt < max_retries:
                    frappe.logger().warning(
                        f"Authentication failed (attempt {attempt + 1}), retrying..."
                    )
                else:
                    title = _("Authentication Failed")
                    message = _(
                        f"All {max_retries + 1} attempts failed: {str(auth_error)}"
                    )
                    frappe.log_error(
                        title,
                        message,
                    )
                    raise

    def authenticate_with_retry(self):
        auth_details = self.get_auth_details()
        login_url = self.get_api_from_ebims_settings("login")
        headers = {"Content-Type": "application/json"}

        data = {
            "username": auth_details["username"],
            "password": auth_details["password"],
        }

        try:
            response = requests.post(login_url, json=data, headers=headers, timeout=30)
            response.raise_for_status()

            try:
                result = response.json()
            except ValueError as e:
                frappe.msgprint(_("Received non-JSON response from OBR server"))
                frappe.log_error(
                    _("OBRAPIBase Authentication Error"),
                    f"Error decoding JSON response: {str(e)}",
                )
                raise AuthenticationError("Invalid JSON response from OBR server")

            if result.get("success"):
                return result["result"]["token"]

        except requests.exceptions.RequestException as e:
            frappe.msgprint(_("Authentication problem with OBR server, job queued"))
            frappe.log_error(
                _("OBRAPIBase Authentication Error"),
                f"Error during authentication: {str(e)}",
            )
            raise AuthenticationError(str(e))

    def get_auth_details(self):
        # TODO: Pick company from the ref document
        company = frappe.defaults.get_user_default("Company")

        if not company:
            frappe.throw(
                _("No default Company found. Please set one in your User Defaults")
            )

        try:
            ebims_settings = frappe.get_doc("eBMS Settings", company)
        except frappe.DoesNotExistError:
            frappe.throw(
                _("Kindly create 'eBMS Settings' for company {0}").format(company)
            )
        except Exception as e:
            frappe.throw(_("Error fetching eBMS Settings: {0}").format(str(e)))

        return {
            "username": ebims_settings.username,
            "password": ebims_settings.get_password("password", raise_exception=False),
            "start_date": ebims_settings.start_date,
            "sandbox": ebims_settings.sandbox,
            "tp_legal_form": ebims_settings.taxpayers_legal_form,
            "tp_activity_sector": ebims_settings.taxpayers_sector_of_activity,
            "system_identification_given_by_obr": ebims_settings.system_identification_given_by_obr,
            "the_taxpayers_commercial_register_number": ebims_settings.the_taxpayers_commercial_register_number,
            "the_taxpayers_tax_center": ebims_settings.the_taxpayers_tax_center,
            "type_of_taxpayer": ebims_settings.type_of_taxpayer,
            "subject_to_consumption_tax": ebims_settings.subject_to_consumption_tax,
            "subject_to_flatrate_withholding_tax": ebims_settings.subject_to_flatrate_withholding_tax,
            "subject_to_vat": ebims_settings.subject_to_vat,
            "allow_obr_to_track_sales": ebims_settings.allow_obr_to_track_sales,
            "allow_obr_to_track_stock_movement": ebims_settings.allow_obr_to_track_stock_movement,
        }

    def get_api_from_ebims_settings(self, method_name):
        company = frappe.defaults.get_user_default("Company")

        if not company:
            frappe.throw(
                _("No default Company found. Please set one in your User Defaults")
            )

        try:
            ebims_settings = frappe.get_doc("eBMS Settings", company)
        except frappe.DoesNotExistError:
            frappe.throw(
                _("Kindly create 'eBMS Settings' for company {0}").format(company)
            )
        except Exception as e:
            frappe.throw(_("Error fetching eBMS Settings: {0}").format(str(e)))

        sandbox = ebims_settings.sandbox
        api_list_doc = None

        if sandbox:
            try:
                api_list_doc = frappe.get_doc("eBMS Endpoint URLs", "SandBox")
            except frappe.DoesNotExistError:
                frappe.throw(_("Kindly create 'SandBox' urls in eBMS Endpoint URLs"))

        else:
            try:
                api_list_doc = frappe.get_doc("eBMS Endpoint URLs", "Production")
            except frappe.DoesNotExistError:
                frappe.throw(_("Kindly create 'Production' urls in eBMS Endpoint URLs"))
            except Exception as e:
                frappe.throw(_("Error fetching Production URLs: {0}").format(str(e)))

        api_list = api_list_doc.get("apis")
        base_url = api_list_doc.get("server_url")
        for api_row in api_list:
            if api_row.get("method_name") == method_name:
                return f"{base_url}{api_row.get('api')}"

        frappe.throw(
            _(
                f"{method_name} {'Sandbox' if sandbox else 'Production'} URL was not found. Please add it in the eBMS endpoint URLs DocType"
            )
        )

    def wait_for_internet(self, delay=5):
        time.sleep(delay)  # Sleep for 10 seconds

    def enqueue_retry_task(self):
        job_id = frappe.enqueue(
            "burundi_compliance.burundi_compliance.utils.background_jobs.retry_authentication",
            queue="default",
            timeout=5,
            is_async=True,
            at_front=True,
        )
        return job_id
