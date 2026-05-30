"""Fixture-first live dry-run acceptance review packet v2.

This module consumes committed PP&D fixture packets only. It reviews a live
-dry-run post-run triage packet v2, a public recrawl dry-run evidence envelope
v2, and an attended DevHub read-only evidence envelope v2 into cited accepted,
deferred, and rejected observation rows. It does not repeat a live run, open or
inspect DevHub, read auth state, create browser artifacts, perform official
actions, or mutate release state.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any, Mapping, Sequence

from ppd.live_dry_run_post_run_triage_packet_v2 import (
    require_valid_live_dry_run_post_run_triage_packet_v2,
)


PACKET_TYPE = "live-dry-run-acceptance-review-packet-v2"
PACKET_VERSION = "v2"
MODE = "fixture_first_live_dry_run_acceptance_review_only"

REQUIRED_ATTESTATIONS = (
    "no_live_repeat",
    "no_auth_state",
    "no_browser_artifact",
    "no_official_action",
    "no_release_state_mutation",
)

REQUIRED_DECISIONS = ("accepted", "deferred", "rejected")

DEFAULT_OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/acceptance/live_dry_run_acceptance_review_packet_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_live_dry_run_acceptance_review_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_PRIVATE_OR_AUTH_RE = re.compile(
    r"\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|"
    r"(?:password|credential|secret|token|cookie|auth state|session state|storage state)\s*[:=]|"
    r"permit\s*(?:number|#|no\.)\s*[:#]?\s*[A-Z0-9-]{4,})\b",
    re.IGNORECASE,
)
_BROWSER_ARTIFACT_RE = re.compile(
    r"\b(screenshot|trace\.zip|playwright trace|browser trace|har file|\.har\b|auth_state\.json|storage_state\.json)\b|"
    r"(/home/|/Users/|C:\\Users\\|file://)",
    re.IGNORECASE,
)
_LIVE_REPEAT_RE = re.compile(
    r"\b(repeated|reran|ran|opened|launched|navigated|crawled|downloaded|captured)\b.{0,80}\b(live|DevHub|browser|Playwright|crawl|processor)\b",
    re.IGNORECASE,
)
_OFFICIAL_ACTION_RE = re.compile(
    r"\b(submitted|uploaded|paid|scheduled|cancelled|canceled|certified|purchased|withdrew|reactivated)\b|"
    r"\b(click|press|select)\s+(submit|pay|upload|schedule|cancel|certify)\b",
    re.IGNORECASE,
)
_MUTATION_KEYS = frozenset(
    {
        "release_state_mutation",
        "active_release_state_mutation",
        "mutates_release_state",
        "release_state_mutated",
        "source_registry_mutation",
        "surface_registry_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "monitoring_mutation",
        "agent_state_mutation",
    }
)


@dataclass(frozen=True)
class AcceptanceReviewValidationResult:
    valid: bool
    errors: tuple[str, ...]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(str(path) + " must contain a JSON object")
    return data


def build_from_fixture_paths(
    live_dry_run_post_run_triage_packet_path: Path,
    public_recrawl_dry_run_evidence_envelope_path: Path,
    attended_devhub_read_only_evidence_envelope_path: Path,
) -> dict[str, Any]:
    return build_live_dry_run_acceptance_review_packet_v2(
        load_json(live_dry_run_post_run_triage_packet_path),
        load_json(public_recrawl_dry_run_evidence_envelope_path),
        load_json(attended_devhub_read_only_evidence_envelope_path),
    )


def build_live_dry_run_acceptance_review_packet_v2(
    live_dry_run_post_run_triage_packet_v2: Mapping[str, Any],
    public_recrawl_dry_run_evidence_envelope_v2: Mapping[str, Any],
    attended_devhub_read_only_evidence_envelope_v2: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic acceptance review packet from fixture packets."""

    require_valid_live_dry_run_post_run_triage_packet_v2(live_dry_run_post_run_triage_packet_v2)
    _validate_public_envelope(public_recrawl_dry_run_evidence_envelope_v2)
    _validate_devhub_envelope(attended_devhub_read_only_evidence_envelope_v2)

    accepted_rows = _accepted_rows(
        live_dry_run_post_run_triage_packet_v2,
        public_recrawl_dry_run_evidence_envelope_v2,
        attended_devhub_read_only_evidence_envelope_v2,
    )
    deferred_rows = _deferred_rows(live_dry_run_post_run_triage_packet_v2)
    rejected_rows = _rejected_rows(
        live_dry_run_post_run_triage_packet_v2,
        public_recrawl_dry_run_evidence_envelope_v2,
        attended_devhub_read_only_evidence_envelope_v2,
    )

    packet = {
        "packet_type": PACKET_TYPE,
        "version": PACKET_VERSION,
        "packet_id": "fixture-first-live-dry-run-acceptance-review-packet-v2-20260529",
        "mode": MODE,
        "fixture_first": True,
        "consumes": {
            "live_dry_run_post_run_triage_packet_v2": _packet_ref(live_dry_run_post_run_triage_packet_v2, "packet_id"),
            "public_recrawl_dry_run_evidence_envelope_v2": _packet_ref(public_recrawl_dry_run_evidence_envelope_v2, "envelope_id"),
            "attended_devhub_read_only_evidence_envelope_v2": _packet_ref(attended_devhub_read_only_evidence_envelope_v2, "envelope_id"),
        },
        "observation_rows": {
            "accepted": accepted_rows,
            "deferred": deferred_rows,
            "rejected": rejected_rows,
        },
        "reviewer_owner_fields": {
            "primary_reviewer_owner": "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER",
            "public_recrawl_reviewer_owner": "TBD_PP_D_PUBLIC_RECRAWL_REVIEW_OWNER",
            "devhub_readonly_reviewer_owner": "TBD_PP_D_DEVHUB_READONLY_REVIEW_OWNER",
            "release_state_owner": "TBD_PP_D_RELEASE_STATE_OWNER",
            "owner_assignment_status": "placeholder_required_before_promotion",
            "citations": [
                "live_dry_run_post_run_triage_packet_v2.reviewer_owner_fields",
                "public_recrawl_dry_run_evidence_envelope_v2.attestations",
                "attended_devhub_read_only_evidence_envelope_v2.observation_slots.attestations",
            ],
        },
        "follow_up_task_references": _follow_up_task_references(),
        "offline_validation_commands": [list(command) for command in DEFAULT_OFFLINE_VALIDATION_COMMANDS],
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
        "side_effects": {
            "live_repeat_performed": False,
            "auth_state_created_or_read": False,
            "browser_artifact_created_or_read": False,
            "official_action_performed": False,
            "release_state_mutated": False,
        },
        "source_packet_redacted_snapshot": {
            "live_dry_run_post_run_triage_packet_v2": deepcopy(dict(live_dry_run_post_run_triage_packet_v2)),
            "public_recrawl_dry_run_evidence_envelope_v2": deepcopy(dict(public_recrawl_dry_run_evidence_envelope_v2)),
            "attended_devhub_read_only_evidence_envelope_v2": deepcopy(dict(attended_devhub_read_only_evidence_envelope_v2)),
        },
        "validation_status": "fixture_acceptance_review_packet_pending_reviewer_owner_signoff",
    }
    require_valid_live_dry_run_acceptance_review_packet_v2(packet)
    return packet


