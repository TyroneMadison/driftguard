from guard.plan_parser import MISSING_IN_CLOUD, load_plan_file, parse_plan


def test_clean_plan_reports_nothing(repo_root):
    items = load_plan_file(repo_root / "sample_data" / "plan_clean.json", "demo")
    assert items == []


def test_drift_plan_reports_all_shapes(drift_items):
    by_address = {item.address: item for item in drift_items}
    assert len(drift_items) == 4

    sg = by_address["aws_security_group.app"]
    assert sg.action == "update"
    assert "ingress" in sg.changed_attributes

    missing = by_address["aws_ssm_parameter.feature_flag"]
    assert missing.action == "missing"
    assert missing.changed_attributes == [MISSING_IN_CLOUD]

    replaced = by_address["aws_instance.legacy_worker"]
    assert replaced.action == "replace"
    assert "ami" in replaced.changed_attributes


def test_read_and_noop_actions_are_ignored():
    doc = {
        "resource_changes": [
            {"address": "a", "type": "t", "change": {"actions": ["no-op"]}},
            {"address": "b", "type": "t", "change": {"actions": ["read"]}},
        ]
    }
    assert parse_plan(doc, "demo") == []
