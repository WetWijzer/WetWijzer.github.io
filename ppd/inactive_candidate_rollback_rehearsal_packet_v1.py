"""Fixture-first inactive candidate rollback rehearsal packet v1.

This module builds and validates an offline rollback rehearsal packet from
synthetic inactive release candidate, smoke replay, monitoring outcome, and
stale-source hold packet references. It records rollback triggers, rollback
order, evidence preservation checks, reviewer dispositions, and exact offline
validation commands only.
"""

from __future__ import annotations

from copy import deepcopy
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "ppd.inactive_candidate_rollback_rehearsal_packet.v1"
MODE = "fixture_first_inactive_candidate_rollback_rehearsal_only"

REQUIRED_INPUT_REFS = (
    "synthetic_inactive_release_candidate",
    "synthetic_smoke_replay",
    "synthetic_monitoring_outcome",
    "synthetic_stale_source_hold_packet",
)

REQUIRED_TRIGGER_IDS = (
    "smoke_replay_regression_detected",
    "monitoring_outcome_blocked",
    "stale_source_hold_active",
    "reviewer_disposition_blocks_candidate",
)

REQUIRED_ROLLBACK_STEP_IDS = (
    "freeze_inactive_candidate_reference",
    "preserve_smoke_replay_evidence",
    "preserve_monitoring_outcome_evidence",
    "preserve_stale_source_hold_evidence",
    "record_reviewer_dispositions",
    "confirm_no_active_release_changes",
    "rerun_offline_validation_commands",
)

REQUIRED_EVIDENCE_CHECK_IDS = (
    "inactive_candidate_ref_retained",
    "smoke_replay_ref_retained",
    "monitoring_outcome_ref_retained",
    "stale_source_hold_ref_retained",
    "reviewer_disposition_ref_retained",
)

REQUIRED_REVIEWER_ROLES = (
    "release_reviewer",
    "smoke_replay_reviewer",
    "monitoring_reviewer",
    "source_freshness_reviewer",
)

REQUIRED_ATTESTATIONS = (
    "fixture_first",
    "offline_only",
    "synthetic_refs_only",
    "inactive_candidate_only",
    "no_release_promotion",
    "no_release_activation",
    "no_live_crawling",
    "no_devhub_access",
    "no_private_files",
    "no_form_filling",
    "no_uploads",
    "no_submissions",
    "no_certifications",
    "no_payments",
    "no_scheduling",
    "no_prompt_mutation",
    "no_guardrail_mutation",
    "no_process_model_mutation",
    "no_requirement_mutation",
    "no_contract_mutation",
    "no_source_mutation",
    "no_archive_mutation",
    "no_document_mutation",
    "no_devhub_surface_mutation",
    "no_crawler_mutation",
    "no_release_state_mutation",
    "no_daemon_state_mutation",
)

MUTATION_FLAGS = (
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_process_model_mutation",
    "active_requirement_mutation",
    "active_contract_mutation",
    "active_source_mutation",
    "active_archive_mutation",
    "active_document_mutation",
    "active_devhub_surface_mutation",
    "active_crawler_mutation",
    "active_release_mutation",
    "active_daemon_state_mutation",
    "release_promotion_performed",
    "release_activation_performed",
    "live_crawl_performed",
    "devhub_accessed",
    "private_file_accessed",
    "form_fill_performed",
    "upload_performed",
    "submission_performed",
    "certification_performed",
    "payment_performed",
    "scheduling_performed",
)

EXACT_OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/inactive_candidate_rollback_rehearsal_packet_v1.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_inactive_candidate_rollback_rehearsal_packet_v1.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

FORBIDDEN_KEY_TERMS = {
    "auth_state",
    "browser_state",
    "cookie",
    "credentials",
    "download_path",
    "downloaded_document",
    "field_value",
    "har",
    "local_private_path",
    "password",
    "payment_details",
    "private_file",
    "private_path",
    "raw_body",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "secret",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "warc_path",
}