def validate_live_dry_run_acceptance_review_packet_v2(packet: Mapping[str, Any]) -> AcceptanceReviewValidationResult:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be " + PACKET_TYPE)
    if packet.get("version") != PACKET_VERSION:
        errors.append("version must be v2")
    if packet.get("mode") != MODE:
        errors.append("mode must be " + MODE)
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")

    consumes = _mapping(packet.get("consumes"))
    for key in (
        "live_dry_run_post_run_triage_packet_v2",
        "public_recrawl_dry_run_evidence_envelope_v2",
        "attended_devhub_read_only_evidence_envelope_v2",
    ):
        if not _text(consumes.get(key)):
            errors.append("consumes." + key + " is required")

    rows = _mapping(packet.get("observation_rows"))
    for decision in REQUIRED_DECISIONS:
        section_rows = _sequence(rows.get(decision))
        if not section_rows:
            errors.append("observation_rows." + decision + " must be non-empty")
        for index, row_value in enumerate(section_rows):
            prefix = "observation_rows." + decision + "[" + str(index) + "]"
            if not isinstance(row_value, Mapping):
                errors.append(prefix + " must be an object")
                continue
            if row_value.get("decision") != decision:
                errors.append(prefix + ".decision must be " + decision)
            for field_name in (
                "row_id",
                "observation_summary",
                "reviewer_owner",
                "follow_up_task_ref",
                "rationale",
            ):
                if not _text(row_value.get(field_name)):
                    errors.append(prefix + "." + field_name + " is required")
            if not _text_list(row_value.get("citations")):
                errors.append(prefix + ".citations must be non-empty")
            if not _text_list(row_value.get("source_packet_refs")):
                errors.append(prefix + ".source_packet_refs must be non-empty")

    owners = _mapping(packet.get("reviewer_owner_fields"))
    for key in (
        "primary_reviewer_owner",
        "public_recrawl_reviewer_owner",
        "devhub_readonly_reviewer_owner",
        "release_state_owner",
        "owner_assignment_status",
    ):
        if not _text(owners.get(key)):
            errors.append("reviewer_owner_fields." + key + " is required")
    if not _text_list(owners.get("citations")):
        errors.append("reviewer_owner_fields.citations must be non-empty")

    if not _sequence(packet.get("follow_up_task_references")):
        errors.append("follow_up_task_references must be non-empty")
    for index, task in enumerate(_sequence(packet.get("follow_up_task_references"))):
        if not isinstance(task, Mapping):
            errors.append("follow_up_task_references[" + str(index) + "] must be an object")
            continue
        for field_name in ("task_ref", "owner", "status", "description", "citations"):
            if field_name == "citations":
                if not _text_list(task.get(field_name)):
                    errors.append("follow_up_task_references[" + str(index) + "].citations must be non-empty")
            elif not _text(task.get(field_name)):
                errors.append("follow_up_task_references[" + str(index) + "]." + field_name + " is required")

    if not _command_sequence(packet.get("offline_validation_commands")):
        errors.append("offline_validation_commands must include safe offline commands")

    attestations = _mapping(packet.get("attestations"))
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            errors.append("attestations." + key + " must be true")

    side_effects = _mapping(packet.get("side_effects"))
    for key in (
        "live_repeat_performed",
        "auth_state_created_or_read",
        "browser_artifact_created_or_read",
        "official_action_performed",
        "release_state_mutated",
    ):
        if side_effects.get(key) is not False:
            errors.append("side_effects." + key + " must be false")

    _scan_unsafe(packet, "$", errors)
    return AcceptanceReviewValidationResult(valid=not errors, errors=tuple(dict.fromkeys(errors)))


