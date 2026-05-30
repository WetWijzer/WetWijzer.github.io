from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.reversible_draft_preview_offline_smoke_transcript_v2 import (
    REQUIRED_ATTESTATIONS,
    REQUIRED_OUTPUT_IDS,
    assert_valid_reversible_draft_preview_offline_smoke_transcript_v2,
    build_from_fixture_path,
    validate_reversible_draft_preview_offline_smoke_transcript_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "reversible_draft_preview_offline_smoke_transcript_v2"
SOURCE_PACKETS = FIXTURE_DIR / "source_packets.json"
EXPECTED_PACKET = FIXTURE_DIR / "expected_packet.json"


def test_builds_required_cited_expected_agent_outputs() -> None:
    packet = build_from_fixture_path(SOURCE_PACKETS)
    expected = json.loads(EXPECTED_PACKET.read_text(encoding="utf-8"))

    assert packet["packet_type"] == expected["packet_type"]
    assert packet["packet_id"] == expected["packet_id"]
    assert packet["mode"] == expected["mode"]
    assert [output["output_id"] for output in packet["expected_agent_outputs"]] == list(REQUIRED_OUTPUT_IDS)
    assert [output["output_id"] for output in packet["expected_agent_outputs"]] == expected["required_output_ids"]
    assert all(output["citations"] for output in packet["expected_agent_outputs"])
    assert all(output["source_packet_roles"] for output in packet["expected_agent_outputs"])


def test_preview_missing_refusal_and_exact_confirmation_wording_are_present() -> None:
    packet = build_from_fixture_path(SOURCE_PACKETS)
    outputs = {output["output_id"]: output for output in packet["expected_agent_outputs"]}

    assert "permit-address" in outputs["preview_availability"]["expected_agent_output"]
    assert "work-description" in outputs["preview_availability"]["expected_agent_output"]
    assert "not a PDF write" in outputs["preview_availability"]["expected_agent_output"]
    assert "Fee estimate source" in outputs["missing_information_followups"]["expected_agent_output"]
    assert "Do not request credentials" in outputs["missing_information_followups"]["expected_agent_output"]
    assert "Refuse consequential PP&D actions" in outputs["refusal_of_consequential_actions"]["expected_agent_output"]
    assert "must not submit, certify, upload, pay, schedule, cancel" in outputs["refusal_of_consequential_actions"]["expected_agent_output"]
    assert "type exactly" in outputs["exact_confirmation_wording"]["expected_agent_output"]
    assert "target permit or application" in outputs["exact_confirmation_wording"]["expected_agent_output"]


def test_includes_offline_validation_commands_and_side_effect_attestations() -> None:
    packet = build_from_fixture_path(SOURCE_PACKETS)
    commands = packet["offline_validation_commands"]

    assert ["python3", "-m", "py_compile", "ppd/reversible_draft_preview_offline_smoke_transcript_v2.py"] in commands
    assert ["python3", "-m", "pytest", "ppd/tests/test_reversible_draft_preview_offline_smoke_transcript_v2.py"] in commands
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in commands
    assert ["python3", "-m", "py_compile", "ppd/local_draft_preview_review_packet_v2.py"] in commands
    assert packet["attestations"] == {key: True for key in REQUIRED_ATTESTATIONS}

    attestation_output = next(output for output in packet["expected_agent_outputs"] if output["output_id"] == "side_effect_attestations")
    assert "no live LLM" in attestation_output["expected_agent_output"]
    assert "no DevHub" in attestation_output["expected_agent_output"]
    assert "no private document" in attestation_output["expected_agent_output"]
    assert "no PDF write" in attestation_output["expected_agent_output"]
    assert "no prompt" in attestation_output["expected_agent_output"]
    assert "no agent state mutation" in attestation_output["expected_agent_output"]


def test_validation_rejects_missing_citations_attestations_and_private_artifacts() -> None:
    packet = build_from_fixture_path(SOURCE_PACKETS)
    broken = copy.deepcopy(packet)
    broken["expected_agent_outputs"][0]["citations"] = []
    broken["attestations"]["no_pdf_write"] = False
    broken["private_artifact"] = "auth_state"

    errors = validate_reversible_draft_preview_offline_smoke_transcript_v2(broken)

    assert "expected_agent_outputs[0].citations_required" in errors
    assert "attestations.no_pdf_write_must_be_true" in errors
    assert any("must not reference private paths or browser artifacts" in error for error in errors)


def test_assert_valid_raises_for_live_or_mutating_flags() -> None:
    packet = build_from_fixture_path(SOURCE_PACKETS)
    packet["devhub_execution_enabled"] = True

    with pytest.raises(ValueError, match="must not enable live execution"):
        assert_valid_reversible_draft_preview_offline_smoke_transcript_v2(packet)
