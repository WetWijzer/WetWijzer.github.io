from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from ppd.agent_readiness.inactive_promotion_candidate_packet_v2 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    InactivePromotionCandidatePacketV2Error,
    assert_valid_inactive_promotion_candidate_packet_v2,
    build_inactive_promotion_candidate_packet_v2,
    build_inactive_promotion_candidate_packet_v2_from_file,
    load_json_object,
    validate_inactive_promotion_candidate_packet_v2,
)

FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "inactive_promotion_candidate_packet_v2"
    / "approved_combined_rehearsal_v1.json"
)


def _packet() -> dict[str, Any]:
    return build_inactive_promotion_candidate_packet_v2_from_file(FIXTURE)


def test_builds_inactive_candidate_deltas_from_approved_rehearsal_rows() -> None:
    packet = _packet()

    assert packet["packet_type"] == "ppd.inactive_promotion_candidate_packet.v2"
    assert packet["mode"] == "fixture_first_inactive_candidate_only"
    assert packet["consumed_approved_dependency_row_ids"] == [
        "dependency-001-devhub-application-guide-draft-surface",
        "dependency-002-single-pdf-upload-staging-surface",
    ]
    assert packet["inactive_source_registry_candidate_deltas"][0]["active_source_mutation"] is False
    assert packet["inactive_archive_manifest_candidate_deltas"][0]["raw_body_persisted"] is False
    assert packet["inactive_normalized_document_candidate_references"][0]["candidate_status"] == "inactive_reference_only"
    assert packet["inactive_devhub_surface_candidate_deltas"][0]["requires_attendance"] is True
    assert packet["inactive_devhub_surface_candidate_deltas"][0]["requires_exact_confirmation"] is True
    assert packet["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert_valid_inactive_promotion_candidate_packet_v2(packet)


def test_packet_includes_guardrail_replay_prerequisites_and_unsigned_signoff_placeholders() -> None:
    packet = _packet()

    assert packet["guardrail_replay_prerequisites"][0] == {
        "guardrail_replay_ref": "guardrail-replay-prerequisite:dependency-001-devhub-application-guide-draft-surface",
        "dependency_row_id": "dependency-001-devhub-application-guide-draft-surface",
        "required_source_evidence_ids": ["source:ppd-devhub-guide-submit-permit-application#draft-save-for-later"],
        "required_requirement_ids": ["requirement:devhub-application-draft-save-for-later"],
        "required_surface_ids": ["devhub-permit-application-draft-surface"],
        "expected_replay_mode": "offline_fixture_only",
        "required_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
        "active_guardrail_mutation": False,
    }
    assert packet["reviewer_signoff_placeholders"][0] == {
        "signoff_id": "reviewer-signoff:dependency-001-devhub-application-guide-draft-surface",
        "dependency_row_id": "dependency-001-devhub-application-guide-draft-surface",
        "reviewer": "",
        "reviewed_at": "",
        "decision": "pending_manual_review",
        "notes": "",
    }


def test_rejects_unapproved_dependency_rehearsal_rows() -> None:
    rehearsal = copy.deepcopy(load_json_object(FIXTURE))
    rehearsal["dependency_rows"][0]["reviewer_approval_status"] = "pending"

    with pytest.raises(InactivePromotionCandidatePacketV2Error, match="reviewer_approval_status"):
        build_inactive_promotion_candidate_packet_v2(rehearsal)


@pytest.mark.parametrize(
    "section",
    [
        "inactive_source_registry_candidate_deltas",
        "inactive_archive_manifest_candidate_deltas",
        "inactive_normalized_document_candidate_references",
        "inactive_devhub_surface_candidate_deltas",
        "guardrail_replay_prerequisites",
        "reviewer_signoff_placeholders",
    ],
)
def test_rejects_missing_inactive_candidate_sections_replay_prerequisites_and_signoffs(section: str) -> None:
    packet = _packet()
    packet[section] = []

    result = validate_inactive_promotion_candidate_packet_v2(packet)

    assert not result.valid
    assert f"{section} must be a non-empty list" in "; ".join(result.problems)


def test_rejects_missing_validation_commands() -> None:
    packet = _packet()
    packet.pop("exact_offline_validation_commands")

    result = validate_inactive_promotion_candidate_packet_v2(packet)

    assert not result.valid
    assert "exact_offline_validation_commands must match" in "; ".join(result.problems)


def test_rejects_missing_guardrail_replay_prerequisite_details() -> None:
    packet = _packet()
    packet["guardrail_replay_prerequisites"][0]["required_source_evidence_ids"] = []
    packet["guardrail_replay_prerequisites"][0]["required_commands"] = []

    result = validate_inactive_promotion_candidate_packet_v2(packet)

    assert not result.valid
    problems = "; ".join(result.problems)
    assert "required_source_evidence_ids must be a non-empty list" in problems
    assert "required_commands must match" in problems


def test_rejects_missing_reviewer_signoff_placeholder_fields() -> None:
    packet = _packet()
    del packet["reviewer_signoff_placeholders"][0]["reviewer"]

    result = validate_inactive_promotion_candidate_packet_v2(packet)

    assert not result.valid
    assert "reviewer_signoff_placeholders[0].reviewer is required" in "; ".join(result.problems)


def test_rejects_delta_cross_reference_gaps() -> None:
    packet = _packet()
    packet["inactive_devhub_surface_candidate_deltas"] = packet["inactive_devhub_surface_candidate_deltas"][:1]

    result = validate_inactive_promotion_candidate_packet_v2(packet)

    assert not result.valid
    assert "inactive_devhub_surface_candidate_deltas must reference every consumed approved dependency row" in "; ".join(result.problems)


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("browser_state_path", "state.json", "must not include private"),
        ("raw_crawl_output", "raw html", "must not include private"),
        ("downloaded_document_path", "permit.pdf", "must not include private"),
        ("live_note", "live DevHub access completed", "must not claim live execution"),
        ("action_note", "agent may submit permit", "must not include official-action language"),
        ("guarantee_note", "permit will be approved", "must not guarantee"),
    ],
)
def test_rejects_private_artifacts_live_claims_official_action_language_and_guarantees(
    key: str, value: Any, expected: str
) -> None:
    packet = _packet()
    packet[key] = value

    result = validate_inactive_promotion_candidate_packet_v2(packet)

    assert not result.valid
    assert expected in "; ".join(result.problems)


@pytest.mark.parametrize(
    "flag",
    [
        "active_source_mutation",
        "active_source_registry_mutation",
        "active_surface_mutation",
        "active_devhub_surface_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_process_mutation",
    ],
)
def test_rejects_active_mutation_flags(flag: str) -> None:
    packet = _packet()
    packet[flag] = True

    result = validate_inactive_promotion_candidate_packet_v2(packet)

    assert not result.valid
    assert f"packet.{flag} must be false" in "; ".join(result.problems)
