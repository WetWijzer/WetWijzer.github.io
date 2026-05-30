import copy
from pathlib import Path

from ppd.devhub.attended_read_only_observation_packet_v2 import (
    assert_valid_attended_read_only_observation_packet_v2,
    load_json_packet,
    validate_attended_read_only_observation_packet_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_read_only_observation_packet_v2.json"


def _fixture_data():
    return load_json_packet(FIXTURE_PATH)


def test_devhub_attended_read_only_observation_packet_v2_fixture_is_valid():
    packet = _fixture_data()

    assert validate_attended_read_only_observation_packet_v2(packet) == ()
    assert_valid_attended_read_only_observation_packet_v2(packet)


def test_packet_requires_all_source_packets_to_be_consumed():
    packet = _fixture_data()
    packet["source_packets"]["devhub_attended_read_only_pilot_runbook"]["consumed"] = False

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("source_packets.devhub_attended_read_only_pilot_runbook.consumed" in error for error in errors)


def test_packet_rejects_missing_observed_surface_rows_and_allowed_fields():
    packet = _fixture_data()
    packet["observed_surfaces"] = []

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("observed_surfaces must be non-empty" in error for error in errors)

    packet = _fixture_data()
    packet["observed_surfaces"][0].pop("allowed_observation_fields")

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("observed_surfaces[0].allowed_observation_fields must be non-empty" in error for error in errors)


def test_packet_rejects_unsupported_observation_fields():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["allowed_observation_fields"].append("raw_authenticated_dom")

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("unsupported fields" in error for error in errors)


def test_packet_rejects_uncited_observed_surfaces():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["citations"] = []

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("observed_surfaces[0].citations must be non-empty" in error for error in errors)


def test_packet_rejects_missing_manual_login_handoff_reminders():
    packet = _fixture_data()
    packet["manual_login_handoff_reminders"] = []

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("manual_login_handoff_reminders must be non-empty" in error for error in errors)


def test_packet_rejects_consequential_allowed_action():
    packet = _fixture_data()
    action = copy.deepcopy(packet["allowed_read_only_actions"][0])
    action["action_id"] = "submit_application"
    action["label"] = "Submit application"
    packet["allowed_read_only_actions"].append(action)

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not describe consequential DevHub action" in error for error in errors)


def test_packet_rejects_consequential_official_action_language_outside_handoff():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["redacted_state_summary"] = "Operator clicked submit and completed official permit submission."

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not contain consequential official DevHub action language" in error for error in errors)


def test_packet_rejects_private_artifact_keys_and_live_execution_claims():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["storage_state"] = "redacted"
    packet["observed_surfaces"][0]["redacted_state_summary"] = "Playwright launched a live browser and captured a screenshot."

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("private DevHub artifact keys" in error for error in errors)
    assert any("must not claim live DevHub or browser execution" in error for error in errors)


def test_packet_rejects_private_authenticated_values():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["permit_number"] = "24-123456-000-00-CO"
    packet["observed_surfaces"][0]["review_note"] = "Contact owner@example.test for this permit."

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not contain private or authenticated values" in error for error in errors)


def test_packet_rejects_session_browser_raw_and_downloaded_artifacts():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["downloaded_documents"] = ["private.pdf"]
    packet["observed_surfaces"][0]["browser_artifact"] = "trace.zip"
    packet["observed_surfaces"][0]["raw_crawl_output"] = "raw private page text"

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("downloaded_documents" in error for error in errors)
    assert any("browser_artifact" in error for error in errors)
    assert any("raw_crawl_output" in error for error in errors)


def test_packet_rejects_screenshot_trace_har_references():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["evidence_artifact"] = "review the Playwright trace and HAR file"

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not reference screenshots, traces, HAR" in error for error in errors)


def test_packet_rejects_automated_login_or_mfa_claims():
    packet = _fixture_data()
    packet["manual_login_handoff_reminders"][0]["operator_note"] = "Playwright signed in and handled MFA automatically."

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not claim automated login, MFA" in error for error in errors)


def test_packet_rejects_legal_or_permitting_outcome_guarantees():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["redacted_state_summary"] = "This observation guarantees approval and legal compliance."

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not guarantee legal compliance or permitting outcomes" in error for error in errors)


def test_packet_rejects_active_mutation_flags():
    packet = _fixture_data()
    packet["active_devhub_surface_mutation"] = True
    packet["active_guardrail_mutation"] = True
    packet["active_source_mutation"] = True
    packet["active_prompt_mutation"] = True
    packet["active_contract_mutation"] = True
    packet["active_release_state_mutation"] = True

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("active_devhub_surface_mutation" in error for error in errors)
    assert any("active_guardrail_mutation" in error for error in errors)
    assert any("active_source_mutation" in error for error in errors)
    assert any("active_prompt_mutation" in error for error in errors)
    assert any("active_contract_mutation" in error for error in errors)
    assert any("active_release_state_mutation" in error for error in errors)


def test_packet_requires_forbidden_browser_artifact_attestations():
    packet = _fixture_data()
    packet["forbidden_browser_artifact_attestations"] = [
        row for row in packet["forbidden_browser_artifact_attestations"] if row["attestation_id"] != "no_har"
    ]

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("forbidden_browser_artifact_attestations.no_har must be attested absent" in error for error in errors)


def test_packet_requires_redaction_review_placeholders():
    packet = _fixture_data()
    packet["redaction_review_placeholders"] = []

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("redaction_review_placeholders must be non-empty" in error for error in errors)


def test_packet_requires_timeout_or_manual_handoff_notes():
    packet = _fixture_data()
    packet["timeout_and_manual_handoff_notes"] = []

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("timeout_and_manual_handoff_notes must be non-empty" in error for error in errors)


def test_packet_requires_validation_commands():
    packet = _fixture_data()
    packet["offline_validation_commands"] = []

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("offline_validation_commands must be non-empty" in error for error in errors)
    assert any("offline_validation_commands must include validation commands" in error for error in errors)


def test_packet_requires_no_live_and_no_artifact_attestations():
    packet = _fixture_data()
    packet["safety_attestations"]["no_har"] = False
    packet["safety_attestations"].pop("no_surface_registry_mutation")

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("safety_attestations.no_har must be true" in error for error in errors)
    assert any("safety_attestations.no_surface_registry_mutation must be true" in error for error in errors)
