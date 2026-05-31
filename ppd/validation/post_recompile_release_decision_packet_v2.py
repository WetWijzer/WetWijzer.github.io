"""Fixture-first post-recompile release decision packet v2 validation.

The packet is an offline decision artifact. It consumes approved
post-recompile agent readiness replay v2 evidence and produces ordered release
review rows, hold outcomes, reviewer placeholders, rollback references, and
blocked-action reminders. It does not activate guardrails, mutate prompts, open
DevHub, crawl live sources, or perform official actions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

PACKET_VERSION = "post-recompile-release-decision-packet-v2"
SOURCE_REPLAY_VERSION = "post-recompile-agent-readiness-replay-v2"

EXACT_OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/validation/post_recompile_release_decision_packet_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_post_recompile_release_decision_packet_v2"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

REQUIRED_REPLAY_CASE_TYPES = frozenset(
    {
        "replay_case",
        "stale_source_hold_resolution_placeholder",
        "caution_template_check",
        "next_safe_action_summary",
        "refused_consequential_action_example",
        "reviewer_disposition",
    }
)

REQUIRED_PACKET_FLAGS = frozenset(
    {
        "fixture_first",
        "offline_only",
        "inactive_only",
        "no_guardrail_activation",
        "no_prompt_changes",
        "no_devhub_opened",
        "no_live_source_crawl",
        "no_official_actions",
    }
)

FORBIDDEN_TRUE_FLAG_KEYS = frozenset(
    {
        "guardrail_activation",
        "active_guardrail_mutation",
        "prompt_mutation",
        "active_prompt_mutation",
        "devhub_opened",
        "live_source_crawl",
        "official_action_performed",
        "release_state_activated",
    }
)

FORBIDDEN_TEXT_MARKERS = (
    "executed in devhub",
    "opened devhub",
    "live crawl completed",
    "official action completed",
    "release activated",
    "guardrails activated",
    "prompts changed",
    "permit guaranteed",
)

FORBIDDEN_ARTIFACT_MARKERS = (
    "/private/",
    "private/",
    "/session/",
    "session/",
    "/browser/",
    "browser/",
    "/raw/",
    "raw/",
    "/downloaded/",
    "downloaded/",
    "auth_state",
    "storage_state",
    "trace.zip",
    ".har",
)


def build_packet_from_replay(replay: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic inactive decision packet from approved replay evidence."""

    replay_errors = _validate_source_replay(replay)
    if replay_errors:
        raise ValueError("source replay is not approved release evidence: " + "; ".join(replay_errors))

    replay_cases = [case for case in replay.get("replay_cases", []) if isinstance(case, Mapping)]
    decision_rows: list[dict[str, Any]] = []
    for index, case in enumerate(replay_cases, start=1):
        case_type = str(case.get("type", ""))
        row_id = f"release-decision-row-{index:03d}"
        hold_required = case_type in {
            "stale_source_hold_resolution_placeholder",
            "refused_consequential_action_example",
            "reviewer_disposition",
        }
        decision_rows.append(
            {
                "sequence": index,
                "row_id": row_id,
                "source_replay_case_id": str(case.get("id", row_id)),
                "source_replay_case_type": case_type,
                "release_decision": "hold-inactive" if hold_required else "ready-for-review",
                "decision_basis": str(case.get("summary", "offline replay evidence row")),
                "stale_source_hold_outcome": "manual-source-review-required" if case_type == "stale_source_hold_resolution_placeholder" else "not-applicable",
                "inactive_to_active_eligibility_note": "Eligible only after stale-source holds are resolved, reviewer signoff is completed, rollback references are accepted, and a separate operator release decision is made.",
                "blocked_consequential_action_reminder": "Do not upload, submit, certify, pay, schedule, cancel, or make official changes from this packet.",
                "rollback_reference_id": f"rollback-reference-{index:03d}",
                "reviewer_signoff_placeholder_id": f"reviewer-signoff-{index:03d}",
            }
        )

    return {
        "version": PACKET_VERSION,
        "source_replay": {
            "version": SOURCE_REPLAY_VERSION,
            "approved_evidence": True,
            "replay_case_count": len(replay_cases),
        },
        "fixture_first": True,
        "offline_only": True,
        "inactive_only": True,
        "no_guardrail_activation": True,
        "no_prompt_changes": True,
        "no_devhub_opened": True,
        "no_live_source_crawl": True,
        "no_official_actions": True,
        "decision_rows": decision_rows,
        "stale_source_hold_outcomes": [
            {
                "source_replay_case_id": row["source_replay_case_id"],
                "row_id": row["row_id"],
                "outcome": row["stale_source_hold_outcome"],
            }
            for row in decision_rows
            if row["stale_source_hold_outcome"] != "not-applicable"
        ],
        "reviewer_signoff_placeholders": [
            {
                "placeholder_id": row["reviewer_signoff_placeholder_id"],
                "row_id": row["row_id"],
                "status": "pending-human-review",
                "reviewer": "",
                "signed_at": "",
                "notes": "",
            }
            for row in decision_rows
        ],
        "rollback_references": [
            {
                "rollback_reference_id": row["rollback_reference_id"],
                "row_id": row["row_id"],
                "reference": "Use the prior inactive fixture state and do not mutate active release state from this packet.",
            }
            for row in decision_rows
        ],
        "inactive_to_active_eligibility_notes": [
            {
                "row_id": row["row_id"],
                "note": row["inactive_to_active_eligibility_note"],
            }
            for row in decision_rows
        ],
        "blocked_consequential_action_reminders": [
            {
                "row_id": row["row_id"],
                "reminder": row["blocked_consequential_action_reminder"],
            }
            for row in decision_rows
        ],
        "offline_validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
    }


