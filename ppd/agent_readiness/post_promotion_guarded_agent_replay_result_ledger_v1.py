"""Validation for post-promotion guarded agent replay result ledgers v1.

The result ledger is the offline evidence that a guarded-agent replay was run
against deterministic fixtures after promotion. The validator is deliberately
fail-closed: replay rows must be complete, cited, reviewable, rollback-aware,
and free of private artifacts, live-execution claims, consequential action
language, legal/permitting guarantees, and active mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

LEDGER_TYPE = "ppd.post_promotion_guarded_agent_replay_result_ledger.v1"
PLAN_TYPE = "ppd.post_promotion_guarded_agent_replay_plan.v1"
_ALLOWED_EXPECTED_OUTCOMES = {"PASS", "BLOCK"}
_PLACEHOLDER_VALUES = {"expected_pass", "expected_block", "pass", "block"}

_PRIVATE_OR_SESSION_KEY_TOKENS = {
    "auth",
    "authorization",
    "browser_context",
    "cookie",
    "credential",
    "devhub_session",
    "email",
    "har",
    "local_storage",
    "mfa",
    "password",
    "payment",
    "private",
    "secret",
    "session",
    "storage_state",
    "token",
    "trace",
}
_RAW_ARTIFACT_KEY_TOKENS = {
    "download",
    "downloaded_data",
    "downloaded_document",
    "downloaded_pdf",
    "pdf_bytes",
    "raw_body",
    "raw_crawl",
    "raw_data",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "trace",
}
_MUTATION_FLAG_KEYS = {
    "active_agent_state_mutation",
    "active_fixture_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "agent_state_mutation_enabled",
    "fixture_mutation_enabled",
    "guardrail_mutation_enabled",
    "mutation_flags",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
}
_FORBIDDEN_VALUE_PATTERNS = (
    re.compile(r"\b(?:cookie|session state|auth state|storage state|bearer token|password|credential|mfa|captcha)\b", re.IGNORECASE),
    re.compile(r"\b(?:screenshot|trace\.zip|playwright trace|browser trace|har file|\.har\b|\.trace\b)\b", re.IGNORECASE),
    re.compile(r"\b(?:raw crawl|raw html|raw pdf|raw downloaded|downloaded document|downloaded pdf|pdf bytes)\b", re.IGNORECASE),
    re.compile(r"\b(?:live devhub|live execution|executed live|ran live|opened devhub|clicked devhub|submitted through devhub|release complete|release completed|promoted to release)\b", re.IGNORECASE),
    re.compile(r"\b(?:approval guaranteed|guarantee(?:d|s)? approval|permit will be approved|permit will issue|legal advice|legally sufficient|compliance guaranteed|inspection will pass)\b", re.IGNORECASE),
    re.compile(r"\b(?:submit|submitted|submission|pay|paid|payment|upload|uploaded|schedule|scheduled|cancel|cancelled|canceled|certify|certified|purchase|purchased)\b", re.IGNORECASE),
    re.compile(r"\b(?:active prompt|active guardrail|active release[-_ ]state|active fixture|active agent[-_ ]state)\b.{0,80}\b(?:mutat|write|patch|replace|update|promot)", re.IGNORECASE),
    re.compile(r"\b(?:mutat|write|patch|replace|update|promot)\b.{0,80}\b(?:active prompt|active guardrail|active release[-_ ]state|active fixture|active agent[-_ ]state)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ReplayResultLedgerV1ValidationResult:
    """Machine-readable validation result for replay result ledgers."""

    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


def load_json_fixture(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("fixture must be a JSON object")
    return loaded


def validate_post_promotion_guarded_agent_replay_result_ledger_v1(
    ledger: Mapping[str, Any],
) -> ReplayResultLedgerV1ValidationResult:
    """Return fail-closed validation for a replay result ledger v1 payload."""

    problems: list[str] = []
    if ledger.get("ledger_type") != LEDGER_TYPE:
        problems.append(f"ledger_type must be {LEDGER_TYPE}")
    if ledger.get("fixture_only") is not True:
        problems.append("fixture_only must be true")

    source_plan = _mapping(ledger.get("source_plan")) or _mapping(ledger.get("source_plan_ref"))
    if source_plan.get("plan_type") != PLAN_TYPE:
        problems.append(f"source_plan.plan_type must be {PLAN_TYPE}")
    if not _text(source_plan.get("plan_id")):
        problems.append("source_plan.plan_id must be non-empty")

    evidence_ids = set(_string_list(ledger.get("source_evidence_ids")))
    if not evidence_ids:
        problems.append("source_evidence_ids must be non-empty")

    scenario_order = _string_list(ledger.get("scenario_order"))
    if not scenario_order:
        problems.append("scenario_order must be non-empty")

    rows = _mapping_sequence(ledger.get("replay_result_rows") or ledger.get("result_rows"))
    if not rows:
        problems.append("replay_result_rows must be non-empty")
    _validate_replay_rows(problems, rows, scenario_order, evidence_ids)

    if not _command_vectors(ledger.get("validation_commands")):
        problems.append("validation_commands must include at least one command vector")

    _validate_text_safety(problems, ledger)
    return ReplayResultLedgerV1ValidationResult(valid=not problems, problems=tuple(problems))


def assert_valid_post_promotion_guarded_agent_replay_result_ledger_v1(ledger: Mapping[str, Any]) -> None:
    """Raise ValueError when a replay result ledger v1 payload is invalid."""

    result = validate_post_promotion_guarded_agent_replay_result_ledger_v1(ledger)
    if not result.valid:
        raise ValueError("invalid post-promotion guarded agent replay result ledger v1: " + "; ".join(result.problems))


def _validate_replay_rows(
    problems: list[str],
    rows: Sequence[Mapping[str, Any]],
    scenario_order: Sequence[str],
    evidence_ids: set[str],
) -> None:
    rows_by_scenario: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(rows):
        scenario_id = _text(row.get("scenario_id"))
        row_path = f"replay_result_rows[{index}]"
        if not scenario_id:
            problems.append(f"{row_path}.scenario_id must be non-empty")
        elif scenario_id in rows_by_scenario:
            problems.append(f"{row_path}.scenario_id duplicates {scenario_id}")
        else:
            rows_by_scenario[scenario_id] = row
        if scenario_order and scenario_id and scenario_id not in scenario_order:
            problems.append(f"{row_path}.scenario_id is not listed in scenario_order")
        _validate_single_row(problems, row, row_path, evidence_ids)

    for scenario_id in scenario_order:
        if scenario_id not in rows_by_scenario:
            problems.append(f"replay_result_rows missing result row for scenario {scenario_id}")


def _validate_single_row(problems: list[str], row: Mapping[str, Any], row_path: str, evidence_ids: set[str]) -> None:
    if not _text(row.get("scenario_ref")):
        problems.append(f"{row_path}.scenario_ref must reference the replay scenario")

    citations = _string_list(row.get("source_evidence_ids")) or _string_list(row.get("citations"))
    if not citations:
        problems.append(f"{row_path}.source_evidence_ids must cite scenario evidence")
    for citation in citations:
        if citation not in evidence_ids:
            problems.append(f"{row_path}.source_evidence_ids cites unknown evidence id {citation}")

    outcome = _text(row.get("expected_pass_block_outcome_placeholder") or row.get("expected_outcome_placeholder"))
    decision = _text(row.get("expected_guardrail_decision") or row.get("expected_result"))
    if outcome.lower() not in _PLACEHOLDER_VALUES and decision.upper() not in _ALLOWED_EXPECTED_OUTCOMES:
        problems.append(f"{row_path} must include expected pass/block outcome placeholder")

    if not _text(row.get("reviewer_observation_placeholder")):
        problems.append(f"{row_path}.reviewer_observation_placeholder must be non-empty")

    mismatch = _mapping(row.get("mismatch_carry_forward"))
    if not mismatch:
        problems.append(f"{row_path}.mismatch_carry_forward must be present")
    else:
        if "mismatch_detected" not in mismatch:
            problems.append(f"{row_path}.mismatch_carry_forward.mismatch_detected must be present")
        if "carry_forward_required" not in mismatch:
            problems.append(f"{row_path}.mismatch_carry_forward.carry_forward_required must be present")
        if not _text(mismatch.get("carry_forward_ref")):
            problems.append(f"{row_path}.mismatch_carry_forward.carry_forward_ref must be non-empty")

    if not _text(row.get("rollback_checkpoint_ref")):
        problems.append(f"{row_path}.rollback_checkpoint_ref must be non-empty")
    if not _command_vectors(row.get("validation_commands")):
        problems.append(f"{row_path}.validation_commands must include at least one command vector")


def _validate_text_safety(problems: list[str], value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if any(token in normalized for token in _PRIVATE_OR_SESSION_KEY_TOKENS) and child not in (None, False, "", [], {}):
                problems.append(f"{child_path} must not include private, authenticated, session, browser, auth, or payment artifacts")
            if any(token in normalized for token in _RAW_ARTIFACT_KEY_TOKENS) and child not in (None, False, "", [], {}):
                problems.append(f"{child_path} must not include screenshots, traces, HAR files, raw crawl, PDF, or downloaded data")
            if normalized in _MUTATION_FLAG_KEYS and child not in (None, False, "", [], {}):
                problems.append(f"{child_path} must not declare active guardrail, prompt, release-state, fixture, or agent-state mutation")
            _validate_text_safety(problems, child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _validate_text_safety(problems, child, f"{path}[{index}]")
    elif isinstance(value, str):
        for pattern in _FORBIDDEN_VALUE_PATTERNS:
            if pattern.search(value):
                problems.append(f"{path} contains forbidden replay-result ledger language")
                break


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) else ()


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    return tuple(item for item in _sequence(value) if isinstance(item, Mapping))


def _string_list(value: Any) -> list[str]:
    return [item for item in _sequence(value) if isinstance(item, str) and item]


def _command_vectors(value: Any) -> tuple[tuple[str, ...], ...]:
    commands: list[tuple[str, ...]] = []
    for item in _sequence(value):
        parts = tuple(part for part in _sequence(item) if isinstance(part, str) and part)
        if parts:
            commands.append(parts)
    return tuple(commands)


def _text(value: Any, fallback: str = "") -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback
