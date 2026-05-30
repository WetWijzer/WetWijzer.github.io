from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ppd.devhub.observation_redaction_acceptance_packet_v2 import (
    ObservationPacketError,
    build_acceptance_packet,
    validate_acceptance_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_observation_redaction_acceptance_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _valid_packet() -> dict:
    return build_acceptance_packet(_load_fixture("attended_read_only_observation_plan_v2.json"))


def test_build_acceptance_packet_matches_expected_fixture() -> None:
    plan = _load_fixture("attended_read_only_observation_plan_v2.json")
    expected = _load_fixture("expected_acceptance_packet_v2.json")

    assert build_acceptance_packet(plan) == expected


def test_valid_acceptance_packet_validation_passes() -> None:
    assert validate_acceptance_packet(_valid_packet()) == []


def test_private_value_fields_are_drop_decisions() -> None:
    packet = _valid_packet()

    decisions = {item["field_id"]: item for item in packet["field_level_decisions"]}

    assert decisions["permit_number_value"]["decision"] == "drop"
    assert decisions["permit_number_value"]["stored_representation"] == "label_and_class_only"
    assert decisions["site_address_value"]["decision"] == "drop"
    assert decisions["page_heading"]["decision"] == "keep"


def test_consequential_actions_are_blocked_even_in_synthetic_plans() -> None:
    packet = _valid_packet()

    confirmations = {item["action_id"]: item for item in packet["action_boundary_confirmations"]}

    assert confirmations["observe_status_labels"]["read_only_confirmed"] is True
    assert confirmations["observe_status_labels"]["consequential_action_blocked"] is False
    assert confirmations["submit_application"]["read_only_confirmed"] is False
    assert confirmations["submit_application"]["consequential_action_blocked"] is True


def test_prohibited_private_artifact_keys_are_rejected() -> None:
    plan = _load_fixture("attended_read_only_observation_plan_v2.json")
    plan["screenshots"] = ["not-allowed.png"]

    with pytest.raises(ObservationPacketError, match="prohibited private artifact key"):
        build_acceptance_packet(plan)


def test_non_synthetic_observation_plan_is_rejected() -> None:
    plan = _load_fixture("attended_read_only_observation_plan_v2.json")
    plan["synthetic_fixture_only"] = False

    with pytest.raises(ObservationPacketError, match="synthetic_fixture_only"):
        build_acceptance_packet(plan)


def test_live_value_kind_is_rejected() -> None:
    plan = _load_fixture("attended_read_only_observation_plan_v2.json")
    plan["observations"][0]["value_kind"] = "live"

    with pytest.raises(ObservationPacketError, match="synthetic value_kind"):
        build_acceptance_packet(plan)


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("reviewer_redaction_checks", "missing_reviewer_redaction_checks"),
        ("field_level_decisions", "missing_field_level_keep_drop_decisions"),
        ("private_value_exclusion_attestations", "missing_private_value_exclusion_attestations"),
        ("action_boundary_confirmations", "missing_action_boundary_confirmations"),
        ("unresolved_risk_notes", "missing_unresolved_risk_notes"),
        ("offline_validation_commands", "missing_validation_commands"),
    ],
)
def test_acceptance_packet_validation_rejects_missing_required_sections(field: str, code: str) -> None:
    packet = _valid_packet()
    packet[field] = []

    assert code in validate_acceptance_packet(packet)


def test_acceptance_packet_validation_rejects_missing_field_keep_drop_decision() -> None:
    packet = _valid_packet()
    packet["field_level_decisions"][0] = deepcopy(packet["field_level_decisions"][0])
    packet["field_level_decisions"][0].pop("decision")

    assert "missing_field_level_keep_drop_decisions" in validate_acceptance_packet(packet)


def test_acceptance_packet_validation_rejects_missing_action_boundary_booleans() -> None:
    packet = _valid_packet()
    packet["action_boundary_confirmations"][0] = deepcopy(packet["action_boundary_confirmations"][0])
    packet["action_boundary_confirmations"][0].pop("read_only_confirmed")

    assert "missing_action_boundary_confirmations" in validate_acceptance_packet(packet)


def test_acceptance_packet_validation_rejects_private_session_browser_raw_and_downloaded_artifacts() -> None:
    packet = _valid_packet()
    packet["review_notes"] = "Stored downloaded artifact from browser trace.zip for review."

    assert "private_session_browser_raw_or_downloaded_artifact" in validate_acceptance_packet(packet)


def test_acceptance_packet_validation_rejects_automated_login_or_mfa_claims() -> None:
    packet = _valid_packet()
    packet["review_notes"] = "The worker automated MFA during the DevHub sign-in."

    assert "automated_login_or_mfa_claim" in validate_acceptance_packet(packet)


def test_acceptance_packet_validation_rejects_consequential_official_action_enablement() -> None:
    packet = _valid_packet()
    packet["review_notes"] = "The agent may submit the permit application after this packet is accepted."

    assert "consequential_official_action_language" in validate_acceptance_packet(packet)


def test_acceptance_packet_validation_rejects_legal_or_permitting_guarantees() -> None:
    packet = _valid_packet()
    packet["review_notes"] = "This packet guarantees issuance and confirms the permit will be approved."

    assert "legal_or_permitting_guarantee" in validate_acceptance_packet(packet)


def test_acceptance_packet_validation_rejects_active_mutation_flags() -> None:
    packet = _valid_packet()
    packet["mutation_flags"] = {
        "active_devhub_surface_mutation": True,
        "active_guardrail_mutation": False,
    }

    assert (
        "active_devhub_surface_guardrail_source_prompt_contract_or_release_state_mutation_flag"
        in validate_acceptance_packet(packet)
    )
