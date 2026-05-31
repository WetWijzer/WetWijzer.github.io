from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.crawler.public_crawl_retry_recovery_packet_v2 import (
    FORBIDDEN_MUTATION_MARKERS,
    REQUIRED_OFFLINE_COMMANDS,
    REQUIRED_SCENARIOS,
    load_packet,
    require_valid_packet,
    validate_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_crawl_retry_recovery_packet_v2.json"


def _valid_packet() -> dict:
    return load_packet(FIXTURE_PATH)


def test_retry_recovery_packet_v2_fixture_is_valid() -> None:
    packet = _valid_packet()

    assert validate_packet(packet) == []
    require_valid_packet(packet)


def test_retry_recovery_packet_v2_has_exact_required_scenarios() -> None:
    packet = _valid_packet()
    names = {scenario["name"] for scenario in packet["scenarios"]}

    assert names == REQUIRED_SCENARIOS


def test_retry_recovery_packet_v2_is_offline_and_commit_safe() -> None:
    packet = _valid_packet()

    for marker in FORBIDDEN_MUTATION_MARKERS:
        assert packet["mutation_boundaries"][marker] is False

    for scenario in packet["scenarios"]:
        assert scenario["fixture_only"] is True
        assert scenario["commits_raw_body"] is False
        assert scenario["executes_processor"] is False
        assert scenario["starts_crawler"] is False
        assert scenario["recovery_packet"]["reviewer_disposition_placeholder"] == "pending_reviewer_disposition"


def test_retry_recovery_packet_v2_lists_exact_offline_validation_commands() -> None:
    packet = _valid_packet()

    assert packet["offline_validation_commands"] == [list(command) for command in REQUIRED_OFFLINE_COMMANDS]


def test_retry_recovery_packet_v2_rejects_missing_required_scenario_rows() -> None:
    expected_missing = {
        "robots_policy_denial": "missing scenarios: robots_policy_denial",
        "synthetic_policy_denial": "missing scenarios: synthetic_policy_denial",
        "timeout_row": "missing scenarios: timeout_row",
        "redirect_changed": "missing scenarios: redirect_changed",
        "content_type_skip": "missing scenarios: content_type_skip",
        "too_large_skip": "missing scenarios: too_large_skip",
        "processor_handoff_failure": "missing scenarios: processor_handoff_failure",
        "no_raw_body_archive_decision": "missing scenarios: no_raw_body_archive_decision",
        "retry_backoff_plan": "missing scenarios: retry_backoff_plan",
        "reviewer_disposition_placeholder": "missing scenarios: reviewer_disposition_placeholder",
    }

    for scenario_name, expected_error in expected_missing.items():
        packet = _valid_packet()
        packet["scenarios"] = [
            scenario for scenario in packet["scenarios"] if scenario["name"] != scenario_name
        ]

        assert expected_error in validate_packet(packet)


def test_retry_recovery_packet_v2_rejects_missing_validation_commands() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"] = []

    assert "offline_validation_commands must exactly match the packet v2 offline command list" in validate_packet(packet)


def test_retry_recovery_packet_v2_rejects_private_session_browser_raw_or_downloaded_artifacts() -> None:
    packet = _valid_packet()
    packet["artifact_manifest"] = ["ppd/private-artifact/session-state.json"]

    errors = validate_packet(packet)

    assert "artifact_manifest must be empty for retry/recovery packet v2" in errors
    assert any("must not reference private/session/browser/raw/downloaded artifacts" in error for error in errors)


def test_retry_recovery_packet_v2_rejects_live_crawl_claims_and_legal_guarantees() -> None:
    packet = _valid_packet()
    packet["live_crawl_claims"] = ["live crawl completed"]
    packet["legal_or_permitting_guarantees"] = ["guaranteed permit approval"]

    errors = validate_packet(packet)

    assert "live_crawl_claims must be empty" in errors
    assert "legal_or_permitting_guarantees must be empty" in errors
    assert "packet must not include live crawl claims, legal claims, or permitting guarantees" in errors


def test_retry_recovery_packet_v2_rejects_active_mutation_flags() -> None:
    packet = _valid_packet()
    packet["mutation_boundaries"]["network_access"] = True
    packet["mutation_boundaries"]["archive_mutation"] = True

    errors = validate_packet(packet)

    assert "mutation_boundaries.network_access must be false" in errors
    assert "mutation_boundaries.archive_mutation must be false" in errors


def test_retry_recovery_packet_v2_rejects_missing_retry_backoff_plan_details() -> None:
    packet = _valid_packet()
    scenario = next(row for row in packet["scenarios"] if row["name"] == "retry_backoff_plan")
    scenario["retry_plan"] = {"decision": "retry_with_backoff", "backoff_seconds": []}

    assert "scenario retry_backoff_plan must include a retry/backoff plan" in validate_packet(packet)


def test_retry_recovery_packet_v2_rejects_missing_reviewer_dispositions() -> None:
    packet = _valid_packet()
    scenario = next(row for row in packet["scenarios"] if row["name"] == "timeout_row")
    scenario["recovery_packet"] = deepcopy(scenario["recovery_packet"])
    del scenario["recovery_packet"]["reviewer_disposition_placeholder"]

    assert "scenario timeout_row requires reviewer_disposition_placeholder" in validate_packet(packet)


def test_retry_recovery_packet_v2_rejects_weakened_specific_safety_rows() -> None:
    cases = [
        ("robots_policy_denial", "skip_reason", "not_robots", "scenario robots_policy_denial must model a robots/policy denial skip"),
        ("synthetic_policy_denial", "skip_reason", "not_policy", "scenario synthetic_policy_denial must model a local policy denial skip"),
        ("timeout_row", "skip_reason", "not_timeout", "scenario timeout_row must model a timeout skip"),
        ("redirect_changed", "skip_reason", "not_redirect", "scenario redirect_changed must model a redirect-change row"),
        ("content_type_skip", "skip_reason", "not_content_type", "scenario content_type_skip must model an unsupported content-type skip"),
        ("too_large_skip", "skip_reason", "not_too_large", "scenario too_large_skip must model a too-large skip"),
        ("processor_handoff_failure", "skip_reason", "not_processor", "scenario processor_handoff_failure must model a processor handoff failure"),
        (
            "no_raw_body_archive_decision",
            "archive_decision",
            "raw_body_persisted",
            "scenario no_raw_body_archive_decision must model the no-raw-body archive decision",
        ),
    ]

    for scenario_name, field, replacement, expected_error in cases:
        packet = _valid_packet()
        scenario = next(row for row in packet["scenarios"] if row["name"] == scenario_name)
        scenario["recovery_packet"] = deepcopy(scenario["recovery_packet"])
        scenario["recovery_packet"][field] = replacement

        assert expected_error in validate_packet(packet)
