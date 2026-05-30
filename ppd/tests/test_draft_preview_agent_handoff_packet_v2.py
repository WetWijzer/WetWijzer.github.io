from pathlib import Path

from ppd.draft_preview_agent_handoff_packet_v2 import (
    PACKET_VERSION,
    REQUIRED_ATTESTATIONS,
    build_packet_from_paths,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "draft_preview_agent_handoff_packet_v2"
SMOKE_TRANSCRIPT = FIXTURE_DIR / "reversible_draft_preview_offline_smoke_transcript_v2.json"
REVIEW_PACKET = FIXTURE_DIR / "local_draft_preview_review_packet_v2.json"
PROMPT_RELEASE_HANDOFF = FIXTURE_DIR / "prompt_refresh_release_handoff_fixtures.json"


def test_builds_fixture_first_handoff_packet_v2() -> None:
    packet = build_packet_from_paths(SMOKE_TRANSCRIPT, REVIEW_PACKET, PROMPT_RELEASE_HANDOFF)

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["source_fixture_ids"] == [
        "offline-smoke-transcript-draft-preview-v2-20260529",
        "local-review-packet-draft-preview-v2-20260529",
        "prompt-refresh-release-handoff-fixtures-20260529",
    ]
    assert len(packet["fixture_provenance"]) == 3
    assert all(item["sha256"] for item in packet["fixture_provenance"])


def test_consumer_notes_are_cited_and_boundary_focused() -> None:
    packet = build_packet_from_paths(SMOKE_TRANSCRIPT, REVIEW_PACKET, PROMPT_RELEASE_HANDOFF)

    notes = packet["consumer_facing_handoff_notes"]
    assert notes
    assert all(note["citations"] for note in notes)
    combined = " ".join(note["body"] for note in notes).lower()
    assert "draft preview only" in combined
    assert "does not submit" in combined
    assert "private documents" in combined


def test_safe_scenarios_and_blocked_language_are_explicit() -> None:
    packet = build_packet_from_paths(SMOKE_TRANSCRIPT, REVIEW_PACKET, PROMPT_RELEASE_HANDOFF)

    scenarios = packet["supported_safe_draft_preview_scenarios"]
    scenario_ids = {scenario["scenario_id"] for scenario in scenarios}
    assert "local-pdf-preview-only" in scenario_ids
    assert "draft-field-gap-review" in scenario_ids

    blocked = packet["blocked_consequential_action_language"]
    blocked_actions = {item["action"] for item in blocked}
    assert {"submit_application", "upload_document", "pay_fee"}.issubset(blocked_actions)
    blocked_text = " ".join(item["consumer_language"].lower() for item in blocked)
    assert "cannot submit" in blocked_text
    assert "cannot upload" in blocked_text
    assert "cannot enter payment details" in blocked_text


def test_exact_confirmation_rollback_validation_and_attestations() -> None:
    packet = build_packet_from_paths(SMOKE_TRANSCRIPT, REVIEW_PACKET, PROMPT_RELEASE_HANDOFF)

    triggers = {item["trigger"] for item in packet["required_exact_confirmation_reminders"]}
    assert "submit_application" in triggers
    assert "upload_document" in triggers
    assert "pay_fee" in triggers
    assert "schedule_or_cancel_inspection" in triggers

    rollback = packet["rollback_owner_fields"]
    assert rollback["owner"] == "PP&D draft preview fixture maintainer"
    assert "no DevHub or release state rollback" in rollback["rollback_scope"]

    commands = packet["offline_validation_commands"]
    assert ["python3", "-m", "py_compile", "ppd/draft_preview_agent_handoff_packet_v2.py"] in commands
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in commands

    assert packet["attestations"] == {key: True for key in REQUIRED_ATTESTATIONS}
