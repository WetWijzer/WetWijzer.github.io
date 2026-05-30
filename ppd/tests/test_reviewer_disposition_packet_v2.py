from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.reviewer_disposition_packet_v2 import (
    build_packet_from_paths,
    validate_reviewer_disposition_packet_v2,
)

FIXTURES = Path(__file__).parent / "fixtures" / "reviewer_disposition_packet_v2"


def _packet() -> dict:
    return build_packet_from_paths(
        FIXTURES / "inactive_promotion_patch_preview_v1.json",
        FIXTURES / "promotion_readiness_checklist_v2.json",
        FIXTURES / "offline_acceptance_rehearsal_evidence.json",
    )


def test_reviewer_disposition_packet_v2_contains_cited_rows_and_blockers() -> None:
    packet = _packet()

    rows = {row["artifact_id"]: row for row in packet["disposition_rows"]}
    assert rows["inactive-preview-alpha"]["disposition"] == "approve"
    assert rows["inactive-preview-beta"]["disposition"] == "block"
    assert rows["inactive-preview-gamma"]["disposition"] == "defer"
    assert all(row["citations"] for row in rows.values())

    blockers = packet["unresolved_blocker_inventory"]
    assert {blocker["blocker_id"] for blocker in blockers} == {
        "block-beta-missing-citation",
        "rehearsal-beta-failed",
    }
    assert packet["reviewer_owner_assignments"] == {
        "ppd-reviewer-a": ["inactive-preview-alpha"],
        "ppd-reviewer-b": ["inactive-preview-beta"],
        "ppd-reviewer-c": ["inactive-preview-gamma"],
    }
    assert validate_reviewer_disposition_packet_v2(packet).ok


def test_reviewer_disposition_packet_v2_includes_commands_rollbacks_and_attestations() -> None:
    packet = _packet()

    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["exact_validation_commands"]
    assert ["python3", "-m", "pytest", "ppd/tests/test_reviewer_disposition_packet_v2.py"] in packet["exact_validation_commands"]
    assert len(packet["rollback_checkpoints"]) == 3
    assert all(checkpoint["checkpoint"] for checkpoint in packet["rollback_checkpoints"])

    attestations = packet["attestations"]
    assert attestations["no_live_crawl"]["attested"] is True
    assert attestations["no_devhub_session"]["attested"] is True
    assert attestations["no_private_artifact"]["attested"] is True
    assert attestations["no_official_action"]["attested"] is True


def test_rejects_uncited_disposition_rows_and_missing_required_status_classes() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["disposition_rows"][0]["citations"] = []
    broken["disposition_rows"] = [row for row in broken["disposition_rows"] if row["disposition"] != "defer"]
    broken["disposition_rows"][0]["disposition"] = "pending"

    result = validate_reviewer_disposition_packet_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "disposition_rows[0].citations must be non-empty" in joined
    assert "disposition_rows[0].disposition must be approve, block, or defer" in joined
    assert "disposition_rows must include approve, block, and defer dispositions" in joined


def test_rejects_missing_blocker_inventory_owner_assignments_commands_and_rollbacks() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["unresolved_blocker_inventory"] = []
    broken["reviewer_owner_assignments"] = {}
    broken["exact_validation_commands"] = []
    broken["rollback_checkpoints"] = []

    result = validate_reviewer_disposition_packet_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "unresolved_blocker_inventory must be non-empty" in joined
    assert "reviewer_owner_assignments must be non-empty" in joined
    assert "exact_validation_commands must be a non-empty list of command lists" in joined
    assert "rollback_checkpoints must be non-empty" in joined


def test_rejects_disposition_rows_missing_reviewer_owner_assignment() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["reviewer_owner_assignments"]["ppd-reviewer-a"] = ["other-artifact"]

    result = validate_reviewer_disposition_packet_v2(broken)

    assert not result.ok
    assert "disposition_rows[0] must be represented in reviewer_owner_assignments" in "; ".join(result.errors)


def test_rejects_missing_blocker_fields_and_rollback_coverage() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["unresolved_blocker_inventory"][0]["citation"] = ""
    broken["rollback_checkpoints"] = broken["rollback_checkpoints"][:-1]

    result = validate_reviewer_disposition_packet_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "unresolved_blocker_inventory[0].citation must be present" in joined
    assert "rollback_checkpoints must cover disposition artifact inactive-preview-gamma" in joined


def test_rejects_private_authenticated_session_browser_raw_downloaded_and_pdf_artifacts() -> None:
    unsafe_cases = [
        ("auth_state", "state.json"),
        ("authenticated_fact", "private account value"),
        ("browser_artifact", "trace.zip"),
        ("browser_state", "state"),
        ("devhub_session", "session"),
        ("downloaded_document", "form.pdf"),
        ("downloaded_pdf", "permit.pdf"),
        ("pdf_artifact", "public-form.pdf"),
        ("private_artifact", "private.json"),
        ("raw_crawl_output", "body.html"),
        ("raw_pdf", "%PDF"),
        ("session_artifact", "storage-state.json"),
        ("storage_state", "state.json"),
        ("trace_file", "trace.zip"),
        ("note", "The raw PDF data is attached."),
        ("note", "This includes authenticated facts from the account."),
    ]

    for key, value in unsafe_cases:
        packet = _packet()
        packet[key] = value
        result = validate_reviewer_disposition_packet_v2(packet)
        assert not result.ok, key


def test_rejects_legal_or_permitting_guarantees_and_consequential_action_language() -> None:
    unsafe_notes = [
        "The permit will be approved.",
        "This legal outcome is guaranteed.",
        "The permitting outcome will be issued.",
        "Guarantees approval for the fixture.",
        "Finally submit the application.",
        "Click the certify button.",
        "Upload corrections in DevHub.",
        "Schedule inspection after approval.",
        "Enter payment details now.",
        "Cancel permit from the portal.",
    ]

    for note in unsafe_notes:
        packet = _packet()
        packet["note"] = note
        result = validate_reviewer_disposition_packet_v2(packet)
        assert not result.ok, note


def test_rejects_active_source_document_requirement_process_guardrail_prompt_release_or_agent_mutation_flags() -> None:
    unsafe_cases = [
        ("active_source_mutation", True),
        ("active_document_mutation", True),
        ("active_requirement_mutation", True),
        ("active_process_mutation", True),
        ("active_guardrail_mutation", True),
        ("active_prompt_mutation", True),
        ("active_release_state_mutation", True),
        ("active_agent_state_mutation", True),
        ("active_source", "enabled"),
        ("active_document", {"write": True}),
        ("active_requirement", ["change"]),
        ("active_process", True),
        ("mutates_guardrails", True),
        ("mutates_prompt", True),
        ("mutates_release_state", True),
        ("mutates_agent_state", True),
    ]

    for key, value in unsafe_cases:
        packet = _packet()
        packet[key] = value
        result = validate_reviewer_disposition_packet_v2(packet)
        assert not result.ok, key
