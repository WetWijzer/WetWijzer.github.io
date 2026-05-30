"""Fixture-first refresh implementation proposal v2.

This module consumes committed public-source observation, DevHub read-only surface,
and post-dry-run guardrail impact review fixtures. It proposes patch rows only;
it does not crawl, open DevHub, run processors, mutate registries, mutate active
guardrails, mutate prompts, or change release state.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ppd.devhub_surface_observation_refresh_candidate_v2 import (
    validate_devhub_surface_observation_refresh_candidate_v2,
)
from ppd.logic.post_dry_run_guardrail_impact_review_v2 import (
    assert_valid_post_dry_run_guardrail_impact_review_v2,
)
from ppd.source_observation_refresh_candidate_v2 import validate_source_observation_refresh_candidate_v2

PROPOSAL_VERSION = "refresh_implementation_proposal_v2"

ATTESTATIONS = {
    "no_live_crawl": True,
    "no_live_devhub": True,
    "no_processor": True,
    "no_registry_mutation": True,
    "no_guardrail_mutation": True,
    "no_prompt_mutation": True,
    "no_release_state_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/refresh_implementation_proposal_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_refresh_implementation_proposal_v2"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_DEPENDENCY_ORDER = [
    "validate-input-fixtures",
    "review-source-patch-rows",
    "review-surface-patch-rows",
    "review-guardrail-patch-rows",
    "rollback-readiness-check",
]

_MUTATION_FLAGS = {
    "active_source_mutation",
    "active_surface_registry_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "registry_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "mutates_registry",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_release_state",
}

_PROHIBITED_KEYS = {
    "auth_state",
    "browser_artifact",
    "browser_session",
    "crawl_output",
    "downloaded_document",
    "har",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_pdf",
    "registry_write",
    "screenshot",
    "session_file",
    "storage_state",
    "trace",
}

_PROHIBITED_TEXT = (
    "live crawl completed",
    "live crawler completed",
    "opened devhub",
    "ran processor",
    "processor completed",
    "registry updated",
    "guardrail updated",
    "prompt updated",
    "release state updated",
)


@dataclass(frozen=True)
class ProposalValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_refresh_implementation_proposal_v2_from_files(
    public_source_observation_refresh_candidate_v2_path: str | Path,
    devhub_read_only_surface_observation_refresh_candidate_v2_path: str | Path,
    post_dry_run_guardrail_impact_review_v2_path: str | Path,
) -> dict[str, Any]:
    source_path = Path(public_source_observation_refresh_candidate_v2_path)
    surface_path = Path(devhub_read_only_surface_observation_refresh_candidate_v2_path)
    guardrail_path = Path(post_dry_run_guardrail_impact_review_v2_path)

    source_packet = load_json(source_path)
    surface_packet = load_json(surface_path)
    guardrail_review = load_json(guardrail_path)

    source_result = validate_source_observation_refresh_candidate_v2(source_packet)
    if not source_result.ok:
        raise ValueError("invalid public source observation refresh candidate v2: " + "; ".join(source_result.errors))
    surface_result = validate_devhub_surface_observation_refresh_candidate_v2(surface_packet)
    if not surface_result.ok:
        raise ValueError("invalid DevHub read-only surface observation refresh candidate v2: " + "; ".join(surface_result.errors))
    assert_valid_post_dry_run_guardrail_impact_review_v2(guardrail_review)

    source_ref = source_path.as_posix()
    surface_ref = surface_path.as_posix()
    guardrail_ref = guardrail_path.as_posix()

    proposal = {
        "proposal_version": PROPOSAL_VERSION,
        "fixture_first": True,
        "source_fixtures": {
            "public_source_observation_refresh_candidate_v2": source_ref,
            "devhub_read_only_surface_observation_refresh_candidate_v2": surface_ref,
            "post_dry_run_guardrail_impact_review_v2": guardrail_ref,
        },
        "proposed_source_patch_rows": _source_patch_rows(source_packet, source_ref),
        "proposed_surface_patch_rows": _surface_patch_rows(surface_packet, surface_ref),
        "proposed_guardrail_patch_rows": _guardrail_patch_rows(guardrail_review, guardrail_ref),
        "reviewer_owner_fields": _reviewer_owner_fields(source_packet, surface_packet, guardrail_review),
        "dependency_ordering": list(_DEPENDENCY_ORDER),
        "rollback_notes": _rollback_notes(source_packet, surface_packet, guardrail_review, source_ref, surface_ref, guardrail_ref),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(ATTESTATIONS),
    }
    require_refresh_implementation_proposal_v2(proposal)
    return proposal


def validate_refresh_implementation_proposal_v2(proposal: dict[str, Any]) -> ProposalValidationResult:
    errors: list[str] = []
    if proposal.get("proposal_version") != PROPOSAL_VERSION:
        errors.append(f"proposal_version must be {PROPOSAL_VERSION}")
    if proposal.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if proposal.get("attestations") != ATTESTATIONS:
        errors.append("attestations must preserve no-live/no-mutation proposal guardrails")
    _validate_patch_rows(proposal.get("proposed_source_patch_rows"), "proposed_source_patch_rows", errors)
    _validate_patch_rows(proposal.get("proposed_surface_patch_rows"), "proposed_surface_patch_rows", errors)
    _validate_patch_rows(proposal.get("proposed_guardrail_patch_rows"), "proposed_guardrail_patch_rows", errors)
    _validate_reviewer_owners(proposal.get("reviewer_owner_fields"), errors)
    _validate_dependency_ordering(proposal.get("dependency_ordering"), errors)
    _validate_rollback_notes(proposal.get("rollback_notes"), errors)
    if not isinstance(proposal.get("offline_validation_commands"), list) or not proposal.get("offline_validation_commands"):
        errors.append("offline_validation_commands must be a non-empty list")
    _reject_prohibited_content(proposal, "$", errors)
    return ProposalValidationResult(ok=not errors, errors=tuple(errors))


def require_refresh_implementation_proposal_v2(proposal: dict[str, Any]) -> None:
    result = validate_refresh_implementation_proposal_v2(proposal)
    if not result.ok:
        raise ValueError("invalid refresh implementation proposal v2: " + "; ".join(result.errors))


def _source_patch_rows(packet: dict[str, Any], fixture_ref: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in _dicts(packet.get("candidates")):
        source_id = _text(candidate.get("source_id"))
        rows.append(
            {
                "patch_id": f"source-patch-{source_id}",
                "patch_kind": "source_registry_metadata_review_row",
                "proposal_scope": "proposed-only",
                "source_id": source_id,
                "affected_source_ids": _strings(candidate.get("affected_source_ids")) or [source_id],
                "reviewer_owner": _text(candidate.get("reviewer_owner")) or "ppd-reviewer-unassigned",
                "dependency_after": ["validate-input-fixtures"],
                "rollback_note": "Discard this proposed row and keep the current source registry unchanged.",
                "citations": [{"fixture": fixture_ref, "field": f"candidates[{source_id}]"}] + _dicts(candidate.get("citations")),
            }
        )
    return rows


def _surface_patch_rows(packet: dict[str, Any], fixture_ref: str) -> list[dict[str, Any]]:
    confidence = {_text(item.get("surface_id")): item for item in _dicts(packet.get("selector_confidence_notes"))}
    handoff = {_text(item.get("surface_id")): item for item in _dicts(packet.get("manual_handoff_dispositions"))}
    redaction = {_text(item.get("surface_id")): item for item in _dicts(packet.get("redaction_dispositions"))}
    owners = {_text(item.get("surface_id")): _text(item.get("reviewer_owner")) for item in _dicts(packet.get("reviewer_owner_fields"))}
    rows: list[dict[str, Any]] = []
    for observation in _dicts(packet.get("observations")):
        surface_id = _text(observation.get("surface_id"))
        rows.append(
            {
                "patch_id": f"surface-patch-{surface_id}",
                "patch_kind": "surface_registry_read_only_review_row",
                "proposal_scope": "proposed-only",
                "surface_id": surface_id,
                "read_only": True,
                "selector_confidence": _text(confidence.get(surface_id, {}).get("confidence")),
                "manual_handoff_required": bool(handoff.get(surface_id, {}).get("required", False)),
                "redaction_disposition": _text(redaction.get(surface_id, {}).get("disposition")),
                "reviewer_owner": owners.get(surface_id) or "ppd-reviewer-unassigned",
                "dependency_after": ["review-source-patch-rows"],
                "rollback_note": "Discard this proposed row and keep the current surface registry unchanged.",
                "citations": [{"fixture": fixture_ref, "field": f"observations[{surface_id}]"}] + _dicts(observation.get("citations")),
            }
        )
    return rows


def _guardrail_patch_rows(review: dict[str, Any], fixture_ref: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in _dicts(review.get("impact_decisions")):
        decision_id = _text(decision.get("decision_id"))
        rows.append(
            {
                "patch_id": f"guardrail-patch-{decision_id}",
                "patch_kind": "guardrail_predicate_review_row",
                "proposal_scope": "proposed-only",
                "decision_id": decision_id,
                "guardrail_bundle_id": _text(review.get("guardrail_bundle_id")),
                "predicate_ids": _strings(decision.get("predicate_ids")),
                "dependency_after": ["review-surface-patch-rows"],
                "rollback_note": _text(review.get("rollback_notes")),
                "citations": [{"fixture": fixture_ref, "field": f"impact_decisions[{decision_id}]", "citation_ids": _strings(decision.get("citation_ids"))}],
            }
        )
    for check in _dicts(review.get("blocked_action_checks")):
        action_id = _text(check.get("action_id"))
        rows.append(
            {
                "patch_id": f"guardrail-block-{action_id}",
                "patch_kind": "blocked_consequential_action_review_row",
                "proposal_scope": "proposed-only",
                "action_id": action_id,
                "blocked": check.get("blocked") is True,
                "dependency_after": ["review-guardrail-patch-rows"],
                "rollback_note": _text(review.get("rollback_notes")),
                "citations": [{"fixture": fixture_ref, "field": f"blocked_action_checks[{action_id}]", "citation_ids": _strings(check.get("citation_ids"))}],
            }
        )
    return rows


def _reviewer_owner_fields(source_packet: dict[str, Any], surface_packet: dict[str, Any], review: dict[str, Any]) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    for candidate in _dicts(source_packet.get("candidates")):
        fields.append({"scope": f"source:{_text(candidate.get('source_id'))}", "reviewer_owner": _text(candidate.get("reviewer_owner")) or "ppd-reviewer-unassigned"})
    for owner in _dicts(surface_packet.get("reviewer_owner_fields")):
        fields.append({"scope": f"surface:{_text(owner.get('surface_id'))}", "reviewer_owner": _text(owner.get("reviewer_owner")) or "ppd-reviewer-unassigned"})
    for owner in _dicts(review.get("reviewer_owners")):
        fields.append({"scope": "guardrail-impact-review", "reviewer_owner": _text(owner.get("owner_id") or owner.get("team") or owner.get("name"))})
    return [field for field in fields if field["reviewer_owner"]]


def _rollback_notes(
    source_packet: dict[str, Any],
    surface_packet: dict[str, Any],
    review: dict[str, Any],
    source_ref: str,
    surface_ref: str,
    guardrail_ref: str,
) -> list[dict[str, Any]]:
    return [
        {
            "scope": "source-patch-rows",
            "note": "No registry write is performed; discard proposed source rows to roll back this proposal.",
            "citations": [{"fixture": source_ref, "field": "candidates", "affected_source_ids": _strings(source_packet.get("affected_source_ids"))}],
        },
        {
            "scope": "surface-patch-rows",
            "note": "No surface registry write is performed; discard proposed surface rows to roll back this proposal.",
            "citations": [{"fixture": surface_ref, "field": "observations"}],
        },
        {
            "scope": "guardrail-patch-rows",
            "note": _text(review.get("rollback_notes")),
            "citations": [{"fixture": guardrail_ref, "field": "rollback_notes"}],
        },
    ]


def _validate_patch_rows(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{name} must be a non-empty list")
        return
    for index, row in enumerate(value):
        path = f"{name}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{path} must be an object")
            continue
        for field in ("patch_id", "patch_kind", "proposal_scope", "rollback_note"):
            if not _text(row.get(field)):
                errors.append(f"{path}.{field} must be present")
        if row.get("proposal_scope") != "proposed-only":
            errors.append(f"{path}.proposal_scope must be proposed-only")
        if not _has_citations(row.get("citations")):
            errors.append(f"{path}.citations must cite fixture evidence")
        if not isinstance(row.get("dependency_after"), list) or not row.get("dependency_after"):
            errors.append(f"{path}.dependency_after must be present")
        if name != "proposed_guardrail_patch_rows" and not _text(row.get("reviewer_owner")):
            errors.append(f"{path}.reviewer_owner must be present")


def _validate_reviewer_owners(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("reviewer_owner_fields must be a non-empty list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not _text(item.get("scope")) or not _text(item.get("reviewer_owner")):
            errors.append(f"reviewer_owner_fields[{index}] must include scope and reviewer_owner")


def _validate_dependency_ordering(value: Any, errors: list[str]) -> None:
    if value != _DEPENDENCY_ORDER:
        errors.append("dependency_ordering must preserve fixture validation, source, surface, guardrail, rollback review order")


def _validate_rollback_notes(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("rollback_notes must be a non-empty list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not _text(item.get("scope")) or not _text(item.get("note")) or not _has_citations(item.get("citations")):
            errors.append(f"rollback_notes[{index}] must include scope, note, and citations")


def _reject_prohibited_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            lowered_key = str(key).lower()
            if lowered_key in _PROHIBITED_KEYS:
                errors.append(f"{child_path} is prohibited in refresh implementation proposals")
            if lowered_key in _MUTATION_FLAGS and child is True:
                errors.append(f"{child_path} must not be true in refresh implementation proposals")
            _reject_prohibited_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in _PROHIBITED_TEXT):
            errors.append(f"{path} contains prohibited live execution or mutation claim")


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []


def _has_citations(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, dict) and item for item in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
