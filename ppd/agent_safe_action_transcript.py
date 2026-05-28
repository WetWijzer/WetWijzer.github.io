"""Build and validate PP&D agent safe-action transcripts.

The transcript builder is intentionally fixture-first. It accepts committed,
metadata-only rows, evaluates each row with the PP&D preflight decision matrix,
and emits the narrow message type an agent may show to a user before any live
crawl, authenticated browser work, upload, submission, payment, certification,
scheduling, cancellation, or account action.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

from ppd.agent_preflight_decision_matrix import PreflightOutcome, evaluate_agent_preflight


_ALLOWED_MESSAGE_TYPES = {
    "ask-user",
    "local-preview",
    "reversible-draft",
    "manual-handoff",
    "refused-action",
}

_OUTCOME_MESSAGE_TYPES = {
    PreflightOutcome.BLOCKED: "ask-user",
    PreflightOutcome.LOCAL_PREVIEW: "local-preview",
    PreflightOutcome.REVERSIBLE_DRAFT: "reversible-draft",
    PreflightOutcome.MANUAL_HANDOFF: "manual-handoff",
    PreflightOutcome.REFUSED: "refused-action",
}

_ALLOWED_ASK_STATUSES = {"missing", "stale", "ambiguous", "conflicting"}
_FORBIDDEN_PROMPT_TERMS = {
    "auth",
    "authorization",
    "bank",
    "card",
    "cookie",
    "credential",
    "credentials",
    "credit card",
    "cvv",
    "login",
    "mfa",
    "password",
    "payment detail",
    "payment details",
    "session",
    "token",
}
_CONSEQUENTIAL_TERMS = {
    "acknowledge",
    "cancel",
    "certif",
    "pay",
    "payment",
    "schedule",
    "submit",
    "upload",
}
_PRIVATE_TEXT_PATTERNS = (
    re.compile(r"/home/[A-Za-z0-9._-]+/[^\s,;:)]+"),
    re.compile(r"/[A-Za-z0-9._-]+/(?:private|devhub|sessions?|traces?|auth|downloads?)/[^\s,;:)]+", re.IGNORECASE),
    re.compile(r"[A-Za-z]:\\\\[^\s,;:)]+"),
    re.compile(r"\b(?:Bearer\s+)?[A-Za-z0-9_-]{24,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
)


@dataclass(frozen=True)
class SafeActionTranscriptMessage:
    """One cited, agent-facing safe-action message."""

    message_id: str
    message_type: str
    preflight_outcome: str
    text: str
    citations: tuple[str, ...]
    citation_backed_reasons: tuple[Mapping[str, Any], ...]
    blocked_official_actions: tuple[str, ...]
    next_safe_actions: tuple[str, ...]
    asked_facts: tuple[Mapping[str, Any], ...] = ()
    exact_confirmation_gate: Mapping[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "preflight_outcome": self.preflight_outcome,
            "text": self.text,
            "citations": list(self.citations),
            "citation_backed_reasons": [dict(reason) for reason in self.citation_backed_reasons],
            "blocked_official_actions": list(self.blocked_official_actions),
            "next_safe_actions": list(self.next_safe_actions),
        }
        if self.asked_facts:
            result["asked_facts"] = [dict(fact) for fact in self.asked_facts]
        if self.exact_confirmation_gate is not None:
            result["exact_confirmation_gate"] = dict(self.exact_confirmation_gate)
        return result


def build_safe_action_transcript(case: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic cited transcript for one synthetic PP&D case."""

    source_ids = _source_evidence_ids(case.get("source_evidence", ()))
    messages = []
    for index, row in enumerate(_rows(case), start=1):
        decision = evaluate_agent_preflight(_mapping(row.get("packet"), "packet"))
        message_type = _message_type_for(row, decision.outcome)
        citations = _citations(row, source_ids)
        blocked_actions = _blocked_actions(row)
        asked_facts = _asked_facts(row, decision.outcome, citations)
        reasons = _citation_backed_reasons(row, decision.reasons, citations)
        messages.append(
            SafeActionTranscriptMessage(
                message_id=str(row.get("message_id") or f"message-{index:02d}"),
                message_type=message_type,
                preflight_outcome=decision.outcome.value,
                text=_redact_private_text(_message_text(row, decision.outcome, decision.reasons)),
                citations=citations,
                citation_backed_reasons=reasons,
                blocked_official_actions=blocked_actions,
                next_safe_actions=tuple(_redact_private_text(action) for action in decision.next_safe_actions),
                asked_facts=asked_facts,
                exact_confirmation_gate=_exact_confirmation_gate(row, blocked_actions),
            ).as_dict()
        )

    return {
        "case_id": str(case.get("case_id") or "synthetic_ppd_case"),
        "transcript_id": str(case.get("transcript_id") or "synthetic_ppd_safe_action_transcript"),
        "messages": messages,
    }


