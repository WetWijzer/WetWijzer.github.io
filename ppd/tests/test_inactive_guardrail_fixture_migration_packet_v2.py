from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.inactive_guardrail_fixture_migration_packet_v2 import (
    PACKET_TYPE,
    REQUIRED_ATTESTATIONS,
    build_inactive_guardrail_fixture_migration_packet_v2_from_fixture,
    validate_inactive_guardrail_fixture_migration_packet_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "inactive_guardrail_fixture_migration_packet_v2" / "source_packets.json"


def valid_packet() -> dict[str, object]:
    return build_inactive_guardrail_fixture_migration_packet_v2_from_fixture(FIXTURE)


def test_builds_fixture_first_inactive_guardrail_fixture_migration_packet_v2() -> None:
    packet = valid_packet()

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["packet_version"] == 2
    assert packet["mode"] == "fixture_first_inactive_guardrail_predicate_rows_only"
    assert packet["attestations"] == REQUIRED_ATTESTATIONS
    assert packet["attestations"]["no_active_source_mutation"] is True
    assert packet["attestations"]["no_active_surface_registry_mutation"] is True
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]

    predicate_rows = packet["cited_fixture_only_guardrail_predicate_rows"]
    template_checks = packet["before_after_explanation_template_checks"]
    blocked_checks = packet["blocked_consequential_action_regression_checks"]

    assert predicate_rows
    assert template_checks
    assert blocked_checks
    assert packet["rollback_checkpoints"]
    assert packet["reviewer_owner_fields"]

    first = predicate_rows[0]
    assert first["fixture_only"] is True
    assert first["inactive"] is True
    assert first["active_guardrail_mutation"] is False
    assert first["active_prompt_mutation"] is False
    assert first["citations"]
    assert len(first["before_fixture_checksum"]) == 64
    assert len(first["after_fixture_checksum"]) == 64
    validate_inactive_guardrail_fixture_migration_packet_v2(packet)


def test_packet_carries_explanation_template_checks_blocked_regressions_rollback_and_reviewers() -> None:
    packet = valid_packet()

    template = packet["before_after_explanation_template_checks"][0]
    assert template["before_template"]
    assert template["after_template"]
    assert template["active_prompt_mutation"] is False
    assert template["citations"]

    blocked = packet["blocked_consequential_action_regression_checks"][0]
    assert blocked["before_blocked"] is True
    assert blocked["after_blocked"] is True
    assert blocked["consequential_action_remains_blocked"] is True
    assert blocked["citations"]

    rollback = packet["rollback_checkpoints"][0]
    assert rollback["active_guardrail_or_prompt_unchanged"] is True
    assert rollback["reviewer_owner"]
    assert rollback["citations"]

    owner = packet["reviewer_owner_fields"][0]
    assert owner["reviewer_owner"]
    assert owner["linked_row_ids"]
    assert owner["citations"]


def test_validation_rejects_missing_fixture_rows_templates_blocked_checks_rollback_and_owners() -> None:
    base = valid_packet()

    cases = [
        ("cited_fixture_only_guardrail_predicate_rows", "guardrail predicate rows"),
        ("before_after_explanation_template_checks", "explanation-template checks"),
        ("blocked_consequential_action_regression_checks", "consequential-action regression checks"),
        ("rollback_checkpoints", "rollback checkpoints"),
        ("reviewer_owner_fields", "reviewer-owner fields"),
    ]

    for key, message in cases:
        broken = deepcopy(base)
        broken[key] = []
        with pytest.raises(ValueError, match=message):
            validate_inactive_guardrail_fixture_migration_packet_v2(broken)


def test_validation_rejects_uncited_rows_and_unblocked_consequential_actions() -> None:
    packet = valid_packet()

    for section in (
        "cited_fixture_only_guardrail_predicate_rows",
        "before_after_explanation_template_checks",
        "blocked_consequential_action_regression_checks",
        "rollback_checkpoints",
    ):
        uncited = deepcopy(packet)
        uncited[section][0]["citations"] = []
        with pytest.raises(ValueError, match="citations must be non-empty"):
            validate_inactive_guardrail_fixture_migration_packet_v2(uncited)

    unblocked = deepcopy(packet)
    unblocked["blocked_consequential_action_regression_checks"][0]["after_blocked"] = False
    with pytest.raises(ValueError, match="must keep consequential actions blocked"):
        validate_inactive_guardrail_fixture_migration_packet_v2(unblocked)


def test_validation_rejects_missing_before_after_template_fields_and_blocked_regression_fields() -> None:
    packet = valid_packet()

    for field in ("before_template", "after_template"):
        broken = deepcopy(packet)
        broken["before_after_explanation_template_checks"][0][field] = ""
        with pytest.raises(ValueError, match=f"{field} must be present"):
            validate_inactive_guardrail_fixture_migration_packet_v2(broken)

    for field in ("before_blocked", "after_blocked"):
        broken = deepcopy(packet)
        broken["blocked_consequential_action_regression_checks"][0][field] = False
        with pytest.raises(ValueError, match="must keep consequential actions blocked"):
            validate_inactive_guardrail_fixture_migration_packet_v2(broken)


def test_validation_rejects_missing_no_live_no_mutation_attestations() -> None:
    packet = valid_packet()
    broken = deepcopy(packet)
    broken["attestations"]["no_active_surface_registry_mutation"] = False

    with pytest.raises(ValueError, match="no-live/no-active-mutation"):
        validate_inactive_guardrail_fixture_migration_packet_v2(broken)


def test_validation_rejects_active_guardrail_prompt_source_surface_monitoring_release_and_agent_mutation_flags() -> None:
    flags = (
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_source_mutation",
        "active_surface_registry_mutation",
        "active_monitoring_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
        "source_mutation_enabled",
        "surface_registry_mutation_enabled",
    )

    for flag in flags:
        packet = valid_packet()
        packet["cited_fixture_only_guardrail_predicate_rows"][0][flag] = True
        with pytest.raises(ValueError, match="mutation flag|active guardrail and prompt mutation false"):
            validate_inactive_guardrail_fixture_migration_packet_v2(packet)

    for nested_key in ("guardrail", "prompt", "source", "surface_registry", "monitoring", "release_state", "agent_state"):
        nested = valid_packet()
        nested["mutation_flags"] = {nested_key: True}
        with pytest.raises(ValueError, match="mutation flag"):
            validate_inactive_guardrail_fixture_migration_packet_v2(nested)


def test_validation_rejects_private_authenticated_raw_live_guarantee_and_consequential_language() -> None:
    cases = [
        {"private_fact": "owner name"},
        {"authenticated_fact": "permit dashboard value"},
        {"llm_response": "called live llm"},
        {"auth_state": "storage-state.json"},
        {"browser_session": "session.zip"},
        {"raw_pdf": "raw bytes"},
        {"raw_crawl": "raw crawl bytes"},
        {"note": "processor completed for this packet"},
        {"note": "opened DevHub during this packet"},
        {"note": "guaranteed permit approval"},
        {"note": "legal outcome guaranteed"},
        {"note": "final submission is ready"},
        {"note": "submit payment from the packet"},
        {"note": "final upload has been enabled"},
        {"note": "schedule inspection now"},
        {"note": "cancel permit from this migration"},
    ]

    for injected in cases:
        packet = valid_packet()
        packet["unsafe_test_field"] = injected
        with pytest.raises(ValueError, match="prohibited|mutation flag"):
            validate_inactive_guardrail_fixture_migration_packet_v2(packet)
