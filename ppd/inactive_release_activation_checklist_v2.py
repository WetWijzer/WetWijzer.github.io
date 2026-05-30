"""Fixture-first inactive release activation checklist v2.

This module consumes guarded agent replay acceptance packet v2 and produces an
inactive activation checklist. It does not promote releases, mutate release
state, touch public sources, open DevHub, store private artifacts, or perform
official PP&D actions.
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ppd.guarded_replay_acceptance_v2 import require_acceptance_packet_v2

JsonObject = dict[str, Any]

PACKET_TYPE = "ppd.inactive_release_activation_checklist.v2"
PACKET_VERSION = "v2"
SOURCE_PACKET_KEY = "guarded_agent_replay_acceptance_packet_v2"

DEFAULT_OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/inactive_release_activation_checklist_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_release_activation_checklist_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

MUTATION_FLAGS: tuple[str, ...] = (
    "active_activation_applied",
    "active_release_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_source_mutation",
    "active_surface_mutation",
    "active_contract_mutation",
    "official_action_performed",
)

REQUIRED_ATTESTATIONS: tuple[str, ...] = (
    "no_devhub_opened",
    "no_live_crawl",
    "no_public_source_mutation",
    "no_private_artifact_storage",
    "no_official_action",
    "no_release_state_mutation",
)

_FORBIDDEN_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("live_access_claim", re.compile(r"\b(live devhub accessed|devhub opened|live crawl ran|live run completed)\b", re.IGNORECASE)),
    ("promotion_claim", re.compile(r"\b(promoted to active|activation applied|release state updated|production release complete)\b", re.IGNORECASE)),
    ("private_or_raw_artifact", re.compile(r"\b(auth state|browser state|cookie|credential|downloaded document|har file|private artifact|raw crawl|raw html|raw pdf|session state|storage state|trace file)\b", re.IGNORECASE)),
    ("official_action_language", re.compile(r"\b(application submitted|certified|fee paid|inspection scheduled|official action completed|permit submitted|uploaded to official record)\b", re.IGNORECASE)),
    ("permit_outcome_guarantee", re.compile(r"\b(approval guaranteed|permit will be approved|legally sufficient|legal advice|no legal risk)\b", re.IGNORECASE)),
)


class InactiveReleaseActivationChecklistV2Error(ValueError):
    """Raised when inactive activation checklist v2 validation fails."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid inactive release activation checklist v2: " + "; ".join(self.errors))


def load_json_fixture(path: str | Path) -> JsonObject:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object fixture at {path}")
    return loaded


def build_from_fixture_path(path: str | Path, *, reviewer_owner: str = "inactive-release-activation-reviewer") -> JsonObject:
    return build_inactive_release_activation_checklist_v2(load_json_fixture(path), reviewer_owner=reviewer_owner)


def build_inactive_release_activation_checklist_v2(
    source_packets: Mapping[str, Any],
    *,
    reviewer_owner: str = "inactive-release-activation-reviewer",
) -> JsonObject:
    acceptance_packet = _acceptance_packet(source_packets)
    require_acceptance_packet_v2(acceptance_packet)

    checklist = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "checklist_id": "fixture-first-inactive-release-activation-checklist-v2",
        "fixture_first": True,
        "metadata_only": True,
        "inactive_activation_only": True,
        "consumes": {SOURCE_PACKET_KEY: _packet_ref(acceptance_packet)},
        "ordered_inactive_activation_prerequisites": _ordered_prerequisites(acceptance_packet, reviewer_owner),
        "human_approval_placeholders": _human_approval_placeholders(acceptance_packet, reviewer_owner),
        "rollback_confirmation_placeholders": _rollback_confirmation_placeholders(acceptance_packet, reviewer_owner),
        "validation_transcript_placeholders": _validation_transcript_placeholders(reviewer_owner),
        "no_live_access_attestations": _no_live_access_attestations(reviewer_owner),
        "exact_offline_validation_commands": copy.deepcopy(DEFAULT_OFFLINE_VALIDATION_COMMANDS),
        "mutation_flags": {flag: False for flag in MUTATION_FLAGS},
    }
    assert_valid_inactive_release_activation_checklist_v2(checklist)
    return checklist


