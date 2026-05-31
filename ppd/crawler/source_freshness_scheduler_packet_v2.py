from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

PACKET_TYPE = "ppd_source_freshness_scheduler_packet_v2"
PACKET_VERSION = "2.0"

REQUIRED_MUTATION_FLAGS = (
    "active_source_mutation",
    "active_requirement_mutation",
    "active_guardrail_mutation",
    "active_process_model_mutation",
    "active_contract_mutation",
    "active_prompt_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
)

REQUIRED_BOUNDARY_FALSE_FLAGS = (
    "live_crawl_performed",
    "live_crawl_claimed",
    "private_artifacts_committed",
    "raw_artifacts_committed",
    "downloaded_artifacts_committed",
)

_FORBIDDEN_TRUE_KEY_MARKERS = (
    "livecrawl",
    "livefetch",
    "livenetwork",
    "browsertrace",
    "sessionstate",
    "privateartifact",
    "rawartifact",
    "downloadedartifact",
    "sourcemutation",
    "requirementmutation",
    "guardrailmutation",
    "processmodelmutation",
    "processmutation",
    "contractmutation",
    "promptmutation",
    "devhubsurfacemutation",
    "releasestatemutation",
)

_FORBIDDEN_VALUE_MARKERS = (
    "auth_state",
    "browser_state",
    "cookie",
    "credential",
    "har",
    "playwright-trace",
    "raw_crawl",
    "raw-crawl",
    "session_cookie",
    "storage_state",
    "trace.zip",
    ".warc",
    "warc://",
    "/raw/",
    "/downloads/",
    "downloaded_documents",
    "downloaded-documents",
)

_GUARANTEE_MARKERS = (
    "guarantee approval",
    "guaranteed approval",
    "permit will be issued",
    "permit is guaranteed",
    "legal advice",
    "legally guarantees",
    "compliance guaranteed",
    "approval guaranteed",
)


@dataclass(frozen=True)
class SourceFreshnessSchedulerPacketV2ValidationResult:
    valid: bool
    errors: tuple[str, ...]


class SourceFreshnessSchedulerPacketV2Error(ValueError):
    pass


def validate_source_freshness_scheduler_packet_v2(packet: Mapping[str, Any]) -> SourceFreshnessSchedulerPacketV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return SourceFreshnessSchedulerPacketV2ValidationResult(False, ("packet must be an object",))

    _collect_forbidden_content(packet, "$", errors)

    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be " + PACKET_TYPE)
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be " + PACKET_VERSION)
    if not _text(packet.get("packet_id")):
        errors.append("packet_id is required")
    if not _text(packet.get("generated_at")).endswith("Z"):
        errors.append("generated_at must end in Z")
    for key in ("fixture_first", "metadata_only"):
        if packet.get(key) is not True:
            errors.append(key + " must be true")

    boundary = packet.get("side_effect_boundary")
    if not isinstance(boundary, Mapping):
        errors.append("side_effect_boundary must be an object")
    else:
        for key in REQUIRED_BOUNDARY_FALSE_FLAGS + REQUIRED_MUTATION_FLAGS:
            if boundary.get(key) is not False:
                errors.append("side_effect_boundary." + key + " must be false")
        for key, value in boundary.items():
            if _normalized_key(str(key)).endswith("allowed") and value is not False:
                errors.append("side_effect_boundary." + str(key) + " must be false")

    commands = _require_list(packet.get("validation_commands"), "validation_commands", errors)
    if not commands:
        errors.append("validation_commands must include at least one offline validation command")
    for index, command in enumerate(commands):
        if isinstance(command, str):
            if not command.strip():
                errors.append("validation_commands[" + str(index) + "] must not be empty")
        elif isinstance(command, list):
            if not command or not all(_text(part) for part in command):
                errors.append("validation_commands[" + str(index) + "] must include non-empty command parts")
        else:
            errors.append("validation_commands[" + str(index) + "] must be a string or list of strings")

    scheduler_rows = _require_list(packet.get("scheduler_rows"), "scheduler_rows", errors)
    if not scheduler_rows:
        errors.append("scheduler_rows must include at least one source freshness schedule row")

    for index, row in enumerate(scheduler_rows):
        prefix = "scheduler_rows[" + str(index) + "]"
        if not isinstance(row, Mapping):
            errors.append(prefix + " must be an object")
            continue
        for key in ("source_id", "canonical_url", "source_anchor", "recrawl_frequency", "stale_source_hold_triggers"):
            if key == "stale_source_hold_triggers":
                if not _text_list(row.get(key)):
                    errors.append(prefix + "." + key + " must not be empty")
            elif not _text(row.get(key)):
                errors.append(prefix + "." + key + " is required")
        if not _text_list(row.get("affected_surface_categories")):
            errors.append(prefix + ".affected_surface_categories must not be empty")
        if not _text(row.get("skipped_authenticated_url_note")):
            errors.append(prefix + ".skipped_authenticated_url_note is required")
        if not _text_list(row.get("source_anchor_citations")):
            errors.append(prefix + ".source_anchor_citations must not be empty")
        if not _text(row.get("recrawl_frequency")).strip().lower() in {"daily", "every_few_days", "weekly", "monthly", "quarterly"}:
            errors.append(prefix + ".recrawl_frequency must be daily, every_few_days, weekly, monthly, or quarterly")
        if _text(row.get("skip_reason")).strip().lower() == "authenticated" and not _text(row.get("skipped_authenticated_url_note")):
            errors.append(prefix + ".skipped_authenticated_url_note is required for authenticated skips")

    summary = packet.get("packet_summary")
    if not isinstance(summary, Mapping):
        errors.append("packet_summary must be an object")
    else:
        if summary.get("scheduler_row_count") != len(scheduler_rows):
            errors.append("packet_summary.scheduler_row_count must match scheduler_rows length")

    return SourceFreshnessSchedulerPacketV2ValidationResult(not errors, tuple(dict.fromkeys(errors)))


def require_valid_source_freshness_scheduler_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_source_freshness_scheduler_packet_v2(packet)
    if not result.valid:
        raise SourceFreshnessSchedulerPacketV2Error("; ".join(result.errors))


def _collect_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = _normalized_key(key_text)
            if any(marker in normalized for marker in _FORBIDDEN_TRUE_KEY_MARKERS) and child not in (None, "", [], {}, False):
                errors.append(path + "." + key_text + " must be false or empty")
            _collect_forbidden_content(child, path + "." + key_text, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_forbidden_content(child, path + "[" + str(index) + "]", errors)
    elif isinstance(value, str):
        lowered = value.lower()
        for marker in _FORBIDDEN_VALUE_MARKERS:
            if marker in lowered:
                errors.append(path + " contains forbidden private, session, browser, raw, or downloaded artifact marker " + marker)
        for marker in _GUARANTEE_MARKERS:
            if marker in lowered:
                errors.append(path + " contains forbidden legal or permitting guarantee marker " + marker)


def _require_list(value: Any, field: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(field + " must be a list")
        return []
    return value


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_text(row) for row in value if _text(row)]
    return []


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else default
    return default


def _normalized_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


__all__ = [
    "PACKET_TYPE",
    "PACKET_VERSION",
    "SourceFreshnessSchedulerPacketV2Error",
    "SourceFreshnessSchedulerPacketV2ValidationResult",
    "require_valid_source_freshness_scheduler_packet_v2",
    "validate_source_freshness_scheduler_packet_v2",
]
