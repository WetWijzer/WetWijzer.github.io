from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ppd.devhub.surface_map_candidate_v2 import (
    SurfaceMapCandidateError,
    build_surface_map_candidate,
    validate_surface_map_candidate,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_surface_map_candidate_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _valid_candidate() -> dict:
    return build_surface_map_candidate(_load_fixture("redaction_acceptance_packet_v2.json"))


def test_build_surface_map_candidate_matches_expected_fixture() -> None:
    packet = _load_fixture("redaction_acceptance_packet_v2.json")
    expected = _load_fixture("expected_surface_map_candidate_v2.json")

    assert build_surface_map_candidate(packet) == expected


def test_valid_surface_map_candidate_validation_passes() -> None:
    assert validate_surface_map_candidate(_valid_candidate()) == []


def test_candidate_rows_are_ordered_and_inactive() -> None:
    candidate = _valid_candidate()

    assert [row["order"] for row in candidate["candidate_rows"]] == [1, 2, 3, 4, 5, 6]
    assert {row["activation_state"] for row in candidate["candidate_rows"]} == {"inactive_surface_map_candidate"}
    assert {row["commit_safety"] for row in candidate["candidate_rows"]} == {"fixture_only_no_devhub_access"}


def test_candidate_rows_have_placeholder_cross_references() -> None:
    candidate = _valid_candidate()

    selector_ids = {item["placeholder_id"] for item in candidate["selector_stability_placeholders"]}
    role_ids = {item["placeholder_id"] for item in candidate["accessible_role_evidence_placeholders"]}
    message_ids = {item["placeholder_id"] for item in candidate["redacted_validation_message_placeholders"]}
    classification_ids = {item["classification_id"] for item in candidate["action_boundary_classifications"]}
    disposition_ids = {item["placeholder_id"] for item in candidate["reviewer_disposition_placeholders"]}

    for row in candidate["candidate_rows"]:
        assert row["selector_stability_placeholder_id"] in selector_ids
        assert row["accessible_role_evidence_placeholder_id"] in role_ids
        assert row["redacted_validation_message_placeholder_id"] in message_ids
        assert row["action_boundary_classification_id"] in classification_ids
        assert row["reviewer_disposition_placeholder_id"] in disposition_ids


def test_action_boundary_classifications_block_official_actions() -> None:
    candidate = _valid_candidate()
    classifications = {item["row_id"]: item for item in candidate["action_boundary_classifications"]}

    assert classifications["surface-row-005-action-observe_status_labels"]["classification"] == "safe_read_only_observation"
    assert classifications["surface-row-005-action-observe_status_labels"]["official_action_allowed"] is False
    assert classifications["surface-row-006-action-submit_application"]["classification"] == "consequential_official_blocked"
    assert classifications["surface-row-006-action-submit_application"]["requires_exact_confirmation"] is True
    assert classifications["surface-row-006-action-submit_application"]["official_action_allowed"] is False


def test_invalid_source_redaction_packet_is_rejected() -> None:
    packet = _load_fixture("redaction_acceptance_packet_v2.json")
    packet["field_level_decisions"] = []

    with pytest.raises(SurfaceMapCandidateError, match="source redaction packet is invalid"):
        build_surface_map_candidate(packet)


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("candidate_rows", "missing_inactive_surface_map_candidate_rows"),
        ("selector_stability_placeholders", "missing_selector_stability_placeholders"),
        ("accessible_role_evidence_placeholders", "missing_accessible_role_evidence_placeholders"),
        ("redacted_validation_message_placeholders", "missing_redacted_validation_message_placeholders"),
        ("action_boundary_classifications", "missing_action_boundary_classifications"),
        ("reviewer_disposition_placeholders", "missing_reviewer_disposition_placeholders"),
        ("offline_validation_commands", "missing_validation_commands"),
    ],
)
def test_candidate_validation_rejects_missing_required_sections(field: str, code: str) -> None:
    candidate = _valid_candidate()
    candidate[field] = []

    assert code in validate_surface_map_candidate(candidate)


def test_candidate_validation_rejects_non_inactive_rows() -> None:
    candidate = _valid_candidate()
    candidate["candidate_rows"][0] = deepcopy(candidate["candidate_rows"][0])
    candidate["candidate_rows"][0]["activation_state"] = "ready_for_release"

    assert "candidate_row_not_inactive" in validate_surface_map_candidate(candidate)


def test_candidate_validation_rejects_private_session_browser_raw_and_downloaded_artifacts() -> None:
    candidate = _valid_candidate()
    candidate["review_notes"] = "Stored downloaded artifact from browser trace.zip for review."

    assert "private_session_browser_raw_or_downloaded_artifact" in validate_surface_map_candidate(candidate)


def test_candidate_validation_rejects_automated_login_or_mfa_claims() -> None:
    candidate = _valid_candidate()
    candidate["review_notes"] = "The worker automated MFA during the DevHub sign-in."

    assert "automated_login_or_mfa_claim" in validate_surface_map_candidate(candidate)


def test_candidate_validation_rejects_consequential_official_action_enablement() -> None:
    candidate = _valid_candidate()
    candidate["review_notes"] = "The agent may submit the permit application after this packet is accepted."

    assert "consequential_official_action_language" in validate_surface_map_candidate(candidate)


def test_candidate_validation_rejects_legal_or_permitting_guarantees() -> None:
    candidate = _valid_candidate()
    candidate["review_notes"] = "This candidate guarantees issuance and confirms the permit will be approved."

    assert "legal_or_permitting_guarantee" in validate_surface_map_candidate(candidate)


def test_candidate_validation_rejects_active_mutation_flags() -> None:
    candidate = _valid_candidate()
    candidate["mutation_flags"] = {
        "active_devhub_surface_mutation": True,
        "active_guardrail_mutation": False,
    }

    assert (
        "active_devhub_surface_guardrail_source_prompt_contract_or_release_state_mutation_flag"
        in validate_surface_map_candidate(candidate)
    )