def validate_inactive_release_activation_checklist_v2(checklist: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(checklist, Mapping):
        return ["checklist must be an object"]

    if checklist.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if checklist.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be v2")
    for flag in ("fixture_first", "metadata_only", "inactive_activation_only"):
        if checklist.get(flag) is not True:
            errors.append(f"{flag} must be true")

    consumes = checklist.get("consumes")
    if not isinstance(consumes, Mapping) or not _non_empty_text(consumes.get(SOURCE_PACKET_KEY)):
        errors.append(f"consumes.{SOURCE_PACKET_KEY} is required")

    _validate_ordered_prerequisites(checklist.get("ordered_inactive_activation_prerequisites"), errors)
    _validate_placeholders(checklist.get("human_approval_placeholders"), "human_approval_placeholders", "not_approved", errors)
    _validate_placeholders(checklist.get("rollback_confirmation_placeholders"), "rollback_confirmation_placeholders", "not_confirmed", errors)
    _validate_placeholders(checklist.get("validation_transcript_placeholders"), "validation_transcript_placeholders", "not_recorded", errors)
    _validate_attestations(checklist.get("no_live_access_attestations"), errors)

    if checklist.get("exact_offline_validation_commands") != DEFAULT_OFFLINE_VALIDATION_COMMANDS:
        errors.append("exact_offline_validation_commands must match the required offline command inventory exactly")

    mutation_flags = checklist.get("mutation_flags")
    if not isinstance(mutation_flags, Mapping):
        errors.append("mutation_flags must be an object")
    else:
        for flag in MUTATION_FLAGS:
            if mutation_flags.get(flag) is not False:
                errors.append(f"mutation_flags.{flag} must be false")

    _scan_text_values(checklist, errors)
    return errors


def assert_valid_inactive_release_activation_checklist_v2(checklist: Mapping[str, Any]) -> None:
    errors = validate_inactive_release_activation_checklist_v2(checklist)
    if errors:
        raise InactiveReleaseActivationChecklistV2Error(errors)


def _acceptance_packet(source_packets: Mapping[str, Any]) -> JsonObject:
    candidate = source_packets.get(SOURCE_PACKET_KEY) if SOURCE_PACKET_KEY in source_packets else source_packets
    if not isinstance(candidate, dict):
        raise InactiveReleaseActivationChecklistV2Error([f"{SOURCE_PACKET_KEY} must be an object"])
    return copy.deepcopy(candidate)


def _packet_ref(packet: Mapping[str, Any]) -> str:
    for key in ("packet_id", "id", "checklist_id"):
        value = packet.get(key)
        if _non_empty_text(value):
            return str(value)
    return "guarded-agent-replay-acceptance-packet-v2-fixture"


def _ordered_prerequisites(packet: Mapping[str, Any], reviewer_owner: str) -> list[JsonObject]:
    rows = [
        ("guarded-replay-accepted", "Reviewer acceptance rows from guarded replay packet v2 must remain accepted."),
        ("scenario-evidence-traces-reviewed", "Scenario-to-evidence traces must be reviewed before any separate activation decision."),
        ("human-approval-placeholders-open", "Human approval placeholders must remain unapproved in this inactive checklist."),
        ("rollback-confirmation-placeholders-open", "Rollback confirmation placeholders must be available before any separate activation decision."),
        ("validation-transcript-placeholders-open", "Offline validation transcript placeholders must be ready for human-entered results."),
        ("no-live-access-attested", "No-live-access attestations must be present before any separate activation decision."),
    ]
    citations = _citations(packet)
    prerequisites: list[JsonObject] = []
    for index, (slug, summary) in enumerate(rows, start=1):
        prerequisites.append(
            {
                "prerequisite_id": f"inactive-activation-v2-{slug}",
                "order": index,
                "status": "pending_human_review",
                "summary": summary,
                "required_before": "any_active_release_activation",
                "reviewer_owner": reviewer_owner,
                "citations": citations,
            }
        )
    return prerequisites


def _human_approval_placeholders(packet: Mapping[str, Any], reviewer_owner: str) -> list[JsonObject]:
    rows = packet.get("reviewer_acceptance_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        rows = []
    placeholders: list[JsonObject] = []
    for index, row in enumerate(rows, start=1):
        reviewer = row.get("reviewer") if isinstance(row, Mapping) else "reviewer"
        placeholders.append(
            {
                "approval_id": f"inactive-activation-human-approval-{index}",
                "reviewer": str(reviewer or "reviewer"),
                "status": "not_approved",
                "approval_value_placeholder": None,
                "approved_at_placeholder": None,
                "reviewer_owner": reviewer_owner,
                "citations": [f"fixture:reviewer_acceptance_rows:{index}"],
            }
        )
    return placeholders or [
        {
            "approval_id": "inactive-activation-human-approval-1",
            "reviewer": reviewer_owner,
            "status": "not_approved",
            "approval_value_placeholder": None,
            "approved_at_placeholder": None,
            "reviewer_owner": reviewer_owner,
            "citations": ["fixture:reviewer_acceptance_rows"],
        }
    ]


def _rollback_confirmation_placeholders(packet: Mapping[str, Any], reviewer_owner: str) -> list[JsonObject]:
    citations = _citations(packet)
    return [
        {
            "rollback_confirmation_id": "inactive-activation-v2-discard-checklist",
            "status": "not_confirmed",
            "confirmation_value_placeholder": None,
            "rollback_scope": "Discard this inactive checklist fixture; no active release state exists to roll back from this artifact.",
            "reviewer_owner": reviewer_owner,
            "citations": citations,
        },
        {
            "rollback_confirmation_id": "inactive-activation-v2-rerun-offline-validation",
            "status": "not_confirmed",
            "confirmation_value_placeholder": None,
            "rollback_scope": "Rerun exact offline validation commands before any separate activation review restarts.",
            "reviewer_owner": reviewer_owner,
            "citations": ["fixture:exact_offline_validation_commands"],
        },
    ]


def _validation_transcript_placeholders(reviewer_owner: str) -> list[JsonObject]:
    return [
        {
            "transcript_id": f"inactive-activation-validation-transcript-{index}",
            "status": "not_recorded",
            "command": command,
            "observed_exit_code_placeholder": None,
            "transcript_summary_placeholder": None,
            "reviewer_owner": reviewer_owner,
            "citations": ["fixture:exact_offline_validation_commands"],
        }
        for index, command in enumerate(DEFAULT_OFFLINE_VALIDATION_COMMANDS, start=1)
    ]


def _no_live_access_attestations(reviewer_owner: str) -> list[JsonObject]:
    return [
        {
            "attestation_id": f"inactive-activation-v2-{name.replace('_', '-')}",
            "attestation": name,
            "attested": True,
            "scope": "inactive fixture checklist only",
            "reviewer_owner": reviewer_owner,
            "citations": ["fixture:guarded_agent_replay_acceptance_packet_v2"],
        }
        for name in REQUIRED_ATTESTATIONS
    ]


def _validate_ordered_prerequisites(value: Any, errors: list[str]) -> None:
    rows = _mapping_rows(value)
    if not rows:
        errors.append("ordered_inactive_activation_prerequisites must contain rows")
        return
    for index, row in enumerate(rows):
        prefix = f"ordered_inactive_activation_prerequisites[{index}]"
        if row.get("order") != index + 1:
            errors.append(f"{prefix}.order must be {index + 1}")
        for key in ("prerequisite_id", "summary", "required_before", "reviewer_owner"):
            if not _non_empty_text(row.get(key)):
                errors.append(f"{prefix}.{key} is required")
        if row.get("status") != "pending_human_review":
            errors.append(f"{prefix}.status must be pending_human_review")
        if not _sequence(row.get("citations")):
            errors.append(f"{prefix}.citations is required")


def _validate_placeholders(value: Any, field: str, required_status: str, errors: list[str]) -> None:
    rows = _mapping_rows(value)
    if not rows:
        errors.append(f"{field} must contain rows")
        return
    for index, row in enumerate(rows):
        prefix = f"{field}[{index}]"
        if row.get("status") != required_status:
            errors.append(f"{prefix}.status must be {required_status}")
        if not _non_empty_text(row.get("reviewer_owner")):
            errors.append(f"{prefix}.reviewer_owner is required")
        if not _sequence(row.get("citations")):
            errors.append(f"{prefix}.citations is required")


def _validate_attestations(value: Any, errors: list[str]) -> None:
    rows = _mapping_rows(value)
    if len(rows) != len(REQUIRED_ATTESTATIONS):
        errors.append("no_live_access_attestations must contain one row per required attestation")
    seen = {str(row.get("attestation")) for row in rows}
    for required in REQUIRED_ATTESTATIONS:
        if required not in seen:
            errors.append(f"missing no-live-access attestation: {required}")
    for index, row in enumerate(rows):
        prefix = f"no_live_access_attestations[{index}]"
        if row.get("attested") is not True:
            errors.append(f"{prefix}.attested must be true")
        if not _non_empty_text(row.get("reviewer_owner")):
            errors.append(f"{prefix}.reviewer_owner is required")
        if not _sequence(row.get("citations")):
            errors.append(f"{prefix}.citations is required")


def _scan_text_values(value: Any, errors: list[str]) -> None:
    if isinstance(value, str):
        for code, pattern in _FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(value):
                errors.append(f"{code}: {value}")
        return
    if isinstance(value, Mapping):
        for item in value.values():
            _scan_text_values(item, errors)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            _scan_text_values(item, errors)


def _citations(packet: Mapping[str, Any]) -> list[str]:
    citations = ["fixture:guarded_agent_replay_acceptance_packet_v2"]
    if _sequence(packet.get("scenario_to_evidence_traces")):
        citations.append("fixture:scenario_to_evidence_traces")
    if _sequence(packet.get("reviewer_acceptance_rows")):
        citations.append("fixture:reviewer_acceptance_rows")
    return citations


def _mapping_rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, str):
        return ()
    if isinstance(value, Sequence):
        return value
    return ()


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