def validate_safe_action_transcript(transcript: Mapping[str, Any]) -> tuple[str, ...]:
    """Return validation issue codes for a generated safe-action transcript."""

    issues: list[str] = []
    messages = transcript.get("messages")
    if not isinstance(messages, list) or not messages:
        return ("missing_messages",)

    seen_types = set()
    for message in messages:
        if not isinstance(message, Mapping):
            issues.append("invalid_message")
            continue
        message_type = message.get("message_type")
        seen_types.add(message_type)
        if message_type not in _ALLOWED_MESSAGE_TYPES:
            issues.append("invalid_message_type")

        citations = message.get("citations")
        if not isinstance(citations, list) or not citations or not all(isinstance(item, str) and item for item in citations):
            issues.append("missing_citations")
            citations = []

        text = message.get("text")
        if not isinstance(text, str) or not text.strip():
            issues.append("missing_text")
        elif _contains_private_text(text):
            issues.append("unredacted_private_value")

        _validate_citation_backed_reasons(message, citations, issues)
        _validate_asked_facts(message, message_type, citations, issues)

        blocked_actions = message.get("blocked_official_actions")
        if message_type in {"manual-handoff", "refused-action"} and not blocked_actions:
            issues.append("missing_blocked_official_actions")
        if _has_consequential_actions(blocked_actions):
            _validate_exact_confirmation_gate(message, blocked_actions, issues)

    required = {
        "ask-user",
        "local-preview",
        "reversible-draft",
        "manual-handoff",
        "refused-action",
    }
    if seen_types != required:
        issues.append("missing_required_message_type")

    return tuple(dict.fromkeys(issues))


