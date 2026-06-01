from pathlib import Path

import pytest

from ppd.agent_readiness.stale_source_agent_hold_packet_v1 import (
    PACKET_VERSION,
    build_packet_from_fixture,
    build_stale_source_agent_hold_packet,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "stale_source_agent_hold_packet_v1"
    / "synthetic_monitoring_outcomes.json"
)


def test_fixture_maps_monitoring_rows_to_agent_hold_packet() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["mode"] == "fixture_first_offline_hold"
    assert packet["mutation_policy"] == "read_only_candidate_packet_only"
    assert packet["input_row_count"] == 3

    assert packet["affected_source_ids"] == [
        "source-devhub-permit-application-guide",
        "source-fee-payment-guide",
        "source-submit-plans-online-single-pdf",
    ]
    assert packet["affected_process_ids"] == [
        "process-building-permit-application",
        "process-fee-payment-review",
    ]
    assert packet["affected_guardrail_bundle_ids"] == [
        "guardrail-building-permit-application",
        "guardrail-fee-payment",
    ]

    missing_check_ids = {item["check_id"] for item in packet["missing_information_checks"]}
    assert "missing-info::outcome-001::permit_type_selection_complete" in missing_check_ids
    assert "missing-info::outcome-002::document_package_complete" in missing_check_ids
    assert "missing-info::outcome-003::payment_guidance_cited" in missing_check_ids
    assert all(item["requires_private_user_fact"] is False for item in packet["missing_information_checks"])

    blocked_check_ids = {item["check_id"] for item in packet["blocked_action_checks"]}
    assert "blocked-action::outcome-001::dynamic_questions_current" in blocked_check_ids
    assert "blocked-action::outcome-002::file_preparation_current" in blocked_check_ids
    assert "blocked-action::outcome-003::payment_guidance_cited" not in blocked_check_ids

    changes = {item["change_id"]: item for item in packet["next_safe_action_changes"]}
    assert changes["next-safe-action::outcome-001"]["to"] == "hold_for_offline_source_freshness_review"
    assert changes["next-safe-action::outcome-002"]["requires_live_crawl"] is False
    assert changes["next-safe-action::outcome-003"]["requires_devhub_access"] is False

    warnings = {item["warning_id"]: item for item in packet["citation_warnings"]}
    assert warnings[
        "citation-warning::outcome-003::citation::source-fee-payment-guide"
    ]["agent_may_quote_as_current"] is False

    holds = {item["hold_id"]: item for item in packet["reviewer_holds"]}
    assert holds["reviewer-hold::outcome-002"]["allowed_disposition"] == [
        "confirm_fixture",
        "refresh_public_source_later",
        "keep_hold",
    ]


def test_packet_declares_only_offline_validation_commands_and_forbidden_mutations() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet[
        "offline_validation_commands"
    ]
    command_text = " ".join(" ".join(command) for command in packet["offline_validation_commands"])
    assert "curl" not in command_text
    assert "playwright" not in command_text
    assert "devhub" not in command_text.lower()

    prohibited = set(packet["prohibited_mutations"])
    assert "private_user_facts" in prohibited
    assert "live_crawling" in prohibited
    assert "devhub_access" in prohibited
    assert "active_guardrail_mutation" in prohibited
    assert "daemon_state_mutation" in prohibited


def test_private_or_runtime_fields_are_rejected() -> None:
    row = {
        "row_id": "bad-row",
        "source_id": "source-x",
        "canonical_url": "https://www.portland.gov/ppd/example",
        "outcome": "stale",
        "severity": "high",
        "observed_at": "2026-06-01T10:19:00Z",
        "affected_process_ids": [],
        "affected_requirement_ids": [],
        "affected_guardrail_bundle_ids": [],
        "affected_agent_checks": [],
        "citation_ids": [],
        "current_next_safe_action": "draft",
        "replacement_next_safe_action": "hold",
        "reviewer_note": "hold",
        "user_email": "private@example.invalid",
    }

    with pytest.raises(ValueError, match="private or runtime-only"):
        build_stale_source_agent_hold_packet([row])
