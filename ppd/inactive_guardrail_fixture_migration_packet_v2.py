from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.guardrail_patch_application_preview_v2 import (
    build_guardrail_patch_application_preview_v2_from_fixture,
    validate_guardrail_patch_application_preview_v2,
)
from ppd.validation.offline_patch_migration_approval_matrix_v2 import (
    validate_offline_patch_migration_approval_matrix_v2,
)

PACKET_TYPE = "ppd.inactive_guardrail_fixture_migration_packet.v2"
PACKET_VERSION = 2

REQUIRED_ATTESTATIONS = {
    "no_live_llm": True,
    "no_devhub": True,
    "no_crawler": True,
    "no_processor": True,
    "no_active_guardrail_or_prompt_mutation": True,
    "no_active_guardrail_mutation": True,
    "no_active_prompt_mutation": True,
    "no_active_source_mutation": True,
    "no_active_surface_registry_mutation": True,
    "no_active_monitoring_mutation": True,
    "no_active_release_state_mutation": True,
    "no_active_agent_state_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/inactive_guardrail_fixture_migration_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_guardrail_fixture_migration_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_PROHIBITED_KEYS = {
    "auth_state",
    "authenticated_fact",
    "authenticated_facts",
    "authenticated_value",
    "browser_artifact",
    "browser_context",
    "browser_session",
    "browser_storage_state",
    "browser_trace",
    "cookies",
    "crawl_artifact",
    "crawl_output",
    "devhub_session",
    "downloaded_document",
    "har",
    "har_path",
    "llm_response",
    "payment_details",
    "pdf_artifact",
    "private_fact",
    "private_facts",
    "private_value",
    "raw_body",
    "raw_browser",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "raw_session",
    "screenshot",
    "session_artifact",
    "session_file",
    "session_state",
    "storage_state",
    "trace",
    "trace_path",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_guardrail_or_prompt_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "agent_state_mutation_enabled",
    "apply_guardrail_changes",
    "apply_prompt_changes",
    "guardrail_mutation",
    "guardrail_mutation_enabled",
    "monitoring_mutation",
    "monitoring_mutation_enabled",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_source",
    "mutates_sources",
    "mutates_surface_registry",
    "prompt_mutation",
    "prompt_mutation_enabled",
    "release_state_mutation",
    "release_state_mutation_enabled",
    "source_mutation",
    "source_mutation_enabled",
    "surface_registry_mutation",
    "surface_registry_mutation_enabled",
    "update_guardrails",
    "update_prompts",
    "update_sources",
    "update_surface_registry",
}

_PRIVATE_TEXT_TERMS = (
    "authenticated fact",
    "authenticated facts",
    "authenticated value",
    "credential",
    "mfa",
    "password",
    "private devhub value",
    "private fact",
    "private facts",
    "session token",
)

_RAW_ARTIFACT_TEXT_TERMS = (
    "browser artifact",
    "browser session artifact",
    "crawl artifact",
    "har artifact",
    "pdf artifact",
    "raw body",
    "raw browser",
    "raw crawl",
    "raw download",
    "raw html",
    "raw pdf",
    "raw session",
    "screenshot artifact",
    "session artifact",
    "storage state artifact",
    "trace artifact",
)

_LIVE_EXECUTION_TEXT_TERMS = (
    "called live llm",
    "crawler completed",
    "crawler ran",
    "devhub live run completed",
    "live crawler completed",
    "live devhub",
    "live llm",
    "live llm completed",
    "opened devhub",
    "processor completed",
    "processor ran",
    "ran crawler",
    "ran devhub",
    "ran live llm",
    "ran llm",
    "ran processor",
    "used devhub",
)

_OUTCOME_GUARANTEE_TEXT_TERMS = (
    "approval is guaranteed",
    "application will be accepted",
    "guaranteed approval",
    "guaranteed legal outcome",
    "guaranteed permit",
    "legal determination",
    "legal guarantee",
    "legal outcome guaranteed",
    "permit will be approved",
    "permit will be issued",
    "will be approved",
)

