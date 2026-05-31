"""Fixture-first public refresh dry-run replay packet v2.

This module replays committed synthetic public refresh scenarios into expected
review rows. It is deliberately metadata-only: it never fetches public sources,
downloads documents, invokes processors, touches DevHub, or mutates active
source, archive, document, requirement, guardrail, prompt, contract, DevHub, or
release-state surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

PACKET_TYPE = "ppd.public_refresh_dry_run_replay_packet.v2"
MODE = "fixture_first_public_refresh_dry_run_replay_only"

REQUIRED_SCENARIOS = frozenset(
    {
        "source_freshness",
        "changed_hash",
        "redirect_change",
        "content_type_skip",
        "too_large_skip",
        "robots_policy_denial",
        "processor_handoff_failure",
        "no_raw_body_archive",
    }
)

EXPECTED_ROW_KINDS = (
    "archive_manifest",
    "document_record",
    "requirement_impact",
    "guardrail_impact",
    "reviewer_hold",
    "retry_backoff",
    "validation_command",
)

FORBIDDEN_TRUE_KEYS = frozenset(
    {
        "active_archive_mutated",
        "active_contract_mutated",
        "active_crawler_invoked",
        "active_devhub_surface_mutated",
        "active_document_mutated",
        "active_guardrail_mutated",
        "active_prompt_mutated",
        "active_release_state_mutated",
        "active_requirement_mutated",
        "active_source_mutated",
        "archive_mutated",
        "crawler_invoked",
        "devhub_accessed",
        "document_downloaded",
        "live_network_invoked",
        "processor_executed",
        "raw_body_downloaded",
        "raw_body_persisted",
        "source_mutated",
    }
)

ALLOWED_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/public_refresh_dry_run_replay_packet_v2.py"),
    ("python3", "-m", "py_compile", "ppd/tests/test_public_refresh_dry_run_replay_packet_v2.py"),
    ("python3", "-m", "unittest", "ppd.tests.test_public_refresh_dry_run_replay_packet_v2"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]


def build_public_refresh_dry_run_replay_packet_v2(source_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic replay packet from a synthetic fixture packet."""

    scenarios = _scenario_rows(source_packet.get("scenarios"))
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        rows.extend(_expected_rows_for_scenario(scenario))

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v2",
        "mode": MODE,
        "packet_id": _text(source_packet.get("packet_id"), "public-refresh-dry-run-replay-v2-fixture"),
        "fixture_first": True,
        "dry_run": True,
        "metadata_only": True,
        "synthetic_replay": True,
        "scenario_kinds": [str(scenario["scenario_kind"]) for scenario in scenarios],
        "expected_row_kinds": list(EXPECTED_ROW_KINDS),
        "rows": rows,
        "attestations": _attestations(),
        "active_surface_mutations": _active_surface_mutations(),
        "validation_commands": [list(command) for command in ALLOWED_VALIDATION_COMMANDS],
    }
    require_valid_public_refresh_dry_run_replay_packet_v2(packet)
    return packet


