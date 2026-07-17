"""Route drift into alerts people act on instead of mute.

Three principles:
1. Severity decides the channel, not the volume of findings.
2. Deduplication: the same drift never pages twice inside its window.
3. Every alert carries the next action, not just the observation.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .plan_parser import DriftItem

IMMEDIATE = "immediate"
DAILY_DIGEST = "daily-digest"
WEEKLY_DIGEST = "weekly-digest"

CHANNEL_BY_SEVERITY = {
    "critical": IMMEDIATE,
    "high": IMMEDIATE,
    "medium": DAILY_DIGEST,
    "low": WEEKLY_DIGEST,
}

DEDUPE_WINDOW_SECONDS = 24 * 3600


def fingerprint(item: DriftItem) -> str:
    return hashlib.sha256(item.fingerprint_source.encode("utf-8")).hexdigest()[:16]


class DedupeState:
    """Tiny JSON-backed memory of which fingerprints alerted recently."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.seen: dict[str, float] = {}
        if self.path.exists():
            self.seen = json.loads(self.path.read_text())

    def is_fresh(self, fp: str, now: float | None = None,
                 window: int = DEDUPE_WINDOW_SECONDS) -> bool:
        now = time.time() if now is None else now
        last = self.seen.get(fp)
        return last is None or (now - last) > window

    def mark(self, fp: str, now: float | None = None) -> None:
        self.seen[fp] = time.time() if now is None else now

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.seen, indent=2))


def route(items: list[DriftItem], state: DedupeState | None = None,
          now: float | None = None) -> dict[str, list[DriftItem]]:
    """Group actionable drift by delivery channel, suppressing repeats."""
    routed: dict[str, list[DriftItem]] = {
        IMMEDIATE: [],
        DAILY_DIGEST: [],
        WEEKLY_DIGEST: [],
    }
    for item in items:
        fp = fingerprint(item)
        if state is not None:
            if not state.is_fresh(fp, now=now):
                continue
            state.mark(fp, now=now)
        channel = CHANNEL_BY_SEVERITY.get(item.severity, DAILY_DIGEST)
        routed[channel].append(item)
    return routed


SEVERITY_EMOJI = {
    "critical": ":rotating_light:",
    "high": ":warning:",
    "medium": ":mag:",
    "low": ":label:",
}


def format_slack(items: list[DriftItem], title: str = "DriftGuard report") -> dict:
    """Build a Slack Block Kit payload for one batch of drift."""
    lines = []
    for item in items:
        emoji = SEVERITY_EMOJI.get(item.severity, ":grey_question:")
        attrs = ", ".join(item.changed_attributes) or "n/a"
        lines.append(
            f"{emoji} *{item.severity.upper()}* `{item.address}` "
            f"({item.stack}) action *{item.action}*, changed: {attrs}"
        )
    body = "\n".join(lines) if lines else "No actionable drift. Quiet is a feature."
    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": title},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": body},
            },
        ]
    }


def format_text(routed: dict[str, list[DriftItem]]) -> str:
    lines = []
    for channel in (IMMEDIATE, DAILY_DIGEST, WEEKLY_DIGEST):
        batch = routed.get(channel, [])
        lines.append(f"[{channel}] {len(batch)} item(s)")
        for item in batch:
            attrs = ", ".join(item.changed_attributes) or "n/a"
            lines.append(
                f"  {item.severity.upper():<8} {item.address} "
                f"({item.stack}) {item.action}: {attrs}"
            )
            if item.note:
                lines.append(f"           note: {item.note}")
    return "\n".join(lines)
