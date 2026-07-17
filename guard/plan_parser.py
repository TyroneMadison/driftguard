"""Parse terraform plan JSON into drift items.

DriftGuard runs terraform plan on a schedule against unchanged code.
In that context, any planned change IS drift: either the real world
moved away from the code, or code merged without an apply. Both are
incidents waiting for a timestamp.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# Marker strings for the two asymmetric drift shapes.
MISSING_IN_CLOUD = "<resource missing in cloud>"
REMOVED_FROM_CODE = "<resource no longer in code>"


@dataclass
class DriftItem:
    stack: str
    address: str
    resource_type: str
    action: str  # update | replace | missing | unmanaged
    changed_attributes: list[str] = field(default_factory=list)
    severity: str = "medium"
    auto_remediable: bool = False
    note: str = ""

    @property
    def fingerprint_source(self) -> str:
        attrs = ",".join(sorted(self.changed_attributes))
        return f"{self.stack}|{self.address}|{self.action}|{attrs}"


def _diff_keys(before: dict | None, after: dict | None) -> list[str]:
    before = before or {}
    after = after or {}
    changed = []
    for key in sorted(set(before) | set(after)):
        if before.get(key) != after.get(key):
            changed.append(key)
    return changed


def parse_plan(plan_document: dict, stack: str) -> list[DriftItem]:
    """Convert a terraform show -json document into drift items."""
    items: list[DriftItem] = []

    for change in plan_document.get("resource_changes", []):
        actions = change.get("change", {}).get("actions", [])
        if actions in ([], ["no-op"], ["read"]):
            continue

        before = change.get("change", {}).get("before")
        after = change.get("change", {}).get("after")
        address = change.get("address", "<unknown>")
        rtype = change.get("type", "<unknown>")

        if actions == ["create"]:
            items.append(
                DriftItem(
                    stack=stack,
                    address=address,
                    resource_type=rtype,
                    action="missing",
                    changed_attributes=[MISSING_IN_CLOUD],
                )
            )
        elif actions == ["delete"]:
            items.append(
                DriftItem(
                    stack=stack,
                    address=address,
                    resource_type=rtype,
                    action="unmanaged",
                    changed_attributes=[REMOVED_FROM_CODE],
                )
            )
        elif "delete" in actions and "create" in actions:
            items.append(
                DriftItem(
                    stack=stack,
                    address=address,
                    resource_type=rtype,
                    action="replace",
                    changed_attributes=_diff_keys(before, after),
                )
            )
        else:
            items.append(
                DriftItem(
                    stack=stack,
                    address=address,
                    resource_type=rtype,
                    action="update",
                    changed_attributes=_diff_keys(before, after),
                )
            )

    return items


def load_plan_file(path: str | Path, stack: str) -> list[DriftItem]:
    with open(path, encoding="utf-8") as fh:
        return parse_plan(json.load(fh), stack)
