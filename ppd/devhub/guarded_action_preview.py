"""Deterministic guardrails for previewing DevHub action plans.

This module is intentionally fixture-friendly and side-effect free. It does not
control a browser, persist session state, or inspect private DevHub data. It only
classifies a proposed action preflight packet before any executor is allowed to
run.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

ALLOWED_ACTION_TYPES = frozenset({"reversible_draft_fill"})
ALLOWED_ACTION_CLASSIFICATIONS = frozenset({"reversible_draft_preview"})
FAIL_CLOSED_ACTIONS = frozenset(
    {
        "continue",
        "save",
        "save_draft",
        "save_for_later",
        "official_upload",
        "upload",
        "certification",
        "certify",
        "submission",
        "submit",
        "payment",
        "pay",
        "pay_fee",
        "enter_payment_details",
        "schedule",
        "inspection_scheduling",
        "schedule_inspection",
        "cancellation",
        "cancel",
        "mfa",
        "captcha",
        "account_creation",
    }
)
SIDE_EFFECT_TERMS = (
    "continue",
    "save",
    "submit",
    "submission",
    "certify",
    "certification",
    "upload",
    "payment",
    "pay fee",
    "pay_fees",
    "schedule",
    "inspection scheduling",
)
SENSITIVE_KEY_TERMS = (
    "password",
    "credential",
    "secret",
    "token",
    "cookie",
    "session",
    "auth_state",
    "authorization",
    "card",
    "cvv",
    "cvc",
    "routing",
    "bank_account",
    "payment_detail",
    "payment_details",
    "private_value",
    "private_values",
    "raw_value",
    "unredacted",
)
SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b"),
    re.compile(r"\b\d+\s+[A-Za-z0-9 .'-]+\s+(?:Ave|Avenue|Blvd|Boulevard|Ct|Court|Dr|Drive|Ln|Lane|Pl|Place|Rd|Road|St|Street|Way)\b", re.IGNORECASE),
)
MIN_SELECTOR_CONFIDENCE = 0.85


@dataclass(frozen=True)
class ActionPreviewDecision:
    """Result of a guarded action preview evaluation."""

    allowed: bool
    action_type: str
    status: str
    reasons: tuple[str, ...]
    required: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "action_type": self.action_type,
            "status": self.status,
            "reasons": list(self.reasons),
            "required": list(self.required),
        }


def evaluate_guarded_action_preview(action_plan: Mapping[str, Any]) -> ActionPreviewDecision:
    """Evaluate whether a proposed DevHub action may proceed to preview.

    A reversible draft preview may proceed only when the preflight packet is
    grounded in public source evidence, redacted surface evidence, selector
    confidence, attended DevHub context, and concrete preview metadata.
    Consequential, financial, account-security, private, or unsupported actions
    fail closed.
    """

    if not isinstance(action_plan, Mapping):
        return ActionPreviewDecision(
            allowed=False,
            action_type="unknown",
            status="blocked_missing_guardrails",
            reasons=("action preflight packet must be an object",),
            required=("action_preflight_packet",),
        )

    action_type = _string_value(action_plan.get("action_type")) or "unknown"
    classification = _string_value(action_plan.get("action_classification"))

    missing = _missing_common_requirements(action_plan)
    sensitive_findings = _sensitive_packet_findings(action_plan)
    side_effect_findings = _side_effect_findings(action_plan)

    if sensitive_findings:
        return ActionPreviewDecision(
            allowed=False,
            action_type=action_type,
            status="refused_sensitive_packet",
            reasons=tuple(sensitive_findings),
            required=("redacted_preflight_packet",),
        )

    if action_type in FAIL_CLOSED_ACTIONS or side_effect_findings:
        reason = f"{action_type} is a side-effect or official DevHub action"
        reasons = (reason, *tuple(side_effect_findings)) if side_effect_findings else (reason,)
        return ActionPreviewDecision(
            allowed=False,
            action_type=action_type,
            status="refused_side_effect_request",
            reasons=reasons,
            required=("manual_user_handoff", "action_specific_confirmation"),
        )

    if missing:
        return ActionPreviewDecision(
            allowed=False,
            action_type=action_type,
            status="blocked_missing_guardrails",
            reasons=tuple(f"missing or invalid {name}" for name in missing),
            required=tuple(missing),
        )

    if classification not in ALLOWED_ACTION_CLASSIFICATIONS or action_type not in ALLOWED_ACTION_TYPES:
        return ActionPreviewDecision(
            allowed=False,
            action_type=action_type,
            status="refused_unknown_action",
            reasons=("action_type and action_classification are not an approved reversible draft preview",),
            required=("supported_action_type", "supported_action_classification"),
        )

    return ActionPreviewDecision(
        allowed=True,
        action_type=action_type,
        status="preview_ready",
        reasons=(),
        required=(
            "action_classification",
            "source_evidence",
            "surface_evidence",
            "selector_confidence",
            "attendance",
            "preview_metadata",
        ),
    )


def _missing_common_requirements(action_plan: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []

    if _string_value(action_plan.get("action_classification")) not in ALLOWED_ACTION_CLASSIFICATIONS:
        missing.append("action_classification")
    if not _has_source_evidence(action_plan.get("source_evidence")):
        missing.append("source_evidence")
    if not _has_surface_evidence(action_plan.get("surface_evidence")):
        missing.append("surface_evidence")
    if not _has_selector_confidence(action_plan.get("selector_confidence")):
        missing.append("selector_confidence")
    if action_plan.get("attendance") is not True:
        missing.append("attendance")
    if action_plan.get("devhub_attended") is not True:
        missing.append("devhub_attended")
    if not _has_preview_metadata(action_plan.get("preview_metadata")):
        missing.append("preview_metadata")

    return missing


def _has_source_evidence(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return False
    if not value:
        return False
    for item in value:
        if not isinstance(item, Mapping):
            return False
        if not _string_value(item.get("source_id")):
            return False
        if not _string_value(item.get("citation")):
            return False
    return True


def _has_surface_evidence(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    if _string_value(value.get("surface_id")) == "":
        return False
    if _string_value(value.get("surface_kind")) not in {"devhub_authenticated_redacted", "devhub_public_redacted"}:
        return False
    if value.get("redacted") is not True:
        return False
    if value.get("contains_private_values") is not False:
        return False
    return True


def _has_selector_confidence(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return float(value) >= MIN_SELECTOR_CONFIDENCE


def _has_preview_metadata(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    if _string_value(value.get("preview_id")) == "":
        return False
    if _string_value(value.get("mode")) != "preview_only":
        return False
    if value.get("may_mutate_devhub") is not False:
        return False
    fields = value.get("fields")
    if not isinstance(fields, Sequence) or isinstance(fields, (str, bytes)) or not fields:
        return False
    for field in fields:
        if not isinstance(field, Mapping):
            return False
        if not _string_value(field.get("selector")):
            return False
        if "redacted_proposed_value" not in field:
            return False
    return True


def _side_effect_findings(action_plan: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    for path, value in _iter_side_effect_request_values(action_plan):
        lowered = value.lower()
        for term in SIDE_EFFECT_TERMS:
            if term in lowered:
                findings.append(f"{path} requests side-effect term {term}")
                break
    return findings


def _iter_side_effect_request_values(action_plan: Mapping[str, Any]) -> Iterable[tuple[str, str]]:
    request_keys = (
        "action_type",
        "action_kind",
        "action_label",
        "action_classification",
        "requested_effect",
        "control_label",
        "button_text",
        "intent",
        "next_action",
    )
    for key in request_keys:
        value = _string_value(action_plan.get(key))
        if value:
            yield key, value

    preview_metadata = action_plan.get("preview_metadata")
    if isinstance(preview_metadata, Mapping):
        for key in ("action_label", "control_label", "button_text", "intent", "next_action"):
            value = _string_value(preview_metadata.get(key))
            if value:
                yield f"preview_metadata.{key}", value
        fields = preview_metadata.get("fields")
        if isinstance(fields, Sequence) and not isinstance(fields, (str, bytes)):
            for index, field in enumerate(fields):
                if isinstance(field, Mapping):
                    for key in ("selector", "label", "control_label"):
                        value = _string_value(field.get(key))
                        if value:
                            yield f"preview_metadata.fields[{index}].{key}", value


def _sensitive_packet_findings(value: Any, path: str = "packet") -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            child_path = f"{path}.{key_text}"
            if any(term in key_lower for term in SENSITIVE_KEY_TERMS):
                findings.append(f"{child_path} contains sensitive key material")
            findings.extend(_sensitive_packet_findings(item, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, item in enumerate(value):
            findings.extend(_sensitive_packet_findings(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        if _string_is_unredacted_private_value(value):
            findings.append(f"{path} contains private, credential, or payment detail value")
    return findings


def _string_is_unredacted_private_value(value: str) -> bool:
    stripped = value.strip()
    if not stripped or stripped.startswith("[REDACTED"):
        return False
    lowered = stripped.lower()
    if any(term in lowered for term in ("password=", "bearer ", "api_key", "credit card", "visa", "mastercard")):
        return True
    return any(pattern.search(stripped) for pattern in SENSITIVE_VALUE_PATTERNS)


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


__all__ = [
    "ActionPreviewDecision",
    "ALLOWED_ACTION_CLASSIFICATIONS",
    "ALLOWED_ACTION_TYPES",
    "FAIL_CLOSED_ACTIONS",
    "MIN_SELECTOR_CONFIDENCE",
    "evaluate_guarded_action_preview",
]