FORBIDDEN_TRUE_KEYS = {
    "activation_performed",
    "active_release_state_mutation",
    "certification_performed",
    "devhub_accessed",
    "form_fill_performed",
    "live_crawl_performed",
    "payment_performed",
    "promotion_performed",
    "release_activation_performed",
    "release_promotion_performed",
    "scheduling_performed",
    "submission_performed",
    "upload_performed",
}

FORBIDDEN_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|"
    r"(auth[_ -]?state|browser[_ -]?state|cookie|credential|devhub session|har|password|"
    r"payment detail|private file|private path|raw[_ -]?(body|crawl|download|html|pdf)|"
    r"secret|session[_ -]?state|storage[_ -]?state|token|trace|warc)",
    re.IGNORECASE,
)

CONSEQUENTIAL_TEXT_RE = re.compile(
    r"\b(click submit|certify acknowledgement|certify application|enter payment|pay fees|"
    r"promote release|activate release|schedule inspection|submit payment|submit permit|"
    r"submit request|upload correction|upload document|upload plans)\b",
    re.IGNORECASE,
)


class InactiveCandidateRollbackRehearsalError(ValueError):
    """Raised when a rollback rehearsal packet is incomplete or unsafe."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid inactive candidate rollback rehearsal packet v1: " + "; ".join(self.errors))


def load_inactive_candidate_rollback_rehearsal_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise InactiveCandidateRollbackRehearsalError(["fixture must contain a JSON object"])
    return loaded


def build_inactive_candidate_rollback_rehearsal_packet_v1(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build the rollback rehearsal packet from synthetic fixture references."""

    input_errors = validate_inactive_candidate_rollback_rehearsal_source_v1(source)
    if input_errors:
        raise InactiveCandidateRollbackRehearsalError(input_errors)

    refs = deepcopy(_mapping(source.get("input_refs")))
    triggers = _rollback_triggers(refs)
    rollback_order = _rollback_order(refs, triggers)
    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v1",
        "mode": MODE,
        "fixture_first": True,
        "offline_only": True,
        "synthetic_refs_only": True,
        "inactive_candidate_only": True,
        "input_refs": refs,
        "rollback_triggers": triggers,
        "rollback_order": rollback_order,
        "evidence_preservation_checks": _evidence_preservation_checks(refs),
        "reviewer_dispositions": _reviewer_dispositions(source),
        "exact_offline_validation_commands": [list(command) for command in EXACT_OFFLINE_VALIDATION_COMMANDS],
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "mutation_flags": {name: False for name in MUTATION_FLAGS},
        "overall_status": "rollback_rehearsal_ready_with_inactive_candidate_held",
    }

    output_errors = validate_inactive_candidate_rollback_rehearsal_packet_v1(packet)
    if output_errors:
        raise InactiveCandidateRollbackRehearsalError(output_errors)
    return packet


