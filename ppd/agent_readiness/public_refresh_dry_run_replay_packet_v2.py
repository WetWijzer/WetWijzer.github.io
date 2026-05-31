"""Validation for public refresh dry-run replay packet v2.

The validator is intentionally side-effect free. It checks committed packet
metadata and evidence rows only; it does not crawl, download, archive, mutate,
or inspect private DevHub/session state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


PACKET_VERSION = 2

REQUIRED_ROW_KINDS: tuple[str, ...] = (
    "freshness",
    "changed_hash",
    "redirect_change",
    "skip_or_denial",
    "processor_handoff_failure",
    "no_raw_body_archive_decision",
    "requirement_or_guardrail_impact",
    "reviewer_hold",
    "retry_backoff_plan",
    "validation_command",
)

MUTATION_FLAG_NAMES: tuple[str, ...] = (
    "crawler_mutation",
    "source_mutation",
    "archive_mutation",
    "document_mutation",
    "requirement_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "contract_mutation",
    "devhub_surface_mutation",
    "release_state_mutation",
)

PRIVATE_ARTIFACT_KEYS: tuple[str, ...] = (
    "auth_state",
    "browser_artifact",
    "browser_trace",
    "cookie",
    "downloaded_artifact",
    "downloaded_document",
    "har",
    "local_private_path",
    "private_artifact",
    "raw_body",
    "raw_body_artifact",
    "raw_download",
    "screenshot",
    "session_artifact",
    "session_file",
    "session_state",
    "trace",
)

PRIVATE_ARTIFACT_VALUE_MARKERS: tuple[str, ...] = (
    "/private/",
    "auth-state",
    "auth_state",
    "browser-trace",
    "browser_trace",
    "cookies.json",
    "downloaded-document",
    "downloaded_document",
    "har.zip",
    "raw-body",
    "raw_body",
    "session-state",
    "session_state",
    "storage_state",
    "trace.zip",
)

LIVE_CRAWL_KEYS: tuple[str, ...] = (
    "active_crawl",
    "actual_crawl",
    "crawl_completed",
    "crawl_performed",
    "live_crawl",
    "live_crawl_claim",
    "live_crawl_performed",
    "network_crawl",
)

LEGAL_GUARANTEE_MARKERS: tuple[str, ...] = (
    "approval guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "guaranteed permit",
    "legal guarantee",
    "legally guaranteed",
    "permit guaranteed",
    "permitting guarantee",
)


@dataclass(frozen=True)
class ValidationError:
    """A deterministic validation error with a stable code and location."""

    code: str
    message: str
    path: str = "$"

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


class PublicRefreshDryRunReplayPacketV2Error(ValueError):
    """Raised when a packet fails strict validation."""

    def __init__(self, errors: Sequence[ValidationError]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(error.message for error in self.errors))


def validate_public_refresh_dry_run_replay_packet_v2(packet: Mapping[str, Any]) -> list[ValidationError]:
    """Return validation errors for a public refresh dry-run replay packet v2."""

    errors: list[ValidationError] = []

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(
            ValidationError(
                "invalid_packet_version",
                "public refresh dry-run replay packet must declare packet_version 2",
                "$.packet_version",
            )
        )

    if packet.get("packet_type") != "public_refresh_dry_run_replay":
        errors.append(
            ValidationError(
                "invalid_packet_type",
                "packet_type must be public_refresh_dry_run_replay",
                "$.packet_type",
            )
        )

    if packet.get("mode") != "dry_run":
        errors.append(
            ValidationError(
                "not_dry_run",
                "public refresh replay packets must be dry-run only",
                "$.mode",
            )
        )

    rows = packet.get("evidence_rows")
    if not isinstance(rows, list):
        errors.append(
            ValidationError(
                "missing_evidence_rows",
                "packet must include evidence_rows as a list",
                "$.evidence_rows",
            )
        )
        rows = []

    present_kinds = _row_kinds(rows)
    for required_kind in REQUIRED_ROW_KINDS:
        if required_kind not in present_kinds:
            errors.append(
                ValidationError(
                    f"missing_{required_kind}_row",
                    f"packet is missing required {required_kind} evidence row",
                    "$.evidence_rows",
                )
            )

    errors.extend(_validate_rows(rows))
    errors.extend(_validate_validation_commands(packet))
    errors.extend(_reject_private_artifacts(packet))
    errors.extend(_reject_live_crawl_claims(packet))
    errors.extend(_reject_legal_or_permitting_guarantees(packet))
    errors.extend(_reject_active_mutation_flags(packet))

    return errors


def assert_valid_public_refresh_dry_run_replay_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise a deterministic exception when the packet is invalid."""

    errors = validate_public_refresh_dry_run_replay_packet_v2(packet)
    if errors:
        raise PublicRefreshDryRunReplayPacketV2Error(errors)