def validate_public_refresh_dry_run_replay_packet_v2(packet: Mapping[str, Any]) -> ValidationResult:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be " + PACKET_TYPE)
    if packet.get("packet_version") != "v2":
        errors.append("packet_version must be v2")
    if packet.get("mode") != MODE:
        errors.append("mode must be " + MODE)
    for key in ("fixture_first", "dry_run", "metadata_only", "synthetic_replay"):
        if packet.get(key) is not True:
            errors.append(key + " must be true")

    scenario_kinds = set(_text_list(packet.get("scenario_kinds")))
    missing_scenarios = sorted(REQUIRED_SCENARIOS - scenario_kinds)
    if missing_scenarios:
        errors.append("missing scenario kinds: " + ", ".join(missing_scenarios))

    expected_row_kinds = set(_text_list(packet.get("expected_row_kinds")))
    missing_row_kinds = [kind for kind in EXPECTED_ROW_KINDS if kind not in expected_row_kinds]
    if missing_row_kinds:
        errors.append("missing expected row kinds: " + ", ".join(missing_row_kinds))

    rows = [row for row in _sequence(packet.get("rows")) if isinstance(row, Mapping)]
    if not rows:
        errors.append("rows must include deterministic replay rows")
    by_scenario: dict[str, set[str]] = {scenario_kind: set() for scenario_kind in REQUIRED_SCENARIOS}
    for index, row in enumerate(rows):
        path = "rows[" + str(index) + "]"
        scenario_kind = _text(row.get("scenario_kind"))
        row_kind = _text(row.get("row_kind"))
        if scenario_kind not in REQUIRED_SCENARIOS:
            errors.append(path + ".scenario_kind is unknown")
        if row_kind not in EXPECTED_ROW_KINDS:
            errors.append(path + ".row_kind is unknown")
        if scenario_kind in by_scenario:
            by_scenario[scenario_kind].add(row_kind)
        if row.get("expected") is not True:
            errors.append(path + ".expected must be true")
        if row.get("raw_body_persisted") is not False:
            errors.append(path + ".raw_body_persisted must be false")
        if row.get("live_network_invoked") is not False:
            errors.append(path + ".live_network_invoked must be false")
        if row.get("processor_executed") is not False:
            errors.append(path + ".processor_executed must be false")
        if not _text(row.get("review_status")):
            errors.append(path + ".review_status is required")
        if row_kind == "validation_command" and _command_tuple(row.get("command")) not in ALLOWED_VALIDATION_COMMANDS:
            errors.append(path + ".command must be an allowed deterministic offline validation command")
    for scenario_kind, row_kinds in sorted(by_scenario.items()):
        missing_for_scenario = [kind for kind in EXPECTED_ROW_KINDS if kind not in row_kinds]
        if missing_for_scenario:
            errors.append(scenario_kind + " missing row kinds: " + ", ".join(missing_for_scenario))

    commands = [_command_tuple(command) for command in _sequence(packet.get("validation_commands"))]
    if tuple(commands) != ALLOWED_VALIDATION_COMMANDS:
        errors.append("validation_commands must match the allowed deterministic offline command list")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be a mapping")
    else:
        for key, value in _attestations().items():
            if attestations.get(key) != value:
                errors.append("attestations." + key + " must be " + str(value).lower())

    mutation_flags = packet.get("active_surface_mutations")
    if not isinstance(mutation_flags, Mapping):
        errors.append("active_surface_mutations must be a mapping")
    else:
        for key in sorted(FORBIDDEN_TRUE_KEYS):
            if mutation_flags.get(key) is not False:
                errors.append("active_surface_mutations." + key + " must be false")
    _collect_forbidden_true_claims(packet, "$", errors)
    return ValidationResult(valid=not errors, errors=tuple(errors))


def require_valid_public_refresh_dry_run_replay_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_public_refresh_dry_run_replay_packet_v2(packet)
    if not result.valid:
        raise ValueError("invalid public refresh dry-run replay packet v2: " + "; ".join(result.errors))


def _expected_rows_for_scenario(scenario: Mapping[str, Any]) -> list[dict[str, Any]]:
    scenario_kind = _text(scenario["scenario_kind"])
    scenario_id = _text(scenario.get("scenario_id"), scenario_kind.replace("_", "-"))
    source_id = _text(scenario.get("source_id"), "synthetic-source")
    rows: list[dict[str, Any]] = []
    for order, row_kind in enumerate(EXPECTED_ROW_KINDS, start=1):
        rows.append(
            {
                "row_id": scenario_id + "-" + row_kind.replace("_", "-"),
                "scenario_id": scenario_id,
                "scenario_kind": scenario_kind,
                "source_id": source_id,
                "row_kind": row_kind,
                "row_order": order,
                "expected": True,
                "expected_status": _expected_status(scenario_kind, row_kind),
                "expected_artifact_ref": "fixture://public_refresh_dry_run_replay_packet_v2/" + scenario_id + "/" + row_kind,
                "review_status": _review_status(scenario_kind, row_kind),
                "retry_after_seconds": _retry_after_seconds(scenario_kind, row_kind),
                "command": list(ALLOWED_VALIDATION_COMMANDS[order % len(ALLOWED_VALIDATION_COMMANDS)]) if row_kind == "validation_command" else [],
                "citation_ids": _text_list(scenario.get("citation_ids")) or [scenario_id + "-fixture-citation"],
                "raw_body_persisted": False,
                "live_network_invoked": False,
                "processor_executed": False,
                "active_mutation_performed": False,
            }
        )
    return rows


