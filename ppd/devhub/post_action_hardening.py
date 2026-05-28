"""Fixture-first post-action hardening review for attended DevHub previews.

This module validates commit-safe review packets produced after a synthetic or
attended DevHub preview cycle. It intentionally accepts plain dictionaries so
fixtures can exercise the contract before live browser automation exists.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


ALLOWED_NEXT_ACTION_CATEGORIES = {"read_only", "local_preview"}
BLOCKED_FOLLOW_UP_CATEGORIES = {"consequential", "financial", "account_security"}
REQUIRED_JOURNAL_EVENT_TYPE = "post-action hardening review"
REQUIRED_BLOCKED_FOLLOWUP_IDS = {
    "submit-permit-request",
    "certify-acknowledgement",
    "upload-to-official-record",
    "purchase-trade-permit",
    "schedule-inspection",
    "cancel-or-withdraw",
    "request-extension-or-reactivation",
    "enter-payment-details",
    "submit-payment",
}
FORBIDDEN_OFFICIAL_COMPLETION_ACTION_IDS = {
    "submit-permit-request",
    "submit_permit_request",
    "certify-acknowledgement",
    "certify_acknowledgement",
    "upload-to-official-record",
    "official_upload",
    "purchase-trade-permit",
    "purchase_trade_permit",
    "schedule-inspection",
    "schedule_inspection",
    "cancel-or-withdraw",
    "cancel_or_withdraw",
    "request-extension-or-reactivation",
    "request_extension_or_reactivation",
    "enter-payment-details",
    "enter_payment_details",
    "submit-payment",
    "submit_payment",
}

PRIVATE_BROWSER_ARTIFACT_KEYS = {
    "auth_state",
    "browser_artifact",
    "cookie",
    "cookies",
    "download",
    "downloads",
    "har",
    "local_private_path",
    "raw_authenticated_text",
    "raw_crawl_output",
    "screenshot",
    "screenshots",
    "session_file",
    "session_path",
    "storage_state",
    "trace",
    "traces",
    "video",
    "videos",
}
PRIVATE_VALUE_KEYS = {
    "account_number",
    "card_number",
    "cardholder",
    "cardholder_name",
    "credential",
    "credentials",
    "cvv",
    "password",
    "payment_card_number",
    "payment_details",
    "routing_number",
    "security_code",
    "token",
}

PRIVATE_VALUE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bpassword\b", re.IGNORECASE),
    re.compile(r"\bpasscode\b", re.IGNORECASE),
    re.compile(r"\bmfa\b", re.IGNORECASE),
    re.compile(r"\bcaptcha\b", re.IGNORECASE),
    re.compile(r"\bcookie\b", re.IGNORECASE),
    re.compile(r"\bsession[_ -]?state\b", re.IGNORECASE),
    re.compile(r"\bauth[_ -]?state\b", re.IGNORECASE),
    re.compile(r"\braw authenticated\b", re.IGNORECASE),
    re.compile(r"\bauthenticated page text\b", re.IGNORECASE),
    re.compile(r"\binnerText\b", re.IGNORECASE),
    re.compile(r"\btextContent\b", re.IGNORECASE),
    re.compile(r"\bpage[_ -]?html\b", re.IGNORECASE),
    re.compile(r"\btrace\b", re.IGNORECASE),
    re.compile(r"\bhar\b", re.IGNORECASE),
    re.compile(r"\bscreenshot\b", re.IGNORECASE),
    re.compile(r"\bcard\s*(number|holder|cvv)\b", re.IGNORECASE),
    re.compile(r"\bcvv\b", re.IGNORECASE),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"/(Users|home)/[^\s/]+/", re.IGNORECASE),
    re.compile(r"\.(har|png|webm|zip)\b", re.IGNORECASE),
)
ATTEMPT_ONLY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*(playwright\s+)?(clicked|click|filled|fill|typed|selected|pressed)\b", re.IGNORECASE),
    re.compile(r"\b(clicked|filled|typed|selected|pressed)\s+(the\s+)?(button|field|control|input|checkbox|radio)\b", re.IGNORECASE),
)
FORBIDDEN_NEXT_ACTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsubmit\b", re.IGNORECASE),
    re.compile(r"\bupload\b", re.IGNORECASE),
    re.compile(r"\bschedule\b", re.IGNORECASE),
    re.compile(r"\bcancel\b", re.IGNORECASE),
    re.compile(r"\bwithdraw\b", re.IGNORECASE),
    re.compile(r"\bpay\b|\bpayment\b", re.IGNORECASE),
    re.compile(r"\bcertif", re.IGNORECASE),
)


@dataclass(frozen=True)
class HardeningReviewResult:
    """Validation result for a post-action hardening review packet."""

    valid: bool
    errors: tuple[str, ...]

    def require_valid(self) -> None:
        if not self.valid:
            raise ValueError("Invalid DevHub hardening review packet: " + "; ".join(self.errors))


def validate_hardening_review_packet(packet: Mapping[str, Any]) -> HardeningReviewResult:
    """Validate a commit-safe post-action review packet."""

    errors: list[str] = []

    if packet.get("packet_type") != "devhub_post_action_hardening_review":
        errors.append("packet_type must be devhub_post_action_hardening_review")

    if packet.get("cycle_kind") not in {"synthetic_attended_preview", "attended_preview"}:
        errors.append("cycle_kind must identify an attended preview cycle")

    _validate_action(packet, errors)
    _validate_outcome_evidence(packet, errors)
    _validate_confirmation(packet, errors)
    _validate_journal_link(packet, errors)
    _validate_redaction(packet, errors)
    _validate_blocked_followups(packet, errors)
    _validate_next_safe_actions(packet, errors)

    return HardeningReviewResult(valid=not errors, errors=tuple(errors))


def packet_is_valid(packet: Mapping[str, Any]) -> bool:
    """Return True when a packet satisfies all hardening requirements."""

    return validate_hardening_review_packet(packet).valid


def _validate_action(packet: Mapping[str, Any], errors: list[str]) -> None:
    action = _mapping(packet.get("action"))
    action_id = _text(action.get("action_id"))
    if action.get("mode") != "preview_only":
        errors.append("action.mode must be preview_only")
    if action.get("official_state_changed") is not False:
        errors.append("action.official_state_changed must be false")
    if action_id in FORBIDDEN_OFFICIAL_COMPLETION_ACTION_IDS:
        errors.append("action.action_id must not claim completion of official upload, submission, scheduling, cancellation, certification, or payment")


def _validate_outcome_evidence(packet: Mapping[str, Any], errors: list[str]) -> None:
    evidence = _sequence(packet.get("source_backed_outcome_evidence"))
    if not evidence:
        errors.append("source_backed_outcome_evidence must not be empty")
        return

    for index, item in enumerate(evidence):
        evidence_item = _mapping(item)
        prefix = f"source_backed_outcome_evidence[{index}]"
        if not _text(evidence_item.get("source_id")):
            errors.append(f"{prefix}.source_id is required")
        if not _text(evidence_item.get("canonical_url")):
            errors.append(f"{prefix}.canonical_url is required")
        if not _text(evidence_item.get("supports_outcome")):
            errors.append(f"{prefix}.supports_outcome is required")
        if not _text(evidence_item.get("observed_preview_fact")):
            errors.append(f"{prefix}.observed_preview_fact is required")
        if not _text(evidence_item.get("citation")):
            errors.append(f"{prefix}.citation is required")
        if _is_attempt_only(_text(evidence_item.get("observed_preview_fact"))):
            errors.append(f"{prefix}.observed_preview_fact cannot be only clicked or filled control evidence")
        if _is_attempt_only(_text(evidence_item.get("supports_outcome"))):
            errors.append(f"{prefix}.supports_outcome must describe outcome evidence, not only a control interaction")


def _validate_confirmation(packet: Mapping[str, Any], errors: list[str]) -> None:
    confirmation = _mapping(packet.get("user_visible_confirmation"))
    text = _text(confirmation.get("text"))
    if not text:
        errors.append("user_visible_confirmation.text is required")
        return

    lowered = text.lower()
    required_phrases = ("preview", "no official", "next")
    missing = [phrase for phrase in required_phrases if phrase not in lowered]
    if missing:
        errors.append("user_visible_confirmation.text must mention preview, no official change, and next actions")


def _validate_journal_link(packet: Mapping[str, Any], errors: list[str]) -> None:
    journal = _mapping(packet.get("journal_linkage"))
    if journal.get("event_type") != REQUIRED_JOURNAL_EVENT_TYPE:
        errors.append(f"journal_linkage.event_type must be {REQUIRED_JOURNAL_EVENT_TYPE}")
    if not _text(journal.get("journal_event_id")):
        errors.append("journal_linkage.journal_event_id is required")
    if not _text(journal.get("review_packet_id")):
        errors.append("journal_linkage.review_packet_id is required")
    if journal.get("commit_safe") is not True:
        errors.append("journal_linkage.commit_safe must be true")


def _validate_redaction(packet: Mapping[str, Any], errors: list[str]) -> None:
    checks = _sequence(packet.get("redaction_checks"))
    if not checks:
        errors.append("redaction_checks must not be empty")
    for index, item in enumerate(checks):
        check = _mapping(item)
        if check.get("passed") is not True:
            errors.append(f"redaction_checks[{index}] must pass")
        if _sequence(check.get("findings")):
            errors.append(f"redaction_checks[{index}].findings must be empty")

    for location, key, value in _walk_items(packet):
        normalized_key = _normalize_key(key)
        if normalized_key in PRIVATE_BROWSER_ARTIFACT_KEYS:
            errors.append(f"private browser artifact key appears at {location}")
        if normalized_key in PRIVATE_VALUE_KEYS:
            errors.append(f"private value key appears at {location}")
        if isinstance(value, str) and value != "[REDACTED]":
            for pattern in PRIVATE_VALUE_PATTERNS:
                if pattern.search(value):
                    errors.append(f"private or disallowed value appears at {location}")
                    break


def _validate_blocked_followups(packet: Mapping[str, Any], errors: list[str]) -> None:
    followups = _sequence(packet.get("blocked_consequential_followups"))
    if not followups:
        errors.append("blocked_consequential_followups must not be empty")
        return

    seen_ids: set[str] = set()
    for index, item in enumerate(followups):
        followup = _mapping(item)
        prefix = f"blocked_consequential_followups[{index}]"
        action_id = _text(followup.get("action_id"))
        if action_id:
            seen_ids.add(action_id)
        if followup.get("blocked") is not True:
            errors.append(f"{prefix}.blocked must be true")
        if followup.get("category") not in BLOCKED_FOLLOW_UP_CATEGORIES:
            errors.append(f"{prefix}.category must be consequential, financial, or account_security")
        if not _text(followup.get("requires_user_confirmation")):
            errors.append(f"{prefix}.requires_user_confirmation is required")
        if not _text(followup.get("reason")):
            errors.append(f"{prefix}.reason is required")

    missing = REQUIRED_BLOCKED_FOLLOWUP_IDS - seen_ids
    if missing:
        errors.append("blocked_consequential_followups missing required official action blocks: " + ", ".join(sorted(missing)))


def _validate_next_safe_actions(packet: Mapping[str, Any], errors: list[str]) -> None:
    actions = _sequence(packet.get("next_safe_actions"))
    if not actions:
        errors.append("next_safe_actions must not be empty")
        return

    for index, item in enumerate(actions):
        action = _mapping(item)
        prefix = f"next_safe_actions[{index}]"
        label = _text(action.get("label"))
        if action.get("category") not in ALLOWED_NEXT_ACTION_CATEGORIES:
            errors.append(f"{prefix}.category must be read_only or local_preview")
        if action.get("requires_attended_browser") is not False:
            errors.append(f"{prefix}.requires_attended_browser must be false")
        if action.get("changes_official_record") is not False:
            errors.append(f"{prefix}.changes_official_record must be false")
        if not label:
            errors.append(f"{prefix}.label is required")
        if not _source_ids(action):
            errors.append(f"{prefix}.sourceEvidenceIds is required")
        if not _text(action.get("citation")):
            errors.append(f"{prefix}.citation is required")
        if any(pattern.search(label) for pattern in FORBIDDEN_NEXT_ACTION_PATTERNS):
            errors.append(f"{prefix}.label must not propose upload, submission, scheduling, cancellation, certification, or payment")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _source_ids(value: Mapping[str, Any]) -> list[str]:
    raw = value.get("sourceEvidenceIds")
    return [_text(item) for item in _sequence(raw) if _text(item)]


def _normalize_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def _is_attempt_only(value: str) -> bool:
    if not value:
        return False
    return any(pattern.search(value) for pattern in ATTEMPT_ONLY_PATTERNS)


def _walk_items(value: Any, prefix: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            location = f"{prefix}.{key}"
            yield location, str(key), child
            yield from _walk_items(child, location)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk_items(child, f"{prefix}[{index}]")
