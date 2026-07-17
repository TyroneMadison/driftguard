"""Severity classification driven by a reviewable policy file.

The difference between an alerting system people trust and one they mute
is whether severity decisions are explicit. These rules live in YAML,
under version control, next to the code they protect.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

from .plan_parser import DriftItem

TAG_ONLY_ATTRIBUTES = {"tags", "tags_all"}

DEFAULT_RULE = {
    "severity": "medium",
    "auto_remediable": False,
    "note": "No explicit policy matched, defaulting to medium.",
}


def load_rules(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        document = yaml.safe_load(fh)
    return document.get("rules", [])


def is_tag_only(item: DriftItem) -> bool:
    attrs = set(item.changed_attributes)
    return bool(attrs) and attrs.issubset(TAG_ONLY_ATTRIBUTES)


def classify(item: DriftItem, rules: list[dict]) -> DriftItem:
    """Assign severity and remediation eligibility to one drift item."""
    # Tag-only drift is noise with a paper trail. Downgrade and auto-fix.
    if item.action == "update" and is_tag_only(item):
        item.severity = "low"
        item.auto_remediable = True
        item.note = "Tag-only drift, safe to enforce from code."
        return item

    for rule in rules:
        pattern = rule.get("match", "*")
        if fnmatch.fnmatch(item.resource_type, pattern) or fnmatch.fnmatch(
            item.address, pattern
        ):
            item.severity = rule.get("severity", DEFAULT_RULE["severity"])
            item.auto_remediable = bool(rule.get("auto_remediable", False))
            item.note = rule.get("note", "")
            return item

    item.severity = DEFAULT_RULE["severity"]
    item.auto_remediable = DEFAULT_RULE["auto_remediable"]
    item.note = DEFAULT_RULE["note"]
    return item


def classify_all(items: list[DriftItem], rules: list[dict]) -> list[DriftItem]:
    return [classify(item, rules) for item in items]