_CONSEQUENTIAL_ACTION_TEXT_TERMS = (
    "cancel inspection",
    "cancel permit",
    "cancel request",
    "cancellation completed",
    "certify acknowledgement",
    "enable payment",
    "enable scheduling",
    "enable submission",
    "execute cancellation",
    "execute payment",
    "final cancellation",
    "final payment",
    "final scheduling",
    "final submission",
    "final submit",
    "final upload",
    "official upload enabled",
    "perform cancellation",
    "perform payment",
    "schedule inspection",
    "submit application",
    "submit payment",
    "upload correction",
)


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_inactive_guardrail_fixture_migration_packet_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = load_json(fixture_path)
    base = fixture_path.parent
    preview = build_guardrail_patch_application_preview_v2_from_fixture(
        base / _required_text(fixture, "guardrail_patch_application_preview_v2_fixture")
    )
    matrix = load_json(base / _required_text(fixture, "offline_patch_migration_approval_matrix_v2_fixture"))
    return build_inactive_guardrail_fixture_migration_packet_v2(preview, matrix)


def build_inactive_guardrail_fixture_migration_packet_v2(
    guardrail_patch_application_preview_v2: Mapping[str, Any],
    offline_patch_migration_approval_matrix_v2: Mapping[str, Any],
) -> dict[str, Any]:
    preview_result = validate_guardrail_patch_application_preview_v2(guardrail_patch_application_preview_v2)
    if not preview_result.ok:
        raise ValueError("invalid guardrail patch application preview v2: " + "; ".join(preview_result.errors))

    matrix_result = validate_offline_patch_migration_approval_matrix_v2(offline_patch_migration_approval_matrix_v2)
    if not matrix_result.ok:
        raise ValueError("invalid offline patch migration approval matrix v2: " + "; ".join(error.code for error in matrix_result.errors))

    approvals = [row for row in _approval_rows(offline_patch_migration_approval_matrix_v2) if _text(row.get("decision")).lower() == "approve"]
    if not approvals:
        raise ValueError("offline patch migration approval matrix v2 must include at least one approve row")

    predicate_rows: list[dict[str, Any]] = []
    template_checks: list[dict[str, Any]] = []
    blocked_checks: list[dict[str, Any]] = []
    rollback_rows: list[dict[str, Any]] = []

    for preview_index, preview in enumerate(_dicts(guardrail_patch_application_preview_v2.get("guardrail_fixture_patch_previews"))):
        approval = approvals[preview_index % len(approvals)]
        approval_id = _row_id(approval, preview_index)
        reviewer_owner = _text(preview.get("reviewer_owner")) or _text(approval.get("reviewer_owner"))
        citations = _merge_citations(_citations(preview), _citation_strings(approval))
        bundle_id = _required_text(preview, "guardrail_bundle_id")
        preview_id = _required_text(preview, "preview_id")

        before_by_predicate = {_required_text(row, "predicate_id"): row for row in _dicts(preview.get("before_predicate_rows"))}
        for after_row in _dicts(preview.get("after_predicate_rows")):
            predicate_id = _required_text(after_row, "predicate_id")
            before_row = before_by_predicate.get(predicate_id, {})
            row_id = f"inactive-guardrail-fixture-{_slug(bundle_id)}-{_slug(predicate_id)}"
            predicate_rows.append(
                {
                    "predicate_row_id": row_id,
                    "preview_id": preview_id,
                    "guardrail_bundle_id": bundle_id,
                    "predicate_id": predicate_id,
                    "before_predicate_state": _text(before_row.get("predicate_state")) or "current_fixture_predicate_retained",
                    "after_predicate_state": _required_text(after_row, "predicate_state"),
                    "row_state": "inactive_fixture_only_guardrail_predicate_patch",
                    "fixture_only": True,
                    "inactive": True,
                    "active_guardrail_mutation": False,
                    "active_prompt_mutation": False,
                    "approval_row_id": approval_id,
                    "approval_decision": "approve",
                    "reviewer_owner": reviewer_owner,
                    "citations": _merge_citations(citations, _citations(after_row), _citations(before_row)),
                    "before_fixture_checksum": _checksum(before_row),
                    "after_fixture_checksum": _checksum(after_row),
                }
            )

        for delta in _dicts(preview.get("explanation_template_deltas")):
            predicate_id = _required_text(delta, "predicate_id")
            template_checks.append(
                {
                    "template_check_id": f"template-check-{_slug(bundle_id)}-{_slug(predicate_id)}",
                    "preview_id": preview_id,
                    "guardrail_bundle_id": bundle_id,
                    "predicate_id": predicate_id,
                    "before_template": _required_text(delta, "before_template"),
                    "after_template": _required_text(delta, "after_template"),
                    "delta_disposition": _required_text(delta, "delta_disposition"),
                    "fixture_only": True,
                    "active_prompt_mutation": False,
                    "reviewer_owner": reviewer_owner,
                    "citations": _merge_citations(citations, _citations(delta)),
                }
            )

        for check in _dicts(preview.get("blocked_consequential_action_checks")):
            action_id = _required_text(check, "action_id")
            blocked_checks.append(
                {
                    "regression_check_id": f"blocked-regression-{_slug(action_id)}",
                    "preview_id": preview_id,
                    "guardrail_bundle_id": bundle_id,
                    "action_id": action_id,
                    "before_blocked": True,
                    "after_blocked": check.get("blocked") is True,
                    "blocked_reason": _required_text(check, "reason"),
                    "fixture_only": True,
                    "consequential_action_remains_blocked": True,
                    "reviewer_owner": reviewer_owner,
                    "citations": _merge_citations(citations, _citations(check)),
                }
            )

        rollback_rows.append(
            {
                "checkpoint_id": f"rollback-inactive-guardrail-fixture-{_slug(preview_id)}",
                "preview_id": preview_id,
                "summary": _required_text(preview, "rollback_checkpoint"),
                "rollback_action": "discard_fixture_only_guardrail_predicate_rows_and_rebuild_from_guardrail_preview",
                "active_guardrail_or_prompt_unchanged": True,
                "reviewer_owner": reviewer_owner,
                "citations": citations,
            }
        )

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": "inactive-guardrail-fixture-migration-packet-v2",
        "mode": "fixture_first_inactive_guardrail_predicate_rows_only",
        "consumes": {
            "guardrail_patch_application_preview_v2": _text(guardrail_patch_application_preview_v2.get("preview_type")),
            "offline_patch_migration_approval_matrix_v2": "offline_patch_migration_approval_matrix_v2",
        },
        "cited_fixture_only_guardrail_predicate_rows": predicate_rows,
        "before_after_explanation_template_checks": template_checks,
        "blocked_consequential_action_regression_checks": blocked_checks,
        "rollback_checkpoints": rollback_rows,
        "reviewer_owner_fields": _reviewer_owner_fields(predicate_rows, template_checks, blocked_checks),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    validate_inactive_guardrail_fixture_migration_packet_v2(packet)
    return packet


