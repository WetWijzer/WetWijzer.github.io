from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.devhub_surface_patch_application_preview_v2 import (
    build_devhub_surface_patch_application_preview_v2_from_fixture,
    validate_devhub_surface_patch_application_preview_v2,
)
from ppd.validation.offline_patch_migration_approval_matrix_v2 import (
    validate_offline_patch_migration_approval_matrix_v2,
)

PACKET_TYPE = "ppd.inactive_devhub_surface_fixture_migration_packet.v2"
PACKET_VERSION = 2

REQUIRED_ATTESTATIONS = {
    "no_live_devhub": True,
    "no_auth_state": True,
    "no_screenshot": True,
    "no_trace": True,
    "no_har": True,
    "no_active_surface_registry_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/inactive_devhub_surface_fixture_migration_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_devhub_surface_fixture_migration_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_PROHIBITED_KEYS = {
    "access_token",
    "auth_state",
    "authorization",
    "browser_context_state",
    "cookie",
    "credentials",
    "devhub_session_file",
    "har",
    "har_path",
    "password",
    "private_value",
    "screenshot",
    "screenshot_path",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "trace_path",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "apply_surface_registry_changes",
    "mutates_surface_registry",
    "surface_registry_mutation",
    "surface_registry_mutation_enabled",
    "surface_registry_write",
    "update_surface_registry",
}

_PROHIBITED_TEXT = (
    "access token",
    "auth state",
    "browser automation completed",
    "cookie value",
    "devhub live run completed",
    "devhub session",
    "final payment",
    "final submission",
    "guaranteed approval",
    "har file",
    "opened devhub",
    "permit will be approved",
    "playwright trace",
    "private devhub value",
    "schedule inspection",
    "screenshot file",
    "storage-state.json",
    "submit application",
    "submit payment",
    "trace.zip",
    "upload correction",
)


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_inactive_devhub_surface_fixture_migration_packet_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = load_json(fixture_path)
    base = fixture_path.parent
    preview = build_devhub_surface_patch_application_preview_v2_from_fixture(
        base / _required_text(fixture, "devhub_surface_patch_application_preview_v2_fixture")
    )
    matrix = load_json(base / _required_text(fixture, "offline_patch_migration_approval_matrix_v2_fixture"))
    return build_inactive_devhub_surface_fixture_migration_packet_v2(preview, matrix)


