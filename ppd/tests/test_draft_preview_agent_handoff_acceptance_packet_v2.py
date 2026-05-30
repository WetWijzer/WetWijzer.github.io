from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.acceptance.draft_preview_agent_handoff_acceptance_packet_v2 import (
    REQUIRED_ATTESTATIONS,
    AcceptancePacketError,
    build_acceptance_packet,
    build_from_fixture_paths,
    load_json,
    validate_acceptance_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
ACCEPTANCE_FIXTURES = FIXTURE_DIR / "draft_preview_agent_handoff_acceptance_packet_v2"
HANDOFF_PACKET = ACCEPTANCE_FIXTURES / "draft_preview_agent_handoff_packet_v2.json"
SOURCE_FIXTURES = FIXTURE_DIR / "draft_preview_agent_handoff_packet_v2"
SMOKE_TRANSCRIPT = SOURCE_FIXTURES / "reversible_draft_preview_offline_smoke_transcript_v2.json"
PROMPT_RELEASE_HANDOFF = SOURCE_FIXTURES / "prompt_refresh_release_handoff_fixtures.json"


def _source_packets() -> tuple[dict, dict, dict]:
    return load_json(HANDOFF_PACKET), load_json(SMOKE_TRANSCRIPT), load_json(PROMPT_RELEASE_HANDOFF)


def _valid_packet() -> dict:
    return build_from_fixture_paths(HANDOFF_PACKET, SMOKE_TRANSCRIPT, PROMPT_RELEASE_HANDOFF)


def test_builds_cited_accepted_deferred_and_rejected_decisions() -> None:
    packet = _valid_packet()

    decisions = packet["consumer_handoff_decisions"]
    assert {"accepted", "deferred", "rejected"} == set(decisions)
    assert decisions["accepted"]
    assert decisions["deferred"]
    assert decisions["rejected"]

    for group_name, group in decisions.items():
        assert all(item["decision"] == group_name for item in group)
        assert all(item["citations"] for item in group)
        assert all(item["consumer_handoff_decision"] for item in group)
        assert all(item["rationale"] for item in group)

    accepted_refs = {item["handoff_ref"] for item in decisions["accepted"]}
    assert "preview-is-not-submission" in accepted_refs
    assert "local-pdf-preview-only" in accepted_refs

    deferred_refs = {item["handoff_ref"] for item in decisions["deferred"]}
    assert {"submit_application", "upload_document", "pay_fee", "schedule_or_cancel_inspection"}.issubset(deferred_refs)

    rejected_refs = {item["handoff_ref"] for item in decisions["rejected"]}
    assert {"submit_application", "upload_document", "pay_fee"}.issubset(rejected_refs)


def test_migration_checklist_rollback_commands_and_attestations() -> None:
    packet = _valid_packet()

    checklist = {item["checklist_item_id"]: item for item in packet["migration_checklist_items"]}
    assert checklist["migrate-accepted-draft-preview-consumer-notes"]["status"] == "ready_for_fixture_consumer_migration"
    assert checklist["defer-exact-confirmation-live-action-reminders"]["status"] == "deferred_until_attended_confirmation_review"
    assert checklist["reject-consequential-action-execution-migration"]["status"] == "blocked_from_consumer_migration"
    assert all(item["summary"] for item in checklist.values())
    assert all(item["decision_refs"] for item in checklist.values())

    rollback = packet["rollback_owner_fields"]
    assert rollback["owner"] == "PP&D draft preview fixture maintainer"
    assert "no DevHub or release state rollback" in rollback["rollback_scope"]
    assert rollback["rollback_trigger"]
    assert rollback["rollback_validation"]

    commands = packet["offline_validation_commands"]
    assert ["python3", "-m", "py_compile", "ppd/acceptance/draft_preview_agent_handoff_acceptance_packet_v2.py"] in commands
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in commands

    assert packet["attestations"] == {key: True for key in REQUIRED_ATTESTATIONS}
    validate_acceptance_packet(packet)


def test_rejects_uncited_acceptance_decision() -> None:
    packet = _valid_packet()
    packet["consumer_handoff_decisions"]["accepted"][0]["citations"] = []

    with pytest.raises(AcceptancePacketError, match="citations required"):
        validate_acceptance_packet(packet)


def test_rejects_missing_decision_rationale_for_each_bucket() -> None:
    for bucket in ("accepted", "deferred", "rejected"):
        packet = _valid_packet()
        packet["consumer_handoff_decisions"][bucket][0]["rationale"] = ""

        with pytest.raises(AcceptancePacketError, match="rationale required"):
            validate_acceptance_packet(packet)


def test_rejects_missing_migration_or_rollback_fields() -> None:
    packet = _valid_packet()
    del packet["migration_checklist_items"][0]["summary"]

    with pytest.raises(AcceptancePacketError, match="migration_checklist_items\[0\].summary required"):
        validate_acceptance_packet(packet)

    packet = _valid_packet()
    del packet["rollback_owner_fields"]["rollback_validation"]

    with pytest.raises(AcceptancePacketError, match="rollback_owner_fields.rollback_validation required"):
        validate_acceptance_packet(packet)


def test_rejects_private_authenticated_facts_raw_pdf_and_authenticated_values() -> None:
    unsafe_cases = [
        ("private_fact", "owner phone number"),
        ("authenticated_value", "AUTHENTICATED_VALUE: permit dashboard balance"),
        ("raw_pdf", "RAW_PDF_BYTES: JVBERi0x"),
        ("browser_artifact", "trace.zip"),
        ("body", "/home/example/private-plan.pdf"),
    ]
    for key, value in unsafe_cases:
        packet = _valid_packet()
        packet["consumer_handoff_decisions"]["accepted"][0][key] = value

        with pytest.raises(AcceptancePacketError):
            validate_acceptance_packet(packet)


def test_rejects_live_execution_claims_from_inputs_and_packets() -> None:
    handoff, smoke, prompt = _source_packets()
    smoke["live_llm_executed"] = True

    with pytest.raises(AcceptancePacketError, match="live_llm_executed"):
        build_acceptance_packet(handoff, smoke, prompt)

    packet = _valid_packet()
    packet["consumer_handoff_decisions"]["accepted"][0]["body"] = "The crawler ran and processed live PDF files for this handoff."

    with pytest.raises(AcceptancePacketError, match="live LLM, DevHub, browser, PDF, crawler, or processor execution"):
        validate_acceptance_packet(packet)


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    packet = _valid_packet()
    packet["consumer_handoff_decisions"]["accepted"][0]["body"] = "The permit will be approved after this preview."

    with pytest.raises(AcceptancePacketError, match="guarantee legal or permitting outcomes"):
        validate_acceptance_packet(packet)


def test_rejects_final_submission_payment_upload_scheduling_or_cancellation_language() -> None:
    examples = [
        "I submitted the application in DevHub.",
        "Payment completed for the permit fee.",
        "Click upload to add the document to the official record.",
        "Inspection scheduled for tomorrow.",
        "The cancellation completed in DevHub.",
    ]
    for text in examples:
        packet = _valid_packet()
        packet["consumer_handoff_decisions"]["accepted"][0]["body"] = text

        with pytest.raises(AcceptancePacketError, match="final submission, payment, upload, scheduling, or cancellation language"):
            validate_acceptance_packet(packet)


def test_rejects_active_mutation_flags() -> None:
    mutation_flags = [
        "prompt_mutation_enabled",
        "guardrail_update_active",
        "pdf_write_enabled",
        "gap_analysis_mutation_enabled",
        "monitoring_update_active",
        "release_state_mutated",
        "agent_state_mutation_enabled",
    ]
    for flag in mutation_flags:
        packet = _valid_packet()
        packet[flag] = True

        with pytest.raises(AcceptancePacketError, match="must not enable prompt, guardrail, PDF, gap-analysis, monitoring, release-state, or agent-state mutation"):
            validate_acceptance_packet(packet)


def test_required_no_side_effect_attestations_remain_allowed() -> None:
    packet = _valid_packet()
    packet["attestations"] = {key: True for key in REQUIRED_ATTESTATIONS}

    validate_acceptance_packet(packet)
