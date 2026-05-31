from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.devhub.reversible_draft_executor_review_packet_v2 import (
    assert_valid_reversible_draft_executor_review_packet_v2,
    validate_reversible_draft_executor_review_packet_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "reversible_draft_executor_review_packet_v2" / "valid_packet.json"


def _valid_packet() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _issue_codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_reversible_draft_executor_review_packet_v2(packet)}


def test_valid_reversible_draft_executor_review_packet_v2_fixture_passes() -> None:
    packet = _valid_packet()

    assert validate_reversible_draft_executor_review_packet_v2(packet) == []
    assert_valid_reversible_draft_executor_review_packet_v2(packet)


def test_rejects_missing_reviewer_rows() -> None:
    packet = _valid_packet()
    packet["reviewer_rows"] = []

    assert "missing_reviewer_rows" in _issue_codes(packet)


def test_rejects_missing_dry_run_request_acceptance_fields() -> None:
    packet = _valid_packet()
    del packet["dry_run_request_acceptance"]["accepted_at"]

    assert "missing_dry_run_request_acceptance_field" in _issue_codes(packet)


def test_rejects_missing_preview_only_response_review_fields() -> None:
    packet = _valid_packet()
    packet["preview_only_response_review"]["preview_only"] = False

    assert "preview_only_not_confirmed" in _issue_codes(packet)


def test_rejects_missing_user_fact_trace_review() -> None:
    packet = _valid_packet()
    packet["trace_review"]["user_fact_trace_review"] = []

    assert "missing_trace_review" in _issue_codes(packet)


def test_rejects_missing_source_evidence_trace_review() -> None:
    packet = _valid_packet()
    packet["trace_review"]["source_evidence_trace_review"] = []

    assert "missing_trace_review" in _issue_codes(packet)


def test_rejects_missing_selector_confidence_hold_reasons() -> None:
    packet = _valid_packet()
    del packet["selector_confidence_review"]["selectors"][0]["hold_reason"]

    assert "missing_selector_hold_reason" in _issue_codes(packet)


def test_rejects_missing_exact_confirmation_stop_gate_review() -> None:
    packet = _valid_packet()
    packet["exact_confirmation_stop_gate_review"]["exact_confirmation_required"] = False

    assert "stop_gate_not_confirmed" in _issue_codes(packet)


def test_rejects_missing_refused_consequential_action_review() -> None:
    packet = _valid_packet()
    packet["refused_consequential_action_review"]["refused_actions"] = []

    assert "missing_refused_actions" in _issue_codes(packet)


def test_rejects_missing_validation_commands() -> None:
    packet = _valid_packet()
    packet["validation_commands"] = []

    assert "missing_validation_commands" in _issue_codes(packet)


def test_rejects_private_session_browser_raw_and_downloaded_artifacts() -> None:
    forbidden_values = [
        "private_artifact",
        "session_file",
        "browser_trace",
        "raw_crawl_output",
        "downloaded_document",
    ]

    for forbidden_value in forbidden_values:
        packet = _valid_packet()
        packet["notes"] = forbidden_value
        assert "forbidden_artifact_reference" in _issue_codes(packet)


def test_rejects_live_devhub_execution_and_official_submission_claims() -> None:
    forbidden_values = [
        "Live DevHub execution completed",
        "Official draft saved",
        "Permit submitted",
    ]

    for forbidden_value in forbidden_values:
        packet = _valid_packet()
        packet["notes"] = forbidden_value
        assert "forbidden_claim" in _issue_codes(packet)


def test_rejects_legal_or_permitting_guarantees() -> None:
    forbidden_values = [
        "Guaranteed approval",
        "Legal advice",
        "Compliance guaranteed",
    ]

    for forbidden_value in forbidden_values:
        packet = _valid_packet()
        packet["notes"] = forbidden_value
        assert "forbidden_claim" in _issue_codes(packet)


def test_rejects_active_mutation_flags() -> None:
    for flag in packet_mutation_flags():
        packet = _valid_packet()
        packet["mutation_flags"][flag] = True
        assert "active_mutation_flag" in _issue_codes(packet)


def packet_mutation_flags() -> list[str]:
    return [
        "prompt_mutation_active",
        "guardrail_mutation_active",
        "devhub_surface_mutation_active",
        "source_mutation_active",
        "contract_mutation_active",
        "release_state_mutation_active",
    ]


def test_rejects_packet_missing_each_required_top_level_section() -> None:
    packet = _valid_packet()

    for section in list(packet):
        if section in {"packet_version", "packet_id", "notes"}:
            continue
        candidate = copy.deepcopy(packet)
        del candidate[section]
        assert "missing_section" in _issue_codes(candidate)
