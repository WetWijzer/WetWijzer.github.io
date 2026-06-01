"""Inactive guardrail promotion candidate v4 validation.

The v4 packet is fixture-first and inactive-only. It records the references and
manual prerequisites needed before a later reviewed task may consider activating
any guardrail bundle. It must not mutate active guardrails, store private DevHub
artifacts, claim official action completion, or make legal/permitting guarantees.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.inactive_guardrail_promotion_candidate.v4"
PACKET_VERSION = "v4"
INACTIVE_STATUS = "inactive_candidate_only"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/inactive_guardrail_bundle_promotion_candidate_v4.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_inactive_guardrail_bundle_promotion_candidate_v4"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_LISTS = (
    "readiness_replay_references",
    "prior_guardrail_placeholder_fixtures",
    "inactive_promotion_rows",
    "activation_prerequisites",
    "stale_source_holds",
    "reviewer_signoff_placeholders",
    "rollback_plan",
    "post_promotion_smoke_checks",
    "offline_validation_commands",
    "validation_commands",
)

_REQUIRED_TRUE_FLAGS = (
    "fixture_first",
    "inactive_candidate_only",
    "metadata_only",
    "readiness_replay_refs_required",
    "prior_guardrail_placeholders_required",
    "manual_reviewer_signoff_required",
    "rollback_plan_required",
    "post_promotion_smoke_required",
    "stale_source_holds_carried_forward",
    "validation_commands_required",
)

_REQUIRED_FALSE_FLAGS = (
    "active_guardrail_mutation",
    "active_guardrail_bundle_mutation",
    "active_prompt_mutation",
    "active_process_model_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
    "active_mutation",
    "guardrails_changed",
    "guardrail_bundles_changed",
    "prompts_changed",
    "process_models_changed",
    "requirements_changed",
    "sources_changed",
    "release_state_changed",
    "promotion_executed",
    "activation_executed",
    "official_action_completed",
    "opens_devhub",
    "stores_private_artifacts",
    "uploads",
    "submits",
    "certifies",
    "pays",
    "schedules",
)

_PRIVATE_KEY_RE = re.compile(
    r"(^|_)(auth|browser|cookie|credential|devhub[_-]?session|download|downloaded|har|password|payment|private|raw|screenshot|session|storage[_-]?state|token|trace[_-]?(file|artifact|archive)?|warc)(_|$)",
    re.IGNORECASE,
)
_PRIVATE_VALUE_RE = re.compile(
    r"(auth state|browser state|cookie jar|credential|downloaded document|har file|private devhub|private artifact|raw crawl|raw body|raw html|raw pdf|session state|storage state|trace.zip|warc payload|live devhub|/(tmp|private|var/folders|home)/|\\users\\|\.har$|\.warc(\.gz)?$)",
    re.IGNORECASE,
)
_FORBIDDEN_CLAIM_RE = re.compile(
    r"(active guardrail (was )?(mutated|changed|replaced)|guardrail bundle activated|official action completed|completion confirmed|certified acknowledgement|paid fee|payment completed|scheduled inspection|submitted permit|uploaded correction|permit will be approved|permit will issue|approval guaranteed|guarantee approval|legal advice|legal guarantee|legally compliant|permitting guarantee)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InactiveGuardrailBundlePromotionCandidateV4Result:
    valid: bool
    problems: tuple[str, ...]


class InactiveGuardrailBundlePromotionCandidateV4Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid inactive guardrail promotion candidate v4: " + "; ".join(self.problems))


def load_inactive_guardrail_bundle_promotion_candidate_v4(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("inactive guardrail promotion candidate v4 fixture must be a JSON object")
    assert_valid_inactive_guardrail_bundle_promotion_candidate_v4(loaded)
    return loaded


def assert_valid_inactive_guardrail_bundle_promotion_candidate_v4(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_guardrail_bundle_promotion_candidate_v4(packet)
    if not result.valid:
        raise InactiveGuardrailBundlePromotionCandidateV4Error(result.problems)


def validate_inactive_guardrail_bundle_promotion_candidate_v4(
    packet: Mapping[str, Any],
) -> InactiveGuardrailBundlePromotionCandidateV4Result:
    if not isinstance(packet, Mapping):
        return InactiveGuardrailBundlePromotionCandidateV4Result(False, ("packet must be an object",))

    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")

    for key in _REQUIRED_TRUE_FLAGS:
        if packet.get(key) is not True:
            problems.append(f"{key} must be true")
    for key in _REQUIRED_FALSE_FLAGS:
        if packet.get(key) is not False:
            problems.append(f"{key} must be false")
    for key in _REQUIRED_LISTS:
        if not _non_empty_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")

    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        problems.append("offline_validation_commands must exactly match the v4 offline validation command bundle")
    if packet.get("validation_commands") != VALIDATION_COMMANDS:
        problems.append("validation_commands must contain the PP&D daemon self-test command")

    _validate_inactive_rows(packet.get("inactive_promotion_rows"), problems)
    _validate_activation_prerequisites(packet.get("activation_prerequisites"), problems)
    _validate_stale_source_holds(packet.get("stale_source_holds"), problems)
    _validate_reviewer_signoffs(packet.get("reviewer_signoff_placeholders"), problems)
    _validate_rollback_plan(packet.get("rollback_plan"), problems)
    _validate_smoke_checks(packet.get("post_promotion_smoke_checks"), problems)
    _validate_cross_references(packet, problems)
    _validate_forbidden_payload(packet, problems)
    return InactiveGuardrailBundlePromotionCandidateV4Result(not problems, tuple(problems))


def _validate_inactive_rows(value: Any, problems: list[str]) -> None:
    seen: set[str] = set()
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"inactive_promotion_rows[{index}]"
        candidate_id = _text(row.get("candidate_id"))
        if not candidate_id:
            problems.append(f"{prefix}.candidate_id is required")
        elif candidate_id in seen:
            problems.append(f"{prefix}.candidate_id must be unique")
        seen.add(candidate_id)
        if row.get("candidate_status") != INACTIVE_STATUS:
            problems.append(f"{prefix}.candidate_status must remain inactive_candidate_only")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")
        for key in (
            "readiness_replay_ref",
            "prior_guardrail_placeholder_fixture_ref",
            "activation_prerequisite_ref",
            "stale_source_hold_ref",
            "reviewer_signoff_placeholder_ref",
            "rollback_plan_ref",
            "post_promotion_smoke_check_ref",
        ):
            if not _text(row.get(key)):
                problems.append(f"{prefix}.{key} is required")


def _validate_activation_prerequisites(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"activation_prerequisites[{index}]"
        if not _text(row.get("prerequisite_id")):
            problems.append(f"{prefix}.prerequisite_id is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")
        for key in ("requires_readiness_replay", "requires_prior_placeholder_fixture", "requires_stale_source_hold_review", "requires_reviewer_signoff", "requires_rollback_plan", "requires_post_promotion_smoke", "requires_validation_commands"):
            if row.get(key) is not True:
                problems.append(f"{prefix}.{key} must be true")


def _validate_stale_source_holds(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"stale_source_holds[{index}]"
        if not _text(row.get("hold_id")):
            problems.append(f"{prefix}.hold_id is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("hold_status") != "held_pending_public_source_freshness_review":
            problems.append(f"{prefix}.hold_status must be held_pending_public_source_freshness_review")
        if row.get("promotion_blocked") is not True:
            problems.append(f"{prefix}.promotion_blocked must be true")


def _validate_reviewer_signoffs(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"reviewer_signoff_placeholders[{index}]"
        if not _text(row.get("placeholder_id")):
            problems.append(f"{prefix}.placeholder_id is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("signoff_status") != "pending_manual_review":
            problems.append(f"{prefix}.signoff_status must be pending_manual_review")
        if row.get("reviewer") not in {"", None}:
            problems.append(f"{prefix}.reviewer must be blank until manual review")
        if row.get("signed_at") not in {"", None}:
            problems.append(f"{prefix}.signed_at must be blank until manual review")


def _validate_rollback_plan(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"rollback_plan[{index}]"
        if not _text(row.get("rollback_ref")):
            problems.append(f"{prefix}.rollback_ref is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("rollback_target") != "discard_inactive_candidate_only":
            problems.append(f"{prefix}.rollback_target must be discard_inactive_candidate_only")
        if row.get("active_state_changed") is not False:
            problems.append(f"{prefix}.active_state_changed must be false")


def _validate_smoke_checks(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"post_promotion_smoke_checks[{index}]"
        if not _text(row.get("smoke_check_id")):
            problems.append(f"{prefix}.smoke_check_id is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("smoke_status") != "planned_not_run_for_inactive_candidate":
            problems.append(f"{prefix}.smoke_status must be planned_not_run_for_inactive_candidate")
        if row.get("requires_separate_post_promotion_task") is not True:
            problems.append(f"{prefix}.requires_separate_post_promotion_task must be true")


def _validate_cross_references(packet: Mapping[str, Any], problems: list[str]) -> None:
    candidate_ids = {_text(row.get("candidate_id")) for row in _mapping_sequence(packet.get("inactive_promotion_rows"))}
    refs = {
        "readiness_replay_references": {_text(row.get("replay_ref")) for row in _mapping_sequence(packet.get("readiness_replay_references"))},
        "prior_guardrail_placeholder_fixtures": {_text(row.get("fixture_ref")) for row in _mapping_sequence(packet.get("prior_guardrail_placeholder_fixtures"))},
        "activation_prerequisites": {_text(row.get("prerequisite_id")) for row in _mapping_sequence(packet.get("activation_prerequisites"))},
        "stale_source_holds": {_text(row.get("hold_id")) for row in _mapping_sequence(packet.get("stale_source_holds"))},
        "reviewer_signoff_placeholders": {_text(row.get("placeholder_id")) for row in _mapping_sequence(packet.get("reviewer_signoff_placeholders"))},
        "rollback_plan": {_text(row.get("rollback_ref")) for row in _mapping_sequence(packet.get("rollback_plan"))},
        "post_promotion_smoke_checks": {_text(row.get("smoke_check_id")) for row in _mapping_sequence(packet.get("post_promotion_smoke_checks"))},
    }
    row_ref_fields = {
        "readiness_replay_ref": "readiness_replay_references",
        "prior_guardrail_placeholder_fixture_ref": "prior_guardrail_placeholder_fixtures",
        "activation_prerequisite_ref": "activation_prerequisites",
        "stale_source_hold_ref": "stale_source_holds",
        "reviewer_signoff_placeholder_ref": "reviewer_signoff_placeholders",
        "rollback_plan_ref": "rollback_plan",
        "post_promotion_smoke_check_ref": "post_promotion_smoke_checks",
    }
    for index, row in enumerate(_mapping_sequence(packet.get("inactive_promotion_rows"))):
        for field, section in row_ref_fields.items():
            if _text(row.get(field)) not in refs[section]:
                problems.append(f"inactive_promotion_rows[{index}].{field} must reference {section}")
    for section in refs:
        for index, row in enumerate(_mapping_sequence(packet.get(section))):
            candidate_id = _text(row.get("candidate_id"))
            if candidate_id and candidate_id not in candidate_ids:
                problems.append(f"{section}[{index}].candidate_id must reference inactive_promotion_rows")


def _validate_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    allowed_keys = {"readiness_replay_references", "readiness_replay_ref"}
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _REQUIRED_FALSE_FLAGS and value is not False:
            problems.append(f"{path} must be false")
        if normalized_key not in allowed_keys and _PRIVATE_KEY_RE.search(normalized_key) and _truthy(value):
            problems.append(f"{path} must not include private, session, auth, raw, browser, trace, or downloaded artifacts")
        if isinstance(value, str):
            if _PRIVATE_VALUE_RE.search(value):
                problems.append(f"{path} must not reference private, session, auth, raw, browser, trace, or downloaded artifacts")
            if _FORBIDDEN_CLAIM_RE.search(value):
                problems.append(f"{path} must not claim active mutation, official-action completion, legal guarantees, or permitting guarantees")


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
