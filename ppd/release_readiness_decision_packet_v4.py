"""Fixture-first release readiness decision packet v4 validation for PP&D.

The v4 packet is an offline decision artifact. It records candidate references,
holds, caveats, compatibility notes, rollback ownership, smoke replay planning,
and validation commands without activating a release or storing private artifacts.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence

PACKET_VERSION = "release-readiness-decision-packet-v4"

OFFLINE_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "-m", "py_compile", "ppd/release_readiness_decision_packet_v4.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_release_readiness_decision_packet_v4.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

REQUIRED_SECTIONS: tuple[tuple[str, str, str], ...] = (
    ("promotion_candidate_references", "missing_promotion_candidate_references", "promotion candidate references are required"),
    ("go_no_go_recommendation", "missing_go_no_go_recommendation", "go/no-go recommendation is required"),
    ("unresolved_hold_inventory", "missing_unresolved_hold_inventory", "unresolved hold inventory is required"),
    ("source_freshness_caveats", "missing_source_freshness_caveats", "source freshness caveats are required"),
    ("agent_api_compatibility_notes", "missing_agent_api_compatibility_notes", "agent API compatibility notes are required"),
    ("rollback_owner_placeholders", "missing_rollback_owner_placeholders", "rollback owner placeholders are required"),
    ("post_decision_smoke_replay_plan", "missing_post_decision_smoke_replay_plan", "post-decision smoke replay plan is required"),
    ("validation_commands", "missing_validation_commands", "validation commands are required"),
)

PRIVATE_OR_SESSION_KEY_RE = re.compile(
    r"(auth[_-]?state|browser[_-]?(artifact|state)?|cookie|credential|download(ed)?|har|password|private|raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|session[_-]?(artifact|state|storage)?|storage[_-]?state|token|trace)",
    re.IGNORECASE,
)
ACTIVE_MUTATION_KEY_RE = re.compile(
    r"(^|_)(active_)?(artifact|fixture|guardrail|prompt|release|release_state|surface|surface_map|agent_state)_(activation|mutation|mutating|promotion|update|write)(_|$)|(^|_)(activates|mutates|promotes|updates|writes)_(artifacts|fixtures|guardrails|prompts|release|release_state|surface|surface_map|agent_state)(_|$)",
    re.IGNORECASE,
)
ACTIVE_ACTIVATION_KEY_RE = re.compile(
    r"(^|_)(activation|active_release|release_activation|production_release)_(complete|completed|enabled|performed|ready|succeeded|success)(_|$)|(^|_)(activates_release|enables_active_release)(_|$)",
    re.IGNORECASE,
)
PRIVATE_OR_SESSION_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|(auth[_ -]?state|browser[_ -]?(artifact|state)|cookies?|credentials?|downloaded[_ -]?(artifact|document|file|pdf)|har\b|password|private[_ -]?(artifact|file|path|value)|raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|screenshots?|session[_ -]?(artifact|state|storage)|storage[_ -]?state|tokens?|trace[_ -]?(file|zip)?)",
    re.IGNORECASE,
)
ACTIVE_ACTIVATION_TEXT_RE = re.compile(
    r"\b(active release enabled|activated release|activation completed|activation succeeded|production release enabled|release is active|released to production)\b",
    re.IGNORECASE,
)
OFFICIAL_ACTION_TEXT_RE = re.compile(
    r"\b(official action (completed|performed)|submitted (the )?(application|permit|payment)|submission completed|paid (the )?fee|payment completed|scheduled (an? )?inspection|cancell?ed (an? )?inspection|certified (the )?application|uploaded (corrections|plans|documents|files))\b",
    re.IGNORECASE,
)
GUARANTEE_TEXT_RE = re.compile(
    r"\b(guaranteed approval|guaranteed issuance|permit will be approved|permit will be issued|approval is guaranteed|issuance is guaranteed|legal advice|legal guarantee|permitting guarantee)\b",
    re.IGNORECASE,
)
NEGATED_TEXT_RE = re.compile(r"\b(no|not|never|without|does not|did not|must not|forbidden|disallowed|unchanged)\b", re.IGNORECASE)
COMMAND_FORBIDDEN_RE = re.compile(r"\b(live|crawl|devhub|playwright|browser|network|auth|session|promote|activate)\b", re.IGNORECASE)


@dataclass(frozen=True)
class DecisionPacketV4Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def build_release_readiness_decision_packet_v4() -> dict[str, Any]:
    packet = {
        "packet_version": PACKET_VERSION,
        "mode": "fixture-first-offline-only",
        "release_state_changed": False,
        "activation_performed": False,
        "active_mutation_performed": False,
        "promotion_candidate_references": [
            {
                "candidate_id": "inactive-guardrail-bundle-promotion-candidate-v4",
                "packet_ref": "ppd.agent_readiness.inactive_guardrail_bundle_promotion_candidate_v4",
                "candidate_status": "inactive_fixture_reference_only",
                "source_evidence_ids": ["fixture:inactive-guardrail-bundle-promotion-candidate-v4"],
            }
        ],
        "go_no_go_recommendation": {
            "recommendation": "no_go",
            "basis": "v4 records an offline decision hold until human review resolves all placeholders and caveats.",
            "release_allowed": False,
            "activation_allowed": False,
        },
        "unresolved_hold_inventory": [
            {
                "hold_id": "hold-source-freshness-and-human-review",
                "status": "unresolved",
                "owner_placeholder": "release_reviewer",
                "required_resolution": "Confirm source freshness caveats and reviewer disposition outside this packet.",
            }
        ],
        "source_freshness_caveats": [
            {
                "caveat_id": "source-freshness-caveat-1",
                "description": "Official source freshness must be verified by a later reviewed packet before any separate activation decision.",
                "staleness_risk": "unresolved",
            }
        ],
        "agent_api_compatibility_notes": [
            {
                "note_id": "agent-api-compatibility-note-1",
                "contract_ref": "ppd.agent_readiness.guardrail_api_contract",
                "compatibility_status": "requires_offline_smoke_replay",
                "mutation_required": False,
            }
        ],
        "rollback_owner_placeholders": [
            {
                "rollback_owner_role": "release_operator",
                "placeholder_status": "pending_human_assignment",
                "responsibility": "Retain current active release artifacts and discard this inactive decision packet if review fails.",
            }
        ],
        "post_decision_smoke_replay_plan": [
            {
                "smoke_replay_id": "post-decision-smoke-replay-v4",
                "command_ref": "offline-pytest-release-readiness-decision-packet-v4",
                "expected_result": "validation rejects incomplete or unsafe v4 packets before any separate release path.",
                "requires_network": False,
            }
        ],
        "validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
    }
    assert_valid_release_readiness_decision_packet_v4(packet)
    return packet


def validate_release_readiness_decision_packet_v4(packet: Mapping[str, Any]) -> list[DecisionPacketV4Issue]:
    issues: list[DecisionPacketV4Issue] = []
    if packet.get("packet_version") != PACKET_VERSION:
        issues.append(DecisionPacketV4Issue("invalid_packet_version", "$.packet_version", f"packet_version must be {PACKET_VERSION}"))
    if packet.get("release_state_changed") is not False:
        issues.append(DecisionPacketV4Issue("active_mutation_flag", "$.release_state_changed", "release_state_changed must be false"))
    if packet.get("activation_performed") is not False:
        issues.append(DecisionPacketV4Issue("active_activation_claim", "$.activation_performed", "activation_performed must be false"))
    if packet.get("active_mutation_performed") is not False:
        issues.append(DecisionPacketV4Issue("active_mutation_flag", "$.active_mutation_performed", "active_mutation_performed must be false"))

    for field, code, message in REQUIRED_SECTIONS:
        if _empty(packet.get(field)):
            issues.append(DecisionPacketV4Issue(code, f"$.{field}", message))

    _validate_go_no_go(packet.get("go_no_go_recommendation"), issues)
    _validate_validation_commands(packet.get("validation_commands"), issues)
    _scan_for_unsafe_content(packet, "$", issues)
    return issues


def assert_valid_release_readiness_decision_packet_v4(packet: Mapping[str, Any]) -> None:
    issues = validate_release_readiness_decision_packet_v4(packet)
    if issues:
        detail = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        raise ValueError(f"release readiness decision packet v4 validation failed: {detail}")


def _validate_go_no_go(value: Any, issues: list[DecisionPacketV4Issue]) -> None:
    if not isinstance(value, Mapping):
        return
    if value.get("recommendation") not in {"go", "no_go", "hold"}:
        issues.append(DecisionPacketV4Issue("invalid_go_no_go_recommendation", "$.go_no_go_recommendation.recommendation", "recommendation must be go, no_go, or hold"))
    if value.get("release_allowed") is not False or value.get("activation_allowed") is not False:
        issues.append(DecisionPacketV4Issue("active_activation_claim", "$.go_no_go_recommendation", "v4 fixture packet cannot allow release or activation"))


def _validate_validation_commands(value: Any, issues: list[DecisionPacketV4Issue]) -> None:
    if not isinstance(value, list) or not value:
        return
    for index, command in enumerate(value):
        path = f"$.validation_commands[{index}]"
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
            issues.append(DecisionPacketV4Issue("invalid_validation_command", path, "validation commands must be non-empty argv string lists"))
            continue
        if COMMAND_FORBIDDEN_RE.search(" ".join(command)):
            issues.append(DecisionPacketV4Issue("unsafe_validation_command", path, "validation commands must stay offline and avoid live, crawl, DevHub, browser, auth, session, promotion, or activation workflows"))


def _scan_for_unsafe_content(value: Any, path: str, issues: list[DecisionPacketV4Issue]) -> None:
    for child_path, key, child in _iter_nodes(value, path):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key and PRIVATE_OR_SESSION_KEY_RE.search(normalized_key) and _present(child):
            issues.append(DecisionPacketV4Issue("private_session_auth_artifact", child_path, "private/session/auth artifacts, screenshots, traces, HAR, raw captures, and downloaded documents are not allowed"))
        if normalized_key and ACTIVE_MUTATION_KEY_RE.search(normalized_key) and _active(child):
            issues.append(DecisionPacketV4Issue("active_mutation_flag", child_path, "active mutation flags are not allowed"))
        if normalized_key and ACTIVE_ACTIVATION_KEY_RE.search(normalized_key) and _active(child):
            issues.append(DecisionPacketV4Issue("active_activation_claim", child_path, "active activation claims are not allowed"))
        if isinstance(child, str) and not _negated(child):
            if PRIVATE_OR_SESSION_TEXT_RE.search(child):
                issues.append(DecisionPacketV4Issue("private_session_auth_artifact_text", child_path, "packet text must not reference private/session/auth artifacts"))
            if ACTIVE_ACTIVATION_TEXT_RE.search(child):
                issues.append(DecisionPacketV4Issue("active_activation_claim", child_path, "packet text must not claim active activation"))
            if OFFICIAL_ACTION_TEXT_RE.search(child):
                issues.append(DecisionPacketV4Issue("official_action_completion_claim", child_path, "official-action completion claims are not allowed"))
            if GUARANTEE_TEXT_RE.search(child):
                issues.append(DecisionPacketV4Issue("legal_or_permitting_guarantee", child_path, "legal or permitting guarantees are not allowed"))


def _iter_nodes(value: Any, path: str, key: str = "") -> Iterable[tuple[str, str, Any]]:
    yield path, key, value
    if isinstance(value, Mapping):
        for child_key, child in value.items():
            child_key_text = str(child_key)
            yield from _iter_nodes(child, f"{path}.{child_key_text}", child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _iter_nodes(child, f"{path}[{index}]", key)


def _empty(value: Any) -> bool:
    if value is None or value is False:
        return True
    if isinstance(value, (str, bytes, Sequence, Mapping, set, frozenset)):
        return len(value) == 0
    return False


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (Sequence, Mapping, set, frozenset)) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _active(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "activated", "complete", "completed", "enabled", "ready", "true", "yes"}
    if isinstance(value, (Sequence, Mapping, set, frozenset)) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False


def _negated(value: str) -> bool:
    return NEGATED_TEXT_RE.search(value[:96]) is not None


def clone_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(packet))
