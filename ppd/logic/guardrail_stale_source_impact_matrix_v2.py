"""Fixture-first stale-source impact matrix v2 for PP&D guardrail bundles.

This module consumes the public source freshness review packet v2 shape and emits
synthetic reviewer rows only. It does not crawl sources, open DevHub, change
prompts, modify active guardrail bundles, or perform official actions.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PACKET_VERSION = "guardrail-stale-source-impact-matrix-v2"
SOURCE_PACKET_VERSION = "public-source-freshness-review-packet-v2"

_FALSE_FLAGS = (
    "live_crawl_performed",
    "recrawl_performed",
    "devhub_opened",
    "devhub_automation_performed",
    "official_action_performed",
    "active_guardrail_bundles_mutated",
    "active_guardrails_mutated",
    "active_prompts_mutated",
    "active_release_state_mutated",
    "legal_or_permitting_guarantees_made",
)

_FORBIDDEN_KEYS = {
    "raw_body",
    "response_body",
    "downloaded_body",
    "downloaded_document",
    "raw_crawl_output",
    "crawl_output",
    "browser_trace",
    "trace",
    "screenshot",
    "credential",
    "password",
    "token",
    "session_cookie",
    "payment_data",
}


@dataclass(frozen=True)
class GuardrailStaleSourceImpactMatrixV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json_fixture(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_guardrail_stale_source_impact_matrix_v2(public_source_freshness_review_packet_v2: Mapping[str, Any] | str | Path) -> dict[str, Any]:
    """Build an offline synthetic impact matrix from a freshness review packet."""

    source_packet = _load_packet(public_source_freshness_review_packet_v2)
    rows = _freshness_rows(source_packet)
    ordered_rows = [_build_matrix_row(row, index + 1) for index, row in enumerate(rows)]

    matrix = {
        "packet_version": PACKET_VERSION,
        "source_packet_version": source_packet.get("packet_version", SOURCE_PACKET_VERSION),
        "generation_mode": "fixture_first_offline_synthetic_guardrail_impact_matrix",
        "consumed_public_source_freshness_review_packet_v2": True,
        "live_crawl_performed": False,
        "recrawl_performed": False,
        "devhub_opened": False,
        "devhub_automation_performed": False,
        "official_action_performed": False,
        "active_guardrail_bundles_mutated": False,
        "active_guardrails_mutated": False,
        "active_prompts_mutated": False,
        "active_release_state_mutated": False,
        "legal_or_permitting_guarantees_made": False,
        "ordered_synthetic_guardrail_impact_rows": ordered_rows,
        "stale_source_hold_reasons": _hold_reasons(ordered_rows),
        "required_re_extraction_placeholders": _re_extraction_placeholders(ordered_rows),
        "user_facing_caution_templates": _caution_templates(),
        "blocked_action_reminders": _blocked_action_reminders(),
        "reviewer_disposition_placeholders": _reviewer_disposition_placeholders(ordered_rows),
        "offline_validation_commands": offline_validation_commands(),
    }
    require_valid_guardrail_stale_source_impact_matrix_v2(matrix)
    return matrix


def validate_guardrail_stale_source_impact_matrix_v2(packet: Mapping[str, Any]) -> GuardrailStaleSourceImpactMatrixV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return GuardrailStaleSourceImpactMatrixV2ValidationResult(False, ("packet must be a JSON object",))

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be guardrail-stale-source-impact-matrix-v2")

    _collect_forbidden(packet, "packet", errors)
    for flag in _FALSE_FLAGS:
        if _truthy(packet.get(flag)):
            errors.append(f"{flag} must be absent or false")

    rows = packet.get("ordered_synthetic_guardrail_impact_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("ordered_synthetic_guardrail_impact_rows must include at least one guardrail row")
        rows = []

    for index, row in enumerate(rows):
        path = f"ordered_synthetic_guardrail_impact_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be a JSON object")
            continue
        _validate_row(row, path, errors)
        _collect_forbidden(row, path, errors)

    required_sections = (
        "stale_source_hold_reasons",
        "required_re_extraction_placeholders",
        "user_facing_caution_templates",
        "blocked_action_reminders",
        "reviewer_disposition_placeholders",
        "offline_validation_commands",
    )
    for key in required_sections:
        if not _non_empty_list(packet.get(key)):
            errors.append(f"{key} must be a non-empty list")

    if not _valid_commands(packet.get("offline_validation_commands")):
        errors.append("offline_validation_commands must include exact offline validation commands")

    return GuardrailStaleSourceImpactMatrixV2ValidationResult(not errors, tuple(errors))


def require_valid_guardrail_stale_source_impact_matrix_v2(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_stale_source_impact_matrix_v2(packet)
    if not result.ok:
        raise ValueError("invalid guardrail stale source impact matrix v2: " + "; ".join(result.errors))


def offline_validation_commands() -> list[list[str]]:
    return [
        ["python3", "-m", "py_compile", "ppd/logic/guardrail_stale_source_impact_matrix_v2.py"],
        ["python3", "-m", "unittest", "ppd.tests.test_guardrail_stale_source_impact_matrix_v2"],
        ["python3", "-m", "unittest", "ppd.tests.test_public_source_freshness_review_v2"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def _load_packet(value: Mapping[str, Any] | str | Path) -> Mapping[str, Any]:
    if isinstance(value, (str, Path)):
        loaded = load_json_fixture(value)
    else:
        loaded = value
    if not isinstance(loaded, Mapping):
        raise ValueError("public source freshness review packet v2 must be a JSON object")
    _collect_forbidden_or_raise(loaded)
    return loaded


def _freshness_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = packet.get("ordered_synthetic_freshness_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("public source freshness review packet v2 must include ordered_synthetic_freshness_rows")
    parsed: list[Mapping[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("freshness rows must be JSON objects")
        parsed.append(row)
    return parsed


def _build_matrix_row(row: Mapping[str, Any], ordinal: int) -> dict[str, Any]:
    source_id = str(row.get("source_id") or f"source-{ordinal}")
    stale = _is_stale_or_placeholder(row)
    guardrail_id = _guardrail_bundle_id(row, source_id)
    impact_status = "synthetic_impacted_guardrail_hold" if stale else "synthetic_unimpacted_guardrail_monitor"
    hold_reason = (
        "stale_source_review_pending_required_re_extraction"
        if stale
        else "source_fixture_current_no_guardrail_hold_from_stale_source_matrix"
    )
    return {
        "row_order": ordinal,
        "source_id": source_id,
        "canonical_url": str(row.get("canonical_url") or "PLACEHOLDER_CANONICAL_URL"),
        "official_anchor_id": str(row.get("official_anchor_id") or "PLACEHOLDER_OFFICIAL_ANCHOR_ID"),
        "synthetic_guardrail_bundle_id": guardrail_id,
        "impact_status": impact_status,
        "is_impacted_by_stale_source": stale,
        "is_unimpacted_by_stale_source": not stale,
        "stale_source_hold_reason": hold_reason,
        "required_re_extraction_placeholder": {
            "status": "PLACEHOLDER_RE_EXTRACTION_REQUIRED_BEFORE_GUARDRAIL_USE" if stale else "PLACEHOLDER_NO_RE_EXTRACTION_REQUIRED_FOR_THIS_ROW",
            "source_id": source_id,
            "replacement_evidence_packet": "PLACEHOLDER_PUBLIC_SOURCE_RE_EXTRACTION_PACKET_V2",
            "reviewer_confirmation": "PLACEHOLDER_REVIEWER_CONFIRMATION_PENDING",
        },
        "user_facing_caution_template": "This guardrail references public source material that is pending freshness review; do not present it as current Portland PP&D guidance until reviewer disposition is complete." if stale else "This guardrail row has no stale-source hold in this offline matrix; continue to cite the underlying source date and reviewer status.",
        "blocked_action_reminder": "Do not recrawl sources, open DevHub, update active guardrail bundles, change prompts, or perform official actions from this matrix.",
        "reviewer_disposition_placeholder": {
            "status": "PLACEHOLDER_REVIEWER_DISPOSITION_PENDING",
            "reviewer": "PLACEHOLDER_REVIEWER",
            "reviewed_at": "PLACEHOLDER_REVIEWED_AT",
            "decision": "PLACEHOLDER_HOLD_RELEASE_OR_REEXTRACT_DECISION",
            "notes": "PLACEHOLDER_REVIEW_NOTES",
        },
        "offline_validation_commands": offline_validation_commands(),
    }


def _guardrail_bundle_id(row: Mapping[str, Any], source_id: str) -> str:
    values = row.get("affected_guardrail_bundle_placeholders") or row.get("affected_guardrail_bundle_ids")
    if isinstance(values, list):
        for value in values:
            if isinstance(value, str) and value and not value.startswith("PLACEHOLDER_"):
                return value
    return "synthetic-guardrail-bundle-for-" + source_id.replace("_", "-")


def _is_stale_or_placeholder(row: Mapping[str, Any]) -> bool:
    text_values = [
        row.get("registry_freshness_status"),
        row.get("last_seen_placeholder"),
        row.get("current_content_hash"),
    ]
    hash_change = row.get("hash_change_placeholder")
    if isinstance(hash_change, Mapping):
        text_values.extend(hash_change.values())
    combined = " ".join(str(value).lower() for value in text_values if value is not None)
    return any(marker in combined for marker in ("stale", "placeholder", "pending", "missing"))


def _hold_reasons(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source_id": row["source_id"],
            "synthetic_guardrail_bundle_id": row["synthetic_guardrail_bundle_id"],
            "hold_reason": row["stale_source_hold_reason"],
        }
        for row in rows
        if row.get("is_impacted_by_stale_source")
    ] or [
        {
            "source_id": "none",
            "synthetic_guardrail_bundle_id": "none",
            "hold_reason": "no_stale_source_holds_detected_in_fixture_matrix",
        }
    ]


def _re_extraction_placeholders(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [row["required_re_extraction_placeholder"] for row in rows]


def _caution_templates() -> list[dict[str, str]]:
    return [
        {
            "template_id": "stale_source_guardrail_caution",
            "template": "Public source freshness is unresolved for this guardrail. Treat the row as review-only until re-extraction and reviewer disposition are complete.",
        },
        {
            "template_id": "unimpacted_guardrail_citation_caution",
            "template": "No stale-source hold is recorded for this row in the offline matrix. Continue to show source date and reviewer status.",
        },
    ]


def _blocked_action_reminders() -> list[str]:
    return [
        "Do not recrawl sources from this packet.",
        "Do not open DevHub or automate authenticated workflows.",
        "Do not mutate active guardrail bundles, prompts, source registries, contracts, or release state.",
        "Do not represent this offline packet as legal, permitting, or official PP&D action.",
    ]


def _reviewer_disposition_placeholders(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [row["reviewer_disposition_placeholder"] | {"source_id": row["source_id"]} for row in rows]


def _validate_row(row: Mapping[str, Any], path: str, errors: list[str]) -> None:
    required = (
        "row_order",
        "source_id",
        "canonical_url",
        "synthetic_guardrail_bundle_id",
        "impact_status",
        "stale_source_hold_reason",
        "required_re_extraction_placeholder",
        "user_facing_caution_template",
        "blocked_action_reminder",
        "reviewer_disposition_placeholder",
        "offline_validation_commands",
    )
    for key in required:
        if key not in row or row.get(key) in (None, "", []):
            errors.append(f"{path}.{key} is required")
    if row.get("is_impacted_by_stale_source") is row.get("is_unimpacted_by_stale_source"):
        errors.append(f"{path} must be exactly one of impacted or unimpacted")
    if not isinstance(row.get("required_re_extraction_placeholder"), Mapping):
        errors.append(f"{path}.required_re_extraction_placeholder must be an object")
    if not isinstance(row.get("reviewer_disposition_placeholder"), Mapping):
        errors.append(f"{path}.reviewer_disposition_placeholder must be an object")
    if not _valid_commands(row.get("offline_validation_commands")):
        errors.append(f"{path}.offline_validation_commands must include exact offline validation commands")


def _collect_forbidden_or_raise(value: Any) -> None:
    errors: list[str] = []
    _collect_forbidden(value, "packet", errors)
    if errors:
        raise ValueError("; ".join(errors))


def _collect_forbidden(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in _FORBIDDEN_KEYS:
                errors.append(f"{path}.{key} is a forbidden private/raw/browser artifact field")
            if lowered in _FALSE_FLAGS and _truthy(nested):
                errors.append(f"{path}.{key} must be absent or false")
            _collect_forbidden(nested, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_forbidden(item, f"{path}[{index}]", errors)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "none", "null"}
    return bool(value)


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _valid_commands(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(command, list)
        and bool(command)
        and all(isinstance(part, str) and part for part in command)
        for command in value
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build PP&D guardrail stale-source impact matrix v2 from a freshness packet fixture.")
    parser.add_argument("public_source_freshness_review_packet_v2", type=Path)
    args = parser.parse_args(argv)
    packet = build_guardrail_stale_source_impact_matrix_v2(args.public_source_freshness_review_packet_v2)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
