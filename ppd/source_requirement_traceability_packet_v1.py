"""Fixture-first source-to-requirement traceability packet v1.

The packet builder is intentionally offline-only. It consumes committed PP&D
fixtures and emits cited trace rows that can be reviewed before any live crawl,
download, raw body persistence, or source registry mutation is considered.
"""

from __future__ import annotations

from collections.abc import Mapping
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

TRACEABILITY_PACKET_VERSION = "source_to_requirement_traceability_packet_v1"

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "unittest", "ppd.tests.test_source_requirement_traceability_packet_v1"],
]

SAFETY_ATTESTATIONS: dict[str, bool] = {
    "no_live_crawl": True,
    "no_download": True,
    "no_raw_body": True,
    "no_active_registry_mutation": True,
}

REVIEWER_OWNER_FIELDS: dict[str, str] = {
    "reviewer_owner_role": "PP&D fixture traceability reviewer",
    "implementation_owner_role": "PP&D guardrail compiler maintainer",
    "freshness_owner_role": "PP&D public source registry maintainer",
}

PROHIBITED_REFERENCE_KEYS = {
    "body",
    "download",
    "download_path",
    "download_url",
    "downloaded_document",
    "downloaded_document_path",
    "html_body",
    "local_download_path",
    "raw_body",
    "raw_document",
    "raw_html",
    "response_body",
}

ACTIVE_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_process_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "agent_state_mutation",
    "guardrail_mutation",
    "monitoring_mutation",
    "process_mutation",
    "release_state_mutation",
    "requirement_mutation",
    "source_mutation",
}

PRIVATE_OR_AUTH_URL_RE = re.compile(
    r"(?:^|[/.?&#_-])(?:auth|authenticated|login|session|account|private|case|token|credential)(?:$|[/.?&#_-])",
    re.IGNORECASE,
)
DOWNLOAD_REFERENCE_RE = re.compile(r"(?:^|/)(?:download|downloads)(?:$|[/?#])|\.(?:pdf|docx?|xlsx?)(?:$|[?#])", re.IGNORECASE)
GUARANTEE_RE = re.compile(
    r"\b(?:guarantee[sd]?|approval is certain|will be approved|permit will issue|permit guaranteed|legal advice|legally sufficient|compliance is guaranteed|no risk of denial)\b",
    re.IGNORECASE,
)
ACTIVE_MUTATION_TEXT_RE = re.compile(
    r"\b(?:source|requirement|process|guardrail|monitoring|release[-_ ]state|agent[-_ ]state)\b"
    r".{0,48}\b(?:mutation|mutate|write|apply|enable|activate|update)\b|"
    r"\b(?:mutation|mutate|write|apply|enable|activate|update)\b"
    r".{0,48}\b(?:source|requirement|process|guardrail|monitoring|release[-_ ]state|agent[-_ ]state)\b",
    re.IGNORECASE,
)


class SourceRequirementTraceabilityPacketV1Error(ValueError):
    """Raised when a traceability packet is unsafe or incomplete."""


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _public_canonical_url(value: Any) -> str | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    parts = urlsplit(raw)
    path = parts.path
    if path.endswith("/download"):
        path = path[: -len("/download")]
    elif path == "/download":
        path = "/"
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def _source_records(source_registry: Any, process_packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    if isinstance(source_registry, dict):
        source_items = _as_list(source_registry.get("sources"))
    else:
        source_items = _as_list(source_registry)

    for source in source_items:
        if not isinstance(source, dict):
            continue
        source_id = str(source.get("source_id", ""))
        if not source_id:
            continue
        if source.get("privacy_classification", "public") == "private_authenticated":
            continue
        if source.get("source_type", "public_html") == "devhub_authenticated":
            continue
        records[source_id] = dict(source)

    for evidence in _as_list(process_packet.get("source_evidence")):
        if not isinstance(evidence, dict):
            continue
        source_id = str(evidence.get("source_id", ""))
        if not source_id:
            continue
        existing = records.setdefault(source_id, {})
        existing.setdefault("source_id", source_id)
        existing.setdefault("canonical_url", _public_canonical_url(evidence.get("canonical_url")))
        existing.setdefault("source_type", "public_html")
        existing.setdefault("privacy_classification", "public")
        existing.setdefault("freshness_status", "fixture_current")
        existing.setdefault("source_evidence_ids", [])
        if evidence.get("evidence_id") not in existing["source_evidence_ids"]:
            existing["source_evidence_ids"].append(evidence.get("evidence_id"))

    for source in records.values():
        source["canonical_url"] = _public_canonical_url(source.get("canonical_url"))
        source.setdefault("freshness_status", "fixture_current")
    return records


def _document_records(document_registry: dict[str, Any], normalized_document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for document in _as_list(document_registry.get("documents")):
        if not isinstance(document, dict):
            continue
        if document.get("document_type") == "devhub_authenticated":
            continue
        source_id = str(document.get("source_id", ""))
        if source_id:
            records[source_id] = dict(document)

    normalized_source_id = str(
        normalized_document.get("source_id")
        or normalized_document.get("fixture_id")
        or normalized_document.get("document_id", "")
    )
    if normalized_source_id:
        records.setdefault(
            normalized_source_id,
            {
                "document_id": normalized_document.get("document_id"),
                "source_id": normalized_source_id,
                "title": normalized_document.get("title"),
                "document_type": normalized_document.get("source_type", "public_html"),
                "sections": normalized_document.get("source_order", []),
            },
        )
    return records


def _evidence_lookup(process_packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(evidence.get("evidence_id")): evidence
        for evidence in _as_list(process_packet.get("source_evidence"))
        if isinstance(evidence, dict) and evidence.get("evidence_id")
    }


def _section_id(requirement: dict[str, Any]) -> str:
    stage = str(requirement.get("process_stage", "unspecified-stage"))
    return stage.replace(" ", "-").replace("/", "-")


def _affected_guardrails(source: dict[str, Any], process_packet: dict[str, Any]) -> list[str]:
    guardrail_ids = source.get("guardrail_bundle_ids")
    if isinstance(guardrail_ids, list) and guardrail_ids:
        return [str(item) for item in guardrail_ids]
    bundle_id = process_packet.get("guardrail_bundle_id")
    return [str(bundle_id)] if bundle_id else []


def build_traceability_packet(
    *,
    source_registry: Any,
    document_registry: dict[str, Any],
    normalized_document: dict[str, Any],
    process_packet: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic cited source-to-requirement traceability packet."""

    sources = _source_records(source_registry, process_packet)
    documents = _document_records(document_registry, normalized_document)
    evidence_by_id = _evidence_lookup(process_packet)
    requirement_stage_links: dict[str, str] = {}
    rows: list[dict[str, Any]] = []

    for requirement in _as_list(process_packet.get("requirement_node_candidates")):
        if not isinstance(requirement, dict):
            continue
        if requirement.get("human_review_status") != "reviewed":
            continue
        if requirement.get("formalization_status") not in {"assembly_candidate", "formalized"}:
            continue

        requirement_id = str(requirement.get("requirement_id", ""))
        if not requirement_id:
            continue
        requirement_stage_links[requirement_id] = str(requirement.get("process_stage", ""))

        for evidence_id in _as_list(requirement.get("source_evidence_ids")):
            evidence = evidence_by_id.get(str(evidence_id), {})
            source_id = str(evidence.get("source_id", evidence_id))
            source = sources.get(source_id, {})
            document = documents.get(source_id, {})
            canonical_url = _public_canonical_url(source.get("canonical_url") or evidence.get("canonical_url"))
            rows.append(
                {
                    "trace_row_id": f"trace-{requirement_id}-{evidence_id}",
                    "source_id": source_id,
                    "source_evidence_id": str(evidence_id),
                    "citations": [
                        {
                            "source_evidence_id": str(evidence_id),
                            "source_id": source_id,
                            "canonical_url": canonical_url,
                        }
                    ],
                    "canonical_url": canonical_url,
                    "document_id": document.get("document_id")
                    or source.get("normalized_document_id")
                    or f"fixture-doc-{source_id}",
                    "document_section_id": _section_id(requirement),
                    "document_section_label": requirement.get("object"),
                    "requirement_id": requirement_id,
                    "requirement_type": requirement.get("requirement_type"),
                    "process_id": process_packet.get("process_id"),
                    "process_stage": requirement.get("process_stage"),
                    "affected_guardrail_bundle_ids": _affected_guardrails(source, process_packet),
                    "freshness_status": source.get("freshness_status", "fixture_current"),
                    "reviewer_owner_fields": {
                        **REVIEWER_OWNER_FIELDS,
                        "human_review_status": requirement.get("human_review_status"),
                    },
                    "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
                    "attestations": dict(SAFETY_ATTESTATIONS),
                }
            )

    rows.sort(key=lambda row: (str(row["requirement_id"]), str(row["source_evidence_id"])))
    packet = {
        "packet_version": TRACEABILITY_PACKET_VERSION,
        "packet_id": "fixture-first-source-to-requirement-traceability-v1",
        "input_fixture_paths": [
            "ppd/tests/fixtures/change_impact/current_sources.json",
            "ppd/tests/fixtures/citation_integrity/document_records.json",
            "ppd/tests/fixtures/html_extraction/synthetic_ppd_guidance_normalized.json",
            "ppd/tests/fixtures/process_model/fixture_first_assembly_packet.json",
        ],
        "process_id": process_packet.get("process_id"),
        "guardrail_bundle_id": process_packet.get("guardrail_bundle_id"),
        "known_source_ids": sorted(sources),
        "known_requirement_ids": sorted(requirement_stage_links),
        "requirement_process_stage_links": requirement_stage_links,
        "row_count": len(rows),
        "rows": rows,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "attestations": dict(SAFETY_ATTESTATIONS),
    }
    assert_valid_traceability_packet(packet)
    return packet


def validate_traceability_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return fail-closed validation errors for a traceability packet v1."""

    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be a mapping"]
    if packet.get("packet_version") != TRACEABILITY_PACKET_VERSION:
        errors.append("packet_version must be source_to_requirement_traceability_packet_v1")
    if packet.get("attestations") != SAFETY_ATTESTATIONS:
        errors.append("packet attestations must keep crawl, download, raw body, and registry mutation disabled")

    known_sources = {str(item) for item in _as_list(packet.get("known_source_ids")) if str(item).strip()}
    known_requirements = {str(item) for item in _as_list(packet.get("known_requirement_ids")) if str(item).strip()}
    stage_links = packet.get("requirement_process_stage_links")
    if not isinstance(stage_links, Mapping):
        stage_links = {}
        errors.append("requirement_process_stage_links must be present")

    rows = _as_list(packet.get("rows"))
    if packet.get("row_count") != len(rows):
        errors.append("row_count must equal rows length")
    if not rows:
        errors.append("rows must not be empty")

    for index, row in enumerate(rows):
        path = f"rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be a mapping")
            continue
        source_id = str(row.get("source_id", "")).strip()
        requirement_id = str(row.get("requirement_id", "")).strip()
        stage = str(row.get("process_stage", "")).strip()
        citations = _as_list(row.get("citations"))

        if not source_id:
            errors.append(f"{path}.source_id is required")
        elif known_sources and source_id not in known_sources:
            errors.append(f"{path}.source_id references unknown source id")
        if not requirement_id:
            errors.append(f"{path}.requirement_id is required")
        elif known_requirements and requirement_id not in known_requirements:
            errors.append(f"{path}.requirement_id references unknown requirement id")
        if not row.get("source_evidence_id") or not citations:
            errors.append(f"{path} is missing source citations")
        if not row.get("document_id") or not row.get("document_section_id"):
            errors.append(f"{path} is missing document citation links")
        if not stage:
            errors.append(f"{path}.process_stage is required")
        elif stage_links.get(requirement_id) != stage:
            errors.append(f"{path}.process_stage does not match requirement_process_stage_links")
        if not row.get("freshness_status"):
            errors.append(f"{path}.freshness_status is required")
        if not _as_list(row.get("affected_guardrail_bundle_ids")):
            errors.append(f"{path}.affected_guardrail_bundle_ids is required")
        if row.get("attestations") != SAFETY_ATTESTATIONS:
            errors.append(f"{path}.attestations must keep crawl, download, raw body, and registry mutation disabled")

    _scan_for_prohibited_content(packet, "packet", errors)
    return _dedupe(errors)


def assert_valid_traceability_packet(packet: Mapping[str, Any]) -> None:
    errors = validate_traceability_packet(packet)
    if errors:
        raise SourceRequirementTraceabilityPacketV1Error("; ".join(errors))


def validate_source_requirement_traceability_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    return validate_traceability_packet(packet)


def assert_valid_source_requirement_traceability_packet_v1(packet: Mapping[str, Any]) -> None:
    assert_valid_traceability_packet(packet)


def _scan_for_prohibited_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = _normalize_key(raw_key)
            child_path = f"{path}.{raw_key}"
            if key in PROHIBITED_REFERENCE_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} references raw body or downloaded document content")
            if key in ACTIVE_MUTATION_KEYS and _is_truthy(child):
                errors.append(f"{child_path} declares an active source, requirement, process, guardrail, monitoring, release-state, or agent-state mutation flag")
            _scan_for_prohibited_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_prohibited_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        _scan_text(value, path, errors)


def _scan_text(text: str, path: str, errors: list[str]) -> None:
    if text.startswith(("http://", "https://")):
        if PRIVATE_OR_AUTH_URL_RE.search(text):
            errors.append(f"{path} references a private or authenticated URL")
        if DOWNLOAD_REFERENCE_RE.search(text):
            errors.append(f"{path} references a raw body or downloaded document")
    if GUARANTEE_RE.search(text):
        errors.append(f"{path} makes a legal or permitting outcome guarantee")
    if ACTIVE_MUTATION_TEXT_RE.search(text) and not _mentions_disabled_mutation_attestation(text):
        errors.append(f"{path} references active source, requirement, process, guardrail, monitoring, release-state, or agent-state mutation")


def _mentions_disabled_mutation_attestation(text: str) -> bool:
    normalized = text.lower().replace("-", "_").replace(" ", "_")
    return normalized.startswith("no_active_") or "no_active_" in normalized or "mutation_disabled" in normalized


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "active", "enabled", "enable", "apply", "write"}
    return bool(value)


def _dedupe(errors: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for error in errors:
        if error not in seen:
            seen.add(error)
            result.append(error)
    return result
