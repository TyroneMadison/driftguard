from guard.plan_parser import DriftItem
from guard.severity import classify, classify_all, load_rules


def test_security_group_drift_is_critical(classified_items):
    sg = next(i for i in classified_items if i.address == "aws_security_group.app")
    assert sg.severity == "critical"
    assert sg.auto_remediable is False


def test_tag_only_drift_is_low_and_auto_remediable(classified_items):
    tags = next(
        i for i in classified_items if i.address == "azurerm_storage_account.logs"
    )
    assert tags.severity == "low"
    assert tags.auto_remediable is True


def test_unmatched_resource_defaults_to_medium(repo_root):
    rules = load_rules(repo_root / "policies" / "severity-rules.yaml")
    item = DriftItem(
        stack="demo",
        address="aws_route53_record.api",
        resource_type="aws_route53_record",
        action="update",
        changed_attributes=["ttl"],
    )
    classified = classify(item, rules)
    assert classified.severity == "medium"


def test_classify_all_preserves_count(classified_items, drift_items):
    assert len(classified_items) == len(drift_items)
