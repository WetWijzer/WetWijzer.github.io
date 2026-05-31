"""Fixture-first public change report packet v2 validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import parse_qsl, urlparse

_ALLOWED_HOSTS = frozenset({"www.portland.gov", "devhub.portlandoregon.gov", "www.portlandoregon.gov", "www.portlandmaps.com"})
_ALLOWED_REQUIREMENT_CHANGE_TYPES = frozenset({"added", "removed", "changed"})
_REQUIREMENT_CHANGE_ORDER = {"added": 0, "removed": 1, "changed": 2}
_PRIVATE_QUERY_KEYS = frozenset({"access_token", "api_key", "auth", "code", "cookie", "key", "password", "session", "sessionid", "sig", "signature", "state", "token"})
_RAW_OR_PRIVATE_KEY_PARTS = ("auth", "browser", "cookie", "credential", "download", "har", "local_path", "password", "private", "raw", "screenshot", "session", "storage_state", "trace")
_RAW_OR_PRIVATE_EXACT_KEYS = frozenset({"body", "content", "file_path", "html", "pdf_bytes", "pdf_path", "response_body", "text"})
_MUTATION_DOMAINS = ("source", "requirement", "process", "process_model", "guardrail", "prompt", "contract", "devhub_surface", "surface", "release_state")
_MUTATION_EXACT_KEYS = frozenset({"source_registry_updated", "requirement_registry_updated", "process_model_updated", "guardrail_bundle_updated", "prompt_updated", "contract_updated", "devhub_surface_updated", "release_state_updated"})
_LIVE_REEXTRACTION_KEYS = frozenset({"download_performed", "live_content_reextracted", "live_crawl_performed", "live_fetch_performed", "network_access_performed", "reextracted_live_content"})
_FORBIDDEN_TEXT_PHRASES = frozenset({"downloaded live", "fetched live", "live crawl", "live fetch", "live re-extraction completed", "recrawled live", "legal advice", "legally sufficient", "permit approval guaranteed", "permitting approval guaranteed", "guaranteed approval", "will be approved", "will receive a permit"})
_DEFAULT_REQUIRED_VALIDATION_COMMANDS = (("python3", "-m", "py_compile", "ppd/public_change_report_packet_v2.py"), ("python3", "-m", "py_compile", "ppd/tests/test_public_change_report_packet_v2.py"), ("python3", "-m", "pytest", "ppd/tests/test_public_change_report_packet_v2.py"), ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"))


class PublicChangeReportPacketV2Error(ValueError):
    """Raised when an offline public change report fixture is unsafe."""


def load_public_change_report_fixture_v2(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        fixture = json.load(handle)
    if not isinstance(fixture, dict):
        raise PublicChangeReportPacketV2Error("fixture must be a JSON object")
    return fixture


def build_public_change_report_packet_v2(fixture: Mapping[str, Any]) -> dict[str, Any]:
    _reject_raw_or_private_fields(fixture)
    _reject_forbidden_text(fixture)
    _reject_mutation_or_live_flags(fixture)

    if _required_text(fixture, "packet_version") != "public_change_report_packet_v2_fixture":
        raise PublicChangeReportPacketV2Error("packet_version must be public_change_report_packet_v2_fixture")
    if fixture.get("fixture_only") is not True:
        raise PublicChangeReportPacketV2Error("fixture_only must be true")
    if _required_text(fixture, "input_mode") != "synthetic_changed_source_hashes":
        raise PublicChangeReportPacketV2Error("input_mode must be synthetic_changed_source_hashes")

    side_effect_policy = _mapping(fixture.get("side_effect_policy"), "side_effect_policy")
    for key in ("live_content_reextracted", "active_requirements_mutated", "active_process_models_mutated", "active_guardrail_bundles_mutated", "active_source_registries_mutated"):
        _require_false(side_effect_policy, key)

    source_hashes = _source_hashes(fixture.get("synthetic_changed_source_hashes"))
    source_ids = {source["source_id"] for source in source_hashes}
    requirement_rows = _requirement_rows(fixture.get("requirement_deltas"), source_ids)
    validation_commands = _validation_commands(fixture.get("exact_offline_validation_commands"))

    change_types = {row["change_type"] for row in requirement_rows}
    if change_types != _ALLOWED_REQUIREMENT_CHANGE_TYPES:
        missing = sorted(_ALLOWED_REQUIREMENT_CHANGE_TYPES - change_types, key=lambda item: _REQUIREMENT_CHANGE_ORDER[item])
        raise PublicChangeReportPacketV2Error("requirement_deltas must cover added, removed, and changed rows; missing: " + ", ".join(missing))

    ordered_rows = sorted(requirement_rows, key=lambda row: (_REQUIREMENT_CHANGE_ORDER[row["change_type"]], row["requirement_id"]))
    for index, row in enumerate(ordered_rows, start=1):
        row["row_order"] = index

    affected_process_model_ids = sorted({process_id for row in ordered_rows for process_id in row["affected_process_model_ids"]})
    affected_guardrail_bundle_ids = sorted({bundle_id for row in ordered_rows for bundle_id in row["affected_guardrail_bundle_ids"]})

    return {
        "packet_type": "public_change_report_packet_v2",
        "packet_id": f"public-change-report-v2::{_required_text(fixture, 'packet_id')}",
        "generated_from": "synthetic_changed_source_hashes_fixture",
        "side_effect_policy": {"fixture_only": True, "live_content_reextracted": False, "active_requirements_mutated": False, "active_process_models_mutated": False, "active_guardrail_bundles_mutated": False, "active_source_registries_mutated": False},
        "synthetic_changed_source_hashes": source_hashes,
        "requirement_rows": ordered_rows,
        "affected_process_model_ids": affected_process_model_ids,
        "affected_guardrail_bundle_ids": affected_guardrail_bundle_ids,
        "reviewer_disposition_placeholders": [row["reviewer_disposition_placeholder"] for row in ordered_rows],
        "stale_source_carry_forward_notes": [row["stale_source_carry_forward_note"] for row in ordered_rows],
        "summary_counts": {"source_hashes": len(source_hashes), "added_requirement_rows": sum(1 for row in ordered_rows if row["change_type"] == "added"), "removed_requirement_rows": sum(1 for row in ordered_rows if row["change_type"] == "removed"), "changed_requirement_rows": sum(1 for row in ordered_rows if row["change_type"] == "changed"), "affected_process_models": len(affected_process_model_ids), "affected_guardrail_bundles": len(affected_guardrail_bundle_ids)},
        "exact_offline_validation_commands": [list(command) for command in validation_commands],
    }


def build_public_change_report_packet_v2_from_file(path: str | Path) -> dict[str, Any]:
    return build_public_change_report_packet_v2(load_public_change_report_fixture_v2(path))


def _source_hashes(value: Any) -> list[dict[str, Any]]:
    sources = _sequence_of_mappings(value, "synthetic_changed_source_hashes")
    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for source in sources:
        source_id = _required_text(source, "source_id")
        if source_id in seen_ids:
            raise PublicChangeReportPacketV2Error(f"duplicate source_id: {source_id}")
        seen_ids.add(source_id)
        previous_hash = _required_text(source, "previous_hash")
        current_hash = _required_text(source, "current_hash")
        if previous_hash == current_hash:
            raise PublicChangeReportPacketV2Error(f"{source_id} must use distinct changed-source hashes")
        result.append({"source_id": source_id, "canonical_url": _public_url(_required_text(source, "canonical_url"), source_id), "previous_hash": previous_hash, "current_hash": current_hash, "hash_status": _required_text(source, "hash_status"), "stale_source_carry_forward_note": _required_text(source, "stale_source_carry_forward_note"), "source_registry_mutated": False})
    if not result:
        raise PublicChangeReportPacketV2Error("synthetic_changed_source_hashes must not be empty")
    return result


def _requirement_rows(value: Any, source_ids: set[str]) -> list[dict[str, Any]]:
    deltas = _sequence_of_mappings(value, "requirement_deltas")
    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for delta in deltas:
        requirement_id = _required_text(delta, "requirement_id")
        if requirement_id in seen_ids:
            raise PublicChangeReportPacketV2Error(f"duplicate requirement_id: {requirement_id}")
        seen_ids.add(requirement_id)
        source_id = _required_text(delta, "source_id")
        if source_id not in source_ids:
            raise PublicChangeReportPacketV2Error(f"{requirement_id} references an unknown source_id")
        change_type = _required_text(delta, "change_type")
        if change_type not in _ALLOWED_REQUIREMENT_CHANGE_TYPES:
            raise PublicChangeReportPacketV2Error(f"unsupported requirement change_type: {change_type}")
        process_ids = _string_sequence(delta.get("affected_process_model_ids"), "affected_process_model_ids")
        guardrail_ids = _string_sequence(delta.get("affected_guardrail_bundle_ids"), "affected_guardrail_bundle_ids")
        reviewer_placeholder = _required_text(delta, "reviewer_disposition_placeholder")
        if "pending" not in reviewer_placeholder:
            raise PublicChangeReportPacketV2Error(f"{requirement_id} reviewer disposition placeholder must remain pending")
        result.append({"row_id": f"public-change-report-v2-{change_type}-{requirement_id}", "row_order": 0, "change_type": change_type, "requirement_id": requirement_id, "source_id": source_id, "requirement_summary": _required_text(delta, "requirement_summary"), "affected_process_model_ids": sorted(process_ids), "affected_guardrail_bundle_ids": sorted(guardrail_ids), "reviewer_disposition_placeholder": reviewer_placeholder, "stale_source_carry_forward_note": _required_text(delta, "stale_source_carry_forward_note"), "active_requirement_mutated": False})
    if not result:
        raise PublicChangeReportPacketV2Error("requirement_deltas must not be empty")
    return result


def _validation_commands(value: Any) -> tuple[tuple[str, ...], ...]:
    parsed = tuple(tuple(_string_sequence(command, "exact_offline_validation_commands item")) for command in _sequence(value, "exact_offline_validation_commands"))
    if not parsed:
        raise PublicChangeReportPacketV2Error("exact_offline_validation_commands must not be empty")
    if not set(_DEFAULT_REQUIRED_VALIDATION_COMMANDS).issubset(set(parsed)):
        raise PublicChangeReportPacketV2Error("exact_offline_validation_commands must include the public change report v2 offline checks")
    return parsed


def _reject_raw_or_private_fields(value: Any, path: str = "$." ) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = _normalized_key(key)
            if normalized in _RAW_OR_PRIVATE_EXACT_KEYS or any(part in normalized for part in _RAW_OR_PRIVATE_KEY_PARTS):
                raise PublicChangeReportPacketV2Error(f"raw or private field is not allowed at {path}{key}")
            _reject_raw_or_private_fields(child, f"{path}{key}.")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_raw_or_private_fields(child, f"{path}{index}.")


def _reject_forbidden_text(value: Any, path: str = "$" ) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        for phrase in _FORBIDDEN_TEXT_PHRASES:
            if phrase in lowered:
                raise PublicChangeReportPacketV2Error(f"forbidden live crawl, legal, or permitting guarantee claim is not allowed at {path}")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_forbidden_text(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_forbidden_text(child, f"{path}[{index}]")


def _reject_mutation_or_live_flags(value: Any, path: str = "$" ) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = _normalized_key(key)
            if normalized in _LIVE_REEXTRACTION_KEYS and child is not False:
                raise PublicChangeReportPacketV2Error(f"live re-extraction flag must be false at {path}.{key}")
            if _is_active_mutation_flag(normalized, child):
                raise PublicChangeReportPacketV2Error(f"active source, requirement, process-model, guardrail, prompt, contract, DevHub surface, or release-state mutation flag must be false at {path}.{key}")
            _reject_mutation_or_live_flags(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_mutation_or_live_flags(child, f"{path}[{index}]")


def _is_active_mutation_flag(normalized_key: str, value: Any) -> bool:
    if not _truthy(value):
        return False
    if normalized_key in _MUTATION_EXACT_KEYS:
        return True
    if "mutation" not in normalized_key and "mutated" not in normalized_key and "updated" not in normalized_key:
        return False
    if "active" not in normalized_key and "mutated" not in normalized_key and "updated" not in normalized_key:
        return False
    return any(domain in normalized_key for domain in _MUTATION_DOMAINS)


def _public_url(url: str, source_id: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise PublicChangeReportPacketV2Error(f"{source_id} canonical_url must use HTTPS")
    if parsed.hostname not in _ALLOWED_HOSTS:
        raise PublicChangeReportPacketV2Error(f"{source_id} canonical_url is outside the PP&D public allowlist")
    if parsed.username or parsed.password:
        raise PublicChangeReportPacketV2Error(f"{source_id} canonical_url must not include credentials")
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & _PRIVATE_QUERY_KEYS:
        raise PublicChangeReportPacketV2Error(f"{source_id} canonical_url contains private query parameters")
    return url


def _require_false(value: Mapping[str, Any], key: str) -> None:
    if value.get(key) is not False:
        raise PublicChangeReportPacketV2Error(f"{key} must be false")


def _mapping(value: Any, key: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PublicChangeReportPacketV2Error(f"{key} must be an object")
    return value


def _sequence(value: Any, key: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise PublicChangeReportPacketV2Error(f"{key} must be a list")
    return value


def _sequence_of_mappings(value: Any, key: str) -> tuple[Mapping[str, Any], ...]:
    items = _sequence(value, key)
    if not all(isinstance(item, Mapping) for item in items):
        raise PublicChangeReportPacketV2Error(f"{key} must be a list of objects")
    return tuple(items)


def _string_sequence(value: Any, key: str) -> tuple[str, ...]:
    result = []
    for item in _sequence(value, key):
        if not isinstance(item, str) or not item.strip():
            raise PublicChangeReportPacketV2Error(f"{key} must contain non-empty strings")
        result.append(item.strip())
    if not result:
        raise PublicChangeReportPacketV2Error(f"{key} must not be empty")
    return tuple(result)


def _required_text(value: Mapping[str, Any], key: str) -> str:
    child = value.get(key)
    if not isinstance(child, str) or not child.strip():
        raise PublicChangeReportPacketV2Error(f"{key} must be a non-empty string")
    return child.strip()


def _normalized_key(key: Any) -> str:
    return str(key).strip().lower().replace("-", "_").replace(" ", "_")


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "mutate", "mutated", "true", "yes"}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return False
