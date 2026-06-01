from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from ppd.devhub.attended_readonly_observation_evidence_intake_packet_v1 import (
    accepted_intake_rows,
    validate_attended_readonly_observation_evidence_intake_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_readonly_observation_evidence_intake_packet_v1.json"


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def finding_codes(packet: dict[str, object]) -> set[str]:
    return {finding.code for finding in validate_attended_readonly_observation_evidence_intake_packet_v1(packet).findings}


def test_valid_fixture_records_required_read_only_evidence_categories() -> None:
    packet = load_fixture()

    result = validate_attended_readonly_observation_evidence_intake_packet_v1(packet)
    rows = accepted_intake_rows(packet)

    assert result.ok, result.messages()
    assert [row["intake_row_id"] for row in rows] == ["intake-home-readonly-001", "intake-permit-detail-readonly-001"]
    for row in rows:
        assert row["classification"] in {"safe_read_only", "read_only_observation"}
        assert row["observed_page_headings"]
        assert row["observed_url_patterns"]
        assert row["accessible_landmarks"]
        assert row["read_only_action_labels"]
        assert row["validation_messages"]
        assert row["attachment_list_metadata_placeholders"]
        assert row["fee_notice_status_placeholders"]
        assert row["stop_condition_hits"]
        assert row["manual_handoff_notes"]
        assert row["offline_validation_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]


def test_rejects_missing_required_intake_evidence_sequences() -> None:
    required = (
        "observed_page_headings",
        "observed_url_patterns",
        "accessible_landmarks",
        "read_only_action_labels",
        "validation_messages",
        "attachment_list_metadata_placeholders",
        "fee_notice_status_placeholders",
        "stop_condition_hits",
        "manual_handoff_notes",
        "offline_validation_commands",
    )
    for key in required:
        packet = load_fixture()
        packet["intake_rows"][0][key] = []
        assert "missing_sequence" in finding_codes(packet) or "missing_offline_validation_commands" in finding_codes(packet)


def test_rejects_non_synthetic_authorization_or_unredacted_placeholder() -> None:
    packet = load_fixture()
    packet["renewal_authorization_rows"][0]["origin"] = "live_authorization_row"
    assert "unsafe_authorization_origin" in finding_codes(packet)

    packet = load_fixture()
    packet["redacted_observation_placeholders"][0]["private_values_redacted"] = False
    assert "placeholder_not_redacted" in finding_codes(packet)


def test_rejects_unknown_references_and_unsafe_classification() -> None:
    packet = load_fixture()
    packet["intake_rows"][0]["authorization_row_id"] = "missing-row"
    packet["intake_rows"][0]["classification"] = "reversible_draft"

    codes = finding_codes(packet)

    assert "unknown_reference" in codes
    assert "unsafe_intake_classification" in codes


def test_rejects_private_artifacts_live_access_consequential_claims_and_mutations() -> None:
    cases = (
        "stored credential token",
        "kept session state",
        "saved screenshot and trace.zip",
        "raw crawl output from authenticated page",
        "opened DevHub and logged into DevHub",
        "filled form then submit",
        "active surface update",
    )
    for text in cases:
        packet = load_fixture()
        packet["operator_note"] = text
        assert "forbidden_text" in finding_codes(packet)

    packet = deepcopy(load_fixture())
    packet["mutation_flags"]["active_guardrail_mutation"] = True
    assert "active_mutation_flag" in finding_codes(packet)


def test_rejects_browser_or_network_validation_commands() -> None:
    packet = load_fixture()
    packet["intake_rows"][0]["offline_validation_commands"] = [["curl", "https://devhub.portlandoregon.gov"]]

    assert "online_or_browser_validation_command" in finding_codes(packet)


def test_rejects_artifact_policy_flags() -> None:
    for flag in load_fixture()["artifact_policy"]:
        packet = load_fixture()
        packet["artifact_policy"][flag] = True
        assert "unsafe_artifact_policy" in finding_codes(packet)