def _rows(case: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    rows = case.get("preflight_decision_matrix")
    if not isinstance(rows, list) or not rows:
        raise ValueError("case must include a non-empty preflight_decision_matrix")
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("each preflight decision row must be an object")
    return rows


def _source_evidence_ids(source_evidence: Any) -> set[str]:
    if not isinstance(source_evidence, list):
        raise ValueError("source_evidence must be a list")
    source_ids = set()
    for source in source_evidence:
        if not isinstance(source, Mapping) or not source.get("source_evidence_id"):
            raise ValueError("each source evidence record must include source_evidence_id")
        source_ids.add(str(source["source_evidence_id"]))
    return source_ids


def _message_type_for(row: Mapping[str, Any], outcome: PreflightOutcome) -> str:
    expected = _OUTCOME_MESSAGE_TYPES.get(outcome)
    if expected is None:
        raise ValueError(f"preflight outcome {outcome.value} cannot become a safe-action message")
    requested = str(row.get("message_type") or expected)
    if requested != expected:
        raise ValueError(f"row message_type {requested} does not match preflight outcome {outcome.value}")
    return requested


def _citations(row: Mapping[str, Any], source_ids: set[str]) -> tuple[str, ...]:
    raw = row.get("citations")
    if not isinstance(raw, list) or not raw:
        raise ValueError("each transcript row must include citations")
    citations = tuple(str(item) for item in raw)
    missing = [citation for citation in citations if citation not in source_ids]
    if missing:
        raise ValueError("citations are not present in source_evidence: " + ", ".join(missing))
    return citations


def _blocked_actions(row: Mapping[str, Any]) -> tuple[str, ...]:
    raw = row.get("blocked_official_actions", ())
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ValueError("blocked_official_actions must be a list when present")
    return tuple(_redact_private_text(str(item)) for item in raw)


def _message_text(row: Mapping[str, Any], outcome: PreflightOutcome, reasons: Sequence[str]) -> str:
    template = row.get("message_template")
    if isinstance(template, str) and template.strip():
        return template.format(outcome=outcome.value, reasons="; ".join(reasons))
    return f"Preflight outcome {outcome.value}: {'; '.join(reasons)}"


def _asked_facts(row: Mapping[str, Any], outcome: PreflightOutcome, citations: tuple[str, ...]) -> tuple[Mapping[str, Any], ...]:
    if outcome != PreflightOutcome.BLOCKED:
        return ()
    raw = row.get("asked_facts")
    if isinstance(raw, list):
        return tuple(_normalize_asked_fact(item, citations) for item in raw if isinstance(item, Mapping))

    packet = _mapping(row.get("packet"), "packet")
    gaps = packet.get("case_gaps") or packet.get("case_gap_report") or {}
    if not isinstance(gaps, Mapping):
        return ()
    facts: list[Mapping[str, Any]] = []
    for status, key in (
        ("missing", "missing_facts"),
        ("stale", "stale_evidence"),
        ("ambiguous", "ambiguous_facts"),
        ("conflicting", "conflicting_evidence"),
        ("conflicting", "conflicting_facts"),
    ):
        value = gaps.get(key)
        if isinstance(value, list):
            for fact in value:
                fact_id = _fact_id(fact)
                if fact_id:
                    facts.append(
                        {
                            "fact_id": fact_id,
                            "status": status,
                            "prompt": f"Please provide the {fact_id.replace('_', ' ')}.",
                            "reason": f"This {status} fact blocks the next safe PP&D action.",
                            "citations": list(citations),
                        }
                    )
    return tuple(facts)


def _normalize_asked_fact(item: Mapping[str, Any], fallback_citations: tuple[str, ...]) -> Mapping[str, Any]:
    citations = item.get("citations") or item.get("reason_citation_ids") or list(fallback_citations)
    if not isinstance(citations, list):
        citations = list(fallback_citations)
    return {
        "fact_id": _redact_private_text(str(item.get("fact_id") or item.get("id") or "")),
        "status": str(item.get("status") or "missing").strip().lower(),
        "prompt": _redact_private_text(str(item.get("prompt") or "")),
        "reason": _redact_private_text(str(item.get("reason") or "Required before the next safe PP&D action.")),
        "citations": [str(citation) for citation in citations],
    }


def _fact_id(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("fact_id") or value.get("id") or value.get("field")
    return str(value or "").strip()


def _citation_backed_reasons(
    row: Mapping[str, Any], decision_reasons: Sequence[str], citations: tuple[str, ...]
) -> tuple[Mapping[str, Any], ...]:
    raw = row.get("citation_backed_reasons") or row.get("reason_citations")
    if isinstance(raw, list) and raw:
        reasons = []
        for item in raw:
            if isinstance(item, Mapping):
                item_citations = item.get("citations") or item.get("reason_citation_ids") or citations
                if not isinstance(item_citations, list):
                    item_citations = list(citations)
                reasons.append(
                    {
                        "reason": _redact_private_text(str(item.get("reason") or item.get("text") or "")),
                        "citations": [str(citation) for citation in item_citations],
                    }
                )
        return tuple(reasons)
    return tuple(
        {"reason": _redact_private_text(str(reason)), "citations": list(citations)}
        for reason in decision_reasons
    )


def _exact_confirmation_gate(row: Mapping[str, Any], blocked_actions: tuple[str, ...]) -> Mapping[str, Any] | None:
    if not _has_consequential_actions(blocked_actions):
        return None
    raw = row.get("exact_confirmation_gate")
    if isinstance(raw, Mapping):
        return dict(raw)
    return {
        "required": True,
        "exact_required": True,
        "default_refusal": True,
        "confirmation_satisfied": False,
        "requires_attended_user": True,
        "blocked_actions": list(blocked_actions),
        "required_exact_text": "CONFIRM " + "; ".join(blocked_actions),
    }


def _validate_citation_backed_reasons(message: Mapping[str, Any], citations: Sequence[str], issues: list[str]) -> None:
    reasons = message.get("citation_backed_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("missing_citation_backed_reasons")
        return
    citation_set = set(citations)
    for reason in reasons:
        if not isinstance(reason, Mapping):
            issues.append("invalid_reason")
            continue
        text = reason.get("reason")
        reason_citations = reason.get("citations")
        if not isinstance(text, str) or not text.strip():
            issues.append("invalid_reason")
        if not isinstance(reason_citations, list) or not reason_citations:
            issues.append("missing_citation_backed_reasons")
        elif any(citation not in citation_set for citation in reason_citations):
            issues.append("reason_citation_not_in_message_citations")


def _validate_asked_facts(
    message: Mapping[str, Any], message_type: Any, citations: Sequence[str], issues: list[str]
) -> None:
    asked_facts = message.get("asked_facts", [])
    if message_type != "ask-user":
        if asked_facts:
            issues.append("asked_facts_on_non_ask_user_message")
        return
    if not isinstance(asked_facts, list) or not asked_facts:
        issues.append("missing_asked_facts")
        return
    citation_set = set(citations)
    for fact in asked_facts:
        if not isinstance(fact, Mapping):
            issues.append("invalid_asked_fact")
            continue
        status = str(fact.get("status") or "").strip().lower()
        if status not in _ALLOWED_ASK_STATUSES:
            issues.append("fact_not_missing_stale_ambiguous_or_conflicting")
        fact_id = str(fact.get("fact_id") or "")
        prompt = str(fact.get("prompt") or "")
        reason = str(fact.get("reason") or "")
        if not fact_id or not prompt or not reason:
            issues.append("invalid_asked_fact")
        if _contains_forbidden_prompt(f"{fact_id} {prompt}"):
            issues.append("forbidden_sensitive_prompt")
        if _contains_private_text(f"{fact_id} {prompt} {reason}"):
            issues.append("unredacted_private_value")
        fact_citations = fact.get("citations")
        if not isinstance(fact_citations, list) or not fact_citations:
            issues.append("missing_citations")
        elif any(citation not in citation_set for citation in fact_citations):
            issues.append("asked_fact_citation_not_in_message_citations")


def _validate_exact_confirmation_gate(message: Mapping[str, Any], blocked_actions: Any, issues: list[str]) -> None:
    gate = message.get("exact_confirmation_gate")
    if not isinstance(gate, Mapping):
        issues.append("missing_exact_confirmation_gate")
        return
    required_flags = (
        gate.get("required") is True,
        gate.get("exact_required") is True or gate.get("exactRequired") is True,
        gate.get("default_refusal") is True or gate.get("defaultRefusal") is True,
        gate.get("confirmation_satisfied") is False or gate.get("confirmationSatisfied") is False,
    )
    if not all(required_flags):
        issues.append("invalid_exact_confirmation_gate")
    exact_text = gate.get("required_exact_text") or gate.get("exactPhrase") or gate.get("requiredExactText")
    if not isinstance(exact_text, str) or not exact_text.strip():
        issues.append("invalid_exact_confirmation_gate")
    gate_actions = gate.get("blocked_actions") or gate.get("blockedActions") or []
    if isinstance(blocked_actions, list) and isinstance(gate_actions, list):
        missing = [action for action in blocked_actions if action not in gate_actions]
        if missing:
            issues.append("exact_confirmation_gate_missing_blocked_action")


def _has_consequential_actions(actions: Any) -> bool:
    if not isinstance(actions, list) and not isinstance(actions, tuple):
        return False
    action_text = " ".join(str(action).lower() for action in actions)
    return any(term in action_text for term in _CONSEQUENTIAL_TERMS)


def _contains_forbidden_prompt(value: str) -> bool:
    lower = value.lower()
    return any(term in lower for term in _FORBIDDEN_PROMPT_TERMS)


def _contains_private_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in _PRIVATE_TEXT_PATTERNS)


def _redact_private_text(value: str) -> str:
    redacted = value
    for pattern in _PRIVATE_TEXT_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value
