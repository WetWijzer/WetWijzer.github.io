"""Fixture-first public refresh impact summary packet v3.

This module intentionally aggregates synthetic replay outcomes only. It does not
crawl, download, call processors, touch DevHub, or mutate release state.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PACKET_VERSION = "public-refresh-impact-summary-v3"

ROW_TYPES = (
    "source",
    "archive",
    "document",
    "requirement",
    "process_model",
    "guardrail",
    "agent_readiness",
    "reviewer_hold",
    "retry_backoff",
    "release_hold",
)

ROW_LABELS = {
    "source": "Affected public source summary",
    "archive": "Archive manifest summary",
    "document": "Normalized document summary",
    "requirement": "Requirement impact summary",
    "process_model": "Process model impact summary",
    "guardrail": "Guardrail impact summary",
    "agent_readiness": "Agent readiness summary",
    "reviewer_hold": "Reviewer hold summary",
    "retry_backoff": "Retry and backoff summary",
    "release_hold": "Release hold summary",
}

OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/public_refresh_impact_summary_v3.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_public_refresh_impact_summary_v3.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

MUTATION_BOUNDARIES = {
    "network_access": "forbidden",
    "raw_downloads": "forbidden",
    "processor_execution": "forbidden",
    "devhub_access": "forbidden",
    "active_crawler": "forbidden",
    "source_mutation": "forbidden",
    "archive_mutation": "forbidden",
    "document_mutation": "forbidden",
    "requirement_mutation": "forbidden",
    "process_model_mutation": "forbidden",
    "guardrail_mutation": "forbidden",
    "prompt_mutation": "forbidden",
    "contract_mutation": "forbidden",
    "devhub_surface_mutation": "forbidden",
    "release_state_mutation": "forbidden",
}

_ACTIVE_MUTATION_KEYS = {
    "active_crawl",
    "active_crawler",
    "active_mutation",
    "active_mutation_enabled",
    "active_promotion",
    "active_release_mutation",
    "active_source_mutation",
    "archive_mutation",
    "contract_mutation",
    "document_mutation",
    "guardrail_mutation",
    "mutates_active_artifacts",
    "process_model_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "requirement_mutation",
    "source_mutation",
}

_PRIVATE_ARTIFACT_KEY_RE = re.compile(
    r"(?:auth|browser|cookie|credential|download|har|private|raw|screenshot|session|storage_state|trace)",
    re.IGNORECASE,
)
_PRIVATE_ARTIFACT_TEXT_RE = re.compile(
    r"(?:/tmp/|/private/|\.auth/|auth_state|browser_state|cookies?\.json|downloaded[_ -]document|downloads?/|har[_ -]?file|raw[_ -]crawl|raw/body|session[_ -]state|storage_state|trace\.zip)",
    re.IGNORECASE,
)
_LIVE_CRAWL_CLAIM_RE = re.compile(
    r"(?:live\s+(?:crawl|crawler|network|processor|devhub|browser)\s+(?:completed|executed|performed|ran|succeeded)|(?:completed|executed|performed|ran)\s+(?:a\s+)?live\s+(?:crawl|crawler|network|processor|devhub|browser))",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"(?:guarantee[sd]?\s+(?:permit|approval|issuance|legal|compliance)|(?:permit|approval|issuance|legal|compliance)\s+(?:is\s+)?guarantee[sd]?)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReplayOutcome:
    """A synthetic replay outcome from a committed fixture."""

    outcome_id: str
    row_type: str
    status: str
    affected_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    notes: str

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ReplayOutcome":
        row_type = str(value["row_type"])
        if row_type not in ROW_TYPES:
            raise ValueError(f"unsupported row_type: {row_type}")

        affected_ids = tuple(str(item) for item in value.get("affected_ids", ()))
        evidence_ids = tuple(str(item) for item in value.get("evidence_ids", ()))
        if not affected_ids:
            raise ValueError(f"outcome {value.get('outcome_id')} must include affected_ids")

        return cls(
            outcome_id=str(value["outcome_id"]),
            row_type=row_type,
            status=str(value["status"]),
            affected_ids=affected_ids,
            evidence_ids=evidence_ids,
            notes=str(value.get("notes", "")),
        )


def load_replay_outcomes(path: Path) -> tuple[ReplayOutcome, ...]:
    """Load synthetic replay outcomes from a local fixture file."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    outcomes = payload.get("synthetic_replay_outcomes")
    if not isinstance(outcomes, list):
        raise ValueError("fixture must contain synthetic_replay_outcomes list")
    return tuple(ReplayOutcome.from_mapping(item) for item in outcomes)


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def build_public_refresh_impact_summary_v3(
    outcomes: Iterable[ReplayOutcome],
    *,
    fixture_name: str,
) -> dict[str, Any]:
    """Aggregate synthetic public refresh replay outcomes into packet v3 rows."""

    grouped: dict[str, list[ReplayOutcome]] = defaultdict(list)
    for outcome in outcomes:
        grouped[outcome.row_type].append(outcome)

    rows: list[dict[str, Any]] = []
    for row_type in ROW_TYPES:
        row_outcomes = grouped.get(row_type, [])
        affected_ids = _sorted_unique(
            affected_id
            for outcome in row_outcomes
            for affected_id in outcome.affected_ids
        )
        evidence_ids = _sorted_unique(
            evidence_id
            for outcome in row_outcomes
            for evidence_id in outcome.evidence_ids
        )
        outcome_counts = dict(sorted(Counter(outcome.status for outcome in row_outcomes).items()))
        rows.append(
            {
                "row_type": row_type,
                "label": ROW_LABELS[row_type],
                "affected_count": len(affected_ids),
                "outcome_counts": outcome_counts,
                "affected_ids": affected_ids,
                "evidence_ids": evidence_ids,
                "validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
                "notes": [outcome.notes for outcome in row_outcomes if outcome.notes],
            }
        )

    totals = {
        "row_count": len(rows),
        "synthetic_outcome_count": sum(len(items) for items in grouped.values()),
        "affected_id_count": sum(row["affected_count"] for row in rows),
        "rows_with_holds": sum(
            1
            for row in rows
            if row["outcome_counts"].get("held", 0) or row["outcome_counts"].get("blocked", 0)
        ),
    }

    packet = {
        "packet_version": PACKET_VERSION,
        "fixture_name": fixture_name,
        "generated_from": "committed synthetic public refresh replay fixture",
        "offline_only": True,
        "mutation_boundaries": MUTATION_BOUNDARIES,
        "validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
        "totals": totals,
        "rows": rows,
    }
    require_valid_public_refresh_impact_summary_v3(packet)
    return packet


