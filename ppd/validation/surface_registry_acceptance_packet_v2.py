from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

PRIVATE_VALUE_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|bearer\s+[a-z0-9._-]+|session[_-]?id|cookie|authorization)",
    re.IGNORECASE,
)
ARTIFACT_RE = re.compile(r"\b(screenshot|trace|har|storage_state|auth_state|cookies?\.json|\.har|\.trace|\.png)\b", re.IGNORECASE)
LIVE_EXEC_RE = re.compile(r"\b(live\s+(devhub|browser)|devhub\s+login|authenticated\s+browser|playwright\s+run|browser\s+execution)\b", re.IGNORECASE)
GUARANTEE_RE = re.compile(r"\b(guarantee|guaranteed|approved|permit\s+will\s+be|legal\s+advice|compliant\s+with\s+law)\b", re.IGNORECASE)
CONSEQUENTIAL_RE = re.compile(r"\b(submit|submission|certify|certification|pay|payment|upload|cancel|schedule|book|file\s+permit)\b", re.IGNORECASE)
MUTATION_KEYS = {
    "active_surface_registry_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
}
MUTATION_KEY_PARTS = ("surface_registry", "guardrail", "prompt", "monitoring", "release_state", "agent_state")


def _walk(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            out.append(str(key))
            out.extend(_walk(item))
    elif isinstance(value, str):
        out.append(value)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            out.extend(_walk(item))
    else:
        out.append(str(value))
    return out


def _present(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def _citations(decision: Mapping[str, Any]) -> Any:
    return decision.get("citations") or decision.get("evidence") or decision.get("source_citations")


def validate_surface_registry_acceptance_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    decisions = packet.get("acceptance_decisions") or packet.get("decisions") or []
    if not isinstance(decisions, Sequence) or isinstance(decisions, (str, bytes, bytearray)):
        errors.append("decisions_not_list")
        decisions = []

    seen = {"accepted": False, "deferred": False, "rejected": False}
    for index, decision in enumerate(decisions):
        if not isinstance(decision, Mapping):
            errors.append(f"decision_{index}_not_object")
            continue
        disposition = str(decision.get("disposition") or decision.get("decision") or "").lower()
        if disposition in seen:
            seen[disposition] = True
        if disposition in seen and not _present(decision.get("rationale")):
            errors.append(f"missing_{disposition}_rationale")
        if not _present(_citations(decision)):
            errors.append("uncited_acceptance_decision")

    for disposition, found in seen.items():
        if not found:
            errors.append(f"missing_{disposition}_decision")

    dispositions = packet.get("dispositions") or {}
    selector_confidence = packet.get("selector_confidence") or dispositions.get("selector_confidence") if isinstance(dispositions, Mapping) else None
    manual_handoff = packet.get("manual_handoff") or dispositions.get("manual_handoff") if isinstance(dispositions, Mapping) else None
    if not _present(selector_confidence):
        errors.append("missing_selector_confidence_disposition")
    if not _present(manual_handoff):
        errors.append("missing_manual_handoff_disposition")
    if not _present(packet.get("redaction_gates")):
        errors.append("missing_redaction_gates")
    if not _present(packet.get("rollback_notes")):
        errors.append("missing_rollback_notes")

    searchable = "\n".join(_walk(packet))
    if PRIVATE_VALUE_RE.search(searchable):
        errors.append("private_or_authenticated_value")
    if ARTIFACT_RE.search(searchable):
        errors.append("session_auth_or_browser_artifact_reference")
    if LIVE_EXEC_RE.search(searchable):
        errors.append("live_devhub_or_browser_execution_claim")
    if GUARANTEE_RE.search(searchable):
        errors.append("legal_or_permitting_outcome_guarantee")
    if CONSEQUENTIAL_RE.search(searchable):
        errors.append("consequential_action_enablement")

    flags = packet.get("mutation_flags") or packet.get("active_mutation_flags") or {}
    if isinstance(flags, Mapping):
        for key, value in flags.items():
            key_text = str(key).lower()
            if bool(value) and (key_text in MUTATION_KEYS or any(part in key_text for part in MUTATION_KEY_PARTS)):
                errors.append("active_mutation_flag")
                break
    elif flags:
        errors.append("active_mutation_flag")

    return sorted(set(errors))


def assert_surface_registry_acceptance_packet_v2(packet: Mapping[str, Any]) -> None:
    errors = validate_surface_registry_acceptance_packet_v2(packet)
    if errors:
        raise ValueError("surface-registry acceptance packet v2 rejected: " + ", ".join(errors))
