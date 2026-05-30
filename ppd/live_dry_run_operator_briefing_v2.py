"""Validation for PP&D live-dry-run operator briefing packet v2."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class BriefingPacketValidationIssue:
    """A deterministic validation finding for a briefing packet."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class BriefingPacketValidationResult:
    """Validation result for live-dry-run operator briefing packets."""

    valid: bool
    issues: tuple[BriefingPacketValidationIssue, ...]


_BLOCKED_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "private_or_authenticated_fact",
        re.compile(
            r"\b(private|authenticated|account[- ]scoped|logged[- ]in|devhub account|applicant|owner|tenant|contractor license|permit number|application number|ivr number|case number|personal address|email address|phone number|payment detail|credit card)\b",
            re.IGNORECASE,
        ),
        "Briefing packets must not contain private, authenticated, account-scoped, or user-specific facts.",
    ),
    (
        "raw_artifact_reference",
        re.compile(
            r"\b(raw crawl|raw html|raw pdf|pdf bytes|downloaded pdf|warc|har\b|trace\.zip|playwright trace|browser artifact|screenshot|storage state|storage_state|cookies?\.json|session file|auth state|crawl dump|page source)\b",
            re.IGNORECASE,
        ),
        "Briefing packets must not contain raw crawl, PDF, session, browser, trace, HAR, screenshot, or auth-state artifacts.",
    ),
    (
        "live_execution_claim",
        re.compile(
            r"\b(i|we|agent|operator|worker)\s+(clicked|submitted|uploaded|paid|scheduled|cancelled|canceled|certified|purchased|filed|executed)\b|\b(live execution completed|ran live|performed in devhub|made official change)\b",
            re.IGNORECASE,
        ),
        "Briefing packets must not claim live execution or official account changes.",
    ),
    (
        "credential_mfa_captcha_automation",
        re.compile(
            r"\b(automate|bypass|solve|handle|script|enter|fill|capture|store|reuse)\b.{0,48}\b(password|credential|login code|mfa|2fa|one[- ]time code|otp|captcha|security prompt)\b|\b(password|credential|mfa|2fa|otp|captcha)\b.{0,48}\b(automate|bypass|solve|script|store|reuse)\b",
            re.IGNORECASE,
        ),
        "Briefing packets must not include credential, MFA, CAPTCHA, or security-prompt automation language.",
    ),
    (
        "outcome_guarantee",
        re.compile(
            r"\b(guarantee|guaranteed|assure|ensure|will be approved|permit will issue|approval is certain|legally sufficient|compliant as a matter of law|no legal risk|cannot be denied)\b",
            re.IGNORECASE,
        ),
        "Briefing packets must not guarantee legal, permitting, approval, issuance, or compliance outcomes.",
    ),
    (
        "consequential_action_language",
        re.compile(
            r"\b(final submit|submit now|click submit|submit the application|make payment|submit payment|pay the fee|enter payment|upload to devhub|upload corrections|official upload|schedule inspection|cancel inspection|cancel permit|withdraw application|certify acknowledgement|purchase permit)\b",
            re.IGNORECASE,
        ),
        "Briefing packets must not include final submission, payment, upload, scheduling, cancellation, certification, withdrawal, or purchase language.",
    ),
)

_MUTATION_FLAG_NAMES = frozenset(
    {
        "active_source_mutation",
        "source_mutation",
        "mutate_sources",
        "update_sources",
        "active_surface_registry_mutation",
        "surface_registry_mutation",
        "mutate_surface_registry",
        "update_surface_registry",
        "active_prompt_mutation",
        "prompt_mutation",
        "mutate_prompts",
        "update_prompts",
        "active_guardrail_mutation",
        "guardrail_mutation",
        "mutate_guardrails",
        "update_guardrails",
        "active_monitoring_mutation",
        "monitoring_mutation",
        "mutate_monitoring",
        "update_monitoring",
        "active_release_state_mutation",
        "release_state_mutation",
        "mutate_release_state",
        "update_release_state",
        "active_agent_state_mutation",
        "agent_state_mutation",
        "mutate_agent_state",
        "update_agent_state",
    }
)


