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


def test_packet_rejects_uncited_observed_surfaces():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["citations"] = []

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("observed_surfaces[0].citations must be non-empty" in error for error in errors)


def test_packet_rejects_consequential_allowed_action():
    packet = _fixture_data()
    action = copy.deepcopy(packet["allowed_read_only_actions"][0])
    action["action_id"] = "submit_application"
    action["label"] = "Submit application"
    packet["allowed_read_only_actions"].append(action)

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not describe consequential DevHub action" in error for error in errors)


def test_packet_rejects_consequential_action_language_outside_handoff():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["redacted_state_summary"] = "Operator clicked submit and completed permit submission."

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not contain consequential DevHub action language" in error for error in errors)


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


def test_packet_rejects_screenshot_trace_har_references():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["evidence_artifact"] = "review the Playwright trace and HAR file"

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not reference screenshots, traces, HAR" in error for error in errors)


def test_packet_rejects_legal_or_permitting_outcome_guarantees():
    packet = _fixture_data()
    packet["observed_surfaces"][0]["redacted_state_summary"] = "This observation guarantees approval and legal compliance."

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("must not guarantee legal compliance or permitting outcomes" in error for error in errors)


def test_packet_rejects_active_mutation_flags():
    packet = _fixture_data()
    packet["active_surface_registry_mutation"] = True
    packet["prompt_mutation"] = True
    packet["monitoring_mutation"] = True
    packet["release_state_mutation"] = True
    packet["agent_state_mutation"] = True
    packet["guardrail_mutation"] = True

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("active_surface_registry_mutation" in error for error in errors)
    assert any("prompt_mutation" in error for error in errors)
    assert any("monitoring_mutation" in error for error in errors)
    assert any("release_state_mutation" in error for error in errors)
    assert any("agent_state_mutation" in error for error in errors)
    assert any("guardrail_mutation" in error for error in errors)


def test_packet_requires_no_live_and_no_artifact_attestations():
    packet = _fixture_data()
    packet["safety_attestations"]["no_har"] = False
    packet["safety_attestations"].pop("no_surface_registry_mutation")

    errors = validate_attended_read_only_observation_packet_v2(packet)

    assert any("safety_attestations.no_har must be true" in error for error in errors)
    assert any("safety_attestations.no_surface_registry_mutation must be true" in error for error in errors)
