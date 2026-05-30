"""Validation for inactive release promotion readiness digest v1.

The digest is intentionally commit-safe metadata. It must not include private
browser/session artifacts, live execution claims, legal outcome guarantees, or
flags that imply the validator mutated active release state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ReadinessDigestFinding:
    """A single readiness digest validation failure."""

    code: str
    message: str
    location: str


@dataclass(frozen=True)
class ReadinessDigestValidationResult:
    """Validation result for an inactive readiness digest."""

    ok: bool
    findings: tuple[ReadinessDigestFinding, ...]


_REQUIRED_FIELDS: tuple[tuple[str, str], ...] = (
    ("readiness_summary_rows", "readiness summary rows are required"),
    ("unresolved_hold_carry_forward", "unresolved hold carry-forward fields are required"),
    ("unresolved_blocker_carry_forward", "unresolved blocker carry-forward fields are required"),
    ("rollback_rehearsal_refs", "rollback rehearsal references are required"),
    ("prerequisite_validation_commands", "prerequisite validation command inventory is required"),
    ("reviewer_handoff_placeholders", "reviewer handoff placeholders are required"),
    ("no_go_reasons", "no-go reason fields are required"),
)

_PRIVATE_ARTIFACT_TERMS: tuple[str, ...] = (
    "auth_state",
    "browser_context",
    "cookie",
    "credential",
    "devhub_session",
    "localstorage",
    "mfa",
    "password",
    "private devhub",
    "session storage",
    "session_state",
    "storage_state",
    "token",
)

_FORBIDDEN_FILE_SUFFIXES: tuple[str, ...] = (
    ".auth",
    ".auth.json",
    ".cookies",
    ".har",
    ".png",
    ".screenshot",
    ".session",
    ".trace",
    ".webm",
    ".zip",
)

_FORBIDDEN_PATH_PARTS: tuple[str, ...] = (
    "auth",
    "auth-state",
    "auth_state",
    "browser-artifacts",
    "browser_artifacts",
    "downloads",
    "har",
    "raw",
    "raw-crawl",
    "raw_crawl",
    "screenshots",
    "session",
    "sessions",
    "storage-state",
    "storage_state",
    "traces",
)

_RAW_DATA_TERMS: tuple[str, ...] = (
    "downloaded data",
    "downloaded pdf",
    "raw crawl",
    "raw downloaded",
    "raw html",
    "raw pdf",
    "warc",
)

_LIVE_RELEASE_CLAIMS: tuple[str, ...] = (
    "executed promotion",
    "live crawl completed",
    "live execution",
    "promoted to release",
    "promotion complete",
    "release complete",
    "release-complete",
    "released to production",
)

_OUTCOME_GUARANTEES: tuple[str, ...] = (
    "approval guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legal guarantee",
    "permit will be approved",
    "permitting outcome guaranteed",
    "will pass inspection",
)

_CONSEQUENTIAL_ACTION_TERMS: tuple[str, ...] = (
    "certify acknowledgement",
    "click submit",
    "complete payment",
    "final payment",
    "official upload",
    "pay fees",
    "schedule inspection",
    "submit application",
    "submit permit",
    "upload correction",
)

_MUTATION_FLAGS: tuple[str, ...] = (
    "active_artifact_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_fixture_mutation",
    "active_agent_state_mutation",
    "mutates_active_artifacts",
    "mutates_active_prompts",
    "mutates_active_release_state",
    "mutates_active_fixtures",
    "mutates_active_agent_state",
)


def validate_inactive_readiness_digest_v1(digest: Mapping[str, Any]) -> ReadinessDigestValidationResult:
    """Return validation findings for an inactive readiness digest v1.

    The accepted shape is deliberately simple: a mapping with version/kind/status
    metadata plus non-empty inventory fields. Additional fields are allowed only
    when they remain commit-safe and do not claim live execution or mutation.
    """

    findings: list[ReadinessDigestFinding] = []

    if digest.get("schema_version") != "inactive-release-promotion-readiness-digest-v1":
        findings.append(
            ReadinessDigestFinding(
                "invalid_schema_version",
                "schema_version must be inactive-release-promotion-readiness-digest-v1",
                "schema_version",
            )
        )

    if digest.get("status") != "inactive":
        findings.append(
            ReadinessDigestFinding(
                "invalid_status",
                "inactive release promotion readiness digest v1 must declare status inactive",
                "status",
            )
        )

    for field_name, message in _REQUIRED_FIELDS:
        if _is_missing(digest.get(field_name)):
            findings.append(ReadinessDigestFinding(f"missing_{field_name}", message, field_name))

    for flag_name in _MUTATION_FLAGS:
        if bool(digest.get(flag_name)):
            findings.append(
                ReadinessDigestFinding(
                    "active_mutation_flag",
                    f"{flag_name} must be absent or false in an inactive digest",
                    flag_name,
                )
            )

    for location, value in _walk_values(digest):
        if isinstance(value, str):
            lower_value = value.lower()
            _append_term_findings(findings, lower_value, location, _PRIVATE_ARTIFACT_TERMS, "private_or_session_artifact")
            _append_term_findings(findings, lower_value, location, _RAW_DATA_TERMS, "raw_or_downloaded_data")
            _append_term_findings(findings, lower_value, location, _LIVE_RELEASE_CLAIMS, "live_execution_or_release_claim")
            _append_term_findings(findings, lower_value, location, _OUTCOME_GUARANTEES, "legal_or_permitting_outcome_guarantee")
            _append_term_findings(findings, lower_value, location, _CONSEQUENTIAL_ACTION_TERMS, "consequential_action_language")
            _append_path_finding(findings, value, location)

    return ReadinessDigestValidationResult(ok=not findings, findings=tuple(findings))


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Mapping):
        return not value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return len(value) == 0
    return False


def _walk_values(value: Any, location: str = "$.") -> Iterable[tuple[str, Any]]:
    yield location.rstrip("."), value
    if isinstance(value, Mapping):
        for key, child in value.items():
            safe_key = str(key).replace(".", "_")
            yield from _walk_values(child, f"{location}{safe_key}.")
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            yield from _walk_values(child, f"{location}[{index}].")


def _append_term_findings(
    findings: list[ReadinessDigestFinding],
    lower_value: str,
    location: str,
    terms: Iterable[str],
    code: str,
) -> None:
    for term in terms:
        if term in lower_value:
            findings.append(
                ReadinessDigestFinding(
                    code,
                    f"inactive readiness digest contains prohibited term: {term}",
                    location,
                )
            )


def _append_path_finding(findings: list[ReadinessDigestFinding], value: str, location: str) -> None:
    normalized = value.replace("\\", "/").lower()
    path = PurePosixPath(normalized)
    path_parts = tuple(part for part in path.parts if part not in ("/", ""))

    if any(normalized.endswith(suffix) for suffix in _FORBIDDEN_FILE_SUFFIXES):
        findings.append(
            ReadinessDigestFinding(
                "private_browser_or_capture_file",
                "inactive readiness digest must not reference screenshots, traces, HAR, auth, or session files",
                location,
            )
        )
        return

    if any(part in _FORBIDDEN_PATH_PARTS for part in path_parts):
        findings.append(
            ReadinessDigestFinding(
                "private_browser_or_raw_data_path",
                "inactive readiness digest must not reference private browser artifacts or raw/downloaded data paths",
                location,
            )
        )