def build_inactive_devhub_surface_fixture_migration_packet_v2(
    devhub_surface_patch_application_preview_v2: Mapping[str, Any],
    offline_patch_migration_approval_matrix_v2: Mapping[str, Any],
) -> dict[str, Any]:
    preview_result = validate_devhub_surface_patch_application_preview_v2(devhub_surface_patch_application_preview_v2)
    if not preview_result.ok:
        raise ValueError("invalid DevHub surface patch application preview v2: " + "; ".join(preview_result.errors))

    matrix_result = validate_offline_patch_migration_approval_matrix_v2(offline_patch_migration_approval_matrix_v2)
    if not matrix_result.ok:
        raise ValueError("invalid offline patch migration approval matrix v2: " + "; ".join(error.code for error in matrix_result.errors))

    approvals = [row for row in _approval_rows(offline_patch_migration_approval_matrix_v2) if _text(row.get("decision")).lower() == "approve"]
    if not approvals:
        raise ValueError("offline patch migration approval matrix v2 must include at least one approve row")

    surface_rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []
    selector_checks: list[dict[str, Any]] = []
    handoff_rows: list[dict[str, Any]] = []
    redaction_rows: list[dict[str, Any]] = []
    rollback_rows: list[dict[str, Any]] = []

    previews = _dicts(devhub_surface_patch_application_preview_v2.get("surface_registry_fixture_patch_previews"))
    for index, preview in enumerate(previews):
        approval = approvals[index % len(approvals)]
        approval_id = _row_id(approval, index)
        reviewer_owner = _text(preview.get("reviewer_owner")) or _text(approval.get("reviewer_owner"))
        surface_id = _required_text(preview, "surface_id")
        preview_id = _required_text(preview, "preview_id")
        citations = _merge_citations(_citations(preview), _citation_strings(approval))

        surface_row_id = f"inactive-devhub-surface-fixture-{_slug(surface_id)}"
        surface_rows.append(
            {
                "surface_patch_row_id": surface_row_id,
                "preview_id": preview_id,
                "surface_id": surface_id,
                "affected_surface_ids": _strings(preview.get("affected_surface_ids")) or [surface_id],
                "row_state": "inactive_fixture_only_surface_patch",
                "fixture_only": True,
                "inactive": True,
                "active_surface_registry_mutation": False,
                "approval_row_id": approval_id,
                "approval_decision": "approve",
                "reviewer_owner": reviewer_owner,
                "citations": citations,
                "before_fixture_checksum": _checksum(_dicts(preview.get("before_synthetic_action_rows"))),
                "after_fixture_checksum": _checksum(_dicts(preview.get("after_synthetic_action_rows"))),
            }
        )

        for phase, key in (("before", "before_synthetic_action_rows"), ("after", "after_synthetic_action_rows")):
            for action_index, action in enumerate(_dicts(preview.get(key))):
                action_rows.append(
                    {
                        "action_patch_row_id": f"inactive-devhub-action-fixture-{_slug(surface_id)}-{phase}-{action_index + 1}",
                        "surface_patch_row_id": surface_row_id,
                        "preview_id": preview_id,
                        "surface_id": surface_id,
                        "phase": phase,
                        "synthetic_action": _required_text(action, "synthetic_action"),
                        "row_state": _required_text(action, "row_state"),
                        "fixture_only": True,
                        "inactive": True,
                        "active_surface_registry_mutation": False,
                        "reviewer_owner": reviewer_owner,
                        "citations": _merge_citations(citations, _citations(action)),
                    }
                )

        for delta in _dicts(preview.get("selector_confidence_deltas")):
            selector_checks.append(
                {
                    "selector_check_id": f"selector-confidence-{_slug(surface_id)}",
                    "surface_patch_row_id": surface_row_id,
                    "preview_id": preview_id,
                    "surface_id": surface_id,
                    "before_confidence": _required_text(delta, "before_confidence"),
                    "after_confidence": _required_text(delta, "after_confidence"),
                    "delta_disposition": _required_text(delta, "delta_disposition"),
                    "fixture_only": True,
                    "reviewer_owner": reviewer_owner,
                    "citations": _merge_citations(citations, _citations(delta)),
                }
            )

        handoff = _mapping(preview.get("manual_handoff_disposition"))
        handoff_rows.append(
            {
                "manual_handoff_disposition_id": f"manual-handoff-{_slug(surface_id)}",
                "surface_patch_row_id": surface_row_id,
                "preview_id": preview_id,
                "surface_id": surface_id,
                "required": handoff.get("required") is True,
                "reason": _required_text(handoff, "reason"),
                "fixture_only": True,
                "reviewer_owner": reviewer_owner,
                "citations": _merge_citations(citations, _citations(handoff)),
            }
        )

        redaction = _mapping(preview.get("redaction_disposition"))
        redaction_rows.append(
            {
                "redaction_disposition_id": f"redaction-{_slug(surface_id)}",
                "surface_patch_row_id": surface_row_id,
                "preview_id": preview_id,
                "surface_id": surface_id,
                "disposition": _required_text(redaction, "disposition"),
                "reason": _required_text(redaction, "reason"),
                "fixture_only": True,
                "reviewer_owner": reviewer_owner,
                "citations": _merge_citations(citations, _citations(redaction)),
            }
        )

        rollback_rows.append(
            {
                "checkpoint_id": f"rollback-inactive-devhub-surface-fixture-{_slug(surface_id)}",
                "surface_patch_row_id": surface_row_id,
                "preview_id": preview_id,
                "surface_id": surface_id,
                "summary": _required_text(preview, "rollback_checkpoint"),
                "rollback_action": "discard_fixture_only_surface_and_action_patch_rows_and_rebuild_from_preview",
                "active_surface_registry_unchanged": True,
                "reviewer_owner": reviewer_owner,
                "citations": citations,
            }
        )

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": "inactive-devhub-surface-fixture-migration-packet-v2",
        "mode": "fixture_first_inactive_devhub_surface_action_patch_rows_only",
        "consumes": {
            "devhub_surface_patch_application_preview_v2": _text(devhub_surface_patch_application_preview_v2.get("preview_type")),
            "offline_patch_migration_approval_matrix_v2": "offline_patch_migration_approval_matrix_v2",
        },
        "cited_fixture_only_surface_patch_rows": surface_rows,
        "cited_fixture_only_action_patch_rows": action_rows,
        "selector_confidence_before_after_checks": selector_checks,
        "manual_handoff_dispositions": handoff_rows,
        "redaction_dispositions": redaction_rows,
        "rollback_checkpoints": rollback_rows,
        "reviewer_owner_fields": _reviewer_owner_fields(surface_rows),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    validate_inactive_devhub_surface_fixture_migration_packet_v2(packet)
    return packet


