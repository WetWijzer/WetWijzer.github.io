"""Fixture-first post-decision smoke replay v4.

This packet consumes only committed release decision packet v4 fixtures and
inactive guardrail placeholder fixtures. It is an offline smoke replay artifact;
it does not activate guardrails, open DevHub, fetch documents, upload, submit,
certify, pay, schedule, or make legal/permitting guarantees.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

PACKET_TYPE = "ppd.post_decision_smoke_replay.v4"
PACKET_VERSION = "v4"
MODE = "fixture_first_post_decision_smoke_replay_v4"
RELEASE_DECISION_PACKET_VERSION = "release_decision_packet_v4"
PLACEHOLDER_FIXTURE_KIND = "inactive_guardrail_placeholder_fixture"
EXACT_OFFLINE_VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

REQUIRED_BOUNDARIES = {
    "fixture_first": True,
    "release_decision_packet_v4_fixtures_only": True,
    "inactive_guardrail_placeholder_fixtures_only": True,
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

_REQUIRED_LISTS = (
    "unresolved_hold_propagation",
    "source_freshness_caveat_display",
    "agent_api_compatibility_notes",
    "guardrail_placeholder_checks",
    "rollback_owner_placeholders",
    "manual_handoff_reminders",
    "smoke_expectations",
)

_REQUIRED_EXPECTATION_IDS = frozenset(
    {
        "go-no-go-outcome-handling",
        "inactive-guardrail-placeholder-checks",
        "unresolved-hold-propagation",
        "source-freshness-caveat-display",
        "agent-api-compatibility-checks",
        "rollback-owner-placeholder-checks",
        "manual-handoff-reminders",
        "offline-validation-command-exactness",
    }
)

_FORBIDDEN_TRUE_FLAGS = frozenset(
    {
        "guardrail_activation_enabled",
        "active_activation",
        "active_guardrail_activation",
        "active_guardrail_mutation",
        "active_release_state_mutation",
        "active_mutation",
        "devhub_opened",
        "private_documents_read",
        "upload_enabled",
        "submission_enabled",
        "certification_enabled",
        "payment_enabled",
        "scheduling_enabled",
        "legal_or_permitting_guarantee_enabled",
        "guardrails_activated",
        "uploads_performed",
        "submissions_performed",
        "certifications_performed",
        "payments_performed",
        "scheduling_performed",
        "legal_or_permitting_guarantees_made",
    }
)

_SENSITIVE_KEY_RE = re.compile(
    r"(^|_)(auth|browser_state|cookie|credential|har|password|raw|screenshot|session|session_state|storage_state|token|trace)(_|$)",
    re.IGNORECASE,
)
_FORBIDDEN_TEXT_RE = re.compile(
    r"(activation complete|activated guardrails|active guardrails|approval guaranteed|guaranteed approval|guaranteed issuance|legal advice|legal guarantee|permit will be approved|permit will be issued|will pass plan review|official action completed|submitted permit|uploaded correction|paid fee|scheduled inspection|certified acknowledgement|live devhub|session state|storage state|trace file|raw crawl|raw pdf)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PostDecisionSmokeReplayV4Result:
    valid: bool
    problems: tuple[str, ...]


class PostDecisionSmokeReplayV4Error(ValueError):
    def __init__(self, problems: Sequence[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid post-decision smoke replay v4: " + "; ".join(self.problems))


def load_post_decision_smoke_replay_v4_fixture(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise ValueError("post-decision smoke replay v4 source fixture must be an object")
    return build_post_decision_smoke_replay_v4(loaded)


def assert_valid_post_decision_smoke_replay_v4(packet: Mapping[str, Any]) -> None:
    result = validate_post_decision_smoke_replay_v4(packet)
    if not result.valid:
        raise PostDecisionSmokeReplayV4Error(result.problems)


def build_post_decision_smoke_replay_v4(source_fixture: Mapping[str, Any]) -> dict[str, Any]:
    decision = _mapping(source_fixture.get("release_decision_packet_v4"), "release_decision_packet_v4")
    placeholders = _mapping_sequence(source_fixture.get("inactive_guardrail_placeholder_fixtures"))
    _validate_release_decision_input(decision)
    _validate_placeholder_inputs(placeholders)

    recommendation = _text(decision.get("recommendation"))
    unresolved_holds = _mapping_sequence(decision.get("unresolved_hold_inventory"))
    candidate_ids = _string_list(decision.get("candidate_ids"))
    source_refs = _required_source_references(source_fixture, placeholders)

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": "post-decision-smoke-replay-v4-fixture",
        "mode": MODE,
        "consumes_only": {
            "release_decision_packet_v4_fixtures": True,
            "inactive_guardrail_placeholder_fixtures": True,
        },
        "source_fixture_refs": _string_list(source_fixture.get("source_fixture_refs")),
        "required_source_references": source_refs,
        "boundaries": dict(REQUIRED_BOUNDARIES),
        "release_outcome_handling": {
            "go_no_go_outcome": recommendation,
            "agent_expected_outcome": "block_activation_and_surface_unresolved_holds" if recommendation == "NO_GO" else "display_caveats_before_any_later_review",
            "candidate_ids": candidate_ids,
            "activation_allowed": False,
        },
        "unresolved_hold_propagation": [_hold_row(row) for row in unresolved_holds],
        "source_freshness_caveat_display": [_display_row("source-freshness", value) for value in _string_list(decision.get("source_freshness_caveats"))],
        "agent_api_compatibility_notes": [_display_row("agent-api", value) for value in _string_list(decision.get("agent_api_compatibility_notes"))],
        "guardrail_placeholder_checks": [_placeholder_check(row) for row in placeholders],
        "rollback_owner_placeholders": _rollback_placeholders(decision, placeholders),
        "manual_handoff_reminders": _manual_handoff_reminders(),
        "smoke_expectations": _smoke_expectations(recommendation),
        "attestations": dict(REQUIRED_ATTESTATIONS),
        "exact_offline_validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
        "validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
    }
    assert_valid_post_decision_smoke_replay_v4(packet)
    return packet


def validate_post_decision_smoke_replay_v4(packet: Mapping[str, Any]) -> PostDecisionSmokeReplayV4Result:
    if not isinstance(packet, Mapping):
        return PostDecisionSmokeReplayV4Result(False, ("packet must be an object",))
    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")
    if packet.get("mode") != MODE:
        problems.append(f"mode must be {MODE}")
    if packet.get("consumes_only") != {"release_decision_packet_v4_fixtures": True, "inactive_guardrail_placeholder_fixtures": True}:
        problems.append("consumes_only must allow only release decision packet v4 fixtures and inactive guardrail placeholder fixtures")
    _validate_required_source_references(packet.get("required_source_references"), problems)
    if packet.get("boundaries") != REQUIRED_BOUNDARIES:
        problems.append("boundaries must exactly preserve fixture-only offline non-activation limits")
    if packet.get("attestations") != REQUIRED_ATTESTATIONS:
        problems.append("attestations must exactly deny guardrail activation, DevHub access, private document reads, official actions, and guarantees")
    if packet.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("exact_offline_validation_commands must contain only the daemon self-test command")
    if packet.get("validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("validation_commands must contain only the daemon self-test command")
    for key in _REQUIRED_LISTS:
        if not _mapping_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")
    _validate_outcome(packet.get("release_outcome_handling"), problems)
    _validate_hold_rows(packet.get("unresolved_hold_propagation"), problems)
    _validate_display_rows(packet.get("source_freshness_caveat_display"), "source_freshness_caveat_display", problems)
    _validate_display_rows(packet.get("agent_api_compatibility_notes"), "agent_api_compatibility_notes", problems)
    _validate_placeholder_checks(packet.get("guardrail_placeholder_checks"), problems)
    _validate_rollback_rows(packet.get("rollback_owner_placeholders"), problems)
    _validate_handoff_rows(packet.get("manual_handoff_reminders"), problems)
    _validate_smoke_expectations(packet.get("smoke_expectations"), problems)
    _scan_for_forbidden_payload(packet, "$", problems)
    return PostDecisionSmokeReplayV4Result(not problems, tuple(dict.fromkeys(problems)))


def _validate_release_decision_input(decision: Mapping[str, Any]) -> None:
    if decision.get("packet_version") != RELEASE_DECISION_PACKET_VERSION:
        raise ValueError("release_decision_packet_v4.packet_version must be release_decision_packet_v4")
    if decision.get("source_mode") != "fixtures_only":
        raise ValueError("release decision packet must be fixtures_only")
    if decision.get("guardrail_activation") != "not_performed":
        raise ValueError("release decision packet must not perform guardrail activation")
    if decision.get("devhub_access") != "not_performed":
        raise ValueError("release decision packet must not access DevHub")
    if decision.get("legal_or_permitting_guarantee") != "not_provided":
        raise ValueError("release decision packet must not provide legal or permitting guarantees")
    if decision.get("recommendation") not in {"NO_GO", "GO_WITH_CAVEATS"}:
        raise ValueError("release decision packet recommendation must be NO_GO or GO_WITH_CAVEATS")
    if not _string_list(decision.get("source_freshness_caveats")):
        raise ValueError("release decision packet must include source_freshness_caveats")
    if not _string_list(decision.get("agent_api_compatibility_notes")):
        raise ValueError("release decision packet must include agent_api_compatibility_notes")
    if not _mapping_sequence(decision.get("rollback_owner_placeholders")):
        raise ValueError("release decision packet must include rollback_owner_placeholders")


def _validate_placeholder_inputs(rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError("inactive_guardrail_placeholder_fixtures must be non-empty")
    for index, row in enumerate(rows):
        if row.get("fixture_kind") != PLACEHOLDER_FIXTURE_KIND:
            raise ValueError(f"inactive_guardrail_placeholder_fixtures[{index}].fixture_kind must be {PLACEHOLDER_FIXTURE_KIND}")
        if row.get("placeholder_status") != "inactive_placeholder_only":
            raise ValueError(f"inactive_guardrail_placeholder_fixtures[{index}].placeholder_status must be inactive_placeholder_only")
        if row.get("activation_allowed") is not False:
            raise ValueError(f"inactive_guardrail_placeholder_fixtures[{index}].activation_allowed must be false")
        if not _text(row.get("placeholder_id")):
            raise ValueError(f"inactive_guardrail_placeholder_fixtures[{index}].placeholder_id is required")
        if not _text(row.get("guardrail_bundle_id")):
            raise ValueError(f"inactive_guardrail_placeholder_fixtures[{index}].guardrail_bundle_id is required")


def _validate_required_source_references(value: Any, problems: list[str]) -> None:
    refs = value if isinstance(value, Mapping) else {}
    if not _string_list(refs.get("release_decision_packet_v4_refs")):
        problems.append("required_source_references.release_decision_packet_v4_refs must be non-empty")
    if not _string_list(refs.get("inactive_guardrail_placeholder_fixture_refs")):
        problems.append("required_source_references.inactive_guardrail_placeholder_fixture_refs must be non-empty")


def _validate_outcome(value: Any, problems: list[str]) -> None:
    row = value if isinstance(value, Mapping) else {}
    if row.get("go_no_go_outcome") not in {"NO_GO", "GO_WITH_CAVEATS"}:
        problems.append("release_outcome_handling.go_no_go_outcome must be NO_GO or GO_WITH_CAVEATS")
    if not _text(row.get("agent_expected_outcome")):
        problems.append("release_outcome_handling.agent_expected_outcome is required")
    if row.get("activation_allowed") is not False:
        problems.append("release_outcome_handling.activation_allowed must be false")


def _validate_hold_rows(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"unresolved_hold_propagation[{index}]"
        for key in ("candidate_id", "hold_id", "reason", "owner_placeholder"):
            if not _text(row.get(key)):
                problems.append(f"{prefix}.{key} is required")
        if row.get("hold_status") != "unresolved_hold_propagated":
            problems.append(f"{prefix}.hold_status must be unresolved_hold_propagated")
        if row.get("blocks_go") is not True:
            problems.append(f"{prefix}.blocks_go must be true")


def _validate_display_rows(value: Any, field: str, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"{field}[{index}]"
        if not _text(row.get("display_text")):
            problems.append(f"{prefix}.display_text is required")
        if row.get("display_required") is not True:
            problems.append(f"{prefix}.display_required must be true")


def _validate_placeholder_checks(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"guardrail_placeholder_checks[{index}]"
        for key in ("placeholder_id", "guardrail_bundle_id", "placeholder_status"):
            if not _text(row.get(key)):
                problems.append(f"{prefix}.{key} is required")
        if row.get("placeholder_status") != "inactive_placeholder_only":
            problems.append(f"{prefix}.placeholder_status must be inactive_placeholder_only")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")


def _validate_rollback_rows(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"rollback_owner_placeholders[{index}]"
        if not _text(row.get("candidate_or_placeholder_id")):
            problems.append(f"{prefix}.candidate_or_placeholder_id is required")
        if not _text(row.get("rollback_owner_placeholder")):
            problems.append(f"{prefix}.rollback_owner_placeholder is required")
        if row.get("owner_assignment_status") != "placeholder_pending_manual_assignment":
            problems.append(f"{prefix}.owner_assignment_status must be placeholder_pending_manual_assignment")
        if row.get("active_state_changed") is not False:
            problems.append(f"{prefix}.active_state_changed must be false")


def _validate_handoff_rows(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"manual_handoff_reminders[{index}]"
        if not _text(row.get("reminder_id")):
            problems.append(f"{prefix}.reminder_id is required")
        if row.get("handoff_status") != "pending_manual_handoff":
            problems.append(f"{prefix}.handoff_status must be pending_manual_handoff")
        if row.get("acknowledgement_required") is not True:
            problems.append(f"{prefix}.acknowledgement_required must be true")


def _validate_smoke_expectations(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    ids = {_text(row.get("expectation_id")) for row in rows}
    missing = sorted(_REQUIRED_EXPECTATION_IDS - ids)
    if missing:
        problems.append("smoke_expectations missing required expectation ids: " + ", ".join(missing))
    for index, row in enumerate(rows):
        prefix = f"smoke_expectations[{index}]"
        if not _text(row.get("expectation_id")):
            problems.append(f"{prefix}.expectation_id is required")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")
        if not _text(row.get("expected_result")):
            problems.append(f"{prefix}.expected_result is required")


def _hold_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": _text(row.get("candidate_id")),
        "hold_id": _text(row.get("hold_id"), "unidentified-hold"),
        "reason": _text(row.get("reason"), "Unresolved fixture hold remains."),
        "owner_placeholder": _text(row.get("owner_placeholder"), "TBD_REVIEWER"),
        "hold_status": "unresolved_hold_propagated",
        "blocks_go": True,
    }


def _display_row(prefix: str, value: str) -> dict[str, Any]:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return {
        "display_id": f"{prefix}-{digest}",
        "display_text": value,
        "display_required": True,
    }


def _placeholder_check(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "placeholder_id": _text(row.get("placeholder_id")),
        "guardrail_bundle_id": _text(row.get("guardrail_bundle_id")),
        "placeholder_status": "inactive_placeholder_only",
        "activation_allowed": False,
        "expected_agent_behavior": "treat_as_placeholder_and_do_not_activate",
    }


def _rollback_placeholders(decision: Mapping[str, Any], placeholders: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _mapping_sequence(decision.get("rollback_owner_placeholders")):
        rows.append(
            {
                "candidate_or_placeholder_id": _text(row.get("candidate_id")),
                "rollback_owner_placeholder": _text(row.get("rollback_owner_placeholder"), "TBD_ROLLBACK_OWNER"),
                "rollback_decision_placeholder": _text(row.get("rollback_decision_placeholder"), "TBD_AFTER_REVIEW"),
                "owner_assignment_status": "placeholder_pending_manual_assignment",
                "active_state_changed": False,
            }
        )
    for row in placeholders:
        rows.append(
            {
                "candidate_or_placeholder_id": _text(row.get("placeholder_id")),
                "rollback_owner_placeholder": _text(row.get("rollback_owner_placeholder"), "TBD_ROLLBACK_OWNER"),
                "rollback_decision_placeholder": "TBD_AFTER_REVIEW",
                "owner_assignment_status": "placeholder_pending_manual_assignment",
                "active_state_changed": False,
            }
        )
    return rows


def _manual_handoff_reminders() -> list[dict[str, Any]]:
    return [
        {
            "reminder_id": "manual-handoff-release-reviewer",
            "handoff_status": "pending_manual_handoff",
            "acknowledgement_required": True,
            "reminder": "Human release reviewer must reconcile no-go holds before any later activation task.",
        },
        {
            "reminder_id": "manual-handoff-operator",
            "handoff_status": "pending_manual_handoff",
            "acknowledgement_required": True,
            "reminder": "Operator must use only the exact offline validation command listed in this packet.",
        },
    ]


def _smoke_expectations(recommendation: str) -> list[dict[str, Any]]:
    return [
        {
            "expectation_id": "go-no-go-outcome-handling",
            "expected_result": recommendation,
            "activation_allowed": False,
        },
        {
            "expectation_id": "inactive-guardrail-placeholder-checks",
            "expected_result": "all_placeholders_remain_inactive",
            "activation_allowed": False,
        },
        {
            "expectation_id": "unresolved-hold-propagation",
            "expected_result": "unresolved_holds_are_preserved_and_block_go",
            "activation_allowed": False,
        },
        {
            "expectation_id": "source-freshness-caveat-display",
            "expected_result": "source_freshness_caveats_are_user_visible",
            "activation_allowed": False,
        },
        {
            "expectation_id": "agent-api-compatibility-checks",
            "expected_result": "agent_api_compatibility_notes_are_user_visible",
            "activation_allowed": False,
        },
        {
            "expectation_id": "rollback-owner-placeholder-checks",
            "expected_result": "rollback_owners_remain_placeholder_pending_manual_assignment",
            "activation_allowed": False,
        },
        {
            "expectation_id": "manual-handoff-reminders",
            "expected_result": "manual_handoff_acknowledgement_required",
            "activation_allowed": False,
        },
        {
            "expectation_id": "offline-validation-command-exactness",
            "expected_result": "daemon_self_test_only",
            "activation_allowed": False,
        },
    ]


def _required_source_references(source_fixture: Mapping[str, Any], placeholders: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    release_refs = _string_list(source_fixture.get("release_decision_packet_v4_refs"))
    if not release_refs:
        release_refs = _string_list(source_fixture.get("source_fixture_refs"))
    placeholder_refs = _string_list(source_fixture.get("inactive_guardrail_placeholder_fixture_refs"))
    if not placeholder_refs:
        placeholder_refs = [_text(row.get("placeholder_id")) for row in placeholders if _text(row.get("placeholder_id"))]
    return {
        "release_decision_packet_v4_refs": release_refs,
        "inactive_guardrail_placeholder_fixture_refs": placeholder_refs,
    }


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
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
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _scan_for_forbidden_payload(child, f"{path}[{index}]", problems)
    elif isinstance(value, str) and _FORBIDDEN_TEXT_RE.search(value):
        problems.append(f"{path} contains a prohibited activation, live, official-action, private-artifact, or guarantee claim")
