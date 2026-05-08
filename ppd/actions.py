"""Deterministic PP&D action classification and confirmation checkpoints.

This module is intentionally small and dependency-free so it can be used by
scrapers, automation planners, and tests without importing browser or network
runtime code.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ActionClass(str, Enum):
    """Automation safety class for a requested PP&D action."""

    READ_ONLY = "read_only"
    REVERSIBLE_DRAFT = "reversible_draft"
    EXACT_CONFIRMATION_REQUIRED = "exact_confirmation_required"
    UNSUPPORTED_HANDOFF = "unsupported_handoff"


class ActionKind(str, Enum):
    """Known PP&D action families."""

    READ_ONLY = "read_only"
    REVERSIBLE_DRAFT = "reversible_draft"
    OFFICIAL_UPLOAD = "official_upload"
    SUBMISSION = "submission"
    CERTIFICATION = "certification"
    CANCELLATION = "cancellation"
    INSPECTION_SCHEDULING = "inspection_scheduling"
    PAYMENT_REVIEW = "payment_review"
    PAYMENT_EXECUTION = "payment_execution"
    UNSUPPORTED_HANDOFF = "unsupported_handoff"


@dataclass(frozen=True)
class ActionPolicy:
    """Classification result for an automation action."""

    kind: ActionKind
    action_class: ActionClass
    exact_confirmation: str | None
    may_execute: bool
    reason: str


EXACT_CONFIRMATION_PROMPTS: dict[ActionKind, str] = {
    ActionKind.OFFICIAL_UPLOAD: "I confirm this official PP&D upload should proceed",
    ActionKind.SUBMISSION: "I confirm this PP&D submission should proceed",
    ActionKind.CERTIFICATION: "I confirm this PP&D certification should proceed",
    ActionKind.CANCELLATION: "I confirm this PP&D cancellation should proceed",
    ActionKind.INSPECTION_SCHEDULING: "I confirm this PP&D inspection scheduling should proceed",
    ActionKind.PAYMENT_EXECUTION: "I confirm this PP&D payment execution should proceed",
}

_READ_ONLY_TERMS = (
    "read",
    "view",
    "search",
    "lookup",
    "download",
    "archive",
    "scrape",
    "inspect status",
    "permit status",
    "payment review",
    "review payment",
    "fee review",
    "review fees",
)

_REVERSIBLE_DRAFT_TERMS = (
    "draft",
    "prepare",
    "stage",
    "prefill",
    "save draft",
    "reversible draft",
)

_OFFICIAL_UPLOAD_TERMS = (
    "upload",
    "official upload",
    "attach document",
    "file document",
)

_SUBMISSION_TERMS = (
    "submit",
    "submission",
    "send application",
    "file application",
)

_CERTIFICATION_TERMS = (
    "certify",
    "certification",
    "attest",
    "sign certification",
)

_CANCELLATION_TERMS = (
    "cancel",
    "cancellation",
    "withdraw",
    "void",
)

_INSPECTION_TERMS = (
    "schedule inspection",
    "inspection scheduling",
    "book inspection",
    "reschedule inspection",
)

_PAYMENT_EXECUTION_TERMS = (
    "pay",
    "payment execution",
    "execute payment",
    "submit payment",
    "charge card",
    "ach",
)

_UNSUPPORTED_TERMS = (
    "captcha",
    "mfa",
    "two-factor",
    "2fa",
    "account creation",
    "create account",
    "password reset",
    "impersonate",
)


def classify_action(description: str) -> ActionPolicy:
    """Classify a PP&D action description into a deterministic safety policy."""

    text = _normalize(description)
    if not text:
        return ActionPolicy(
            kind=ActionKind.UNSUPPORTED_HANDOFF,
            action_class=ActionClass.UNSUPPORTED_HANDOFF,
            exact_confirmation=None,
            may_execute=False,
            reason="empty action description requires human handoff",
        )

    if _contains_any(text, _UNSUPPORTED_TERMS):
        return _unsupported("unsupported account, CAPTCHA, MFA, or impersonation workflow")
    if _contains_any(text, _PAYMENT_EXECUTION_TERMS):
        return _exact(ActionKind.PAYMENT_EXECUTION, "payment execution changes money movement state")
    if _contains_any(text, _INSPECTION_TERMS):
        return _exact(ActionKind.INSPECTION_SCHEDULING, "inspection scheduling changes an official appointment")
    if _contains_any(text, _CANCELLATION_TERMS):
        return _exact(ActionKind.CANCELLATION, "cancellation or withdrawal changes official record state")
    if _contains_any(text, _CERTIFICATION_TERMS):
        return _exact(ActionKind.CERTIFICATION, "certification or attestation is an official user act")
    if _contains_any(text, _SUBMISSION_TERMS):
        return _exact(ActionKind.SUBMISSION, "submission changes official PP&D record state")
    if _contains_any(text, _OFFICIAL_UPLOAD_TERMS):
        return _exact(ActionKind.OFFICIAL_UPLOAD, "official upload changes submitted PP&D materials")
    if _contains_any(text, _REVERSIBLE_DRAFT_TERMS):
        return ActionPolicy(
            kind=ActionKind.REVERSIBLE_DRAFT,
            action_class=ActionClass.REVERSIBLE_DRAFT,
            exact_confirmation=None,
            may_execute=True,
            reason="draft action is reversible and does not submit official state",
        )
    if _contains_any(text, _READ_ONLY_TERMS):
        return ActionPolicy(
            kind=ActionKind.PAYMENT_REVIEW if "payment" in text or "fee" in text else ActionKind.READ_ONLY,
            action_class=ActionClass.READ_ONLY,
            exact_confirmation=None,
            may_execute=True,
            reason="read-only review does not change PP&D state",
        )
    return _unsupported("unrecognized PP&D action requires human handoff")


def exact_confirmation_matches(policy: ActionPolicy, confirmation: str | None) -> bool:
    """Return true only when the supplied confirmation exactly matches policy text."""

    if policy.action_class is not ActionClass.EXACT_CONFIRMATION_REQUIRED:
        return True
    return confirmation == policy.exact_confirmation


def checkpoint_allows(description: str, confirmation: str | None = None) -> bool:
    """Classify an action and apply its exact-confirmation checkpoint."""

    policy = classify_action(description)
    if not policy.may_execute:
        return False
    return exact_confirmation_matches(policy, confirmation)


def _exact(kind: ActionKind, reason: str) -> ActionPolicy:
    return ActionPolicy(
        kind=kind,
        action_class=ActionClass.EXACT_CONFIRMATION_REQUIRED,
        exact_confirmation=EXACT_CONFIRMATION_PROMPTS[kind],
        may_execute=True,
        reason=reason,
    )


def _unsupported(reason: str) -> ActionPolicy:
    return ActionPolicy(
        kind=ActionKind.UNSUPPORTED_HANDOFF,
        action_class=ActionClass.UNSUPPORTED_HANDOFF,
        exact_confirmation=None,
        may_execute=False,
        reason=reason,
    )


def _normalize(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)