def validate_inactive_candidate_rollback_rehearsal_source_v1(source: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_walk_safety_errors(source, "$"))

    if source.get("packet_type") != "ppd.inactive_candidate_rollback_rehearsal_source.v1":
        errors.append("packet_type must be ppd.inactive_candidate_rollback_rehearsal_source.v1")
    if source.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if source.get("offline_only") is not True:
        errors.append("offline_only must be true")
    if source.get("synthetic_refs_only") is not True:
        errors.append("synthetic_refs_only must be true")

    refs = _mapping(source.get("input_refs"))
    if not refs:
        errors.append("input_refs must be a non-empty object")
    for ref_name in REQUIRED_INPUT_REFS:
        ref = _mapping(refs.get(ref_name))
        if not ref:
            errors.append(f"input_refs.{ref_name} must be present")
            continue
        _require_text(ref, "artifact_id", f"input_refs.{ref_name}", errors)
        _require_text(ref, "schema_version", f"input_refs.{ref_name}", errors)
        _require_text(ref, "status", f"input_refs.{ref_name}", errors)
        if ref.get("synthetic") is not True:
            errors.append(f"input_refs.{ref_name}.synthetic must be true")
        if ref.get("inactive") is not True:
            errors.append(f"input_refs.{ref_name}.inactive must be true")

    dispositions = list(_mapping_sequence(source.get("reviewer_dispositions")))
    roles = {str(item.get("role") or "") for item in dispositions}
    for role in REQUIRED_REVIEWER_ROLES:
        if role not in roles:
            errors.append(f"reviewer_dispositions missing {role}")
    for index, item in enumerate(dispositions):
        path = f"reviewer_dispositions[{index}]"
        _require_text(item, "role", path, errors)
        _require_text(item, "disposition", path, errors)
        _require_text(item, "evidence_ref", path, errors)
        if item.get("requires_rollback_rehearsal") is not True:
            errors.append(f"{path}.requires_rollback_rehearsal must be true")

    commands = source.get("exact_offline_validation_commands")
    if commands is not None and _commands(commands) != [list(command) for command in EXACT_OFFLINE_VALIDATION_COMMANDS]:
        errors.append("exact_offline_validation_commands must match the v1 offline command inventory exactly")

    return errors


def validate_inactive_candidate_rollback_rehearsal_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_walk_safety_errors(packet, "$"))

    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != "v1":
        errors.append("packet_version must be v1")
    if packet.get("mode") != MODE:
        errors.append(f"mode must be {MODE}")
    for key in ("fixture_first", "offline_only", "synthetic_refs_only", "inactive_candidate_only"):
        if packet.get(key) is not True:
            errors.append(f"{key} must be true")

    refs = _mapping(packet.get("input_refs"))
    for ref_name in REQUIRED_INPUT_REFS:
        if ref_name not in refs:
            errors.append(f"input_refs missing {ref_name}")

    triggers = list(_mapping_sequence(packet.get("rollback_triggers")))
    trigger_ids = tuple(str(item.get("trigger_id") or "") for item in triggers)
    if trigger_ids != REQUIRED_TRIGGER_IDS:
        errors.append("rollback_triggers must match the required trigger order")
    for index, item in enumerate(triggers):
        path = f"rollback_triggers[{index}]"
        if item.get("rollback_required") is not True:
            errors.append(f"{path}.rollback_required must be true")
        _require_text(item, "evidence_ref", path, errors)
        _require_text(item, "trigger_reason", path, errors)

    rollback_steps = list(_mapping_sequence(packet.get("rollback_order")))
    step_ids = tuple(str(item.get("step_id") or "") for item in rollback_steps)
    if step_ids != REQUIRED_ROLLBACK_STEP_IDS:
        errors.append("rollback_order must match the required step order")
    for index, item in enumerate(rollback_steps):
        path = f"rollback_order[{index}]"
        if item.get("order") != index + 1:
            errors.append(f"{path}.order must be {index + 1}")
        _require_text(item, "action", path, errors)
        _require_text(item, "evidence_ref", path, errors)
        if item.get("offline_only") is not True:
            errors.append(f"{path}.offline_only must be true")

    checks = list(_mapping_sequence(packet.get("evidence_preservation_checks")))
    check_ids = tuple(str(item.get("check_id") or "") for item in checks)
    if check_ids != REQUIRED_EVIDENCE_CHECK_IDS:
        errors.append("evidence_preservation_checks must match the required check order")
    for index, item in enumerate(checks):
        path = f"evidence_preservation_checks[{index}]"
        if item.get("preserved") is not True:
            errors.append(f"{path}.preserved must be true")
        _require_text(item, "evidence_ref", path, errors)

    dispositions = list(_mapping_sequence(packet.get("reviewer_dispositions")))
    roles = tuple(str(item.get("role") or "") for item in dispositions)
    if roles != REQUIRED_REVIEWER_ROLES:
        errors.append("reviewer_dispositions must match the required reviewer role order")
    for index, item in enumerate(dispositions):
        path = f"reviewer_dispositions[{index}]"
        _require_text(item, "disposition", path, errors)
        _require_text(item, "evidence_ref", path, errors)
        if item.get("candidate_remains_inactive") is not True:
            errors.append(f"{path}.candidate_remains_inactive must be true")

    if _commands(packet.get("exact_offline_validation_commands")) != [list(command) for command in EXACT_OFFLINE_VALIDATION_COMMANDS]:
        errors.append("exact_offline_validation_commands must match the v1 offline command inventory exactly")

    attestations = _mapping(packet.get("attestations"))
    for name in REQUIRED_ATTESTATIONS:
        if attestations.get(name) is not True:
            errors.append(f"attestations.{name} must be true")

    mutation_flags = _mapping(packet.get("mutation_flags"))
    for name in MUTATION_FLAGS:
        if mutation_flags.get(name) is not False:
            errors.append(f"mutation_flags.{name} must be false")

    return errors


