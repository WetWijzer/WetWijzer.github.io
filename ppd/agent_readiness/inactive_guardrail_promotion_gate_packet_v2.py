"""Fixture-first inactive guardrail promotion gate packet v2.

This module evaluates synthetic inactive guardrail migration preview rows and
emits recommendation metadata only. It does not promote guardrails, change active
prompts, update source registries, touch DevHub surfaces, or perform live crawl
or official PP&D actions.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PACKET_TYPE = "ppd.inactive_guardrail_promotion_gate_packet.v2"
SOURCE_PACKET_TYPE = "ppd.synthetic_inactive_guardrail_migration_preview_rows.v2"
MODE = "fixture_first_inactive_guardrail_promotion_gate_only"
OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/inactive_guardrail_promotion_gate_packet_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_inactive_guardrail_promotion_gate_packet_v2"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

MUTATION_FLAGS = (
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_contract_mutation",
    "active_source_registry_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
    "guardrail_promotion_performed",
    "prompt_update_performed",
    "requirement_update_performed",
    "process_model_update_performed",
    "contract_update_performed",
    "source_registry_update_performed",
    "devhub_surface_update_performed",
    "release_state_update_performed",
    "live_crawl_performed",
    "devhub_access_performed",
    "form_fill_performed",
    "upload_performed",
    "submission_performed",
    "certification_performed",
    "payment_performed",
    "scheduling_performed",
    "official_action_performed",
)

GATE_ROW_SECTIONS = (
    "deterministic_predicates",
    "deontic_rules",
    "temporal_rules",
    "reversible_action_predicates",
    "exact_confirmation_predicates",
    "refused_action_predicates",
    "stale_source_holds",
)

REQUIRED_PREVIEW_SECTIONS = GATE_ROW_SECTIONS + (
    "source_evidence_traces",
    "explanation_template_placeholders",
    "reviewer_dispositions",
    "offline_validation_commands",
)

PROMOTION_RECOMMENDATIONS = {"promote", "hold", "reject"}
REQUIRED_RECOMMENDATION_FIELDS = (
    "recommendation_id",
    "source_row_id",
    "source_section",
    "source_evidence_trace_ids",
    "recommendation",
    "predicate_result",
    "deontic_result",
    "temporal_result",
    "reversible_action_result",
    "exact_confirmation_result",
    "refused_action_result",
    "stale_source_result",
    "explanation_template_result",
    "reviewer_disposition_result",
    "offline_validation_result",
    "reason_codes",
    "validation_commands",
)

ROW_REQUIRED_FIELDS = (
    "row_id",
    "deterministic_predicate",
    "deontic_rule",
    "temporal_rule",
    "reversible_action",
    "requires_exact_confirmation",
    "refuses_prohibited_action",
    "source_evidence_trace_ids",
)

ALLOWED_DEONTIC_RULES = {"permission", "obligation", "prohibition", "action_gate"}
ALLOWED_TEMPORAL_RULES = {"current", "before_official_action", "hold_until_fresh"}

FORBIDDEN_KEY_TOKENS = (
    "auth",
    "browser",
    "cookie",
    "credential",
    "devhub_session",
    "download",
    "har",
    "password",
    "payment_detail",
    "private",
    "raw_body",
    "raw_crawl",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session",
    "storage_state",
    "upload_file",
    "warc_payload",
)
FORBIDDEN_TRACE_KEY_TOKENS = ("trace",)

FORBIDDEN_VALUE_PHRASES = (
    "approval is guaranteed",
    "application submitted",
    "certification completed",
    "devhub session",
    "document uploaded",
    "fee paid",
    "final payment",
    "guardrail promoted",
    "inspection scheduled",
    "legal guarantee",
    "legal advice",
    "live crawl completed",
    "opened devhub",
    "permit guaranteed",
    "permit is guaranteed",
    "permit will be issued",
    "promoted to active",
    "submission completed",
)


class InactiveGuardrailPromotionGatePacketV2Error(ValueError):
    """Raised when a gate packet or source fixture is invalid."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid inactive guardrail promotion gate packet v2: " + "; ".join(self.errors))


