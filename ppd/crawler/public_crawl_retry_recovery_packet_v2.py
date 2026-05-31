"""Offline validator for the PP&D public crawl retry/recovery packet v2.

This module is intentionally fixture-first. It validates committed packet data that
models crawler recovery decisions without performing crawl, archive, source,
processor, document, requirement, guardrail, DevHub, prompt, contract, or release
state mutations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

PACKET_VERSION = "public-crawl-retry-recovery-v2"

REQUIRED_SCENARIOS = frozenset(
    {
        "robots_policy_denial",
        "synthetic_policy_denial",
        "timeout_row",
        "redirect_changed",
        "content_type_skip",
        "too_large_skip",
        "processor_handoff_failure",
        "no_raw_body_archive_decision",
        "retry_backoff_plan",
        "reviewer_disposition_placeholder",
    }
)

FORBIDDEN_MUTATION_MARKERS = frozenset(
    {
        "network_access",
        "raw_download",
        "processor_execution",
        "active_crawler",
        "source_mutation",
        "archive_mutation",
        "document_mutation",
        "requirement_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "contract_mutation",
        "devhub_surface_mutation",
        "release_state_mutation",
    }
)

REQUIRED_OFFLINE_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/crawler/public_crawl_retry_recovery_packet_v2.py"),
    ("python3", "-m", "py_compile", "ppd/tests/test_public_crawl_retry_recovery_packet_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_public_crawl_retry_recovery_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

FORBIDDEN_ARTIFACT_KEY_FRAGMENTS = (
    "artifact",
    "auth_state",
    "browser_state",
    "cookie",
    "download",
    "har",
    "local_path",
    "raw_body",
    "screenshot",
    "session",
    "storage_state",
    "trace",
)

FORBIDDEN_ARTIFACT_VALUE_FRAGMENTS = (
    ".auth/",
    ".download",
    ".har",
    ".trace",
    "auth-state",
    "browser-state",
    "downloaded-artifact",
    "private-artifact",
    "raw-body",
    "session-state",
    "storage-state",
)

FORBIDDEN_CLAIM_FRAGMENTS = (
    "active crawler ran",
    "downloaded live",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legal guarantee",
    "live crawl completed",
    "live crawl evidence",
    "permitting guarantee",
    "raw body persisted",
)

ScenarioPredicate = Callable[[dict[str, Any]], bool]


def _retry_decision_is(expected: str) -> ScenarioPredicate:
    def predicate(scenario: dict[str, Any]) -> bool:
        retry_plan = scenario.get("retry_plan")
        return isinstance(retry_plan, dict) and retry_plan.get("decision") == expected

    return predicate


def _recovery_skip_reason_is(expected: str) -> ScenarioPredicate:
    def predicate(scenario: dict[str, Any]) -> bool:
        recovery_packet = scenario.get("recovery_packet")
        return isinstance(recovery_packet, dict) and recovery_packet.get("skip_reason") == expected

    return predicate


def _recovery_archive_decision_is(expected: str) -> ScenarioPredicate:
    def predicate(scenario: dict[str, Any]) -> bool:
        recovery_packet = scenario.get("recovery_packet")
        return isinstance(recovery_packet, dict) and recovery_packet.get("archive_decision") == expected

    return predicate


def _retry_plan_has_backoff(scenario: dict[str, Any]) -> bool:
    retry_plan = scenario.get("retry_plan")
    if not isinstance(retry_plan, dict):
        return False
    backoff_seconds = retry_plan.get("backoff_seconds")
    if not isinstance(backoff_seconds, list) or not backoff_seconds:
        return False
    return all(isinstance(value, int) and value > 0 for value in backoff_seconds)


REQUIRED_SCENARIO_PREDICATES: dict[str, tuple[tuple[str, ScenarioPredicate], ...]] = {
    "robots_policy_denial": (
        ("must model a robots/policy denial skip", _recovery_skip_reason_is("disallowed_by_robots_or_policy")),
        ("must not retry robots/policy denials", _retry_decision_is("do_not_retry")),
    ),
    "synthetic_policy_denial": (
        ("must model a local policy denial skip", _recovery_skip_reason_is("private_or_authenticated_boundary")),
        ("must not retry local policy denials", _retry_decision_is("do_not_retry")),
    ),
    "timeout_row": (
        ("must model a timeout skip", _recovery_skip_reason_is("timeout")),
        ("must include a timeout backoff plan", _retry_plan_has_backoff),
    ),
    "redirect_changed": (
        ("must model a redirect-change row", _recovery_skip_reason_is("redirect_changed")),
        ("must hold redirect changes for review", _retry_decision_is("do_not_retry_until_reviewed")),
    ),
    "content_type_skip": (
        ("must model an unsupported content-type skip", _recovery_skip_reason_is("unsupported_content_type")),
        ("must not retry unsupported content types", _retry_decision_is("do_not_retry")),
    ),
    "too_large_skip": (
        ("must model a too-large skip", _recovery_skip_reason_is("too_large")),
        ("must not retry too-large skips", _retry_decision_is("do_not_retry")),
    ),
    "processor_handoff_failure": (
        ("must model a processor handoff failure", _recovery_skip_reason_is("processor_handoff_failure")),
        ("must include processor handoff recovery backoff", _retry_plan_has_backoff),
    ),
    "no_raw_body_archive_decision": (
        (
            "must model the no-raw-body archive decision",
            _recovery_archive_decision_is("metadata_and_normalized_reference_only"),
        ),
        ("must record raw body was not persisted", _recovery_skip_reason_is("raw_body_not_persisted_by_policy")),
    ),
    "retry_backoff_plan": (
        ("must include a retry/backoff plan", _retry_plan_has_backoff),
        ("must model retry_with_backoff", _retry_decision_is("retry_with_backoff")),
    ),
    "reviewer_disposition_placeholder": (
        ("must hold for reviewer disposition", _retry_decision_is("hold_for_review")),
        ("must require review before mutation", _recovery_archive_decision_is("review_required_before_any_state_change")),
    ),
}


def load_packet(path: str | Path) -> dict[str, Any]:
    """Load a retry/recovery packet fixture from disk."""

    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("retry/recovery packet fixture must be a JSON object")
    return loaded


def _iter_key_values(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            next_path = f"{path}.{key}"
            rows.append((next_path, nested))
            rows.extend(_iter_key_values(nested, next_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            rows.extend(_iter_key_values(nested, f"{path}[{index}]"))
    return rows


def _iter_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            strings.extend(_iter_strings(nested))
    elif isinstance(value, list):
        for nested in value:
            strings.extend(_iter_strings(nested))
    return strings


def _validate_forbidden_artifacts(packet: dict[str, Any], errors: list[str]) -> None:
    artifact_manifest = packet.get("artifact_manifest", [])
    if artifact_manifest not in ([], None):
        errors.append("artifact_manifest must be empty for retry/recovery packet v2")

    for path, value in _iter_key_values(packet):
        key = path.rsplit(".", 1)[-1].lower()
        key_mentions_artifact = any(fragment in key for fragment in FORBIDDEN_ARTIFACT_KEY_FRAGMENTS)
        if key_mentions_artifact and value not in (False, None, [], {}, ""):
            if key in {"commits_raw_body", "raw_download"} and value is False:
                continue
            errors.append(f"{path} must not reference private/session/browser/raw/downloaded artifacts")

        if isinstance(value, str):
            lowered_value = value.lower()
            if any(fragment in lowered_value for fragment in FORBIDDEN_ARTIFACT_VALUE_FRAGMENTS):
                errors.append(f"{path} must not reference private/session/browser/raw/downloaded artifacts")


def _validate_forbidden_claims(packet: dict[str, Any], errors: list[str]) -> None:
    live_crawl_claims = packet.get("live_crawl_claims", [])
    if live_crawl_claims not in ([], None):
        errors.append("live_crawl_claims must be empty")

    legal_guarantees = packet.get("legal_or_permitting_guarantees", [])
    if legal_guarantees not in ([], None):
        errors.append("legal_or_permitting_guarantees must be empty")

    for value in _iter_strings(packet):
        lowered_value = value.lower()
        if any(fragment in lowered_value for fragment in FORBIDDEN_CLAIM_FRAGMENTS):
            errors.append("packet must not include live crawl claims, legal claims, or permitting guarantees")
            return


def validate_packet(packet: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors for a packet fixture."""

    errors: list[str] = []

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be public-crawl-retry-recovery-v2")

    mode = packet.get("mode")
    if mode != "fixture_first_offline":
        errors.append("mode must be fixture_first_offline")

    mutation_boundaries = packet.get("mutation_boundaries")
    if not isinstance(mutation_boundaries, dict):
        errors.append("mutation_boundaries must be an object")
    else:
        for marker in sorted(FORBIDDEN_MUTATION_MARKERS):
            if mutation_boundaries.get(marker) is not False:
                errors.append(f"mutation_boundaries.{marker} must be false")

    commands = packet.get("offline_validation_commands")
    expected_commands = [list(command) for command in REQUIRED_OFFLINE_COMMANDS]
    if commands != expected_commands:
        errors.append("offline_validation_commands must exactly match the packet v2 offline command list")

    _validate_forbidden_artifacts(packet, errors)
    _validate_forbidden_claims(packet, errors)

    scenarios = packet.get("scenarios")
    if not isinstance(scenarios, list):
        errors.append("scenarios must be a list")
        return errors

    scenarios_by_name: dict[str, dict[str, Any]] = {}
    scenario_names: set[str] = set()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"scenarios[{index}] must be an object")
            continue

        name = scenario.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"scenarios[{index}].name must be a non-empty string")
            continue
        scenario_names.add(name)
        scenarios_by_name[name] = scenario

        if scenario.get("fixture_only") is not True:
            errors.append(f"scenario {name} must set fixture_only true")
        if scenario.get("commits_raw_body") is not False:
            errors.append(f"scenario {name} must set commits_raw_body false")
        if scenario.get("executes_processor") is not False:
            errors.append(f"scenario {name} must set executes_processor false")
        if scenario.get("starts_crawler") is not False:
            errors.append(f"scenario {name} must set starts_crawler false")

        retry_plan = scenario.get("retry_plan")
        if not isinstance(retry_plan, dict):
            errors.append(f"scenario {name} retry_plan must be an object")
        else:
            if "decision" not in retry_plan:
                errors.append(f"scenario {name} retry_plan.decision is required")
            if "backoff_seconds" not in retry_plan:
                errors.append(f"scenario {name} retry_plan.backoff_seconds is required")

        recovery_packet = scenario.get("recovery_packet")
        if not isinstance(recovery_packet, dict):
            errors.append(f"scenario {name} recovery_packet must be an object")
        else:
            if recovery_packet.get("reviewer_disposition_placeholder") != "pending_reviewer_disposition":
                errors.append(f"scenario {name} requires reviewer_disposition_placeholder")
            if "archive_decision" not in recovery_packet:
                errors.append(f"scenario {name} recovery_packet.archive_decision is required")
            if "skip_reason" not in recovery_packet:
                errors.append(f"scenario {name} recovery_packet.skip_reason is required")

    missing = REQUIRED_SCENARIOS.difference(scenario_names)
    if missing:
        errors.append("missing scenarios: " + ", ".join(sorted(missing)))

    unexpected = scenario_names.difference(REQUIRED_SCENARIOS)
    if unexpected:
        errors.append("unexpected scenarios: " + ", ".join(sorted(unexpected)))

    for name, predicates in REQUIRED_SCENARIO_PREDICATES.items():
        scenario = scenarios_by_name.get(name)
        if scenario is None:
            continue
        for message, predicate in predicates:
            if not predicate(scenario):
                errors.append(f"scenario {name} {message}")

    return errors


def require_valid_packet(packet: dict[str, Any]) -> None:
    """Raise ValueError when a packet fixture fails validation."""

    errors = validate_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))


__all__ = [
    "FORBIDDEN_MUTATION_MARKERS",
    "PACKET_VERSION",
    "REQUIRED_OFFLINE_COMMANDS",
    "REQUIRED_SCENARIOS",
    "load_packet",
    "require_valid_packet",
    "validate_packet",
]
