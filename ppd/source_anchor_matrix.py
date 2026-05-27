"""Fixture-first validation for PP&D official source anchor coverage.

The matrix is intentionally synthetic metadata. It proves that the original
public source anchors from the PP&D plan have stable identifiers and processing
policy before any crawl, login, download, or authenticated automation occurs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set
from urllib.parse import urlsplit


ORIGINAL_PUBLIC_SOURCE_ANCHORS: Sequence[str] = (
    "https://www.portland.gov/ppd",
    "https://www.portland.gov/ppd/how-use-online-permitting-tools",
    "https://devhub.portlandoregon.gov",
    "https://www.portland.gov/ppd/devhub-faqs",
    "https://www.portland.gov/ppd/devhub-sign-guide",
    "https://www.portland.gov/ppd/get-permit/apply-permits",
    "https://www.portland.gov/ppd/devhub-guide-submit-permit-application",
    "https://www.portland.gov/ppd/get-permit/submit-plans-online",
    "https://www.portland.gov/ppd/brochures-forms-handouts/permits-and-inspections-applications",
    "https://www.portland.gov/ppd/spp-file-naming-standards-preparing-pdfs",
    "https://www.portland.gov/ppd/documents/how-pay-fees/download",
    "https://www.portlandmaps.com",
)

REQUIRED_MATRIX_FIELDS: Sequence[str] = (
    "source_id",
    "canonical_url",
    "source_type",
    "owning_surface",
    "crawl_frequency",
    "processor_policy",
    "freshness_status",
)

ALLOWED_PUBLIC_HOSTS: Set[str] = {
    "www.portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
}

ALLOWED_SOURCE_TYPES: Set[str] = {
    "public_html",
    "public_pdf",
    "public_form",
    "devhub_public",
    "devhub_authenticated",
    "external_reference",
}

FIXTURE_FRESHNESS_STATUSES: Set[str] = {
    "synthetic_unverified",
    "fixture_seed_pending_first_crawl",
}

READY_FRESHNESS_STATUSES: Set[str] = {
    "fresh",
    "current",
    "verified_current",
}

ALLOWED_FRESHNESS_STATUSES: Set[str] = FIXTURE_FRESHNESS_STATUSES | READY_FRESHNESS_STATUSES

PRIVATE_PATH_MARKERS: Sequence[str] = (
    "/login",
    "/log-in",
    "/signin",
    "/sign-in",
    "/register",
    "/account",
    "/accounts",
    "/dashboard",
    "/my-permits",
    "/mypermits",
    "/permitcart",
    "/payment",
    "/checkout",
    "/admin",
)

PRIVATE_QUERY_KEYS: Set[str] = {
    "access_token",
    "auth",
    "code",
    "id_token",
    "password",
    "session",
    "sessionid",
    "ticket",
    "token",
}


class SourceAnchorMatrixError(ValueError):
    """Raised when the fixture-first source anchor matrix is incomplete."""


def load_anchor_matrix(path: Path) -> List[Dict[str, Any]]:
    """Load a committed source anchor coverage fixture."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    anchors = payload.get("anchors")
    if not isinstance(anchors, list):
        raise SourceAnchorMatrixError("source anchor fixture must contain an anchors list")
    return anchors


def validate_anchor_matrix(
    rows: Iterable[Mapping[str, Any]],
    *,
    require_ready_freshness: bool = False,
) -> List[Mapping[str, Any]]:
    """Validate official anchor coverage without performing crawl work."""
    materialized = list(rows)
    if not materialized:
        raise SourceAnchorMatrixError("source anchor matrix is empty")

    source_ids: Set[str] = set()
    canonical_urls: Set[str] = set()

    for index, row in enumerate(materialized):
        missing_fields = [field for field in REQUIRED_MATRIX_FIELDS if not row.get(field)]
        if missing_fields:
            raise SourceAnchorMatrixError(
                "anchor row {0} is missing required fields: {1}".format(
                    index, ", ".join(missing_fields)
                )
            )

        source_id = str(row["source_id"])
        canonical_url = str(row["canonical_url"])
        source_type = str(row["source_type"])
        freshness_status = str(row["freshness_status"])

        if source_id in source_ids:
            raise SourceAnchorMatrixError("duplicate source_id: {0}".format(source_id))
        source_ids.add(source_id)

        if canonical_url in canonical_urls:
            raise SourceAnchorMatrixError(
                "duplicate canonical_url: {0}".format(canonical_url)
            )
        canonical_urls.add(canonical_url)

        _validate_public_anchor_url(source_id, canonical_url)

        if source_type not in ALLOWED_SOURCE_TYPES:
            raise SourceAnchorMatrixError(
                "unsupported source_type for {0}: {1}".format(source_id, source_type)
            )

        if require_ready_freshness and freshness_status not in READY_FRESHNESS_STATUSES:
            raise SourceAnchorMatrixError(
                "stale official source anchor freshness_status for {0}: {1}".format(
                    source_id, freshness_status
                )
            )
        if freshness_status not in ALLOWED_FRESHNESS_STATUSES:
            raise SourceAnchorMatrixError(
                "unsupported freshness_status for {0}: {1}".format(
                    source_id, freshness_status
                )
            )

        if row.get("synthetic_metadata") is not True:
            raise SourceAnchorMatrixError(
                "anchor row {0} must be marked synthetic_metadata=true".format(source_id)
            )

        if row.get("live_crawl_performed") is not False:
            raise SourceAnchorMatrixError(
                "anchor row {0} must be marked live_crawl_performed=false".format(
                    source_id
                )
            )

    missing_urls = sorted(set(ORIGINAL_PUBLIC_SOURCE_ANCHORS) - canonical_urls)
    extra_urls = sorted(canonical_urls - set(ORIGINAL_PUBLIC_SOURCE_ANCHORS))
    if missing_urls or extra_urls:
        details = []
        if missing_urls:
            details.append("missing canonical URLs: {0}".format(", ".join(missing_urls)))
        if extra_urls:
            details.append("unexpected canonical URLs: {0}".format(", ".join(extra_urls)))
        raise SourceAnchorMatrixError("; ".join(details))

    return materialized


def _validate_public_anchor_url(source_id: str, canonical_url: str) -> None:
    parsed = urlsplit(canonical_url)
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    if parsed.scheme != "https" or not host:
        raise SourceAnchorMatrixError(
            "unsupported canonical_url scheme for {0}: {1}".format(source_id, canonical_url)
        )
    if parsed.username or parsed.password:
        raise SourceAnchorMatrixError(
            "private or authenticated canonical_url for {0}: {1}".format(
                source_id, canonical_url
            )
        )
    if host not in ALLOWED_PUBLIC_HOSTS:
        raise SourceAnchorMatrixError(
            "unsupported host for {0}: {1}".format(source_id, host)
        )
    if any(marker in path for marker in PRIVATE_PATH_MARKERS):
        raise SourceAnchorMatrixError(
            "private or authenticated canonical_url for {0}: {1}".format(
                source_id, canonical_url
            )
        )
    if query:
        query_keys = {part.split("=", 1)[0] for part in query.split("&") if part}
        if query_keys & PRIVATE_QUERY_KEYS:
            raise SourceAnchorMatrixError(
                "private or authenticated canonical_url for {0}: {1}".format(
                    source_id, canonical_url
                )
            )
