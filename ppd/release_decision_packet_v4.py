"""Fixture-first PP&D release decision packet v4.

This module only reads inactive guardrail promotion candidate v4 fixtures and
assembles reviewer-facing release decision data. It does not activate guardrails,
open DevHub, fetch documents, upload, submit, certify, pay, schedule, or make
legal/permitting guarantees.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PACKET_VERSION = "release_decision_packet_v4"
CANDIDATE_VERSION = "inactive_guardrail_promotion_candidate_v4"
OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/release_decision_packet_v4.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_release_decision_packet_v4.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def load_candidates(fixture_path: str | Path) -> list[dict[str, Any]]:
    """Load inactive guardrail promotion candidate v4 fixtures."""
    path = Path(fixture_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("fixture must contain a candidates list")
    for candidate in candidates:
        _assert_inactive_candidate_v4(candidate)
    return candidates


def build_packet(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic reviewer-facing decision packet."""
    if not candidates:
        raise ValueError("at least one inactive candidate fixture is required")
    for candidate in candidates:
        _assert_inactive_candidate_v4(candidate)

    unresolved_holds = _collect_unresolved_holds(candidates)
    freshness_caveats = _collect_unique(candidates, "source_freshness_caveats")
    api_notes = _collect_unique(candidates, "agent_api_compatibility_notes")
    rollback_placeholders = _collect_rollback_placeholders(candidates)

    recommendation = "NO_GO" if unresolved_holds else "GO_WITH_CAVEATS"
    rationale = (
        "Unresolved holds remain; do not promote guardrails."
        if unresolved_holds
        else "No unresolved holds were present in the inactive fixture set; reviewer approval is still required before any activation."
    )

    return {
        "packet_version": PACKET_VERSION,
        "input_candidate_version": CANDIDATE_VERSION,
        "source_mode": "fixtures_only",
        "guardrail_activation": "not_performed",
        "devhub_access": "not_performed",
        "legal_or_permitting_guarantee": "not_provided",
        "recommendation": recommendation,
        "recommendation_rationale": rationale,
        "candidate_ids": [candidate["candidate_id"] for candidate in candidates],
        "unresolved_hold_inventory": unresolved_holds,
        "source_freshness_caveats": freshness_caveats,
        "agent_api_compatibility_notes": api_notes,
        "rollback_owner_placeholders": rollback_placeholders,
        "post_decision_smoke_replay_plan": [
            "Keep guardrails inactive while replaying fixture-backed smoke checks.",
            "Run release packet tests against ppd/tests/fixtures/release_decision_packet_v4 only.",
            "Run daemon self-test offline after packet generation.",
            "Require a human reviewer to assign rollback owners before any separate activation change."
        ],
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


def build_packet_from_fixture(fixture_path: str | Path) -> dict[str, Any]:
    return build_packet(load_candidates(fixture_path))


def _assert_inactive_candidate_v4(candidate: dict[str, Any]) -> None:
    if candidate.get("candidate_version") != CANDIDATE_VERSION:
        raise ValueError("candidate must be inactive_guardrail_promotion_candidate_v4")
    if candidate.get("status") != "inactive":
        raise ValueError("candidate status must be inactive")
    if candidate.get("guardrails_active") is not False:
        raise ValueError("candidate must not activate guardrails")
    if not isinstance(candidate.get("candidate_id"), str) or not candidate["candidate_id"]:
        raise ValueError("candidate_id is required")


def _collect_unresolved_holds(candidates: list[dict[str, Any]]) -> list[dict[str, str]]:
    holds: list[dict[str, str]] = []
    for candidate in candidates:
        for hold in candidate.get("unresolved_holds", []):
            holds.append({
                "candidate_id": candidate["candidate_id"],
                "hold_id": str(hold.get("hold_id", "unidentified_hold")),
                "reason": str(hold.get("reason", "unspecified")),
                "owner_placeholder": str(hold.get("owner_placeholder", "TBD_REVIEWER")),
            })
    return holds


def _collect_unique(candidates: list[dict[str, Any]], field: str) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for candidate in candidates:
        for value in candidate.get(field, []):
            text = str(value)
            if text not in seen:
                seen.add(text)
                values.append(text)
    return values


def _collect_rollback_placeholders(candidates: list[dict[str, Any]]) -> list[dict[str, str]]:
    placeholders: list[dict[str, str]] = []
    for candidate in candidates:
        rollback = candidate.get("rollback", {})
        placeholders.append({
            "candidate_id": candidate["candidate_id"],
            "rollback_owner_placeholder": str(rollback.get("owner_placeholder", "TBD_ROLLBACK_OWNER")),
            "rollback_decision_placeholder": str(rollback.get("decision_placeholder", "TBD_REVIEW_DECISION")),
        })
    return placeholders
