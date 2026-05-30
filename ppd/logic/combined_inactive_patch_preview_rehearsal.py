"""Validation for combined inactive patch preview dependency rehearsal v1 artifacts.

The validator is intentionally schema-light: rehearsal artifacts are produced by
several daemon paths, so this module checks for required safety semantics without
requiring one exact serialization shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


_ALLOWED_SCOPE = "combined_inactive_fixture_preview_rehearsal_v1"
_ALLOWED_MUTATION_FLAGS = frozenset(
    {
        "combined_inactive_fixture_preview_rehearsal",
        "fixture_preview_only",
        "inactive_patch_preview_only",
        "no_live_execution",
        "no_applied_promotion",
        "no_mutation",
    }
)

_PRIVATE_OR_BROWSER_ARTIFACT_TERMS = (
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "password",
    "secret",
    "token",
    "auth_state",
    "storage_state",
    "session_state",
    "session file",
    "browser profile",
    "localstorage",
    "indexeddb",
)

_FORBIDDEN_CAPTURE_TERMS = (
    "screenshot",
    "screenshots",
    "trace.zip",
    "playwright trace",
    "har",
    ".har",
    "auth.json",
    "storage-state.json",
    "raw crawl",
    "raw html",
    "raw pdf",
    "downloaded pdf",
    "downloaded data",
    "crawl output",
)

_LIVE_OR_PROMOTION_CLAIM_TERMS = (
    "live execution completed",
    "live crawl completed",
    "ran live",
    "executed live",
    "promotion applied",
    "applied promotion",
    "promoted to active",
    "production promotion",
    "published promotion",
)

_GUARANTEE_TERMS = (
    "permit will be approved",
    "approval guaranteed",
    "guaranteed approval",
    "legally sufficient",
    "legal compliance guaranteed",
    "no legal risk",
    "will pass inspection",
    "will be issued",
)

_CONSEQUENTIAL_ACTION_TERMS = (
    "pay fee",
    "payment submitted",
    "submit application",
    "submitted application",
    "schedule inspection",
    "scheduled inspection",
    "cancel permit",
    "cancel inspection",
    "certify application",
    "certification completed",
    "upload correction",
    "uploaded correction",
    "upload plans",
    "uploaded plans",
)

_EVIDENCE_CONTAINERS = (
    "public_source_evidence",
    "devhub_observation_evidence",
    "evidence",
    "source_evidence",
    "observations",
)


@dataclass(frozen=True)
class RehearsalValidationFinding:
    """A deterministic validation finding for a rehearsal artifact."""

    code: str
    message: str


def validate_combined_inactive_patch_preview_rehearsal_v1(
    artifact: Mapping[str, Any],
) -> list[RehearsalValidationFinding]:
    """Return validation findings for a combined inactive rehearsal artifact."""

    findings: list[RehearsalValidationFinding] = []

    if artifact.get("schema_version") != "combined_inactive_patch_preview_dependency_rehearsal_v1":
        findings.append(
            RehearsalValidationFinding(
                "wrong_schema_version",
                "artifact must declare combined inactive patch preview dependency rehearsal v1",
            )
        )

    scope = artifact.get("scope")
    if scope != _ALLOWED_SCOPE:
        findings.append(
            RehearsalValidationFinding(
                "outside_combined_inactive_fixture_preview_rehearsal_scope",
                "artifact scope must be limited to combined inactive fixture preview rehearsal v1",
            )
        )

    _require_non_empty_sequence(
        artifact,
        "cross_family_dependency_rows",
        "missing_cross_family_dependency_rows",
        "cross-family dependency rows are required",
        findings,
    )
    _require_non_empty_sequence(
        artifact,
        "unchanged_family_inventory",
        "missing_unchanged_family_inventory",
        "unchanged-family inventory is required",
        findings,
    )
    _require_non_empty_sequence(
        artifact,
        "blocked_promotion_carry_forward_notes",
        "missing_blocked_promotion_carry_forward_notes",
        "blocked-promotion carry-forward notes are required",
        findings,
    )
    _require_non_empty_sequence(
        artifact,
        "reviewer_signoff_placeholders",
        "missing_reviewer_signoff_placeholders",
        "reviewer signoff placeholders are required",
        findings,
    )
    _require_non_empty_sequence(
        artifact,
        "rollback_checkpoints",
        "missing_rollback_checkpoints",
        "rollback checkpoints are required",
        findings,
    )
    _require_non_empty_sequence(
        artifact,
        "validation_commands",
        "missing_validation_commands",
        "validation commands are required",
        findings,
    )

    _validate_dependency_rows(artifact.get("cross_family_dependency_rows"), findings)
    _validate_evidence_citations(artifact, findings)
    _validate_mutation_flags(artifact.get("mutation_flags"), findings)
    _validate_forbidden_text(artifact, findings)

    return findings


def assert_valid_combined_inactive_patch_preview_rehearsal_v1(
    artifact: Mapping[str, Any],
) -> None:
    """Raise ValueError when the rehearsal artifact is invalid."""

    findings = validate_combined_inactive_patch_preview_rehearsal_v1(artifact)
    if findings:
        joined = "; ".join(f"{finding.code}: {finding.message}" for finding in findings)
        raise ValueError(joined)


def _require_non_empty_sequence(
    artifact: Mapping[str, Any],
    key: str,
    code: str,
    message: str,
    findings: list[RehearsalValidationFinding],
) -> None:
    value = artifact.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        findings.append(RehearsalValidationFinding(code, message))


def _validate_dependency_rows(
    rows: Any,
    findings: list[RehearsalValidationFinding],
) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return

    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            findings.append(
                RehearsalValidationFinding(
                    "invalid_cross_family_dependency_row",
                    f"dependency row {index} must be an object",
                )
            )
            continue

        missing = [
            key
            for key in ("source_family", "dependent_family", "dependency", "evidence_ids")
            if not row.get(key)
        ]
        if missing:
            findings.append(
                RehearsalValidationFinding(
                    "invalid_cross_family_dependency_row",
                    f"dependency row {index} is missing required fields: {', '.join(missing)}",
                )
            )

        evidence_ids = row.get("evidence_ids")
        if not isinstance(evidence_ids, Sequence) or isinstance(evidence_ids, (str, bytes)) or not evidence_ids:
            findings.append(
                RehearsalValidationFinding(
                    "uncited_cross_family_dependency_row",
                    f"dependency row {index} must cite evidence ids",
                )
            )


def _validate_evidence_citations(
    artifact: Mapping[str, Any],
    findings: list[RehearsalValidationFinding],
) -> None:
    public_items = _collect_named_items(artifact, "public_source_evidence")
    devhub_items = _collect_named_items(artifact, "devhub_observation_evidence")

    if not public_items:
        findings.append(
            RehearsalValidationFinding(
                "missing_public_source_evidence",
                "at least one cited public source evidence row is required",
            )
        )
    if not devhub_items:
        findings.append(
            RehearsalValidationFinding(
                "missing_devhub_observation_evidence",
                "at least one cited DevHub observation evidence row is required",
            )
        )

    for index, item in enumerate(public_items):
        if not _has_citation(item, ("source_id", "canonical_url", "citation")):
            findings.append(
                RehearsalValidationFinding(
                    "uncited_public_source_evidence",
                    f"public source evidence row {index} must include source_id, canonical_url, or citation",
                )
            )

    for index, item in enumerate(devhub_items):
        if not _has_citation(item, ("observation_id", "source_id", "citation")):
            findings.append(
                RehearsalValidationFinding(
                    "uncited_devhub_observation_evidence",
                    f"DevHub observation evidence row {index} must include observation_id, source_id, or citation",
                )
            )


def _validate_mutation_flags(
    flags: Any,
    findings: list[RehearsalValidationFinding],
) -> None:
    if flags is None:
        return
    if not isinstance(flags, Sequence) or isinstance(flags, (str, bytes)):
        findings.append(
            RehearsalValidationFinding(
                "invalid_mutation_flags",
                "mutation_flags must be a list limited to inactive fixture preview rehearsal flags",
            )
        )
        return

    for flag in flags:
        if flag not in _ALLOWED_MUTATION_FLAGS:
            findings.append(
                RehearsalValidationFinding(
                    "mutation_flag_outside_combined_inactive_fixture_preview_rehearsal_scope",
                    f"mutation flag {flag!r} is outside the combined inactive fixture preview rehearsal scope",
                )
            )


def _validate_forbidden_text(
    artifact: Mapping[str, Any],
    findings: list[RehearsalValidationFinding],
) -> None:
    text = "\n".join(_walk_text(artifact)).lower()
    checks = (
        (
            _PRIVATE_OR_BROWSER_ARTIFACT_TERMS,
            "private_authenticated_session_or_browser_artifact",
            "private, authenticated, session, or browser artifacts are not allowed",
        ),
        (
            _FORBIDDEN_CAPTURE_TERMS,
            "forbidden_capture_or_raw_data_artifact",
            "screenshots, traces, HAR/auth files, raw crawl/PDF, or downloaded data are not allowed",
        ),
        (
            _LIVE_OR_PROMOTION_CLAIM_TERMS,
            "live_execution_or_applied_promotion_claim",
            "live execution and applied-promotion claims are outside inactive preview rehearsal scope",
        ),
        (
            _GUARANTEE_TERMS,
            "legal_or_permitting_outcome_guarantee",
            "legal or permitting outcome guarantees are not allowed",
        ),
        (
            _CONSEQUENTIAL_ACTION_TERMS,
            "payment_submission_scheduling_cancellation_certification_or_upload_language",
            "payment, submission, scheduling, cancellation, certification, and upload action language is not allowed",
        ),
    )

    for terms, code, message in checks:
        if any(term in text for term in terms):
            findings.append(RehearsalValidationFinding(code, message))


def _collect_named_items(artifact: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = artifact.get(key)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [item for item in value if isinstance(item, Mapping)]

    evidence = artifact.get("evidence")
    if isinstance(evidence, Mapping):
        nested = evidence.get(key)
        if isinstance(nested, Sequence) and not isinstance(nested, (str, bytes)):
            return [item for item in nested if isinstance(item, Mapping)]

    return []


def _has_citation(item: Mapping[str, Any], keys: Iterable[str]) -> bool:
    return any(bool(item.get(key)) for key in keys)


def _walk_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, Mapping):
        for key, nested in value.items():
            yield str(key)
            yield from _walk_text(nested)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for nested in value:
            yield from _walk_text(nested)
