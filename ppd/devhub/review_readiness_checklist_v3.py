"""Validation for attended review readiness checklist v3.

The checklist is intentionally conservative. It is a preflight artifact for
attended review only, so it must not contain private facts, raw artifacts, live
execution claims, outcome guarantees, consequential DevHub action language, or
active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any, Iterable, Mapping, Sequence


_ALLOWED_DEFERRAL_DISPOSITIONS = {
    "none",
    "not_applicable",
    "blocked_until_cited",
    "blocked_until_owner_review",
    "requires_human_review",
    "deferred_with_owner",
    "rejected",
}

_PRIVATE_FACT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bprivate\s+(?:fact|value|document|upload|attachment|case|account)\b",
        r"\bauthenticated\s+(?:fact|value|page|portal|session|devhub|account)\b",
        r"\baccount-scoped\s+(?:fact|value|page|data|record)\b",
        r"\b(?:password|credential|cookie|session\s*token|mfa\s*code|captcha)\b",
        r"\b(?:permit|application|ivr)\s*(?:number|no\.?|#)\s*[:=]",
        r"\b(?:homeowner|contractor|applicant|owner)\s+(?:name|email|phone|address)\s*[:=]",
    )
)

_RAW_ARTIFACT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:har|trace|screenshot|video|browser\s*state|storage\s*state)\b",
        r"\b(?:playwright|selenium)\s+(?:trace|session|artifact|recording)\b",
        r"\braw\s+(?:crawl|html|pdf|body|download|artifact|response)\b",
        r"\b(?:crawl|browser|session|pdf)\s+artifact\b",
        r"\.(?:har|zip|webm|png|jpg|jpeg|pdf|warc)(?:\b|$)",
        r"\b/tmp/|\b/var/folders/|\b/home/[^\s]+/|\b/users/[^\s]+/",
    )
)

_LIVE_EXECUTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:ran|executed|clicked|submitted|uploaded|paid|scheduled|cancelled|canceled)\s+(?:in|on|against)\s+(?:live|production|devhub)",
        r"\blive\s+(?:crawl|browser|run|execution|submission|payment|upload|scheduling|cancellation)\b",
        r"\bproduction\s+(?:run|execution|browser|devhub|submission|payment|upload)\b",
        r"\bverified\s+by\s+(?:clicking|submitting|uploading|paying|scheduling|canceling|cancelling)\b",
    )
)

_OUTCOME_GUARANTEE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bguarantee(?:s|d)?\b.*\b(?:approval|issuance|permit|inspection|legal|compliance|outcome)\b",
        r"\bwill\s+(?:be\s+)?(?:approved|issued|accepted|legal|compliant|permitted)\b",
        r"\bensures?\s+(?:approval|issuance|acceptance|legal\s+compliance|permit\s+approval)\b",
        r"\b(?:approved|issued|accepted)\s+without\s+(?:review|delay|correction)\b",
    )
)

_CONSEQUENTIAL_ACTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bfinal\s+(?:submit|submission|payment|upload|schedule|scheduling|cancel|cancellation)\b",
        r"\b(?:submit|submitted|submission)\s+(?:the\s+)?(?:application|permit|request|plans|corrections|form)\b",
        r"\b(?:pay|paid|payment|purchase|purchased)\s+(?:the\s+)?(?:fee|fees|permit|invoice)\b",
        r"\b(?:upload|uploaded)\s+(?:the\s+)?(?:plans|corrections|documents|files|attachments)\b",
        r"\b(?:schedule|scheduled|scheduling)\s+(?:the\s+)?(?:inspection|appointment)\b",
        r"\b(?:cancel|cancelled|canceled|cancellation|withdraw|withdrawn)\s+(?:the\s+)?(?:permit|request|inspection|application)\b",
        r"\b(?:certify|certified|acknowledge|acknowledged)\s+(?:the\s+)?(?:application|submission|statement|terms)\b",
    )
)

_MUTATION_KEY_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"(?:^|_)(?:source|surface_registry|guardrail|prompt|monitoring|release_state|agent_state)_?mutation(?:_|$)",
        r"(?:^|_)(?:mutate|mutates|mutating)_(?:source|surface_registry|guardrail|prompt|monitoring|release_state|agent_state)(?:_|$)",
        r"(?:^|_)(?:source|surface_registry|guardrail|prompt|monitoring|release_state|agent_state)_?(?:write|update|patch|publish|deploy|activate|enable)(?:_|$)",
    )
)

_MUTATION_VALUE_PATTERN = re.compile(r"\b(?:active|enabled|true|write|update|patch|publish|deploy|mutate)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ChecklistValidationError:
    """A deterministic checklist validation failure."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class ChecklistValidationResult:
    """Validation result for attended review readiness checklist v3."""

    ok: bool
    errors: tuple[ChecklistValidationError, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": [error.__dict__ for error in self.errors],
        }


def load_checklist(path: str | Path) -> Mapping[str, Any]:
    """Load a JSON checklist from disk without touching live PP&D systems."""

    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError("checklist root must be a JSON object")
    return value