def require_inactive_candidate_rollback_rehearsal_packet_v1(packet: Mapping[str, Any]) -> None:
    errors = validate_inactive_candidate_rollback_rehearsal_packet_v1(packet)
    if errors:
        raise InactiveCandidateRollbackRehearsalError(errors)


def build_inactive_candidate_rollback_rehearsal_packet_v1_from_fixture(path: str | Path) -> dict[str, Any]:
    return build_inactive_candidate_rollback_rehearsal_packet_v1(
        load_inactive_candidate_rollback_rehearsal_fixture(path)
    )


def _rollback_triggers(refs: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "trigger_id": "smoke_replay_regression_detected",
            "rollback_required": True,
            "trigger_reason": "Synthetic smoke replay reported a blocked regression outcome.",
            "evidence_ref": _artifact_ref(refs, "synthetic_smoke_replay"),
        },
        {
            "trigger_id": "monitoring_outcome_blocked",
            "rollback_required": True,
            "trigger_reason": "Synthetic monitoring outcome requires hold before any activation.",
            "evidence_ref": _artifact_ref(refs, "synthetic_monitoring_outcome"),
        },
        {
            "trigger_id": "stale_source_hold_active",
            "rollback_required": True,
            "trigger_reason": "Synthetic stale-source hold remains active for the candidate.",
            "evidence_ref": _artifact_ref(refs, "synthetic_stale_source_hold_packet"),
        },
        {
            "trigger_id": "reviewer_disposition_blocks_candidate",
            "rollback_required": True,
            "trigger_reason": "At least one synthetic reviewer disposition requires hold and rollback rehearsal.",
            "evidence_ref": _artifact_ref(refs, "synthetic_inactive_release_candidate"),
        },
    ]


