from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ppd.devhub.surface_map_candidate_validation import (
    readonly_surface_map_candidate_v2_is_valid,
    validate_readonly_surface_map_candidate_v2,
    validate_surface_map_candidate,
    validate_surface_map_candidates,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "surface_map_candidate_validation.json"


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _candidate(candidate_id: str) -> dict[str, object]:
    fixture = _fixture()
    candidates = fixture["candidates"]
    assert isinstance(candidates, list)
    for candidate in candidates:
        assert isinstance(candidate, dict)
        if candidate.get("candidate_id") == candidate_id:
            return candidate
    raise AssertionError(f"missing fixture candidate {candidate_id}")


def _v2_packet(packet_id: str) -> dict[str, object]:
    fixture = _fixture()
    packets = fixture["candidate_v2_packets"]
    assert isinstance(packets, list)
    for packet in packets:
        assert isinstance(packet, dict)
        if packet.get("candidate_id") == packet_id:
            return packet
    raise AssertionError(f"missing fixture candidate v2 packet {packet_id}")


def _codes(candidate_id: str) -> set[str]:
    result = validate_surface_map_candidate(_candidate(candidate_id))
    return {violation.code for violation in result.violations}


def _v2_codes(packet: dict[str, object]) -> set[str]:
    result = validate_readonly_surface_map_candidate_v2(packet)
    return {violation.code for violation in result.violations}


def test_clear_candidate_allows_reversible_draft_actions() -> None:
    result = validate_surface_map_candidate(_candidate("valid_residential_draft_surface"))

    assert result.reversible_draft_allowed is True
    assert result.violations == ()


def test_low_confidence_or_missing_route_and_heading_blocks_reversible_drafts() -> None:
    assert _codes("low_confidence_missing_context") == {
        "low_selector_confidence",
        "missing_route_evidence",
        "missing_heading_evidence",
    }


def test_ambiguous_required_labels_block_reversible_drafts() -> None:
    result = validate_surface_map_candidate(_candidate("ambiguous_required_labels"))

    assert result.reversible_draft_allowed is False
    messages = [violation.message for violation in result.violations]
    assert "required field 'owner_name' must have exactly one non-empty label" in messages
    assert "required label 'project contact' is shared by fields: applicant_name, contractor_name" in messages


def test_consequential_controls_cannot_be_classified_reversible() -> None:
    result = validate_surface_map_candidate(_candidate("consequential_controls_mislabeled_reversible"))

    assert result.reversible_draft_allowed is False
    assert {violation.code for violation in result.violations} == {"consequential_control_marked_reversible"}
    messages = [violation.message for violation in result.violations]
    assert "actions item 'submit_application' must not be classified as reversible" in messages
    assert "actions item 'pay_fee' must not be classified as reversible" in messages
    assert "upload_controls item 'upload_plans' must not be classified as reversible" in messages


def test_batch_validation_fails_closed_when_any_candidate_is_unsafe() -> None:
    fixture = _fixture()
    candidates = fixture["candidates"]
    assert isinstance(candidates, list)

    result = validate_surface_map_candidates(candidates)

    assert result.reversible_draft_allowed is False
    assert len(result.results) == 4
    assert result.results[0].reversible_draft_allowed is True
    assert all(item.candidate_id for item in result.results)


def test_readonly_surface_map_candidate_v2_accepts_complete_redacted_packet() -> None:
    packet = _v2_packet("valid_readonly_surface_map_candidate_v2")

    result = validate_readonly_surface_map_candidate_v2(packet)

    assert result.violations == ()
    assert readonly_surface_map_candidate_v2_is_valid(packet) is True


def test_readonly_surface_map_candidate_v2_rejects_missing_rows_placeholders_review_and_commands() -> None:
    packet = _v2_packet("valid_readonly_surface_map_candidate_v2")
    packet.pop("candidate_rows")
    packet.pop("validation_commands")

    codes = _v2_codes(packet)

    assert "missing_candidate_rows" in codes
    assert "missing_validation_commands" in codes

    incomplete = _v2_packet("valid_readonly_surface_map_candidate_v2")
    row = incomplete["candidate_rows"][0]
    assert isinstance(row, dict)
    for key in (
        "selector_stability_placeholder",
        "accessible_role_evidence_placeholder",
        "redacted_validation_message_placeholder",
        "action_boundary_classification",
        "reviewer_disposition",
    ):
        row.pop(key)

    codes = _v2_codes(incomplete)

    assert "missing_selector_stability_placeholder" in codes
    assert "missing_accessible_role_evidence_placeholder" in codes
    assert "missing_redacted_validation_message_placeholder" in codes
    assert "missing_action_boundary_classification" in codes
    assert "missing_reviewer_disposition" in codes


def test_readonly_surface_map_candidate_v2_rejects_private_artifacts_auth_automation_actions_and_guarantees() -> None:
    packet = _v2_packet("unsafe_readonly_surface_map_candidate_v2")

    codes = _v2_codes(packet)

    assert "private_session_or_auth_value" in codes
    assert "prohibited_artifact_reference" in codes
    assert "automated_login_or_mfa_claim" in codes
    assert "consequential_official_action_language" in codes
    assert "legal_or_permitting_guarantee" in codes


def test_readonly_surface_map_candidate_v2_rejects_active_mutation_flags() -> None:
    mutation_flags = (
        "active_devhub_surface_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_contract_mutation",
        "active_source_mutation",
        "active_release_state_mutation",
    )

    for flag in mutation_flags:
        packet = deepcopy(_v2_packet("valid_readonly_surface_map_candidate_v2"))
        packet[flag] = True

        codes = _v2_codes(packet)

        assert "active_mutation_flag" in codes
