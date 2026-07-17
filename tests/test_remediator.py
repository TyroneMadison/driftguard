from guard.remediator import AUTO_APPLY, OPEN_PR, PAGE_HUMAN, decide, remediation_plan, summarize


def test_critical_pages_a_human(classified_items):
    sg = next(i for i in classified_items if i.address == "aws_security_group.app")
    assert decide(sg) == PAGE_HUMAN


def test_tag_only_auto_applies(classified_items):
    tags = next(
        i for i in classified_items if i.address == "azurerm_storage_account.logs"
    )
    assert decide(tags) == AUTO_APPLY


def test_medium_opens_pr(classified_items):
    param = next(
        i for i in classified_items if i.address == "aws_ssm_parameter.feature_flag"
    )
    assert decide(param) == OPEN_PR


def test_plan_contains_next_steps(classified_items):
    plan = remediation_plan(classified_items)
    assert plan[PAGE_HUMAN], "expected at least one page decision"
    auto_steps = [e["next_step"] for e in plan[AUTO_APPLY]]
    assert any("terraform apply" in step for step in auto_steps)
    assert "page-human" in summarize(plan)