def validate_live_dry_run_operator_briefing_packet_v2(packet: Mapping[str, Any]) -> BriefingPacketValidationResult:
    """Validate a live-dry-run operator briefing packet v2.

    The validator is intentionally conservative: the packet is allowed to brief an
    operator for public, cited, attended dry-run review, but it must not contain
    private/authenticated facts, raw artifacts, live-execution claims,
    consequential action instructions, or active mutation flags.
    """

    issues: list[BriefingPacketValidationIssue] = []

    if not isinstance(packet, Mapping):
        return BriefingPacketValidationResult(
            valid=False,
            issues=(
                BriefingPacketValidationIssue(
                    code="invalid_packet_type",
                    path="$",
                    message="Briefing packet must be a mapping.",
                ),
            ),
        )

    _validate_go_no_go_notes(packet, issues)
    _validate_required_sequence(packet, "attendance_checkpoints", issues)
    _validate_required_sequence(packet, "stop_conditions", issues)
    _scan_value(packet, "$", issues)

    return BriefingPacketValidationResult(valid=not issues, issues=tuple(issues))


def assert_live_dry_run_operator_briefing_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a briefing packet fails validation."""

    result = validate_live_dry_run_operator_briefing_packet_v2(packet)
    if result.valid:
        return
    detail = "; ".join(f"{issue.path}: {issue.message}" for issue in result.issues)
    raise ValueError(f"Invalid live-dry-run operator briefing packet v2: {detail}")


def _validate_go_no_go_notes(packet: Mapping[str, Any], issues: list[BriefingPacketValidationIssue]) -> None:
    notes = packet.get("go_no_go_notes")
    if not isinstance(notes, Sequence) or isinstance(notes, (str, bytes)) or not notes:
        issues.append(
            BriefingPacketValidationIssue(
                code="missing_go_no_go_notes",
                path="$.go_no_go_notes",
                message="Briefing packet must include one or more cited go/no-go notes.",
            )
        )
        return

    for index, note in enumerate(notes):
        path = f"$.go_no_go_notes[{index}]"
        if not isinstance(note, Mapping):
            issues.append(
                BriefingPacketValidationIssue(
                    code="uncited_go_no_go_note",
                    path=path,
                    message="Go/no-go notes must be mappings with structured citations.",
                )
            )
            continue
        if not _has_nonempty_citations(note):
            issues.append(
                BriefingPacketValidationIssue(
                    code="uncited_go_no_go_note",
                    path=path,
                    message="Go/no-go note must include non-empty citations, source_evidence_ids, or public_source_ids.",
                )
            )


def _validate_required_sequence(
    packet: Mapping[str, Any], field_name: str, issues: list[BriefingPacketValidationIssue]
) -> None:
    value = packet.get(field_name)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        issues.append(
            BriefingPacketValidationIssue(
                code=f"missing_{field_name}",
                path=f"$.{field_name}",
                message=f"Briefing packet must include one or more {field_name.replace('_', ' ')}.",
            )
        )


def _has_nonempty_citations(note: Mapping[str, Any]) -> bool:
    for field_name in ("citations", "source_evidence_ids", "public_source_ids"):
        value = note.get(field_name)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0:
            return True
    return False


def _scan_value(value: Any, path: str, issues: list[BriefingPacketValidationIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in _MUTATION_FLAG_NAMES and _is_truthy_mutation_value(child):
                issues.append(
                    BriefingPacketValidationIssue(
                        code="active_mutation_flag",
                        path=child_path,
                        message="Briefing packets must not set active source, surface-registry, prompt, guardrail, monitoring, release-state, or agent-state mutation flags.",
                    )
                )
            _scan_text(key_text, child_path, issues)
            _scan_value(child, child_path, issues)
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _scan_value(child, f"{path}[{index}]", issues)
        return

    if isinstance(value, str):
        _scan_text(value, path, issues)


def _scan_text(text: str, path: str, issues: list[BriefingPacketValidationIssue]) -> None:
    for code, pattern, message in _BLOCKED_TEXT_PATTERNS:
        if pattern.search(text):
            issues.append(BriefingPacketValidationIssue(code=code, path=path, message=message))


def _is_truthy_mutation_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "active", "enabled", "on", "mutate", "write"}
    return bool(value)
