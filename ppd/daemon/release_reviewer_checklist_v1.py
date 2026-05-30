"""Validation for guarded agent release reviewer checklist v1.

The validator is intentionally text based and deterministic. It is used by the
PP&D daemon handoff path to reject release-review artifacts that omit required
manual review controls or claim unsafe activity.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, List, Sequence, Tuple


@dataclass(frozen=True)
class ChecklistFinding:
    """A deterministic validation finding for a release reviewer checklist."""

    code: str
    message: str
    line: int | None = None


_CHECKBOX_ROW_RE = re.compile(r"^\s*(?:[-*]|\|)?\s*\[([ xX])\]\s+(.+?)\s*$")
_CITATION_RE = re.compile(
    r"(\[[^\]]+\]\(https?://[^)]+\)|\[[^\]]+\]\([^)]*\)|\[\^[^\]]+\]|\b(?:citation|citations|source|sources|evidence|fixture|fixtures)\s*[:=]\s*\S+|\bppd/(?:tests/fixtures|daemon|logic|devhub|crawler|extraction)/\S+)",
    re.IGNORECASE,
)
_COMMAND_RE = re.compile(r"(^|\n)\s*(?:python3?|pytest|uv|node|npm|pnpm|npx|ruff|mypy|tsc)\b", re.IGNORECASE)
_PLACEHOLDER_RE = re.compile(r"(?:\{\{\s*manual[_ -]?signoff[^}]*\}\}|]*>|\[\s*manual[_ -]?signoff\s*\])", re.IGNORECASE)

_REQUIRED_SECTIONS: Sequence[Tuple[str, str, re.Pattern[str]]] = (
    (
        "missing_manual_signoff_placeholder",
        "Checklist must include an explicit manual signoff placeholder.",
        re.compile(r"manual\s+sign[- ]?off|manual_signoff|reviewer\s+sign[- ]?off", re.IGNORECASE),
    ),
    (
        "missing_unresolved_blocker_handling",
        "Checklist must describe how unresolved blockers keep the release blocked.",
        re.compile(r"unresolved\s+blocker|blockers?\s+unresolved|release\s+blocked|blocked\s+release", re.IGNORECASE),
    ),
    (
        "missing_validation_replay_commands",
        "Checklist must include validation replay commands.",
        re.compile(r"validation\s+replay|replay\s+commands?|re-run\s+validation|rerun\s+validation", re.IGNORECASE),
    ),
    (
        "missing_rollback_checkpoint",
        "Checklist must include rollback checkpoints.",
        re.compile(r"rollback\s+checkpoint|checkpoint\s+rollback|rollback\s+plan|revert\s+checkpoint", re.IGNORECASE),
    ),
)

_FORBIDDEN_PATTERNS: Sequence[Tuple[str, str, re.Pattern[str]]] = (
    (
        "private_or_session_artifact",
        "Checklist must not include private, authenticated, session, or browser artifacts.",
        re.compile(
            r"\b(?:cookie|cookies|credential|credentials|password|secret|token|auth(?:enticated)?\s+state|storageState|session\s+(?:file|state|artifact|cookie)|browser\s+artifact|playwright\s+trace|trace\.zip|\.har\b|HAR\s+file|screenshot|video\s+recording)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "raw_crawl_pdf_download_artifact",
        "Checklist must not include raw crawl, raw PDF, or downloaded data artifacts.",
        re.compile(
            r"\b(?:raw\s+(?:crawl|html|body|pdf|download|downloaded\s+data|capture)|downloaded\s+(?:pdf|document|file|data)|crawl\s+dump|warc\s+body|pdf\s+dump)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "live_execution_or_promotion_claim",
        "Checklist must not claim live execution or promotion.",
        re.compile(
            r"\b(?:ran\s+live|live\s+(?:crawl|execution|run)|executed\s+against\s+production|promoted\s+(?:to\s+)?(?:prod|production|release)|released\s+to\s+(?:prod|production)|production\s+promotion)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "legal_or_permitting_guarantee",
        "Checklist must not guarantee legal or permitting outcomes.",
        re.compile(
            r"\b(?:guarantee(?:d|s)?|ensure(?:d|s)?|will\s+(?:be\s+)?approved|permit\s+approval\s+guaranteed|legally\s+valid|legal\s+advice|compliance\s+guarantee|approval\s+is\s+certain)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "consequential_action_language",
        "Checklist must not authorize consequential actions such as submit, pay, schedule, certify, upload, cancel, or withdraw.",
        re.compile(
            r"\b(?:submit(?:ted|s)?\s+(?:the\s+)?(?:permit|application|request)|pay(?:s|ing|ment)?\s+(?:fees?|invoice)|schedule(?:d|s)?\s+(?:an\s+)?inspection|certif(?:y|ied|ies)\s+(?:the\s+)?acknowledg|upload(?:ed|s)?\s+(?:corrections?|documents?)\s+to\s+(?:the\s+)?official|cancel(?:ed|led|s)?\s+(?:the\s+)?(?:permit|inspection)|withdraw(?:n|s)?\s+(?:the\s+)?(?:permit|application))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "active_mutation_flag",
        "Checklist must not set active prompt, guardrail, process, fixture, release-state, or agent-state mutation flags.",
        re.compile(
            r"\b(?:--(?:mutate|update|write|promote|activate)[-_]?(?:prompt|prompts|guardrail|guardrails|process|processes|fixture|fixtures|release[-_]?state|agent[-_]?state)|(?:prompt|guardrail|process|fixture|release[-_]?state|agent[-_]?state)[-_ ]mutation\s*[:=]\s*(?:true|enabled|active|1)|active\s+(?:prompt|guardrail|process|fixture|release[-_]?state|agent[-_]?state)\s+mutation)\b",
            re.IGNORECASE,
        ),
    ),
)


def checklist_rows(text: str) -> List[Tuple[int, str]]:
    """Return line numbers and text for markdown checklist rows."""

    rows: List[Tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = _CHECKBOX_ROW_RE.match(line)
        if match:
            rows.append((line_number, match.group(2).strip()))
    return rows


def validate_guarded_agent_release_reviewer_checklist_v1(text: str) -> List[ChecklistFinding]:
    """Validate guarded agent release reviewer checklist v1 content."""

    findings: List[ChecklistFinding] = []
    stripped = text.strip()
    if not stripped:
        return [ChecklistFinding("empty_checklist", "Checklist content is empty.")]

    rows = checklist_rows(text)
    if not rows:
        findings.append(ChecklistFinding("missing_checklist_rows", "Checklist must contain markdown checklist rows."))

    for line_number, row_text in rows:
        if not _CITATION_RE.search(row_text):
            findings.append(
                ChecklistFinding(
                    "uncited_checklist_row",
                    "Every checklist row must include a citation, source, evidence reference, or fixture path.",
                    line_number,
                )
            )

    for code, message, pattern in _REQUIRED_SECTIONS:
        if not pattern.search(text):
            findings.append(ChecklistFinding(code, message))

    if not _PLACEHOLDER_RE.search(text):
        findings.append(
            ChecklistFinding(
                "missing_manual_signoff_placeholder_token",
                "Manual signoff must use a placeholder token such as {{manual_signoff_reviewer}}.",
            )
        )

    if re.search(r"validation\s+replay|replay\s+commands?|re-run\s+validation|rerun\s+validation", text, re.IGNORECASE) and not _COMMAND_RE.search(text):
        findings.append(
            ChecklistFinding(
                "missing_validation_replay_command_lines",
                "Validation replay section must include concrete command lines.",
            )
        )

    for code, message, pattern in _FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(ChecklistFinding(code, message, _line_for_offset(text, match.start())))

    return findings


def is_valid_guarded_agent_release_reviewer_checklist_v1(text: str) -> bool:
    """Return True when checklist v1 passes all deterministic validation."""

    return not validate_guarded_agent_release_reviewer_checklist_v1(text)


def finding_codes(findings: Iterable[ChecklistFinding]) -> List[str]:
    """Return finding codes in validation order for compact tests and callers."""

    return [finding.code for finding in findings]


def _line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1
