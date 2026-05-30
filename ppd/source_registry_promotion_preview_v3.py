"""Validation for public source registry promotion preview v3.

The preview validator is intentionally side-effect free. It accepts a JSON-like
mapping and returns stable validation errors that callers can surface before any
registry promotion is allowed.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from urllib.parse import parse_qsl, urlparse

ALLOWED_PUBLIC_HOSTS = {
    "www.portland.gov",
    "portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
    "portlandmaps.com",
}

AUTH_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "code",
    "cookie",
    "jwt",
    "key",
    "password",
    "session",
    "sessionid",
    "sid",
    "signature",
    "token",
}

RAW_ARTIFACT_KEYS = {
    "archive_artifact_ref",
    "archive_path",
    "archive_url",
    "browser_artifact",
    "browser_state",
    "browser_trace",
    "download_path",
    "download_url",
    "downloaded_document",
    "downloaded_file",
    "downloaded_path",
    "har",
    "har_path",
    "html_body",
    "local_archive",
    "raw_archive",
    "raw_body",
    "raw_content",
    "raw_download",
    "raw_html",
    "screenshot",
    "screenshot_path",
    "trace",
    "trace_path",
    "warc_path",
}

COMPLETION_CLAIM_KEYS = {
    "crawler_completed",
    "live_crawl_complete",
    "live_crawl_completed",
    "live_crawler_completed",
    "processor_complete",
    "processor_completed",
    "processors_completed",
}

COMPLETION_CLAIM_PHRASES = (
    "crawl completed",
    "crawler completed",
    "finished live crawl",
    "live crawl completed",
    "live crawler completed",
    "processor completed",
    "processor finished",
    "processing completed",
)

OUTCOME_GUARANTEE_PHRASES = (
    "approval guaranteed",
    "guarantee approval",
    "guarantee permit",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legally compliant",
    "permit approval is guaranteed",
    "permit will be approved",
    "will be approved",
    "will be issued",
)

MUTATION_FLAG_TERMS = (
    "agent_state",
    "agent-state",
    "guardrail",
    "monitoring",
    "process",
    "prompt",
    "release_state",
    "release-state",
    "requirement",
    "schedule",
    "source",
)

MUTATION_ACTION_TERMS = (
    "active",
    "apply",
    "applied",
    "enable",
    "enabled",
    "mutate",
    "mutation",
    "patch",
    "publish",
    "set",
    "update",
    "write",
)

URL_FIELD_HINTS = ("url", "uri", "href", "link")


def validate_public_source_registry_promotion_preview_v3(preview: Mapping[str, object]) -> list[str]:
    """Return deterministic validation errors for a promotion preview payload."""

    errors: list[str] = []
    patches = _as_sequence(preview.get("patch_candidates"))
    if not patches:
        errors.append("patch_candidates: at least one patch candidate is required")
        patches = []

    dependency_order = _as_sequence(preview.get("dependency_order"))
    if not dependency_order:
        errors.append("dependency_order: dependency order is required")

    rollback_checkpoints = _as_sequence(preview.get("rollback_checkpoints"))
    if not rollback_checkpoints:
        errors.append("rollback_checkpoints: rollback checkpoints are required")

    patch_ids: list[str] = []
    for index, raw_patch in enumerate(patches):
        location = f"patch_candidates[{index}]"
        if not isinstance(raw_patch, Mapping):
            errors.append(f"{location}: patch candidate must be an object")
            continue
        patch = raw_patch
        patch_id = _string_value(patch.get("patch_id") or patch.get("id"))
        if patch_id:
            patch_ids.append(patch_id)
        else:
            errors.append(f"{location}.patch_id: patch candidate id is required")

        if not _has_nonempty_sequence(patch, "citations") and not _has_nonempty_sequence(patch, "source_evidence_ids"):
            errors.append(f"{location}.citations: uncited patch candidates are rejected")

        if not isinstance(patch.get("before_metadata"), Mapping) or not patch.get("before_metadata"):
            errors.append(f"{location}.before_metadata: before metadata is required")
        if not isinstance(patch.get("after_metadata"), Mapping) or not patch.get("after_metadata"):
            errors.append(f"{location}.after_metadata: after metadata is required")

        if not _has_nonempty_sequence(patch, "affected_source_ids"):
            errors.append(f"{location}.affected_source_ids: at least one affected source id is required")
        if not _has_nonempty_sequence(patch, "affected_requirement_ids"):
            errors.append(f"{location}.affected_requirement_ids: at least one affected requirement id is required")

        _collect_payload_errors(patch, location, errors)

    if dependency_order and patch_ids:
        ordered_ids = {_string_value(value) for value in dependency_order}
        missing_order = sorted(patch_id for patch_id in patch_ids if patch_id not in ordered_ids)
        for patch_id in missing_order:
            errors.append(f"dependency_order: missing patch id {patch_id}")

    if rollback_checkpoints and patch_ids:
        checkpoint_ids = _rollback_patch_ids(rollback_checkpoints)
        missing_checkpoints = sorted(patch_id for patch_id in patch_ids if patch_id not in checkpoint_ids)
        for patch_id in missing_checkpoints:
            errors.append(f"rollback_checkpoints: missing rollback checkpoint for patch id {patch_id}")

    _collect_payload_errors(preview, "preview", errors)
    return sorted(dict.fromkeys(errors))


def is_public_source_registry_promotion_preview_v3_valid(preview: Mapping[str, object]) -> bool:
    """Return True when the preview has no validation errors."""

    return not validate_public_source_registry_promotion_preview_v3(preview)


def _collect_payload_errors(value: object, location: str, errors: list[str]) -> None:
    for key_path, leaf in _walk(value, location):
        key_name = key_path.rsplit(".", 1)[-1].lower()
        normalized_key = key_name.replace("-", "_")

        if normalized_key in RAW_ARTIFACT_KEYS and _is_present(leaf):
            errors.append(f"{key_path}: raw body, download, archive, and browser artifacts are rejected")

        if normalized_key in COMPLETION_CLAIM_KEYS and leaf is True:
            errors.append(f"{key_path}: live crawler or processor completion claims are rejected")

        if _is_active_mutation_flag(normalized_key, leaf):
            errors.append(f"{key_path}: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected")

        if _looks_like_url_field(normalized_key) and isinstance(leaf, str):
            url_error = _validate_public_url(leaf)
            if url_error:
                errors.append(f"{key_path}: {url_error}")

        if isinstance(leaf, str):
            text = " ".join(leaf.lower().split())
            if any(phrase in text for phrase in COMPLETION_CLAIM_PHRASES):
                errors.append(f"{key_path}: live crawler or processor completion claims are rejected")
            if any(phrase in text for phrase in OUTCOME_GUARANTEE_PHRASES):
                errors.append(f"{key_path}: legal or permitting outcome guarantees are rejected")


def _validate_public_url(raw_url: str) -> str | None:
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"}:
        return "unsupported URL scheme is rejected"
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_PUBLIC_HOSTS:
        return "non-allowlisted URL is rejected"
    if parsed.username or parsed.password:
        return "authenticated URL is rejected"
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & AUTH_QUERY_KEYS:
        return "authenticated URL is rejected"
    path = parsed.path.lower()
    if any(part in path for part in ("/login", "/signin", "/sign-in", "/register", "/oauth", "/auth")):
        return "authenticated URL is rejected"
    return None


def _rollback_patch_ids(checkpoints: Sequence[object]) -> set[str]:
    patch_ids: set[str] = set()
    for checkpoint in checkpoints:
        if isinstance(checkpoint, str):
            patch_ids.add(checkpoint)
        elif isinstance(checkpoint, Mapping):
            patch_id = _string_value(checkpoint.get("patch_id") or checkpoint.get("id"))
            if patch_id:
                patch_ids.add(patch_id)
    return patch_ids


def _walk(value: object, location: str) -> Iterable[tuple[str, object]]:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_location = f"{location}.{key}"
            yield child_location, child
            yield from _walk(child, child_location)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            child_location = f"{location}[{index}]"
            yield child_location, child
            yield from _walk(child, child_location)


def _as_sequence(value: object) -> list[object]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _has_nonempty_sequence(mapping: Mapping[str, object], key: str) -> bool:
    value = mapping.get(key)
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _string_value(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _is_present(value: object) -> bool:
    return value is not None and value is not False and value != "" and value != [] and value != {}


def _looks_like_url_field(key: str) -> bool:
    return any(hint in key for hint in URL_FIELD_HINTS)


def _is_active_mutation_flag(key: str, value: object) -> bool:
    if value is not True:
        return False
    return any(term in key for term in MUTATION_FLAG_TERMS) and any(action in key for action in MUTATION_ACTION_TERMS)
