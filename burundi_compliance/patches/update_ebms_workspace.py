import json
from pathlib import Path

import frappe


def execute():
    workspace_name = "Burundi Compliance"

    if not frappe.db.exists("Workspace", workspace_name):
        return

    source_path = (
        Path(frappe.get_app_path("burundi_compliance"))
        / "burundi_compliance"
        / "workspace"
        / "burundi_compliance"
        / "burundi_compliance.json"
    )

    source = json.loads(source_path.read_text())

    frappe.db.set_value(
        "Workspace",
        workspace_name,
        {
            "title": "eBMS",
            "label": source["label"],
            "content": source["content"],
        },
        update_modified=False,
    )

    frappe.db.delete(
        "Workspace Link",
        {
            "parent": workspace_name,
            "parenttype": "Workspace",
            "parentfield": "links",
            "label": ["in", ["Stock Entry", "Stock Reconciliation"]],
        },
    )

    frappe.clear_cache()