def require_valid_live_dry_run_acceptance_review_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_live_dry_run_acceptance_review_packet_v2(packet)
    if not result.valid:
        raise ValueError("invalid live dry-run acceptance review packet v2: " + "; ".join(result.errors))


def _accepted_rows(triage: Mapping[str, Any], public_envelope: Mapping[str, Any], devhub_envelope: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in _sequence(triage.get("observation_decisions")):
        if isinstance(decision, Mapping) and decision.get("decision") == "accepted":
            decision_id = _text(decision.get("decision_id"), "accepted-observation")
            rows.append(
                _row(
                    "accept-" + decision_id,
                    "accepted",
                    _text(decision.get("summary")),
                    "Accept the cited observation for offline reviewer acceptance review only.",
                    "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER",
                    "follow-up-confirm-accepted-observations",
                    _text_list(decision.get("citations")),
                    ["live_dry_run_post_run_triage_packet_v2.observation_decisions"],
                )
            )
    rows.append(
        _row(
            "accept-public-recrawl-evidence-envelope",
            "accepted",
            "Accept the public recrawl dry-run evidence envelope as metadata-only fixture evidence.",
            "Envelope attestations and side effects show no live crawl, processor invocation, raw body persistence, download, or source registry mutation.",
            "TBD_PP_D_PUBLIC_RECRAWL_REVIEW_OWNER",
            "follow-up-public-recrawl-envelope-owner-signoff",
            _citations(public_envelope, "public_recrawl_dry_run_evidence_envelope_v2.attestations"),
            ["public_recrawl_dry_run_evidence_envelope_v2"],
        )
    )
    rows.append(
        _row(
            "accept-devhub-readonly-evidence-envelope",
            "accepted",
            "Accept the attended DevHub read-only evidence envelope as synthetic read-only fixture evidence.",
            "Envelope observation slots are cited and limited to read-only labels, manual handoff notes, redaction outcomes, abort conditions, validation commands, and attestations.",
            "TBD_PP_D_DEVHUB_READONLY_REVIEW_OWNER",
            "follow-up-devhub-readonly-envelope-owner-signoff",
            _citations(devhub_envelope, "attended_devhub_read_only_evidence_envelope_v2.observation_slots"),
            ["attended_devhub_read_only_evidence_envelope_v2"],
        )
    )
    return rows


def _deferred_rows(triage: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in _sequence(triage.get("observation_decisions")):
        if isinstance(decision, Mapping) and decision.get("decision") in {"deferred", "escalated"}:
            decision_id = _text(decision.get("decision_id"), "deferred-observation")
            rows.append(
                _row(
                    "defer-" + decision_id,
                    "deferred",
                    _text(decision.get("summary")),
                    "Keep the observation deferred until reviewer-owner signoff and a separate authorization packet exist.",
                    "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER",
                    "follow-up-resolve-deferred-live-dry-run-observations",
                    _text_list(decision.get("citations")),
                    ["live_dry_run_post_run_triage_packet_v2.observation_decisions"],
                )
            )
    if not rows:
        rows.append(
            _row(
                "defer-reviewer-owner-signoff",
                "deferred",
                "Defer promotion until reviewer-owner fields are assigned outside this fixture packet.",
                "The acceptance packet is review-only and requires owner signoff before downstream promotion.",
                "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER",
                "follow-up-assign-acceptance-review-owners",
                ["live_dry_run_post_run_triage_packet_v2.reviewer_owner_fields"],
                ["live_dry_run_post_run_triage_packet_v2"],
            )
        )
    return rows


def _rejected_rows(triage: Mapping[str, Any], public_envelope: Mapping[str, Any], devhub_envelope: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        _row(
            "reject-live-repeat-from-acceptance-review",
            "rejected",
            "Reject any live repeat, live crawl, processor invocation, or authenticated browser replay from this acceptance review packet.",
            "The source packets authorize fixture-only post-run review, not new live execution.",
            "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER",
            "follow-up-create-separate-live-authorization-before-any-repeat",
            _citations(triage, "live_dry_run_post_run_triage_packet_v2.attestations"),
            ["live_dry_run_post_run_triage_packet_v2"],
        ),
        _row(
            "reject-auth-state-and-browser-artifacts",
            "rejected",
            "Reject any auth state, browser profile, screenshot, trace, HAR, raw authenticated text, or downloaded document artifact.",
            "Public and DevHub evidence envelopes attest to metadata-only and synthetic read-only evidence boundaries.",
            "TBD_PP_D_DEVHUB_READONLY_REVIEW_OWNER",
            "follow-up-preserve-redaction-boundary-in-review-notes",
            _citations(public_envelope, "public_recrawl_dry_run_evidence_envelope_v2.side_effects")
            + _citations(devhub_envelope, "attended_devhub_read_only_evidence_envelope_v2.observation_slots.attestations"),
            [
                "public_recrawl_dry_run_evidence_envelope_v2",
                "attended_devhub_read_only_evidence_envelope_v2",
            ],
        ),
        _row(
            "reject-official-action-and-release-mutation",
            "rejected",
            "Reject any submission, upload, certification, payment, scheduling, cancellation, official action, or release-state mutation.",
            "Acceptance review rows are cited observations only and do not promote, publish, or mutate release state.",
            "TBD_PP_D_RELEASE_STATE_OWNER",
            "follow-up-confirm-no-release-state-mutation-before-promotion",
            _citations(triage, "live_dry_run_post_run_triage_packet_v2.side_effects"),
            ["live_dry_run_post_run_triage_packet_v2"],
        ),
    ]


def _row(
    row_id: str,
    decision: str,
    observation_summary: str,
    rationale: str,
    reviewer_owner: str,
    follow_up_task_ref: str,
    citations: Sequence[str],
    source_packet_refs: Sequence[str],
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "decision": decision,
        "observation_summary": observation_summary,
        "rationale": rationale,
        "reviewer_owner": reviewer_owner,
        "follow_up_task_ref": follow_up_task_ref,
        "citations": list(citations),
        "source_packet_refs": list(source_packet_refs),
    }


def _follow_up_task_references() -> list[dict[str, Any]]:
    return [
        {
            "task_ref": "follow-up-confirm-accepted-observations",
            "owner": "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER",
            "status": "pending_reviewer_owner_assignment",
            "description": "Confirm accepted observation rows remain fixture-only and cited before downstream promotion.",
            "citations": ["live_dry_run_post_run_triage_packet_v2.observation_decisions"],
        },
        {
            "task_ref": "follow-up-resolve-deferred-live-dry-run-observations",
            "owner": "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER",
            "status": "pending_separate_authorization_packet",
            "description": "Resolve deferred and escalated observations without repeating live activity from this packet.",
            "citations": ["live_dry_run_post_run_triage_packet_v2.observation_decisions"],
        },
        {
            "task_ref": "follow-up-create-separate-live-authorization-before-any-repeat",
            "owner": "TBD_PP_D_RELEASE_STATE_OWNER",
            "status": "blocked_in_this_packet",
            "description": "Require a separate authorization packet before any future live repeat, browser run, or public recrawl.",
            "citations": ["live_dry_run_post_run_triage_packet_v2.attestations"],
        },
    ]


def _validate_public_envelope(envelope: Mapping[str, Any]) -> None:
    if envelope.get("packet_type") != "public-recrawl-dry-run-evidence-envelope":
        raise ValueError("public recrawl evidence envelope packet_type mismatch")
    if envelope.get("version") != "v2":
        raise ValueError("public recrawl evidence envelope version must be v2")
    if envelope.get("fixture_first") is not True:
        raise ValueError("public recrawl evidence envelope must be fixture_first")
    if envelope.get("metadata_only") is not True:
        raise ValueError("public recrawl evidence envelope must be metadata_only")
    attestations = _mapping(envelope.get("attestations"))
    for key in ("no_live_crawl", "no_processor", "no_raw_body", "no_download", "no_source_registry_mutation"):
        if attestations.get(key) is not True:
            raise ValueError("public recrawl evidence envelope missing attestation: " + key)
    if not _sequence(envelope.get("observation_slots")):
        raise ValueError("public recrawl evidence envelope observation_slots required")


def _validate_devhub_envelope(envelope: Mapping[str, Any]) -> None:
    if envelope.get("version") != "devhub-readonly-evidence-envelope-v2":
        raise ValueError("DevHub read-only evidence envelope version mismatch")
    if envelope.get("mode") != "fixture-first-attended-read-only":
        raise ValueError("DevHub read-only evidence envelope mode mismatch")
    slots = _mapping(envelope.get("observation_slots"))
    attestations_slot = _mapping(slots.get("attestations"))
    attestations = _mapping(attestations_slot.get("value"))
    for key in ("no_live_devhub", "no_auth_state", "no_screenshot", "no_trace", "no_har", "no_surface_registry_mutation"):
        if attestations.get(key) is not True:
            raise ValueError("DevHub read-only evidence envelope missing attestation: " + key)
    if not slots:
        raise ValueError("DevHub read-only evidence envelope observation_slots required")


def _packet_ref(packet: Mapping[str, Any], preferred_key: str) -> str:
    return _text(packet.get(preferred_key) or packet.get("packet_id") or packet.get("plan_id") or packet.get("version"), "unknown-fixture-packet")


def _citations(packet: Mapping[str, Any], fallback: str) -> list[str]:
    citations = _text_list(packet.get("citations"))
    if citations:
        return citations
    return [fallback]


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value
    return fallback


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item)
    return result


def _command_sequence(value: Any) -> bool:
    commands = _sequence(value)
    if not commands:
        return False
    for command in commands:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part for part in command):
            return False
        if command[0] != "python3":
            return False
    return True