def _rollback_order(refs: Mapping[str, Any], triggers: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    smoke_ref = _artifact_ref(refs, "synthetic_smoke_replay")
    monitoring_ref = _artifact_ref(refs, "synthetic_monitoring_outcome")
    stale_ref = _artifact_ref(refs, "synthetic_stale_source_hold_packet")
    candidate_ref = _artifact_ref(refs, "synthetic_inactive_release_candidate")
    return [
        {
            "order": 1,
            "step_id": "freeze_inactive_candidate_reference",
            "action": "Keep the synthetic inactive candidate reference unchanged and held.",
            "evidence_ref": candidate_ref,
            "offline_only": True,
        },
        {
            "order": 2,
            "step_id": "preserve_smoke_replay_evidence",
            "action": "Retain the synthetic smoke replay packet reference for reviewer traceability.",
            "evidence_ref": smoke_ref,
            "offline_only": True,
        },
        {
            "order": 3,
            "step_id": "preserve_monitoring_outcome_evidence",
            "action": "Retain the synthetic monitoring outcome packet reference for reviewer traceability.",
            "evidence_ref": monitoring_ref,
            "offline_only": True,
        },
        {
            "order": 4,
            "step_id": "preserve_stale_source_hold_evidence",
            "action": "Retain the synthetic stale-source hold packet reference for reviewer traceability.",
            "evidence_ref": stale_ref,
            "offline_only": True,
        },
        {
            "order": 5,
            "step_id": "record_reviewer_dispositions",
            "action": "Record reviewer dispositions against synthetic packet references only.",
            "evidence_ref": candidate_ref,
            "offline_only": True,
        },
        {
            "order": 6,
            "step_id": "confirm_no_active_release_changes",
            "action": "Confirm all active release, crawler, source, archive, document, prompt, guardrail, process-model, requirement, contract, DevHub surface, and daemon-state mutation flags remain false.",
            "evidence_ref": candidate_ref,
            "offline_only": True,
        },
        {
            "order": 7,
            "step_id": "rerun_offline_validation_commands",
            "action": "Run only the exact offline validation command inventory recorded in this packet.",
            "evidence_ref": str(len(triggers)) + " rollback triggers recorded",
            "offline_only": True,
        },
    ]


def _evidence_preservation_checks(refs: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "inactive_candidate_ref_retained",
            "evidence_ref": _artifact_ref(refs, "synthetic_inactive_release_candidate"),
            "preserved": True,
        },
        {
            "check_id": "smoke_replay_ref_retained",
            "evidence_ref": _artifact_ref(refs, "synthetic_smoke_replay"),
            "preserved": True,
        },
        {
            "check_id": "monitoring_outcome_ref_retained",
            "evidence_ref": _artifact_ref(refs, "synthetic_monitoring_outcome"),
            "preserved": True,
        },
        {
            "check_id": "stale_source_hold_ref_retained",
            "evidence_ref": _artifact_ref(refs, "synthetic_stale_source_hold_packet"),
            "preserved": True,
        },
        {
            "check_id": "reviewer_disposition_ref_retained",
            "evidence_ref": "synthetic_reviewer_disposition_rows_v1",
            "preserved": True,
        },
    ]


def _reviewer_dispositions(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = {str(item.get("role") or ""): item for item in _mapping_sequence(source.get("reviewer_dispositions"))}
    dispositions: list[dict[str, Any]] = []
    for role in REQUIRED_REVIEWER_ROLES:
        row = _mapping(rows.get(role))
        dispositions.append(
            {
                "role": role,
                "disposition": str(row.get("disposition") or "hold_for_rollback_rehearsal"),
                "evidence_ref": str(row.get("evidence_ref") or role + "_synthetic_evidence_ref"),
                "candidate_remains_inactive": True,
                "requires_rollback_rehearsal": True,
            }
        )
    return dispositions


def _artifact_ref(refs: Mapping[str, Any], key: str) -> str:
    ref = _mapping(refs.get(key))
    artifact_id = str(ref.get("artifact_id") or key)
    schema_version = str(ref.get("schema_version") or "v1")
    return artifact_id + "@" + schema_version


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _commands(value: Any) -> list[list[str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    commands: list[list[str]] = []
    for item in value:
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            command = [part for part in item if isinstance(part, str)]
            if len(command) == len(item):
                commands.append(command)
    return commands


def _require_text(row: Mapping[str, Any], key: str, path: str, errors: list[str]) -> None:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}.{key} must be a non-empty string")


def _walk_safety_errors(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            if normalized_key in FORBIDDEN_KEY_TERMS:
                errors.append(f"{path}.{key_text} uses forbidden private or raw artifact key")
            if normalized_key in FORBIDDEN_TRUE_KEYS and child is True:
                errors.append(f"{path}.{key_text} must not be true")
            errors.extend(_walk_safety_errors(child, f"{path}.{key_text}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            errors.extend(_walk_safety_errors(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        if FORBIDDEN_TEXT_RE.search(value):
            errors.append(f"{path} contains forbidden private or raw artifact text")
        if CONSEQUENTIAL_TEXT_RE.search(value):
            errors.append(f"{path} contains forbidden consequential action text")
    return errors
