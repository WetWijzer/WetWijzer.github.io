"""Fixture-first inactive activation checklist v4.

This module consumes only post-decision smoke replay v4 fixtures and assembles
reviewer-controlled activation checklist rows. It never activates guardrails,
opens DevHub, reads private documents, uploads, submits, certifies, pays,
schedules, or makes legal/permitting guarantees.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from ppd.agent_readiness.post_decision_smoke_replay_v4 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    PACKET_TYPE as POST_DECISION_PACKET_TYPE,
    assert_valid_post_decision_smoke_replay_v4,
)

PACKET_TYPE = "ppd.inactive_activation_checklist.v4"
PACKET_VERSION = "v4"
MODE = "fixture_first_inactive_activation_checklist_v4"

REQUIRED_BOUNDARIES = {
    "fixture_first": True,
    "post_decision_smoke_replay_v4_fixtures_only": True,
    "guardrail_activation_enabled": False,
    "devhub_opened": False,
    "private_documents_read": False,
    "upload_enabled": False,
    "submission_enabled": False,
    "certification_enabled": False,
    "payment_enabled": False,
    "scheduling_enabled": False,
    "legal_or_permitting_guarantee_enabled": False,
}

REQUIRED_ATTESTATIONS = {
    "guardrails_activated": False,
    "devhub_opened": False,
    "private_documents_read": False,
    "uploads_performed": False,
    "submissions_performed": False,
    "certifications_performed": False,
    "payments_performed": False,
    "scheduling_performed": False,
    "legal_or_permitting_guarantees_made": False,
}

REQUIRED_LIST_FIELDS = (
    "reviewer_controlled_activation_prerequisites",
    "required_signoff_placeholders",
    "source_freshness_hold_clearance_criteria",
    "rollback_checkpoint_rows",
    "post_activation_smoke_checks",
    "agent_notification_notes",
)

_FORBIDDEN_TRUE_FLAGS = frozenset(
    {
        "active_activation",
        "active_guardrail_activation",
        "active_guardrail_mutation",
        "active_mutation",
        "active_release_state_mutation",
        "certification_enabled",
        "certifications_performed",
        "devhub_opened",
        "guardrail_activation_enabled",
        "guardrails_activated",
        "legal_or_permitting_guarantee_enabled",
        "legal_or_permitting_guarantees_made",
        "payment_enabled",
        "payments_performed",
        "private_documents_read",
        "scheduling_enabled",
        "scheduling_performed",
        "submission_enabled",
        "submissions_performed",
        "upload_enabled",
        "uploads_performed",
    }
)

_SENSITIVE_KEY_RE = re.compile(
    r"(^|_)(auth|browser_state|cookie|credential|download|har|password|private|raw|screenshot|session|session_state|storage_state|token|trace)(_|$)",
    re.IGNORECASE,
)
_FORBIDDEN_TEXT_RE = re.compile(
    r"(activation complete|activated guardrails|active guardrails|approval guaranteed|guaranteed approval|guaranteed issuance|legal advice|legal guarantee|permit will be approved|permit will be issued|official action completed|submitted permit|uploaded correction|paid fee|scheduled inspection|certified acknowledgement|live devhub|session state|storage state|trace file|raw crawl|raw pdf)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InactiveActivationChecklistV4Result:
    valid: bool
    problems: tuple[str, ...]


class InactiveActivationChecklistV4Error(ValueError):
    def __init__(self, problems: Sequence[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid inactive activation checklist v4: " + "; ".join(self.problems))


def load_inactive_activation_checklist_v4_fixture(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise ValueError("inactive activation checklist v4 source fixture must be an object")
    return build_inactive_activation_checklist_v4(loaded)


def assert_valid_inactive_activation_checklist_v4(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_activation_checklist_v4(packet)
    if not result.valid:
        raise InactiveActivationChecklistV4Error(result.problems)


def build_inactive_activation_checklist_v4(source_fixture: Mapping[str, Any]) -> dict[str, Any]:
    replays = _mapping_sequence(source_fixture.get("post_decision_smoke_replay_v4_fixtures"))
    if not replays:
        raise ValueError("post_decision_smoke_replay_v4_fixtures must be non-empty")
    for replay in replays:
        assert_valid_post_decision_smoke_replay_v4(replay)

    replay_refs = _string_list(source_fixture.get("post_decision_smoke_replay_v4_refs"))
    if not replay_refs:
        replay_refs = [_text(replay.get("packet_id")) for replay in replays if _text(replay.get("packet_id"))]

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": "inactive-activation-checklist-v4-fixture",
        "mode": MODE,
        "consumes_only": {"post_decision_smoke_replay_v4_fixtures": True},
        "required_source_references": {"post_decision_smoke_replay_v4_refs": replay_refs},
        "boundaries": dict(REQUIRED_BOUNDARIES),
        "reviewer_controlled_activation_prerequisites": _activation_prerequisites(replays),
        "required_signoff_placeholders": _signoff_placeholders(replays),
        "source_freshness_hold_clearance_criteria": _freshness_clearance_criteria(replays),
        "rollback_checkpoint_rows": _rollback_checkpoint_rows(replays),
        "post_activation_smoke_checks": _post_activation_smoke_checks(replays),
        "agent_notification_notes": _agent_notification_notes(replays),
        "attestations": dict(REQUIRED_ATTESTATIONS),
        "exact_offline_validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
        "validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
    }
    assert_valid_inactive_activation_checklist_v4(packet)
    return packet


def validate_inactive_activation_checklist_v4(packet: Mapping[str, Any]) -> InactiveActivationChecklistV4Result:
    if not isinstance(packet, Mapping):
        return InactiveActivationChecklistV4Result(False, ("packet must be an object",))
    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")
    if packet.get("mode") != MODE:
        problems.append(f"mode must be {MODE}")
    if packet.get("consumes_only") != {"post_decision_smoke_replay_v4_fixtures": True}:
        problems.append("consumes_only must allow only post-decision smoke replay v4 fixtures")
    refs = packet.get("required_source_references") if isinstance(packet.get("required_source_references"), Mapping) else {}
    if not _string_list(refs.get("post_decision_smoke_replay_v4_refs")):
        problems.append("required_source_references.post_decision_smoke_replay_v4_refs must be non-empty")
    if packet.get("boundaries") != REQUIRED_BOUNDARIES:
        problems.append("boundaries must exactly preserve fixture-only inactive activation limits")
    if packet.get("attestations") != REQUIRED_ATTESTATIONS:
        problems.append("attestations must exactly deny guardrail activation, DevHub access, private document reads, official actions, and guarantees")
    if packet.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("exact_offline_validation_commands must contain only the daemon self-test command")
    if packet.get("validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("validation_commands must contain only the daemon self-test command")
    for field in REQUIRED_LIST_FIELDS:
        if not _mapping_sequence(packet.get(field)):
            problems.append(f"{field} must be a non-empty list")
    _validate_prerequisites(packet.get("reviewer_controlled_activation_prerequisites"), problems)
    _validate_signoffs(packet.get("required_signoff_placeholders"), problems)
    _validate_freshness(packet.get("source_freshness_hold_clearance_criteria"), problems)
    _validate_rollback(packet.get("rollback_checkpoint_rows"), problems)
    _validate_smoke(packet.get("post_activation_smoke_checks"), problems)
    _validate_notes(packet.get("agent_notification_notes"), problems)
    _scan_for_forbidden_payload(packet, "$", problems)
    return InactiveActivationChecklistV4Result(not problems, tuple(dict.fromkeys(problems)))


def _activation_prerequisites(replays: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        _prereq("confirm-post-decision-outcome", "Reviewer confirms each post-decision smoke replay outcome before any later activation task."),
        _prereq("resolve-unresolved-holds", "Reviewer resolves or explicitly carries forward every unresolved hold propagated by the replay."),
        _prereq("assign-required-signoffs", "Reviewer assigns named humans for all signoff placeholders outside this fixture."),
        _prereq("clear-source-freshness-holds", "Reviewer clears source freshness hold criteria using public-source review outside this inactive packet."),
        _prereq("approve-rollback-checkpoints", "Reviewer accepts rollback checkpoint rows before any later activation task."),
    ]
    for replay in replays:
        outcome = replay.get("release_outcome_handling") if isinstance(replay.get("release_outcome_handling"), Mapping) else {}
        if outcome.get("go_no_go_outcome") == "NO_GO":
            rows.append(_prereq("no-go-replay-remains-blocking", "NO_GO replay outcome must be reconciled by reviewers before any later activation task."))
    return rows


def _prereq(prerequisite_id: str, description: str) -> dict[str, Any]:
    return {
        "prerequisite_id": prerequisite_id,
        "description": description,
        "control_owner_placeholder": "TBD_RELEASE_REVIEWER",
        "status": "pending_reviewer_control",
        "required_before": "any_guardrail_activation",
        "activation_allowed": False,
    }


def _signoff_placeholders(replays: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "signoff_id": "release-reviewer-signoff",
            "source_replay_packet_ids": _packet_ids(replays),
            "required_role_placeholder": "TBD_RELEASE_REVIEWER",
            "signoff_status": "placeholder_pending_manual_signoff",
            "signed_by": None,
            "required_before_activation": True,
            "activation_allowed": False,
        },
        {
            "signoff_id": "source-freshness-reviewer-signoff",
            "source_replay_packet_ids": _packet_ids(replays),
            "required_role_placeholder": "TBD_SOURCE_REVIEWER",
            "signoff_status": "placeholder_pending_manual_signoff",
            "signed_by": None,
            "required_before_activation": True,
            "activation_allowed": False,
        },
    ]


def _freshness_clearance_criteria(replays: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    caveats: list[str] = []
    for replay in replays:
        for row in _mapping_sequence(replay.get("source_freshness_caveat_display")):
            caveats.append(_text(row.get("display_text")))
    if not caveats:
        caveats = ["No source freshness caveat was available in the fixture; reviewer clearance remains required."]
    rows = []
    for caveat in caveats:
        rows.append(
            {
                "criterion_id": "source-freshness-clearance-" + hashlib.sha256(caveat.encode("utf-8")).hexdigest()[:12],
                "caveat_text": caveat,
                "clearance_required": True,
                "clearance_status": "pending_reviewer_clearance",
                "clearance_evidence_placeholder": "TBD_PUBLIC_SOURCE_FRESHNESS_REVIEW",
                "activation_allowed": False,
            }
        )
    return rows


def _rollback_checkpoint_rows(replays: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for replay in replays:
        for row in _mapping_sequence(replay.get("rollback_owner_placeholders")):
            checkpoint_id = "rollback-checkpoint-" + hashlib.sha256(_text(row.get("candidate_or_placeholder_id")).encode("utf-8")).hexdigest()[:12]
            rows.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "candidate_or_placeholder_id": _text(row.get("candidate_or_placeholder_id")),
                    "rollback_owner_placeholder": _text(row.get("rollback_owner_placeholder"), "TBD_ROLLBACK_OWNER"),
                    "rollback_decision_placeholder": _text(row.get("rollback_decision_placeholder"), "TBD_AFTER_REVIEW"),
                    "checkpoint_status": "pending_reviewer_confirmation",
                    "active_state_changed": False,
                    "activation_allowed": False,
                }
            )
    return rows


def _post_activation_smoke_checks(replays: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "post-activation-guardrail-lookup-health",
            "source_replay_packet_ids": _packet_ids(replays),
            "planned_check": "After a separate approved activation task, verify guardrail lookup health from committed public fixtures only.",
            "check_status": "placeholder_pending_future_activation",
            "requires_separate_activation_authorization": True,
            "activation_allowed_by_this_packet": False,
        },
        {
            "check_id": "post-activation-agent-notification-visibility",
            "source_replay_packet_ids": _packet_ids(replays),
            "planned_check": "After a separate approved activation task, verify agents can see source freshness caveats and manual handoff reminders.",
            "check_status": "placeholder_pending_future_activation",
            "requires_separate_activation_authorization": True,
            "activation_allowed_by_this_packet": False,
        },
    ]


def _agent_notification_notes(replays: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "note_id": "notify-agents-activation-not-approved",
            "source_replay_packet_ids": _packet_ids(replays),
            "notification_text": "Inactive checklist prepared for reviewer control only; no guardrails are active from this packet.",
            "notification_status": "placeholder_pending_manual_release_notice",
            "requires_manual_reviewer_release": True,
            "activation_allowed": False,
        }
    ]
    for replay in replays:
        for row in _mapping_sequence(replay.get("agent_api_compatibility_notes")):
            text = _text(row.get("display_text"))
            rows.append(
                {
                    "note_id": "agent-api-note-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:12],
                    "source_replay_packet_ids": [_text(replay.get("packet_id"))],
                    "notification_text": text,
                    "notification_status": "placeholder_pending_manual_release_notice",
                    "requires_manual_reviewer_release": True,
                    "activation_allowed": False,
                }
            )
    return rows


def _validate_prerequisites(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"reviewer_controlled_activation_prerequisites[{index}]"
        if not _text(row.get("prerequisite_id")) or not _text(row.get("description")):
            problems.append(f"{prefix} requires prerequisite_id and description")
        if row.get("status") != "pending_reviewer_control":
            problems.append(f"{prefix}.status must be pending_reviewer_control")
        if row.get("required_before") != "any_guardrail_activation":
            problems.append(f"{prefix}.required_before must be any_guardrail_activation")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")


def _validate_signoffs(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"required_signoff_placeholders[{index}]"
        if not _text(row.get("signoff_id")) or not _text(row.get("required_role_placeholder")):
            problems.append(f"{prefix} requires signoff_id and required_role_placeholder")
        if row.get("signoff_status") != "placeholder_pending_manual_signoff":
            problems.append(f"{prefix}.signoff_status must be placeholder_pending_manual_signoff")
        if row.get("signed_by") is not None:
            problems.append(f"{prefix}.signed_by must remain null")
        if row.get("required_before_activation") is not True:
            problems.append(f"{prefix}.required_before_activation must be true")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")


def _validate_freshness(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"source_freshness_hold_clearance_criteria[{index}]"
        if not _text(row.get("criterion_id")) or not _text(row.get("caveat_text")):
            problems.append(f"{prefix} requires criterion_id and caveat_text")
        if row.get("clearance_required") is not True:
            problems.append(f"{prefix}.clearance_required must be true")
        if row.get("clearance_status") != "pending_reviewer_clearance":
            problems.append(f"{prefix}.clearance_status must be pending_reviewer_clearance")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")


def _validate_rollback(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"rollback_checkpoint_rows[{index}]"
        if not _text(row.get("checkpoint_id")) or not _text(row.get("rollback_owner_placeholder")):
            problems.append(f"{prefix} requires checkpoint_id and rollback_owner_placeholder")
        if row.get("checkpoint_status") != "pending_reviewer_confirmation":
            problems.append(f"{prefix}.checkpoint_status must be pending_reviewer_confirmation")
        if row.get("active_state_changed") is not False:
            problems.append(f"{prefix}.active_state_changed must be false")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")


def _validate_smoke(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"post_activation_smoke_checks[{index}]"
        if not _text(row.get("check_id")) or not _text(row.get("planned_check")):
            problems.append(f"{prefix} requires check_id and planned_check")
        if row.get("check_status") != "placeholder_pending_future_activation":
            problems.append(f"{prefix}.check_status must be placeholder_pending_future_activation")
        if row.get("requires_separate_activation_authorization") is not True:
            problems.append(f"{prefix}.requires_separate_activation_authorization must be true")
        if row.get("activation_allowed_by_this_packet") is not False:
            problems.append(f"{prefix}.activation_allowed_by_this_packet must be false")


def _validate_notes(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"agent_notification_notes[{index}]"
        if not _text(row.get("note_id")) or not _text(row.get("notification_text")):
            problems.append(f"{prefix} requires note_id and notification_text")
        if row.get("notification_status") != "placeholder_pending_manual_release_notice":
            problems.append(f"{prefix}.notification_status must be placeholder_pending_manual_release_notice")
        if row.get("requires_manual_reviewer_release") is not True:
            problems.append(f"{prefix}.requires_manual_reviewer_release must be true")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")


def _packet_ids(replays: Sequence[Mapping[str, Any]]) -> list[str]:
    return [_text(replay.get("packet_id"), POST_DECISION_PACKET_TYPE) for replay in replays]


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in (_text(item) for item in value) if item]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _scan_for_forbidden_payload(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in _FORBIDDEN_TRUE_FLAGS and child is True:
                problems.append(f"{child_path} must not be true")
            if _SENSITIVE_KEY_RE.search(key_text) and child not in (False, None, "", [], {}):
                problems.append(f"{child_path} must not contain private or runtime artifact data")
            _scan_for_forbidden_payload(child, child_path, problems)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_forbidden_payload(child, f"{path}[{index}]", problems)
    elif isinstance(value, str) and _FORBIDDEN_TEXT_RE.search(value):
        problems.append(f"{path} contains a prohibited activation, live, official-action, private-artifact, or guarantee claim")
