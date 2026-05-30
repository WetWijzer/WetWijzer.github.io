"""Build fixture-first guarded agent replay acceptance packets.

This module intentionally stays offline and data-only. It does not invoke browser
automation, live crawls, prompt rendering, authenticated surfaces, or production
contracts. The packet is a reviewer acceptance aid derived from a supplied
post-release guarded agent replay matrix v2 fixture.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PACKET_VERSION = "guarded-agent-replay-acceptance-packet-v2"
SOURCE_MATRIX_VERSION = "post-release-guarded-agent-replay-matrix-v2"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/review/guarded_agent_replay_acceptance_packet_v2.py"],
    ["python3", "-m", "py_compile", "ppd/tests/test_guarded_agent_replay_acceptance_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_guarded_agent_replay_acceptance_packet_v2.py"],
]


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON object from disk."""
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("expected a JSON object")
    return loaded


def build_acceptance_packet(matrix: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a guarded agent replay matrix fixture into reviewer rows."""
    matrix_version = str(matrix.get("matrix_version", ""))
    if matrix_version != SOURCE_MATRIX_VERSION:
        raise ValueError(f"expected matrix_version {SOURCE_MATRIX_VERSION!r}")

    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError("expected scenarios to be a list")

    ordered_scenarios = sorted(
        (_require_mapping(item, "scenario") for item in scenarios),
        key=lambda item: (int(item.get("reviewer_order", 9999)), str(item.get("scenario_id", ""))),
    )

    rows = [_build_row(index + 1, scenario) for index, scenario in enumerate(ordered_scenarios)]

    return {
        "packet_version": PACKET_VERSION,
        "source_matrix_version": matrix_version,
        "source_fixture": matrix.get("source_fixture", "post_release_guarded_agent_replay_matrix_v2.json"),
        "acceptance_scope": {
            "fixture_first": True,
            "offline_only": True,
            "changes_active_prompts": False,
            "changes_production_contracts": False,
            "changes_guardrails": False,
            "changes_release_state": False,
            "changes_public_sources": False,
            "creates_private_artifacts": False,
        },
        "reviewer_acceptance_rows": rows,
        "unresolved_risk_notes": _normalise_text_list(matrix.get("unresolved_risk_notes")),
        "exact_offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


def write_acceptance_packet(matrix_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """Build and write an acceptance packet JSON file."""
    packet = build_acceptance_packet(load_json(matrix_path))
    Path(output_path).write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def _build_row(position: int, scenario: Mapping[str, Any]) -> dict[str, Any]:
    scenario_id = _required_text(scenario, "scenario_id")
    evidence = _normalise_text_list(scenario.get("evidence_refs"))
    blocked_actions = _normalise_text_list(scenario.get("blocked_actions"))
    missing_facts = _normalise_text_list(scenario.get("missing_fact_prompts"))
    draft_previews = _normalise_text_list(scenario.get("reversible_draft_previews"))
    risks = _normalise_text_list(scenario.get("unresolved_risks"))

    return {
        "reviewer_order": position,
        "scenario_id": scenario_id,
        "reviewer_acceptance_row": {
            "title": str(scenario.get("title", scenario_id)),
            "expected_guarded_outcome": str(scenario.get("expected_guarded_outcome", "review required before action")),
            "acceptance_status": "pending_reviewer_acceptance",
        },
        "scenario_to_evidence_trace_placeholder": {
            "status": "placeholder_pending_reviewer_trace",
            "expected_evidence_refs": evidence,
            "notes": "Reviewer records fixture evidence mapping here; no live crawl or private artifact is required.",
        },
        "missing_fact_prompt_review_placeholder": {
            "status": "placeholder_pending_reviewer_review",
            "expected_prompts": missing_facts,
        },
        "blocked_action_review_placeholder": {
            "status": "placeholder_pending_reviewer_review",
            "expected_blocked_actions": blocked_actions,
        },
        "reversible_draft_preview_review_placeholder": {
            "status": "placeholder_pending_reviewer_review",
            "expected_preview_refs": draft_previews,
        },
        "unresolved_risk_notes": risks,
    }


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"expected {label} to be an object")
    return value


def _required_text(source: Mapping[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"expected non-empty text field {key!r}")
    return value


def _normalise_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("expected a list of strings")
    normalised: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("expected a list of non-empty strings")
        normalised.append(item)
    return normalised
