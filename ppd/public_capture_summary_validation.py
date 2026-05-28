"""Validation for public PP&D capture result summaries.

This module is intentionally small and data-shape tolerant. It validates plain
Python mappings before a capture result summary is exposed for review or marked
ready.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_PRIVATE_HOST_RE = re.compile(
    r"(^|\.)(localhost|local|internal|intranet)$|"
    r"(^|\.)(devhub|amanda|trakit|projectdox)(\.|$)",
    re.IGNORECASE,
)
_AUTH_URL_RE = re.compile(r"(token|session|auth|sso|login|password|secret|cookie)=", re.IGNORECASE)
_LOCAL_PATH_RE = re.compile(
    r"(^/|^[A-Za-z]:\\|\\\\|\.pdf$|\.docx?$|\.xlsx?$|/downloads?/|/raw/|/crawl/|/tmp/|/private/)",
    re.IGNORECASE,
)

_RAW_BODY_KEYS = {
    "body",
    "content",
    "document_body",
    "html",
    "page_html",
    "raw",
    "raw_body",
    "raw_content",
    "raw_html",
    "response_body",
    "text",
}

_PATH_KEYS = {
    "download_path",
    "downloaded_path",
    "downloaded_document_path",
    "file",
    "file_path",
    "local_path",
    "path",
    "pdf_path",
    "raw_path",
}

_READY_STATUSES = {"ready", "ready_for_review", "review_ready"}
_REVIEWED_STATUSES = {"approved", "reviewed", "verified"}


@dataclass(frozen=True)
class SummaryValidationError:
    """A deterministic validation error for a public capture summary."""

    code: str
    path: str
    message: str


def validate_public_capture_result_summary(summary: Mapping[str, Any]) -> list[SummaryValidationError]:
    """Return validation errors for a public capture result summary."""

    errors: list[SummaryValidationError] = []

    source_id = summary.get("source_id")
    if not isinstance(source_id, str) or not source_id.strip():
        errors.append(
            SummaryValidationError(
                "missing_source_id",
                "source_id",
                "Public capture summaries must include a non-empty source_id.",
            )
        )

    _validate_work_item_links(summary, errors)
    _walk(summary, "$", errors)
    _validate_hashes(summary, errors)
    _validate_ready_status(summary, errors)
    return errors


def assert_public_capture_result_summary(summary: Mapping[str, Any]) -> None:
    """Raise ValueError when a public capture result summary is not publishable."""

    errors = validate_public_capture_result_summary(summary)
    if errors:
        detail = "; ".join(f"{error.code} at {error.path}: {error.message}" for error in errors)
        raise ValueError(detail)


def _validate_work_item_links(summary: Mapping[str, Any], errors: list[SummaryValidationError]) -> None:
    for field in ("citations", "extractions"):
        value = summary.get(field)
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
            errors.append(
                SummaryValidationError(
                    f"missing_{field}_work_item_links",
                    field,
                    f"Public capture summaries must include at least one {field[:-1]} work-item link.",
                )
            )
            continue

        for index, item in enumerate(value):
            item_path = f"{field}[{index}]"
            if not isinstance(item, Mapping):
                errors.append(
                    SummaryValidationError(
                        f"invalid_{field}_work_item_link",
                        item_path,
                        f"{field[:-1].title()} work-item links must be objects.",
                    )
                )
                continue
            work_item_id = item.get("work_item_id") or item.get("work_item") or item.get("id")
            if not isinstance(work_item_id, str) or not work_item_id.strip():
                errors.append(
                    SummaryValidationError(
                        f"missing_{field}_work_item_id",
                        item_path,
                        f"{field[:-1].title()} links must include a work_item_id.",
                    )
                )


def _walk(value: Any, path: str, errors: list[SummaryValidationError]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized = key_text.lower()
            if normalized in _RAW_BODY_KEYS:
                errors.append(
                    SummaryValidationError(
                        "raw_body_field",
                        child_path,
                        "Public summaries must not include raw body, HTML, or full text fields.",
                    )
                )
            if normalized in _PATH_KEYS and isinstance(child, str) and _LOCAL_PATH_RE.search(child):
                errors.append(
                    SummaryValidationError(
                        "downloaded_document_path",
                        child_path,
                        "Public summaries must not include downloaded or local document paths.",
                    )
                )
            _walk(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _walk(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        _validate_string_value(value, path, errors)


def _validate_string_value(value: str, path: str, errors: list[SummaryValidationError]) -> None:
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"}:
        if parsed.username or parsed.password or _PRIVATE_HOST_RE.search(parsed.hostname or "") or _AUTH_URL_RE.search(parsed.query):
            errors.append(
                SummaryValidationError(
                    "private_or_authenticated_url",
                    path,
                    "Public summaries must not include private, authenticated, or credentialed URLs.",
                )
            )
    elif parsed.scheme in {"file", "s3", "gs"}:
        errors.append(
            SummaryValidationError(
                "downloaded_document_path",
                path,
                "Public summaries must not include local or private document locations.",
            )
        )


def _validate_hashes(summary: Mapping[str, Any], errors: list[SummaryValidationError]) -> None:
    verified_hashes = summary.get("verified_hashes") or summary.get("source_hashes") or []
    if isinstance(verified_hashes, Mapping):
        allowed = {str(value).lower() for value in verified_hashes.values() if isinstance(value, str)}
    elif isinstance(verified_hashes, Sequence) and not isinstance(verified_hashes, (str, bytes)):
        allowed = {str(value).lower() for value in verified_hashes if isinstance(value, str)}
    else:
        allowed = set()

    for hash_path, hash_value in _iter_hash_fields(summary):
        normalized = hash_value.lower()
        if _SHA256_RE.fullmatch(normalized) and normalized not in allowed:
            errors.append(
                SummaryValidationError(
                    "invented_hash",
                    hash_path,
                    "Hash fields must match a verified source_hashes or verified_hashes entry.",
                )
            )


def _iter_hash_fields(value: Any, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if "hash" in key_text.lower() or key_text.lower() in {"sha256", "digest"}:
                if isinstance(child, str):
                    found.append((child_path, child))
            found.extend(_iter_hash_fields(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            found.extend(_iter_hash_fields(child, f"{path}[{index}]"))
    return found


def _validate_ready_status(summary: Mapping[str, Any], errors: list[SummaryValidationError]) -> None:
    status = str(summary.get("guardrail_status") or summary.get("status") or "").lower()
    review_status = str(summary.get("review_status") or "").lower()
    if status in _READY_STATUSES and review_status not in _REVIEWED_STATUSES:
        errors.append(
            SummaryValidationError(
                "ready_before_review",
                "guardrail_status",
                "Guardrail status cannot be ready before review_status is reviewed, verified, or approved.",
            )
        )
