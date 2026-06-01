"""Fixture-first requirement re-extraction delta queue v4.

This module validates offline PP&D requirement re-extraction delta queue
packets before any active requirement, process, or guardrail state can be
updated. It accepts committed synthetic fixtures only and rejects raw crawl
bodies, private/session/auth artifacts, live crawl/OCR completion claims,
legal or permitting guarantees, and active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

QUEUE_VERSION = "public-refresh-requirement-reextraction-delta-queue-v4"
MODE = "fixture_first_offline_delta_review_only"

EXPECTED_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "-m", "py_compile", "ppd/agent_readiness/public_refresh_requirement_reextraction_delta_queue_v4.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_public_refresh_requirement_reextraction_delta_queue_v4.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

ALLOWED_REQUIREMENT_TYPES = frozenset(
    {
        "obligation",
        "prohibition",
        "permission",
        "precondition",
        "exception",
        "deadline",
        "fee_trigger",
        "license_requirement",
        "document_requirement",
        "action_gate",
    }
)

ALLOWED_PROCESS_STAGES = frozenset(
    {
        "pre-application research",
        "account setup or manual login",
        "property lookup",
        "permit type selection",
        "eligibility screening",
        "document preparation",
        "application data entry",
        "upload staging",
        "acknowledgement/certification review",
        "submission",
        "prescreen/intake",
        "fee payment",
        "plan review",
        "corrections/checksheets",
        "approval/issuance",
        "inspections",
        "closeout, cancellation, expiration, extension, or reactivation",
    }
)

ALLOWED_HUMAN_REVIEW_STATUSES = frozenset(
    {
        "needs_human_review",
        "blocked_by_stale_source",
        "blocked_by_conflicting_evidence",
        "ready_for_reviewer_triage",
    }
)

ALLOWED_SKIPPED_SOURCE_REASONS = frozenset(
    {
        "outside_allowlist",
        "unsupported_scheme",
        "private_or_authenticated",
        "disallowed_by_robots_or_policy",
        "raw_download_not_permitted",
        "too_large",
        "unsupported_content_type",
        "not_skipped_fixture_source",
    }
)

ALLOWED_REVIEWER_HOLDS = frozenset(
    {
        "hold_until_freshness_packet_reviewed",
        "hold_until_source_evidence_placeholder_resolved",
        "hold_until_expected_requirement_type_confirmed",
        "hold_until_process_stage_confirmed",
        "hold_until_skipped_source_reason_reviewed",
        "hold_until_reviewer_approval",
    }
)

REQUIRED_FALSE_FLAGS = (
    "active_mutation",
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_guardrail_mutation",
    "live_crawl",
    "live_extraction",
    "ocr_completed",
    "raw_public_body_artifact",
    "private_artifact",
    "session_artifact",
    "auth_artifact",
    "legal_or_permitting_guarantee",
)

PROHIBITED_KEYS = frozenset(
    {
        "access_token",
        "auth_artifact",
        "auth_state",
        "browser_trace",
        "cookie",
        "credential",
        "devhub_session",
        "html_body",
        "local_private_path",
        "password",
        "private_artifact",
        "public_body",
        "raw_body",
        "raw_crawl_output",
        "raw_html",
        "raw_public_body",
        "raw_public_body_artifact",
        "raw_text",
        "session_artifact",
        "session_state",
        "screenshot",
        "trace",
    }
)

PROHIBITED_PHRASES = frozenset(
    {
        "active guardrail mutation",
        "active process model mutation",
        "active requirement mutation",
        "guaranteed approval",
        "guaranteed permit",
        "legal advice",
        "live crawl completed",
        "live crawl succeeded",
        "ocr completed",
        "ocr completion confirmed",
        "permit guaranteed",
        "raw public body stored",
    }
)


@dataclass(frozen=True)
class RequirementReextractionDeltaRowV4:
    row_id: str
    freshness_packet_refs: tuple[str, ...]
    source_evidence_placeholders: tuple[str, ...]
    expected_requirement_types: tuple[str, ...]
    affected_process_stages: tuple[str, ...]
    human_review_status: str
    skipped_source_reasons: tuple[str, ...]
    reviewer_holds: tuple[str, ...]
    validation_commands: tuple[tuple[str, ...], ...]
    candidate_requirement_id: str
    candidate_summary: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "RequirementReextractionDeltaRowV4":
        _reject_prohibited_content(row)
        if row.get("requirement_reextraction_delta_queue_v4_row") is not True:
            raise ValueError("row must declare requirement_reextraction_delta_queue_v4_row true")
        for flag in REQUIRED_FALSE_FLAGS:
            if row.get(flag) is not False:
                raise ValueError(f"row must declare {flag} false")

        requirement_types = _required_allowed_tuple(row, "expected_requirement_types", ALLOWED_REQUIREMENT_TYPES)
        process_stages = _required_allowed_tuple(row, "affected_process_stages", ALLOWED_PROCESS_STAGES)
        human_review_status = _required_text(row, "human_review_status")
        if human_review_status not in ALLOWED_HUMAN_REVIEW_STATUSES:
            raise ValueError(f"unsupported human_review_status: {human_review_status}")
        skipped_source_reasons = _required_allowed_tuple(row, "skipped_source_reasons", ALLOWED_SKIPPED_SOURCE_REASONS)
        reviewer_holds = _required_allowed_tuple(row, "reviewer_holds", ALLOWED_REVIEWER_HOLDS)
        validation_commands = _required_validation_commands(row, "validation_commands")

        return cls(
            row_id=_required_text(row, "row_id"),
            freshness_packet_refs=_required_text_tuple(row, "freshness_packet_refs"),
            source_evidence_placeholders=_required_placeholder_tuple(row, "source_evidence_placeholders"),
            expected_requirement_types=requirement_types,
            affected_process_stages=process_stages,
            human_review_status=human_review_status,
            skipped_source_reasons=skipped_source_reasons,
            reviewer_holds=reviewer_holds,
            validation_commands=validation_commands,
            candidate_requirement_id=_required_placeholder_text(row, "candidate_requirement_id"),
            candidate_summary=_required_text(row, "candidate_summary"),
        )


def build_requirement_reextraction_delta_queue_v4(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    normalized_rows = tuple(RequirementReextractionDeltaRowV4.from_mapping(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one requirement re-extraction delta row is required")
    queue = {
        "queue_version": QUEUE_VERSION,
        "mode": MODE,
        "row_count": len(normalized_rows),
        "freshness_packet_refs": _sorted_unique(_flatten(row.freshness_packet_refs for row in normalized_rows)),
        "source_evidence_placeholders": _sorted_unique(_flatten(row.source_evidence_placeholders for row in normalized_rows)),
        "expected_requirement_types": _sorted_unique(_flatten(row.expected_requirement_types for row in normalized_rows)),
        "affected_process_stages": _sorted_unique(_flatten(row.affected_process_stages for row in normalized_rows)),
        "human_review_statuses": _sorted_unique(row.human_review_status for row in normalized_rows),
        "skipped_source_reasons": _sorted_unique(_flatten(row.skipped_source_reasons for row in normalized_rows)),
        "reviewer_holds": _sorted_unique(_flatten(row.reviewer_holds for row in normalized_rows)),
        "validation_commands": [list(command) for command in EXPECTED_VALIDATION_COMMANDS],
        "delta_candidates": [_candidate_from_row(row) for row in sorted(normalized_rows, key=lambda item: item.row_id)],
        "attestations": {flag: False for flag in REQUIRED_FALSE_FLAGS},
    }
    validate_requirement_reextraction_delta_queue_v4(queue)
    return queue


def validate_requirement_reextraction_delta_queue_v4(queue: Mapping[str, Any]) -> None:
    _reject_prohibited_content(queue)
    if queue.get("queue_version") != QUEUE_VERSION:
        raise ValueError(f"queue_version must be {QUEUE_VERSION}")
    if queue.get("mode") != MODE:
        raise ValueError(f"mode must be {MODE}")
    for key in (
        "freshness_packet_refs",
        "source_evidence_placeholders",
        "expected_requirement_types",
        "affected_process_stages",
        "human_review_statuses",
        "skipped_source_reasons",
        "reviewer_holds",
    ):
        if not _non_empty_list_of_strings(queue.get(key)):
            raise ValueError(f"queue must include non-empty {key}")
    _validate_allowed_values(queue["expected_requirement_types"], "expected_requirement_types", ALLOWED_REQUIREMENT_TYPES)
    _validate_allowed_values(queue["affected_process_stages"], "affected_process_stages", ALLOWED_PROCESS_STAGES)
    _validate_allowed_values(queue["human_review_statuses"], "human_review_statuses", ALLOWED_HUMAN_REVIEW_STATUSES)
    _validate_allowed_values(queue["skipped_source_reasons"], "skipped_source_reasons", ALLOWED_SKIPPED_SOURCE_REASONS)
    _validate_allowed_values(queue["reviewer_holds"], "reviewer_holds", ALLOWED_REVIEWER_HOLDS)
    if queue.get("validation_commands") != [list(command) for command in EXPECTED_VALIDATION_COMMANDS]:
        raise ValueError("queue must include exact validation_commands")
    candidates = queue.get("delta_candidates")
    if not _non_empty_list_of_mappings(candidates):
        raise ValueError("queue must include non-empty delta_candidates")
    for candidate in candidates:
        _validate_candidate(candidate)
    attestations = queue.get("attestations")
    if not isinstance(attestations, Mapping):
        raise ValueError("queue must include attestations")
    for flag in REQUIRED_FALSE_FLAGS:
        if attestations.get(flag) is not False:
            raise ValueError(f"queue attestation {flag} must be false")


def load_requirement_reextraction_delta_rows_v4(path: Path) -> tuple[dict[str, Any], ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("fixture must be a JSON object")
    _reject_prohibited_content(payload)
    rows = payload.get("requirement_reextraction_delta_queue_v4_rows")
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        raise ValueError("fixture must contain non-empty requirement_reextraction_delta_queue_v4_rows objects")
    return tuple(rows)


def build_queue_from_fixture(path: Path) -> dict[str, Any]:
    return build_requirement_reextraction_delta_queue_v4(load_requirement_reextraction_delta_rows_v4(path))


def _candidate_from_row(row: RequirementReextractionDeltaRowV4) -> dict[str, Any]:
    return {
        "candidate_id": f"requirement-reextraction-delta-v4::{row.row_id}",
        "candidate_requirement_id": row.candidate_requirement_id,
        "candidate_summary": row.candidate_summary,
        "freshness_packet_refs": list(row.freshness_packet_refs),
        "source_evidence_placeholders": list(row.source_evidence_placeholders),
        "expected_requirement_types": list(row.expected_requirement_types),
        "affected_process_stages": list(row.affected_process_stages),
        "human_review_status": row.human_review_status,
        "skipped_source_reasons": list(row.skipped_source_reasons),
        "reviewer_holds": list(row.reviewer_holds),
        "validation_commands": [list(command) for command in row.validation_commands],
        "active_mutation": False,
        "active_requirement_mutation": False,
        "active_process_model_mutation": False,
        "active_guardrail_mutation": False,
        "live_crawl": False,
        "live_extraction": False,
        "ocr_completed": False,
        "raw_public_body_artifact": False,
        "private_artifact": False,
        "session_artifact": False,
        "auth_artifact": False,
        "legal_or_permitting_guarantee": False,
    }


def _validate_candidate(candidate: Mapping[str, Any]) -> None:
    for key in ("candidate_id", "candidate_requirement_id", "candidate_summary", "human_review_status"):
        _required_text(candidate, key)
    _required_placeholder_text(candidate, "candidate_requirement_id")
    _validate_allowed_values(_required_text_tuple(candidate, "freshness_packet_refs"), "freshness_packet_refs", None)
    _required_placeholder_tuple(candidate, "source_evidence_placeholders")
    _validate_allowed_values(_required_text_tuple(candidate, "expected_requirement_types"), "expected_requirement_types", ALLOWED_REQUIREMENT_TYPES)
    _validate_allowed_values(_required_text_tuple(candidate, "affected_process_stages"), "affected_process_stages", ALLOWED_PROCESS_STAGES)
    _validate_allowed_values((_required_text(candidate, "human_review_status"),), "human_review_status", ALLOWED_HUMAN_REVIEW_STATUSES)
    _validate_allowed_values(_required_text_tuple(candidate, "skipped_source_reasons"), "skipped_source_reasons", ALLOWED_SKIPPED_SOURCE_REASONS)
    _validate_allowed_values(_required_text_tuple(candidate, "reviewer_holds"), "reviewer_holds", ALLOWED_REVIEWER_HOLDS)
    if candidate.get("validation_commands") != [list(command) for command in EXPECTED_VALIDATION_COMMANDS]:
        raise ValueError("candidate must include exact validation_commands")
    for flag in REQUIRED_FALSE_FLAGS:
        if candidate.get(flag) is not False:
            raise ValueError(f"candidate must declare {flag} false")


def _reject_prohibited_content(value: Any, path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).lower()
            if key_text in PROHIBITED_KEYS:
                raise ValueError(f"{path} contains prohibited artifact key: {key}")
            _reject_prohibited_content(nested, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, nested in enumerate(value):
            _reject_prohibited_content(nested, f"{path}[{index}]")
    elif isinstance(value, str):
        normalized = " ".join(value.lower().replace("_", " ").replace("-", " ").split())
        for phrase in PROHIBITED_PHRASES:
            if phrase in normalized:
                raise ValueError(f"{path} contains prohibited claim phrase: {phrase}")


def _required_text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_placeholder_text(row: Mapping[str, Any], key: str) -> str:
    value = _required_text(row, key)
    if not (value.startswith("placeholder:") or value.startswith("pending-")):
        raise ValueError(f"{key} must remain a placeholder")
    return value


def _required_text_tuple(row: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = row.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        raise ValueError(f"{key} must be a non-empty list of strings")
    output = tuple(item for item in value if isinstance(item, str) and item.strip())
    if len(output) != len(value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return output


def _required_placeholder_tuple(row: Mapping[str, Any], key: str) -> tuple[str, ...]:
    values = _required_text_tuple(row, key)
    for value in values:
        if not (value.startswith("placeholder:") or value.startswith("pending-")):
            raise ValueError(f"{key} must contain only placeholders")
    return values


def _required_allowed_tuple(row: Mapping[str, Any], key: str, allowed: frozenset[str]) -> tuple[str, ...]:
    values = _required_text_tuple(row, key)
    _validate_allowed_values(values, key, allowed)
    return values


def _required_validation_commands(row: Mapping[str, Any], key: str) -> tuple[tuple[str, ...], ...]:
    value = row.get(key)
    expected = tuple(tuple(command) for command in EXPECTED_VALIDATION_COMMANDS)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{key} must match expected validation commands")
    commands = tuple(tuple(part for part in command) for command in value if isinstance(command, Sequence) and not isinstance(command, (str, bytes, bytearray)))
    if commands != expected:
        raise ValueError(f"{key} must match expected validation commands")
    return commands


def _validate_allowed_values(values: Sequence[str], key: str, allowed: frozenset[str] | None) -> None:
    if allowed is None:
        return
    for value in values:
        if value not in allowed:
            raise ValueError(f"unsupported {key}: {value}")


def _non_empty_list_of_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _non_empty_list_of_mappings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, Mapping) for item in value)


def _flatten(groups: Iterable[Iterable[str]]) -> tuple[str, ...]:
    return tuple(item for group in groups for item in group)


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))
