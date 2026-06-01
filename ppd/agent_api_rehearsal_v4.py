"""Fixture-first PP&D agent API compatibility rehearsal v4.

The rehearsal is intentionally offline-only. It reads committed monitoring and
synthetic agent request fixtures, then returns deterministic compatibility
responses for the agent-facing API surface without activating guardrails or
performing DevHub/browser/document/payment/submission side effects.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REHEARSAL_VERSION = "agent_api_compatibility_rehearsal_v4"
MONITORING_FIXTURE_KIND = "post_activation_monitoring_rehearsal_v4"
REQUEST_FIXTURE_KIND = "synthetic_agent_request_v4"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_api_rehearsal_v4.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_agent_api_rehearsal_v4.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

PROHIBITED_SIDE_EFFECTS = {
    "activate_guardrails": False,
    "open_devhub": False,
    "read_private_documents": False,
    "upload": False,
    "submit": False,
    "certify": False,
    "pay": False,
    "schedule": False,
    "legal_or_permitting_guarantee": False,
}

SAFE_DRAFT_ACTIONS = {"draft_pdf_fields", "draft_devhub_fields", "save_local_draft"}
MANUAL_HANDOFF_ACTIONS = {"upload", "submit", "certify", "pay", "schedule", "cancel", "withdraw"}
REFUSED_ACTIONS = {"guarantee_permit_approval", "bypass_captcha", "bypass_mfa", "create_account"}


def load_json_fixture(path: Path) -> dict[str, Any]:
    """Load a JSON fixture object from a committed fixture path."""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return payload


def load_fixture_dir(fixture_dir: Path, expected_kind: str) -> list[dict[str, Any]]:
    """Load all JSON fixtures of the expected kind from a directory."""
    if not fixture_dir.is_dir():
        raise FileNotFoundError(f"fixture directory does not exist: {fixture_dir}")

    fixtures: list[dict[str, Any]] = []
    for path in sorted(fixture_dir.glob("*.json")):
        payload = load_json_fixture(path)
        if payload.get("fixture_kind") != expected_kind:
            raise ValueError(
                f"unexpected fixture kind in {path}: {payload.get('fixture_kind')!r}"
            )
        payload["_fixture_path"] = path.name
        fixtures.append(payload)

    if not fixtures:
        raise ValueError(f"no {expected_kind} fixtures found in {fixture_dir}")
    return fixtures


def build_monitoring_index(monitoring_fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    """Index public rehearsal evidence by case id and source id."""
    cases: dict[str, dict[str, Any]] = {}
    sources: dict[str, dict[str, Any]] = {}

    for fixture in monitoring_fixtures:
        for source in fixture.get("source_citations", []):
            source_id = source.get("source_id")
            if source_id:
                sources[source_id] = source

        for case in fixture.get("cases", []):
            case_id = case.get("case_id")
            if not case_id:
                raise ValueError(f"monitoring case missing case_id in {fixture['_fixture_path']}")
            cases[case_id] = case

    return {"cases": cases, "sources": sources}


def citation_payload(source_ids: list[str], sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Return source citation payloads limited to public fixture metadata."""
    citations: list[dict[str, Any]] = []
    for source_id in source_ids:
        source = sources.get(source_id, {})
        citations.append(
            {
                "source_id": source_id,
                "canonical_url": source.get("canonical_url"),
                "title": source.get("title"),
                "last_verified_at": source.get("last_verified_at"),
                "excerpt": source.get("excerpt"),
            }
        )
    return citations


def classify_action(action: str) -> str:
    if action in SAFE_DRAFT_ACTIONS:
        return "reversible_draft_only"
    if action in MANUAL_HANDOFF_ACTIONS:
        return "manual_handoff_required"
    if action in REFUSED_ACTIONS:
        return "refused"
    return "read_only_or_gap_analysis"


def build_response(
    request: dict[str, Any],
    monitoring_index: dict[str, Any],
) -> dict[str, Any]:
    """Build one deterministic expected agent API response."""
    request_id = request.get("request_id")
    case_id = request.get("case_id")
    action = request.get("requested_action", "analyze_case")
    case = monitoring_index["cases"].get(case_id, {})
    action_class = classify_action(action)

    missing_facts = list(case.get("missing_facts", []))
    stale_evidence = list(case.get("stale_evidence", []))
    conflicting_evidence = list(case.get("conflicting_evidence", []))
    source_ids = list(dict.fromkeys(request.get("source_ids", []) + case.get("source_ids", [])))

    blocks: list[str] = []
    if missing_facts:
        blocks.append("missing_facts")
    if stale_evidence:
        blocks.append("stale_evidence")
    if conflicting_evidence:
        blocks.append("conflicting_evidence")
    if action_class in {"manual_handoff_required", "refused"}:
        blocks.append(action_class)

    refusal_explanation = None
    if action_class == "refused":
        refusal_explanation = (
            "The requested action is outside PP&D offline rehearsal boundaries and "
            "cannot be represented as a safe draft, read-only review, or attended handoff."
        )
    elif action_class == "manual_handoff_required":
        refusal_explanation = (
            "This official DevHub action requires user attendance and exact confirmation; "
            "the rehearsal reports the handoff instead of performing the action."
        )

    return {
        "rehearsal_version": REHEARSAL_VERSION,
        "request_id": request_id,
        "case_id": case_id,
        "requested_action": action,
        "action_classification": action_class,
        "status": "blocked" if blocks else "ready_for_read_only_response",
        "missing_facts": missing_facts,
        "stale_evidence": stale_evidence,
        "conflicting_evidence": conflicting_evidence,
        "reversible_draft_only": action_class == "reversible_draft_only",
        "manual_handoff_required": action_class == "manual_handoff_required",
        "refusal_explanation": refusal_explanation,
        "source_citations": citation_payload(source_ids, monitoring_index["sources"]),
        "blocked_reasons": blocks,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "side_effects": dict(PROHIBITED_SIDE_EFFECTS),
        "guarantees": [],
    }


def rehearse_agent_api_compatibility_v4(
    monitoring_fixture_dir: Path,
    synthetic_request_fixture_dir: Path,
) -> dict[str, Any]:
    """Run the offline compatibility rehearsal from committed fixtures only."""
    monitoring_fixtures = load_fixture_dir(monitoring_fixture_dir, MONITORING_FIXTURE_KIND)
    request_fixtures = load_fixture_dir(synthetic_request_fixture_dir, REQUEST_FIXTURE_KIND)
    monitoring_index = build_monitoring_index(monitoring_fixtures)

    responses = []
    for fixture in request_fixtures:
        for request in fixture.get("requests", []):
            responses.append(build_response(request, monitoring_index))

    return {
        "rehearsal_version": REHEARSAL_VERSION,
        "fixture_inputs": {
            "monitoring_fixture_kind": MONITORING_FIXTURE_KIND,
            "request_fixture_kind": REQUEST_FIXTURE_KIND,
            "monitoring_fixture_count": len(monitoring_fixtures),
            "request_fixture_count": len(request_fixtures),
        },
        "responses": responses,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "side_effects": dict(PROHIBITED_SIDE_EFFECTS),
    }