def build_packet_from_fixture(path: Path) -> dict[str, Any]:
    return build_public_refresh_impact_summary_v3(
        load_replay_outcomes(path),
        fixture_name=path.name,
    )


def validate_public_refresh_impact_summary_v3(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a public refresh impact summary v3 packet."""

    errors: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be public-refresh-impact-summary-v3")
    if packet.get("offline_only") is not True:
        errors.append("offline_only must be true")

    _validate_validation_commands(packet.get("validation_commands"), "validation_commands", errors)
    _validate_mutation_boundaries(packet.get("mutation_boundaries"), errors)
    _validate_rows(packet.get("rows"), errors)
    _scan_forbidden_values(packet, "$", errors)
    return errors


def require_valid_public_refresh_impact_summary_v3(packet: Mapping[str, Any]) -> None:
    errors = validate_public_refresh_impact_summary_v3(packet)
    if errors:
        raise ValueError("invalid public refresh impact summary v3: " + "; ".join(errors))


def _validate_validation_commands(value: Any, path: str, errors: list[str]) -> None:
    expected = [list(command) for command in OFFLINE_VALIDATION_COMMANDS]
    if value != expected:
        errors.append(f"{path} must include exact offline validation commands")


def _validate_mutation_boundaries(value: Any, errors: list[str]) -> None:
    if value != MUTATION_BOUNDARIES:
        errors.append("mutation_boundaries must match forbidden offline-only boundaries")
        return
    if any(status != "forbidden" for status in value.values()):
        errors.append("mutation_boundaries must forbid all live access and active mutations")


def _validate_rows(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("rows must be a list")
        return

    rows_by_type: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(value):
        path = f"rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        row_type = row.get("row_type")
        if row_type not in ROW_TYPES:
            errors.append(f"{path}.row_type must be one of the required summary row types")
            continue
        if row_type in rows_by_type:
            errors.append(f"duplicate {row_type} row is not allowed")
        rows_by_type[str(row_type)] = row
        _validate_row(str(row_type), row, path, errors)

    for row_type in ROW_TYPES:
        if row_type not in rows_by_type:
            errors.append(f"missing required {row_type} row")


def _validate_row(row_type: str, row: Mapping[str, Any], path: str, errors: list[str]) -> None:
    if row.get("label") != ROW_LABELS[row_type]:
        errors.append(f"{path}.label must match the required row label")
    _validate_non_empty_string_list(row.get("affected_ids"), f"{path}.affected_ids", errors)
    _validate_non_empty_string_list(row.get("evidence_ids"), f"{path}.evidence_ids", errors)
    affected_ids = row.get("affected_ids")
    if isinstance(affected_ids, list) and row.get("affected_count") != len(set(affected_ids)):
        errors.append(f"{path}.affected_count must match unique affected_ids count")
    outcome_counts = row.get("outcome_counts")
    if not isinstance(outcome_counts, Mapping) or not outcome_counts:
        errors.append(f"{path}.outcome_counts must include at least one outcome")
    _validate_validation_commands(row.get("validation_commands"), f"{path}.validation_commands", errors)


def _validate_non_empty_string_list(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{path} must include at least one value")
        return
    if any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{path} must contain non-empty strings")


def _scan_forbidden_values(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if _is_active_mutation_flag(key_text, child):
                errors.append(f"active mutation flag is not allowed at {child_path}")
            if _is_private_artifact_field(key_text, child):
                errors.append(f"private/session/browser/raw/downloaded artifact is not allowed at {child_path}")
            _scan_forbidden_values(child, child_path, errors)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden_values(child, f"{path}[{index}]", errors)
        return

    if isinstance(value, str):
        _scan_forbidden_text(value, path, errors)


def _is_active_mutation_flag(key: str, value: Any) -> bool:
    normalized = key.strip().lower().replace("-", "_")
    return normalized in _ACTIVE_MUTATION_KEYS and value not in (False, None, "", "forbidden")


def _is_private_artifact_field(key: str, value: Any) -> bool:
    if not _PRIVATE_ARTIFACT_KEY_RE.search(key):
        return False
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, str) and value.lower() in {"forbidden", "not_stored", "not stored", "none"}:
        return False
    return True


def _scan_forbidden_text(text: str, path: str, errors: list[str]) -> None:
    if _PRIVATE_ARTIFACT_TEXT_RE.search(text):
        errors.append(f"private/session/browser/raw/downloaded artifact reference is not allowed at {path}")
    if _LIVE_CRAWL_CLAIM_RE.search(text):
        errors.append(f"live crawl or live automation claim is not allowed at {path}")
    if _GUARANTEE_RE.search(text):
        errors.append(f"legal or permitting guarantee is not allowed at {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="Path to synthetic replay outcome fixture JSON")
    args = parser.parse_args()
    packet = build_packet_from_fixture(args.fixture)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
