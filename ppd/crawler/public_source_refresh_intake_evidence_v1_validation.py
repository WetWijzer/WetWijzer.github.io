"""Safety validation for public source refresh evidence intake packets v1.

The validator is intentionally fixture-first and side-effect free. It validates
reviewer intake evidence metadata only; it does not crawl, download, archive, or
mutate source, requirement, process, guardrail, monitoring, release, or agent
state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


ALLOWED_PUBLIC_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

_AUTHENTICATED_URL_MARKERS = (
    "/login",
    "/sign-in",
    "/signin",
    "/register",
    "/account",
    "/accounts",
    "/dashboard",
    "/my-permits",
    "/myrequests",
    "/oauth",
    "/saml",
    "/callback",
    "access_token=",
    "auth=",
    "code=",
    "session=",
    "state=",
)

_FORBIDDEN_KEY_TOKENS = frozenset(
    {
        "rawpagebody",
        "rawbody",
        "rawhtml",
        "pagebody",
        "responsebody",
        "bodyhtml",
        "documentbytes",
        "pdfbytes",
        "downloadeddocument",
        "downloadeddocuments",
        "downloadedpdf",
        "downloadedfile",
        "processorcompleted",
        "processorcomplete",
        "processorfinished",
        "processordone",
        "processorexecuted",
        "processorinvoked",
        "archivecompleted",
        "archivecomplete",
        "archivefinished",
        "archivedone",
        "archiveartifactwritten",
        "archivemanifestupdated",
        "activesourcemutation",
        "sourcemutationactive",
        "sourceregistrymutation",
        "sourceupdated",
        "sourcemutated",
        "activerequirementmutation",
        "requirementmutationactive",
        "requirementupdated",
        "requirementmutated",
        "activeprocessmutation",
        "processmutationactive",
        "processupdated",
        "processmutated",
        "activeguardrailmutation",
        "guardrailmutationactive",
        "guardrailupdated",
        "guardrailmutated",
        "activemonitoringmutation",
        "monitoringmutationactive",
        "monitoringupdated",
        "monitoringmutated",
        "activereleasestatemutation",
        "releasestatemutationactive",
        "releasestateupdated",
        "releasestatemutated",
        "activeagentstatemutation",
        "agentstatemutationactive",
        "agentstateupdated",
        "agentstatemutated",
    }
)

_FORBIDDEN_VALUE_MARKERS = (
    "auth_state",
    "cookies.json",
    "credential",
    "localstorage.json",
    "password",
    "session_cookie",
    "storage_state",
    "trace.zip",
    "warc://",
    ".warc",
    "/raw/",
    "raw_crawl",
    "raw-crawl",
    "rawcrawl",
    "crawl_output",
    "crawl-output",
    "downloaded_documents",
    "downloaded-documents",
    "/downloads/",
    "archive_artifacts",
    "archive-artifacts",
    "processor_output",
    "processor-output",
    "processor_outputs",
    "processor-outputs",
)

_OUTCOME_GUARANTEE_MARKERS = (
    "guaranteed approval",
    "guarantees approval",
    "permit will be approved",
    "permit approval is guaranteed",
    "application will be approved",
    "approval is guaranteed",
    "ensures issuance",
    "will issue the permit",
    "will pass inspection",
    "legal advice",
    "legal conclusion",
)


@dataclass(frozen=True)
class PublicSourceRefreshEvidenceIntakeV1ValidationResult:
    """Validation result for public source refresh evidence intake packet v1."""

    valid: bool
    errors: tuple[str, ...]


class PublicSourceRefreshEvidenceIntakeV1ValidationError(ValueError):
    """Raised when an intake packet v1 is unsafe or incomplete."""


def validate_public_source_refresh_evidence_intake_packet_v1(
    packet: Mapping[str, Any],
) -> PublicSourceRefreshEvidenceIntakeV1ValidationResult:
    """Validate public source refresh evidence intake packet v1 safety rules."""

    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return PublicSourceRefreshEvidenceIntakeV1ValidationResult(False, ("packet must be an object",))

    _collect_forbidden_content(packet, "$", errors)

    rows = packet.get("synthetic_reviewer_evidence", packet.get("intake_rows"))
    if not isinstance(rows, list) or not rows:
        errors.append("synthetic_reviewer_evidence or intake_rows must include at least one intake row")
        rows = []

    for index, row in enumerate(rows):
        prefix = "intake_rows[" + str(index) + "]"
        if not isinstance(row, Mapping):
            errors.append(prefix + " must be an object")
            continue

        fields = row.get("synthetic_reviewer_evidence_fields")
        if not isinstance(fields, Mapping):
            fields = {}

        source_id = _first_text(row.get("source_id"), fields.get("source_id"))
        canonical_url = _first_text(row.get("canonical_url"), fields.get("canonical_url"))
        affected_source_ids = _text_list(row.get("affected_source_ids")) or _text_list(fields.get("affected_source_ids"))
        affected_requirement_ids = _text_list(row.get("affected_requirement_ids")) or _text_list(fields.get("affected_requirement_ids"))
        citation_refs = row.get("citation_refs", fields.get("citation_refs"))
        rationale = _first_text(
            row.get("defer_or_rollback_rationale"),
            fields.get("defer_or_rollback_rationale"),
            row.get("rollback_rationale"),
            fields.get("rollback_rationale"),
        )

        if not _first_text(row.get("evidence_id"), fields.get("evidence_id")):
            errors.append(prefix + ".evidence_id is required")
        if not source_id:
            errors.append(prefix + ".source_id is required")
        if not canonical_url:
            errors.append(prefix + ".canonical_url is required")
        else:
            _validate_public_url(canonical_url, prefix + ".canonical_url", errors)
        if not affected_source_ids:
            errors.append(prefix + ".affected_source_ids must include at least one source id")
        if not affected_requirement_ids:
            errors.append(prefix + ".affected_requirement_ids must include at least one requirement id")
        if not rationale:
            errors.append(prefix + ".defer_or_rollback_rationale is required")
        if not isinstance(citation_refs, list) or not citation_refs:
            errors.append(prefix + ".citation_refs must include at least one citation")
        else:
            for citation_index, citation in enumerate(citation_refs):
                citation_prefix = prefix + ".citation_refs[" + str(citation_index) + "]"
                if not isinstance(citation, Mapping):
                    errors.append(citation_prefix + " must be an object")
                    continue
                if not _text(citation.get("citation_id")):
                    errors.append(citation_prefix + ".citation_id is required")
                if not _text(citation.get("affected_source_id")):
                    errors.append(citation_prefix + ".affected_source_id is required")
                if not _text(citation.get("affected_requirement_id")):
                    errors.append(citation_prefix + ".affected_requirement_id is required")

    return PublicSourceRefreshEvidenceIntakeV1ValidationResult(False if errors else True, tuple(dict.fromkeys(errors)))


def require_valid_public_source_refresh_evidence_intake_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise when public source refresh evidence intake packet v1 is invalid."""

    result = validate_public_source_refresh_evidence_intake_packet_v1(packet)
    if not result.valid:
        raise PublicSourceRefreshEvidenceIntakeV1ValidationError("; ".join(result.errors))


