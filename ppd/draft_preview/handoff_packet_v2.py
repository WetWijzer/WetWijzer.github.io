"""Validation for draft preview agent handoff packet v2.

The validator is intentionally conservative. A draft preview packet is allowed
only when it is citation-backed, preview-scoped, and free of claims or flags
that imply live execution, private source use, official outcomes, or state
mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


class HandoffPacketV2ValidationError(ValueError):
    """Raised when a draft preview handoff packet v2 is unsafe to hand off."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


@dataclass(frozen=True)
class _TextHit:
    path: str
    text: str


_PRIVATE_FACT_PATTERNS = (
    "authenticated fact",
    "private fact",
    "private devhub",
    "account-scoped",
    "user account shows",
    "my permits",
    "permit detail page says",
    "logged in",
    "signed in",
    "session cookie",
    "auth token",
    "password",
    "mfa",
    "captcha",
    "private upload",
    "private document",
    "local file path",
)

_RAW_PDF_PATTERNS = (
    "raw pdf value",
    "raw_pdf_value",
    "acroform value",
    "field raw value",
    "pdf field value",
    "unredacted pdf",
    "filled pdf value",
)

_LIVE_EXECUTION_PATTERNS = (
    "ran the llm",
    "called the llm",
    "queried the llm",
    "ran devhub",
    "opened devhub",
    "clicked in devhub",
    "filled in devhub",
    "submitted in devhub",
    "launched browser",
    "browser session",
    "playwright clicked",
    "downloaded pdf",
    "parsed live pdf",
    "ran crawler",
    "live crawl",
    "crawled today",
    "ran processor",
    "processor executed",
    "browser executed",
)

_GUARANTEE_PATTERNS = (
    "permit will be approved",
    "approval is guaranteed",
    "guaranteed approval",
    "guarantee issuance",
    "will pass inspection",
    "will be accepted",
    "will be issued",
    "legally sufficient",
    "complies with all code",
    "meets all legal requirements",
)

_CONSEQUENTIAL_ACTION_PATTERNS = (
    "final submit",
    "final submission",
    "submit the application",
    "submitted the application",
    "submit payment",
    "pay the fee",
    "payment submitted",
    "upload corrections",
    "uploaded corrections",
    "upload to devhub",
    "schedule inspection",
    "inspection scheduled",
    "cancel permit",
    "cancelled permit",
    "withdraw application",
    "certify acknowledgement",
)

_MUTATION_FLAG_NAMES = (
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_pdf_mutation",
    "active_gap_analysis_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "mutates_prompt",
    "mutates_guardrails",
    "mutates_pdf",
    "mutates_gap_analysis",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
)

_MUTATION_FLAG_TEXT = (
    "active prompt mutation",
    "active guardrail mutation",
    "active pdf mutation",
    "active gap-analysis mutation",
    "active gap analysis mutation",
    "active monitoring mutation",
    "active release-state mutation",
    "active release state mutation",
    "active agent-state mutation",
    "active agent state mutation",
)

_REQUIRED_EXACT_CONFIRMATION_TERMS = (
    "exact confirmation",
    "action-specific confirmation",
    "user attendance",
    "confirmed exact action",
)


def validate_handoff_packet_v2(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate a draft preview agent handoff packet v2.

    Returns a compact acceptance record when valid and raises
    HandoffPacketV2ValidationError with deterministic error codes when invalid.
    """

    errors: list[str] = []

    if packet.get("version") not in ("draft_preview_agent_handoff_packet_v2", "v2", 2):
        errors.append("invalid_version")

    notes = _sequence(packet.get("handoff_notes"))
    if not notes:
        errors.append("missing_handoff_notes")
    else:
        for index, note in enumerate(notes):
            if not isinstance(note, Mapping):
                errors.append(f"handoff_notes[{index}].invalid_note")
                continue
            text = str(note.get("text", "")).strip()
            evidence = _sequence(note.get("source_evidence_ids")) or _sequence(note.get("citations"))
            if not text:
                errors.append(f"handoff_notes[{index}].missing_text")
            if not evidence or not all(str(item).strip() for item in evidence):
                errors.append(f"handoff_notes[{index}].missing_citation")

    if not _non_empty_strings(packet.get("supported_scenario_refs")):
        errors.append("missing_supported_scenario_refs")
    if not _non_empty_strings(packet.get("blocked_scenario_refs")):
        errors.append("missing_blocked_scenario_refs")

    reminders = _lower_join(packet.get("exact_confirmation_reminders"))
    if not reminders or not any(term in reminders for term in _REQUIRED_EXACT_CONFIRMATION_TERMS):
        errors.append("missing_exact_confirmation_reminders")

    for hit in _text_hits(packet):
        lowered = hit.text.lower()
        _reject_patterns(errors, hit.path, lowered, _PRIVATE_FACT_PATTERNS, "private_or_authenticated_fact")
        _reject_patterns(errors, hit.path, lowered, _RAW_PDF_PATTERNS, "raw_pdf_value")
        _reject_patterns(errors, hit.path, lowered, _LIVE_EXECUTION_PATTERNS, "live_execution_claim")
        _reject_patterns(errors, hit.path, lowered, _GUARANTEE_PATTERNS, "outcome_guarantee")
        _reject_patterns(errors, hit.path, lowered, _CONSEQUENTIAL_ACTION_PATTERNS, "consequential_action_language")
        _reject_patterns(errors, hit.path, lowered, _MUTATION_FLAG_TEXT, "active_mutation_flag")

    for path in _truthy_flag_paths(packet):
        flag_name = path.rsplit(".", 1)[-1]
        if flag_name in _MUTATION_FLAG_NAMES:
            errors.append(f"{path}.active_mutation_flag")

    if errors:
        raise HandoffPacketV2ValidationError(sorted(set(errors)))

    return {
        "validation_status": "accepted",
        "version": "draft_preview_agent_handoff_packet_v2",
        "handoff_note_count": len(notes),
    }


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, (list, tuple)):
        return value
    return ()


def _non_empty_strings(value: Any) -> bool:
    return bool(_sequence(value)) and all(isinstance(item, str) and item.strip() for item in value)


def _lower_join(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, Mapping):
        return " ".join(str(item).lower() for item in value.values())
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return " ".join(str(item).lower() for item in value)
    return ""


def _text_hits(value: Any, path: str = "packet") -> list[_TextHit]:
    if isinstance(value, str):
        return [_TextHit(path=path, text=value)]
    if isinstance(value, Mapping):
        hits: list[_TextHit] = []
        for key, child in value.items():
            hits.extend(_text_hits(child, f"{path}.{key}"))
        return hits
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        hits = []
        for index, child in enumerate(value):
            hits.extend(_text_hits(child, f"{path}[{index}]"))
        return hits
    return []


def _truthy_flag_paths(value: Any, path: str = "packet") -> list[str]:
    if isinstance(value, Mapping):
        paths: list[str] = []
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _MUTATION_FLAG_NAMES and child is True:
                paths.append(child_path)
            paths.extend(_truthy_flag_paths(child, child_path))
        return paths
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        paths = []
        for index, child in enumerate(value):
            paths.extend(_truthy_flag_paths(child, f"{path}[{index}]"))
        return paths
    return []


def _reject_patterns(
    errors: list[str],
    path: str,
    lowered_text: str,
    patterns: Sequence[str],
    code: str,
) -> None:
    if any(pattern in lowered_text for pattern in patterns):
        errors.append(f"{path}.{code}")
