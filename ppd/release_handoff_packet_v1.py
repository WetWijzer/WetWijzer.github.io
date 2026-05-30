"""Validation for PP&D human release handoff packet v1.

The validator is intentionally data-shape tolerant so release tooling can call it
before a packet is rendered. It rejects safety-sensitive handoff content without
performing network access, live execution, or artifact inspection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


FORBIDDEN_MUTATION_FLAGS = frozenset(
    {
        "source",
        "sources",
        "source_registry",
        "source-registry",
        "surface_registry",
        "surface-registry",
        "guardrail",
        "guardrails",
        "prompt",
        "prompts",
        "release_state",
        "release-state",
        "agent_state",
        "agent-state",
    }
)

_PRIVATE_ARTIFACT_MARKERS = (
    "authenticated",
    "auth state",
    "auth_state",
    "bearer ",
    "cookie",
    "credential",
    "devhub session",
    "har",
    "local private",
    "mfa",
    "password",
    "payment detail",
    "private artifact",
    "private upload",
    "session storage",
    "session_state",
    "screenshot",
    "trace.zip",
)

_LIVE_EXECUTION_MARKERS = (
    "applied live",
    "executed live",
    "live crawl completed",
    "live execution",
    "promoted to production",
    "promotion completed",
    "published to production",
    "submitted to devhub",
)

_LEGAL_OR_PERMITTING_GUARANTEE_MARKERS = (
    "approval guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "guaranteed permit",
    "guarantees approval",
    "legal guarantee",
    "permit guaranteed",
    "will be approved",
    "will be issued",
)

_CONSEQUENTIAL_ACTION_MARKERS = (
    "certify the acknowledgement",
    "click submit",
    "enter payment",
    "make the payment",
    "pay the fee",
    "purchase the permit",
    "schedule the inspection",
    "submit the application",
    "submit the permit",
    "upload corrections",
    "withdraw the permit",
)


@dataclass(frozen=True)
class HandoffValidationIssue:
    """A deterministic validation failure for a handoff packet."""

    code: str
    message: str
    path: str


@dataclass(frozen=True)
class HandoffValidationResult:
    """Validation result for a human release handoff packet."""

    valid: bool
    issues: tuple[HandoffValidationIssue, ...]

    def raise_for_issues(self) -> None:
        if self.issues:
            details = "; ".join(f"{issue.code} at {issue.path}" for issue in self.issues)
            raise ValueError(f"invalid human release handoff packet v1: {details}")


def validate_human_release_handoff_packet_v1(packet: Mapping[str, Any]) -> HandoffValidationResult:
    """Validate a PP&D human release handoff packet v1.

    The packet must be inspectable and human-safe. Recommendations need explicit
    citations, fixture families must be present, unresolved blockers and rollback
    or post-apply validation checklists must be disclosed, and the packet cannot
    claim private artifacts, live execution, legal outcomes, consequential user
    actions, or active mutation flags.
    """

    issues: list[HandoffValidationIssue] = []

    if packet.get("version") not in {"human-release-handoff-packet-v1", "v1"}:
        issues.append(
            HandoffValidationIssue(
                "unsupported_version",
                "human release handoff packets must declare v1",
                "version",
            )
        )

    issues.extend(_recommendation_issues(packet.get("recommendations")))
    issues.extend(_fixture_family_issues(packet))
    issues.extend(_blocker_disclosure_issues(packet))
    issues.extend(_checklist_issues(packet))
    issues.extend(_artifact_issues(packet.get("artifacts")))
    issues.extend(_text_marker_issues(packet))
    issues.extend(_mutation_flag_issues(packet.get("mutation_flags")))

    return HandoffValidationResult(valid=not issues, issues=tuple(issues))


def assert_valid_human_release_handoff_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError if a handoff packet fails validation."""

    validate_human_release_handoff_packet_v1(packet).raise_for_issues()


