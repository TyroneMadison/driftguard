import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from guard.plan_parser import load_plan_file  # noqa: E402
from guard.severity import classify_all, load_rules  # noqa: E402


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def drift_items(repo_root):
    return load_plan_file(repo_root / "sample_data" / "plan_drift.json", stack="demo")


@pytest.fixture
def classified_items(repo_root, drift_items):
    rules = load_rules(repo_root / "policies" / "severity-rules.yaml")
    return classify_all(drift_items, rules)