def _row_kinds(rows: Sequence[Any]) -> set[str]:
    kinds: set[str] = set()
    for row in rows:
        if isinstance(row, Mapping) and isinstance(row.get("kind"), str):
            kinds.add(row["kind"])
    return kinds


def _validate_rows(rows: Sequence[Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for index, row in enumerate(rows):
        path = f"$.evidence_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(ValidationError("invalid_evidence_row", "each evidence row must be an object", path))
            continue
        if not isinstance(row.get("kind"), str) or not row.get("kind"):
            errors.append(ValidationError("missing_row_kind", "evidence row must include a non-empty kind", f"{path}.kind"))
        if row.get("status") not in {"observed", "planned", "blocked", "held", "validated"}:
            errors.append(
                ValidationError(
                    "invalid_row_status",
                    "evidence row status must be observed, planned, blocked, held, or validated",
                    f"{path}.status",
                )
            )
        if not isinstance(row.get("evidence"), str) or not row.get("evidence", "").strip():
            errors.append(ValidationError("missing_row_evidence", "evidence row must include non-empty evidence text", f"{path}.evidence"))
    return errors


def _validate_validation_commands(packet: Mapping[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    commands = packet.get("validation_commands")
    if not isinstance(commands, list) or not commands:
        return [
            ValidationError(
                "missing_validation_commands",
                "packet must include at least one validation command",
                "$.validation_commands",
            )
        ]
    for index, command in enumerate(commands):
        path = f"$.validation_commands[{index}]"
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            errors.append(
                ValidationError(
                    "invalid_validation_command",
                    "validation commands must be non-empty string arrays",
                    path,
                )
            )
    return errors


def _reject_private_artifacts(packet: Mapping[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for path, key, value in _walk(packet):
        normalized_key = key.lower() if key else ""
        if any(marker in normalized_key for marker in PRIVATE_ARTIFACT_KEYS):
            errors.append(
                ValidationError(
                    "private_artifact_reference",
                    "packet must not reference private, session, browser, raw, or downloaded artifacts",
                    path,
                )
            )
        if isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in PRIVATE_ARTIFACT_VALUE_MARKERS):
                errors.append(
                    ValidationError(
                        "private_artifact_reference",
                        "packet must not reference private, session, browser, raw, or downloaded artifacts",
                        path,
                    )
                )
    return _dedupe_errors(errors)


def _reject_live_crawl_claims(packet: Mapping[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for path, key, value in _walk(packet):
        normalized_key = key.lower() if key else ""
        if any(marker in normalized_key for marker in LIVE_CRAWL_KEYS) and value:
            errors.append(
                ValidationError(
                    "live_crawl_claim",
                    "dry-run replay packet must not claim a live crawl was performed",
                    path,
                )
            )
        if isinstance(value, str):
            lowered = value.lower()
            if "live crawl" in lowered and any(word in lowered for word in ("completed", "performed", "ran", "executed")):
                errors.append(
                    ValidationError(
                        "live_crawl_claim",
                        "dry-run replay packet must not claim a live crawl was performed",
                        path,
                    )
                )
    return _dedupe_errors(errors)


def _reject_legal_or_permitting_guarantees(packet: Mapping[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for path, _key, value in _walk(packet):
        if isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in LEGAL_GUARANTEE_MARKERS):
                errors.append(
                    ValidationError(
                        "legal_or_permitting_guarantee",
                        "packet must not include legal or permitting guarantees",
                        path,
                    )
                )
    return _dedupe_errors(errors)


def _reject_active_mutation_flags(packet: Mapping[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    flags = packet.get("mutation_flags")
    if flags is not None and not isinstance(flags, Mapping):
        errors.append(ValidationError("invalid_mutation_flags", "mutation_flags must be an object when present", "$.mutation_flags"))
        return errors

    if isinstance(flags, Mapping):
        for flag_name in MUTATION_FLAG_NAMES:
            if flags.get(flag_name):
                errors.append(
                    ValidationError(
                        "active_mutation_flag",
                        f"dry-run replay packet must not activate {flag_name}",
                        f"$.mutation_flags.{flag_name}",
                    )
                )

    for path, key, value in _walk(packet):
        if key in MUTATION_FLAG_NAMES and value:
            errors.append(
                ValidationError(
                    "active_mutation_flag",
                    f"dry-run replay packet must not activate {key}",
                    path,
                )
            )
    return _dedupe_errors(errors)


def _walk(value: Any, path: str = "$", key: str | None = None) -> Iterable[tuple[str, str | None, Any]]:
    yield path, key, value
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            yield from _walk(child_value, f"{path}.{child_key_text}", child_key_text)
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{path}[{index}]", None)


def _dedupe_errors(errors: Sequence[ValidationError]) -> list[ValidationError]:
    seen: set[tuple[str, str]] = set()
    deduped: list[ValidationError] = []
    for error in errors:
        key = (error.code, error.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(error)
    return deduped
