"""Fixture-first stale-source agent hold packet v1.

This module converts synthetic source-monitoring outcome rows into an
agent-facing hold packet. It is intentionally offline-only: it reads caller
provided rows, emits deterministic checks, and does not crawl, authenticate,
fill forms, upload, submit, activate releases, or mutate prompts, guardrails,
process models, requirements, contracts, sources, archives, documents, DevHub
surfaces, crawler state, release state, or daemon state.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PACKET_VERSION = "stale-source-agent-hold-packet-v1"

OFFLINE_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "-m", "py_compile", "ppd/agent_readiness/stale_source_agent_hold_packet_v1.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_stale_source_agent_hold_packet_v1.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

PROHIBITED_MUTATIONS: tuple[str, ...] = (
    "private_user_facts",
    "live_crawling",
    "devhub_access",
    "form_filling",
    "uploads",
    "submissions",
    "certifications",
    "payments",
    "scheduling",
    "release_activation",
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_process_model_mutation",
    "active_requirement_mutation",
    "active_contract_mutation",
    "active_source_mutation",
    "active_archive_mutation",
    "active_document_mutation",
    "active_devhub_surface_mutation",
    "active_crawler_mutation",
    "active_release_mutation",
    "daemon_state_mutation",
)

STALE_STATUSES = frozenset({"stale", "missing", "changed", "citation_gap", "unverified"})
BLOCKING_STATUSES = frozenset({"stale", "missing", "changed", "unverified"})
CITATION_STATUSES = frozenset({"stale", "missing", "changed", "citation_gap", "unverified"})
REVIEWER_STATUSES = frozenset({"stale", "missing", "changed", "citation_gap", "unverified", "reviewer_hold"})

SENSITIVE_KEYS = frozenset(
    {
        "user_name",
        "user_email",
        "email",
        "phone",
        "address",
        "applicant",
        "owner",
        "password",
        "token",
        "cookie",
        "session",
        "auth_state",
        "payment",
        "card",
        "ssn",
        "private_fact",
        "private_user_fact",
        "local_path",
        "screenshot",
        "trace",
        "har",
    }
)


@dataclass(frozen=True)
class MonitoringOutcomeRow:
    """Synthetic monitoring row used to build an offline hold packet."""

    row_id: str
    source_id: str
    canonical_url: str
    outcome: str
    severity: str
    observed_at: str
    affected_process_ids: tuple[str, ...]
    affected_requirement_ids: tuple[str, ...]
    affected_guardrail_bundle_ids: tuple[str, ...]
    affected_agent_checks: tuple[str, ...]
    citation_ids: tuple[str, ...]
    current_next_safe_action: str
    replacement_next_safe_action: str
    reviewer_note: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "MonitoringOutcomeRow":
        forbidden = sorted(key for key in row if _looks_sensitive(key))
        if forbidden:
            raise ValueError(f"monitoring row contains private or runtime-only keys: {forbidden}")

        return cls(
            row_id=_required_text(row, "row_id"),
            source_id=_required_text(row, "source_id"),
            canonical_url=_required_text(row, "canonical_url"),
            outcome=_required_text(row, "outcome"),
            severity=_required_text(row, "severity"),
            observed_at=_required_text(row, "observed_at"),
            affected_process_ids=_text_tuple(row, "affected_process_ids"),
            affected_requirement_ids=_text_tuple(row, "affected_requirement_ids"),
            affected_guardrail_bundle_ids=_text_tuple(row, "affected_guardrail_bundle_ids"),
            affected_agent_checks=_text_tuple(row, "affected_agent_checks"),
            citation_ids=_text_tuple(row, "citation_ids"),
            current_next_safe_action=_required_text(row, "current_next_safe_action"),
            replacement_next_safe_action=_required_text(row, "replacement_next_safe_action"),
            reviewer_note=_required_text(row, "reviewer_note"),
        )


def build_stale_source_agent_hold_packet(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Build an offline-only stale-source hold packet from synthetic rows."""

    normalized_rows = tuple(MonitoringOutcomeRow.from_mapping(row) for row in rows)

    missing_information_checks: list[dict[str, Any]] = []
    blocked_action_checks: list[dict[str, Any]] = []
    next_safe_action_changes: list[dict[str, Any]] = []
    citation_warnings: list[dict[str, Any]] = []
    reviewer_holds: list[dict[str, Any]] = []

    for row in normalized_rows:
        if row.outcome in STALE_STATUSES:
            missing_information_checks.extend(_missing_information_checks(row))
            next_safe_action_changes.append(_next_safe_action_change(row))

        if row.outcome in BLOCKING_STATUSES:
            blocked_action_checks.extend(_blocked_action_checks(row))

        if row.outcome in CITATION_STATUSES:
            citation_warnings.extend(_citation_warnings(row))

        if row.outcome in REVIEWER_STATUSES:
            reviewer_holds.append(_reviewer_hold(row))

    return {
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_offline_hold",
        "mutation_policy": "read_only_candidate_packet_only",
        "input_row_count": len(normalized_rows),
        "affected_source_ids": _sorted_unique(row.source_id for row in normalized_rows),
        "affected_process_ids": _sorted_unique(_flatten(row.affected_process_ids for row in normalized_rows)),
        "affected_requirement_ids": _sorted_unique(_flatten(row.affected_requirement_ids for row in normalized_rows)),
        "affected_guardrail_bundle_ids": _sorted_unique(_flatten(row.affected_guardrail_bundle_ids for row in normalized_rows)),
        "missing_information_checks": _sorted_dicts(missing_information_checks, "check_id"),
        "blocked_action_checks": _sorted_dicts(blocked_action_checks, "check_id"),
        "next_safe_action_changes": _sorted_dicts(next_safe_action_changes, "change_id"),
        "citation_warnings": _sorted_dicts(citation_warnings, "warning_id"),
        "reviewer_holds": _sorted_dicts(reviewer_holds, "hold_id"),
        "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
        "prohibited_mutations": list(PROHIBITED_MUTATIONS),
    }