def validate_inactive_guardrail_fixture_migration_packet_v2(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != PACKET_TYPE:
        raise ValueError(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        raise ValueError("packet_version must be 2")
    if packet.get("mode") != "fixture_first_inactive_guardrail_predicate_rows_only":
        raise ValueError("mode must be fixture_first_inactive_guardrail_predicate_rows_only")
    if packet.get("attestations") != REQUIRED_ATTESTATIONS:
        raise ValueError("required no-live/no-active-mutation attestations are missing")

    predicate_rows = _dicts(packet.get("cited_fixture_only_guardrail_predicate_rows"))
    template_checks = _dicts(packet.get("before_after_explanation_template_checks"))
    blocked_checks = _dicts(packet.get("blocked_consequential_action_regression_checks"))
    rollback_rows = _dicts(packet.get("rollback_checkpoints"))
    owner_rows = _dicts(packet.get("reviewer_owner_fields"))
    commands = packet.get("offline_validation_commands")

    if not predicate_rows:
        raise ValueError("cited fixture-only guardrail predicate rows must be non-empty")
    if not template_checks:
        raise ValueError("before/after explanation-template checks must be non-empty")
    if not blocked_checks:
        raise ValueError("blocked consequential-action regression checks must be non-empty")
    if not rollback_rows:
        raise ValueError("rollback checkpoints must be non-empty")
    if not owner_rows:
        raise ValueError("reviewer-owner fields must be non-empty")
    if not isinstance(commands, list) or not commands or not all(isinstance(command, list) and command for command in commands):
        raise ValueError("offline validation commands must be non-empty command arrays")

    predicate_ids = {_required_text(row, "predicate_row_id") for row in predicate_rows}
    for index, row in enumerate(predicate_rows):
        path = f"cited_fixture_only_guardrail_predicate_rows[{index}]"
        for field in ("preview_id", "guardrail_bundle_id", "predicate_id", "before_predicate_state", "after_predicate_state", "approval_row_id", "reviewer_owner"):
            if not _text(row.get(field)):
                raise ValueError(f"{path}.{field} must be present")
        if row.get("fixture_only") is not True or row.get("inactive") is not True:
            raise ValueError(f"{path} must be inactive fixture-only")
        if row.get("active_guardrail_mutation") is not False or row.get("active_prompt_mutation") is not False:
            raise ValueError(f"{path} must keep active guardrail and prompt mutation false")
        _require_sha256(row, "before_fixture_checksum", path)
        _require_sha256(row, "after_fixture_checksum", path)
        if not _citations(row):
            raise ValueError(f"{path}.citations must be non-empty")

    for index, row in enumerate(template_checks):
        path = f"before_after_explanation_template_checks[{index}]"
        for field in ("template_check_id", "preview_id", "guardrail_bundle_id", "predicate_id", "before_template", "after_template", "delta_disposition", "reviewer_owner"):
            if not _text(row.get(field)):
                raise ValueError(f"{path}.{field} must be present")
        if row.get("fixture_only") is not True or row.get("active_prompt_mutation") is not False:
            raise ValueError(f"{path} must be fixture-only with active_prompt_mutation false")
        if not _citations(row):
            raise ValueError(f"{path}.citations must be non-empty")

    for index, row in enumerate(blocked_checks):
        path = f"blocked_consequential_action_regression_checks[{index}]"
        for field in ("regression_check_id", "preview_id", "guardrail_bundle_id", "action_id", "blocked_reason", "reviewer_owner"):
            if not _text(row.get(field)):
                raise ValueError(f"{path}.{field} must be present")
        if row.get("before_blocked") is not True or row.get("after_blocked") is not True:
            raise ValueError(f"{path} must keep consequential actions blocked before and after")
        if row.get("consequential_action_remains_blocked") is not True:
            raise ValueError(f"{path}.consequential_action_remains_blocked must be true")
        if not _citations(row):
            raise ValueError(f"{path}.citations must be non-empty")

    for index, row in enumerate(rollback_rows):
        path = f"rollback_checkpoints[{index}]"
        if row.get("active_guardrail_or_prompt_unchanged") is not True:
            raise ValueError(f"{path}.active_guardrail_or_prompt_unchanged must be true")
        if not _text(row.get("checkpoint_id")) or not _text(row.get("summary")):
            raise ValueError(f"{path} must include checkpoint_id and summary")
        if not _citations(row):
            raise ValueError(f"{path}.citations must be non-empty")

    for index, row in enumerate(owner_rows):
        if not _text(row.get("owner_field_id")) or not _text(row.get("reviewer_owner")):
            raise ValueError(f"reviewer_owner_fields[{index}] must include owner_field_id and reviewer_owner")
        linked = row.get("linked_row_ids")
        if not isinstance(linked, list) or not linked or not set(str(item) for item in linked).intersection(predicate_ids):
            raise ValueError(f"reviewer_owner_fields[{index}].linked_row_ids must reference guardrail predicate rows")
        if not _citations(row):
            raise ValueError(f"reviewer_owner_fields[{index}].citations must be non-empty")

    _reject_unsafe_content(packet, "$." )


def _approval_rows(matrix: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = matrix.get("approval_rows") or matrix.get("approvals") or matrix.get("rows") or matrix.get("matrix")
    if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes, bytearray)):
        return [row for row in rows if isinstance(row, Mapping)]
    return []


def _reviewer_owner_fields(*row_groups: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    flat_rows = [row for group in row_groups for row in group]
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in flat_rows:
        owner = _text(row.get("reviewer_owner"))
        bundle_id = _text(row.get("guardrail_bundle_id"))
        key = (owner, bundle_id)
        if not owner or not bundle_id or key in seen:
            continue
        seen.add(key)
        output.append(
            {
                "owner_field_id": f"owner-{_slug(owner)}-{_slug(bundle_id)}",
                "reviewer_owner": owner,
                "guardrail_bundle_id": bundle_id,
                "linked_row_ids": [
                    _text(item.get("predicate_row_id"))
                    for item in flat_rows
                    if _text(item.get("reviewer_owner")) == owner and _text(item.get("guardrail_bundle_id")) == bundle_id and _text(item.get("predicate_row_id"))
                ],
                "citations": _citations(row),
            }
        )
    return output


def _citation_strings(row: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("citations", "citation_ids", "source_evidence_ids", "evidence", "source_refs"):
        value = row.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            values.append(value.strip())
    return values


def _merge_citations(*groups: Any) -> list[Any]:
    merged: list[Any] = []
    seen: set[str] = set()
    for group in groups:
        values = group if isinstance(group, list) else [group]
        for value in values:
            if value in (None, "", [], {}):
                continue
            marker = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
            if marker not in seen:
                seen.add(marker)
                merged.append(value)
    return merged


def _citations(row: Mapping[str, Any]) -> list[Any]:
    value = row.get("citations")
    return value if isinstance(value, list) and value else []


def _checksum(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_sha256(row: Mapping[str, Any], key: str, path: str) -> None:
    value = _text(row.get(key))
    if len(value) != 64 or not all(char in "0123456789abcdef" for char in value.lower()):
        raise ValueError(f"{path}.{key} must be a sha256 hex checksum")


def _reject_unsafe_content(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}{key}"
            normalized_key = _normalize_key(key)
            if normalized_key in _PROHIBITED_KEYS and _present(child):
                raise ValueError(f"{child_path} is prohibited private, authenticated, raw, browser, DevHub, PDF, session, crawl, or LLM artifact content")
            if normalized_key in _MUTATION_KEYS and _present(child):
                raise ValueError(f"{child_path} contains an active guardrail, prompt, source, surface-registry, monitoring, release-state, or agent-state mutation flag")
            if normalized_key == "mutation_flags":
                _reject_mutation_flags(child, child_path)
            _reject_unsafe_content(child, f"{child_path}.")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}].")
    elif isinstance(value, str):
        normalized = _normalize_text(value)
        groups = (
            _PRIVATE_TEXT_TERMS,
            _RAW_ARTIFACT_TEXT_TERMS,
            _LIVE_EXECUTION_TEXT_TERMS,
            _OUTCOME_GUARANTEE_TEXT_TERMS,
            _CONSEQUENTIAL_ACTION_TEXT_TERMS,
        )
        if any(term in normalized for terms in groups for term in terms):
            raise ValueError(f"{path.rstrip('.')} contains prohibited private/authenticated fact, raw artifact, live execution, legal guarantee, consequential-action, or mutation language")


def _reject_mutation_flags(value: Any, path: str) -> None:
    if not isinstance(value, Mapping):
        return
    blocked = {
        "active_agent_state",
        "active_guardrail",
        "active_monitoring",
        "active_prompt",
        "active_release_state",
        "active_source",
        "active_surface_registry",
        "agent_state",
        "guardrail",
        "monitoring",
        "prompt",
        "release_state",
        "source",
        "surface_registry",
    }
    for key, child in value.items():
        normalized = _normalize_key(key)
        if normalized in blocked and _present(child):
            raise ValueError(f"{path}.{key} contains an active mutation flag")


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = _text(mapping.get(key))
    if not value:
        raise ValueError(f"{key} must be present")
    return value


def _row_id(row: Mapping[str, Any], index: int) -> str:
    for key in ("approval_row_id", "row_id", "id"):
        value = _text(row.get(key))
        if value:
            return value
    return f"approval-row-{index + 1}"


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").replace("_", " ").split())


def _slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part) or "item"
