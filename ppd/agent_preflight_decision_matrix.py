"""Fixture-first PP&D agent preflight decision matrix.

The matrix is deliberately metadata-only. It evaluates committed fixture-shaped
records before any live crawl, authenticated browser work, upload, submission,
payment, certification, scheduling, cancellation, or account action is attempted.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping


class PreflightOutcome(str, Enum):
    """Agent-facing preflight outcomes."""

    BLOCKED = "blocked"
    READ_ONLY = "read-only"
    LOCAL_PREVIEW = "local-preview"
    REVERSIBLE_DRAFT = "reversible-draft"
    MANUAL_HANDOFF = "manual-handoff"
    REFUSED = "refused"


@dataclass(frozen=True)
class PreflightDecision:
    """Deterministic preflight decision with auditable reasons."""

    outcome: PreflightOutcome
    reasons: tuple[str, ...]
    next_safe_actions: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "reasons": list(self.reasons),
            "next_safe_actions": list(self.next_safe_actions),
        }


_READY_CRAWL_STATUSES = {"fixture_ready", "ready_metadata_only", "ready", "validated"}
_FRESH_SOURCE_STATUSES = {"fresh", "current", "verified", "unchanged"}
_READY_PROCESS_STATUSES = {"current", "compatible", "validated"}
_READY_DEVHUB_STATUSES = {"attended_ready", "ready_metadata_only", "fixture_validated", "manual_handoff_ready"}
_READY_PREVIEW_STATUSES = {"ready", "preview_ready", "fixture_validated", "metadata_only_ready"}

_READ_ONLY_CLASSES = {"read_only", "safe_read_only", "review", "status_review"}
_LOCAL_PREVIEW_CLASSES = {"local_preview", "pdf_preview", "draft_preview", "metadata_preview"}
_REVERSIBLE_CLASSES = {
    "reversible",
    "reversible_draft",
    "reversible_draft_edit",
    "reversible_draft_fill",
    "draft_edit",
}
_MANUAL_HANDOFF_CLASSES = {
    "certification",
    "consequential",
    "consequential_official",
    "exact_confirmation_required",
    "financial",
    "official",
    "official_upload",
    "payment",
    "schedule_inspection",
    "submission",
    "upload_to_official_record",
}
_REFUSED_CLASSES = {
    "account_creation",
    "captcha",
    "mfa",
    "password_recovery",
    "payment_detail_entry",
    "payment_execution",
    "refused",
    "unsupported_account_action",
}

_PRIVATE_KEYS = {
    "auth_state",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "cvv",
    "password",
    "payment_details",
    "private_value",
    "raw_body",
    "raw_html",
    "session_state",
    "token",
    "trace",
}


def evaluate_agent_preflight(packet: Mapping[str, Any]) -> PreflightDecision:
    """Return a fail-closed PP&D preflight outcome for one fixture packet."""

    private_paths = tuple(_private_metadata_paths(packet))
    if private_paths:
        return _decision(
            PreflightOutcome.REFUSED,
            ["packet contains private or raw runtime metadata: " + ", ".join(private_paths)],
            ["remove private/runtime data and retry with a committed metadata-only fixture"],
        )

    action_class = _normalized_action_class(packet)
    if action_class in _REFUSED_CLASSES:
        return _decision(
            PreflightOutcome.REFUSED,
            [f"action class {action_class} is not automatable by PP&D agents"],
            ["stop automation and provide a human-run playbook instead"],
        )

    blocking_reasons = _blocking_readiness_reasons(packet)
    if blocking_reasons:
        return _decision(
            PreflightOutcome.BLOCKED,
            blocking_reasons,
            ["refresh fixtures and rerun preflight before any live crawl or DevHub action"],
        )

    if action_class in _READ_ONLY_CLASSES:
        return _decision(
            PreflightOutcome.READ_ONLY,
            ["all fixture readiness gates passed for read-only assistance"],
            ["perform cited read-only review only"],
        )

    if action_class in _LOCAL_PREVIEW_CLASSES:
        return _local_preview_decision(packet)

    if action_class in _REVERSIBLE_CLASSES:
        return _reversible_draft_decision(packet)

    if action_class in _MANUAL_HANDOFF_CLASSES:
        return _decision(
            PreflightOutcome.MANUAL_HANDOFF,
            [f"action class {action_class} requires attended manual handoff and exact user confirmation"],
            ["prepare a redacted handoff checklist without executing the official action"],
        )

    return _decision(
        PreflightOutcome.MANUAL_HANDOFF,
        [f"unrecognized action class {action_class or 'missing'} fails closed to manual handoff"],
        ["classify the action with source-backed metadata before proceeding"],
    )


def _blocking_readiness_reasons(packet: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []

    crawl_status = _status(packet.get("crawl_readiness"), "status", "readiness_status", "decision")
    if crawl_status not in _READY_CRAWL_STATUSES:
        reasons.append(f"crawl readiness is not fixture-ready: {crawl_status or 'missing'}")

    freshness_status = _status(packet.get("source_freshness"), "status", "freshness_status")
    if freshness_status not in _FRESH_SOURCE_STATUSES:
        reasons.append(f"source freshness is not current: {freshness_status or 'missing'}")

    process_status = _status(packet.get("process_versioning"), "status", "version_status", "compatibility_status")
    if process_status not in _READY_PROCESS_STATUSES:
        reasons.append(f"process versioning is not compatible: {process_status or 'missing'}")

    case_gaps = packet.get("case_gaps") or packet.get("case_gap_report") or {}
    if not isinstance(case_gaps, Mapping):
        reasons.append("case gaps must be an object")
    else:
        for key in ("missing_facts", "missing_documents", "stale_evidence", "conflicting_evidence", "conflicting_facts"):
            if _non_empty(case_gaps.get(key)):
                reasons.append(f"case gap report contains {key}")

    return reasons


def _local_preview_decision(packet: Mapping[str, Any]) -> PreflightDecision:
    preview_status = _status(packet.get("local_preview"), "status", "readiness_status")
    if preview_status not in _READY_PREVIEW_STATUSES:
        return _decision(
            PreflightOutcome.BLOCKED,
            [f"local preview metadata is not ready: {preview_status or 'missing'}"],
            ["generate a redacted local preview fixture before drafting"],
        )
    return _decision(
        PreflightOutcome.LOCAL_PREVIEW,
        ["all fixture readiness gates passed for local metadata-only preview"],
        ["generate or review the local preview without touching official DevHub state"],
    )


def _reversible_draft_decision(packet: Mapping[str, Any]) -> PreflightDecision:
    preview_status = _status(packet.get("local_preview"), "status", "readiness_status")
    devhub_status = _status(packet.get("devhub_handoff"), "status", "readiness_status", "handoff_status")

    if preview_status not in _READY_PREVIEW_STATUSES:
        return _decision(
            PreflightOutcome.BLOCKED,
            [f"reversible draft lacks ready local preview metadata: {preview_status or 'missing'}"],
            ["prepare a redacted local preview fixture first"],
        )
    if devhub_status not in _READY_DEVHUB_STATUSES:
        return _decision(
            PreflightOutcome.MANUAL_HANDOFF,
            [f"DevHub handoff is not ready for reversible draft assistance: {devhub_status or 'missing'}"],
            ["complete attended DevHub handoff readiness before browser draft work"],
        )
    return _decision(
        PreflightOutcome.REVERSIBLE_DRAFT,
        ["all fixture readiness gates passed for attended reversible draft assistance"],
        ["perform only reversible draft steps with redacted journal metadata"],
    )


def _normalized_action_class(packet: Mapping[str, Any]) -> str:
    action = packet.get("action_classification") or packet.get("action") or packet.get("action_decision_output") or {}
    if isinstance(action, Mapping):
        value = action.get("classification") or action.get("action_class") or action.get("actionClass") or action.get("kind")
    else:
        value = action
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def _status(value: Any, *keys: str) -> str:
    if isinstance(value, Mapping):
        for key in keys:
            if value.get(key) is not None:
                return str(value.get(key)).strip().lower().replace(" ", "_").replace("-", "_")
        return ""
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return bool(str(value).strip())


def _private_metadata_paths(value: Any, path: str = "$") -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).strip().lower()
            child_path = f"{path}.{key}"
            if key_text in _PRIVATE_KEYS:
                yield child_path
            else:
                yield from _private_metadata_paths(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _private_metadata_paths(child, f"{path}[{index}]")


def _decision(outcome: PreflightOutcome, reasons: Iterable[str], next_safe_actions: Iterable[str]) -> PreflightDecision:
    return PreflightDecision(
        outcome=outcome,
        reasons=tuple(reasons),
        next_safe_actions=tuple(next_safe_actions),
    )
