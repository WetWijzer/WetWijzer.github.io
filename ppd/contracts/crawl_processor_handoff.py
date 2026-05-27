"""Crawl-to-processor handoff manifest contracts for PP&D.

These manifests describe the point where PP&D public source discovery hands
allowlisted seed URLs to the read-only ipfs_datasets_py archival processor
suite. They are deterministic planning fixtures only: no raw responses,
downloaded documents, private DevHub state, browser traces, screenshots, or
credentials belong here.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import Any, Mapping, Optional
from urllib.parse import unquote, urlparse

from .archive_adapter import IPFS_DATASETS_PROCESSOR_BACKEND
from .crawl_manifest_privacy import validate_crawl_manifest_privacy


ALLOWED_PUBLIC_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

ALLOWED_PROCESSOR_MODULE_PREFIXES = (
    "ipfs_datasets_py.processors.web_archiving",
    "ipfs_datasets_py.processors.legal_scrapers",
)

RAW_BODY_ARGUMENT_KEYS = frozenset({"body", "raw_body", "rawbody", "response_body", "responsebody", "html", "text", "content", "bytes"})
RAW_ARCHIVE_PATH_ARGUMENT_KEYS = frozenset({"archive_path", "archivepath", "raw_archive_path", "rawarchivepath", "warc_path", "warcpath", "raw_warc_path", "rawwarcpath"})
DOWNLOADED_DOCUMENT_PATH_ARGUMENT_KEYS = frozenset({"downloaded_document_path", "downloadeddocumentpath", "downloaded_pdf_path", "downloadedpdfpath", "document_path", "documentpath", "pdf_path", "pdfpath", "download_path", "downloadpath"})
HASH_ARGUMENT_KEYS = frozenset({"hash", "digest", "sha256", "sha256_hex", "sha256hex", "content_hash", "contenthash", "content_sha256", "contentsha256"})
SIDE_EFFECTFUL_NETWORK_ARGUMENT_KEYS = frozenset({"allow_live_network", "allowlivenetwork", "live_network", "livenetwork", "execute_network", "executenetwork", "network_io_permitted", "networkiopermitted", "network_execution", "networkexecution"})
PRIVATE_PATH_PREFIXES = ("/private/", "/admin/", "/auth/", "/login", "/oauth", "/sso", "/session")
LOCAL_PATH_PREFIXES = ("/tmp/", "/var/tmp/", "/private/", "/home/", "/users/", "~", "./", "../")


class HandoffProcessorFamily(str, Enum):
    WEB_ARCHIVING = "web_archiving"
    LEGAL_SCRAPER = "legal_scraper"


class HandoffPolicyDecision(str, Enum):
    ALLOW = "allow"
    REFUSE = "refuse"
    DEFER = "defer"


@dataclass(frozen=True)
class HandoffPolicy:
    decision: HandoffPolicyDecision
    reasons: tuple[str, ...]
    evaluated_at: str
    evaluator: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.decision != HandoffPolicyDecision.ALLOW:
            errors.append("handoff fixture jobs must be allowed public processor handoffs")
        if not self.reasons:
            errors.append("policy reasons are required")
        if not self.evaluated_at.endswith("Z"):
            errors.append("policy evaluated_at must be an ISO UTC timestamp ending in Z")
        if not self.evaluator.strip():
            errors.append("policy evaluator is required")
        required_reasons = {"public_ppd_allowlisted", "robots_allowed", "no_persist_approved"}
        missing = required_reasons.difference(self.reasons)
        if missing:
            errors.append(f"policy is missing required allow reasons: {sorted(missing)}")
        return errors


@dataclass(frozen=True)
class HandoffProcessor:
    name: str
    family: HandoffProcessorFamily
    module: str
    version: str
    backend_path: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.name.strip():
            errors.append("processor name is required")
        if not self.version.strip():
            errors.append(f"processor {self.name or ''} version is required")
        if self.backend_path != IPFS_DATASETS_PROCESSOR_BACKEND:
            errors.append(
                "processor backend_path must be "
                f"{IPFS_DATASETS_PROCESSOR_BACKEND}, got {self.backend_path}"
            )
        if self.module.startswith("ppd.") or self.module.startswith("ppd/"):
            errors.append("processor module must not point to a PP&D fork")
        if not self.module.startswith(ALLOWED_PROCESSOR_MODULE_PREFIXES):
            errors.append(
                "processor module must reference ipfs_datasets_py web_archiving "
                "or legal_scrapers processors"
            )
        return errors


@dataclass(frozen=True)
class HandoffJob:
    id: str
    seed_id: str
    source_url: str
    canonical_url: str
    processor: HandoffProcessor
    operation: str
    arguments: Mapping[str, Any]
    policy: HandoffPolicy
    output_manifest_ref: str
    manifest_only: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id.strip():
            errors.append("job id is required")
        if not self.seed_id.strip():
            errors.append(f"job {self.id or ''}: seed_id is required")
        errors.extend(_validate_public_https_url(self.source_url, "source_url"))
        errors.extend(_validate_public_https_url(self.canonical_url, "canonical_url"))
        if not self.operation.strip():
            errors.append(f"job {self.id}: operation is required")
        if self.operation not in {"capture_url", "archive_url", "legal_archive_url"}:
            errors.append(f"job {self.id}: unsupported processor operation {self.operation}")
        if not self.manifest_only:
            errors.append(f"job {self.id}: handoff jobs must be manifest_only")
        if not self.output_manifest_ref.startswith("processor_archive_manifests/"):
            errors.append(
                f"job {self.id}: output_manifest_ref must point at "
                "processor_archive_manifests/"
            )
        if _arguments_request_raw_persistence(self.arguments):
            errors.append(f"job {self.id}: arguments must not request raw body or document persistence")
        errors.extend(f"job {self.id}: {error}" for error in _validate_invocation_arguments(self.arguments))
        if self.arguments.get("url") != self.source_url:
            errors.append(f"job {self.id}: arguments.url must match source_url")
        errors.extend(f"job {self.id}: processor: {error}" for error in self.processor.validate())
        errors.extend(f"job {self.id}: policy: {error}" for error in self.policy.validate())
        return errors


@dataclass(frozen=True)
class CrawlProcessorHandoffManifest:
    schema_version: int
    generated_at: str
    backend_path: str
    jobs: tuple[HandoffJob, ...]
    notes: Optional[str] = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.schema_version != 1:
            errors.append("crawl processor handoff schema_version must be 1")
        if not self.generated_at.endswith("Z"):
            errors.append("manifest generated_at must be an ISO UTC timestamp ending in Z")
        if self.backend_path != IPFS_DATASETS_PROCESSOR_BACKEND:
            errors.append(
                "manifest backend_path must be "
                f"{IPFS_DATASETS_PROCESSOR_BACKEND}, got {self.backend_path}"
            )
        if not self.jobs:
            errors.append("manifest requires at least one processor job")

        seen_job_ids: set[str] = set()
        seen_seed_ids: set[str] = set()
        for job in self.jobs:
            if job.id in seen_job_ids:
                errors.append(f"duplicate processor job id {job.id}")
            seen_job_ids.add(job.id)
            if job.seed_id in seen_seed_ids:
                errors.append(f"duplicate seed id {job.seed_id}")
            seen_seed_ids.add(job.seed_id)
            errors.extend(job.validate())

        return errors


def crawl_processor_handoff_manifest_from_dict(data: Mapping[str, Any]) -> CrawlProcessorHandoffManifest:
    jobs_data = data.get("processorJobs", data.get("processor_jobs", ()))
    jobs = tuple(_job_from_dict(item) for item in jobs_data if isinstance(item, Mapping))
    return CrawlProcessorHandoffManifest(
        schema_version=int(data.get("schemaVersion", data.get("schema_version", 0))),
        generated_at=str(data.get("generatedAt", data.get("generated_at", ""))),
        backend_path=str(data.get("backendPath", data.get("backend_path", ""))),
        notes=_optional_str(data.get("notes")),
        jobs=jobs,
    )


def assert_valid_crawl_processor_handoff_manifest(data: Mapping[str, Any]) -> None:
    privacy_findings = validate_crawl_manifest_privacy(data)
    if privacy_findings:
        details = "; ".join(f"{finding.path}: {finding.reason}" for finding in privacy_findings)
        raise ValueError(f"crawl processor handoff manifest failed privacy validation: {details}")

    manifest = crawl_processor_handoff_manifest_from_dict(data)
    errors = manifest.validate()
    if errors:
        raise ValueError("crawl processor handoff manifest failed validation: " + "; ".join(errors))


def _job_from_dict(data: Mapping[str, Any]) -> HandoffJob:
    processor_data = data.get("processor", {})
    policy_data = data.get("policyDecision", data.get("policy_decision", {}))
    if not isinstance(processor_data, Mapping):
        processor_data = {}
    if not isinstance(policy_data, Mapping):
        policy_data = {}

    return HandoffJob(
        id=str(data.get("id", "")),
        seed_id=str(data.get("seedId", data.get("seed_id", ""))),
        source_url=str(data.get("sourceUrl", data.get("source_url", ""))),
        canonical_url=str(data.get("canonicalUrl", data.get("canonical_url", ""))),
        processor=HandoffProcessor(
            name=str(processor_data.get("name", "")),
            family=HandoffProcessorFamily(str(processor_data.get("family", ""))),
            module=str(processor_data.get("module", "")),
            version=str(processor_data.get("version", "")),
            backend_path=str(processor_data.get("backendPath", processor_data.get("backend_path", ""))),
        ),
        operation=str(data.get("operation", "")),
        arguments=data.get("arguments", {}) if isinstance(data.get("arguments", {}), Mapping) else {},
        policy=HandoffPolicy(
            decision=HandoffPolicyDecision(str(policy_data.get("decision", ""))),
            reasons=tuple(str(reason) for reason in policy_data.get("reasons", ())),
            evaluated_at=str(policy_data.get("evaluatedAt", policy_data.get("evaluated_at", ""))),
            evaluator=str(policy_data.get("evaluator", "")),
        ),
        output_manifest_ref=str(data.get("outputManifestRef", data.get("output_manifest_ref", ""))),
        manifest_only=bool(data.get("manifestOnly", data.get("manifest_only", True))),
    )


def _validate_public_https_url(value: str, field_name: str) -> list[str]:
    errors: list[str] = []
    parsed = urlparse(value)
    if parsed.scheme != "https":
        errors.append(f"{field_name} must be an https URL")
    if parsed.netloc not in ALLOWED_PUBLIC_HOSTS:
        errors.append(f"{field_name} host is not PP&D allowlisted: {parsed.netloc}")
    if _is_private_devhub_path(parsed.netloc, parsed.path):
        errors.append(f"{field_name} must not reference private DevHub account paths")
    return errors


def _is_private_devhub_path(host: str, path: str) -> bool:
    if host != "devhub.portlandoregon.gov":
        return False
    private_prefixes = (
        "/account",
        "/dashboard",
        "/my-permits",
        "/mypermits",
        "/permits/my",
        "/requests/my",
        "/cart",
        "/payment",
        "/checkout",
        "/login",
        "/signin",
        "/sign-in",
    )
    lowered_path = path.lower()
    return any(lowered_path.startswith(prefix) for prefix in private_prefixes)


def _arguments_request_raw_persistence(arguments: Mapping[str, Any]) -> bool:
    forbidden_truthy_keys = {
        "persist_body",
        "persistBody",
        "save_body",
        "saveBody",
        "save_html",
        "saveHtml",
        "download_documents",
        "downloadDocuments",
        "write_raw_response",
        "writeRawResponse",
    }
    for key in forbidden_truthy_keys:
        if bool(arguments.get(key)):
            return True
    return False


def _validate_invocation_arguments(arguments: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    _walk_invocation_value(arguments, ("arguments",), errors)
    if _arguments_describe_skipped_capture(arguments) and _mapping_contains_hash(arguments):
        errors.append("skipped captures must not include invented hashes")
    return errors


def _walk_invocation_value(value: Any, path: tuple[str, ...], errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            lowered = _normalized_key(key_text)
            child_path = path + (key_text,)
            joined = ".".join(child_path)
            if lowered in RAW_BODY_ARGUMENT_KEYS:
                errors.append(f"raw body field is not allowed: {joined}")
            if lowered in RAW_ARCHIVE_PATH_ARGUMENT_KEYS:
                errors.append(f"raw archive path is not allowed: {joined}")
            if lowered in DOWNLOADED_DOCUMENT_PATH_ARGUMENT_KEYS:
                errors.append(f"downloaded document path is not allowed: {joined}")
            if lowered in SIDE_EFFECTFUL_NETWORK_ARGUMENT_KEYS and bool(child):
                errors.append(f"side-effectful network execution flag is not allowed: {joined}")
            if lowered.endswith("url") or lowered == "url":
                errors.extend(_validate_argument_url(child, joined))
            if lowered.endswith("path") or lowered in {"path", "file"}:
                errors.extend(_validate_not_local_private_path(child, joined))
            _walk_invocation_value(child, child_path, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_invocation_value(item, path + (str(index),), errors)


def _validate_argument_url(value: Any, path: str) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"URL field must be a non-empty string: {path}"]
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return [f"URL must use http or https: {path}"]
    if not parsed.hostname:
        return [f"URL is missing host: {path}"]
    host = parsed.hostname.lower()
    if _is_private_host(host):
        return [f"private URL is not allowed: {path}"]
    decoded_path = unquote(parsed.path).lower()
    if any(decoded_path.startswith(prefix) for prefix in PRIVATE_PATH_PREFIXES):
        return [f"private URL path is not allowed: {path}"]
    if _is_private_devhub_path(host, decoded_path):
        return [f"private DevHub URL is not allowed: {path}"]
    return []


def _is_private_host(host: str) -> bool:
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_private or address.is_loopback or address.is_link_local or address.is_reserved


def _validate_not_local_private_path(value: Any, path: str) -> list[str]:
    if not isinstance(value, str) or not value:
        return []
    normalized = value.replace("\\", "/")
    lowered = normalized.lower()
    if normalized.startswith(LOCAL_PATH_PREFIXES) or lowered.startswith(LOCAL_PATH_PREFIXES):
        return [f"local private path is not allowed: {path}"]
    parts = PurePosixPath(normalized).parts
    if ".." in parts:
        return [f"local private path is not allowed: {path}"]
    return []


def _arguments_describe_skipped_capture(arguments: Mapping[str, Any]) -> bool:
    status = str(arguments.get("status", arguments.get("captureStatus", ""))).lower()
    return bool(arguments.get("skipped")) or status == "skipped"


def _mapping_contains_hash(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if _normalized_key(str(key)) in HASH_ARGUMENT_KEYS and bool(child):
                return True
            if _mapping_contains_hash(child):
                return True
    if isinstance(value, list):
        return any(_mapping_contains_hash(item) for item in value)
    return False


def _normalized_key(value: str) -> str:
    return value.replace("-", "_").lower()


def _optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)
