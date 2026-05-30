from __future__ import annotations

from pathlib import Path

from ppd.local_draft_preview_review_packet_v2 import ATTESTATIONS, build_from_paths

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "local_draft_preview_review_packet_v2"


def test_builds_reviewer_visible_fixture_packet() -> None:
    packet = build_from_paths(
        FIXTURE_DIR / "preview_plan.json",
        FIXTURE_DIR / "readiness_packet.json",
        FIXTURE_DIR / "gap_analysis.json",
    )

    assert packet["packet_version"] == "local-draft-preview-review-packet-v2"
    assert packet["mode"] == "fixture-first-offline"
    assert packet["attestations"] == ATTESTATIONS

    rows = packet["reviewer_visible_preview_rows"]
    assert len(rows) == 2
    assert rows[0]["row_id"] == "permit-address"
    assert "Local PDF draft preview plan v2 fixture" in rows[0]["citation"]
    assert rows[0]["reviewer_owner"] == "Intake reviewer"
    assert rows[0]["confirmation_checkpoint"].startswith("Confirm the address exactly")
    assert rows[0]["rollback_note"].startswith("Delete the generated row")


def test_includes_blockers_gaps_validation_and_guardrails() -> None:
    packet = build_from_paths(
        FIXTURE_DIR / "preview_plan.json",
        FIXTURE_DIR / "readiness_packet.json",
        FIXTURE_DIR / "gap_analysis.json",
    )

    blockers = packet["unresolved_blocker_summaries"]
    gaps = packet["gap_analysis_checkpoints"]
    commands = packet["offline_validation_commands"]

    assert blockers == [
        {
            "blocker_id": "owner-confirmation",
            "summary": "Owner authorization remains fixture-marked as unresolved.",
            "owner": "Applicant coordinator",
            "citation": "Reversible draft preview readiness packet v2 fixture (ppd/tests/fixtures/local_draft_preview_review_packet_v2/readiness_packet.json)",
        }
    ]
    assert gaps[0]["gap_id"] == "fee-estimate-gap"
    assert gaps[0]["exact_confirmation"] == "Reviewer must confirm the fee estimate source before any live portal action."
    assert ["python3", "-m", "py_compile", "ppd/local_draft_preview_review_packet_v2.py"] in commands
    assert packet["attestations"]["no_private_documents"] is True
    assert packet["attestations"]["no_pdf_write"] is True
    assert packet["attestations"]["no_upload"] is True
    assert packet["attestations"]["no_devhub"] is True
    assert packet["attestations"]["no_agent_state_mutation"] is True