def _scan_unsafe(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + "." + key_text
            if key_text in _MUTATION_KEYS and child is True:
                errors.append(child_path + " must not claim mutation")
            _scan_unsafe(child, child_path, errors)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan_unsafe(child, path + "[" + str(index) + "]", errors)
        return
    if isinstance(value, str):
        if _PRIVATE_OR_AUTH_RE.search(value):
            errors.append(path + " contains private, credential, session, or authenticated values")
        if _BROWSER_ARTIFACT_RE.search(value):
            errors.append(path + " contains browser artifact, auth state, trace, HAR, screenshot, or local path references")
        if _LIVE_REPEAT_RE.search(value):
            errors.append(path + " claims live repeat, live crawl, browser, or processor execution")
        if _OFFICIAL_ACTION_RE.search(value):
            errors.append(path + " claims official action language")


__all__ = [
    "AcceptanceReviewValidationResult",
    "DEFAULT_OFFLINE_VALIDATION_COMMANDS",
    "PACKET_TYPE",
    "PACKET_VERSION",
    "REQUIRED_ATTESTATIONS",
    "build_from_fixture_paths",
    "build_live_dry_run_acceptance_review_packet_v2",
    "require_valid_live_dry_run_acceptance_review_packet_v2",
    "validate_live_dry_run_acceptance_review_packet_v2",
]
