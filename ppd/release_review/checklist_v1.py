"""Deterministic validator for the PP&D release reviewer go/no-go checklist v1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re
from typing import Any, Iterable, Mapping, Sequence


REQUIRED_CHECKLIST_ITEMS = (
    "scope-boundary-review",
    "source-citation-review",
    "private-artifact-review",
    "rollback-readiness-review",
    "validation-replay-review",
    "unresolved-risk-acknowledgement-review",
    "validation-command-review",
    "release-language-review",
    "mutation-flag-review",
)

REQUIRED_EVIDENCE_FIELDS = ("checklist_item_id", "citation")
REQUIRED_ROLLBACK_CONFIRMATIONS = (
    "rollback_owner_confirmed",
    "rollback_steps_confirmed",
    "rollback_stop_condition_confirmed",
)
REQUIRED_VALIDATION_REPLAY_CONFIRMATIONS = (
    "validation_replay_owner_confirmed",
    "validation_replay_inputs_confirmed",
    "validation_replay_expected_results_confirmed",
)
REQUIRED_RISK_PLACEHOLDERS = (
    "unresolved_risks_acknowledged",
    "unresolved_risk_owner_placeholder",
    "unresolved_risk_followup_placeholder",
)
MUTATION_FLAG_FIELDS = (
    "artifact_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "fixture_mutation_enabled",
    "agent_state_mutation_enabled",
)

PRIVATE_ARTIFACT_PATTERNS = (
    re.compile(r"(^|/)(\.auth|auth|auth-state|storage-state|session|sessions|cookies)(/|$)", re.IGNORECASE),
    re.compile(r"\.(har|trace|zip|png|jpe?g|webp|mp4|webm)$", re.IGNORECASE),
    re.compile(r"(^|/)(screenshots?|traces?|har|browser-state|playwright-report)(/|$)", re.IGNORECASE),
)
RAW_DATA_PATTERNS = (
    re.compile(r"(^|/)(raw|crawl|crawls|downloads?|pdfs?)(/|$)", re.IGNORECASE),
    re.compile(r"\.(warc|pdf|html?|mhtml|bin|dat)$", re.IGNORECASE),
)
LIVE_EXECUTION_PATTERNS = (
    re.compile(r"\b(live crawl|live execution|executed live|ran against production|release complete|released successfully)\b", re.IGNORECASE),
)
GUARANTEE_PATTERNS = (
    re.compile(r"\b(guarantee[sd]?|will be approved|permit will issue|legal outcome|permitting outcome)\b", re.IGNORECASE),
)
CONSEQUENTIAL_ACTION_PATTERNS = (
    re.compile(r"\b(submit|certify|upload corrections?|schedule inspection|cancel permit|pay fee|purchase permit|create account)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ReleaseChecklistFinding:
    """A single release checklist validation failure."""

    code: str
    message: str
    location: str


def validate_release_reviewer_go_no_go_checklist_v1(checklist: Mapping[str, Any]) -> list[ReleaseChecklistFinding]:
    """Return every deterministic rejection for a checklist candidate.

    The validator is intentionally schema-light so it can be used against hand-authored
    JSON/YAML-like review records while still enforcing the non-negotiable release gates.
    """

    findings: list[ReleaseChecklistFinding] = []
    checklist_items = _mapping(checklist.get("checklist_items"))
    evidence_rows = _sequence(checklist.get("evidence_citation_coverage"))
    artifacts = _sequence(checklist.get("artifacts"))
    validation_commands = _sequence(checklist.get("validation_commands"))
    claims = _text_values(checklist.get("claims")) + _text_values(checklist.get("notes"))

    for item_id in REQUIRED_CHECKLIST_ITEMS:
        item = checklist_items.get(item_id)
        if not isinstance(item, Mapping):
            findings.append(_finding("missing-checklist-item", "Required checklist item is missing.", f"checklist_items.{item_id}"))
        elif item.get("status") not in {"pass", "acknowledged", "not_applicable_with_citation"}:
            findings.append(_finding("unchecked-checklist-item", "Checklist item must be passed, acknowledged, or explicitly cited as not applicable.", f"checklist_items.{item_id}.status"))

    covered_item_ids: set[str] = set()
    for index, row in enumerate(evidence_rows):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-evidence-row", "Evidence citation coverage rows must be objects.", f"evidence_citation_coverage[{index}]"))
            continue
        for field in REQUIRED_EVIDENCE_FIELDS:
            if not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-evidence-field", "Evidence citation coverage row is missing a required field.", f"evidence_citation_coverage[{index}].{field}"))
        item_id = row.get("checklist_item_id")
        citation = row.get("citation")
        if _non_empty_text(item_id) and _non_empty_text(citation):
            covered_item_ids.add(str(item_id))

    for item_id in REQUIRED_CHECKLIST_ITEMS:
        if item_id not in covered_item_ids:
            findings.append(_finding("missing-evidence-coverage", "Required checklist item lacks an evidence citation coverage row.", f"evidence_citation_coverage.{item_id}"))

    findings.extend(_require_truthy(checklist, REQUIRED_ROLLBACK_CONFIRMATIONS, "missing-rollback-confirmation"))
    findings.extend(_require_truthy(checklist, REQUIRED_VALIDATION_REPLAY_CONFIRMATIONS, "missing-validation-replay-confirmation"))
    findings.extend(_require_truthy(checklist, REQUIRED_RISK_PLACEHOLDERS, "missing-unresolved-risk-placeholder"))

    if not validation_commands:
        findings.append(_finding("missing-validation-command", "At least one deterministic validation command is required.", "validation_commands"))
    for index, command in enumerate(validation_commands):
        if not _valid_command(command):
            findings.append(_finding("invalid-validation-command", "Validation commands must be non-empty argv arrays with string entries.", f"validation_commands[{index}]"))

    for index, artifact in enumerate(artifacts):
        artifact_text = _artifact_text(artifact)
        artifact_path = _artifact_path(artifact)
        if _matches_any(PRIVATE_ARTIFACT_PATTERNS, artifact_text):
            findings.append(_finding("private-or-browser-artifact", "Private, authenticated, session, browser, screenshot, trace, HAR, or auth artifacts are not releaseable.", f"artifacts[{index}]"))
        if artifact_path and _matches_any(RAW_DATA_PATTERNS, artifact_path):
            findings.append(_finding("raw-crawl-or-download-artifact", "Raw crawl, PDF, downloaded, or extracted body data must not be committed as a release artifact.", f"artifacts[{index}]"))

    for index, text in enumerate(claims):
        if _matches_any(LIVE_EXECUTION_PATTERNS, text):
            findings.append(_finding("live-execution-or-release-complete-claim", "Release review must not claim live execution or release completion.", f"claims[{index}]"))
        if _matches_any(GUARANTEE_PATTERNS, text):
            findings.append(_finding("legal-or-permitting-guarantee", "Release review must not guarantee legal or permitting outcomes.", f"claims[{index}]"))
        if _matches_any(CONSEQUENTIAL_ACTION_PATTERNS, text):
            findings.append(_finding("consequential-action-language", "Release review must not direct consequential official actions.", f"claims[{index}]"))

    for field in MUTATION_FLAG_FIELDS:
        if checklist.get(field) is True:
            findings.append(_finding("active-mutation-flag", "Release review must not enable artifact, prompt, release-state, fixture, or agent-state mutation.", field))

    return findings


def _require_truthy(checklist: Mapping[str, Any], fields: Iterable[str], code: str) -> list[ReleaseChecklistFinding]:
    findings: list[ReleaseChecklistFinding] = []
    for field in fields:
        if checklist.get(field) is not True:
            findings.append(_finding(code, "Required release readiness confirmation is missing.", field))
    return findings


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return value
    return ()


def _text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value if item is not None]
    return []


def _artifact_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(str(part) for part in value.values() if part is not None)
    return str(value)


def _artifact_path(value: Any) -> str:
    if isinstance(value, Mapping):
        raw_path = value.get("path") or value.get("artifact_path") or ""
    else:
        raw_path = value
    path = str(raw_path)
    if not path:
        return ""
    return PurePosixPath(path.replace("\\", "/")).as_posix()


def _valid_command(command: Any) -> bool:
    return isinstance(command, list) and bool(command) and all(isinstance(part, str) and bool(part.strip()) for part in command)


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _matches_any(patterns: Iterable[re.Pattern[str]], value: str) -> bool:
    return any(pattern.search(value) for pattern in patterns)


def _finding(code: str, message: str, location: str) -> ReleaseChecklistFinding:
    return ReleaseChecklistFinding(code=code, message=message, location=location)