def validate_packet(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("version") != PACKET_VERSION:
        errors.append(f"version must be {PACKET_VERSION}")

    for flag in sorted(REQUIRED_PACKET_FLAGS):
        if packet.get(flag) is not True:
            errors.append(f"{flag} must be true")

    source_replay = packet.get("source_replay")
    if not isinstance(source_replay, Mapping):
        errors.append("source_replay must be an object")
    else:
        if source_replay.get("version") != SOURCE_REPLAY_VERSION:
            errors.append(f"source_replay.version must be {SOURCE_REPLAY_VERSION}")
        if source_replay.get("approved_evidence") is not True:
            errors.append("source_replay.approved_evidence must be true")

    rows = packet.get("decision_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("decision_rows must contain ordered release decision rows")
        rows = []

    seen_row_ids: set[str] = set()
    expected_sequence = 1
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("decision_rows must contain objects")
            continue
        row_id = str(row.get("row_id", ""))
        if row.get("sequence") != expected_sequence:
            errors.append(f"decision row {row_id or expected_sequence} sequence must be {expected_sequence}")
        expected_sequence += 1
        if not row_id:
            errors.append("decision row row_id is required")
        elif row_id in seen_row_ids:
            errors.append(f"duplicate decision row id: {row_id}")
        seen_row_ids.add(row_id)
        if row.get("release_decision") not in {"ready-for-review", "hold-inactive"}:
            errors.append(f"{row_id}.release_decision must be ready-for-review or hold-inactive")
        for key in (
            "source_replay_case_id",
            "source_replay_case_type",
            "decision_basis",
            "stale_source_hold_outcome",
            "reviewer_signoff_placeholder_id",
            "rollback_reference_id",
            "inactive_to_active_eligibility_note",
            "blocked_consequential_action_reminder",
        ):
            if not str(row.get(key, "")):
                errors.append(f"{row_id}.{key} is required")

    _validate_rows_cover_references(packet, "stale_source_hold_outcomes", seen_row_ids, errors)
    _validate_rows_cover_references(packet, "reviewer_signoff_placeholders", seen_row_ids, errors)
    _validate_rows_cover_references(packet, "rollback_references", seen_row_ids, errors)
    _validate_rows_cover_references(packet, "inactive_to_active_eligibility_notes", seen_row_ids, errors)
    _validate_rows_cover_references(packet, "blocked_consequential_action_reminders", seen_row_ids, errors)

    if packet.get("offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands must exactly match release decision packet v2 commands")
    if packet.get("validation_commands") != [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]:
        errors.append("validation_commands must contain only the PP&D daemon self-test command")

    for path, value in _walk(packet):
        key = path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_TRUE_FLAG_KEYS and value is True:
            errors.append(f"forbidden active flag at {path}")
        if isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in FORBIDDEN_TEXT_MARKERS):
                errors.append(f"forbidden live or official-action claim at {path}")
            if any(marker in lowered for marker in FORBIDDEN_ARTIFACT_MARKERS):
                errors.append(f"forbidden private, browser, raw, or downloaded artifact at {path}")

    return sorted(set(errors))


def _validate_source_replay(replay: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if replay.get("version") != SOURCE_REPLAY_VERSION:
        errors.append(f"source replay version must be {SOURCE_REPLAY_VERSION}")
    cases = replay.get("replay_cases")
    if not isinstance(cases, list) or not cases:
        errors.append("source replay must contain replay_cases")
        return errors
    seen_types = {str(case.get("type")) for case in cases if isinstance(case, Mapping)}
    for case_type in sorted(REQUIRED_REPLAY_CASE_TYPES - seen_types):
        errors.append(f"source replay missing case type: {case_type}")
    if replay.get("validation_commands") != [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]:
        errors.append("source replay validation command must be the PP&D daemon self-test")
    return errors


def _validate_rows_cover_references(packet: Mapping[str, Any], field: str, row_ids: set[str], errors: list[str]) -> None:
    value = packet.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"{field}[{index}] must be an object")
            continue
        row_id = str(item.get("row_id", ""))
        if row_id not in row_ids:
            errors.append(f"{field}[{index}].row_id must reference a decision row")


def _walk(value: Any, path: str = "$.") -> list[tuple[str, Any]]:
    current_path = "$" if path == "$" else path.rstrip(".")
    items: list[tuple[str, Any]] = [(current_path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            items.extend(_walk(child, f"{current_path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{current_path}[{index}]"))
    return items
