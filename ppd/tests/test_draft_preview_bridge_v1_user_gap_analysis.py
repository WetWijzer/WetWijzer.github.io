from __future__ import annotations

import json
from pathlib import Path

from ppd.agent_readiness.draft_preview_bridge_v1_user_gap_analysis import (
    build_user_gap_analysis_from_packet,
    load_fixture_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "draft_preview_bridge_v1"


def _load_json(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_fixture_first_user_gap_analysis_matches_expected_packet() -> None:
    packet = load_fixture_packet(FIXTURE_DIR / "user_gap_analysis_inputs.json")
    expected = _load_json("expected_user_gap_analysis.json")

    assert build_user_gap_analysis_from_packet(packet) == expected


def test_user_gap_analysis_attests_no_private_devhub_or_official_action() -> None:
    packet = _load_json("user_gap_analysis_inputs.json")
    analysis = build_user_gap_analysis_from_packet(packet)

    assert analysis["attestations"] == {
        "no_private_file_attestation": True,
        "no_devhub_attestation": True,
        "no_official_action_attestation": True,
        "attestation_basis": [
            "fixture inputs only",
            "offline draft preview handoff v4 packet",
            "safe actions filtered to unauthenticated read-only classifications",
        ],
    }


def test_field_blockers_are_cited_and_field_scoped() -> None:
    analysis = build_user_gap_analysis_from_packet(_load_json("user_gap_analysis_inputs.json"))
    blockers = {item["field_id"]: item for item in analysis["field_level_draft_blockers"]}

    assert set(blockers) == {"draft-field::property-owner", "draft-field::site-plan-file"}
    assert blockers["draft-field::property-owner"]["blocking_fact_ids"] == ["fact::property-owner"]
    assert blockers["draft-field::property-owner"]["citations"] == ["src::devhub-submit-guide::dynamic-questions"]
    assert blockers["draft-field::site-plan-file"]["blocking_fact_ids"] == ["fact::site-plan-prepared"]
    assert blockers["draft-field::site-plan-file"]["citations"] == ["src::single-pdf-process::separate-documents"]


def test_next_actions_are_limited_to_unauthed_read_only_actions() -> None:
    analysis = build_user_gap_analysis_from_packet(_load_json("user_gap_analysis_inputs.json"))

    assert analysis["next_safe_read_only_actions"] == [
        {
            "action_id": "read::review-single-pdf-guidance",
            "label": "Review cited Single PDF Process guidance before asking the user for document readiness facts.",
            "classification": "read_only",
            "citations": ["src::single-pdf-process::separate-documents"],
        },
        {
            "action_id": "read::review-devhub-submit-guide",
            "label": "Review cited DevHub permit application guidance for dynamic questions and save-for-later limits.",
            "classification": "read_only",
            "citations": ["src::devhub-submit-guide::dynamic-questions"],
        },
    ]