def _validate_public_url(url: str, path: str, errors: list[str]) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        errors.append(path + " must use https")
    if host not in ALLOWED_PUBLIC_HOSTS:
        errors.append(path + " host must be on the PP&D public source allowlist")
    if parsed.username or parsed.password:
        errors.append(path + " must not include authenticated URL userinfo")
    searchable = (parsed.path + "?" + parsed.query).lower()
    if any(marker in searchable for marker in _AUTHENTICATED_URL_MARKERS):
        errors.append(path + " must not target authenticated account, login, OAuth, or session URLs")


def _collect_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = _normalized_key(key_text)
            if normalized_key in _FORBIDDEN_KEY_TOKENS and child not in (None, "", [], {}, False):
                errors.append(path + "." + key_text + " must be false or empty in intake packet v1")
            _collect_forbidden_content(child, path + "." + key_text, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_forbidden_content(child, path + "[" + str(index) + "]", errors)
    elif isinstance(value, str):
        lower_value = value.lower()
        for marker in _FORBIDDEN_VALUE_MARKERS:
            if marker in lower_value:
                errors.append(path + " contains forbidden private, raw, download, processor, or archive artifact marker " + marker)
        for marker in _OUTCOME_GUARANTEE_MARKERS:
            if marker in lower_value:
                errors.append(path + " contains forbidden legal or permitting outcome guarantee marker " + marker)


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [_text(item) for item in value if _text(item)]


def _first_text(*values: Any) -> str:
    for value in values:
        text = _text(value)
        if text:
            return text
    return ""


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _normalized_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


__all__ = [
    "ALLOWED_PUBLIC_HOSTS",
    "PublicSourceRefreshEvidenceIntakeV1ValidationError",
    "PublicSourceRefreshEvidenceIntakeV1ValidationResult",
    "require_valid_public_source_refresh_evidence_intake_packet_v1",
    "validate_public_source_refresh_evidence_intake_packet_v1",
]
