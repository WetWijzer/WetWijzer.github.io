from __future__ import annotations

import json
from pathlib import Path

from ppd.logic.guardrail_bundle_refresh_candidate_v2 import (
    REQUIRED_ATTESTATIONS,
    REQUIRED_OFFLINE_COMMANDS,
    build_from_fixture_paths,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrail_bundle_refresh_candidate_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_builds_expected_guardrail_bundle_refresh_candidate_v2_packet() -> None:
    candidate = build_from_fixture_paths(
        FIXTURE_DIR / "process_model_refresh_impact_v2.json",
        FIXTURE_DIR / "requirement_regeneration_work_order_v2.json",
        FIXTURE_DIR / "guardrail_compiler_fixture_v2.json",
    )

    expected = _load_fixture("expected_guardrail_bundle_refresh_candidate_v2.json")

    assert candidate == expected


def test_packet_contains_required_safety_attestations_and_offline_commands() -> None:
    candidate = build_from_fixture_paths(
        FIXTURE_DIR / "process_model_refresh_impact_v2.json",
        FIXTURE_DIR / "requirement_regeneration_work_order_v2.json",
        FIXTURE_DIR / "guardrail_compiler_fixture_v2.json",
    )

    assert candidate["attestations"] == {name: True for name in REQUIRED_ATTESTATIONS}
    assert candidate["offline_validation_commands"] == [list(command) for command in REQUIRED_OFFLINE_COMMANDS]


def test_packet_preserves_cited_predicate_update_candidate_fields() -> None:
    candidate = build_from_fixture_paths(
        FIXTURE_DIR / "process_model_refresh_impact_v2.json",
        FIXTURE_DIR / "requirement_regeneration_work_order_v2.json",
        FIXTURE_DIR / "guardrail_compiler_fixture_v2.json",
    )

    predicate_ids = {entry["predicate_id"] for entry in candidate["predicate_update_candidates"]}

    assert predicate_ids == {
        "predicate:upload-staging-remains-reversible",
        "predicate:certification-requires-exact-confirmation",
        "predicate:submit-action-blocked-without-attendance",
    }
    assert candidate["affected_process_ids"] == [
        "process:building-permit-plan-review",
        "process:trade-permit-with-plan-review",
    ]
    assert all(entry["reviewer_owner"] == "ppd-requirements-reviewer" for entry in candidate["predicate_update_candidates"])
    assert all(entry["requires_human_review"] is True for entry in candidate["predicate_update_candidates"])


def test_packet_declares_reversible_and_exact_confirmation_checkpoint_expectations() -> None:
    candidate = build_from_fixture_paths(
        FIXTURE_DIR / "process_model_refresh_impact_v2.json",
        FIXTURE_DIR / "requirement_regeneration_work_order_v2.json",
        FIXTURE_DIR / "guardrail_compiler_fixture_v2.json",
    )

    reversible = candidate["reversible_action_checkpoint_expectations"]
    exact = candidate["exact_confirmation_checkpoint_expectations"]

    assert reversible == [
        {
            "predicate_id": "predicate:upload-staging-remains-reversible",
            "action_type": "stage_upload",
            "expected_checkpoint": "reversible_action_checkpoint",
            "must_remain_draft_only": True,
            "citation_ids": ["evidence:ppd-submit-plans-online:single-pdf-process"],
        }
    ]
    assert {entry["action_type"] for entry in exact} == {
        "certify_acknowledgement",
        "submit_permit_request",
    }
    assert all(entry["requires_user_visible_action_label"] is True for entry in exact)
