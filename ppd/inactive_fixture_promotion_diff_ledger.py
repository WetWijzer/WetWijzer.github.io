"""Fixture-first inactive fixture promotion diff ledger v1.

This module intentionally works only from committed JSON fixtures or caller-provided
packet dictionaries. It does not read or write active fixtures, release state, crawl
outputs, browser state, or authenticated artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEDGER_VERSION = "inactive_fixture_promotion_diff_ledger_v1"
DECISION_PACKET_VERSION = "release_promotion_decision_packet_v1"
PATCH_PREVIEW_VERSION = "inactive_promotion_patch_preview_v1"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from a fixture path."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_inactive_fixture_promotion_diff_ledger(
    decision_packet: dict[str, Any], patch_preview: dict[str, Any]
) -> dict[str, Any]:
    """Build a deterministic inactive fixture promotion diff ledger v1."""
    _require_version(decision_packet, DECISION_PACKET_VERSION, "decision packet")
    _require_version(patch_preview, PATCH_PREVIEW_VERSION, "patch preview")

    families = _family_index(decision_packet)
    files = sorted(
        patch_preview.get("files", []),
        key=lambda item: (str(item.get("fixture_family", "")), str(item.get("path", ""))),
    )

    file_summaries = [_file_summary(item, families) for item in files]
    readiness_rows = [_readiness_row(family_id, family, files) for family_id, family in families.items()]
    blocked = _blocked_explanations(readiness_rows, file_summaries)

    return {
        "ledger_version": LEDGER_VERSION,
        "generated_by": "ppd.inactive_fixture_promotion_diff_ledger",
        "source_packets": {
            "decision_packet_id": decision_packet.get("packet_id", ""),
            "decision_packet_version": decision_packet.get("packet_version", ""),
            "patch_preview_id": patch_preview.get("preview_id", ""),
            "patch_preview_version": patch_preview.get("preview_version", ""),
        },
        "file_level_diff_summaries": file_summaries,
        "fixture_family_readiness_rows": readiness_rows,
        "blocked_promotion_explanations": blocked,
        "reviewer_owner_assignments": _reviewer_owner_assignments(readiness_rows, file_summaries),
        "validation_command_inventory": _validation_inventory(decision_packet, patch_preview),
        "rollback_notes": _rollback_notes(readiness_rows, file_summaries),
        "safety_notes": [
            "Ledger is derived from inactive fixture decision and preview packets only.",
            "No active fixtures, release state, authenticated artifacts, or raw crawl outputs are modified.",
        ],
    }


def ledger_to_json(ledger: dict[str, Any]) -> str:
    """Serialize a ledger with stable key order and trailing newline."""
    return json.dumps(ledger, indent=2, sort_keys=True) + "\n"


def _require_version(packet: dict[str, Any], expected: str, label: str) -> None:
    actual = packet.get("packet_version") or packet.get("preview_version")
    if actual != expected:
        raise ValueError(f"unsupported {label} version: {actual!r}; expected {expected!r}")


def _family_index(decision_packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    families: dict[str, dict[str, Any]] = {}
    for family in decision_packet.get("fixture_families", []):
        family_id = str(family.get("fixture_family", ""))
        if not family_id:
            raise ValueError("fixture family rows must include fixture_family")
        families[family_id] = dict(family)
    return dict(sorted(families.items()))


def _file_summary(file_item: dict[str, Any], families: dict[str, dict[str, Any]]) -> dict[str, Any]:
    family_id = str(file_item.get("fixture_family", ""))
    family = families.get(family_id, {})
    added = int(file_item.get("added_lines", 0))
    removed = int(file_item.get("removed_lines", 0))
    changed = int(file_item.get("changed_lines", added + removed))
    blocked_reasons = [str(reason) for reason in file_item.get("blocked_reasons", [])]
    decision = str(family.get("decision", "unknown"))
    promotion_ready = decision == "promote" and not blocked_reasons

    return {
        "path": str(file_item.get("path", "")),
        "fixture_family": family_id,
        "change_type": str(file_item.get("change_type", "unknown")),
        "deterministic_diff_summary": str(file_item.get("summary", "")),
        "added_lines": added,
        "removed_lines": removed,
        "changed_lines": changed,
        "content_hash_before": str(file_item.get("content_hash_before", "")),
        "content_hash_after": str(file_item.get("content_hash_after", "")),
        "source_decision": decision,
        "promotion_ready": promotion_ready,
        "blocked_reasons": blocked_reasons,
    }


def _readiness_row(
    family_id: str, family: dict[str, Any], files: list[dict[str, Any]]
) -> dict[str, Any]:
    family_files = [item for item in files if item.get("fixture_family") == family_id]
    blocked_reasons = [str(reason) for reason in family.get("blocked_reasons", [])]
    for item in family_files:
        blocked_reasons.extend(str(reason) for reason in item.get("blocked_reasons", []))
    blocked_reasons = sorted(set(blocked_reasons))
    decision = str(family.get("decision", "unknown"))
    required_validations = sorted(str(value) for value in family.get("required_validations", []))
    passed_validations = sorted(str(value) for value in family.get("passed_validations", []))
    missing_validations = sorted(set(required_validations) - set(passed_validations))

    return {
        "fixture_family": family_id,
        "decision": decision,
        "readiness": "ready" if decision == "promote" and not blocked_reasons and not missing_validations else "blocked",
        "owner": str(family.get("owner", "unassigned")),
        "reviewer_role": str(family.get("reviewer_role", "ppd-reviewer")),
        "file_count": len(family_files),
        "required_validations": required_validations,
        "passed_validations": passed_validations,
        "missing_validations": missing_validations,
        "blocked_reasons": blocked_reasons,
        "decision_rationale": str(family.get("decision_rationale", "")),
    }


def _blocked_explanations(
    readiness_rows: list[dict[str, Any]], file_summaries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    explanations: list[dict[str, Any]] = []
    files_by_family: dict[str, list[str]] = {}
    for summary in file_summaries:
        files_by_family.setdefault(str(summary["fixture_family"]), []).append(str(summary["path"]))

    for row in readiness_rows:
        if row["readiness"] == "ready":
            continue
        reasons = list(row["blocked_reasons"]) + [
            f"missing validation: {item}" for item in row["missing_validations"]
        ]
        explanations.append(
            {
                "fixture_family": row["fixture_family"],
                "blocked_reasons": sorted(set(reasons)),
                "affected_files": sorted(files_by_family.get(str(row["fixture_family"]), [])),
                "review_next_step": "Resolve blocked reasons in inactive fixtures or decision packet before promotion.",
            }
        )
    return explanations


def _reviewer_owner_assignments(
    readiness_rows: list[dict[str, Any]], file_summaries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    files_by_family: dict[str, list[str]] = {}
    for summary in file_summaries:
        files_by_family.setdefault(str(summary["fixture_family"]), []).append(str(summary["path"]))

    assignments = []
    for row in readiness_rows:
        assignments.append(
            {
                "fixture_family": row["fixture_family"],
                "owner": row["owner"],
                "reviewer_role": row["reviewer_role"],
                "review_scope": "inactive fixture promotion readiness",
                "assigned_files": sorted(files_by_family.get(str(row["fixture_family"]), [])),
            }
        )
    return assignments


def _validation_inventory(
    decision_packet: dict[str, Any], patch_preview: dict[str, Any]
) -> list[dict[str, Any]]:
    commands: dict[str, dict[str, Any]] = {}
    for source_name, packet in (("decision_packet", decision_packet), ("patch_preview", patch_preview)):
        for item in packet.get("validation_commands", []):
            command = tuple(str(part) for part in item.get("command", []))
            if not command:
                continue
            key = "\u0000".join(command)
            commands[key] = {
                "command": list(command),
                "purpose": str(item.get("purpose", "validate inactive fixture promotion ledger inputs")),
                "source": source_name,
                "required_before_promotion": bool(item.get("required_before_promotion", True)),
            }
    return [commands[key] for key in sorted(commands)]


def _rollback_notes(
    readiness_rows: list[dict[str, Any]], file_summaries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    files_by_family: dict[str, list[str]] = {}
    for summary in file_summaries:
        files_by_family.setdefault(str(summary["fixture_family"]), []).append(str(summary["path"]))

    notes = []
    for row in readiness_rows:
        family_id = str(row["fixture_family"])
        if row["readiness"] == "ready":
            note = "If review fails, discard inactive candidate fixture replacements and keep active fixtures unchanged."
        else:
            note = "No promotion should occur while this family is blocked; active fixtures remain unchanged."
        notes.append(
            {
                "fixture_family": family_id,
                "rollback_note": note,
                "inactive_candidate_files": sorted(files_by_family.get(family_id, [])),
            }
        )
    return notes
