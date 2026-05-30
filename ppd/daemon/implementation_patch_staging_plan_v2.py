"""Validation for PP&D implementation patch staging plan v2.

The validator is intentionally side-effect free. It accepts plain dictionaries so
supervisor code, fixtures, and tests can use the same checks without importing a
larger daemon contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


ACTIVE_MUTATION_KEYS = frozenset(
    {
        "registry",
        "source",
        "surface",
        "guardrail",
        "prompt",
        "monitoring",
        "release_state",
        "agent_state",
    }
)

PRIVATE_FACT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bauthenticated\b",
        r"\bprivate\s+(?:devhub|account|permit|case|session|page|field|fact|value)s?\b",
        r"\bcookie\b",
        r"\bcredential\b",
        r"\bpassword\b",
        r"\bmfa\b",
        r"\bsession\s+(?:token|state|storage|file|cookie)\b",
        r"\bpayment\s+(?:card|detail|account|token)\b",
        r"\bprivate\s+upload\b",
    )
)

RAW_ARTIFACT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\.har\b",
        r"\.trace\b",
        r"trace\.zip\b",
        r"storage[_-]?state",
        r"auth[_-]?state",
        r"session[_-]?(?:state|storage|cookies?)",
        r"browser[_-]?(?:profile|context|state)",
        r"raw[_-]?(?:crawl|html|pdf|download|body)",
        r"crawl[_-]?dump",
        r"downloaded[_-]?(?:document|pdf)",
        r"screenshot",
        r"playwright-report",
    )
)

LIVE_EXECUTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bexecuted\s+(?:live|against\s+devhub|in\s+production)\b",
        r"\blive\s+(?:crawl|run|execution|promotion)\b",
        r"\bpromoted\s+(?:to|into)\s+(?:production|active|live)\b",
        r"\bdeployed\s+(?:to|into)\s+(?:production|active|live)\b",
        r"\bsubmitted\s+(?:permit|application|correction|payment)\b",
        r"\bpaid\s+(?:fee|fees)\b",
        r"\bscheduled\s+inspection\b",
    )
)

OUTCOME_GUARANTEE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bguarantee(?:d|s)?\s+(?:approval|issuance|permit|inspection|compliance|outcome)\b",
        r"\bwill\s+(?:be\s+)?(?:approved|issued|accepted|compliant|valid)\b",
        r"\bensures?\s+(?:approval|issuance|acceptance|compliance)\b",
        r"\blegally\s+(?:valid|sufficient|approved|compliant)\b",
        r"\bpermit\s+approval\s+is\s+certain\b",
    )
)

FINAL_OFFICIAL_ACTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bfinal\s+(?:submit|submission|certification|payment|upload|cancellation|scheduling)\b",
        r"\bofficial\s+(?:submit|submission|certification|payment|upload|cancellation|scheduling|action)\b",
        r"\bcertify\s+and\s+submit\b",
        r"\bclick\s+(?:submit|pay|certify|schedule|cancel)\b",
        r"\bmake\s+official\b",
    )
)


@dataclass(frozen=True)
class ValidationIssue:
    """A single staging plan validation failure."""

    code: str
    message: str
    candidate_id: str | None = None

    def as_dict(self) -> dict[str, str]:
        result = {"code": self.code, "message": self.message}
        if self.candidate_id is not None:
            result["candidate_id"] = self.candidate_id
        return result


class StagingPlanValidationError(ValueError):
    """Raised when a staging plan v2 fails validation."""

    def __init__(self, issues: Sequence[ValidationIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.code}: {issue.message}" for issue in self.issues)
        super().__init__(detail)


def validate_implementation_patch_staging_plan_v2(plan: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for an implementation patch staging plan v2.

    Expected shape is deliberately small:
    - ``version`` must be ``implementation_patch_staging_plan_v2``.
    - ``patch_candidates`` must be a non-empty list of dictionaries.
    - each candidate must include target_id, citations, depends_on,
      fixture_migration_notes, and rollback_checkpoints.
    """

    issues: list[ValidationIssue] = []
    if plan.get("version") != "implementation_patch_staging_plan_v2":
        issues.append(
            ValidationIssue(
                "invalid_version",
                "plan version must be implementation_patch_staging_plan_v2",
            )
        )

    candidates = plan.get("patch_candidates")
    if not isinstance(candidates, list) or not candidates:
        issues.append(
            ValidationIssue(
                "missing_patch_candidates",
                "plan must contain at least one patch candidate",
            )
        )
        candidates = []

    issues.extend(_check_mutation_flags(plan, None))
    issues.extend(_check_text_policy(plan, None))
    issues.extend(_check_artifacts(plan, None))

    seen_targets: set[str] = set()
    all_targets = {
        candidate.get("target_id")
        for candidate in candidates
        if isinstance(candidate, Mapping) and isinstance(candidate.get("target_id"), str)
    }

    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping):
            issues.append(
                ValidationIssue(
                    "invalid_patch_candidate",
                    f"patch candidate at index {index} must be an object",
                )
            )
            continue

        candidate_id = _candidate_label(candidate, index)
        target_id = candidate.get("target_id")
        if not _non_empty_string(target_id):
            issues.append(
                ValidationIssue(
                    "missing_target_id",
                    "patch candidate must include a non-empty target_id",
                    candidate_id,
                )
            )
        elif target_id in seen_targets:
            issues.append(
                ValidationIssue(
                    "duplicate_target_id",
                    f"target_id {target_id!r} appears more than once",
                    candidate_id,
                )
            )

        citations = candidate.get("citations")
        if not _non_empty_string_list(citations):
            issues.append(
                ValidationIssue(
                    "uncited_patch_candidate",
                    "patch candidate must include at least one citation",
                    candidate_id,
                )
            )

        if "depends_on" not in candidate:
            issues.append(
                ValidationIssue(
                    "missing_dependency_ordering",
                    "patch candidate must declare depends_on, even when empty",
                    candidate_id,
                )
            )
        else:
            depends_on = candidate.get("depends_on")
            if not isinstance(depends_on, list) or not all(isinstance(item, str) and item.strip() for item in depends_on):
                issues.append(
                    ValidationIssue(
                        "invalid_dependency_ordering",
                        "depends_on must be a list of target_id strings",
                        candidate_id,
                    )
                )
            else:
                for dependency in depends_on:
                    if dependency not in all_targets:
                        issues.append(
                            ValidationIssue(
                                "unknown_dependency_target",
                                f"dependency {dependency!r} is not another target_id in this plan",
                                candidate_id,
                            )
                        )
                    elif dependency not in seen_targets:
                        issues.append(
                            ValidationIssue(
                                "missing_dependency_ordering",
                                f"dependency {dependency!r} must appear before dependent candidate",
                                candidate_id,
                            )
                        )

        if not _non_empty_string(candidate.get("fixture_migration_notes")):
            issues.append(
                ValidationIssue(
                    "missing_fixture_migration_notes",
                    "patch candidate must document fixture migration notes",
                    candidate_id,
                )
            )

        rollback_checkpoints = candidate.get("rollback_checkpoints")
        if not _non_empty_string_list(rollback_checkpoints):
            issues.append(
                ValidationIssue(
                    "missing_rollback_checkpoints",
                    "patch candidate must include rollback checkpoints",
                    candidate_id,
                )
            )

        issues.extend(_check_mutation_flags(candidate, candidate_id))
        issues.extend(_check_text_policy(candidate, candidate_id))
        issues.extend(_check_artifacts(candidate, candidate_id))

        if isinstance(target_id, str):
            seen_targets.add(target_id)

    return issues


