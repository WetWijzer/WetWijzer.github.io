"""Validation for PP&D live-readiness authorization checklist packets.

The v2 packet is intentionally stricter than a general readiness note: it must be
safe to commit, source-grounded, and incapable of enabling live DevHub mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


MUTATION_FLAG_NAMES = frozenset(
    {
        "active_source_mutation",
        "active_schedule_mutation",
        "active_surface_registry_mutation",
        "active_prompt_mutation",
        "active_monitoring_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    }
)

PRIVATE_FACT_MARKERS = (
    "private",
    "authenticated",
    "account_scoped",
    "account-scoped",
    "non_public",
    "non-public",
)

SESSION_ARTIFACT_MARKERS = (
    "cookie",
    "cookies",
    "session",
    "storage_state",
    "localstorage",
    "auth_state",
    "bearer",
    "token",
    "password",
)

BROWSER_ARTIFACT_MARKERS = (
    "screenshot",
    "screenshots",
    "trace",
    "traces",
    ".har",
    " har ",
    "har_path",
    "network log",
)

LIVE_EXECUTION_MARKERS = (
    "clicked live",
    "executed live",
    "ran live",
    "submitted live",
    "uploaded live",
    "paid live",
    "scheduled live",
    "cancelled live",
    "canceled live",
    "changed official",
    "official record updated",
)

BLOCKED_AUTOMATION_MARKERS = (
    "automate credential",
    "automated credential",
    "enter password",
    "password automation",
    "mfa automation",
    "automate mfa",
    "captcha automation",
    "automate captcha",
    "bypass captcha",
    "solve captcha",
    "account creation automation",
)

OUTCOME_GUARANTEE_MARKERS = (
    "guarantee approval",
    "approval guaranteed",
    "permit will be issued",
    "will be approved",
    "legal outcome guaranteed",
    "guarantee permit",
    "guarantee inspection",
)

OFFICIAL_ACTION_MARKERS = (
    "enable submit",
    "enable upload",
    "enable payment",
    "enable schedule",
    "enable cancellation",
    "enable certification",
    "ready to submit",
    "ready to pay",
    "ready to schedule",
    "ready to upload",
    "ready to certify",
    "make official change",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    issues: tuple[ValidationIssue, ...]

    def error_codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)


def validate_live_readiness_authorization_packet_v2(packet: Mapping[str, Any]) -> ValidationResult:
    """Validate a commit-safe PP&D live-readiness authorization packet v2."""

    issues: list[ValidationIssue] = []

    if packet.get("packet_version") not in {"live-readiness-authorization-checklist-v2", "v2"}:
        issues.append(
            ValidationIssue(
                "packet_version_invalid",
                "packet_version must identify live-readiness authorization checklist packet v2.",
                "packet_version",
            )
        )

    prerequisites = _as_sequence(packet.get("prerequisites"))
    if not prerequisites:
        issues.append(
            ValidationIssue(
                "prerequisites_missing",
                "Packet must include cited prerequisites.",
                "prerequisites",
            )
        )
    else:
        for index, prerequisite in enumerate(prerequisites):
            path = f"prerequisites[{index}]"
            if not isinstance(prerequisite, Mapping):
                issues.append(
                    ValidationIssue(
                        "prerequisite_invalid",
                        "Each prerequisite must be an object with citation evidence.",
                        path,
                    )
                )
                continue
            if not _has_citation(prerequisite):
                issues.append(
                    ValidationIssue(
                        "prerequisite_uncited",
                        "Each prerequisite must include a public source citation or source evidence id.",
                        path,
                    )
                )

    _require_signoff(packet, "reviewer_signoff", issues)
    _require_signoff(packet, "operator_signoff", issues)

    fixture_gaps = _as_sequence(packet.get("fixture_gaps"))
    unresolved_gaps = [gap for gap in fixture_gaps if _gap_is_unresolved(gap)]
    if unresolved_gaps:
        issues.append(
            ValidationIssue(
                "fixture_gaps_unresolved",
                "Packet cannot be live-ready while deterministic fixture gaps remain unresolved.",
                "fixture_gaps",
            )
        )

    facts = _as_sequence(packet.get("facts"))
    for index, fact in enumerate(facts):
        if _contains_marker(fact, PRIVATE_FACT_MARKERS):
            issues.append(
                ValidationIssue(
                    "private_or_authenticated_fact",
                    "Packet must not rely on private, authenticated, or account-scoped facts.",
                    f"facts[{index}]",
                )
            )

    artifacts = _as_sequence(packet.get("artifacts"))
    for index, artifact in enumerate(artifacts):
        path = f"artifacts[{index}]"
        if _contains_marker(artifact, SESSION_ARTIFACT_MARKERS):
            issues.append(
                ValidationIssue(
                    "session_or_auth_artifact",
                    "Packet must not reference credentials, sessions, cookies, tokens, or auth state.",
                    path,
                )
            )
        if _contains_marker(artifact, BROWSER_ARTIFACT_MARKERS):
            issues.append(
                ValidationIssue(
                    "browser_artifact_reference",
                    "Packet must not reference screenshots, traces, HAR files, or browser capture artifacts.",
                    path,
                )
            )

    narrative_values = _collect_narrative_values(packet)
    for path, value in narrative_values:
        if _contains_marker(value, LIVE_EXECUTION_MARKERS):
            issues.append(
                ValidationIssue(
                    "live_execution_claim",
                    "Packet must not claim live execution of DevHub or official actions.",
                    path,
                )
            )
        if _contains_marker(value, BLOCKED_AUTOMATION_MARKERS):
            issues.append(
                ValidationIssue(
                    "blocked_credential_or_challenge_automation",
                    "Packet must not include credential, MFA, CAPTCHA, or account automation language.",
                    path,
                )
            )
        if _contains_marker(value, OUTCOME_GUARANTEE_MARKERS):
            issues.append(
                ValidationIssue(
                    "legal_or_permitting_outcome_guarantee",
                    "Packet must not guarantee legal, permitting, approval, payment, or inspection outcomes.",
                    path,
                )
            )
        if _contains_marker(value, OFFICIAL_ACTION_MARKERS):
            issues.append(
                ValidationIssue(
                    "official_action_enablement",
                    "Packet must not enable submission, upload, payment, scheduling, certification, cancellation, or other official actions.",
                    path,
                )
            )

    mutation_flags = packet.get("mutation_flags", {})
    if isinstance(mutation_flags, Mapping):
        for flag_name in sorted(MUTATION_FLAG_NAMES):
            if bool(mutation_flags.get(flag_name)):
                issues.append(
                    ValidationIssue(
                        "active_mutation_flag",
                        f"{flag_name} must be false for a live-readiness authorization packet.",
                        f"mutation_flags.{flag_name}",
                    )
                )
    else:
        issues.append(
            ValidationIssue(
                "mutation_flags_invalid",
                "mutation_flags must be an object containing explicit inactive mutation flags.",
                "mutation_flags",
            )
        )

    return ValidationResult(ok=not issues, issues=tuple(issues))


def _require_signoff(packet: Mapping[str, Any], field: str, issues: list[ValidationIssue]) -> None:
    signoff = packet.get(field)
    if not isinstance(signoff, Mapping):
        issues.append(
            ValidationIssue(
                f"{field}_missing",
                f"{field} must be present and include name, role, timestamp, and affirmation.",
                field,
            )
        )
        return

    missing = [name for name in ("name", "role", "timestamp", "affirmation") if not str(signoff.get(name, "")).strip()]
    if missing:
        issues.append(
            ValidationIssue(
                f"{field}_incomplete",
                f"{field} is missing required fields: {', '.join(missing)}.",
                field,
            )
        )


def _has_citation(value: Mapping[str, Any]) -> bool:
    citation_fields = ("citation", "citations", "source_evidence_id", "source_evidence_ids", "source_url")
    return any(bool(value.get(field)) for field in citation_fields)


def _gap_is_unresolved(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"", "resolved", "closed", "none"}
    if isinstance(value, Mapping):
        status = str(value.get("status", "")).strip().lower()
        return status not in {"resolved", "closed", "not_applicable", "not-applicable"}
    return bool(value)


def _as_sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return ()
    if isinstance(value, list | tuple):
        return value
    return (value,)


def _collect_narrative_values(value: Any, path: str = "$") -> tuple[tuple[str, Any], ...]:
    collected: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            collected.extend(_collect_narrative_values(child, f"{path}.{key}"))
    elif isinstance(value, list | tuple):
        for index, child in enumerate(value):
            collected.extend(_collect_narrative_values(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        collected.append((path, value))
    return tuple(collected)


def _contains_marker(value: Any, markers: Iterable[str]) -> bool:
    haystack = _flatten_text(value).lower()
    return any(marker in haystack for marker in markers)


def _flatten_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_flatten_text(child)}" for key, child in value.items())
    if isinstance(value, list | tuple | set):
        return " ".join(_flatten_text(child) for child in value)
    return str(value)
