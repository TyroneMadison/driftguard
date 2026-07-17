# Working in this repository (humans and AI agents)

DriftGuard is built AI-first: detection logic, tests, and docs are
drafted with AI pair engineering tools, then gated by deterministic
checks and human review. AI agents contributing here follow the same
contract.

## Layout

* guard/ is the scanner: parse plan JSON, classify severity, route
  alerts, decide remediation. Pure Python, PyYAML is the only runtime
  dependency. Keep it that way.
* policies/severity-rules.yaml is the reviewable heart of the system.
  Changing a severity is a pull request with a reviewer, never a hotfix.
* sample_data/ holds recorded terraform show -json output used by tests
  and the demo workflow. Extend it when adding new drift shapes.
* terraform/aws and terraform/azure hold the alert delivery rails and a
  small monitored demo stack per cloud.

## Guardrails

* make test must pass before proposing any change.
* Auto-remediation stays reserved for low severity, tag-only drift.
  Critical drift always pages a human. Do not soften this.
* Never commit state files, plan files, or credentials.
* New resource severity rules need a note explaining the why.

## Validation commands

    make test         # pytest suite
    make scan-demo    # end-to-end scan of recorded drift
    make tf-validate  # terraform validate both stacks (requires terraform)