def _scenario_rows(value: Any) -> list[Mapping[str, Any]]:
    rows = [row for row in _sequence(value) if isinstance(row, Mapping)]
    kinds = {_text(row.get("scenario_kind")) for row in rows}
    missing = sorted(REQUIRED_SCENARIOS - kinds)
    if missing:
        raise ValueError("missing synthetic scenarios: " + ", ".join(missing))
    return rows


def _expected_status(scenario_kind: str, row_kind: str) -> str:
    if row_kind == "archive_manifest":
        return {
            "content_type_skip": "skipped_unsupported_content_type",
            "too_large_skip": "skipped_too_large",
            "robots_policy_denial": "skipped_robots_or_policy_denial",
            "processor_handoff_failure": "metadata_captured_processor_handoff_failed",
            "no_raw_body_archive": "metadata_captured_without_raw_body",
        }.get(scenario_kind, "metadata_captured")
    if row_kind == "document_record":
        return "placeholder_only_no_active_document_record_mutation"
    if row_kind == "requirement_impact":
        return "impact_placeholder_pending_human_review"
    if row_kind == "guardrail_impact":
        return "guardrail_placeholder_pending_human_review"
    if row_kind == "reviewer_hold":
        return "hold_required_before_promotion"
    if row_kind == "retry_backoff":
        return "retry_not_scheduled_fixture_backoff_only"
    return "offline_validation_command_declared"


def _review_status(scenario_kind: str, row_kind: str) -> str:
    if scenario_kind in {"changed_hash", "redirect_change", "source_freshness"}:
        return "review_required_change_or_staleness"
    if row_kind in {"reviewer_hold", "requirement_impact", "guardrail_impact"}:
        return "review_required_before_any_promotion"
    return "fixture_expected_no_live_action"


def _retry_after_seconds(scenario_kind: str, row_kind: str) -> int | None:
    if row_kind != "retry_backoff":
        return None
    return {
        "processor_handoff_failure": 900,
        "robots_policy_denial": 0,
        "too_large_skip": 0,
        "content_type_skip": 0,
    }.get(scenario_kind, 300)


def _attestations() -> dict[str, bool]:
    return {
        "no_network_access": True,
        "no_raw_downloads": True,
        "no_processor_execution": True,
        "no_devhub_access": True,
        "no_active_crawler_source_archive_document_requirement_guardrail_prompt_contract_devhub_or_release_mutation": True,
    }


def _active_surface_mutations() -> dict[str, bool]:
    return {key: False for key in sorted(FORBIDDEN_TRUE_KEYS)}


def _collect_forbidden_true_claims(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + "." + key_text
            if key_text in FORBIDDEN_TRUE_KEYS and child is True:
                errors.append(child_path + " must not be true")
            _collect_forbidden_true_claims(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _collect_forbidden_true_claims(child, path + "[" + str(index) + "]", errors)


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _text_list(value: Any) -> list[str]:
    return [str(item) for item in _sequence(value) if str(item)]


def _command_tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in _sequence(value) if str(item))


__all__ = [
    "ALLOWED_VALIDATION_COMMANDS",
    "EXPECTED_ROW_KINDS",
    "MODE",
    "PACKET_TYPE",
    "REQUIRED_SCENARIOS",
    "ValidationResult",
    "build_public_refresh_dry_run_replay_packet_v2",
    "require_valid_public_refresh_dry_run_replay_packet_v2",
    "validate_public_refresh_dry_run_replay_packet_v2",
]
