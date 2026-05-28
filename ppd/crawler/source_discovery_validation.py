"""Deterministic validation for PP&D public source discovery records.

The validator is intentionally side-effect free. It does not fetch URLs, consult
robots.txt, or inspect authenticated surfaces. It only classifies discovery
records that were already observed by a public-source parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse


ALLOWED_PUBLIC_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

SUPPORTED_SCHEMES = frozenset({"http", "https"})

PRIVATE_PATH_MARKERS = (
    "/account",
    "/accounts",
    "/admin",
    "/auth",
    "/dashboard",
    "/login",
    "/logout",
    "/myaccount",
    "/my-permits",
    "/mypermits",
    "/oauth",
    "/permitcart",
    "/permits/my",
    "/profile",
    "/register",
    "/saml",
    "/secure",
    "/signin",
    "/sign-in",
    "/user",
)

PRIVATE_QUERY_MARKERS = (
    "access_token=",
    "auth=",
    "code=",
    "id_token=",
    "refresh_token=",
    "session=",
    "ticket=",
    "token=",
)

RAW_BODY_KEYS = frozenset(
    {
        "body",
        "content",
        "html",
        "page_body",
        "raw_body",
        "raw_content",
        "raw_html",
        "raw_text",
        "response_body",
        "text",
    }
)

DOWNLOADED_DOCUMENT_PATH_KEYS = frozenset(
    {
        "downloaded_document_path",
        "downloaded_path",
        "document_path",
        "download_path",
        "file_path",
        "local_document_path",
        "local_file_path",
        "path_on_disk",
    }
)

READY_FOR_CRAWL_STATUSES = frozenset(
    {
        "crawl_candidate",
        "queued_for_crawl",
        "ready",
        "ready-for-crawl",
        "ready_for_crawl",
    }
)

REVIEWED_STATUSES = frozenset(
    {
        "approved_for_preflight",
        "human_reviewed",
        "reviewed",
    }
)

PPD_GUIDANCE_HOST = "www.portland.gov"
PPD_GUIDANCE_PREFIX = "/ppd"
PORTLAND_MAPS_HOST = "www.portlandmaps.com"


@dataclass(frozen=True)
class DiscoveryValidationFinding:
    """A deterministic validation result for one discovered URL."""

    record_id: str
    url: str
    decision: str
    reason_code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "record_id": self.record_id,
            "url": self.url,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "message": self.message,
        }


def validate_discovery_records(
    records: Iterable[Mapping[str, Any]],
) -> list[DiscoveryValidationFinding]:
    """Validate discovery records without network access."""

    findings: list[DiscoveryValidationFinding] = []
    for index, record in enumerate(records):
        findings.append(validate_discovery_record(record, fallback_id=str(index)))
    return findings


def validate_discovery_record(
    record: Mapping[str, Any], fallback_id: str = "0"
) -> DiscoveryValidationFinding:
    record_id = str(record.get("record_id") or record.get("id") or fallback_id)
    url = str(record.get("url") or record.get("canonical_url") or record.get("normalized_url") or "")

    raw_body_path = _find_forbidden_key(record, RAW_BODY_KEYS)
    if raw_body_path:
        return _finding(
            record_id,
            url,
            "raw_body_field",
            f"Discovery packet contains raw body field at {raw_body_path}.",
        )

    downloaded_path = _find_forbidden_key(record, DOWNLOADED_DOCUMENT_PATH_KEYS)
    if downloaded_path:
        return _finding(
            record_id,
            url,
            "downloaded_document_path",
            f"Discovery packet contains downloaded document path at {downloaded_path}.",
        )

    source_url = str(record.get("source_url") or record.get("source_page_url") or "").strip()
    if not source_url:
        return _finding(
            record_id,
            url,
            "missing_source_page_evidence",
            "Discovery packet must preserve source-page evidence.",
        )

    link_text = str(record.get("link_text") or record.get("anchor_text") or record.get("label") or "").strip()
    if not link_text:
        return _finding(
            record_id,
            url,
            "missing_link_text_evidence",
            "Discovery packet must preserve link-text evidence.",
        )

    robots_decision = str(record.get("robots_decision") or record.get("robots_policy_decision") or "").strip()
    if not robots_decision:
        return _finding(
            record_id,
            url,
            "missing_robots_decision",
            "Discovery packet must include a robots decision before crawl handoff.",
        )

    policy_decision = str(record.get("policy_decision") or record.get("allowlist_policy_decision") or "").strip()
    if not policy_decision:
        return _finding(
            record_id,
            url,
            "missing_policy_decision",
            "Discovery packet must include a PP&D policy decision before crawl handoff.",
        )

    status = str(record.get("status") or record.get("crawl_status") or "").strip().lower()
    review_status = str(record.get("review_status") or record.get("human_review_status") or "").strip().lower()
    if status in READY_FOR_CRAWL_STATUSES and review_status not in REVIEWED_STATUSES:
        return _finding(
            record_id,
            url,
            "ready_without_review",
            "Discovery packet cannot be ready for crawl before human review.",
        )

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    if scheme and scheme not in SUPPORTED_SCHEMES:
        return _finding(
            record_id,
            url,
            "unsupported_scheme",
            "Discovery URL uses a scheme outside deterministic public crawl support.",
        )

    if not scheme or not host:
        return _finding(
            record_id,
            url,
            "invalid_url",
            "Discovered URL is not absolute.",
        )

    if host not in ALLOWED_PUBLIC_HOSTS:
        return _finding(
            record_id,
            url,
            "outside_allowlist",
            "Discovery URL host is outside the PP&D public source allowlist.",
        )

    if _looks_private_or_authenticated(path, query):
        return _finding(
            record_id,
            url,
            "private_authenticated",
            "Discovery URL appears to require private, account, or authenticated access.",
        )

    if host == PORTLAND_MAPS_HOST and not _is_public_portland_maps_reference(record):
        return _finding(
            record_id,
            url,
            "portland_maps_not_from_ppd_guidance",
            "Portland Maps URLs are allowed only when linked from public PP&D guidance.",
        )

    return DiscoveryValidationFinding(
        record_id=record_id,
        url=url,
        decision="allow",
        reason_code="allowed_public_source",
        message="Discovery URL is within the deterministic PP&D public source policy.",
    )


def _finding(record_id: str, url: str, reason_code: str, message: str) -> DiscoveryValidationFinding:
    return DiscoveryValidationFinding(
        record_id=record_id,
        url=url,
        decision="skip",
        reason_code=reason_code,
        message=message,
    )


def _looks_private_or_authenticated(path: str, query: str) -> bool:
    if any(marker in path for marker in PRIVATE_PATH_MARKERS):
        return True
    if any(marker in query for marker in PRIVATE_QUERY_MARKERS):
        return True
    return False


def _is_public_portland_maps_reference(record: Mapping[str, Any]) -> bool:
    source_url = str(record.get("source_url") or record.get("source_page_url") or "")
    parsed_source = urlparse(source_url)
    source_host = parsed_source.netloc.lower()
    source_path = parsed_source.path.lower()
    if source_host == PPD_GUIDANCE_HOST and source_path.startswith(PPD_GUIDANCE_PREFIX):
        return True

    relationship = str(record.get("relationship") or record.get("link_role") or "").lower()
    return relationship == "ppd_public_portland_maps_reference"


def _find_forbidden_key(value: Any, forbidden_keys: frozenset[str], path: str = "record") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.replace("-", "_").lower()
            child_path = f"{path}.{key_text}"
            if normalized in forbidden_keys:
                return child_path
            nested = _find_forbidden_key(child, forbidden_keys, child_path)
            if nested:
                return nested
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            nested = _find_forbidden_key(child, forbidden_keys, f"{path}[{index}]")
            if nested:
                return nested
    return None
