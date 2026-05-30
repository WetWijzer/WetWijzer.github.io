from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from ppd.devhub.observation_evidence_intake_gate_v1 import (
    REQUIRED_REDACTION_ATTESTATIONS,
    accepted_observation_rows,
    validate_observation_evidence_intake_gate_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "observation_evidence_intake_gate_v1.json"


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def finding_codes(packet: dict[str, object]) -> set[str]:
    return {finding.code for finding in validate_observation_evidence_intake_gate_v1(packet).findings}


def test_accepts_fixture_first_safe_read_only_observation_rows() -> None:
    packet = load_fixture()

    result = validate_observation_evidence_intake_gate_v1(packet)
    rows = accepted_observation_rows(packet)

    assert result.ok, result.messages()
    assert [row["surface_id"] for row in rows] == [
        "devhub-home-read-only-synthetic",
        "devhub-permit-status-read-only-redacted",
    ]
    for row in rows:
        assert row["classification"] in {"safe_read_only", "read_only_observation"}
        assert row["metadata_origin"] in {"synthetic_fixture", "redacted_observation_metadata"}
        assert row["blocked_action_notes"]
        assert row["offline_validation_commands"]
        for attestation in REQUIRED_REDACTION_ATTESTATIONS:
            assert row["redaction_attestations"][attestation] is True


def test_rejects_missing_required_gate_fields() -> None:
    packet = load_fixture()
    row = deepcopy(packet["observation_rows"][0])
    for key in (
        "surface_id",
        "classification",
        "source_evidence_refs",
        "redaction_attestations",
        "blocked_action_notes",
        "reviewer_disposition",
        "offline_validation_commands",
    ):
        row.pop(key, None)
    packet["observation_rows"] = [row]

    codes = finding_codes(packet)

    assert "missing_text" in codes
    assert "unsafe_classification" in codes
    assert "missing_evidence_refs" in codes
    assert "missing_redaction_attestations" in codes
    assert "missing_blocked_action_notes" in codes
    assert "missing_reviewer_disposition" in codes
    assert "missing_offline_validation_commands" in codes


def test_rejects_private_browser_capture_and_raw_data_artifacts() -> None:
    packet = load_fixture()
    row = deepcopy(packet["observation_rows"][0])
    row["session_state"] = "redacted-session-state.json"
    row["auth_file_ref"] = "storage-state.json"
    row["raw_crawl_payload"] = "raw crawl data from DevHub"
    row["raw_pdf_bytes"] = "raw pdf bytes"
    row["downloaded_data_ref"] = "downloaded document"
    row["blocked_action_notes"] = ["Contains screenshot artifact path"]
    packet["observation_rows"] = [row]

    codes = finding_codes(packet)

    assert "forbidden_key" in codes
    assert "forbidden_text" in codes


def test_rejects_non_read_only_or_unattested_rows() -> None:
    packet = load_fixture()
    row = deepcopy(packet["observation_rows"][0])
    row["classification"] = "reversible_draft"
    row["metadata_origin"] = "live_authenticated_capture"
    row["redaction_attestations"]["payment_details_absent"] = False
    packet["observation_rows"] = [row]

    codes = finding_codes(packet)

    assert "unsafe_classification" in codes
    assert "unsafe_metadata_origin" in codes
    assert "failed_redaction_attestation" in codes


def test_rejects_live_promoted_outcome_and_active_action_claims() -> None:
    packet = load_fixture()
    row = deepcopy(packet["observation_rows"][0])
    row["notes"] = "Live authenticated execution completed; observation promoted; permit will be approved; submit the application."
    packet["observation_rows"] = [row]

    codes = finding_codes(packet)

    assert "live_or_promoted_claim" in codes
    assert "outcome_guarantee" in codes
    assert "active_consequential_action_language" in codes


def test_rejects_active_mutation_flags() -> None:
    packet = load_fixture()
    packet["active_surface_mutation"] = True
    packet["mutation_note"] = "Apply surface update to the active registry."

    codes = finding_codes(packet)

    assert "active_mutation_flag" in codes


def test_rejects_online_validation_commands() -> None:
    packet = load_fixture()
    packet["observation_rows"][0]["offline_validation_commands"] = [["curl", "https://devhub.portlandoregon.gov"]]

    codes = finding_codes(packet)

    assert "online_validation_command" in codes
