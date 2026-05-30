from __future__ import annotations

from pathlib import Path

import pytest

from ppd.guarded_replay_acceptance_v2 import (
    GuardedReplayAcceptanceV2Error,
    require_acceptance_packet_v2,
    validate_acceptance_packet_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guarded_replay_acceptance_v2"


def valid_packet() -> dict:
    return {
        "version": 2,
        "reviewer_acceptance_rows": [
            {"reviewer": "fixture-reviewer", "accepted": True, "reviewed_at": "2026-05-30T00:00:00Z"}
        ],
        "scenario_to_evidence_traces": [
            {"scenario": "deterministic replay fixture", "evidence": ["fixture transcript hash"]}
        ],
        "review_placeholders": {
            "missing_fact_prompt_review": {"status": "pending_review"},
            "blocked_action_review": {"status": "pending_review"},
            "reversible_draft_preview_review": {"status": "pending_review"},
        },
        "unresolved_risk_notes": ["No live DevHub, crawl, private session, or official action evidence is included."],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "artifacts": ["ppd/tests/fixtures/guarded_replay_acceptance_v2/packet.json"],
        "claims": ["Deterministic fixture-only replay validation."],
        "mutation_flags": {
            "active_prompt_mutation": False,
            "active_contract_mutation": False,
            "active_guardrail_mutation": False,
            "active_source_mutation": False,
            "active_surface_mutation": False,
            "active_release_state_mutation": False,
        },
    }


def test_valid_fixture_shape_is_accepted() -> None:
    assert FIXTURE_DIR.name == "guarded_replay_acceptance_v2"
    assert validate_acceptance_packet_v2(valid_packet()) == []
    require_acceptance_packet_v2(valid_packet())


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("reviewer_acceptance_rows", "missing reviewer acceptance rows"),
        ("scenario_to_evidence_traces", "missing scenario-to-evidence traces"),
        ("unresolved_risk_notes", "missing unresolved-risk notes"),
        ("validation_commands", "missing validation commands"),
    ],
)
def test_required_rows_traces_notes_and_commands_are_rejected_when_missing(field: str, expected: str) -> None:
    packet = valid_packet()
    packet[field] = []
    assert expected in validate_acceptance_packet_v2(packet)


@pytest.mark.parametrize(
    ("placeholder", "expected"),
    [
        ("missing_fact_prompt_review", "missing missing_fact_prompt_review placeholder"),
        ("blocked_action_review", "missing blocked_action_review placeholder"),
        ("reversible_draft_preview_review", "missing reversible_draft_preview_review placeholder"),
    ],
)
def test_required_review_placeholders_are_rejected_when_missing(placeholder: str, expected: str) -> None:
    packet = valid_packet()
    del packet["review_placeholders"][placeholder]
    assert expected in validate_acceptance_packet_v2(packet)


@pytest.mark.parametrize("marker", ["private", "session", "browser", "raw", "downloaded"])
def test_private_session_browser_raw_and_downloaded_artifacts_are_rejected(marker: str) -> None:
    packet = valid_packet()
    packet["artifacts"] = [f"ppd/tests/fixtures/{marker}-artifact.json"]
    assert f"prohibited artifact marker: {marker}" in validate_acceptance_packet_v2(packet)


@pytest.mark.parametrize(
    "claim",
    [
        "live DevHub evidence was checked",
        "crawl claim collected evidence",
        "application submitted for official action completed",
        "permit will be approved",
        "this is legal advice",
    ],
)
def test_live_crawl_official_action_and_guarantee_claims_are_rejected(claim: str) -> None:
    packet = valid_packet()
    packet["claims"] = [claim]
    assert validate_acceptance_packet_v2(packet)


@pytest.mark.parametrize(
    "flag",
    [
        "active_prompt_mutation",
        "active_contract_mutation",
        "active_guardrail_mutation",
        "active_source_mutation",
        "active_surface_mutation",
        "active_release_state_mutation",
    ],
)
def test_active_mutation_flags_are_rejected(flag: str) -> None:
    packet = valid_packet()
    packet["mutation_flags"][flag] = True
    assert f"active mutation flag is not allowed: {flag}" in validate_acceptance_packet_v2(packet)


def test_require_acceptance_packet_v2_raises_with_errors() -> None:
    packet = valid_packet()
    packet["reviewer_acceptance_rows"] = []
    with pytest.raises(GuardedReplayAcceptanceV2Error) as excinfo:
        require_acceptance_packet_v2(packet)
    assert "missing reviewer acceptance rows" in str(excinfo.value)
