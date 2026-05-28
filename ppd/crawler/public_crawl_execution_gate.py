"""Fixture-first public crawl execution gate for PP&D.

The gate consumes a public crawl readiness handoff packet and returns an
explicit dry-run-only eligibility decision. It performs deterministic validation
only: no HTTP requests, browser automation, processor execution, or artifact
writes occur here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from ppd.contracts.crawl_processor_handoff import assert_valid_crawl_processor_handoff_manifest
from ppd.crawler.crawl_policy import DEFAULT_ALLOWLIST_PATH, CrawlPolicy
from ppd.crawler.public_crawl_readiness import validate_public_crawl_readiness


_FORBIDDEN_OUTPUT_KEYS = {
    "archive_path",
    "body",
    "content",
    "download_path",
    "downloaded_document_path",
    "document_path",
    "html",
    "local_path",
    "raw_archive_path",
    "raw_body",
    "raw_content",
    "raw_html",
    "response_body",
    "saved_path",
    "text",
    "warc_path",
}
_LIVE_EXECUTION_KEYS = {
    "allow_live_network",
    "execute_live",
    "invoke_processor",
    "live_crawl",
    "live_network",
    "network_enabled",
    "run_live",
}
_METADATA_ONLY_MARKERS = ("metadata_only", "manifest_only", "no_raw_body_persisted")


@dataclass(frozen=True)
class GateCheck:
    name: str
    passed: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "evidence": self.evidence,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class PublicCrawlExecutionDecision:
    decision: str
    eligible: bool
    dry_run_only: bool
    live_network_permitted: bool
    evaluated_at: str
    checks: tuple[GateCheck, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": "ppd_public_crawl_execution_gate",
            "decision": self.decision,
            "eligible": self.eligible,
            "dry_run_only": self.dry_run_only,
            "live_network_permitted": self.live_network_permitted,
            "evaluated_at": self.evaluated_at,
            "planned_execution": {
                "network_requests": 0,
                "processor_invocations": 0,
                "raw_artifacts_written": 0,
                "downloaded_documents_written": 0,
            },
            "checks": [check.to_dict() for check in self.checks],
        }


def evaluate_public_crawl_execution_gate(
    packet: Mapping[str, Any],
    *,
    allowlist_path: Path = DEFAULT_ALLOWLIST_PATH,
    now: datetime | None = None,
) -> PublicCrawlExecutionDecision:
    """Return an explicit dry-run-only eligibility decision for a handoff packet."""

    checked_at = now or datetime.now(timezone.utc)
    if checked_at.tzinfo is None:
        checked_at = checked_at.replace(tzinfo=timezone.utc)
    checked_at = checked_at.astimezone(timezone.utc)

    if not isinstance(packet, Mapping):
        check = GateCheck("packet_shape", False, errors=("packet must be a mapping",))
        return _decision((check,), checked_at)

    checks = (
        _dry_run_mode_check(packet),
        _readiness_check(packet, checked_at),
        _allowlist_check(packet, allowlist_path),
        _robots_policy_check(packet),
        _rate_limit_check(packet),
        _processor_contract_check(packet),
        _metadata_only_output_check(packet),
    )
    return _decision(checks, checked_at)


def decision_dict(packet: Mapping[str, Any], *, allowlist_path: Path = DEFAULT_ALLOWLIST_PATH) -> dict[str, Any]:
    """Convenience wrapper for JSON fixtures and daemon validation."""

    return evaluate_public_crawl_execution_gate(packet, allowlist_path=allowlist_path).to_dict()


def _decision(checks: tuple[GateCheck, ...], checked_at: datetime) -> PublicCrawlExecutionDecision:
    eligible = all(check.passed for check in checks)
    return PublicCrawlExecutionDecision(
        decision="eligible_dry_run_only" if eligible else "ineligible",
        eligible=eligible,
        dry_run_only=True,
        live_network_permitted=False,
        evaluated_at=checked_at.isoformat().replace("+00:00", "Z"),
        checks=checks,
    )


def _dry_run_mode_check(packet: Mapping[str, Any]) -> GateCheck:
    errors: list[str] = []
    _collect_live_execution_flags(packet, errors, "packet")
    mode = str(packet.get("execution_mode", packet.get("mode", ""))).strip().lower()
    if mode not in {"dry_run_only", "fixture_dry_run", "public_crawl_dry_run_gate"}:
        errors.append("execution_mode must be dry_run_only")
    return GateCheck(
        "dry_run_only",
        not errors,
        {"execution_mode": mode or None, "live_network_permitted": False},
        tuple(errors),
    )


def _readiness_check(packet: Mapping[str, Any], checked_at: datetime) -> GateCheck:
    errors = validate_public_crawl_readiness(dict(packet), now=checked_at)
    return GateCheck("readiness_handoff", not errors, {"validator": "ppd.crawler.public_crawl_readiness"}, tuple(errors))


def _allowlist_check(packet: Mapping[str, Any], allowlist_path: Path) -> GateCheck:
    errors: list[str] = []
    evidence: dict[str, Any] = {"allowlist_path": allowlist_path.as_posix(), "checked_urls": []}
    try:
        policy = CrawlPolicy.load(allowlist_path)
    except Exception as exc:
        return GateCheck("allowlist", False, evidence, (f"failed to load allowlist: {exc}",))

    urls = _packet_public_urls(packet)
    if not urls:
        errors.append("packet must include at least one URL to preflight against the allowlist")

    checked_urls: list[dict[str, Any]] = []
    for url in urls:
        decision = policy.preflight(url)
        checked_urls.append(
            {
                "url": url,
                "host": urlparse(url).netloc.lower(),
                "allowed": decision.allowed,
                "reason_code": decision.reason_code,
            }
        )
        if not decision.allowed:
            errors.append(f"{url} failed allowlist preflight: {decision.reason_code}")
    evidence["checked_urls"] = checked_urls
    return GateCheck("allowlist", not errors, evidence, tuple(errors))


def _robots_policy_check(packet: Mapping[str, Any]) -> GateCheck:
    errors: list[str] = []
    robots = _normalized_status(packet, ("robots_status", "robots_txt_status", "robots"))
    policy = _normalized_status(packet, ("policy_status", "crawl_policy_status", "public_policy_status"))
    if robots not in {"allowed", "permitted", "public_allowed"}:
        errors.append("robots status must be explicitly allowed")
    if policy not in {"approved", "allowed", "public", "public_allowed"}:
        errors.append("crawl policy status must be explicitly approved")
    return GateCheck("robots_and_policy", not errors, {"robots_status": robots, "policy_status": policy}, tuple(errors))


def _rate_limit_check(packet: Mapping[str, Any]) -> GateCheck:
    rate_limit = packet.get("rate_limit", packet.get("rate_limits", packet.get("crawl_rate_limit")))
    errors: list[str] = []
    if not isinstance(rate_limit, Mapping):
        errors.append("rate_limit must be a mapping")
    elif not any(_positive_number(rate_limit.get(key)) for key in ("requests_per_minute", "requests_per_hour", "min_delay_seconds", "crawl_delay_seconds")):
        errors.append("rate_limit must include a positive limit or delay")
    return GateCheck("rate_limit", not errors, {"rate_limit": dict(rate_limit) if isinstance(rate_limit, Mapping) else rate_limit}, tuple(errors))


def _processor_contract_check(packet: Mapping[str, Any]) -> GateCheck:
    manifest = packet.get("processor_handoff_manifest", packet.get("processorHandoffManifest"))
    if not isinstance(manifest, Mapping):
        return GateCheck("processor_contract", False, errors=("processor_handoff_manifest is required",))
    try:
        assert_valid_crawl_processor_handoff_manifest(manifest)
    except Exception as exc:
        return GateCheck("processor_contract", False, {"manifest_present": True}, (str(exc),))
    jobs = manifest.get("processorJobs", manifest.get("processor_jobs", []))
    job_count = len(jobs) if isinstance(jobs, list) else 0
    return GateCheck(
        "processor_contract",
        True,
        {"manifest_present": True, "job_count": job_count, "processor_invocations": 0},
    )


def _metadata_only_output_check(packet: Mapping[str, Any]) -> GateCheck:
    outputs = packet.get("planned_outputs", packet.get("plannedOutputs", packet.get("output_evidence", [])))
    errors: list[str] = []
    if not isinstance(outputs, list) or not outputs:
        return GateCheck("metadata_only_outputs", False, errors=("planned metadata-only output evidence is required",))
    for index, output in enumerate(outputs):
        if not isinstance(output, Mapping):
            errors.append(f"planned_outputs[{index}] must be a mapping")
            continue
        marker_values = [bool(output.get(marker)) for marker in _METADATA_ONLY_MARKERS]
        if not any(marker_values):
            errors.append(f"planned_outputs[{index}] must be marked metadata_only, manifest_only, or no_raw_body_persisted")
        _collect_forbidden_output_fields(output, errors, f"planned_outputs[{index}]")
    return GateCheck("metadata_only_outputs", not errors, {"output_count": len(outputs)}, tuple(errors))


def _packet_public_urls(packet: Mapping[str, Any]) -> list[str]:
    urls: list[str] = []
    for key in ("url", "source_url", "start_url"):
        value = packet.get(key)
        if isinstance(value, str):
            urls.append(value)
    value = packet.get("urls")
    if isinstance(value, list):
        urls.extend(item for item in value if isinstance(item, str))
    anchors = packet.get("source_anchors", packet.get("anchors", packet.get("sources", [])))
    if isinstance(anchors, list):
        for anchor in anchors:
            if isinstance(anchor, Mapping):
                for key in ("url", "href", "source_url"):
                    value = anchor.get(key)
                    if isinstance(value, str):
                        urls.append(value)
                        break
    manifest = packet.get("processor_handoff_manifest", packet.get("processorHandoffManifest"))
    if isinstance(manifest, Mapping):
        jobs = manifest.get("processorJobs", manifest.get("processor_jobs", []))
        if isinstance(jobs, list):
            for job in jobs:
                if isinstance(job, Mapping):
                    for key in ("sourceUrl", "source_url", "canonicalUrl", "canonical_url"):
                        value = job.get(key)
                        if isinstance(value, str):
                            urls.append(value)
    return sorted(set(urls))


def _collect_forbidden_output_fields(value: Any, errors: list[str], path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text.lower() in _FORBIDDEN_OUTPUT_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} must not include raw body, archive, document, or local path evidence")
            _collect_forbidden_output_fields(child, errors, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_forbidden_output_fields(child, errors, f"{path}[{index}]")


def _collect_live_execution_flags(value: Any, errors: list[str], path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in _LIVE_EXECUTION_KEYS and child is True:
                errors.append(f"{child_path} must not enable live crawl, network, or processor execution")
            _collect_live_execution_flags(child, errors, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_live_execution_flags(child, errors, f"{path}[{index}]")


def _normalized_status(packet: Mapping[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = packet.get(key)
        if isinstance(value, str):
            normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
            if normalized:
                return normalized
        if isinstance(value, Mapping):
            nested = _normalized_status(value, ("status", "state", "decision"))
            if nested:
                return nested
    return None


def _positive_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        try:
            return float(value) > 0
        except ValueError:
            return False
    return False
