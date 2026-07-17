# Drift triage runbook

## When a critical drift page arrives

1. Do not auto-remediate. A changed security rule outside a pipeline is
   a possible incident, and enforcing code over it can destroy evidence.
2. Identify the actor: CloudTrail event history on AWS, Activity Log on
   Azure, filtered to the drifted resource and the last 24 hours.
3. Classify:
   * Sanctioned break-glass change: capture the ticket, adopt or enforce
     through an expedited PR, close.
   * Unsanctioned but internal: enforce code, then have the process
     conversation with the team that clicked.
   * No identifiable actor: escalate to security immediately and freeze
     changes to the affected boundary.
4. Only after classification, resolve with one of the two honest moves:
   * enforce: terraform apply against the stack (code wins).
   * adopt: terraform plan -refresh-only, review, codify (reality wins).
5. Confirm the next scheduled scan reports clean.

## When the daily digest grows

A digest that doubles week over week means change management is leaking.
Check which stack and which team the growth concentrates in, and whether
an automation account or a shared admin credential is the common thread.

## When everything drifts at once

A sudden spike across many resources usually means someone applied with
local state, restored an old snapshot, or ran a script with broad write
permissions. Treat the state file as the first suspect: verify the
remote state timestamps and lock history before touching resources.
