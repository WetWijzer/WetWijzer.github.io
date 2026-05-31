"""Validation for PP&D archive manifest import candidate packet v1.

The validator is intentionally side-effect free. It checks a proposed import packet
before any archive manifest rows are accepted into PP&D-controlled state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


PACKET_VERSION = "archive-manifest-import-candidate-packet-v1"


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic validation failure for a candidate packet."""

    code: str
    path: str
    message: str


def validate_candidate_packet_v1(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for an archive manifest import candidate packet.

    An empty issue list means the packet is structurally acceptable for the next
    import stage. This function does not perform network access, crawl live
    systems, read local artifacts, or mutate repository state.
    """

    issues: list[ValidationIssue] = []

    if not isinstance(packet, Mapping):
        return [
            ValidationIssue(
                "packet_not_object",
                "$",
                "candidate packet must be a JSON object",
            )
        ]

    if packet.get("packet_version") != PACKET_VERSION:
        issues.append(
            ValidationIssue(
                "invalid_packet_version",
                "$.packet_version",
                f"packet_version must be {PACKET_VERSION!r}",
            )
        )

    candidates = packet.get("manifest_candidates")
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)) or not candidates:
        issues.append(
            ValidationIssue(
                "missing_manifest_candidates",
                "$.manifest_candidates",
                "manifest_candidates must be a non-empty array",
            )
        )
        candidates = []

    _validate_processor_identity_rows(packet, issues)
    _validate_reviewer_holds(packet, issues)
    _validate_validation_commands(packet, issues)

    for index, candidate in enumerate(candidates):
        path = f"$.manifest_candidates[{index}]"
        if not isinstance(candidate, Mapping):
            issues.append(
                ValidationIssue(
                    "candidate_not_object",
                    path,
                    "manifest candidate must be an object",
                )
            )
            continue
        _validate_manifest_candidate(candidate, path, issues)

    _reject_disallowed_artifact_claims(packet, issues)
    _reject_live_or_authenticated_claims(packet, issues)
    _reject_guarantees(packet, issues)
    _reject_active_mutation_flags(packet, issues)

    return issues


def assert_candidate_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError if a candidate packet is not acceptable."""

    issues = validate_candidate_packet_v1(packet)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        raise ValueError(formatted)


def _validate_manifest_candidate(
    candidate: Mapping[str, Any],
    path: str,
    issues: list[ValidationIssue],
) -> None:
    redirect_chain = candidate.get("redirect_chain")
    if not isinstance(redirect_chain, Sequence) or isinstance(redirect_chain, (str, bytes)) or not redirect_chain:
        issues.append(
            ValidationIssue(
                "missing_redirect_chain",
                f"{path}.redirect_chain",
                "redirect_chain must be a non-empty array",
            )
        )

    http_status = candidate.get("http_status")
    if not isinstance(http_status, int) or isinstance(http_status, bool):
        issues.append(
            ValidationIssue(
                "missing_http_status",
                f"{path}.http_status",
                "http_status must be an integer response status",
            )
        )

    content_type = candidate.get("content_type")
    if not isinstance(content_type, str) or not content_type.strip():
        issues.append(
            ValidationIssue(
                "missing_content_type",
                f"{path}.content_type",
                "content_type must be a non-empty string",
            )
        )

    content_hash = candidate.get("content_hash")
    if not _has_content_hash(content_hash):
        issues.append(
            ValidationIssue(
                "missing_content_hash",
                f"{path}.content_hash",
                "content_hash must include a digest value and algorithm",
            )
        )

    no_raw_body_persisted = candidate.get("no_raw_body_persisted")
    if no_raw_body_persisted is not True:
        issues.append(
            ValidationIssue(
                "missing_no_raw_body_flag",
                f"{path}.no_raw_body_persisted",
                "no_raw_body_persisted must be explicitly true",
            )
        )

    skipped = bool(candidate.get("skipped")) or candidate.get("import_decision") == "skipped"
    if skipped:
        skipped_reason = candidate.get("skipped_reason")
        if not isinstance(skipped_reason, str) or not skipped_reason.strip():
            issues.append(
                ValidationIssue(
                    "missing_skipped_reason",
                    f"{path}.skipped_reason",
                    "skipped candidates must include a skipped_reason",
                )
            )

    archive_artifact_ref = candidate.get("archive_artifact_ref")
    if archive_artifact_ref not in (None, "metadata-only"):
        issues.append(
            ValidationIssue(
                "raw_or_downloaded_artifact_ref",
                f"{path}.archive_artifact_ref",
                "archive_artifact_ref must be omitted or metadata-only for import candidates",
            )
        )


def _validate_processor_identity_rows(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    rows = packet.get("processor_identity_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        issues.append(
            ValidationIssue(
                "missing_processor_identity_rows",
                "$.processor_identity_rows",
                "processor_identity_rows must be a non-empty array",
            )
        )
        return

    for index, row in enumerate(rows):
        path = f"$.processor_identity_rows[{index}]"
        if not isinstance(row, Mapping):
            issues.append(ValidationIssue("processor_identity_row_not_object", path, "processor identity row must be an object"))
            continue
        for field in ("processor_name", "processor_version", "policy_adapter"):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(
                    ValidationIssue(
                        "incomplete_processor_identity_row",
                        f"{path}.{field}",
                        f"processor identity row must include {field}",
                    )
                )


def _validate_reviewer_holds(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    holds = packet.get("reviewer_holds")
    if not isinstance(holds, Sequence) or isinstance(holds, (str, bytes)):
        issues.append(
            ValidationIssue(
                "missing_reviewer_holds",
                "$.reviewer_holds",
                "reviewer_holds must be present as an explicit array, even when empty",
            )
        )


def _validate_validation_commands(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    commands = packet.get("validation_commands")
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)) or not commands:
        issues.append(
            ValidationIssue(
                "missing_validation_commands",
                "$.validation_commands",
                "validation_commands must be a non-empty array of argv arrays",
            )
        )
        return

    for command_index, command in enumerate(commands):
        command_path = f"$.validation_commands[{command_index}]"
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes)) or not command:
            issues.append(
                ValidationIssue(
                    "invalid_validation_command",
                    command_path,
                    "each validation command must be a non-empty argv array",
                )
            )
            continue
        for arg_index, arg in enumerate(command):
            if not isinstance(arg, str) or not arg:
                issues.append(
                    ValidationIssue(
                        "invalid_validation_command_argument",
                        f"{command_path}[{arg_index}]",
                        "validation command arguments must be non-empty strings",
                    )
                )


