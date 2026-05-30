"""Validation for PP&D refresh implementation proposal v2 payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any


_FORBIDDEN_ARTIFACT_RE = re.compile(
    r"\b(raw crawl|crawl output|downloaded pdf|\.pdf\b|session storage|local storage|"
    r"browser trace|playwright trace|auth state|cookies?\.json|storage_state|har|"
    r"screenshot|devhub session)\b",
    re.IGNORECASE,
)

_PRIVATE_FACT_RE = re.compile(
    r"\b(private|authenticated|logged[- ]in|account[- ]specific|personal data|"
    r"permit applicant|owner email|owner phone|session cookie|bearer token|api key|"
    r"password|secret)\b",
    re.IGNORECASE,
)

_LIVE_EXECUTION_RE = re.compile(
    r"\b(executed live|live run|ran against devhub|promoted to production|"
    r"deployed|released|submitted|uploaded|certified|paid|cancelled|created account)\b",
    re.IGNORECASE,
)

_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|approval guaranteed|permit will issue|"
    r"legal advice|legally sufficient|ensures compliance|cannot be denied)\b",
    re.IGNORECASE,
)

_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(file the permit|submit the application|pay the fee|certify|sign|"
    r"cancel the permit|schedule inspection|make the appeal|rely on this to)\b",
    re.IGNORECASE,
)

_MUTATION_KEYS = {
    "active_source_mutation",
    "active_surface_registry_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
}

_MUTATION_TARGETS = {
    "source",
    "surface-registry",
    "surface_registry",
    "guardrail",
    "prompt",
    "monitoring",
    "release-state",
    "release_state",
    "agent-state",
    "agent_state",
}

_REQUIRED_ROW_KEYS = {
    "source_target_id": "missing source target id",
    "surface_target_id": "missing surface target id",
    "guardrail_target_id": "missing guardrail target id",
    "depends_on": "missing dependency ordering",
    "rollback_notes": "missing rollback notes",
    "reviewer_owner": "missing reviewer owner",
}


def validate_refresh_implementation_proposal_v2(proposal: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a refresh implementation proposal v2.

    The validator is intentionally schema-light so it can run before proposal data is
    normalized. It accepts rows under ``patch_rows`` or ``patches`` and reports stable
    lowercase error fragments for daemon-side matching.
    """

    errors: list[str] = []
    if proposal.get("proposal_version") not in {"refresh-implementation-v2", "v2", 2}:
        errors.append("proposal_version must be refresh-implementation-v2")

    rows = proposal.get("patch_rows", proposal.get("patches"))
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("proposal must include patch_rows")
        rows = []

    _check_active_mutation_flags(proposal, errors, "proposal")
    _check_text(str(proposal.get("summary", "")), errors, "proposal summary")
    _check_text(str(proposal.get("impact", "")), errors, "proposal impact")

    for index, row in enumerate(rows):
        label = f"patch row {index}"
        if not isinstance(row, Mapping):
            errors.append(f"{label} must be an object")
            continue

        citations = row.get("citations", row.get("source_citations"))
        if not _has_citation(citations):
            errors.append(f"{label}: uncited patch row")

        for key, message in _REQUIRED_ROW_KEYS.items():
            if _is_missing(row.get(key)):
                errors.append(f"{label}: {message}")

        _check_active_mutation_flags(row, errors, label)
        for key, value in row.items():
            if isinstance(value, str):
                _check_text(value, errors, f"{label} {key}")
            elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                for item in value:
                    if isinstance(item, str):
                        _check_text(item, errors, f"{label} {key}")

    return errors


def assert_valid_refresh_implementation_proposal_v2(proposal: Mapping[str, Any]) -> None:
    errors = validate_refresh_implementation_proposal_v2(proposal)
    if errors:
        raise ValueError("refresh implementation proposal v2 validation failed: " + "; ".join(errors))


def _has_citation(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(isinstance(item, str) and item.strip() for item in value)
    return False


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return len(value) == 0
    return False


def _check_active_mutation_flags(obj: Mapping[str, Any], errors: list[str], label: str) -> None:
    for key in _MUTATION_KEYS:
        if obj.get(key) is True:
            errors.append(f"{label}: active mutation flag {key} is not allowed")

    mutation = obj.get("mutation")
    if isinstance(mutation, Mapping):
        target = str(mutation.get("target", "")).lower()
        active = mutation.get("active") is True or mutation.get("enabled") is True
        if active and target in _MUTATION_TARGETS:
            errors.append(f"{label}: active {target} mutation is not allowed")

    flags = obj.get("mutation_flags")
    if isinstance(flags, Mapping):
        for target, active in flags.items():
            if active is True and str(target).lower() in _MUTATION_TARGETS:
                errors.append(f"{label}: active {target} mutation is not allowed")


def _check_text(text: str, errors: list[str], label: str) -> None:
    checks = (
        (_FORBIDDEN_ARTIFACT_RE, "raw crawl/pdf/session/browser artifact"),
        (_PRIVATE_FACT_RE, "private or authenticated fact"),
        (_LIVE_EXECUTION_RE, "live execution or promotion claim"),
        (_OUTCOME_GUARANTEE_RE, "legal or permitting outcome guarantee"),
        (_CONSEQUENTIAL_ACTION_RE, "consequential action language"),
    )
    for pattern, message in checks:
        if pattern.search(text):
            errors.append(f"{label}: {message}")
