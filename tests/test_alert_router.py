from guard.alert_router import (
    DAILY_DIGEST,
    IMMEDIATE,
    WEEKLY_DIGEST,
    DedupeState,
    fingerprint,
    format_slack,
    route,
)


def test_routing_by_severity(classified_items):
    routed = route(classified_items)
    immediate_addresses = {i.address for i in routed[IMMEDIATE]}
    assert "aws_security_group.app" in immediate_addresses
    weekly_addresses = {i.address for i in routed[WEEKLY_DIGEST]}
    assert "azurerm_storage_account.logs" in weekly_addresses
    assert isinstance(routed[DAILY_DIGEST], list)


def test_dedupe_suppresses_repeat_alerts(tmp_path, classified_items):
    state = DedupeState(tmp_path / "state.json")
    first = route(classified_items, state=state, now=1000.0)
    assert sum(len(v) for v in first.values()) == len(classified_items)

    second = route(classified_items, state=state, now=2000.0)
    assert sum(len(v) for v in second.values()) == 0


def test_dedupe_window_expires(tmp_path, classified_items):
    state = DedupeState(tmp_path / "state.json")
    route(classified_items, state=state, now=0.0)
    later = route(classified_items, state=state, now=100000.0)
    assert sum(len(v) for v in later.values()) == len(classified_items)


def test_fingerprints_are_stable_and_distinct(classified_items):
    fps = [fingerprint(i) for i in classified_items]
    assert len(set(fps)) == len(fps)
    assert fingerprint(classified_items[0]) == fingerprint(classified_items[0])


def test_slack_payload_carries_addresses(classified_items):
    payload = format_slack(classified_items)
    body = payload["blocks"][1]["text"]["text"]
    assert "aws_security_group.app" in body
