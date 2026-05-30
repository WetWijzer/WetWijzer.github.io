"""Validation for inactive public-source recrawl patch previews.

The preview format is intentionally conservative: it may describe inactive source
rows and placeholder deltas, but it must not claim live crawling, persist raw or
private artifacts, mutate prompts, mutate active artifacts, or promise legal or
permitting outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


APPROVED_DISPOSITIONS = frozenset(
    {
        "inactive_patch_preview",
        "metadata_placeholder_only",
        "no_op_preview",
        "rejected_input",
    }
)

REQUIRED_DELTA_PLACEHOLDERS = (
    "source_registry_delta",
    "archive_manifest_delta",
    "normalized_document_reference_delta",
)

FORBIDDEN_TEXT_PATTERNS = (
    ("raw_crawl_artifact", "raw crawl artifact"),
    ("raw crawl", "raw crawl artifact"),
    ("downloaded document", "downloaded artifact"),
    ("downloaded pdf", "downloaded artifact"),
    ("private artifact", "private artifact"),
    ("private devhub", "private artifact"),
    ("auth state", "private artifact"),
    ("cookie", "private artifact"),
    ("session storage", "private artifact"),
    ("live crawl", "live crawl claim"),
    ("crawled live", "live crawl claim"),
    ("fetched live", "live crawl claim"),
    ("downloaded live", "live crawl claim"),
    ("guarantee approval", "legal or permitting guarantee"),
    ("guaranteed approval", "legal or permitting guarantee"),
    ("permit will be approved", "legal or permitting guarantee"),
    ("legally sufficient", "legal or permitting guarantee"),
    ("legal advice", "legal or permitting guarantee"),
    ("submit permit", "consequential DevHub language"),
    ("certify acknowledgement", "consequential DevHub language"),
    ("pay fee", "consequential DevHub language"),
    ("schedule inspection", "consequential DevHub language"),
    ("upload correction", "consequential DevHub language"),
    ("purchase trade permit", "consequential DevHub language"),
    ("cancel permit", "consequential DevHub language"),
)

MUTATION_FLAG_KEYS = frozenset(
    {
        "active_artifact_mutation",
        "active_artifact_mutation_enabled",
        "mutates_active_artifacts",
        "prompt_mutation",
        "prompt_mutation_enabled",
        "mutates_prompts",
    }
)


@dataclass(frozen=True)
class PreviewValidationIssue:
    """One deterministic validation failure for a patch preview payload."""

    code: str
    message: str
    path: str


class PublicSourceRecrawlInactivePatchPreviewError(ValueError):
    """Raised when an inactive recrawl patch preview is not safe to accept."""

    def __init__(self, issues: Sequence[PreviewValidationIssue]) -> None:
        self.issues = tuple(issues)
        details = "; ".join(f"{issue.path}: {issue.message}" for issue in self.issues)
        super().__init__(details)


def validate_public_source_recrawl_inactive_patch_preview_v1(
    payload: Mapping[str, Any]
) -> None:
    """Reject unsafe or incomplete inactive recrawl patch preview payloads.

    The function is intentionally side-effect free and accepts only already
    materialized mappings, so validation can run in daemon self-tests and fixture
    checks without touching the network, browser state, prompts, or artifacts.
    """

    issues = list(iter_public_source_recrawl_inactive_patch_preview_v1_issues(payload))
    if issues:
        raise PublicSourceRecrawlInactivePatchPreviewError(issues)


def iter_public_source_recrawl_inactive_patch_preview_v1_issues(
    payload: Mapping[str, Any]
) -> Iterable[PreviewValidationIssue]:
    if not isinstance(payload, Mapping):
        yield PreviewValidationIssue(
            "invalid_payload",
            "preview payload must be a mapping",
            "$",
        )
        return

    if payload.get("preview_version") != "public_source_recrawl_inactive_patch_preview_v1":
        yield PreviewValidationIssue(
            "invalid_preview_version",
            "preview_version must be public_source_recrawl_inactive_patch_preview_v1",
            "$.preview_version",
        )

    rows = payload.get("inactive_patch_preview_rows")
    if not isinstance(rows, list) or not rows:
        yield PreviewValidationIssue(
            "missing_inactive_patch_preview_rows",
            "inactive patch preview rows are required",
            "$.inactive_patch_preview_rows",
        )
    else:
        for index, row in enumerate(rows):
            path = f"$.inactive_patch_preview_rows[{index}]"
            if not isinstance(row, Mapping):
                yield PreviewValidationIssue(
                    "invalid_inactive_patch_preview_row",
                    "inactive patch preview row must be a mapping",
                    path,
                )
                continue
            disposition = row.get("disposition")
            if disposition not in APPROVED_DISPOSITIONS:
                yield PreviewValidationIssue(
                    "unapproved_disposition",
                    "inactive patch preview row disposition is not approved",
                    f"{path}.disposition",
                )

    placeholders = payload.get("delta_placeholders")
    if not isinstance(placeholders, Mapping):
        yield PreviewValidationIssue(
            "missing_delta_placeholders",
            "source, archive, and normalized document delta placeholders are required",
            "$.delta_placeholders",
        )
    else:
        for key in REQUIRED_DELTA_PLACEHOLDERS:
            value = placeholders.get(key)
            if not isinstance(value, Mapping) or value.get("placeholder") is not True:
                yield PreviewValidationIssue(
                    f"missing_{key}",
                    f"{key} placeholder is required",
                    f"$.delta_placeholders.{key}",
                )

    replay_notes = payload.get("freshness_monitor_replay_notes")
    if not _non_empty_string_sequence(replay_notes):
        yield PreviewValidationIssue(
            "missing_freshness_monitor_replay_notes",
            "freshness monitor replay notes are required",
            "$.freshness_monitor_replay_notes",
        )

    validation_commands = payload.get("validation_commands")
    if not _valid_validation_commands(validation_commands):
        yield PreviewValidationIssue(
            "missing_validation_commands",
            "validation commands must be a non-empty list of command token lists",
            "$.validation_commands",
        )

    for path, value in _walk(payload):
        if isinstance(value, bool) and path.rsplit(".", 1)[-1] in MUTATION_FLAG_KEYS and value:
            yield PreviewValidationIssue(
                "active_artifact_or_prompt_mutation_flag",
                "active artifact and prompt mutation flags must be absent or false",
                path,
            )
        if isinstance(value, str):
            lowered = value.lower()
            for pattern, label in FORBIDDEN_TEXT_PATTERNS:
                if pattern in lowered:
                    yield PreviewValidationIssue(
                        _code_for_forbidden_label(label),
                        f"preview contains forbidden {label}",
                        path,
                    )


def _non_empty_string_sequence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _valid_validation_commands(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(command, list)
        and bool(command)
        and all(isinstance(token, str) and bool(token.strip()) for token in command)
        for command in value
    )


def _walk(value: Any, path: str = "$.") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}{key}" if path == "$" else f"{path}.{key}"
            yield child_path, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, child
            yield from _walk(child, child_path)


def _code_for_forbidden_label(label: str) -> str:
    return label.replace(" ", "_").replace("/", "_")
