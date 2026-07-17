"""Decide what happens to each piece of drift.

Remediation is a decision tree, not a reflex. There are exactly two
honest ways to resolve drift and both are represented here:

* enforce: reality moved, the code is right, apply the code back.
* adopt: reality is right, the code is stale, update the code via PR.

Auto-apply is reserved for drift that is provably boring (tag-only) and
critical drift never self-heals silently: a human gets paged, because a
changed security group rule might be an attack, not an accident.
"""

from __future__ import annotations

from .plan_parser import DriftItem

AUTO_APPLY = "auto-apply"
OPEN_PR = "open-pr"
PAGE_HUMAN = "page-human"


def decide(item: DriftItem) -> str:
    if item.severity == "critical":
        return PAGE_HUMAN
    if item.auto_remediable and item.severity == "low":
        return AUTO_APPLY
    return OPEN_PR


def remediation_plan(items: list[DriftItem]) -> dict[str, list[dict]]:
    """Build the full remediation plan for a batch of classified drift."""
    plan: dict[str, list[dict]] = {AUTO_APPLY: [], OPEN_PR: [], PAGE_HUMAN: []}
    for item in items:
        decision = decide(item)
        command = None
        if decision == AUTO_APPLY:
            command = f"terraform apply -auto-approve -target={item.address}"
        elif decision == OPEN_PR:
            command = (
                "open PR: adopt with terraform plan -refresh-only, "
                f"or enforce with terraform apply -target={item.address}"
            )
        plan[decision].append(
            {
                "address": item.address,
                "stack": item.stack,
                "severity": item.severity,
                "action": item.action,
                "next_step": command or "page on-call with drift context",
            }
        )
    return plan


def summarize(plan: dict[str, list[dict]]) -> str:
    return (
        f"auto-apply: {len(plan[AUTO_APPLY])}, "
        f"open-pr: {len(plan[OPEN_PR])}, "
        f"page-human: {len(plan[PAGE_HUMAN])}"
    )