def assert_valid_implementation_patch_staging_plan_v2(plan: Mapping[str, Any]) -> None:
    """Raise ``StagingPlanValidationError`` if a plan fails v2 validation."""

    issues = validate_implementation_patch_staging_plan_v2(plan)
    if issues:
        raise StagingPlanValidationError(issues)


def _candidate_label(candidate: Mapping[str, Any], index: int) -> str:
    target_id = candidate.get("target_id")
    if isinstance(target_id, str) and target_id.strip():
        return target_id
    candidate_id = candidate.get("candidate_id")
    if isinstance(candidate_id, str) and candidate_id.strip():
        return candidate_id
    return f"index:{index}"


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _check_mutation_flags(value: Any, candidate_id: str | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, leaf in _walk(value):
        key = path[-1] if path else ""
        normalized_key = key.replace("-", "_").lower()
        if normalized_key.endswith("_mutation"):
            normalized_key = normalized_key[: -len("_mutation")]
        if normalized_key.endswith("_mutation_flag"):
            normalized_key = normalized_key[: -len("_mutation_flag")]
        if normalized_key in ACTIVE_MUTATION_KEYS and _truthy_mutation_value(leaf):
            issues.append(
                ValidationIssue(
                    "active_mutation_flag",
                    f"active {normalized_key} mutation flag is not allowed at {_format_path(path)}",
                    candidate_id,
                )
            )
        if normalized_key in {f"active_{name}_mutation" for name in ACTIVE_MUTATION_KEYS} and _truthy_mutation_value(leaf):
            issues.append(
                ValidationIssue(
                    "active_mutation_flag",
                    f"active mutation flag is not allowed at {_format_path(path)}",
                    candidate_id,
                )
            )
    return issues


def _truthy_mutation_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"active", "true", "yes", "enable", "enabled", "mutate", "mutation"}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return value is not None


def _check_text_policy(value: Any, candidate_id: str | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    text_items = [(path, text) for path, text in _walk_strings(value)]
    policies = (
        ("private_or_authenticated_fact", PRIVATE_FACT_PATTERNS),
        ("live_execution_or_promotion_claim", LIVE_EXECUTION_PATTERNS),
        ("legal_or_permitting_outcome_guarantee", OUTCOME_GUARANTEE_PATTERNS),
        ("final_official_action_language", FINAL_OFFICIAL_ACTION_PATTERNS),
    )
    for path, text in text_items:
        for code, patterns in policies:
            if any(pattern.search(text) for pattern in patterns):
                issues.append(
                    ValidationIssue(
                        code,
                        f"prohibited language found at {_format_path(path)}",
                        candidate_id,
                    )
                )
    return issues


def _check_artifacts(value: Any, candidate_id: str | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, text in _walk_strings(value):
        if any(pattern.search(text) for pattern in RAW_ARTIFACT_PATTERNS):
            issues.append(
                ValidationIssue(
                    "raw_crawl_pdf_session_or_browser_artifact",
                    f"raw crawl/PDF/session/browser artifact reference found at {_format_path(path)}",
                    candidate_id,
                )
            )
    return issues


def _walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = path + (str(key),)
            yield child_path, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = path + (str(index),)
            yield child_path, child
            yield from _walk(child, child_path)


def _walk_strings(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_strings(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, path + (str(index),))


def _format_path(path: tuple[str, ...]) -> str:
    if not path:
        return "$"
    return "$" + "".join(f"[{part!r}]" for part in path)
