import json
from pathlib import Path

from ppd.authorization.live_readiness_authorization_checklist_v2 import (
    REQUIRED_ATTESTATION_IDS,
    REQUIRED_CONSUMED_PACKET_IDS,
    required_authorization_prerequisite_ids,
    required_signoff_field_ids,
    validate_authorization_checklist_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "live_readiness_authorization_checklist_packet_v2.json"


def _load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_live_readiness_authorization_checklist_packet_v2_is_valid():
    packet = _load_fixture()

    result = validate_authorization_checklist_packet(packet)

    assert result.ok, result.errors


def test_packet_consumes_all_required_upstream_packets():
    packet = _load_fixture()

    consumed_ids = {item["packet_id"] for item in packet["consumes"]}

    assert REQUIRED_CONSUMED_PACKET_IDS.issubset(consumed_ids)


def test_packet_keeps_required_attestations_explicit():
    packet = _load_fixture()

    attestation_ids = {item["id"] for item in packet["attestations"]}

    assert REQUIRED_ATTESTATION_IDS.issubset(attestation_ids)
    assert all(item["status"] == "attested_in_fixture" for item in packet["attestations"])


def test_operator_signoff_fields_are_required_and_blank():
    packet = _load_fixture()

    required_field_ids = required_signoff_field_ids(packet)

    assert required_field_ids == (
        "operator_name",
        "authorization_timestamp_utc",
        "authorized_scope",
        "boundary_acknowledgement",
        "attestation_acknowledgement",
    )
    assert all(item["blank_value"] is None for item in packet["operator_signoff_fields"])


def test_authorization_prerequisites_are_cited_for_reviewer_use():
    packet = _load_fixture()

    prerequisite_ids = required_authorization_prerequisite_ids(packet)

    assert prerequisite_ids == (
        "prereq-source-citations-reviewed",
        "prereq-fixture-gap-closures-reviewed",
        "prereq-live-boundaries-reviewed",
        "prereq-operator-signoff-fields-ready",
    )
    for item in packet["authorization_prerequisites"]:
        assert item["citation_refs"]
        assert item["required_evidence_ids"]
        assert item["reviewer_action"]


def test_offline_validation_commands_do_not_authorize_live_or_auth_work():
    packet = _load_fixture()
    forbidden_tokens = ("crawl", "playwright", "browser", "devhub", "login", "auth")

    for command in packet["offline_validation_commands"]:
        command_text = " ".join(command).lower()
        assert not any(token in command_text for token in forbidden_tokens)