def _recommendation_issues(value: Any) -> tuple[HandoffValidationIssue, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        return (
            HandoffValidationIssue(
                "missing_recommendations",
                "handoff packets must include cited recommendations",
                "recommendations",
            ),
        )

    issues: list[HandoffValidationIssue] = []
    for index, item in enumerate(value):
        path = f"recommendations[{index}]"
        if not isinstance(item, Mapping):
            issues.append(HandoffValidationIssue("invalid_recommendation", "recommendations must be objects", path))
            continue
        citations = item.get("citations") or item.get("source_evidence_ids") or item.get("source_ids")
        if not _non_empty_string_list(citations):
            issues.append(
                HandoffValidationIssue(
                    "uncited_recommendation",
                    "each recommendation must include at least one citation or source evidence id",
                    path,
                )
            )
    return tuple(issues)


def _fixture_family_issues(packet: Mapping[str, Any]) -> tuple[HandoffValidationIssue, ...]:
    value = packet.get("inspectable_fixture_families", packet.get("fixture_families"))
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        return (
            HandoffValidationIssue(
                "missing_inspectable_fixture_families",
                "handoff packets must list inspectable fixture families",
                "inspectable_fixture_families",
            ),
        )
    if not all(isinstance(item, str) and item.strip() for item in value):
        return (
            HandoffValidationIssue(
                "invalid_inspectable_fixture_families",
                "inspectable fixture families must be non-empty strings",
                "inspectable_fixture_families",
            ),
        )
    return ()


def _blocker_disclosure_issues(packet: Mapping[str, Any]) -> tuple[HandoffValidationIssue, ...]:
    disclosed = packet.get("unresolved_blockers_disclosed")
    blockers = packet.get("unresolved_blockers")
    if disclosed is not True:
        return (
            HandoffValidationIssue(
                "missing_unresolved_blocker_disclosure",
                "handoff packets must explicitly disclose unresolved blockers, even when none exist",
                "unresolved_blockers_disclosed",
            ),
        )
    if blockers is not None and not isinstance(blockers, Sequence):
        return (
            HandoffValidationIssue(
                "invalid_unresolved_blockers",
                "unresolved blockers must be a list when present",
                "unresolved_blockers",
            ),
        )
    return ()


def _checklist_issues(packet: Mapping[str, Any]) -> tuple[HandoffValidationIssue, ...]:
    rollback = packet.get("rollback_checklist")
    post_apply = packet.get("post_apply_validation_checklist")
    issues: list[HandoffValidationIssue] = []
    if not _non_empty_string_list(rollback):
        issues.append(
            HandoffValidationIssue(
                "missing_rollback_checklist",
                "handoff packets must include a rollback checklist",
                "rollback_checklist",
            )
        )
    if not _non_empty_string_list(post_apply):
        issues.append(
            HandoffValidationIssue(
                "missing_post_apply_validation_checklist",
                "handoff packets must include a post-apply validation checklist",
                "post_apply_validation_checklist",
            )
        )
    return tuple(issues)


def _artifact_issues(value: Any) -> tuple[HandoffValidationIssue, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return (HandoffValidationIssue("invalid_artifacts", "artifacts must be a list", "artifacts"),)

    issues: list[HandoffValidationIssue] = []
    for index, artifact in enumerate(value):
        path = f"artifacts[{index}]"
        if not isinstance(artifact, Mapping):
            issues.append(HandoffValidationIssue("invalid_artifact", "artifacts must be objects", path))
            continue
        privacy = _normalized_text(artifact.get("privacy_classification", ""))
        auth_scope = _normalized_text(artifact.get("auth_scope", ""))
        text = _normalized_text(" ".join(str(part) for part in artifact.values()))
        if privacy not in {"", "public", "commit_safe", "committed_fixture", "synthetic"}:
            issues.append(HandoffValidationIssue("private_or_authenticated_artifact", "artifacts must be public or synthetic", path))
        elif auth_scope and auth_scope not in {"public", "none", "unauthenticated"}:
            issues.append(HandoffValidationIssue("private_or_authenticated_artifact", "authenticated artifacts are not allowed", path))
        elif _contains_any(text, _PRIVATE_ARTIFACT_MARKERS):
            issues.append(HandoffValidationIssue("private_or_authenticated_artifact", "private or authenticated artifact markers are not allowed", path))
    return tuple(issues)


def _text_marker_issues(packet: Mapping[str, Any]) -> tuple[HandoffValidationIssue, ...]:
    text = _normalized_text(_stringify(packet))
    issues: list[HandoffValidationIssue] = []
    if _contains_any(text, _LIVE_EXECUTION_MARKERS):
        issues.append(
            HandoffValidationIssue(
                "live_execution_or_promotion_claim",
                "handoff packets cannot claim live execution or promotion",
                "$",
            )
        )
    if _contains_any(text, _LEGAL_OR_PERMITTING_GUARANTEE_MARKERS):
        issues.append(
            HandoffValidationIssue(
                "legal_or_permitting_outcome_guarantee",
                "handoff packets cannot guarantee legal or permitting outcomes",
                "$",
            )
        )
    if _contains_any(text, _CONSEQUENTIAL_ACTION_MARKERS):
        issues.append(
            HandoffValidationIssue(
                "consequential_action_language",
                "handoff packets cannot instruct or claim consequential official actions",
                "$",
            )
        )
    return tuple(issues)


def _mutation_flag_issues(value: Any) -> tuple[HandoffValidationIssue, ...]:
    if value in (None, {}, []):
        return ()
    issues: list[HandoffValidationIssue] = []
    if isinstance(value, Mapping):
        items = value.items()
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        items = ((str(item), True) for item in value)
    else:
        return (HandoffValidationIssue("invalid_mutation_flags", "mutation flags must be an object or list", "mutation_flags"),)

    for key, active in items:
        normalized_key = _normalized_flag(str(key))
        if normalized_key in {_normalized_flag(flag) for flag in FORBIDDEN_MUTATION_FLAGS} and bool(active):
            issues.append(
                HandoffValidationIssue(
                    "active_forbidden_mutation_flag",
                    "handoff packets cannot carry active source, registry, guardrail, prompt, release-state, or agent-state mutation flags",
                    f"mutation_flags.{key}",
                )
            )
    return tuple(issues)


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and any(
        isinstance(item, str) and item.strip() for item in value
    )


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    return any(marker in text for marker in markers)


def _normalized_text(value: Any) -> str:
    return " ".join(str(value).lower().replace("-", "_").split())


def _normalized_flag(value: str) -> str:
    return value.lower().replace("-", "_").strip()


def _stringify(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_stringify(item)}" for key, item in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return " ".join(_stringify(item) for item in value)
    return str(value)
