"""Deterministic Playwright/PDF handoff validation for PP&D draft automation.

This module intentionally does not drive a browser, read private files, write PDFs,
or contact DevHub. It validates commit-safe fixtures that describe the handoff
between redacted user facts, reversible draft field fills, local PDF previews,
and exact-confirmation checkpoints for official DevHub transitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


REDACTED_VALUE_RE = re.compile(r"^\[[A-Z0-9][A-Z0-9_ .:/@+-]{1,120}\]$")
OFFICIAL_ACTION_KINDS = frozenset(
    {
        "account_creation",
        "captcha",
        "cancel",
        "certify",
        "fee_payment",
        "inspection_schedule",
        "mfa",
        "password_recovery",
        "payment_detail_entry",
        "submit",
        "upload",
    }
)
REVERSIBLE_DRAFT_ACTION_KINDS = frozenset({"draft_field_fill", "pdf_preview_fill", "navigate", "review"})


@dataclass(frozen=True)
class DraftFieldMapping:
    """A reversible field fill shared by DevHub draft UI and local PDF preview."""

    fact_key: str
    devhub_field: str
    pdf_field: str
    label: str
    source_evidence_id: str


@dataclass(frozen=True)
class DevHubTransition:
    """A DevHub transition and the confirmation required before it may proceed."""

    name: str
    action_kind: str
    exact_confirmation: str | None = None
    confirmation_provided: str | None = None


@dataclass(frozen=True)
class HandoffValidationResult:
    ok: bool
    draft_fields: dict[str, str] = field(default_factory=dict)
    pdf_preview_fields: dict[str, str] = field(default_factory=dict)
    blocked_transitions: tuple[str, ...] = ()
    allowed_transitions: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    audit_events: tuple[dict[str, str], ...] = ()


def load_handoff_fixture(path: str | Path) -> Mapping[str, Any]:
    """Load a JSON handoff fixture from a committed PP&D test fixture path."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as fixture_file:
        payload = json.load(fixture_file)
    if not isinstance(payload, dict):
        raise ValueError("handoff fixture root must be a JSON object")
    return payload


def validate_playwright_pdf_handoff(payload: Mapping[str, Any]) -> HandoffValidationResult:
    """Validate a redacted draft-fill handoff without browser or PDF side effects."""

    findings: list[str] = []
    blocked_transitions: list[str] = []
    allowed_transitions: list[str] = []
    audit_events: list[dict[str, str]] = []
    draft_fields: dict[str, str] = {}
    pdf_preview_fields: dict[str, str] = {}

    facts = _mapping(payload.get("redacted_user_facts"), "redacted_user_facts", findings)
    mappings = _sequence(payload.get("field_mappings"), "field_mappings", findings)
    transitions = _sequence(payload.get("devhub_transitions"), "devhub_transitions", findings)

    for index, item in enumerate(mappings):
        if not isinstance(item, Mapping):
            findings.append(f"field_mappings[{index}] must be an object")
            continue
        mapping = _parse_mapping(item, index, findings)
        if mapping is None:
            continue
        fact_value = facts.get(mapping.fact_key)
        if not isinstance(fact_value, str) or not REDACTED_VALUE_RE.fullmatch(fact_value):
            findings.append(f"fact {mapping.fact_key!r} must be present as a redacted token")
            continue
        draft_fields[mapping.devhub_field] = fact_value
        pdf_preview_fields[mapping.pdf_field] = fact_value
        audit_events.append(
            {
                "event": "draft_fact_mapped",
                "fact_key": mapping.fact_key,
                "devhub_field": mapping.devhub_field,
                "pdf_field": mapping.pdf_field,
                "source_evidence_id": mapping.source_evidence_id,
            }
        )

    for index, item in enumerate(transitions):
        if not isinstance(item, Mapping):
            findings.append(f"devhub_transitions[{index}] must be an object")
            continue
        transition = _parse_transition(item, index, findings)
        if transition is None:
            continue
        if transition.action_kind in OFFICIAL_ACTION_KINDS:
            if not transition.exact_confirmation:
                findings.append(f"official transition {transition.name!r} lacks an exact confirmation checkpoint")
                blocked_transitions.append(transition.name)
            elif transition.confirmation_provided != transition.exact_confirmation:
                blocked_transitions.append(transition.name)
                audit_events.append(
                    {
                        "event": "official_transition_blocked",
                        "transition": transition.name,
                        "action_kind": transition.action_kind,
                    }
                )
            else:
                allowed_transitions.append(transition.name)
                audit_events.append(
                    {
                        "event": "official_transition_confirmed",
                        "transition": transition.name,
                        "action_kind": transition.action_kind,
                    }
                )
            continue
        if transition.action_kind in REVERSIBLE_DRAFT_ACTION_KINDS:
            allowed_transitions.append(transition.name)
            audit_events.append(
                {
                    "event": "reversible_transition_allowed",
                    "transition": transition.name,
                    "action_kind": transition.action_kind,
                }
            )
        else:
            findings.append(f"transition {transition.name!r} has unknown action kind {transition.action_kind!r}")
            blocked_transitions.append(transition.name)

    if not draft_fields:
        findings.append("fixture must map at least one redacted fact into a DevHub draft field")
    if not pdf_preview_fields:
        findings.append("fixture must map at least one redacted fact into a PDF preview field")
    if not blocked_transitions:
        findings.append("fixture must prove at least one official DevHub transition remains blocked")

    return HandoffValidationResult(
        ok=not findings,
        draft_fields=draft_fields,
        pdf_preview_fields=pdf_preview_fields,
        blocked_transitions=tuple(blocked_transitions),
        allowed_transitions=tuple(allowed_transitions),
        findings=tuple(findings),
        audit_events=tuple(audit_events),
    )


def _mapping(value: object, name: str, findings: list[str]) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    findings.append(f"{name} must be an object")
    return {}


def _sequence(value: object, name: str, findings: list[str]) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    findings.append(f"{name} must be an array")
    return ()


def _required_string(item: Mapping[str, Any], key: str, context: str, findings: list[str]) -> str | None:
    value = item.get(key)
    if isinstance(value, str) and value.strip():
        return value
    findings.append(f"{context}.{key} must be a non-empty string")
    return None


def _optional_string(item: Mapping[str, Any], key: str) -> str | None:
    value = item.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return None


def _parse_mapping(item: Mapping[str, Any], index: int, findings: list[str]) -> DraftFieldMapping | None:
    context = f"field_mappings[{index}]"
    fact_key = _required_string(item, "fact_key", context, findings)
    devhub_field = _required_string(item, "devhub_field", context, findings)
    pdf_field = _required_string(item, "pdf_field", context, findings)
    label = _required_string(item, "label", context, findings)
    source_evidence_id = _required_string(item, "source_evidence_id", context, findings)
    if not all((fact_key, devhub_field, pdf_field, label, source_evidence_id)):
        return None
    return DraftFieldMapping(
        fact_key=fact_key,
        devhub_field=devhub_field,
        pdf_field=pdf_field,
        label=label,
        source_evidence_id=source_evidence_id,
    )


def _parse_transition(item: Mapping[str, Any], index: int, findings: list[str]) -> DevHubTransition | None:
    context = f"devhub_transitions[{index}]"
    name = _required_string(item, "name", context, findings)
    action_kind = _required_string(item, "action_kind", context, findings)
    if not name or not action_kind:
        return None
    return DevHubTransition(
        name=name,
        action_kind=action_kind,
        exact_confirmation=_optional_string(item, "exact_confirmation"),
        confirmation_provided=_optional_string(item, "confirmation_provided"),
    )
