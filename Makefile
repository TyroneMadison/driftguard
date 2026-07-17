PYTHON ?= python3

.PHONY: help install test scan-demo scan-clean tf-validate

help:
	@echo "Targets: install, test, scan-demo, scan-clean, tf-validate"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest tests -q

scan-demo:
	$(PYTHON) -m guard.cli scan --plan-json sample_data/plan_drift.json --stack demo --no-dedupe --exit-zero

scan-clean:
	$(PYTHON) -m guard.cli scan --plan-json sample_data/plan_clean.json --stack demo --no-dedupe

tf-validate:
	@for dir in terraform/aws terraform/azure; do \
		echo "== $$dir"; \
		terraform -chdir=$$dir init -backend=false -input=false > /dev/null; \
		terraform -chdir=$$dir validate; \
	done
