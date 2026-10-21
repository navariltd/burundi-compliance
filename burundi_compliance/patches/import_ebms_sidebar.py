from pathlib import Path

import frappe
from frappe.modules.import_file import import_file_by_path


def execute():
    sidebar_path = (
        Path(frappe.get_app_path("burundi_compliance"))
        / "workspace_sidebar"
        / "ebms.json"
    )

    if not sidebar_path.is_file():
        raise FileNotFoundError(f"eBMS sidebar configuration not found: {sidebar_path}")

    import_file_by_path(str(sidebar_path), force=True)

    frappe.clear_cache()
