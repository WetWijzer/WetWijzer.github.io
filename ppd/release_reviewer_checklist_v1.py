"""Fixture-first release reviewer go/no-go checklist v1.

This module is intentionally offline-only. It converts an inactive release
promotion readiness digest into deterministic reviewer checklist records without
mutating release state, applying fixture changes, or contacting live systems.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CHECKLIST_VERSION = "fixture-first-release-reviewer-go-no-go-checklist-v1"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/release_reviewer_checklist_v1.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_release_reviewer_checklist_v1"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def load_digest(path: str | Path) -> dict[str, Any]:
    """Load an inactive release promotion readiness digest fixture."""
    with Path(path).open("r", encoding="utf-8") as digest_file:
        data = json.load(digest_file)
    if not isinstance(data, dict):
        raise ValueError("release promotion readiness digest must be a JSON object")
    return data


def build_release_reviewer_checklist(digest: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic reviewer go/no-go checklist data from a digest."""
    release_id = str(digest.get("release_id", "inactive-release"))
    digest_id = str(digest.get("digest_id", "inactive-release-promotion-readiness-digest-v1"))
    generated_from = {
        "digest_id": digest_id,
        "release_id": release_id,
        "source_state": str(digest.get("source_state", "inactive")),
    }

    return {
        "checklist_version": CHECKLIST_VERSION,
        "mode": "fixture_first_offline_review_only",
        "generated_from": generated_from,
        "go_no_go_checklist_items": _checklist_items(digest),
        "evidence_citation_coverage_rows": _evidence_rows(digest),
        "rollback_readiness_confirmations": _rollback_confirmations(digest),
        "validation_replay_confirmations": _validation_confirmations(digest),
        "unresolved_risk_acknowledgement_placeholders": _risk_placeholders(digest),
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "guardrails": [
            "does_not_apply_fixture_changes",
            "does_not_mutate_active_artifacts",
            "does_not_update_release_state",
            "does_not_crawl_live_sources",
            "does_not_access_devhub",
            "does_not_perform_official_actions",
        ],
    }


def _checklist_items(digest: dict[str, Any]) -> list[dict[str, Any]]:
    gates = list(digest.get("promotion_gates", []))
    items: list[dict[str, Any]] = []
    for index, gate in enumerate(gates, start=1):
        gate_name = str(gate.get("name", f"gate-{index}"))
        status = str(gate.get("status", "unknown"))
        items.append(
            {
                "id": f"go-no-go-{index:02d}",
                "title": f"Review {gate_name}",
                "source_gate": gate_name,
                "digest_status": status,
                "required_reviewer_action": "confirm_go_no_go_decision",
                "default_decision": "go" if status == "ready" else "hold",
                "evidence_ids": _string_list(gate.get("evidence_ids", [])),
            }
        )
    return items


def _evidence_rows(digest: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = list(digest.get("evidence", []))
    rows: list[dict[str, Any]] = []
    for index, citation in enumerate(evidence, start=1):
        evidence_id = str(citation.get("id", f"evidence-{index}"))
        rows.append(
            {
                "row_id": f"evidence-coverage-{index:02d}",
                "evidence_id": evidence_id,
                "citation": str(citation.get("citation", "missing citation")),
                "covers": _string_list(citation.get("covers", [])),
                "reviewer_confirmation": "citation_seen_and_matches_digest_claim",
            }
        )
    return rows


def _rollback_confirmations(digest: dict[str, Any]) -> list[dict[str, str]]:
    rollback = digest.get("rollback_readiness", {})
    if not isinstance(rollback, dict):
        rollback = {}
    checks = rollback.get("checks", [])
    confirmations: list[dict[str, str]] = []
    for index, check in enumerate(checks, start=1):
        confirmations.append(
            {
                "id": f"rollback-{index:02d}",
                "confirmation": str(check),
                "reviewer_response_placeholder": "unanswered",
            }
        )
    return confirmations


def _validation_confirmations(digest: dict[str, Any]) -> list[dict[str, Any]]:
    validations = list(digest.get("validation_replay", []))
    confirmations: list[dict[str, Any]] = []
    for index, validation in enumerate(validations, start=1):
        confirmations.append(
            {
                "id": f"validation-replay-{index:02d}",
                "name": str(validation.get("name", f"validation-{index}")),
                "command": _string_list(validation.get("command", [])),
                "expected_result": str(validation.get("expected_result", "pass")),
                "reviewer_response_placeholder": "unanswered",
            }
        )
    return confirmations


def _risk_placeholders(digest: dict[str, Any]) -> list[dict[str, str]]:
    risks = list(digest.get("unresolved_risks", []))
    placeholders: list[dict[str, str]] = []
    for index, risk in enumerate(risks, start=1):
        placeholders.append(
            {
                "id": f"unresolved-risk-{index:02d}",
                "risk": str(risk.get("risk", risk)),
                "acknowledgement_placeholder": "reviewer_must_acknowledge_before_go",
            }
        )
    return placeholders


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build offline release reviewer checklist v1 JSON.")
    parser.add_argument("digest_fixture", help="Path to inactive readiness digest fixture JSON")
    args = parser.parse_args()
    checklist = build_release_reviewer_checklist(load_digest(args.digest_fixture))
    print(json.dumps(checklist, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
