"""Validation for supervised offline release rehearsal v1 packets.

The validator is intentionally fixture-first. It accepts only offline rehearsal
metadata and rejects private/authenticated artifacts, raw crawl output, live
execution claims, official outcome guarantees, consequential action language,
and active mutation flags.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


PACKET_TYPE = "ppd.supervised_offline_release_rehearsal.v1"

REQUIRED_ATTESTATIONS = (
    "fixture_only",
    "supervised_offline_only",
    "no_private_or_authenticated_artifacts",
    "no_raw_crawl_pdf_session_or_browser_data",
    "no_live_execution_or_promotion",
    "no_legal_or_permitting_outcome_guarantees",
    "no_consequential_action_language",
    "no_active_mutation_flags",
)

FORBIDDEN_KEYS = {
    "access_token",
    "archive_artifact_ref",
    "auth",
    "auth_state",
    "authenticated_artifact",
    "authorization",
    "browser_context",
    "browser_state",
    "cookie",
    "credentials",
    "download_path",
    "downloaded_document_path",
    "har",
    "local_path",
    "password",
    "private_artifact",
    "private_path",
    "raw_body",
    "raw_crawl",
    "raw_crawl_output",
    "raw_data",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "secret",
    "session",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "trace_path",
    "warc_path",
}

FORBIDDEN_TRUE_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "browser_execution_performed",
    "devhub_execution_performed",
    "guardrail_mutation",
    "live_actions_performed",
    "live_crawl_executed",
    "live_execution_performed",
    "live_network_called",
    "official_action_performed",
    "prompt_mutation",
    "promotion_executed",
    "release_state_mutation",
    "source_mutation",
    "submitted_to_devhub",
    "surface_registry_mutation",
    "uses_authenticated_session",
}

PRIVATE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|"
    r"(auth(?:enticated)?[_ -]?(artifact|session|state)?|browser[_ -]?(context|data|state)|cookie|credential|"
    r"downloaded[_ -]?document|har|password|private[_ -]?(artifact|path)|raw[_ -]?(body|crawl|data|html|pdf)|"
    r"session[_ -]?(data|state|storage)?|screenshot|secret|storage[_ -]?state|token|trace(?:\.zip)?|warc)",
    re.IGNORECASE,
)

LIVE_OR_PROMOTION_CLAIM_RE = re.compile(
    r"\b(live\s+(execution|run|crawl|network\s+call)\s+(completed|executed|performed|ran)|"
    r"(executed|performed)\s+(the\s+)?live\s+(release|crawl|run)|"
    r"promot(?:e|ed|ion)\s+(to\s+)?(production|live|active)|release\s+promoted|official\s+release\s+(completed|executed))\b",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will\s+be\s+(approved|accepted|issued|legal|compliant)|"
    r"permit\s+(approval|issuance)\s+is\s+(certain|guaranteed)|ensure\s+(approval|issuance|compliance)|"
    r"no\s+legal\s+risk|legally\s+binding|safe\s+harbor)\b",
    re.IGNORECASE,
)

CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(click\s+submit|submit\s+(the\s+)?(permit|application|request)|"
    r"upload\s+(correction|document|file|plans?)|pay\s+(fee|fees|invoice)|enter\s+payment|"
    r"schedule\s+(an\s+)?inspection|certify\s+(the\s+)?(application|acknowledgement)|"
    r"sign\s+(the\s+)?(application|certification)|cancel\s+(permit|inspection|application)|"
    r"withdraw\s+(permit|application|request)|purchase\s+(permit|trade\s+permit))\b",
    re.IGNORECASE,
)

MUTATION_TEXT_RE = re.compile(
    r"\b(active\s+)?(source|surface[-_ ]registry|guardrail|prompt|release[-_ ]state|agent[-_ ]state)\s+mutation\b",
    re.IGNORECASE,
)


class SupervisedOfflineReleaseRehearsalV1Error(ValueError):
    """Raised when a supervised offline release rehearsal packet is invalid."""


def load_supervised_offline_release_rehearsal_fixture(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise SupervisedOfflineReleaseRehearsalV1Error("fixture must contain a JSON object")
    return packet


def validate_supervised_offline_release_rehearsal_v1(packet: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    problems.extend(_walk_safety_errors(packet, "$"))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("supervised") is not True:
        problems.append("supervised must be true")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                problems.append(f"attestations.{name} must be true")

    steps = _section(packet, "rehearsal_steps", "cited_rehearsal_steps", "cited_dry_run_release_steps")
    if not steps:
        problems.append("rehearsal_steps must be a non-empty list")
    for index, step in enumerate(steps):
        path = f"rehearsal_steps[{index}]"
        _require_non_empty_string(step, "step_id", path, problems)
        if not _citations(step):
            problems.append(f"{path}.citations must be a non-empty list of strings")

    blockers = _section(packet, "blocker_handling", "manual_review_blockers", "blockers")
    if not blockers:
        problems.append("blocker_handling must be a non-empty list")
    for index, blocker in enumerate(blockers):
        path = f"blocker_handling[{index}]"
        _require_non_empty_string(blocker, "blocker_id", path, problems)
        if not (blocker.get("disposition") or blocker.get("handling") or blocker.get("status")):
            problems.append(f"{path} must include disposition, handling, or status")
        if not _citations(blocker):
            problems.append(f"{path}.citations must be a non-empty list of strings")

    artifacts = _section(packet, "expected_fixture_artifacts", "expected_fixture_only_artifacts")
    if not artifacts:
        problems.append("expected_fixture_artifacts must be a non-empty list")
    for index, artifact in enumerate(artifacts):
        path = f"expected_fixture_artifacts[{index}]"
        _require_non_empty_string(artifact, "artifact_id", path, problems)
        if artifact.get("fixture_only") is not True:
            problems.append(f"{path}.fixture_only must be true")
        if not _citations(artifact):
            problems.append(f"{path}.citations must be a non-empty list of strings")

    checkpoints = _section(packet, "rollback_checkpoints")
    if not checkpoints:
        problems.append("rollback_checkpoints must be a non-empty list")
    for index, checkpoint in enumerate(checkpoints):
        path = f"rollback_checkpoints[{index}]"
        _require_non_empty_string(checkpoint, "checkpoint_id", path, problems)
        if not (checkpoint.get("restore_action") or checkpoint.get("checkpoint") or checkpoint.get("action")):
            problems.append(f"{path} must include restore_action, checkpoint, or action")
        if not _citations(checkpoint):
            problems.append(f"{path}.citations must be a non-empty list of strings")

    commands = packet.get("validation_command_inventory")
    if not isinstance(commands, list) or not commands:
        problems.append("validation_command_inventory must be a non-empty list")
    else:
        for index, command in enumerate(commands):
            if not _is_command(command):
                problems.append(f"validation_command_inventory[{index}] must be a list of strings")

    return problems


def validate_supervised_offline_release_rehearsal(packet: Mapping[str, Any]) -> list[str]:
    return validate_supervised_offline_release_rehearsal_v1(packet)


def validate_rehearsal_packet(packet: Mapping[str, Any]) -> list[str]:
    return validate_supervised_offline_release_rehearsal_v1(packet)


def build_supervised_offline_release_rehearsal(packet: Mapping[str, Any]) -> dict[str, Any]:
    problems = validate_supervised_offline_release_rehearsal_v1(packet)
    if problems:
        raise SupervisedOfflineReleaseRehearsalV1Error("invalid supervised offline release rehearsal v1: " + "; ".join(problems))
    return dict(packet)


def supervised_offline_release_rehearsal_from_fixture(path: str | Path) -> dict[str, Any]:
    return build_supervised_offline_release_rehearsal(load_supervised_offline_release_rehearsal_fixture(path))


def _section(packet: Mapping[str, Any], *names: str) -> tuple[Mapping[str, Any], ...]:
    for name in names:
        value = packet.get(name)
        if isinstance(value, list):
            return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _citations(item: Mapping[str, Any]) -> list[str]:
    value = item.get("citations")
    if not isinstance(value, list):
        return []
    return [citation for citation in value if isinstance(citation, str) and citation]


def _require_non_empty_string(item: Mapping[str, Any], key: str, path: str, problems: list[str]) -> None:
    if not isinstance(item.get(key), str) or not item.get(key):
        problems.append(f"{path}.{key} must be a non-empty string")


def _is_command(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(part, str) and part for part in value)


def _walk_safety_errors(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized_key = key_text.lower()
            if normalized_key in FORBIDDEN_KEYS:
                problems.append(f"{child_path} is a forbidden private, authenticated, raw, session, PDF, or browser artifact key")
            if normalized_key in FORBIDDEN_TRUE_KEYS and nested is True:
                problems.append(f"{child_path} must not be true in a supervised offline release rehearsal")
            problems.extend(_walk_safety_errors(nested, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            problems.extend(_walk_safety_errors(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        if PRIVATE_TEXT_RE.search(value):
            problems.append(f"{path} contains private, authenticated, raw, session, PDF, or browser artifact text")
        if LIVE_OR_PROMOTION_CLAIM_RE.search(value):
            problems.append(f"{path} contains live execution or promotion claim text")
        if OUTCOME_GUARANTEE_RE.search(value):
            problems.append(f"{path} contains legal or permitting outcome guarantee text")
        if CONSEQUENTIAL_ACTION_RE.search(value):
            problems.append(f"{path} contains consequential action text")
        if MUTATION_TEXT_RE.search(value):
            problems.append(f"{path} contains active mutation flag text")
    return problems
