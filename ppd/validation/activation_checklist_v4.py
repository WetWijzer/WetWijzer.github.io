"""Validation for inactive activation checklist v4 artifacts.

The validator is intentionally text-based and deterministic. It is meant for
committed PP&D planning/checklist fixtures, not live DevHub automation.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ChecklistFinding:
    """A validation issue found in an inactive activation checklist."""

    code: str
    message: str


@dataclass(frozen=True)
class RequiredMarker:
    code: str
    message: str
    patterns: tuple[re.Pattern[str], ...]


@dataclass(frozen=True)
class ProhibitedMarker:
    code: str
    message: str
    pattern: re.Pattern[str]


_REQUIRED_MARKERS: tuple[RequiredMarker, ...] = (
    RequiredMarker(
        code="missing_smoke_replay_reference",
        message="Inactive activation checklist v4 must reference smoke replay evidence.",
        patterns=(
            re.compile(r"\bsmoke\s+replay\b", re.IGNORECASE),
            re.compile(r"\breplay\s+(fixture|transcript|reference|evidence)\b", re.IGNORECASE),
        ),
    ),
    RequiredMarker(
        code="missing_reviewer_prerequisites",
        message="Inactive activation checklist v4 must include reviewer-controlled activation prerequisites.",
        patterns=(
            re.compile(r"\breviewer[- ]controlled\b", re.IGNORECASE),
            re.compile(r"\bactivation\s+prerequisites?\b", re.IGNORECASE),
        ),
    ),
    RequiredMarker(
        code="missing_signoff_placeholders",
        message="Inactive activation checklist v4 must include signoff placeholders.",
        patterns=(
            re.compile(r"\bsign[- ]?off\b", re.IGNORECASE),
            re.compile(r"\bplaceholder\b|\bTBD\b|\bnot\s+signed\b", re.IGNORECASE),
        ),
    ),
    RequiredMarker(
        code="missing_source_freshness_hold_clearance",
        message="Inactive activation checklist v4 must define source freshness hold clearance criteria.",
        patterns=(
            re.compile(r"\bsource\s+freshness\b", re.IGNORECASE),
            re.compile(r"\bhold\s+clearance\b|\bclearance\s+criteria\b", re.IGNORECASE),
        ),
    ),
    RequiredMarker(
        code="missing_rollback_checkpoint_rows",
        message="Inactive activation checklist v4 must include rollback checkpoint rows.",
        patterns=(
            re.compile(r"\brollback\b", re.IGNORECASE),
            re.compile(r"\bcheckpoint\s+rows?\b|\|[^\n]*checkpoint[^\n]*\|", re.IGNORECASE),
        ),
    ),
    RequiredMarker(
        code="missing_post_activation_smoke_checks",
        message="Inactive activation checklist v4 must include post-activation smoke checks.",
        patterns=(
            re.compile(r"\bpost[- ]activation\b", re.IGNORECASE),
            re.compile(r"\bsmoke\s+checks?\b", re.IGNORECASE),
        ),
    ),
    RequiredMarker(
        code="missing_agent_notification_notes",
        message="Inactive activation checklist v4 must include agent notification notes.",
        patterns=(
            re.compile(r"\bagent\s+notification\b", re.IGNORECASE),
            re.compile(r"\bnotes?\b", re.IGNORECASE),
        ),
    ),
    RequiredMarker(
        code="missing_validation_commands",
        message="Inactive activation checklist v4 must include validation commands.",
        patterns=(
            re.compile(r"\bvalidation\s+commands?\b", re.IGNORECASE),
            re.compile(r"\bpython3\b|\bpytest\b|\bppd_daemon\.py\b", re.IGNORECASE),
        ),
    ),
)

_PROHIBITED_MARKERS: tuple[ProhibitedMarker, ...] = (
    ProhibitedMarker(
        code="active_activation_claim",
        message="Inactive activation checklist v4 must not claim activation is active, enabled, or complete.",
        pattern=re.compile(
            r"\b(activation\s+(is\s+)?(active|enabled|live|complete|completed)|"
            r"activated\s+(successfully|in\s+production)|production\s+activation)\b",
            re.IGNORECASE,
        ),
    ),
    ProhibitedMarker(
        code="private_session_auth_artifact",
        message="Inactive activation checklist v4 must not reference private session, auth, trace, HAR, screenshot, cookie, or credential artifacts.",
        pattern=re.compile(
            r"\b(auth\s*state|storage_state|cookie|credential|password|session\s+file|"
            r"private\s+session|HAR\b|trace\.zip|screenshot|MFA\s+secret|token)\b",
            re.IGNORECASE,
        ),
    ),
    ProhibitedMarker(
        code="official_action_completion_claim",
        message="Inactive activation checklist v4 must not claim official PP&D actions were completed.",
        pattern=re.compile(
            r"\b(submitted|uploaded|certified|paid|scheduled|cancelled|canceled|withdrawn)\b"
            r"[^\n]{0,80}\b(permit|application|inspection|fee|payment|correction|official\s+record)\b",
            re.IGNORECASE,
        ),
    ),
    ProhibitedMarker(
        code="legal_or_permitting_guarantee",
        message="Inactive activation checklist v4 must not provide legal or permitting guarantees.",
        pattern=re.compile(
            r"\b(guarantee[sd]?|legally\s+binding|permit\s+will\s+be\s+(approved|issued)|"
            r"approval\s+guaranteed|compliance\s+guaranteed)\b",
            re.IGNORECASE,
        ),
    ),
    ProhibitedMarker(
        code="active_mutation_flag",
        message="Inactive activation checklist v4 must not enable active mutation flags.",
        pattern=re.compile(
            r"\b(active_mutation|mutation_enabled|write_mode|live_write|allow_submit|allow_upload|"
            r"allow_payment|allow_schedule)\s*[:=]\s*(true|1|yes|enabled|on)\b",
            re.IGNORECASE,
        ),
    ),
)

_VERSION_PATTERN = re.compile(r"\bactivation\s+checklist\s+v4\b", re.IGNORECASE)
_INACTIVE_PATTERN = re.compile(r"\b(inactive|disabled|not\s+active|not\s+enabled|read[- ]only\s+validation)\b", re.IGNORECASE)


def validate_inactive_activation_checklist_v4(text: str) -> list[ChecklistFinding]:
    """Return validation findings for an inactive activation checklist v4 body."""

    findings: list[ChecklistFinding] = []

    if not _VERSION_PATTERN.search(text):
        findings.append(
            ChecklistFinding(
                code="missing_activation_checklist_v4_marker",
                message="Checklist must identify itself as activation checklist v4.",
            )
        )

    if not _INACTIVE_PATTERN.search(text):
        findings.append(
            ChecklistFinding(
                code="missing_inactive_marker",
                message="Checklist must explicitly remain inactive, disabled, or read-only.",
            )
        )

    for marker in _REQUIRED_MARKERS:
        if not all(pattern.search(text) for pattern in marker.patterns):
            findings.append(ChecklistFinding(code=marker.code, message=marker.message))

    for marker in _PROHIBITED_MARKERS:
        if marker.pattern.search(text):
            findings.append(ChecklistFinding(code=marker.code, message=marker.message))

    return findings


def validate_inactive_activation_checklist_v4_file(path: Path | str) -> list[ChecklistFinding]:
    """Load and validate an inactive activation checklist v4 file."""

    checklist_path = Path(path)
    return validate_inactive_activation_checklist_v4(checklist_path.read_text(encoding="utf-8"))


def finding_codes(findings: Iterable[ChecklistFinding]) -> set[str]:
    """Return finding codes for concise assertions and daemon reports."""

    return {finding.code for finding in findings}
