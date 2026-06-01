from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.public_refresh_requirement_reextraction_delta_queue_v4 import (
    EXPECTED_VALIDATION_COMMANDS,
    build_queue_from_fixture,
    build_requirement_reextraction_delta_queue_v4,
    load_requirement_reextraction_delta_rows_v4,
    validate_requirement_reextraction_delta_queue_v4,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "public_refresh_requirement_reextraction_delta_queue_v4"
    / "requirement_reextraction_delta_rows.json"
)


def _valid_row() -> dict[str, object]:
    return dict(load_requirement_reextraction_delta_rows_v4(FIXTURE_PATH)[0])


def test_builds_fixture_first_requirement_reextraction_delta_queue_v4() -> None:
    queue = build_queue_from_fixture(FIXTURE_PATH)

    assert queue["queue_version"] == "public-refresh-requirement-reextraction-delta-queue-v4"
    assert queue["mode"] == "fixture_first_offline_delta_review_only"
    assert queue["row_count"] == 1
    assert queue["freshness_packet_refs"] == ["freshness-packet::ppd-devhub-faq::2026-05-08"]
    assert queue["source_evidence_placeholders"] == ["placeholder:evidence-devhub-faq-account-services"]
    assert queue["expected_requirement_types"] == ["action_gate", "precondition"]
    assert queue["affected_process_stages"] == ["account setup or manual login", "application data entry"]
    assert queue["human_review_statuses"] == ["needs_human_review"]
    assert queue["skipped_source_reasons"] == ["not_skipped_fixture_source"]
    assert queue["validation_commands"] == [list(command) for command in EXPECTED_VALIDATION_COMMANDS]

    candidate = queue["delta_candidates"][0]
    assert candidate["active_mutation"] is False
    assert candidate["live_crawl"] is False
    assert candidate["ocr_completed"] is False
    assert candidate["legal_or_permitting_guarantee"] is False


@pytest.mark.parametrize(
    "missing_key",
    [
        "freshness_packet_refs",
        "source_evidence_placeholders",
        "expected_requirement_types",
        "affected_process_stages",
        "human_review_status",
        "skipped_source_reasons",
        "reviewer_holds",
        "validation_commands",
    ],
)
def test_rejects_missing_required_delta_controls(missing_key: str) -> None:
    row = _valid_row()
    row.pop(missing_key)

    with pytest.raises(ValueError, match=missing_key):
        build_requirement_reextraction_delta_queue_v4([row])


@pytest.mark.parametrize(
    "flag",
    [
        "active_mutation",
        "active_requirement_mutation",
        "active_process_model_mutation",
        "active_guardrail_mutation",
        "live_crawl",
        "live_extraction",
        "ocr_completed",
        "raw_public_body_artifact",
        "private_artifact",
        "session_artifact",
        "auth_artifact",
        "legal_or_permitting_guarantee",
    ],
)
def test_rejects_true_external_runtime_or_mutation_flags(flag: str) -> None:
    row = _valid_row()
    row[flag] = True

    with pytest.raises(ValueError, match=flag):
        build_requirement_reextraction_delta_queue_v4([row])


@pytest.mark.parametrize(
    "key",
    [
        "raw_body",
        "raw_html",
        "public_body",
        "raw_public_body",
        "session_state",
        "auth_state",
        "devhub_session",
        "cookie",
        "access_token",
    ],
)
def test_rejects_raw_public_private_session_or_auth_artifact_keys(key: str) -> None:
    row = _valid_row()
    row[key] = "not allowed"

    with pytest.raises(ValueError, match="prohibited artifact key"):
        build_requirement_reextraction_delta_queue_v4([row])


@pytest.mark.parametrize(
    "claim",
    [
        "live crawl completed",
        "OCR completed",
        "guaranteed permit",
        "legal advice",
        "active requirement mutation",
        "active process model mutation",
        "active guardrail mutation",
    ],
)
def test_rejects_prohibited_claim_text(claim: str) -> None:
    row = _valid_row()
    row["candidate_summary"] = claim

    with pytest.raises(ValueError, match="prohibited claim phrase"):
        build_requirement_reextraction_delta_queue_v4([row])


@pytest.mark.parametrize(
    "queue_key",
    [
        "freshness_packet_refs",
        "source_evidence_placeholders",
        "expected_requirement_types",
        "affected_process_stages",
        "human_review_statuses",
        "skipped_source_reasons",
        "reviewer_holds",
    ],
)
def test_queue_validator_rejects_missing_output_sections(queue_key: str) -> None:
    queue = build_queue_from_fixture(FIXTURE_PATH)
    queue[queue_key] = []

    with pytest.raises(ValueError, match=queue_key):
        validate_requirement_reextraction_delta_queue_v4(queue)


def test_queue_validator_rejects_missing_validation_commands() -> None:
    queue = build_queue_from_fixture(FIXTURE_PATH)
    queue["validation_commands"] = []

    with pytest.raises(ValueError, match="validation_commands"):
        validate_requirement_reextraction_delta_queue_v4(queue)


def test_queue_validator_rejects_candidate_active_mutation_after_build() -> None:
    queue = build_queue_from_fixture(FIXTURE_PATH)
    mutated_queue = deepcopy(queue)
    mutated_queue["delta_candidates"][0]["active_mutation"] = True

    with pytest.raises(ValueError, match="active_mutation"):
        validate_requirement_reextraction_delta_queue_v4(mutated_queue)


def test_queue_validator_rejects_candidate_missing_source_evidence_placeholder_after_build() -> None:
    queue = build_queue_from_fixture(FIXTURE_PATH)
    mutated_queue = deepcopy(queue)
    mutated_queue["delta_candidates"][0]["source_evidence_placeholders"] = []

    with pytest.raises(ValueError, match="source_evidence_placeholders"):
        validate_requirement_reextraction_delta_queue_v4(mutated_queue)
