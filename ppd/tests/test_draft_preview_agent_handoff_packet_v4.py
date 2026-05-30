from __future__ import annotations

from pathlib import Path

import pytest

from ppd.draft_preview_agent_handoff_packet_v4 import (
    PACKET_VERSION,
    REQUIRED_ATTESTATIONS,
    DraftPreviewHandoffPacketV4Error,
    build_packet,
    build_packet_from_paths,
    load_json,
    validate_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "draft_preview_agent_handoff_packet_v4"
READINESS_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_readiness_packet_v4"
PDF_FIELD_MAPPING = FIXTURE_DIR / "pdf_field_mapping_fixtures.json"
GUARDRAIL_BUNDLE = READINESS_FIXTURE_DIR / "guardrail_bundle_fixtures.json"


def test_builds_fixture_first_reversible_draft_preview_handoff_packet_v4() -> None:
    packet = build_packet_from_paths(PDF_FIELD_MAPPING, GUARDRAIL_BUNDLE, READINESS_FIXTURE_DIR)

    assert packet["packet_version"] == PACKET_VERSION
    assert "local-pdf-field-mapping-fixtures-v4-20260530" in packet["source_fixture_ids"]
    assert "guardrail-bundle-fixtures-v1" in packet["source_fixture_ids"]
    assert "agent-readiness-api-schema-expectation-packet-v4" in packet["source_fixture_ids"]
    assert len(packet["fixture_provenance"]) == 2
    assert all(item["sha256"] for item in packet["fixture_provenance"])


def test_field_proposals_are_cited_reversible_draft_only_and_block_missing_facts() -> None:
    packet = build_packet_from_paths(PDF_FIELD_MAPPING, GUARDRAIL_BUNDLE, READINESS_FIXTURE_DIR)

    proposals = packet["field_proposals"]
    assert [proposal["field_id"] for proposal in proposals] == ["permit-address-line"]
    assert all(proposal["draft_only"] is True for proposal in proposals)
    assert all(proposal["writes_pdf"] is False for proposal in proposals)
    assert all(proposal["requires_user_review"] is True for proposal in proposals)
    assert all(proposal["citation_ids"] for proposal in proposals)

    blockers = packet["missing_fact_blockers"]
    assert {blocker["fact_key"] for blocker in blockers} == {"applicant_role"}
    blocker_text = " ".join(blocker["question"].lower() for blocker in blockers)
    assert "applicant role" in blocker_text
    assert all("submission" in blocker["blocks_official_actions"] for blocker in blockers)


def test_user_review_checkpoints_rollback_commands_and_attestations_are_explicit() -> None:
    packet = build_packet_from_paths(PDF_FIELD_MAPPING, GUARDRAIL_BUNDLE, READINESS_FIXTURE_DIR)

    checkpoint_ids = {checkpoint["checkpoint_id"] for checkpoint in packet["user_review_checkpoints"]}
    assert "review-field-proposals-before-use" in checkpoint_ids
    assert "guardrail-official-action-stop" in checkpoint_ids
    assert all(checkpoint["review_required"] is True for checkpoint in packet["user_review_checkpoints"])

    rollback = packet["rollback_notes"]
    assert rollback
    assert "local draft packet only" in rollback[0]["rollback_scope"]
    assert "unchanged" in rollback[0]["summary"]

    assert ["python3", "-m", "py_compile", "ppd/draft_preview_agent_handoff_packet_v4.py"] in packet["offline_validation_commands"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]
    assert packet["attestations"] == {key: True for key in REQUIRED_ATTESTATIONS}


def test_readiness_adapter_outputs_are_consumed_without_private_or_official_artifacts() -> None:
    packet = build_packet_from_paths(PDF_FIELD_MAPPING, GUARDRAIL_BUNDLE, READINESS_FIXTURE_DIR)

    output_kinds = {output["output_id"]: output["example_kind"] for output in packet["readiness_adapter_outputs"]}
    assert output_kinds == {
        "preview": "reversible_draft_preview",
        "missing_facts": "missing_information_prompt",
        "blocked_action": "blocked_action_explanation",
    }

    serialized = repr(packet).lower()
    assert "private-upload" not in serialized
    assert "session_cookie" not in serialized
    assert "auth_state" not in serialized
    assert "payment_details" not in serialized
    assert "no_private_file" in serialized
    assert "no_upload" in serialized
    assert "no_certification" in serialized
    assert "no_submission" in serialized
    assert "no_payment" in serialized
    assert "no_inspection_scheduling" in serialized


def test_validation_rejects_missing_attestation_private_paths_and_live_action_claims() -> None:
    packet = build_packet_from_paths(PDF_FIELD_MAPPING, GUARDRAIL_BUNDLE, READINESS_FIXTURE_DIR)

    broken_attestation = dict(packet)
    broken_attestation["attestations"] = dict(packet["attestations"])
    broken_attestation["attestations"]["no_payment"] = False
    with pytest.raises(DraftPreviewHandoffPacketV4Error, match="no_payment"):
        validate_packet(broken_attestation)

    private_packet = dict(packet)
    private_packet["field_proposals"] = [dict(packet["field_proposals"][0], file_path="/private/devhub.pdf")]
    with pytest.raises(DraftPreviewHandoffPacketV4Error, match="forbidden private/raw field"):
        validate_packet(private_packet)

    live_packet = dict(packet)
    live_packet["user_review_checkpoints"] = [dict(packet["user_review_checkpoints"][0], summary="Submit the official application now.")]
    with pytest.raises(DraftPreviewHandoffPacketV4Error, match="official action language"):
        validate_packet(live_packet)


def test_builder_requires_guardrail_bundle_to_block_official_boundaries() -> None:
    pdf_mapping = load_json(PDF_FIELD_MAPPING)
    guardrails = load_json(GUARDRAIL_BUNDLE)
    readiness_packet = build_packet_from_paths(PDF_FIELD_MAPPING, GUARDRAIL_BUNDLE, READINESS_FIXTURE_DIR)
    readiness_outputs = {
        item["output_id"]: {
            "example_kind": item["example_kind"],
            "ready": item["ready"],
            "citations": item["citation_ids"],
            "safe_next_action_classes": item["safe_next_action_classes"],
        }
        for item in readiness_packet["readiness_adapter_outputs"]
    }
    guardrails["blocked_actions"] = ["upload", "submission"]

    with pytest.raises(DraftPreviewHandoffPacketV4Error, match="guardrail bundle missing blocked actions"):
        build_packet(pdf_mapping, guardrails, readiness_outputs)
