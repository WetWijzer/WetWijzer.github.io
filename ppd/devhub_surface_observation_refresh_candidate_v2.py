"""Fixture-first DevHub read-only surface observation refresh candidate v2.

This module intentionally consumes committed review fixtures only. It does not open a
browser, authenticate, mutate a surface registry, or create crawl artifacts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REQUIRED_ATTESTATIONS = {
    "no_live_devhub": True,
    "no_auth_state": True,
    "no_screenshot": True,
    "no_trace": True,
    "no_har": True,
    "no_surface_registry_mutation": True,
}

_PROHIBITED_ARTIFACT_KEYS = {
    "auth_state",
    "browser_artifact",
    "browser_artifacts",
    "cookies",
    "credential",
    "credentials",
    "har",
    "har_path",
    "password",
    "playwright_trace",
    "screenshot",
    "screenshot_path",
    "session",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "trace_path",
}

_PRIVATE_VALUE_KEYS = {
    "account_id",
    "address",
    "api_key",
    "applicant_name",
    "authorization",
    "case_number",
    "cookie",
    "email",
    "license_number",
    "permit_number",
    "phone",
    "private_value",
    "session_id",
    "ssn",
    "username",
}

_PROHIBITED_CLAIMS = (
    "browser automation completed",
    "devhub completed",
    "devhub live run completed",
    "live devhub completion",
    "playwright clicked",
    "submitted successfully",
    "submission completed",
    "permit approved",
    "permit will be approved",
    "approval is guaranteed",
    "guaranteed approval",
    "legal guarantee",
    "legally guaranteed",
    "permitting outcome guaranteed",
    "outcome guaranteed",
)

_CONSEQUENTIAL_ACTIONS = (
    "cancel permit",
    "certify acknowledgement",
    "complete payment",
    "confirm submission",
    "create account",
    "enter payment",
    "final submit",
    "make payment",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "submit payment",
    "upload correction",
    "withdraw permit",
)

_MUTATION_FLAGS = {
    "active_surface_registry_mutation",
    "surface_registry_mutation",
    "mutates_surface_registry",
    "active_guardrail_mutation",
    "guardrail_mutation",
    "mutates_guardrails",
    "active_prompt_mutation",
    "prompt_mutation",
    "mutates_prompts",
    "active_monitoring_mutation",
    "monitoring_mutation",
    "mutates_monitoring",
    "active_release_state_mutation",
    "release_state_mutation",
    "mutates_release_state",
    "active_agent_state_mutation",
    "agent_state_mutation",
    "mutates_agent_state",
}


@dataclass(frozen=True)
class CandidateValidationResult:
    ok: bool
    errors: tuple[str, ...]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must be a JSON object: {path}")
    return data


def _fixture_ref(path: Path) -> str:
    return path.as_posix()


def build_candidate_from_files(
    live_dry_run_acceptance_review_packet_v2_path: Path,
    attended_devhub_read_only_evidence_envelope_v2_path: Path,
    surface_registry_refresh_review_fixture_path: Path,
) -> dict[str, Any]:
    """Build a cited synthetic refresh candidate from read-only fixtures."""

    packet = _load_json(live_dry_run_acceptance_review_packet_v2_path)
    envelope = _load_json(attended_devhub_read_only_evidence_envelope_v2_path)
    registry = _load_json(surface_registry_refresh_review_fixture_path)

    packet_ref = _fixture_ref(live_dry_run_acceptance_review_packet_v2_path)
    envelope_ref = _fixture_ref(attended_devhub_read_only_evidence_envelope_v2_path)
    registry_ref = _fixture_ref(surface_registry_refresh_review_fixture_path)

    surfaces = registry.get("surfaces", [])
    if not isinstance(surfaces, list):
        raise ValueError("surface registry fixture must contain a surfaces list")

    packet_actions = packet.get("accepted_actions", [])
    if not isinstance(packet_actions, list):
        raise ValueError("acceptance review packet fixture must contain accepted_actions list")

    envelope_items = envelope.get("evidence", [])
    if not isinstance(envelope_items, list):
        raise ValueError("evidence envelope fixture must contain evidence list")

    evidence_by_surface = {item.get("surface_id"): item for item in envelope_items if isinstance(item, dict)}
    actions_by_surface = {item.get("surface_id"): item for item in packet_actions if isinstance(item, dict)}

    observations: list[dict[str, Any]] = []
    selector_confidence_notes: list[dict[str, Any]] = []
    manual_handoff_dispositions: list[dict[str, Any]] = []
    redaction_dispositions: list[dict[str, Any]] = []
    reviewer_owner_fields: list[dict[str, Any]] = []

    for surface in surfaces:
        if not isinstance(surface, dict):
            continue
        surface_id = str(surface.get("surface_id", "")).strip()
        if not surface_id:
            continue

        evidence = evidence_by_surface.get(surface_id, {})
        action = actions_by_surface.get(surface_id, {})
        confidence = str(surface.get("selector_confidence", "")).strip()
        handoff = bool(surface.get("manual_handoff_required", False))
        redaction = str(surface.get("redaction", "")).strip()
        reviewer_owner = str(surface.get("reviewer_owner", "unassigned"))

        observations.append(
            {
                "surface_id": surface_id,
                "surface_name": surface.get("surface_name"),
                "synthetic_observation": evidence.get("observation"),
                "synthetic_action_candidate": action.get("action_candidate"),
                "read_only": True,
                "citations": [
                    {"fixture": packet_ref, "field": f"accepted_actions[{surface_id}]", "supports": "action"},
                    {"fixture": envelope_ref, "field": f"evidence[{surface_id}]", "supports": "surface"},
                    {"fixture": registry_ref, "field": f"surfaces[{surface_id}]", "supports": "disposition"},
                ],
            }
        )
        selector_confidence_notes.append(
            {
                "surface_id": surface_id,
                "confidence": confidence,
                "note": surface.get("selector_note", "fixture-derived selector confidence"),
                "citations": [{"fixture": registry_ref, "field": f"surfaces[{surface_id}].selector_confidence"}],
            }
        )
        manual_handoff_dispositions.append(
            {
                "surface_id": surface_id,
                "required": handoff,
                "reason": surface.get("manual_handoff_reason", "not required"),
                "citations": [{"fixture": registry_ref, "field": f"surfaces[{surface_id}].manual_handoff_required"}],
            }
        )
        redaction_dispositions.append(
            {
                "surface_id": surface_id,
                "disposition": redaction,
                "reason": surface.get("redaction_reason", "fixture contains no sensitive values"),
                "citations": [{"fixture": registry_ref, "field": f"surfaces[{surface_id}].redaction"}],
            }
        )
        reviewer_owner_fields.append({"surface_id": surface_id, "reviewer_owner": reviewer_owner})

    candidate = {
        "candidate_version": "devhub_read_only_surface_observation_refresh_candidate_v2",
        "source_fixtures": {
            "live_dry_run_acceptance_review_packet_v2": packet_ref,
            "attended_devhub_read_only_evidence_envelope_v2": envelope_ref,
            "surface_registry_refresh_review_fixture": registry_ref,
        },
        "observations": observations,
        "selector_confidence_notes": selector_confidence_notes,
        "manual_handoff_dispositions": manual_handoff_dispositions,
        "redaction_dispositions": redaction_dispositions,
        "reviewer_owner_fields": reviewer_owner_fields,
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/devhub_surface_observation_refresh_candidate_v2.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_devhub_surface_observation_refresh_candidate_v2.py"],
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ],
        "attestations": dict(_REQUIRED_ATTESTATIONS),
    }
    require_devhub_surface_observation_refresh_candidate_v2(candidate)
    return candidate


def validate_devhub_surface_observation_refresh_candidate_v2(packet: dict[str, Any]) -> CandidateValidationResult:
    errors: list[str] = []
    if packet.get("candidate_version") != "devhub_read_only_surface_observation_refresh_candidate_v2":
        errors.append("candidate_version must be devhub_read_only_surface_observation_refresh_candidate_v2")
    if packet.get("attestations") != _REQUIRED_ATTESTATIONS:
        errors.append("attestations must preserve read-only no-artifact guardrails")
    _validate_observations(packet.get("observations"), errors)
    _validate_selector_confidence_notes(packet.get("selector_confidence_notes"), errors)
    _validate_manual_handoff_dispositions(packet.get("manual_handoff_dispositions"), errors)
    _validate_redaction_dispositions(packet.get("redaction_dispositions"), errors)
    _reject_sensitive_keys_and_values(packet, "$", errors)
    _reject_prohibited_claims(packet, "$", errors)
    _reject_mutation_flags(packet, "$", errors)
    return CandidateValidationResult(ok=not errors, errors=tuple(errors))


def require_devhub_surface_observation_refresh_candidate_v2(packet: dict[str, Any]) -> None:
    result = validate_devhub_surface_observation_refresh_candidate_v2(packet)
    if not result.ok:
        raise ValueError("invalid DevHub surface observation refresh candidate v2: " + "; ".join(result.errors))


def write_candidate(candidate: dict[str, Any], output_path: Path) -> None:
    require_devhub_surface_observation_refresh_candidate_v2(candidate)
    output_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_observations(observations: Any, errors: list[str]) -> None:
    if not isinstance(observations, list) or not observations:
        errors.append("observations must be a non-empty list")
        return
    for index, observation in enumerate(observations):
        path = f"observations[{index}]"
        if not isinstance(observation, dict):
            errors.append(f"{path} must be an object")
            continue
        if observation.get("read_only") is not True:
            errors.append(f"{path}.read_only must be true")
        if not _non_empty_string(observation.get("surface_id")):
            errors.append(f"{path}.surface_id is required")
        if not _non_empty_string(observation.get("synthetic_observation")):
            errors.append(f"{path}.synthetic_observation is required")
        if not _non_empty_string(observation.get("synthetic_action_candidate")):
            errors.append(f"{path}.synthetic_action_candidate is required")
        citations = observation.get("citations")
        if not _has_citations(citations):
            errors.append(f"{path}.citations must cite surface and action observations")
        elif not _has_supported_citation(citations, "surface") or not _has_supported_citation(citations, "action"):
            errors.append(f"{path}.citations must include surface and action support")


def _validate_selector_confidence_notes(notes: Any, errors: list[str]) -> None:
    if not isinstance(notes, list) or not notes:
        errors.append("selector_confidence_notes must be a non-empty list")
        return
    for index, note in enumerate(notes):
        path = f"selector_confidence_notes[{index}]"
        if not isinstance(note, dict):
            errors.append(f"{path} must be an object")
            continue
        if not _non_empty_string(note.get("surface_id")):
            errors.append(f"{path}.surface_id is required")
        if str(note.get("confidence", "")).strip() not in {"high", "medium", "low", "needs-review", "unknown"}:
            errors.append(f"{path}.confidence must be supplied as an allowed selector-confidence disposition")
        if not _has_citations(note.get("citations")):
            errors.append(f"{path}.citations are required")


def _validate_manual_handoff_dispositions(dispositions: Any, errors: list[str]) -> None:
    if not isinstance(dispositions, list) or not dispositions:
        errors.append("manual_handoff_dispositions must be a non-empty list")
        return
    for index, disposition in enumerate(dispositions):
        path = f"manual_handoff_dispositions[{index}]"
        if not isinstance(disposition, dict):
            errors.append(f"{path} must be an object")
            continue
        if not _non_empty_string(disposition.get("surface_id")):
            errors.append(f"{path}.surface_id is required")
        if not isinstance(disposition.get("required"), bool):
            errors.append(f"{path}.required must be a boolean manual-handoff disposition")
        if not _non_empty_string(disposition.get("reason")):
            errors.append(f"{path}.reason is required")
        if not _has_citations(disposition.get("citations")):
            errors.append(f"{path}.citations are required")


def _validate_redaction_dispositions(dispositions: Any, errors: list[str]) -> None:
    allowed = {"none", "redacted", "synthetic-only", "omit-private-values"}
    if not isinstance(dispositions, list) or not dispositions:
        errors.append("redaction_dispositions must be a non-empty list")
        return
    for index, disposition in enumerate(dispositions):
        path = f"redaction_dispositions[{index}]"
        if not isinstance(disposition, dict):
            errors.append(f"{path} must be an object")
            continue
        if not _non_empty_string(disposition.get("surface_id")):
            errors.append(f"{path}.surface_id is required")
        if str(disposition.get("disposition", "")).strip() not in allowed:
            errors.append(f"{path}.disposition must record an allowed redaction outcome")
        if not _non_empty_string(disposition.get("reason")):
            errors.append(f"{path}.reason is required")
        if not _has_citations(disposition.get("citations")):
            errors.append(f"{path}.citations are required")


def _reject_sensitive_keys_and_values(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered_key = str(key).lower()
            child_path = f"{path}.{key}"
            if lowered_key in _PROHIBITED_ARTIFACT_KEYS:
                errors.append(f"{child_path} is prohibited because it references credentials, session/auth state, screenshots, traces, HAR, or browser artifacts")
            if lowered_key in _PRIVATE_VALUE_KEYS:
                errors.append(f"{child_path} is prohibited because DevHub surface refresh candidates must not contain private or authenticated values")
            _reject_sensitive_keys_and_values(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive_keys_and_values(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered = value.lower()
        sensitive_terms = (
            "bearer ",
            "cookie:",
            "password=",
            "sessionid",
            "storage_state",
            "trace.zip",
            ".har",
            ".png",
            ".webm",
            "screenshot",
            "authenticated value",
            "private applicant",
            "api key",
        )
        if any(term in lowered for term in sensitive_terms):
            errors.append(f"{path} appears to contain a private/authenticated value or browser artifact reference")


def _reject_prohibited_claims(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in _PROHIBITED_CLAIMS):
            errors.append(f"{path} contains prohibited browser automation, live DevHub completion, legal, or permitting outcome claim")
        if any(term in lowered for term in _CONSEQUENTIAL_ACTIONS):
            errors.append(f"{path} appears to enable a consequential DevHub action")
    elif isinstance(value, dict):
        for key, child in value.items():
            _reject_prohibited_claims(child, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_claims(child, f"{path}[{index}]", errors)


def _reject_mutation_flags(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if str(key) in _MUTATION_FLAGS and child is True:
                errors.append(f"{child_path} must not be true in DevHub surface observation refresh candidates")
            _reject_mutation_flags(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_mutation_flags(child, f"{path}[{index}]", errors)


def _has_citations(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, dict) and item for item in value)


def _has_supported_citation(citations: Any, support: str) -> bool:
    if not isinstance(citations, list):
        return False
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        if citation.get("supports") == support:
            return True
        field = str(citation.get("field", "")).lower()
        if support == "surface" and "evidence" in field:
            return True
        if support == "action" and "accepted_actions" in field:
            return True
    return False


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
