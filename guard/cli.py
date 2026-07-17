"""DriftGuard command line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .alert_router import DedupeState, format_text, route
from .plan_parser import load_plan_file
from .remediator import PAGE_HUMAN, remediation_plan, summarize
from .severity import classify_all, load_rules


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="driftguard",
        description="Multi-cloud drift detection with actionable alerting.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a terraform plan JSON for drift")
    scan.add_argument("--plan-json", required=True,
                      help="Output of terraform show -json <planfile>")
    scan.add_argument("--stack", required=True,
                      help="Stack label, for example aws-prod")
    scan.add_argument("--rules", default="policies/severity-rules.yaml")
    scan.add_argument("--state", default=".driftguard/state.json",
                      help="Dedupe state file")
    scan.add_argument("--no-dedupe", action="store_true",
                      help="Report every finding regardless of history")
    scan.add_argument("--exit-zero", action="store_true",
                      help="Always exit 0 (demo and digest modes)")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "scan":
        items = load_plan_file(args.plan_json, stack=args.stack)
        rules = load_rules(args.rules)
        items = classify_all(items, rules)

        state = None if args.no_dedupe else DedupeState(Path(args.state))
        routed = route(items, state=state)
        if state is not None:
            state.save()

        print(format_text(routed))
        print()

        plan = remediation_plan([i for batch in routed.values() for i in batch])
        print(f"remediation plan -> {summarize(plan)}")
        for decision, entries in plan.items():
            for entry in entries:
                print(f"  [{decision}] {entry['address']}: {entry['next_step']}")

        if args.exit_zero:
            return 0
        if plan[PAGE_HUMAN]:
            return 2
        if any(routed.values()):
            return 1
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
