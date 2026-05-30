"""Fixture-first DevHub read-only evidence envelope v2 builder and validator.

This module only transforms supplied dry-run fixtures. It does not open a
browser, contact DevHub, persist auth state, or create screenshots/traces/HARs.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENVELOPE_VERSION = "devhub-readonly-evidence-envelope-v2"
REQUIRED_ATTESTATIONS = (
    "no_live_devhub",
    "no_auth_state",
    "no_screenshot",
    "no_trace",
    "no_har",
    "no_surface_registry_mutation",
)
REQUIRED_OBSERVATION_SLOTS = (
    "visible_surface_labels",
    "allowed_read_only_checks",
    "manual_login_mfa_captcha_handoff_notes",
    "redaction_checklist_outcomes",
    "operator_abort_conditions",
    "offline_validation_commands",
    "attestations",
)

_PRIVATE_OR_AUTH_KEYS = {
    "account",
    "account_id",
    "address",
    "auth",
    "auth_state",
    "auth_state_path",
    "authenticated_value",
    "authorization",
    "browser_context",
    "browser_state",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "email",
    "invoice",
    "license",
    "name",
    "password",
    "payment_detail",
    "permit_number",
    "phone",
    "private_value",
    "private_values",
    "raw_authenticated_text",
    "raw_authenticated_value",
    "raw_dom",
    "secret",
    "session",
    "session_file",
    "session_state",
    "storage_state",
    "storage_state_path",
    "token",
    "user",
}
_ARTIFACT_KEYS = {
    "browser_trace",
    "downloaded_documents",
    "har",
    "har_file",
    "har_files",
    "har_path",
    "raw_crawl_output",
    "screenshot",
    "screenshots",
    "screenshot_path",
    "trace",
    "trace_path",
}
_MUTATION_FLAGS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "guardrail_mutation",
    "monitoring_mutation",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_surface_registry",
    "prompt_mutation",
    "release_state_mutation",
    "surface_registry_mutation",
}
_SAFE_ATTESTATION_KEYS = set(REQUIRED_ATTESTATIONS)
_PRIVATE_VALUE_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b|"
    r"\b\d{3,6}\s+(?:N|NE|NW|S|SE|SW|E|W)\s+[A-Z][A-Z0-9 ]+\b|"
    r"\b(?:permit|invoice|account|license)\s*(?:number|no\.|#)?\s*[:#]\s*[A-Z0-9-]{4,}\b|"
    r"\b(?:password|secret|token|authorization|set-cookie)\s*[:=]",
    re.IGNORECASE,
)
_ARTIFACT_REFERENCE_RE = re.compile(
    r"\b(screenshot|screen shot|trace\.zip|browser trace|playwright trace|har file|\.har\b|storage state|auth state|session state)\b|"
    r"(/home/|/users/|c:\\\\users\\\\|file://|storage[_ -]?state\.json|auth[_ -]?state\.json|screenshot\.(?:png|jpe?g|webp))",
    re.IGNORECASE,
)
_LIVE_OR_AUTOMATION_CLAIM_RE = re.compile(
    r"\b(launched|ran|executed|clicked|filled|captured|stored|opened|navigated|completed)\b.{0,80}\b(live devhub|live browser|playwright|browser automation|auth state|screenshot|trace|har)\b|"
    r"\b(live devhub|live browser|playwright|browser automation)\b.{0,80}\b(launched|ran|executed|clicked|filled|captured|stored|opened|navigated|completed)\b",
    re.IGNORECASE,
)
_CONSEQUENTIAL_ENABLEMENT_RE = re.compile(
    r"\b(click|clicked|continue|continued|execute|executed|fill|filled|press|pressed|select|selected|start|started|trigger|triggered|use|used|allow|allowed|enable|enabled)\b.{0,80}\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|save draft|attach)\b|"
    r"\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|save draft|attach)\b.{0,80}\b(allowed|complete|completed|done|enabled|executed|proceed|started|successful|triggered)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|ensure[sd]?|will|shall)\b.{0,80}\b(approval|approved|code compliant|compliance|issuance|issued|legal|permit outcome|permit will|pass inspection)\b|"
    r"\b(approval|approved|issuance|issued|legal compliance|permit outcome|pass inspection)\b.{0,80}\b(guarantee[sd]?|certain|assured|will|shall)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FixtureSource:
    path: str
    document: dict[str, Any]


@dataclass(frozen=True)
class EvidenceEnvelopeValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_fixture(path: str | Path) -> FixtureSource:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError(f"fixture must contain a JSON object: {fixture_path}")
    return FixtureSource(path=str(fixture_path), document=document)


def build_envelope(plan: FixtureSource, ledger: FixtureSource) -> dict[str, Any]:
    """Build cited synthetic observation slots from read-only dry-run fixtures."""
    plan_doc = plan.document
    ledger_doc = ledger.document

    envelope = {
        "version": ENVELOPE_VERSION,
        "mode": "fixture-first-attended-read-only",
        "sources": {
            "attended_devhub_readonly_live_dry_run_plan_v2": plan.path,
            "post_briefing_dry_run_authorization_ledger_v2": ledger.path,
        },
        "observation_slots": {
            "visible_surface_labels": _slot(plan, "visible_surface_labels", plan_doc.get("visible_surface_labels", [])),
            "allowed_read_only_checks": _slot(plan, "allowed_read_only_checks", plan_doc.get("allowed_read_only_checks", [])),
            "manual_login_mfa_captcha_handoff_notes": _slot(
                plan,
                "manual_login_mfa_captcha_handoff_notes",
                plan_doc.get("manual_login_mfa_captcha_handoff_notes", []),
            ),
            "redaction_checklist_outcomes": _slot(
                ledger,
                "redaction_checklist_outcomes",
                ledger_doc.get("redaction_checklist_outcomes", []),
            ),
            "operator_abort_conditions": _slot(plan, "operator_abort_conditions", plan_doc.get("operator_abort_conditions", [])),
            "offline_validation_commands": _slot(
                ledger,
                "offline_validation_commands",
                ledger_doc.get("offline_validation_commands", []),
            ),
            "attestations": _slot(ledger, "attestations", _normalize_attestations(ledger_doc.get("attestations", {}))),
        },
    }
    require_valid_devhub_readonly_evidence_envelope_v2(envelope)
    return envelope


def write_envelope(plan_path: str | Path, ledger_path: str | Path, output_path: str | Path) -> None:
    envelope = build_envelope(load_fixture(plan_path), load_fixture(ledger_path))
    destination = Path(output_path)
    destination.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_devhub_readonly_evidence_envelope_v2(envelope: dict[str, Any]) -> EvidenceEnvelopeValidationResult:
    errors: list[str] = []
    if not isinstance(envelope, dict):
        return EvidenceEnvelopeValidationResult(False, ("envelope must be a JSON object",))
    if envelope.get("version") != ENVELOPE_VERSION:
        errors.append(f"version must be {ENVELOPE_VERSION}")
    if envelope.get("mode") != "fixture-first-attended-read-only":
        errors.append("mode must be fixture-first-attended-read-only")
    _validate_slots(envelope.get("observation_slots"), errors)
    _scan_value(envelope, "$", errors)
    return EvidenceEnvelopeValidationResult(ok=not errors, errors=tuple(dict.fromkeys(errors)))


def require_valid_devhub_readonly_evidence_envelope_v2(envelope: dict[str, Any]) -> None:
    result = validate_devhub_readonly_evidence_envelope_v2(envelope)
    if not result.ok:
        raise ValueError("invalid DevHub read-only evidence envelope v2: " + "; ".join(result.errors))


def _slot(source: FixtureSource, field: str, value: Any) -> dict[str, Any]:
    return {
        "kind": "synthetic_read_only_observation_slot",
        "value": value,
        "citations": [{"source": source.path, "field": field}],
    }


def _normalize_attestations(attestations: Any) -> dict[str, bool]:
    if not isinstance(attestations, dict):
        raise ValueError("attestations must be a JSON object")
    normalized = {name: bool(attestations.get(name, False)) for name in REQUIRED_ATTESTATIONS}
    missing = [name for name, value in normalized.items() if not value]
    if missing:
        raise ValueError("missing required read-only attestations: " + ", ".join(missing))
    return normalized


def _validate_slots(slots: Any, errors: list[str]) -> None:
    if not isinstance(slots, dict):
        errors.append("observation_slots must be an object")
        return
    for name in REQUIRED_OBSERVATION_SLOTS:
        if name not in slots:
            errors.append(f"observation_slots.{name} is required")
    for name, slot in slots.items():
        if not isinstance(slot, dict):
            errors.append(f"slot must be an object: {name}")
            continue
        citations = slot.get("citations")
        if not isinstance(citations, list) or not citations:
            errors.append(f"slot must include citations: {name}")
        elif not all(_valid_citation(citation) for citation in citations):
            errors.append(f"slot citations must include source and field: {name}")
        if slot.get("kind") != "synthetic_read_only_observation_slot":
            errors.append(f"slot has unexpected kind: {name}")
        if name in {"manual_login_mfa_captcha_handoff_notes", "redaction_checklist_outcomes"} and not _non_empty_value(slot.get("value")):
            errors.append(f"slot must include non-empty manual handoff or redaction outcomes: {name}")
    attestations = slots.get("attestations")
    if isinstance(attestations, dict):
        value = attestations.get("value")
        if not isinstance(value, dict):
            errors.append("slot attestations value must be an object")
        else:
            for name in REQUIRED_ATTESTATIONS:
                if value.get(name) is not True:
                    errors.append(f"attestations.{name} must be true")


def _valid_citation(citation: Any) -> bool:
    return isinstance(citation, dict) and isinstance(citation.get("source"), str) and bool(citation.get("source")) and isinstance(citation.get("field"), str) and bool(citation.get("field"))


def _non_empty_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(_non_empty_value(item) for item in value)
    if isinstance(value, dict):
        return bool(value)
    return value is not None


def _scan_value(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            child_path = f"{path}.{key_text}"
            if key_lower in _PRIVATE_OR_AUTH_KEYS:
                errors.append(f"{child_path} must not contain private, authenticated, credential, or session values")
            if key_lower in _ARTIFACT_KEYS:
                errors.append(f"{child_path} must not reference screenshots, traces, HAR, raw crawl output, or browser artifacts")
            if key_lower in _MUTATION_FLAGS and child is True:
                errors.append(f"{child_path} must not enable active surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation")
            if key_lower in _SAFE_ATTESTATION_KEYS and child is not True:
                errors.append(f"{child_path} must remain true")
            _scan_value(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_value(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        if _PRIVATE_VALUE_RE.search(value):
            errors.append(f"{path} must not contain private, authenticated, credential, or session values")
        if _ARTIFACT_REFERENCE_RE.search(value):
            errors.append(f"{path} must not reference screenshots, traces, HAR, auth state, storage state, or session artifacts")
        if _LIVE_OR_AUTOMATION_CLAIM_RE.search(value):
            errors.append(f"{path} must not claim browser automation, live DevHub execution, or live completion")
        if _CONSEQUENTIAL_ENABLEMENT_RE.search(value):
            errors.append(f"{path} must not enable consequential DevHub actions")
        if _GUARANTEE_RE.search(value):
            errors.append(f"{path} must not guarantee legal compliance or permitting outcomes")