def load_synthetic_inactive_guardrail_migration_preview_rows_v2(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        preview = json.load(handle)
    if not isinstance(preview, dict):
        raise InactiveGuardrailPromotionGatePacketV2Error(["preview fixture must be a JSON object"])
    return preview


def build_inactive_guardrail_promotion_gate_packet_v2(
    synthetic_inactive_guardrail_migration_preview_rows_v2: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a fixture-only recommendation gate from synthetic preview rows."""

    preview = deepcopy(dict(synthetic_inactive_guardrail_migration_preview_rows_v2))
    input_errors = validate_synthetic_inactive_guardrail_migration_preview_rows_v2(preview)
    if input_errors:
        raise InactiveGuardrailPromotionGatePacketV2Error(input_errors)

    recommendations = _recommendations(preview)
    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v2",
        "mode": MODE,
        "fixture_first": True,
        "inactive_gate_only": True,
        "recommendations_only": True,
        "source_fixture_ref": _text(preview.get("fixture_id"), "synthetic_inactive_guardrail_migration_preview_rows_v2"),
        "source_packet_type": _text(preview.get("packet_type"), SOURCE_PACKET_TYPE),
        "source_evidence_traces": deepcopy(preview.get("source_evidence_traces")),
        "promotion_recommendations": recommendations,
        "recommendation_counts": _recommendation_counts(recommendations),
        "attestations": {
            "no_guardrails_promoted": True,
            "no_active_prompts_changed": True,
            "no_requirements_changed": True,
            "no_process_models_changed": True,
            "no_contracts_changed": True,
            "no_source_registries_changed": True,
            "no_devhub_surfaces_changed": True,
            "no_release_state_changed": True,
            "no_live_crawl": True,
            "no_devhub_access": True,
            "no_form_filling": True,
            "no_uploads": True,
            "no_submissions": True,
            "no_certifications": True,
            "no_payments": True,
            "no_scheduling": True,
        },
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }
    for flag in MUTATION_FLAGS:
        packet[flag] = False

    errors = validate_inactive_guardrail_promotion_gate_packet_v2(packet)
    if errors:
        raise InactiveGuardrailPromotionGatePacketV2Error(errors)
    return packet


def validate_synthetic_inactive_guardrail_migration_preview_rows_v2(preview: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(preview, Mapping):
        return ["preview fixture must be an object"]
    if preview.get("packet_type") != SOURCE_PACKET_TYPE:
        errors.append(f"preview packet_type must be {SOURCE_PACKET_TYPE}")
    if preview.get("source_mode") != "synthetic_committed_fixture_only":
        errors.append("preview source_mode must be synthetic_committed_fixture_only")
    if preview.get("inactive_preview_only") is not True:
        errors.append("preview inactive_preview_only must be true")
    for section in REQUIRED_PREVIEW_SECTIONS:
        rows = preview.get(section)
        if not isinstance(rows, list) or not rows:
            errors.append(f"preview {section} must be a non-empty list")
    if not isinstance(preview.get("offline_validation_commands"), list) or not preview.get("offline_validation_commands"):
        errors.append("preview offline_validation_commands must be a non-empty list")
    if preview.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        errors.append("preview offline_validation_commands must match exact offline gate commands")
    _validate_source_evidence_traces(preview.get("source_evidence_traces"), errors, root="preview.source_evidence_traces")
    _validate_preview_gate_rows(preview, errors)
    _validate_no_forbidden_payload(preview, errors, root="preview")
    return errors


def validate_inactive_guardrail_promotion_gate_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be an object"]
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("mode") != MODE:
        errors.append(f"mode must be {MODE}")
    for key in ("fixture_first", "inactive_gate_only", "recommendations_only"):
        if packet.get(key) is not True:
            errors.append(f"{key} must be true")
    for flag in MUTATION_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")
    if not isinstance(packet.get("offline_validation_commands"), list) or not packet.get("offline_validation_commands"):
        errors.append("offline_validation_commands must be a non-empty list")
    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands must match exact offline gate commands")
    _validate_source_evidence_traces(packet.get("source_evidence_traces"), errors, root="packet.source_evidence_traces")
    _validate_recommendations(packet.get("promotion_recommendations"), errors)
    _validate_counts(packet.get("recommendation_counts"), packet.get("promotion_recommendations"), errors)
    _validate_no_forbidden_payload(packet, errors, root="packet")
    return errors


def _recommendations(preview: Mapping[str, Any]) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for section in GATE_ROW_SECTIONS:
        for row in _rows(preview.get(section)):
            row_id = _text(row.get("row_id"), _text(row.get("id"), "row"))
            checks = _evaluate_row(section, row, preview)
            recommendation, reason_codes = _recommendation_from_checks(checks)
            recommendations.append(
                {
                    "recommendation_id": f"recommendation.{section}.{row_id}",
                    "source_row_id": row_id,
                    "source_section": section,
                    "source_evidence_trace_ids": _string_items(row.get("source_evidence_trace_ids")),
                    "recommendation": recommendation,
                    "predicate_result": checks["predicate_result"],
                    "deontic_result": checks["deontic_result"],
                    "temporal_result": checks["temporal_result"],
                    "reversible_action_result": checks["reversible_action_result"],
                    "exact_confirmation_result": checks["exact_confirmation_result"],
                    "refused_action_result": checks["refused_action_result"],
                    "stale_source_result": checks["stale_source_result"],
                    "explanation_template_result": checks["explanation_template_result"],
                    "reviewer_disposition_result": checks["reviewer_disposition_result"],
                    "offline_validation_result": checks["offline_validation_result"],
                    "reason_codes": reason_codes,
                    "validation_commands": OFFLINE_VALIDATION_COMMANDS,
                }
            )
    return recommendations


def _evaluate_row(section: str, row: Mapping[str, Any], preview: Mapping[str, Any]) -> dict[str, str]:
    row_id = _text(row.get("row_id"), _text(row.get("id"), "row"))
    disposition = _disposition_for(row_id, preview.get("reviewer_dispositions"))
    return {
        "predicate_result": _result(row.get("deterministic_predicate") is True or section == "deterministic_predicates", row.get("predicate_failure")),
        "deontic_result": _result(row.get("deontic_rule") in ALLOWED_DEONTIC_RULES or section == "deontic_rules", row.get("deontic_failure")),
        "temporal_result": _result(row.get("temporal_rule") in ALLOWED_TEMPORAL_RULES or section == "temporal_rules", row.get("temporal_failure")),
        "reversible_action_result": _result(row.get("reversible_action") is not False, row.get("reversible_action_failure")),
        "exact_confirmation_result": _result(row.get("requires_exact_confirmation") is not False, row.get("exact_confirmation_failure")),
        "refused_action_result": _result(row.get("refuses_prohibited_action") is not False, row.get("refused_action_failure")),
        "stale_source_result": _stale_source_result(row),
        "explanation_template_result": _placeholder_result(row, preview.get("explanation_template_placeholders")),
        "reviewer_disposition_result": _reviewer_result(disposition),
        "offline_validation_result": "pass" if preview.get("offline_validation_commands") == OFFLINE_VALIDATION_COMMANDS else "reject",
    }


def _validate_preview_gate_rows(preview: Mapping[str, Any], errors: list[str]) -> None:
    trace_ids = {_text(row.get("trace_id")) for row in _rows(preview.get("source_evidence_traces"))}
    disposition_ids = {_text(row.get("row_id")) for row in _rows(preview.get("reviewer_dispositions"))}
    for section in GATE_ROW_SECTIONS:
        for index, row in enumerate(_rows(preview.get(section))):
            row_path = f"preview.{section}[{index}]"
            row_id = _text(row.get("row_id"))
            for field in ROW_REQUIRED_FIELDS:
                if field not in row:
                    errors.append(f"{row_path}.{field} is required")
            if not row_id:
                errors.append(f"{row_path}.row_id must be a non-empty string")
            if row.get("deterministic_predicate") is not True:
                errors.append(f"{row_path}.deterministic_predicate must be true")
            if row.get("deontic_rule") not in ALLOWED_DEONTIC_RULES:
                errors.append(f"{row_path}.deontic_rule must be permission, obligation, prohibition, or action_gate")
            if row.get("temporal_rule") not in ALLOWED_TEMPORAL_RULES:
                errors.append(f"{row_path}.temporal_rule must be current, before_official_action, or hold_until_fresh")
            if row.get("reversible_action") is not True:
                errors.append(f"{row_path}.reversible_action must be true")
            if row.get("requires_exact_confirmation") is not True:
                errors.append(f"{row_path}.requires_exact_confirmation must be true")
            if row.get("refuses_prohibited_action") not in {True, False}:
                errors.append(f"{row_path}.refuses_prohibited_action must be a boolean")
            if section == "refused_action_predicates" and "refused_action_failure" not in row:
                errors.append(f"{row_path}.refused_action_failure is required for refused-action gate rows")
            if section == "stale_source_holds" and row.get("stale_source_hold") is not True:
                errors.append(f"{row_path}.stale_source_hold must be true")
            evidence_ids = _string_items(row.get("source_evidence_trace_ids"))
            if not evidence_ids:
                errors.append(f"{row_path}.source_evidence_trace_ids must be a non-empty string list")
            for evidence_id in evidence_ids:
                if evidence_id not in trace_ids:
                    errors.append(f"{row_path}.source_evidence_trace_ids references missing source evidence trace {evidence_id}")
            if row_id and row_id not in disposition_ids:
                errors.append(f"{row_path} is missing reviewer disposition for {row_id}")


def _validate_source_evidence_traces(value: Any, errors: list[str], *, root: str) -> None:
    rows = _rows(value)
    if not rows:
        errors.append(f"{root} must be a non-empty list")
        return
    seen: set[str] = set()
    for index, row in enumerate(rows):
        path = f"{root}[{index}]"
        trace_id = _text(row.get("trace_id"))
        if not trace_id:
            errors.append(f"{path}.trace_id must be a non-empty string")
        elif trace_id in seen:
            errors.append(f"{path}.trace_id must be unique")
        seen.add(trace_id)
        for field in ("source_id", "citation", "evidence_kind"):
            if not _text(row.get(field)):
                errors.append(f"{path}.{field} must be a non-empty string")
        if row.get("committed_fixture_only") is not True:
            errors.append(f"{path}.committed_fixture_only must be true")


def _recommendation_from_checks(checks: Mapping[str, str]) -> tuple[str, list[str]]:
    rejects = sorted(key for key, value in checks.items() if value == "reject")
    holds = sorted(key for key, value in checks.items() if value == "hold")
    if rejects:
        return "reject", [f"{key}:reject" for key in rejects]
    if holds:
        return "hold", [f"{key}:hold" for key in holds]
    return "promote", ["all_offline_predicates_passed"]


def _result(passed: bool, explicit_failure: Any) -> str:
    if explicit_failure is True:
        return "reject"
    return "pass" if passed else "hold"


def _stale_source_result(row: Mapping[str, Any]) -> str:
    if row.get("stale_source") is True and row.get("stale_source_hold") is not True:
        return "reject"
    if row.get("stale_source_hold") is True:
        return "hold"
    return "pass"


def _placeholder_result(row: Mapping[str, Any], placeholders: Any) -> str:
    required = _string_items(row.get("required_explanation_placeholders"))
    if not required:
        return "pass"
    available = {_text(item.get("placeholder")) for item in _rows(placeholders)}
    missing = [item for item in required if item not in available]
    return "hold" if missing else "pass"


def _reviewer_result(disposition: Mapping[str, Any] | None) -> str:
    if disposition is None:
        return "hold"
    status = _text(disposition.get("status"))
    if status == "accepted_for_gate_evaluation":
        return "pass"
    if status in {"rejected_by_reviewer", "reject_preview_mapping"}:
        return "reject"
    return "hold"


def _disposition_for(row_id: str, dispositions: Any) -> Mapping[str, Any] | None:
    for row in _rows(dispositions):
        if _text(row.get("row_id")) == row_id:
            return row
    return None


def _validate_recommendations(rows: Any, errors: list[str]) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("promotion_recommendations must be a non-empty list")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"promotion_recommendations[{index}] must be an object")
            continue
        for field in REQUIRED_RECOMMENDATION_FIELDS:
            if field not in row:
                errors.append(f"promotion_recommendations[{index}].{field} is required")
        if row.get("recommendation") not in PROMOTION_RECOMMENDATIONS:
            errors.append(f"promotion_recommendations[{index}].recommendation must be promote, hold, or reject")
        for result_field in REQUIRED_RECOMMENDATION_FIELDS[5:14]:
            if row.get(result_field) not in {"pass", "hold", "reject"}:
                errors.append(f"promotion_recommendations[{index}].{result_field} must be pass, hold, or reject")
        if row.get("validation_commands") != OFFLINE_VALIDATION_COMMANDS:
            errors.append(f"promotion_recommendations[{index}].validation_commands must match exact offline gate commands")
        if not _string_items(row.get("source_evidence_trace_ids")):
            errors.append(f"promotion_recommendations[{index}].source_evidence_trace_ids must be a non-empty string list")
        reason_codes = row.get("reason_codes")
        if not isinstance(reason_codes, list) or not all(isinstance(item, str) and item for item in reason_codes):
            errors.append(f"promotion_recommendations[{index}].reason_codes must be a non-empty string list")


def _validate_counts(counts: Any, rows: Any, errors: list[str]) -> None:
    if not isinstance(counts, Mapping):
        errors.append("recommendation_counts must be an object")
        return
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return
    expected = _recommendation_counts([row for row in rows if isinstance(row, Mapping)])
    if dict(counts) != expected:
        errors.append("recommendation_counts must match promotion_recommendations")


def _recommendation_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {"promote": 0, "hold": 0, "reject": 0}
    for row in rows:
        recommendation = row.get("recommendation")
        if recommendation in counts:
            counts[recommendation] += 1
    return counts


def _validate_no_forbidden_payload(value: Any, errors: list[str], *, root: str) -> None:
    for path, key, child in _walk(value, path=root):
        key_name = key.lower()
        if any(token in key_name for token in FORBIDDEN_KEY_TOKENS) and _truthy(child):
            errors.append(f"{path} must not include private, browser, session, raw, downloaded, upload, payment, or trace artifacts")
        if any(token in key_name for token in FORBIDDEN_TRACE_KEY_TOKENS) and not _is_source_evidence_trace_path(path) and _truthy(child):
            errors.append(f"{path} must not include private, browser, session, raw, downloaded, upload, payment, or trace artifacts")
        if key_name in MUTATION_FLAGS and child is not False:
            errors.append(f"{path} must be false")
        if isinstance(child, str):
            lowered = child.lower()
            if any(phrase in lowered for phrase in FORBIDDEN_VALUE_PHRASES):
                errors.append(f"{path} must not claim promotion, live execution, DevHub access, official action, legal or permitting guarantees, payment, scheduling, upload, or permit outcome")


def _is_source_evidence_trace_path(path: str) -> bool:
    return ".source_evidence_traces" in path or ".source_evidence_trace_ids" in path


def _walk(value: Any, path: str, key: str = "") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}"
            yield child_path, child_key_text, child
            yield from _walk(child, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, key, child
            yield from _walk(child, child_path, key)


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [_text(item) for item in value if _text(item)]


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Mapping) and not value:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    return True


def _text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback
