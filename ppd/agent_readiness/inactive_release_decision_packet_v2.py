"""Inactive release decision packet v2 for offline PP&D release review.

This module consumes the fixture-only offline release reviewer disposition
intake packet v2 and produces a deterministic inactive decision artifact. It
performs no promotion, source crawling, DevHub access, prompt mutation, release
state update, fixture mutation, or official PP&D action.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from ppd.agent_readiness.offline_release_reviewer_disposition_intake_packet_v2 import (
    PACKET_TYPE as INTAKE_PACKET_TYPE,
    assert_valid_offline_release_reviewer_disposition_intake_packet_v2,
)

PACKET_TYPE = "ppd.inactive_release_decision_packet.v2"

DEFAULT_OFFLINE_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
    ("python3", "-m", "pytest", "ppd/tests/test_inactive_release_decision_packet_v2.py"),
)

_APPROVE_INTAKE_DECISION = "approved_for_offline_review"
_HOLD_INTAKE_DECISIONS = {"blocked", "deferred", "no_go"}
_BLOCKING_CARRY_FORWARD_STATUSES = {"blocked", "deferred", "escalated"}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_artifact_mutation",
    "active_fixture_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "apply_release",
    "fixture_promotion_enabled",
    "guardrail_mutation_enabled",
    "mutates_agent_state",
    "mutates_fixtures",
    "mutates_guardrails",
    "mutates_processes",
    "mutates_prompts",
    "mutates_release_state",
    "promotes_fixtures",
    "release_state_update_enabled",
}

_ACTIVE_MUTATION_NAME_RE = re.compile(
    r"(^|_)(active_)?(artifact|prompt|release_state|fixture|agent_state)_(mutation|mutating|update|change|promotion|write)(_|$)|"
    r"(^|_)(mutates|updates|changes|promotes)_(artifact|prompt|prompts|release_state|fixtures|agent_state)(_|$)",
    re.IGNORECASE,
)

_FORBIDDEN_FIELD_NAME_RE = re.compile(
    r"(auth[_-]?state|browser[_-]?(artifact|state)?|cookie|credential|download(ed)?|har|private|raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|session[_-]?(artifact|state|storage)?|storage[_-]?state|token|trace)",
    re.IGNORECASE,
)

_FORBIDDEN_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth[_ -]?state|browser[_ -]?state|cookie|credential|har\b|password|private[_ -]?(artifact|file|path|value)|"
    r"raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|downloaded[_ -]?(data|document|pdf)|"
    r"screenshot|session[_ -]?(artifact|state|storage)?|storage[_ -]?state|token|trace[_ -]?(file|zip)?)|"
    r"\b(live\s+(crawl|browser|devhub|execution|processor|promotion|run)|crawl\s+live|access\s+devhub|"
    r"promoted\s+(fixtures|release|to)|release\s+(complete|completed|state\s+updated)|official\s+action\s+performed|"
    r"permit\s+will\s+be\s+(approved|issued)|approval\s+is\s+guaranteed|guaranteed\s+(approval|issuance|permit\s+outcome)|"
    r"payment|pay\s+(the\s+)?fee|submit(ted|s|ting)?\b|submission|schedule\s+(the\s+)?inspection|"
    r"cancel\s+(the\s+)?inspection|certif(y|ication)|upload(s|ed|ing)?\b)\b",
    re.IGNORECASE,
)

_COMMAND_FORBIDDEN_RE = re.compile(r"\b(live|crawl|devhub|playwright|browser|network|auth|session)\b", re.IGNORECASE)


@dataclass(frozen=True)
class InactiveReleaseDecisionIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class InactiveReleaseDecisionValidationResult:
    ok: bool
    issues: tuple[InactiveReleaseDecisionIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "issues": [issue.as_dict() for issue in self.issues]}


def build_inactive_release_decision_packet_v2(
    intake_packet: Mapping[str, Any],
    *,
    packet_id: str = "fixture-inactive-release-decision-packet-v2",
    validation_commands: Sequence[Sequence[str]] = DEFAULT_OFFLINE_VALIDATION_COMMANDS,
) -> dict[str, Any]:
    """Build a deterministic inactive decision packet from intake packet v2."""

    assert_valid_offline_release_reviewer_disposition_intake_packet_v2(intake_packet)
    _raise_for_unsafe_content(intake_packet)

    decision_rows = _decision_rows(intake_packet)
    blocked_reasons = _blocked_release_reasons(intake_packet, decision_rows)
    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": packet_id,
        "fixture_only": True,
        "inactive_release_decision": True,
        "source_intake_packet": {
            "packet_type": INTAKE_PACKET_TYPE,
            "packet_id": str(intake_packet.get("packet_id") or "offline-release-reviewer-disposition-intake-v2"),
        },
        "decision_rows": decision_rows,
        "promotion_preconditions": _promotion_preconditions(blocked_reasons),
        "blocked_release_reasons": blocked_reasons,
        "reviewer_signoff_placeholders": _reviewer_signoff_placeholders(intake_packet),
        "prerequisite_validation_replay_inventory": _validation_replay_inventory(validation_commands),
        "rollback_plan_references": _rollback_plan_references(intake_packet),
        "offline_validation_commands": [list(command) for command in validation_commands],
        "non_promotion_attestations": {
            "promotes_fixtures": False,
            "changes_prompts": False,
            "mutates_guardrails": False,
            "mutates_processes": False,
            "mutates_agent_state": False,
            "updates_release_state": False,
            "uses_live_sources": False,
            "accesses_devhub": False,
            "performs_official_actions": False,
        },
    }
    assert_valid_inactive_release_decision_packet_v2(packet)
    return packet


def validate_inactive_release_decision_packet_v2(packet: Mapping[str, Any]) -> InactiveReleaseDecisionValidationResult:
    issues: list[InactiveReleaseDecisionIssue] = []

    if packet.get("packet_type") != PACKET_TYPE:
        issues.append(InactiveReleaseDecisionIssue("invalid_packet_type", "packet_type", f"packet_type must be {PACKET_TYPE}"))
    if packet.get("fixture_only") is not True:
        issues.append(InactiveReleaseDecisionIssue("fixture_only_required", "fixture_only", "fixture_only must be true"))
    if packet.get("inactive_release_decision") is not True:
        issues.append(InactiveReleaseDecisionIssue("inactive_release_decision_required", "inactive_release_decision", "inactive release decision flag must be true"))

    for field in (
        "decision_rows",
        "promotion_preconditions",
        "blocked_release_reasons",
        "reviewer_signoff_placeholders",
        "prerequisite_validation_replay_inventory",
        "rollback_plan_references",
        "offline_validation_commands",
    ):
        if not _mapping_or_command_rows(packet.get(field), field):
            issues.append(InactiveReleaseDecisionIssue("missing_required_rows", field, f"{field} must be a non-empty list"))

    _validate_decision_rows(packet.get("decision_rows"), issues)
    _validate_required_decision_coverage(packet.get("decision_rows"), issues)
    _validate_preconditions(packet.get("promotion_preconditions"), issues)
    _validate_blocked_reasons(packet.get("blocked_release_reasons"), issues)
    _validate_signoffs(packet.get("reviewer_signoff_placeholders"), issues)
    _validate_replay_inventory(packet.get("prerequisite_validation_replay_inventory"), issues)
    _validate_commands(packet.get("offline_validation_commands"), issues)
    _validate_non_promotion_attestations(packet.get("non_promotion_attestations"), issues)
    _scan_for_unsafe_content(packet, "", issues)

    return InactiveReleaseDecisionValidationResult(not issues, tuple(issues))


def assert_valid_inactive_release_decision_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_release_decision_packet_v2(packet)
    if not result.ok:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in result.issues)
        raise ValueError(f"inactive release decision packet v2 validation failed: {formatted}")


def _decision_rows(intake_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, reviewer_row in enumerate(_mapping_rows(intake_packet.get("reviewer_decision_rows"))):
        intake_decision = str(reviewer_row.get("decision") or "").strip()
        decision = "approve" if intake_decision == _APPROVE_INTAKE_DECISION else "hold"
        rows.append(
            {
                "decision_row_id": f"inactive-decision-row-{index + 1}",
                "reviewer_id": str(reviewer_row.get("reviewer_id") or ""),
                "intake_decision": intake_decision,
                "decision": decision,
                "deterministic_rule": "approved_for_offline_review maps to approve; blocked, deferred, and no_go map to hold",
                "rationale": str(reviewer_row.get("rationale") or ""),
                "citations": _citations(reviewer_row),
            }
        )
    return rows


def _promotion_preconditions(blocked_reasons: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    blocker_status = "pending" if blocked_reasons else "ready_for_manual_review"
    return [
        {
            "precondition_id": "precondition-offline-validation-replay",
            "description": "Offline validation commands must be replayed from committed fixtures before any separate operator decision.",
            "status": "pending",
            "required_before": "any_separate_operator_release_decision",
            "citations": ["fixture:offline-validation-command-inventory"],
        },
        {
            "precondition_id": "precondition-blocker-reconciliation",
            "description": "Every hold row and carry-forward blocker must be reconciled outside this inactive fixture artifact.",
            "status": blocker_status,
            "required_before": "any_separate_operator_release_decision",
            "citations": ["fixture:blocked-release-reasons"],
        },
        {
            "precondition_id": "precondition-reviewer-signoffs",
            "description": "Reviewer signoff placeholders must be filled by humans in a separate authorized review path.",
            "status": "pending",
            "required_before": "any_separate_operator_release_decision",
            "citations": ["fixture:reviewer-signoff-placeholders"],
        },
    ]


def _blocked_release_reasons(intake_packet: Mapping[str, Any], decision_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    for row in decision_rows:
        if row.get("decision") == "hold":
            reasons.append(
                {
                    "reason_id": f"blocked-{row.get('decision_row_id')}",
                    "source": "reviewer_decision_rows",
                    "reason": f"Reviewer disposition {row.get('intake_decision')} maps to hold for inactive release decision packet v2.",
                    "owner_placeholder": str(row.get("reviewer_id") or "reviewer"),
                    "citations": list(row.get("citations") or []),
                }
            )

    for index, blocker in enumerate(_mapping_rows(intake_packet.get("unresolved_blocker_carry_forward"))):
        if str(blocker.get("carry_forward_status") or "") in _BLOCKING_CARRY_FORWARD_STATUSES:
            reasons.append(
                {
                    "reason_id": f"blocked-carry-forward-{index + 1}",
                    "source": "unresolved_blocker_carry_forward",
                    "reason": str(blocker.get("carry_forward_reason") or "carry-forward blocker remains open"),
                    "owner_placeholder": str(blocker.get("carry_forward_owner") or "reviewer"),
                    "citations": _citations(blocker),
                }
            )

    for index, placeholder in enumerate(_mapping_rows(intake_packet.get("no_go_reason_placeholders"))):
        reasons.append(
            {
                "reason_id": f"blocked-no-go-placeholder-{index + 1}",
                "source": "no_go_reason_placeholders",
                "reason": str(placeholder.get("reason_placeholder") or "manual no-go reason placeholder"),
                "owner_placeholder": str(placeholder.get("applies_to_decision") or "manual reviewer"),
                "citations": _citations(placeholder),
            }
        )
    return _dedupe_by_id(reasons, "reason_id")


def _reviewer_signoff_placeholders(intake_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, reviewer_row in enumerate(_mapping_rows(intake_packet.get("reviewer_decision_rows"))):
        reviewer_id = str(reviewer_row.get("reviewer_id") or f"reviewer-{index + 1}")
        rows.append(
            {
                "signoff_id": f"signoff-{index + 1}",
                "reviewer_id": reviewer_id,
                "placeholder": "pending_manual_reviewer_signoff",
                "required_before": "any_separate_operator_release_decision",
                "citations": _citations(reviewer_row),
            }
        )
    return rows


def _validation_replay_inventory(commands: Sequence[Sequence[str]]) -> list[dict[str, Any]]:
    return [
        {
            "replay_id": f"offline-validation-command-{index + 1}",
            "command": list(command),
            "mode": "offline_fixture_replay",
            "expected_result": "zero_exit",
            "citations": ["fixture:offline-validation-command-inventory"],
        }
        for index, command in enumerate(commands)
    ]


def _rollback_plan_references(intake_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, acknowledgement in enumerate(_mapping_rows(intake_packet.get("rollback_readiness_acknowledgements"))):
        rows.append(
            {
                "rollback_ref_id": f"rollback-reference-{index + 1}",
                "reviewer_id": str(acknowledgement.get("reviewer_id") or "reviewer"),
                "reference_type": "rollback_readiness_acknowledgement",
                "status": "reference_only_not_activated",
                "citations": _citations(acknowledgement),
            }
        )
    return rows


def _validate_decision_rows(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"decision_rows[{index}]"
        if row.get("decision") not in {"approve", "hold"}:
            issues.append(InactiveReleaseDecisionIssue("invalid_decision", f"{path}.decision", "decision must be approve or hold"))
        if row.get("intake_decision") == _APPROVE_INTAKE_DECISION and row.get("decision") != "approve":
            issues.append(InactiveReleaseDecisionIssue("invalid_approve_mapping", f"{path}.decision", "approved intake rows must map to approve"))
        if row.get("intake_decision") in _HOLD_INTAKE_DECISIONS and row.get("decision") != "hold":
            issues.append(InactiveReleaseDecisionIssue("invalid_hold_mapping", f"{path}.decision", "blocked, deferred, and no_go intake rows must map to hold"))
        if not _has_citation(row.get("citations")):
            issues.append(InactiveReleaseDecisionIssue("uncited_decision_row", f"{path}.citations", "decision row must cite fixture evidence"))


def _validate_required_decision_coverage(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    decisions = {str(row.get("decision") or "") for row in _mapping_rows(value)}
    if "approve" not in decisions:
        issues.append(InactiveReleaseDecisionIssue("missing_approve_decision_row", "decision_rows", "decision rows must include at least one approve row"))
    if "hold" not in decisions:
        issues.append(InactiveReleaseDecisionIssue("missing_hold_decision_row", "decision_rows", "decision rows must include at least one hold row"))


def _validate_preconditions(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"promotion_preconditions[{index}]"
        if not _text(row.get("precondition_id")):
            issues.append(InactiveReleaseDecisionIssue("missing_promotion_precondition", f"{path}.precondition_id", "precondition_id is required"))
        if row.get("status") not in {"pending", "ready_for_manual_review"}:
            issues.append(InactiveReleaseDecisionIssue("invalid_precondition_status", f"{path}.status", "inactive packet preconditions may only be pending or ready_for_manual_review"))
        if row.get("required_before") != "any_separate_operator_release_decision":
            issues.append(InactiveReleaseDecisionIssue("invalid_precondition_gate", f"{path}.required_before", "precondition must gate separate operator release decision"))
        if not _has_citation(row.get("citations")):
            issues.append(InactiveReleaseDecisionIssue("uncited_precondition", f"{path}.citations", "precondition must cite fixture evidence"))


def _validate_blocked_reasons(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"blocked_release_reasons[{index}]"
        if not _text(row.get("reason_id")) or not _text(row.get("reason")):
            issues.append(InactiveReleaseDecisionIssue("invalid_blocked_release_reason", path, "blocked release reason requires reason_id and reason"))
        if not _has_citation(row.get("citations")):
            issues.append(InactiveReleaseDecisionIssue("uncited_blocked_release_reason", f"{path}.citations", "blocked release reason must cite fixture evidence"))


def _validate_signoffs(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"reviewer_signoff_placeholders[{index}]"
        if row.get("placeholder") != "pending_manual_reviewer_signoff":
            issues.append(InactiveReleaseDecisionIssue("invalid_signoff_placeholder", f"{path}.placeholder", "signoff placeholder must remain pending"))
        if row.get("required_before") != "any_separate_operator_release_decision":
            issues.append(InactiveReleaseDecisionIssue("invalid_signoff_gate", f"{path}.required_before", "signoff must gate separate operator release decision"))
        if not _has_citation(row.get("citations")):
            issues.append(InactiveReleaseDecisionIssue("uncited_signoff", f"{path}.citations", "signoff placeholder must cite fixture evidence"))


def _validate_replay_inventory(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"prerequisite_validation_replay_inventory[{index}]"
        if row.get("mode") != "offline_fixture_replay":
            issues.append(InactiveReleaseDecisionIssue("invalid_replay_mode", f"{path}.mode", "replay inventory must be offline_fixture_replay"))
        _validate_single_command(row.get("command"), f"{path}.command", issues)


def _validate_commands(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return
    for index, command in enumerate(value):
        _validate_single_command(command, f"offline_validation_commands[{index}]", issues)


def _validate_single_command(value: Any, path: str, issues: list[InactiveReleaseDecisionIssue]) -> None:
    if not _string_sequence(value):
        issues.append(InactiveReleaseDecisionIssue("invalid_offline_validation_command", path, "validation command must be an argv string list"))
        return
    command_text = " ".join(value)
    if _COMMAND_FORBIDDEN_RE.search(command_text):
        issues.append(InactiveReleaseDecisionIssue("unsafe_offline_validation_command", path, "validation command must not invoke live, crawler, DevHub, browser, network, auth, or session paths"))


def _validate_non_promotion_attestations(value: Any, issues: list[InactiveReleaseDecisionIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(InactiveReleaseDecisionIssue("missing_non_promotion_attestations", "non_promotion_attestations", "non-promotion attestations are required"))
        return
    required_false = (
        "promotes_fixtures",
        "changes_prompts",
        "mutates_guardrails",
        "mutates_processes",
        "mutates_agent_state",
        "updates_release_state",
        "uses_live_sources",
        "accesses_devhub",
        "performs_official_actions",
    )
    for key in required_false:
        if value.get(key) is not False:
            issues.append(InactiveReleaseDecisionIssue("non_promotion_attestation_not_false", f"non_promotion_attestations.{key}", f"{key} must be false"))


def _raise_for_unsafe_content(value: Any) -> None:
    issues: list[InactiveReleaseDecisionIssue] = []
    _scan_for_unsafe_content(value, "", issues)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in issues)
        raise ValueError(f"unsafe inactive release decision content: {formatted}")


def _scan_for_unsafe_content(value: Any, path: str, issues: list[InactiveReleaseDecisionIssue]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if (name in _MUTATION_KEYS or _ACTIVE_MUTATION_NAME_RE.search(name)) and _active_flag(child):
            issues.append(InactiveReleaseDecisionIssue("active_mutation_flag", child_path, "active mutation or fixture promotion flags are not allowed"))
        if name and not name.startswith("no_") and _FORBIDDEN_FIELD_NAME_RE.search(name) and _present_value(child):
            issues.append(InactiveReleaseDecisionIssue("private_or_raw_artifact_field", child_path, "packet fields must not carry private/authenticated browser artifacts, screenshots, traces, HAR files, raw crawl/PDF data, or downloads"))
        if isinstance(child, str) and _FORBIDDEN_TEXT_RE.search(child):
            issues.append(InactiveReleaseDecisionIssue("unsafe_packet_text", child_path, "packet text must not reference private artifacts, raw data, live execution, guarantees, consequential actions, or active release mutation"))


def _mapping_or_command_rows(value: Any, field: str) -> bool:
    if field == "offline_validation_commands":
        return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and any(_string_sequence(item) for item in value)
    return bool(_mapping_rows(value))


def _mapping_rows(value: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _citations(row: Mapping[str, Any]) -> list[str]:
    citations = row.get("citations")
    if isinstance(citations, str) and citations.strip():
        return [citations.strip()]
    if isinstance(citations, Sequence) and not isinstance(citations, (str, bytes, bytearray)):
        result: list[str] = []
        for item in citations:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
            elif isinstance(item, Mapping):
                for key in ("citation", "fixture_id", "source_evidence_id", "source_id", "path", "url", "canonical_url"):
                    text = item.get(key)
                    if isinstance(text, str) and text.strip():
                        result.append(text.strip())
                        break
        if result:
            return result
    return ["fixture:offline-release-reviewer-disposition-intake-v2"]


def _has_citation(value: Any) -> bool:
    return bool(_citations({"citations": value}))


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = str(key) if not path else f"{path}.{key}"
            yield from _walk(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _path_name(path: str) -> str:
    if not path:
        return ""
    return path.rsplit(".", 1)[-1].split("[", 1)[0]


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False


def _present_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and all(isinstance(item, str) and item.strip() for item in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _dedupe_by_id(rows: Sequence[dict[str, Any]], id_field: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        row_id = str(row.get(id_field) or "")
        if row_id and row_id not in seen:
            seen.add(row_id)
            result.append(row)
    return result