def load_synthetic_monitoring_rows(path: Path) -> tuple[dict[str, Any], ...]:
    """Load fixture rows from JSON without resolving any live source."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    rows = payload.get("monitoring_outcomes")
    if not isinstance(rows, list):
        raise ValueError("fixture must contain monitoring_outcomes list")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("each monitoring outcome must be an object")
    return tuple(rows)


def build_packet_from_fixture(path: Path) -> dict[str, Any]:
    return build_stale_source_agent_hold_packet(load_synthetic_monitoring_rows(path))


def _missing_information_checks(row: MonitoringOutcomeRow) -> list[dict[str, Any]]:
    checks = row.affected_agent_checks or ("source_freshness",)
    return [
        {
            "check_id": f"missing-info::{row.row_id}::{check}",
            "source_id": row.source_id,
            "canonical_url": row.canonical_url,
            "outcome": row.outcome,
            "severity": row.severity,
            "agent_check": check,
            "reason": "source evidence is not fresh enough for agent-facing completeness decisions",
            "requires_private_user_fact": False,
            "allowed_resolution": "rerun offline fixture validation or send source update to human reviewer",
        }
        for check in checks
    ]


def _blocked_action_checks(row: MonitoringOutcomeRow) -> list[dict[str, Any]]:
    checks = row.affected_agent_checks or ("source_freshness",)
    return [
        {
            "check_id": f"blocked-action::{row.row_id}::{check}",
            "source_id": row.source_id,
            "outcome": row.outcome,
            "agent_check": check,
            "blocked_action_scope": "official_or_consequential_ppd_action",
            "blocked_actions": [
                "submit",
                "certify",
                "upload",
                "pay",
                "schedule",
                "cancel",
                "activate_release",
            ],
            "reason": "affected source must be reviewed before consequential action guidance is allowed",
        }
        for check in checks
    ]


def _next_safe_action_change(row: MonitoringOutcomeRow) -> dict[str, Any]:
    return {
        "change_id": f"next-safe-action::{row.row_id}",
        "source_id": row.source_id,
        "outcome": row.outcome,
        "from": row.current_next_safe_action,
        "to": row.replacement_next_safe_action,
        "allowed_action_class": "offline_review_only",
        "requires_live_crawl": False,
        "requires_devhub_access": False,
    }


def _citation_warnings(row: MonitoringOutcomeRow) -> list[dict[str, Any]]:
    citation_ids = row.citation_ids or (f"citation::{row.source_id}",)
    return [
        {
            "warning_id": f"citation-warning::{row.row_id}::{citation_id}",
            "source_id": row.source_id,
            "citation_id": citation_id,
            "canonical_url": row.canonical_url,
            "outcome": row.outcome,
            "message": "citation is affected by synthetic stale-source monitoring outcome",
            "agent_may_quote_as_current": False,
        }
        for citation_id in citation_ids
    ]


def _reviewer_hold(row: MonitoringOutcomeRow) -> dict[str, Any]:
    return {
        "hold_id": f"reviewer-hold::{row.row_id}",
        "source_id": row.source_id,
        "outcome": row.outcome,
        "severity": row.severity,
        "observed_at": row.observed_at,
        "reviewer_note": row.reviewer_note,
        "affected_process_ids": list(row.affected_process_ids),
        "affected_requirement_ids": list(row.affected_requirement_ids),
        "affected_guardrail_bundle_ids": list(row.affected_guardrail_bundle_ids),
        "allowed_disposition": ["confirm_fixture", "refresh_public_source_later", "keep_hold"],
    }


def _required_text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _text_tuple(row: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = row.get(key, ())
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{key} must be a list of strings")
    output = tuple(item for item in value if isinstance(item, str) and item.strip())
    if len(output) != len(value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return output


def _looks_sensitive(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in SENSITIVE_KEYS)


def _flatten(groups: Iterable[Iterable[str]]) -> tuple[str, ...]:
    return tuple(item for group in groups for item in group)


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def _sorted_dicts(values: Iterable[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    return sorted(values, key=lambda item: str(item[key]))
