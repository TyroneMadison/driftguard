# Alerting that people act on instead of mute

Alert fatigue is not a volume problem, it is a trust problem. Engineers
mute channels when alerts stop predicting action. DriftGuard is designed
around three rules that keep the signal trustworthy.

## 1. Severity decides the channel

| Severity | Channel | Examples |
| --- | --- | --- |
| critical | immediate page | security group or NSG rules, IAM and RBAC |
| high | immediate channel message | database and storage configuration |
| medium | daily digest | app settings, parameters, replacements |
| low | weekly digest | tag-only drift |

A tag change never pages anyone at 3 AM. A new inbound rule on a
security group always does, because outside a pipeline that pattern is
indistinguishable from an intrusion.

## 2. Deduplication with a window

The same fingerprint (stack, address, action, changed attributes) never
alerts twice inside 24 hours. Known drift awaiting a fix becomes a
digest line, not a daily page. The dedupe state is a small JSON file, so
the mechanism is inspectable and resettable.

## 3. Every alert carries its next action

Findings arrive with the remediation decision attached: auto-apply,
open a PR, or page a human. The two honest resolutions are named
explicitly:

* enforce: reality moved, code is right. Apply code back to reality.
* adopt: reality is right, code is stale. Update code through review.

An alert that only says something changed is trivia. An alert that says
what changed, how bad it is, and what to do next is operations.
