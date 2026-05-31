"""Validation for guardrail recompile reviewer packet v2.

This packet is a review-only handoff artifact. It must prove that each reviewer
row carries the traces and disposition notes needed for guardrail recompilation
review, while also proving that no private artifacts, live crawl/DevHub claims,
outcome guarantees, or active-state mutation flags leaked into the packet.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GuardrailRecompileReviewerPacketV2Finding:
    code: str
    path: str
    message: str


class GuardrailRecompileReviewerPacketV2Error(ValueError):
    """Raised when a guardrail recompile reviewer packet v2 is invalid."""


_REVIEWER_ROW_KEYS = ("reviewer_rows", "review_rows", "guardrail_recompile_reviewer_rows")
_REQUIREMENT_DELTA_TRACE_KEYS = (
    "requirement_delta_trace",
    "requirement_delta_traces",
    "requirement_delta_trace_ids",
    "requirement_delta_review_trace",
    "requirement_delta_review_traces",
)
_PREDICATE_IMPACT_NOTE_KEYS = (
    "predicate_impact_review_note",
    "predicate_impact_review_notes",
    "predicate_impact_reviewer_note",
    "predicate_impact_reviewer_notes",
)
_MIGRATION_RISK_DISPOSITION_KEYS = (
    "migration_risk_disposition",
    "migration_risk_dispositions",
    "migration_risk_review_disposition",
)
_STALE_SOURCE_HOLD_KEYS = (
    "stale_source_hold_carry_forward_decision",
    "stale_source_hold_carry_forward_decisions",
    "stale_source_hold_decision",
    "stale_source_hold_disposition",
)
_BLOCKED_ACTION_CHECK_KEYS = (
    "blocked_action_reminder_check",
    "blocked_action_reminder_checks",
    "blocked_action_reminder_verified",
    "blocked_action_reminders_checked",
)
_VALIDATION_COMMAND_KEYS = ("validation_commands", "offline_validation_commands")

_PRIVATE_ARTIFACT_KEY_MARKERS = (
    "auth_state",
    "browser_artifact",
    "browser_context",
    "browser_profile",
    "browser_state",
    "downloaded_artifact",
    "downloaded_document",
    "downloaded_file",
    "har_file",
    "private_artifact",
    "raw_artifact",
    "raw_crawl",
    "raw_download",
    "session_artifact",
    "session_file",
    "session_path",
    "session_state",
    "storage_state",
    "trace_artifact",
    "trace_file",
)
_PRIVATE_ARTIFACT_STRING_FRAGMENTS = (
    ".har",
    "auth-state",
    "auth_state",
    "browser-state",
    "browser_state",
    "data/private",
    "data/raw",
    "downloaded/",
    "downloads/",
    "raw crawl",
    "raw-crawl",
    "session.json",
    "session-state",
    "session_state",
    "storage-state",
    "storage_state",
    "trace.zip",
)

_LIVE_CLAIM_KEYS = (
    "devhub_claimed_live",
    "devhub_live_claim",
    "devhub_live_execution_claimed",
    "live_crawl_claim",
    "live_crawl_claimed",
    "live_devhub_claim",
    "live_devhub_claimed",
    "live_devhub_execution",
    "live_public_crawl",
)
_LIVE_CLAIM_PHRASES = (
    "authenticated devhub run",
    "live crawl",
    "live devhub",
    "opened devhub",
    "performed a live crawl",
    "ran live devhub",
)

_GUARANTEE_KEYS = (
    "approval_guarantee",
    "guaranteed_outcome",
    "legal_guarantee",
    "legal_outcome_guarantee",
    "permit_approval_guarantee",
    "permitting_guarantee",
    "permitting_outcome_guarantee",
)
_GUARANTEE_PHRASES = (
    "guarantee approval",
    "guaranteed approval",
    "guaranteed permit",
    "guarantees approval",
    "permit will be approved",
    "will be approved",
)

_ACTIVE_MUTATION_SUBJECTS = (
    "source",
    "requirement",
    "process_model",
    "process-model",
    "guardrail",
    "prompt",
    "contract",
    "devhub_surface",
    "devhub-surface",
    "release_state",
    "release-state",
)
_MUTATION_WORDS = ("mutate", "mutated", "mutation", "patch", "promote", "write")
_MUTATION_KEY_SUFFIXES = (
    "mutation_enabled",
    "mutation_flag",
    "mutated",
    "patch_enabled",
    "promotion_enabled",
    "write_enabled",
)


def validate_guardrail_recompile_reviewer_packet_v2(packet: Mapping[str, Any]) -> list[GuardrailRecompileReviewerPacketV2Finding]:
    """Return validation findings for a guardrail recompile reviewer packet v2."""

    if not isinstance(packet, Mapping):
        return [
            GuardrailRecompileReviewerPacketV2Finding(
                "invalid_packet",
                "$",
                "Guardrail recompile reviewer packet v2 must be an object.",
            )
        ]

    findings: list[GuardrailRecompileReviewerPacketV2Finding] = []
    _validate_reviewer_rows(packet, findings)
    _validate_validation_commands(packet, findings)
    _validate_safety_boundaries(packet, findings)
    return findings


def require_valid_guardrail_recompile_reviewer_packet_v2(packet: Mapping[str, Any]) -> None:
    findings = validate_guardrail_recompile_reviewer_packet_v2(packet)
    if findings:
        detail = "; ".join(f"{item.code} at {item.path}: {item.message}" for item in findings)
        raise GuardrailRecompileReviewerPacketV2Error("invalid guardrail recompile reviewer packet v2: " + detail)


def finding_codes(findings: Iterable[GuardrailRecompileReviewerPacketV2Finding]) -> set[str]:
    return {finding.code for finding in findings}


def _validate_reviewer_rows(packet: Mapping[str, Any], findings: list[GuardrailRecompileReviewerPacketV2Finding]) -> None:
    rows_key = next((key for key in _REVIEWER_ROW_KEYS if key in packet), "reviewer_rows")
    rows_value = packet.get(rows_key)
    rows = _mapping_list(rows_value)
    if not rows:
        findings.append(
            GuardrailRecompileReviewerPacketV2Finding(
                "missing_reviewer_rows",
                f"$.{rows_key}",
                "At least one reviewer row object is required.",
            )
        )
        return

    for index, row in enumerate(rows):
        path = f"$.{rows_key}[{index}]"
        if not _has_present(row, _REQUIREMENT_DELTA_TRACE_KEYS):
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "missing_requirement_delta_traces",
                    path,
                    "Reviewer rows must include requirement-delta traces.",
                )
            )
        if not _has_present(row, _PREDICATE_IMPACT_NOTE_KEYS):
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "missing_predicate_impact_review_notes",
                    path,
                    "Reviewer rows must include predicate-impact review notes.",
                )
            )
        if not _has_present(row, _MIGRATION_RISK_DISPOSITION_KEYS):
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "missing_migration_risk_dispositions",
                    path,
                    "Reviewer rows must include migration-risk dispositions.",
                )
            )
        if not _has_present(row, _STALE_SOURCE_HOLD_KEYS):
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "missing_stale_source_hold_carry_forward_decisions",
                    path,
                    "Reviewer rows must include stale-source hold carry-forward decisions.",
                )
            )
        if not _has_present(row, _BLOCKED_ACTION_CHECK_KEYS):
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "missing_blocked_action_reminder_checks",
                    path,
                    "Reviewer rows must include blocked-action reminder checks.",
                )
            )


def _validate_validation_commands(packet: Mapping[str, Any], findings: list[GuardrailRecompileReviewerPacketV2Finding]) -> None:
    commands_key = next((key for key in _VALIDATION_COMMAND_KEYS if key in packet), "validation_commands")
    commands = packet.get(commands_key)
    if not _valid_commands(commands):
        findings.append(
            GuardrailRecompileReviewerPacketV2Finding(
                "missing_validation_commands",
                f"$.{commands_key}",
                "Reviewer packets must include at least one deterministic offline validation command.",
            )
        )


def _validate_safety_boundaries(packet: Mapping[str, Any], findings: list[GuardrailRecompileReviewerPacketV2Finding]) -> None:
    for path, value in _walk(packet):
        key = _last_key(path)
        lowered_key = key.lower()

        if _private_artifact_key(lowered_key) and _present(value):
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "private_session_browser_raw_or_downloaded_artifact",
                    path,
                    "Reviewer packets must not include private, session, browser, raw, or downloaded artifacts.",
                )
            )

        if lowered_key in _LIVE_CLAIM_KEYS and value:
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "live_crawl_or_devhub_claim",
                    path,
                    "Reviewer packets must not claim live crawl or DevHub execution.",
                )
            )

        if lowered_key in _GUARANTEE_KEYS and value:
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "legal_or_permitting_guarantee",
                    path,
                    "Reviewer packets must not include legal or permitting guarantees.",
                )
            )

        if _active_mutation_key(lowered_key) and value is not False and value is not None:
            findings.append(
                GuardrailRecompileReviewerPacketV2Finding(
                    "active_state_mutation_flag",
                    path,
                    "Active source, requirement, process-model, guardrail, prompt, contract, DevHub surface, and release-state mutation flags must be false.",
                )
            )

        if isinstance(value, str):
            normalized = value.strip().lower()
            if _private_artifact_string(normalized):
                findings.append(
                    GuardrailRecompileReviewerPacketV2Finding(
                        "private_session_browser_raw_or_downloaded_artifact",
                        path,
                        "Reviewer packets must not reference private, session, browser, raw, or downloaded artifacts.",
                    )
                )
            if any(phrase in normalized for phrase in _LIVE_CLAIM_PHRASES):
                findings.append(
                    GuardrailRecompileReviewerPacketV2Finding(
                        "live_crawl_or_devhub_claim",
                        path,
                        "Reviewer packets must not claim live crawl or DevHub execution.",
                    )
                )
            if any(phrase in normalized for phrase in _GUARANTEE_PHRASES):
                findings.append(
                    GuardrailRecompileReviewerPacketV2Finding(
                        "legal_or_permitting_guarantee",
                        path,
                        "Reviewer packets must not guarantee legal or permitting outcomes.",
                    )
                )
            if _active_mutation_phrase(normalized):
                findings.append(
                    GuardrailRecompileReviewerPacketV2Finding(
                        "active_state_mutation_flag",
                        path,
                        "Reviewer packets must not claim active-state mutation.",
                    )
                )


def _has_present(row: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return any(_present(row.get(key)) for key in keys)


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _valid_commands(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return False
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)):
            continue
        parts = [part for part in command if isinstance(part, str) and part.strip()]
        if len(parts) == len(command) and parts:
            return True
    return False


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _private_artifact_key(key: str) -> bool:
    return any(marker in key for marker in _PRIVATE_ARTIFACT_KEY_MARKERS)


def _private_artifact_string(value: str) -> bool:
    return any(fragment in value for fragment in _PRIVATE_ARTIFACT_STRING_FRAGMENTS)


def _active_mutation_key(key: str) -> bool:
    if not key.startswith("active_"):
        return False
    if not any(subject in key for subject in _ACTIVE_MUTATION_SUBJECTS):
        return False
    return any(suffix in key for suffix in _MUTATION_KEY_SUFFIXES)


def _active_mutation_phrase(value: str) -> bool:
    if "active" not in value:
        return False
    if not any(subject.replace("_", " ").replace("-", " ") in value for subject in _ACTIVE_MUTATION_SUBJECTS):
        return False
    return any(word in value for word in _MUTATION_WORDS)


def _last_key(path: str) -> str:
    tail = path.rsplit(".", 1)[-1]
    return tail.split("[", 1)[0]


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = path + "." + str(key)
            yield child_path, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, child
            yield from _walk(child, child_path)
