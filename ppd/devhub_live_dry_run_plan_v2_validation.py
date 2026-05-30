"""Validation for attended DevHub read-only live-dry-run plan v2.

The validator is intentionally text-oriented and conservative. It is meant to
screen proposed live-dry-run plans before any DevHub session exists.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


_CITATION_RE = re.compile(
    r"(https?://|\[[^\]]+\]\([^\)]+\)|\bsource\s*:|\bcitation\s*:|\bppd/[\w./-]+:\d+|\bdocs/[\w./-]+:\d+)",
    re.IGNORECASE,
)

_VERIFICATION_STEP_RE = re.compile(
    r"\b(verify|verification|verified|confirm|confirmation|check|assert|inspect|review|validate|validation)\b",
    re.IGNORECASE,
)

_MANUAL_BOUNDARY_RE = re.compile(
    r"\b(manual|human|operator|attended|handoff|hand-off|pause|stop|boundary|do not automate|read-only)\b",
    re.IGNORECASE,
)

_LOGIN_MFA_CAPTCHA_RE = re.compile(
    r"\b(login|log in|sign in|signin|mfa|2fa|multi-factor|captcha|authenticated|authentication|account)\b",
    re.IGNORECASE,
)

_PRIVATE_VALUE_RE = re.compile(
    r"\b(password|passcode|otp|one-time code|totp|secret|api[_ -]?key|access[_ -]?token|refresh[_ -]?token|bearer|authorization header|private value|credential|client secret)\b",
    re.IGNORECASE,
)

_SESSION_ARTIFACT_RE = re.compile(
    r"\b(storage[_-]?state|auth[_-]?state|session[_-]?(file|json|artifact|id)|cookies?\.json|localstorage|indexeddb|devhub[_-]?session|\.auth/)\b",
    re.IGNORECASE,
)

_SCREENSHOT_TRACE_HAR_RE = re.compile(
    r"\b(screenshot|screen capture|trace|tracing|har|\.har|video artifact|recording)\b",
    re.IGNORECASE,
)

_BROWSER_AUTOMATION_RE = re.compile(
    r"\b(playwright|selenium|puppeteer|cypress|chromedriver|geckodriver|browser automation|headless browser|auto-click|autoclick|automated browser)\b",
    re.IGNORECASE,
)

_LIVE_COMPLETION_CLAIM_RE = re.compile(
    r"\b(live devhub|devhub live|production devhub|real devhub)\b.*\b(completed|submitted|filed|created|paid|uploaded|certified|scheduled|cancelled|canceled|finished)\b|\b(completed|submitted|filed|created|paid|uploaded|certified|scheduled|cancelled|canceled|finished)\b.*\b(live devhub|devhub live|production devhub|real devhub)\b",
    re.IGNORECASE,
)

_LEGAL_OUTCOME_RE = re.compile(
    r"\b(guarantee|guaranteed|ensure approval|will be approved|permit will issue|permit will be issued|legally compliant|legal compliance|no legal risk|binding determination|official approval)\b",
    re.IGNORECASE,
)

_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(submit|submission|file permit|pay|payment|checkout|certify|certification|upload|delete|cancel|cancellation|schedule inspection|book inspection|finalize|sign|e-sign|attest|attestation)\b",
    re.IGNORECASE,
)

_MUTATION_FLAG_RE = re.compile(
    r"\b(surface[-_ ]registry|guardrail|prompt|monitoring|release[-_ ]state|agent[-_ ]state)\b[^\n]{0,80}\b(mutate|mutation|write|update|enable|enabled|true|set|change|modify|active)\b|\b(mutate|mutation|write|update|enable|enabled|true|set|change|modify|active)\b[^\n]{0,80}\b(surface[-_ ]registry|guardrail|prompt|monitoring|release[-_ ]state|agent[-_ ]state)\b",
    re.IGNORECASE,
)


_PROHIBITED_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    ("private_or_authenticated_value", "Plan references private, secret, or authenticated values.", _PRIVATE_VALUE_RE),
    ("session_or_auth_artifact", "Plan references session/auth artifacts.", _SESSION_ARTIFACT_RE),
    ("screenshot_trace_har_reference", "Plan references screenshots, traces, HAR, or recordings.", _SCREENSHOT_TRACE_HAR_RE),
    ("browser_automation", "Plan references browser automation tooling or behavior.", _BROWSER_AUTOMATION_RE),
    ("live_devhub_completion_claim", "Plan claims a live DevHub completion outcome.", _LIVE_COMPLETION_CLAIM_RE),
    ("legal_or_permitting_guarantee", "Plan makes a legal or permitting outcome guarantee.", _LEGAL_OUTCOME_RE),
    ("consequential_action_enablement", "Plan enables consequential DevHub actions.", _CONSEQUENTIAL_ACTION_RE),
    ("active_mutation_flag", "Plan enables active mutation of registry, guardrail, prompt, monitoring, release-state, or agent-state surfaces.", _MUTATION_FLAG_RE),
)


def _meaningful_lines(text: str) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield line_number, stripped


def validate_attended_devhub_live_dry_run_plan_v2(text: str) -> list[ValidationIssue]:
    """Return validation issues for an attended read-only DevHub dry-run plan."""
    issues: list[ValidationIssue] = []

    if not text.strip():
        return [ValidationIssue("empty_plan", "Plan text is empty.")]

    for code, message, pattern in _PROHIBITED_PATTERNS:
        if pattern.search(text):
            issues.append(ValidationIssue(code, message))

    if _LOGIN_MFA_CAPTCHA_RE.search(text) and not _MANUAL_BOUNDARY_RE.search(text):
        issues.append(
            ValidationIssue(
                "missing_manual_login_mfa_captcha_boundary",
                "Plan mentions login, MFA, CAPTCHA, or authentication without an explicit manual handoff boundary.",
            )
        )

    for line_number, line in _meaningful_lines(text):
        if _VERIFICATION_STEP_RE.search(line) and not _CITATION_RE.search(line):
            issues.append(
                ValidationIssue(
                    "uncited_verification_step",
                    f"Verification-like step on line {line_number} lacks a citation or source reference.",
                )
            )

    return issues


def assert_valid_attended_devhub_live_dry_run_plan_v2(text: str) -> None:
    issues = validate_attended_devhub_live_dry_run_plan_v2(text)
    if issues:
        rendered = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise ValueError(rendered)


__all__ = [
    "ValidationIssue",
    "assert_valid_attended_devhub_live_dry_run_plan_v2",
    "validate_attended_devhub_live_dry_run_plan_v2",
]
