"""Validation for PP&D source observation patch application preview v2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


ALLOWLISTED_HOSTS = {
    "portland.gov",
    "www.portland.gov",
    "api.portland.gov",
    "efiles.portlandoregon.gov",
    "www.portlandmaps.com",
    "portlandmaps.com",
}

AUTH_QUERY_TOKENS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "bearer",
    "cookie",
    "key",
    "password",
    "session",
    "sessionid",
    "sid",
    "signature",
    "signed",
    "token",
}

RAW_ARTIFACT_KEYS = {
    "archive",
    "archive_path",
    "archived_body",
    "browser_artifact",
    "browser_artifacts",
    "browser_trace",
    "download",
    "download_path",
    "downloaded_document",
    "har",
    "html_body",
    "page_body",
    "raw",
    "raw_body",
    "raw_html",
    "response_body",
    "screenshot",
    "trace",
}

MUTATION_FLAG_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_schedule_mutation",
    "active_source_mutation",
    "agent_state_mutation",
    "guardrail_mutation",
    "monitoring_mutation",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_process",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_requirements",
    "mutates_schedules",
    "mutates_sources",
    "process_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "requirement_mutation",
    "schedule_mutation",
    "source_mutation",
}

LIVE_COMPLETION_CLAIMS = (
    "crawl completed",
    "crawler completed",
    "crawler finished",
    "live crawl completed",
    "live crawler completed",
    "processor completed",
    "processor finished",
    "processing completed",
)

OUTCOME_GUARANTEES = (
    "approval guaranteed",
    "approved permit guaranteed",
    "guarantee approval",
    "guarantee permit",
    "guaranteed approval",
    "guaranteed permit",
    "legal outcome guaranteed",
    "permit approval guaranteed",
    "permitting outcome guaranteed",
    "will be approved",
    "will receive a permit",
)


@dataclass(frozen=True)
class PreviewValidationResult:
    ok: bool
    errors: tuple[str, ...]


class PreviewValidationError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = tuple(errors)


def validate_source_observation_patch_preview_v2(payload: dict[str, Any]) -> PreviewValidationResult:
    errors = _collect_errors(payload)
    if errors:
        raise PreviewValidationError(errors)
    return PreviewValidationResult(ok=True, errors=())


def preview_v2_errors(payload: dict[str, Any]) -> tuple[str, ...]:
    return tuple(_collect_errors(payload))


def _collect_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["preview payload must be an object"]

    rows = payload.get("preview_rows", payload.get("rows"))
    if not isinstance(rows, list) or not rows:
        errors.append("preview rows are required")
        rows = []

    if not _nonempty(payload.get("affected_source_ids")):
        errors.append("affected source ids are required")
    if not _nonempty(payload.get("rollback_checkpoints")):
        errors.append("rollback checkpoints are required")

    for index, row in enumerate(rows):
        prefix = f"preview_rows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not _nonempty(row.get("citations")):
            errors.append(f"{prefix} citations are required")
        if not _nonempty(row.get("before_metadata")):
            errors.append(f"{prefix} before_metadata is required")
        if not _nonempty(row.get("after_metadata")):
            errors.append(f"{prefix} after_metadata is required")
        if not _nonempty(row.get("affected_source_ids")):
            errors.append(f"{prefix} affected_source_ids are required")
        if not _nonempty(row.get("rollback_checkpoint")):
            errors.append(f"{prefix} rollback_checkpoint is required")

    for path, value in _walk(payload):
        key = path[-1].lower() if path else ""
        if key in RAW_ARTIFACT_KEYS and _present(value):
            errors.append(f"{'.'.join(path)} raw/download/archive/browser artifacts are not allowed")
        if key in MUTATION_FLAG_KEYS and value is True:
            errors.append(f"{'.'.join(path)} active mutation flags are not allowed")
        if key.endswith("url") or key == "url":
            if isinstance(value, str) and value:
                url_error = _url_error(value)
                if url_error:
                    errors.append(f"{'.'.join(path)} {url_error}")
        if isinstance(value, str):
            lowered = " ".join(value.lower().split())
            if any(claim in lowered for claim in LIVE_COMPLETION_CLAIMS):
                errors.append(f"{'.'.join(path)} live crawler or processor completion claims are not allowed")
            if any(claim in lowered for claim in OUTCOME_GUARANTEES):
                errors.append(f"{'.'.join(path)} legal or permitting outcome guarantees are not allowed")

    return errors


def _url_error(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        return "must be an http(s) allowlisted URL"
    if parsed.username or parsed.password:
        return "authenticated URLs are not allowed"
    host = (parsed.hostname or "").lower()
    if host not in ALLOWLISTED_HOSTS:
        return "non-allowlisted URLs are not allowed"
    query_keys = {part.split("=", 1)[0].lower() for part in parsed.query.split("&") if part}
    if query_keys & AUTH_QUERY_TOKENS:
        return "authenticated URLs are not allowed"
    return None


def _walk(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    items: list[tuple[tuple[str, ...], Any]] = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_walk(child, path + (str(key),)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk(child, path + (str(index),)))
    return items


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True
