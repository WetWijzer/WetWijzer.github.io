"""Validation helpers for PP&D agent response contracts.

The validator is intentionally narrow and deterministic. It checks response-contract
objects before an agent asks a human for facts, explains a claim, or proposes an
action that could have external consequences.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence

_ALLOWED_FACT_REASONS = {"missing", "stale", "ambiguous", "conflicting"}
_REDACTED = "[REDACTED]"
_PATH_RE = re.compile(r"(?:/Users/|/home/|/tmp/|/var/folders/|[A-Za-z]:\\\\)[^\s'\"]+")
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_LONG_SECRET_RE = re.compile(r"\b(?:sk|pk|ghp|gho|github_pat|hf|xox[baprs]|AKIA)[A-Za-z0-9_\-]{12,}\b")
_KEY_VALUE_SECRET_RE = re.compile(
    r"(?i)\b(?:password|passwd|passphrase|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)\b\s*[:=]\s*\S+"
)
_CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
_CVV_RE = re.compile(r"(?i)\b(?:cvv|cvc|security code)\b\s*[:=]?\s*\d{3,4}\b")
_AUTH_STATE_RE = re.compile(r"(?i)\b(?:cookie|session|bearer|authorization|auth[_ -]?state|refresh[_ -]?token|mfa|totp)\b")
_CONSEQUENTIAL_ACTIONS = {
    "submit",
    "submission",
    "certify",
    "certification",
    "cancel",
    "cancellation",
    "pay",
    "payment",
    "purchase",
    "upload",
    "delete",
    "sign",
    "send",
    "file",
}


@dataclass(frozen=True)
class ContractViolation:
    """A single deterministic validation failure."""

    code: str
    message: str
    field: str


def redact_private_values(value: Any) -> Any:
    """Return a copy of ``value`` with local paths and obvious secrets redacted."""

    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, list):
        return [redact_private_values(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_private_values(item) for item in value)
    if isinstance(value, dict):
        redacted: dict[Any, Any] = {}
        for key, item in value.items():
            if _sensitive_key(str(key)):
                redacted[key] = _REDACTED
            else:
                redacted[key] = redact_private_values(item)
        return redacted
    return value


def validate_agent_response_contract(contract: Mapping[str, Any]) -> list[ContractViolation]:
    """Validate a PP&D agent response contract mapping.

    Expected fields are deliberately simple so tests and daemons can construct
    fixtures without importing a shared contract class:

    ``questions``: list of objects with ``prompt`` and ``reason``.
    ``explanations``: list of objects with ``text`` and non-empty ``citations``.
    ``actions``: list of objects with ``kind`` and, for consequential actions,
    ``requires_explicit_confirmation`` set to true.
    """

    violations: list[ContractViolation] = []
    _validate_questions(contract.get("questions", []), violations)
    _validate_explanations(contract.get("explanations", []), violations)
    _validate_actions(contract.get("actions", []), violations)
    _validate_sensitive_content(contract, violations)
    return violations


def is_valid_agent_response_contract(contract: Mapping[str, Any]) -> bool:
    """Return true when ``contract`` has no validation violations."""

    return not validate_agent_response_contract(contract)


def violation_codes(violations: Iterable[ContractViolation]) -> list[str]:
    """Return stable violation codes for compact assertions and logs."""

    return [violation.code for violation in violations]


def _validate_questions(questions: Any, violations: list[ContractViolation]) -> None:
    if questions in (None, []):
        return
    if not isinstance(questions, Sequence) or isinstance(questions, (str, bytes)):
        violations.append(ContractViolation("questions_type", "questions must be a list", "questions"))
        return

    for index, question in enumerate(questions):
        field = f"questions[{index}]"
        if not isinstance(question, Mapping):
            violations.append(ContractViolation("question_type", "question must be an object", field))
            continue
        reason = str(question.get("reason", "")).strip().lower()
        if reason not in _ALLOWED_FACT_REASONS:
            violations.append(
                ContractViolation(
                    "question_scope",
                    "agent questions may ask only for missing, stale, ambiguous, or conflicting facts",
                    f"{field}.reason",
                )
            )
        prompt = str(question.get("prompt", ""))
        if _contains_sensitive_content(prompt):
            violations.append(
                ContractViolation(
                    "question_sensitive_content",
                    "question prompt must not request or expose credentials, payment details, auth state, private values, or local paths",
                    f"{field}.prompt",
                )
            )


def _validate_explanations(explanations: Any, violations: list[ContractViolation]) -> None:
    if explanations in (None, []):
        return
    if not isinstance(explanations, Sequence) or isinstance(explanations, (str, bytes)):
        violations.append(ContractViolation("explanations_type", "explanations must be a list", "explanations"))
        return

    for index, explanation in enumerate(explanations):
        field = f"explanations[{index}]"
        if not isinstance(explanation, Mapping):
            violations.append(ContractViolation("explanation_type", "explanation must be an object", field))
            continue
        citations = explanation.get("citations", [])
        if not _has_citations(citations):
            violations.append(
                ContractViolation(
                    "uncited_explanation",
                    "agent explanations must include at least one citation",
                    f"{field}.citations",
                )
            )


def _validate_actions(actions: Any, violations: list[ContractViolation]) -> None:
    if actions in (None, []):
        return
    if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
        violations.append(ContractViolation("actions_type", "actions must be a list", "actions"))
        return

    for index, action in enumerate(actions):
        field = f"actions[{index}]"
        if not isinstance(action, Mapping):
            violations.append(ContractViolation("action_type", "action must be an object", field))
            continue
        kind = str(action.get("kind", "")).strip().lower()
        description = str(action.get("description", "")).strip().lower()
        if _is_consequential_action(kind, description) and action.get("requires_explicit_confirmation") is not True:
            violations.append(
                ContractViolation(
                    "confirmation_required",
                    "consequential actions must require explicit confirmation",
                    f"{field}.requires_explicit_confirmation",
                )
            )


def _validate_sensitive_content(value: Any, violations: list[ContractViolation]) -> None:
    redacted = redact_private_values(value)
    if redacted != value:
        violations.append(
            ContractViolation(
                "sensitive_content",
                "contract contains credentials, payment details, auth state, private values, or local paths that must be redacted",
                "$",
            )
        )
    elif _contains_sensitive_content(value):
        violations.append(
            ContractViolation(
                "sensitive_content",
                "contract contains credentials, payment details, auth state, private values, or local paths that must be redacted",
                "$",
            )
        )


def _redact_text(text: str) -> str:
    result = _PATH_RE.sub(_REDACTED, text)
    result = _EMAIL_RE.sub(_REDACTED, result)
    result = _LONG_SECRET_RE.sub(_REDACTED, result)
    result = _KEY_VALUE_SECRET_RE.sub(lambda match: match.group(0).split(match.group(0).strip().split()[-1])[0] + _REDACTED, result)
    result = _CARD_RE.sub(_REDACTED, result)
    result = _CVV_RE.sub(_REDACTED, result)
    return result


def _sensitive_key(key: str) -> bool:
    lowered = key.lower().replace("-", "_")
    sensitive_fragments = (
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "access_key",
        "private_key",
        "cookie",
        "session",
        "authorization",
        "auth_state",
        "credit_card",
        "card_number",
        "cvv",
        "cvc",
    )
    return any(fragment in lowered for fragment in sensitive_fragments)


def _contains_sensitive_content(value: Any) -> bool:
    if isinstance(value, str):
        return any(
            pattern.search(value)
            for pattern in (_PATH_RE, _EMAIL_RE, _LONG_SECRET_RE, _KEY_VALUE_SECRET_RE, _CARD_RE, _CVV_RE, _AUTH_STATE_RE)
        )
    if isinstance(value, Mapping):
        return any(_sensitive_key(str(key)) or _contains_sensitive_content(item) for key, item in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_sensitive_content(item) for item in value)
    return False


def _has_citations(citations: Any) -> bool:
    if not isinstance(citations, Sequence) or isinstance(citations, (str, bytes)):
        return False
    for citation in citations:
        if isinstance(citation, str) and citation.strip():
            return True
        if isinstance(citation, Mapping) and any(str(value).strip() for value in citation.values()):
            return True
    return False


def _is_consequential_action(kind: str, description: str) -> bool:
    tokens = set(re.findall(r"[a-z_]+", f"{kind} {description}".lower()))
    return bool(tokens & _CONSEQUENTIAL_ACTIONS)
