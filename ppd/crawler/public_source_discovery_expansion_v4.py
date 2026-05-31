"""Fixture-first public source discovery expansion packet v4.

This module turns committed synthetic PP&D anchor-page fixtures into canonical
source-discovery rows. It is intentionally offline-only: no network access, no
raw body persistence, no processor handoff, and no mutation of source registries
or crawler state.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urljoin, urlsplit, urlunsplit

ALLOWED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

SUPPORTED_SCHEMES = frozenset({"http", "https"})

SKIP_REASON_CODES = frozenset(
    {
        "outside_allowlist",
        "unsupported_scheme",
        "private_authenticated",
        "disallowed_by_robots_or_policy",
        "raw_download_not_permitted",
        "too_large",
        "unsupported_content_type",
    }
)

PRIVATE_PATH_MARKERS = (
    "/account",
    "/accounts",
    "/admin",
    "/auth",
    "/dashboard",
    "/login",
    "/logout",
    "/my-permits",
    "/oauth",
    "/permitcart",
    "/profile",
    "/register",
    "/saml",
    "/secure",
    "/signin",
    "/sign-in",
    "/user",
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

DISCOVERY_ROW_FIELDS = frozenset(
    {
        "discovery_id",
        "canonical_url",
        "observed_url",
        "source_page_url",
        "source_page_evidence_id",
        "link_text_evidence_id",
        "content_type_hint",
        "allowlist_decision_id",
        "decision",
        "skip_reason_code",
    }
)


@dataclass(frozen=True)
class AnchorObservation:
    """One synthetic anchor observed on an official PP&D source page."""

    source_page_id: str
    source_page_url: str
    href: str
    link_text: str
    content_type_hint: str


def canonicalize_url(url: str, base_url: str | None = None) -> str:
    """Return a deterministic URL form for fixture comparison."""

    joined = urljoin(base_url or "", url.strip())
    parsed = urlsplit(joined)
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if not scheme or not hostname:
        return joined.strip()

    port = parsed.port
    include_port = port is not None and not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    )
    netloc = f"{hostname}:{port}" if include_port else hostname
    path = parsed.path or ""
    if path != "/":
        path = path.rstrip("/")

    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load a committed JSON fixture from disk."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_expansion_packet(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Build the v4 discovery expansion packet from synthetic anchor pages."""

    _reject_raw_body_fields(fixture)
    pages = fixture.get("source_anchor_pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("source_anchor_pages must be a non-empty list")

    source_page_evidence: list[dict[str, Any]] = []
    link_text_evidence: list[dict[str, Any]] = []
    discovered_link_rows: list[dict[str, Any]] = []
    allowlist_decisions: list[dict[str, Any]] = []
    duplicate_normalization_rows: list[dict[str, Any]] = []
    skipped_url_reason_rows: list[dict[str, Any]] = []
    first_seen_by_canonical_url: dict[str, str] = {}

    observation_index = 0
    for page_index, page in enumerate(pages, start=1):
        page_id = _require_string(page, "page_id", f"source_anchor_pages[{page_index - 1}]")
        page_url = canonicalize_url(_require_string(page, "url", page_id))
        title = _require_string(page, "title", page_id)
        source_evidence_id = f"source-page-v4-{page_index:03d}"
        source_page_evidence.append(
            {
                "source_page_evidence_id": source_evidence_id,
                "source_page_id": page_id,
                "canonical_source_page_url": page_url,
                "title": title,
                "fixture_only": True,
                "no_raw_page_body": True,
            }
        )

        anchors = page.get("anchors")
        if not isinstance(anchors, list) or not anchors:
            raise ValueError(f"{page_id}.anchors must be a non-empty list")

        for anchor_index, anchor in enumerate(anchors, start=1):
            observation_index += 1
            observation = AnchorObservation(
                source_page_id=page_id,
                source_page_url=page_url,
                href=_require_string(anchor, "href", f"{page_id}.anchors[{anchor_index - 1}]"),
                link_text=_require_string(anchor, "link_text", f"{page_id}.anchors[{anchor_index - 1}]"),
                content_type_hint=str(anchor.get("content_type_hint") or "unknown"),
            )
            observed_url = urljoin(observation.source_page_url, observation.href.strip())
            canonical_url = canonicalize_url(observation.href, base_url=observation.source_page_url)
            decision, reason = classify_url(canonical_url, observation.content_type_hint)
            discovery_id = f"discovered-v4-{observation_index:03d}"
            link_evidence_id = f"link-text-v4-{observation_index:03d}"
            decision_id = f"allowlist-v4-{observation_index:03d}"

            if canonical_url in first_seen_by_canonical_url:
                duplicate_normalization_rows.append(
                    {
                        "duplicate_id": f"duplicate-v4-{len(duplicate_normalization_rows) + 1:03d}",
                        "canonical_url": canonical_url,
                        "first_discovery_id": first_seen_by_canonical_url[canonical_url],
                        "duplicate_discovery_id": discovery_id,
                        "normalization_basis": "canonical_url",
                    }
                )
            else:
                first_seen_by_canonical_url[canonical_url] = discovery_id

            link_text_evidence.append(
                {
                    "link_text_evidence_id": link_evidence_id,
                    "source_page_evidence_id": source_evidence_id,
                    "link_text": observation.link_text,
                    "observed_href": observation.href,
                    "fixture_only": True,
                }
            )
            allowlist_decisions.append(
                {
                    "allowlist_decision_id": decision_id,
                    "canonical_url": canonical_url,
                    "decision": decision,
                    "skip_reason_code": reason,
                    "allowed_hosts": sorted(ALLOWED_HOSTS),
                    "policy_basis": "fixture_first_public_source_discovery_expansion_v4",
                }
            )

            row = {
                "discovery_id": discovery_id,
                "canonical_url": canonical_url,
                "observed_url": observed_url,
                "source_page_url": observation.source_page_url,
                "source_page_evidence_id": source_evidence_id,
                "link_text_evidence_id": link_evidence_id,
                "content_type_hint": observation.content_type_hint,
                "allowlist_decision_id": decision_id,
                "decision": decision,
                "skip_reason_code": reason,
            }
            discovered_link_rows.append(row)

            if decision == "skip":
                skipped_url_reason_rows.append(
                    {
                        "skip_id": f"skip-v4-{len(skipped_url_reason_rows) + 1:03d}",
                        "discovery_id": discovery_id,
                        "canonical_url": canonical_url,
                        "skip_reason_code": reason,
                        "evidence_ids": [source_evidence_id, link_evidence_id, decision_id],
                    }
                )

    packet = {
        "packet_version": "fixture-first-public-source-discovery-expansion-v4",
        "metadata": {
            "fixture_only": True,
            "no_network_access": True,
            "no_live_crawl": True,
            "no_raw_downloads": True,
            "no_processor_execution": True,
            "no_devhub_access": True,
            "no_registry_mutation": True,
            "allowed_hosts": sorted(ALLOWED_HOSTS),
            "skip_reason_codes": sorted(SKIP_REASON_CODES),
        },
        "source_page_evidence": source_page_evidence,
        "link_text_evidence": link_text_evidence,
        "discovered_link_rows": discovered_link_rows,
        "allowlist_decisions": allowlist_decisions,
        "duplicate_normalization_rows": duplicate_normalization_rows,
        "skipped_url_reason_rows": skipped_url_reason_rows,
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/crawler/public_source_discovery_expansion_v4.py", "ppd/tests/test_public_source_discovery_expansion_v4.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_public_source_discovery_expansion_v4.py"],
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ],
    }
    return packet


def classify_url(canonical_url: str, content_type_hint: str) -> tuple[str, str | None]:
    """Classify a canonical URL using PP&D's narrow fixture policy."""

    parsed = urlsplit(canonical_url)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()

    if scheme not in SUPPORTED_SCHEMES:
        return "skip", "unsupported_scheme"
    if host not in ALLOWED_HOSTS:
        return "skip", "outside_allowlist"
    if any(marker in path for marker in PRIVATE_PATH_MARKERS):
        return "skip", "private_authenticated"
    if content_type_hint == "public_pdf" or path.endswith("/download"):
        return "skip", "raw_download_not_permitted"
    return "allow", None


def validate_expansion_packet(packet: Mapping[str, Any]) -> list[str]:
    """Validate a v4 packet without executing crawlers or reading the network."""

    errors: list[str] = []
    metadata = packet.get("metadata")
    if not isinstance(metadata, Mapping):
        return ["metadata must be an object"]

    for flag in (
        "fixture_only",
        "no_network_access",
        "no_live_crawl",
        "no_raw_downloads",
        "no_processor_execution",
        "no_devhub_access",
        "no_registry_mutation",
    ):
        if metadata.get(flag) is not True:
            errors.append(f"metadata.{flag} must be true")

    if sorted(metadata.get("allowed_hosts") or []) != sorted(ALLOWED_HOSTS):
        errors.append("metadata.allowed_hosts must match PP&D source discovery allowlist")
    if sorted(metadata.get("skip_reason_codes") or []) != sorted(SKIP_REASON_CODES):
        errors.append("metadata.skip_reason_codes must match PP&D skip reason codes")

    source_evidence_ids = _ids(packet.get("source_page_evidence"), "source_page_evidence_id", errors)
    link_evidence_ids = _ids(packet.get("link_text_evidence"), "link_text_evidence_id", errors)
    decision_ids = _ids(packet.get("allowlist_decisions"), "allowlist_decision_id", errors)
    discovery_ids = _ids(packet.get("discovered_link_rows"), "discovery_id", errors)

    skipped_ids = set()
    skipped_rows = packet.get("skipped_url_reason_rows")
    if not isinstance(skipped_rows, list) or not skipped_rows:
        errors.append("skipped_url_reason_rows must be a non-empty list")
    elif isinstance(skipped_rows, list):
        for index, row in enumerate(skipped_rows):
            if not isinstance(row, Mapping):
                errors.append(f"skipped_url_reason_rows[{index}] must be an object")
                continue
            discovery_id = row.get("discovery_id")
            if discovery_id not in discovery_ids:
                errors.append(f"skipped_url_reason_rows[{index}].discovery_id is unknown")
            skipped_ids.add(discovery_id)
            if row.get("skip_reason_code") not in SKIP_REASON_CODES:
                errors.append(f"skipped_url_reason_rows[{index}].skip_reason_code is unsupported")

    rows = packet.get("discovered_link_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("discovered_link_rows must be a non-empty list")
    elif isinstance(rows, list):
        for index, row in enumerate(rows):
            prefix = f"discovered_link_rows[{index}]"
            if not isinstance(row, Mapping):
                errors.append(f"{prefix} must be an object")
                continue
            missing = sorted(DISCOVERY_ROW_FIELDS - set(row))
            if missing:
                errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
                continue
            canonical_url = row.get("canonical_url")
            if not isinstance(canonical_url, str) or canonicalize_url(canonical_url) != canonical_url:
                errors.append(f"{prefix}.canonical_url is not canonicalized")
            if row.get("source_page_evidence_id") not in source_evidence_ids:
                errors.append(f"{prefix}.source_page_evidence_id is unknown")
            if row.get("link_text_evidence_id") not in link_evidence_ids:
                errors.append(f"{prefix}.link_text_evidence_id is unknown")
            if row.get("allowlist_decision_id") not in decision_ids:
                errors.append(f"{prefix}.allowlist_decision_id is unknown")
            expected_decision, expected_reason = classify_url(
                str(row.get("canonical_url")), str(row.get("content_type_hint"))
            )
            if row.get("decision") != expected_decision:
                errors.append(f"{prefix}.decision does not match deterministic policy")
            if row.get("skip_reason_code") != expected_reason:
                errors.append(f"{prefix}.skip_reason_code does not match deterministic policy")
            if row.get("decision") == "skip" and row.get("discovery_id") not in skipped_ids:
                errors.append(f"{prefix} is skipped without a skipped-url reason row")

    duplicates = packet.get("duplicate_normalization_rows")
    if not isinstance(duplicates, list) or not duplicates:
        errors.append("duplicate_normalization_rows must be a non-empty list")
    elif isinstance(duplicates, list):
        for index, row in enumerate(duplicates):
            if not isinstance(row, Mapping):
                errors.append(f"duplicate_normalization_rows[{index}] must be an object")
                continue
            if row.get("first_discovery_id") not in discovery_ids:
                errors.append(f"duplicate_normalization_rows[{index}].first_discovery_id is unknown")
            if row.get("duplicate_discovery_id") not in discovery_ids:
                errors.append(f"duplicate_normalization_rows[{index}].duplicate_discovery_id is unknown")
            if row.get("normalization_basis") != "canonical_url":
                errors.append(f"duplicate_normalization_rows[{index}].normalization_basis must be canonical_url")

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands must be a non-empty list")
    elif any(not isinstance(command, list) or not command for command in commands):
        errors.append("offline_validation_commands entries must be non-empty argv arrays")

    return errors


def _reject_raw_body_fields(value: Any, path: str = "fixture") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) in RAW_BODY_KEYS:
                raise ValueError(f"raw body field is not permitted at {path}.{key}")
            _reject_raw_body_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_raw_body_fields(child, f"{path}[{index}]")


def _require_string(mapping: Mapping[str, Any], key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def _ids(value: Any, key: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list) or not value:
        errors.append(f"{key} rows must be a non-empty list")
        return ids
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            errors.append(f"{key} rows[{index}] must be an object")
            continue
        row_id = row.get(key)
        if not isinstance(row_id, str) or not row_id:
            errors.append(f"{key} rows[{index}].{key} must be a non-empty string")
        elif row_id in ids:
            errors.append(f"{key} duplicates {row_id}")
        else:
            ids.add(row_id)
    return ids