def _has_content_hash(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if not isinstance(value, Mapping):
        return False
    algorithm = value.get("algorithm")
    digest = value.get("value") or value.get("digest") or value.get("hex")
    return isinstance(algorithm, str) and bool(algorithm.strip()) and isinstance(digest, str) and bool(digest.strip())


def _reject_disallowed_artifact_claims(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    disallowed_terms = (
        "raw_body",
        "raw body",
        "downloaded_artifact",
        "downloaded artifact",
        "download_path",
        "download path",
        "local_path",
        "local path",
        "warc_path",
        "html_body",
        "response_body",
        "document_bytes",
    )
    _scan_terms(packet, disallowed_terms, "raw_or_downloaded_artifact", issues)

    private_terms = (
        "cookie",
        "credential",
        "password",
        "session",
        "auth_state",
        "storage_state",
        "storagestate",
        "browser_context",
        "playwright_trace",
        "trace.zip",
        "har",
        "screenshot",
        "video",
        "private_upload",
        "payment_detail",
    )
    _scan_terms(packet, private_terms, "private_session_or_browser_artifact", issues)


def _reject_live_or_authenticated_claims(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    terms = (
        "live crawl",
        "live_crawl",
        "recrawled live",
        "devhub authenticated",
        "authenticated devhub",
        "account-scoped devhub",
        "user session",
        "manual login completed",
    )
    _scan_terms(packet, terms, "live_crawl_or_devhub_claim", issues)


def _reject_guarantees(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    terms = (
        "legal advice",
        "legally sufficient",
        "guarantee approval",
        "guaranteed approval",
        "permit will be issued",
        "permit guaranteed",
        "will pass inspection",
        "no further review required",
    )
    _scan_terms(packet, terms, "legal_or_permitting_guarantee", issues)


def _reject_active_mutation_flags(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    mutation_keys = (
        "active_mutation",
        "mutation_enabled",
        "mutations_enabled",
        "can_submit",
        "can_upload",
        "can_certify",
        "can_pay",
        "can_schedule",
        "can_cancel",
        "can_withdraw",
        "write_enabled",
        "side_effects_enabled",
    )
    for path, key, value in _walk_key_values(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in mutation_keys and value is True:
            issues.append(
                ValidationIssue(
                    "active_mutation_flag",
                    path,
                    f"active mutation flag {key!r} must not be true in an import candidate packet",
                )
            )


def _scan_terms(
    value: Any,
    terms: Iterable[str],
    code: str,
    issues: list[ValidationIssue],
) -> None:
    normalized_terms = tuple(term.lower() for term in terms)
    for path, text in _walk_text(value):
        lowered = text.lower()
        for term in normalized_terms:
            if term in lowered:
                issues.append(
                    ValidationIssue(
                        code,
                        path,
                        f"disallowed import candidate claim contains {term!r}",
                    )
                )
                break


def _walk_text(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            yield child_path, key_text
            yield from _walk_text(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk_text(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def _walk_key_values(value: Any, path: str = "$") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            yield child_path, key_text, child
            yield from _walk_key_values(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk_key_values(child, f"{path}[{index}]")


__all__ = [
    "PACKET_VERSION",
    "ValidationIssue",
    "assert_candidate_packet_v1",
    "validate_candidate_packet_v1",
]
