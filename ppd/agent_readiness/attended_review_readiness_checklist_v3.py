"""Fixture-first attended review readiness checklist v3.

This module intentionally consumes committed fixture data only. It prepares a
future attended human review packet from three already-offline artifacts:

* inactive migration bundle acceptance packet v2
* guardrail regression replay matrix v3
* public source freshness watch plan v3

No live crawl, authentication, release, upload, submission, payment, or official
action is performed here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CHECKLIST_VERSION = "attended-review-readiness-checklist-v3"

_REQUIRED_INPUT_KEYS = (
    "inactive_migration_bundle_acceptance_packet_v2",
    "guardrail_regression_replay_matrix_v3",
    "public_source_freshness_watch_plan_v3",
)

_REQUIRED_ATTESTATIONS = (
    "no_live_crawl",
    "no_authentication",
    "no_release",
    "no_official_action",
)


class ChecklistFixtureError(ValueError):
    """Raised when a readiness checklist fixture is incomplete or unsafe."""


def load_fixture_packet(path: str | Path) -> dict[str, Any]:
    """Load a JSON fixture packet from disk."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ChecklistFixtureError("fixture packet must be a JSON object")
    return packet


def build_attended_review_readiness_checklist_v3(packet: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic attended review readiness checklist from fixtures."""

    _validate_packet(packet)

    migration_packet = packet["inactive_migration_bundle_acceptance_packet_v2"]
    replay_matrix = packet["guardrail_regression_replay_matrix_v3"]
    freshness_plan = packet["public_source_freshness_watch_plan_v3"]

    checklist_rows = []
    checklist_rows.extend(_rows_from_migration_packet(migration_packet))
    checklist_rows.extend(_rows_from_replay_matrix(replay_matrix))
    checklist_rows.extend(_rows_from_freshness_plan(freshness_plan))

    unresolved_deferrals = _collect_unresolved_deferrals(
        migration_packet,
        replay_matrix,
        freshness_plan,
    )

    acceptance_criteria = [
        {
            "criterion_id": "fixture-only-inputs",
            "description": "Readiness review input is limited to committed fixture packet data.",
            "evidence_refs": _packet_evidence_refs(packet),
            "required_result": "No live crawl, authenticated session, raw document download, or official action is needed to render the checklist.",
        },
        {
            "criterion_id": "cited-human-review-rows",
            "description": "Every checklist row includes source fixture references and human-review disposition fields.",
            "evidence_refs": [row["row_id"] for row in checklist_rows],
            "required_result": "Attended reviewers can trace each row back to an offline fixture artifact.",
        },
        {
            "criterion_id": "deferrals-remain-explicit",
            "description": "Unresolved gaps are carried as deferrals instead of being silently accepted.",
            "evidence_refs": [item["deferral_id"] for item in unresolved_deferrals],
            "required_result": "Future attended review can resolve or reject each deferred item with a named reviewer action.",
        },
    ]

    rollback_verification = [
        {
            "check_id": "rollback-fixture-only",
            "description": "Removing the generated checklist leaves only static fixture and test artifacts.",
            "expected_evidence": "No private DevHub state, auth files, traces, HAR files, screenshots, or raw crawl output are created.",
        },
        {
            "check_id": "rollback-no-official-state",
            "description": "The checklist builder has no code path for upload, submit, certify, schedule, cancel, pay, or release actions.",
            "expected_evidence": "Review rollback requires only dropping the generated checklist object or reverting fixture/test files.",
        },
    ]

    offline_validation_commands = [
        ["python3", "-m", "py_compile", "ppd/agent_readiness/attended_review_readiness_checklist_v3.py"],
        ["python3", "-m", "unittest", "ppd.tests.test_attended_review_readiness_checklist_v3"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]

    attestations = {
        "no_live_crawl": True,
        "no_authentication": True,
        "no_release": True,
        "no_official_action": True,
        "fixture_first": True,
        "future_attended_review_only": True,
    }

    return {
        "checklist_version": CHECKLIST_VERSION,
        "source_fixture_packet_id": _string_value(packet, "packet_id"),
        "generated_from": list(_REQUIRED_INPUT_KEYS),
        "checklist_rows": checklist_rows,
        "unresolved_deferrals": unresolved_deferrals,
        "fixture_only_acceptance_criteria": acceptance_criteria,
        "rollback_verification": rollback_verification,
        "offline_validation_commands": offline_validation_commands,
        "attestations": attestations,
    }


def _validate_packet(packet: dict[str, Any]) -> None:
    for key in _REQUIRED_INPUT_KEYS:
        if key not in packet:
            raise ChecklistFixtureError(f"missing required fixture input: {key}")
        if not isinstance(packet[key], dict):
            raise ChecklistFixtureError(f"fixture input must be an object: {key}")

    attestations = packet.get("attestations", {})
    if not isinstance(attestations, dict):
        raise ChecklistFixtureError("attestations must be an object")
    for key in _REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            raise ChecklistFixtureError(f"required attestation is not true: {key}")


def _rows_from_migration_packet(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in _list_value(packet, "acceptance_items"):
        rows.append(
            {
                "row_id": f"migration::{_string_value(item, 'item_id')}",
                "review_area": "inactive migration bundle acceptance",
                "human_review_question": _string_value(item, "review_question"),
                "fixture_input": "inactive_migration_bundle_acceptance_packet_v2",
                "cited_evidence": _list_value(item, "citations"),
                "readiness_signal": _string_value(item, "status"),
                "required_attended_action": _string_value(item, "required_attended_action"),
                "side_effect_boundary": "fixture review only; no migration activation or release action",
            }
        )
    return rows


def _rows_from_replay_matrix(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in _list_value(matrix, "scenarios"):
        rows.append(
            {
                "row_id": f"guardrail::{_string_value(scenario, 'scenario_id')}",
                "review_area": "guardrail regression replay",
                "human_review_question": _string_value(scenario, "review_question"),
                "fixture_input": "guardrail_regression_replay_matrix_v3",
                "cited_evidence": _list_value(scenario, "citations"),
                "readiness_signal": _string_value(scenario, "expected_outcome"),
                "required_attended_action": _string_value(scenario, "required_attended_action"),
                "side_effect_boundary": "offline replay only; no DevHub login, click, submit, upload, schedule, cancel, or payment",
            }
        )
    return rows


def _rows_from_freshness_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for source in _list_value(plan, "watch_sources"):
        rows.append(
            {
                "row_id": f"freshness::{_string_value(source, 'source_id')}",
                "review_area": "public source freshness watch",
                "human_review_question": _string_value(source, "review_question"),
                "fixture_input": "public_source_freshness_watch_plan_v3",
                "cited_evidence": _list_value(source, "citations"),
                "readiness_signal": _string_value(source, "freshness_status"),
                "required_attended_action": _string_value(source, "required_attended_action"),
                "side_effect_boundary": "watch-plan review only; no live public crawl or document download",
            }
        )
    return rows


def _collect_unresolved_deferrals(*sections: dict[str, Any]) -> list[dict[str, Any]]:
    deferrals = []
    for section in sections:
        for item in _list_value(section, "unresolved_deferrals"):
            deferrals.append(
                {
                    "deferral_id": _string_value(item, "deferral_id"),
                    "source_artifact": _string_value(item, "source_artifact"),
                    "reason": _string_value(item, "reason"),
                    "reviewer_resolution_needed": _string_value(item, "reviewer_resolution_needed"),
                    "citations": _list_value(item, "citations"),
                }
            )
    return deferrals


def _packet_evidence_refs(packet: dict[str, Any]) -> list[str]:
    refs = []
    for key in _REQUIRED_INPUT_KEYS:
        artifact = packet[key]
        refs.append(_string_value(artifact, "artifact_id"))
    return refs


def _list_value(mapping: dict[str, Any], key: str) -> list[Any]:
    value = mapping.get(key, [])
    if not isinstance(value, list):
        raise ChecklistFixtureError(f"expected list at {key}")
    return value


def _string_value(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ChecklistFixtureError(f"expected non-empty string at {key}")
    return value


__all__ = [
    "CHECKLIST_VERSION",
    "ChecklistFixtureError",
    "build_attended_review_readiness_checklist_v3",
    "load_fixture_packet",
]