def validate_inactive_devhub_surface_fixture_migration_packet_v2(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != PACKET_TYPE:
        raise ValueError(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        raise ValueError("packet_version must be 2")
    if packet.get("mode") != "fixture_first_inactive_devhub_surface_action_patch_rows_only":
        raise ValueError("mode must be fixture_first_inactive_devhub_surface_action_patch_rows_only")
    if packet.get("attestations") != REQUIRED_ATTESTATIONS:
        raise ValueError("required no-live-DevHub/no-auth-state/no-screenshot/no-trace/no-HAR/no-active-surface-registry-mutation attestations are missing")

    surface_rows = _dicts(packet.get("cited_fixture_only_surface_patch_rows"))
    action_rows = _dicts(packet.get("cited_fixture_only_action_patch_rows"))
    selector_checks = _dicts(packet.get("selector_confidence_before_after_checks"))
    handoff_rows = _dicts(packet.get("manual_handoff_dispositions"))
    redaction_rows = _dicts(packet.get("redaction_dispositions"))
    rollback_rows = _dicts(packet.get("rollback_checkpoints"))
    owner_rows = _dicts(packet.get("reviewer_owner_fields"))
    commands = packet.get("offline_validation_commands")

    if not surface_rows:
        raise ValueError("cited fixture-only surface patch rows must be non-empty")
    if not action_rows:
        raise ValueError("cited fixture-only action patch rows must be non-empty")
    if not selector_checks:
        raise ValueError("selector-confidence before/after checks must be non-empty")
    if not handoff_rows:
        raise ValueError("manual-handoff dispositions must be non-empty")
    if not redaction_rows:
        raise ValueError("redaction dispositions must be non-empty")
    if not rollback_rows:
        raise ValueError("rollback checkpoints must be non-empty")
    if not owner_rows:
        raise ValueError("reviewer-owner fields must be non-empty")
    if not isinstance(commands, list) or not commands or not all(isinstance(command, list) and command for command in commands):
        raise ValueError("offline validation commands must be non-empty command arrays")

    surface_row_ids = {_required_text(row, "surface_patch_row_id") for row in surface_rows}
    for index, row in enumerate(surface_rows):
        path = f"cited_fixture_only_surface_patch_rows[{index}]"
        _require_fields(row, path, ("preview_id", "surface_id", "row_state", "approval_row_id", "reviewer_owner"))
        if row.get("fixture_only") is not True or row.get("inactive") is not True:
            raise ValueError(f"{path} must be inactive fixture-only")
        if row.get("active_surface_registry_mutation") is not False:
            raise ValueError(f"{path} must keep active_surface_registry_mutation false")
        _require_sha256(row, "before_fixture_checksum", path)
        _require_sha256(row, "after_fixture_checksum", path)
        _require_citations(row, path)

    for index, row in enumerate(action_rows):
        path = f"cited_fixture_only_action_patch_rows[{index}]"
        _require_fields(row, path, ("action_patch_row_id", "surface_patch_row_id", "preview_id", "surface_id", "phase", "synthetic_action", "row_state", "reviewer_owner"))
        if row.get("surface_patch_row_id") not in surface_row_ids:
            raise ValueError(f"{path}.surface_patch_row_id must reference a surface patch row")
        if row.get("fixture_only") is not True or row.get("inactive") is not True:
            raise ValueError(f"{path} must be inactive fixture-only")
        if row.get("active_surface_registry_mutation") is not False:
            raise ValueError(f"{path} must keep active_surface_registry_mutation false")
        _require_citations(row, path)

    for index, row in enumerate(selector_checks):
        path = f"selector_confidence_before_after_checks[{index}]"
        _require_fields(row, path, ("selector_check_id", "surface_patch_row_id", "surface_id", "before_confidence", "after_confidence", "delta_disposition", "reviewer_owner"))
        _require_citations(row, path)

    for index, row in enumerate(handoff_rows):
        path = f"manual_handoff_dispositions[{index}]"
        _require_fields(row, path, ("manual_handoff_disposition_id", "surface_patch_row_id", "surface_id", "reason", "reviewer_owner"))
        if "required" not in row:
            raise ValueError(f"{path}.required must be present")
        _require_citations(row, path)

    for index, row in enumerate(redaction_rows):
        path = f"redaction_dispositions[{index}]"
        _require_fields(row, path, ("redaction_disposition_id", "surface_patch_row_id", "surface_id", "disposition", "reason", "reviewer_owner"))
        _require_citations(row, path)

    for index, row in enumerate(rollback_rows):
        path = f"rollback_checkpoints[{index}]"
        _require_fields(row, path, ("checkpoint_id", "surface_patch_row_id", "surface_id", "summary", "rollback_action", "reviewer_owner"))
        if row.get("active_surface_registry_unchanged") is not True:
            raise ValueError(f"{path}.active_surface_registry_unchanged must be true")
        _require_citations(row, path)

    for index, row in enumerate(owner_rows):
        if not _text(row.get("owner_field_id")) or not _text(row.get("reviewer_owner")):
            raise ValueError(f"reviewer_owner_fields[{index}] must include owner_field_id and reviewer_owner")
        linked = row.get("linked_row_ids")
        if not isinstance(linked, list) or not linked or not set(str(item) for item in linked).intersection(surface_row_ids):
            raise ValueError(f"reviewer_owner_fields[{index}].linked_row_ids must reference surface patch rows")
        _require_citations(row, f"reviewer_owner_fields[{index}]")

    _reject_unsafe_content(packet, "$." )


def _approval_rows(matrix: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = matrix.get("approval_rows") or matrix.get("approvals") or matrix.get("rows") or matrix.get("matrix")
    if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes, bytearray)):
        return [row for row in rows if isinstance(row, Mapping)]
    return []


def _reviewer_owner_fields(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        owner = _text(row.get("reviewer_owner"))
        if not owner or owner in seen:
            continue
        seen.add(owner)
        linked = [_text(item.get("surface_patch_row_id")) for item in rows if _text(item.get("reviewer_owner")) == owner]
        output.append(
            {
                "owner_field_id": f"owner-{_slug(owner)}",
                "reviewer_owner": owner,
                "linked_row_ids": linked,
                "citations": _citations(row),
            }
        )
    return output


def _require_fields(row: Mapping[str, Any], path: str, fields: tuple[str, ...]) -> None:
    for field in fields:
        if not _text(row.get(field)):
            raise ValueError(f"{path}.{field} must be present")


def _require_citations(row: Mapping[str, Any], path: str) -> None:
    if not _citations(row):
        raise ValueError(f"{path}.citations must be non-empty")


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


def _checksum(value: Any) -> str:
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
            normalized = _normalize_key(key)
            if normalized in _PROHIBITED_KEYS and _present(child):
                raise ValueError(f"{child_path} is prohibited private, authenticated, session, screenshot, trace, or HAR content")
            if normalized in _MUTATION_KEYS and _active_flag(child):
                raise ValueError(f"{child_path} contains an active mutation flag")
            _reject_unsafe_content(child, f"{child_path}.")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}].")
    elif isinstance(value, str):
        normalized = " ".join(value.lower().replace("-", " ").replace("_", " ").split())
        if any(term in normalized for term in _PROHIBITED_TEXT):
            raise ValueError(f"{path.rstrip('.')} contains prohibited private/authenticated, live DevHub, browser artifact, outcome guarantee, or consequential action language")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []


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


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part) or "item"