def validate_checklist_v3(checklist: Mapping[str, Any]) -> ChecklistValidationResult:
    """Validate an attended review readiness checklist v3 object."""

    errors: list[ChecklistValidationError] = []
    version = checklist.get("version")
    if version not in (3, "3", "v3", "attended-review-readiness-v3"):
        errors.append(_error("version", "invalid_version", "checklist version must be v3"))

    rows = checklist.get("rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
        errors.append(_error("rows", "missing_rows", "checklist rows must be a list"))
        rows = []

    for index, row in enumerate(rows):
        row_path = f"rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(_error(row_path, "invalid_row", "checklist row must be an object"))
            continue
        errors.extend(_validate_row(row, row_path))

    errors.extend(_scan_for_disallowed_content(checklist))
    return ChecklistValidationResult(ok=not errors, errors=tuple(errors))


def assert_checklist_v3_ready(checklist: Mapping[str, Any]) -> None:
    """Raise ValueError when a checklist is not ready for attended review."""

    result = validate_checklist_v3(checklist)
    if result.ok:
        return
    details = "; ".join(f"{error.path}: {error.code}" for error in result.errors)
    raise ValueError(f"attended review readiness checklist v3 rejected: {details}")


def _validate_row(row: Mapping[str, Any], row_path: str) -> list[ChecklistValidationError]:
    errors: list[ChecklistValidationError] = []
    row_id = row.get("id") or row.get("checklist_id")
    if not _present_text(row_id):
        errors.append(_error(f"{row_path}.id", "missing_row_id", "checklist row must have a stable id"))

    if not _has_citation(row):
        errors.append(_error(row_path, "uncited_row", "checklist row must cite source evidence"))

    if not _present_list_or_text(row.get("acceptance_criteria")):
        errors.append(
            _error(
                f"{row_path}.acceptance_criteria",
                "missing_acceptance_criteria",
                "checklist row must define acceptance criteria",
            )
        )

    disposition = row.get("unresolved_deferral_disposition")
    if not _present_text(disposition):
        errors.append(
            _error(
                f"{row_path}.unresolved_deferral_disposition",
                "missing_unresolved_deferral_disposition",
                "checklist row must state how unresolved deferrals are disposed",
            )
        )
    elif str(disposition).strip() not in _ALLOWED_DEFERRAL_DISPOSITIONS:
        errors.append(
            _error(
                f"{row_path}.unresolved_deferral_disposition",
                "invalid_unresolved_deferral_disposition",
                "unresolved deferral disposition is not an allowed v3 value",
            )
        )

    if not _present_list_or_text(row.get("rollback_verification")):
        errors.append(
            _error(
                f"{row_path}.rollback_verification",
                "missing_rollback_verification",
                "checklist row must verify rollback or no-side-effect behavior",
            )
        )

    if not _present_text(row.get("reviewer_owner")):
        errors.append(
            _error(
                f"{row_path}.reviewer_owner",
                "missing_reviewer_owner",
                "checklist row must name the reviewer owner role",
            )
        )

    return errors


def _has_citation(row: Mapping[str, Any]) -> bool:
    citation_fields = (
        "citation_ids",
        "citations",
        "source_evidence_ids",
        "source_citations",
        "evidence_ids",
    )
    for field in citation_fields:
        value = row.get(field)
        if _present_list_or_text(value):
            return True
    return False


def _scan_for_disallowed_content(value: Any) -> list[ChecklistValidationError]:
    errors: list[ChecklistValidationError] = []
    for path, key, scalar in _walk_scalars(value):
        text = str(scalar)
        checks = (
            ("private_or_authenticated_fact", _PRIVATE_FACT_PATTERNS),
            ("raw_artifact", _RAW_ARTIFACT_PATTERNS),
            ("live_execution_claim", _LIVE_EXECUTION_PATTERNS),
            ("outcome_guarantee", _OUTCOME_GUARANTEE_PATTERNS),
            ("consequential_action_language", _CONSEQUENTIAL_ACTION_PATTERNS),
        )
        for code, patterns in checks:
            if any(pattern.search(text) for pattern in patterns):
                errors.append(_error(path, code, f"checklist contains disallowed {code.replace('_', ' ')}"))
                break

        if key and _is_active_mutation_flag(key, scalar):
            errors.append(
                _error(
                    path,
                    "active_mutation_flag",
                    "checklist must not carry active source, registry, guardrail, prompt, monitoring, release-state, or agent-state mutation flags",
                )
            )
    return errors


def _walk_scalars(value: Any, path: str = "$", key: str | None = None) -> Iterable[tuple[str, str | None, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}"
            yield from _walk_scalars(child_value, child_path, child_key_text)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child_value in enumerate(value):
            yield from _walk_scalars(child_value, f"{path}[{index}]", key)
        return
    yield path, key, value


def _is_active_mutation_flag(key: str, value: Any) -> bool:
    if not any(pattern.search(key) for pattern in _MUTATION_KEY_PATTERNS):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if value is None:
        return False
    return bool(_MUTATION_VALUE_PATTERN.search(str(value)))


def _present_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _present_list_or_text(value: Any) -> bool:
    if _present_text(value):
        return True
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_present_text(item) or isinstance(item, Mapping) for item in value)
    return False


def _error(path: str, code: str, message: str) -> ChecklistValidationError:
    return ChecklistValidationError(path=path, code=code, message=message)
