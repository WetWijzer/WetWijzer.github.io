"""Offline release rehearsal gate v2 validation.

This module is intentionally side-effect free. It validates only committed,
redacted release rehearsal metadata and rejects payloads that imply private
artifacts, live execution, official PP&D action, legal/permitting guarantees, or
active release-state mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence


_REQUIRED_SEQUENCE_FIELDS = {
    "promotion_candidate_inputs": "missing promotion candidate inputs",
    "guardrail_replay_inputs": "missing guardrail replay inputs",
    "agent_readiness_inputs": "missing agent readiness inputs",
    "release_gate_checks": "missing release gate checks",
    "evidence_bundle_references": "missing evidence bundle references",
    "validation_transcript_placeholders": "missing validation transcript placeholders",
    "rollback_readiness_placeholders": "missing rollback readiness placeholders",
    "human_reviewer_decisions": "missing human reviewer decisions",
    "validation_commands": "missing validation commands",
}

_PRIVATE_ARTIFACT_TERMS = (
    "auth_state",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "devhub_session",
    "downloaded",
    "har",
    "local_private_path",
    "password",
    "private_upload",
    "raw_crawl",
    "raw_download",
    "session_storage",
    "session-state",
    "session_state",
    "screenshot",
    "trace",
)

_PRIVATE_PATH_PARTS = {
    ".auth",
    ".devhub",
    ".playwright",
    "auth",
    "auth-state",
    "auth_state",
    "browser-state",
    "browser_state",
    "cookies",
    "downloads",
    "downloaded",
    "har",
    "private",
    "raw",
    "screenshots",
    "session",
    "session-state",
    "session_state",
    "storage-state",
    "storage_state",
    "traces",
}

_LIVE_EXECUTION_PHRASES = (
    "completed live crawl",
    "executed against devhub",
    "executed live",
    "live browser run",
    "live devhub run",
    "live execution",
    "performed live",
    "ran against production",
    "ran live",
)

_CONSEQUENTIAL_ACTION_PHRASES = (
    "certified acknowledgement",
    "paid fee",
    "purchased permit",
    "scheduled inspection",
    "submitted application",
    "submitted permit",
    "uploaded correction",
    "withdrew permit",
)

_GUARANTEE_PHRASES = (
    "approval guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legally compliant",
    "permit guaranteed",
    "will be approved",
    "will pass inspection",
)

_MUTATION_FLAG_FIELDS = (
    "active_promotion",
    "active_release_state_mutation",
    "apply_release_state",
    "commit_release_state",
    "execute_promotion",
    "mutate_release_state",
    "promote_now",
    "release_state_mutation_enabled",
)


@dataclass(frozen=True)
class OfflineRehearsalGateIssue:
    """A single offline release rehearsal validation failure."""

    code: str
    message: str
    path: str


@dataclass(frozen=True)
class OfflineRehearsalGateResult:
    """Validation result for an offline release rehearsal gate payload."""

    accepted: bool
    issues: tuple[OfflineRehearsalGateIssue, ...]


def validate_offline_release_rehearsal_gate_v2(
    payload: Mapping[str, Any],
) -> OfflineRehearsalGateResult:
    """Validate a v2 offline release rehearsal gate payload.

    The gate is fail-closed: every required evidence/input bucket must be a
    non-empty sequence, and the full payload is scanned for prohibited artifact
    references, live execution claims, official-action wording, guarantees, and
    release-state mutation flags.
    """

    issues: list[OfflineRehearsalGateIssue] = []

    for field_name, message in _REQUIRED_SEQUENCE_FIELDS.items():
        value = payload.get(field_name)
        if not _is_non_empty_sequence(value):
            issues.append(
                OfflineRehearsalGateIssue(
                    code=field_name,
                    message=message,
                    path=f"$.{field_name}",
                )
            )

    issues.extend(_scan_for_prohibited_values(payload))

    return OfflineRehearsalGateResult(accepted=not issues, issues=tuple(issues))


def assert_offline_release_rehearsal_gate_v2(payload: Mapping[str, Any]) -> None:
    """Raise ``ValueError`` when the offline rehearsal gate rejects a payload."""

    result = validate_offline_release_rehearsal_gate_v2(payload)
    if result.accepted:
        return
    details = "; ".join(f"{issue.path}: {issue.message}" for issue in result.issues)
    raise ValueError(f"offline release rehearsal gate v2 rejected payload: {details}")


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _scan_for_prohibited_values(value: Any, path: str = "$", field_name: str = "") -> tuple[OfflineRehearsalGateIssue, ...]:
    issues: list[OfflineRehearsalGateIssue] = []

    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            key_text = str(key)
            nested_path = f"{path}.{key_text}"
            normalized_key = _normalize_text(key_text)
            if normalized_key in _MUTATION_FLAG_FIELDS and bool(nested_value):
                issues.append(
                    OfflineRehearsalGateIssue(
                        code="active_release_state_mutation_flag",
                        message="active promotion or release-state mutation flags are not allowed",
                        path=nested_path,
                    )
                )
            issues.extend(_scan_for_prohibited_values(nested_value, nested_path, key_text))
        return tuple(issues)

    if _is_non_empty_sequence(value):
        for index, nested_value in enumerate(value):
            issues.extend(_scan_for_prohibited_values(nested_value, f"{path}[{index}]", field_name))
        return tuple(issues)

    if isinstance(value, str):
        issues.extend(_string_issues(value, path, field_name))

    return tuple(issues)


def _string_issues(value: str, path: str, field_name: str) -> tuple[OfflineRehearsalGateIssue, ...]:
    normalized = _normalize_text(value)
    issues: list[OfflineRehearsalGateIssue] = []

    if any(term in normalized for term in _PRIVATE_ARTIFACT_TERMS) or _looks_like_private_path(value):
        issues.append(
            OfflineRehearsalGateIssue(
                code="private_artifact_reference",
                message="private/session/browser/raw/downloaded artifacts are not allowed",
                path=path,
            )
        )

    if any(phrase in normalized for phrase in _LIVE_EXECUTION_PHRASES):
        issues.append(
            OfflineRehearsalGateIssue(
                code="live_execution_claim",
                message="live execution claims are not allowed in offline rehearsal evidence",
                path=path,
            )
        )

    if any(phrase in normalized for phrase in _CONSEQUENTIAL_ACTION_PHRASES):
        issues.append(
            OfflineRehearsalGateIssue(
                code="consequential_official_action_language",
                message="consequential official action language is not allowed",
                path=path,
            )
        )

    if any(phrase in normalized for phrase in _GUARANTEE_PHRASES):
        issues.append(
            OfflineRehearsalGateIssue(
                code="legal_or_permitting_guarantee",
                message="legal or permitting guarantees are not allowed",
                path=path,
            )
        )

    if _normalize_text(field_name) in _MUTATION_FLAG_FIELDS and normalized in {"1", "true", "yes", "on", "enabled"}:
        issues.append(
            OfflineRehearsalGateIssue(
                code="active_release_state_mutation_flag",
                message="active promotion or release-state mutation flags are not allowed",
                path=path,
            )
        )

    return tuple(issues)


def _looks_like_private_path(value: str) -> bool:
    path_text = value.replace("\\", "/")
    if "://" in path_text and not path_text.startswith("file://"):
        return False

    parts = {part.lower() for part in PurePosixPath(path_text).parts if part not in {"/", ""}}
    if parts & _PRIVATE_PATH_PARTS:
        return True

    lowered = path_text.lower()
    return lowered.endswith((".har", ".trace", ".zip")) and any(part in lowered for part in ("trace", "session", "browser", "raw", "download"))


def _normalize_text(value: str) -> str:
    return " ".join(value.replace("-", "_").replace("/", " ").lower().split())
