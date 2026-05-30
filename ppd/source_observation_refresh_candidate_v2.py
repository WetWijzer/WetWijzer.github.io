"""Fixture-first source observation refresh candidate v2 builder.

This module is intentionally metadata-only. It consumes already-produced dry-run
packets and emits candidate observations without crawling, downloading,
processing source bodies, or mutating source registries.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ATTESTATIONS = {
    "no_live_crawl": True,
    "no_processor": True,
    "no_raw_body": True,
    "no_download": True,
    "no_source_registry_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/source_observation_refresh_candidate_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_source_observation_refresh_candidate_v2"],
]

DEFAULT_ALLOWED_HOSTS = {
    "www.portland.gov",
    "portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
}

MUTATION_FLAG_NAMES = {
    "active_source_mutation",
    "source_mutation",
    "schedule_mutation",
    "requirement_mutation",
    "process_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "monitoring_mutation",
    "release_state_mutation",
    "agent_state_mutation",
    "mutates_active_sources",
    "mutates_schedule",
    "mutates_requirements",
    "mutates_process",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
}

PROHIBITED_ARTIFACT_KEYS = {
    "raw_body",
    "body",
    "html_body",
    "response_body",
    "raw_download",
    "download",
    "download_path",
    "download_url",
    "archive",
    "archive_path",
    "archive_url",
    "raw_crawl_output",
    "browser_artifact",
    "browser_artifacts",
    "screenshot",
    "screenshot_path",
    "trace",
    "trace_path",
    "har",
    "har_path",
    "storage_state",
    "auth_state",
    "session_state",
}

PROHIBITED_CLAIM_TERMS = (
    "live crawler completed",
    "crawler completed",
    "live crawl completed",
    "crawl completed",
    "processor completed",
    "processing completed",
    "live crawler",
    "live crawl",
    "processor run finished",
    "permit approved",
    "permit will be approved",
    "approval is guaranteed",
    "guaranteed approval",
    "guarantees approval",
    "legal guarantee",
    "legally guaranteed",
    "permitting outcome guaranteed",
    "outcome guaranteed",
    "guaranteed permitting outcome",
)

AUTH_QUERY_TOKENS = ("token=", "key=", "password=", "session=", "auth=", "code=", "secret=")
AUTH_PATH_TOKENS = ("/dashboard", "/account", "/my-permits", "/mypermits", "/secure", "/private")


@dataclass(frozen=True)
class CandidateValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def _items(packet: dict[str, Any], *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        value = packet.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _source_id(item: dict[str, Any]) -> str | None:
    value = item.get("source_id") or item.get("id") or item.get("source")
    return str(value) if value else None


def _reviewer_owner(source_id: str, live_packet: dict[str, Any], triage_packet: dict[str, Any]) -> str:
    for item in _items(live_packet, "review_items", "accepted_items", "items"):
        if _source_id(item) == source_id and item.get("reviewer_owner"):
            return str(item["reviewer_owner"])
    for item in _items(triage_packet, "triage_items", "items"):
        if _source_id(item) == source_id and item.get("reviewer_owner"):
            return str(item["reviewer_owner"])
    return "ppd-reviewer-unassigned"


def _citation(packet_name: str, item: dict[str, Any]) -> dict[str, str]:
    citation = {
        "packet": packet_name,
        "source_id": str(_source_id(item) or "unknown"),
    }
    if item.get("evidence_id"):
        citation["evidence_id"] = str(item["evidence_id"])
    if item.get("review_id"):
        citation["review_id"] = str(item["review_id"])
    if item.get("triage_id"):
        citation["triage_id"] = str(item["triage_id"])
    if item.get("observed_at"):
        citation["observed_at"] = str(item["observed_at"])
    return citation


def build_source_observation_refresh_candidate_v2(
    live_dry_run_acceptance_review_packet_v2: dict[str, Any],
    public_recrawl_dry_run_evidence_envelope_v2: dict[str, Any],
    source_freshness_drift_triage_v2: dict[str, Any],
) -> dict[str, Any]:
    accepted: set[str] = set()
    skipped: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []

    for item in _items(live_dry_run_acceptance_review_packet_v2, "review_items", "accepted_items", "items"):
        source_id = _source_id(item)
        if not source_id:
            skipped.append({"reason": "missing_source_id", "citation": _citation("live_dry_run_acceptance_review_packet_v2", item)})
            continue
        status = str(item.get("status", "accepted")).lower()
        if status in {"accepted", "candidate", "reviewed"}:
            accepted.add(source_id)
        elif status in {"defer", "deferred"}:
            deferred.append({"source_id": source_id, "reason": str(item.get("reason", "acceptance_review_deferred")), "citation": _citation("live_dry_run_acceptance_review_packet_v2", item)})
        else:
            skipped.append({"source_id": source_id, "reason": str(item.get("reason", f"acceptance_review_status_{status}")), "citation": _citation("live_dry_run_acceptance_review_packet_v2", item)})

    evidence_by_source: dict[str, list[dict[str, Any]]] = {}
    for item in _items(public_recrawl_dry_run_evidence_envelope_v2, "evidence", "evidence_items", "items"):
        source_id = _source_id(item)
        if not source_id:
            skipped.append({"reason": "evidence_missing_source_id", "citation": _citation("public_recrawl_dry_run_evidence_envelope_v2", item)})
            continue
        evidence_by_source.setdefault(source_id, []).append(item)

    triage_by_source: dict[str, dict[str, Any]] = {}
    for item in _items(source_freshness_drift_triage_v2, "triage_items", "items"):
        source_id = _source_id(item)
        if not source_id:
            skipped.append({"reason": "triage_missing_source_id", "citation": _citation("source_freshness_drift_triage_v2", item)})
            continue
        triage_by_source[source_id] = item
        decision = str(item.get("decision", "candidate")).lower()
        if decision in {"defer", "deferred"}:
            deferred.append({"source_id": source_id, "reason": str(item.get("reason", "freshness_drift_deferred")), "citation": _citation("source_freshness_drift_triage_v2", item)})
        elif decision in {"skip", "skipped"}:
            skipped.append({"source_id": source_id, "reason": str(item.get("reason", "freshness_drift_skipped")), "citation": _citation("source_freshness_drift_triage_v2", item)})

    blocked = {str(item.get("source_id")) for item in skipped + deferred if item.get("source_id")}
    candidates: list[dict[str, Any]] = []
    for source_id in sorted(accepted | set(evidence_by_source) | set(triage_by_source)):
        if source_id in blocked:
            continue
        evidence_items = evidence_by_source.get(source_id, [])
        triage_item = triage_by_source.get(source_id)
        if not evidence_items:
            deferred.append({"source_id": source_id, "reason": "missing_public_recrawl_dry_run_evidence", "citation": {"packet": "public_recrawl_dry_run_evidence_envelope_v2", "source_id": source_id}})
            continue
        citations = [_citation("public_recrawl_dry_run_evidence_envelope_v2", item) for item in evidence_items]
        if triage_item:
            citations.append(_citation("source_freshness_drift_triage_v2", triage_item))
        candidates.append(
            {
                "source_id": source_id,
                "affected_source_ids": [source_id],
                "reviewer_owner": _reviewer_owner(source_id, live_dry_run_acceptance_review_packet_v2, source_freshness_drift_triage_v2),
                "observation_type": "public_source_observation_refresh_candidate_v2",
                "metadata_only": True,
                "candidate_metadata": {
                    "freshness_state": str((triage_item or {}).get("freshness_state", "unknown")),
                    "drift_signal": str((triage_item or {}).get("drift_signal", "not_supplied")),
                    "evidence_count": len(evidence_items),
                },
                "citations": citations,
            }
        )

    result = {
        "schema_version": "public_source_observation_refresh_candidate_v2",
        "generated_by": "ppd.source_observation_refresh_candidate_v2",
        "metadata_only": True,
        "attestations": dict(ATTESTATIONS),
        "affected_source_ids": sorted({candidate["source_id"] for candidate in candidates}),
        "candidates": candidates,
        "skipped": skipped,
        "deferred": deferred,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }
    require_source_observation_refresh_candidate_v2(result)
    return result


def validate_source_observation_refresh_candidate_v2(packet: dict[str, Any]) -> CandidateValidationResult:
    errors: list[str] = []
    if packet.get("schema_version") != "public_source_observation_refresh_candidate_v2":
        errors.append("schema_version must be public_source_observation_refresh_candidate_v2")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")
    if packet.get("attestations") != ATTESTATIONS:
        errors.append("attestations must preserve metadata-only no-crawl guardrails")

    allowlisted_hosts = _allowlisted_hosts(packet.get("url_allowlist")) or set(DEFAULT_ALLOWED_HOSTS)
    _validate_candidate_observations(packet.get("candidates"), packet.get("affected_source_ids"), errors)
    _validate_skip_or_defer(packet.get("skipped"), "skipped", errors)
    _validate_skip_or_defer(packet.get("deferred"), "deferred", errors)
    _reject_unsafe_urls(packet, "$", allowlisted_hosts, errors)
    _reject_prohibited_artifacts(packet, "$", errors)
    _reject_prohibited_claims(packet, "$", errors)
    _reject_mutation_flags(packet, "$", errors)
    return CandidateValidationResult(ok=not errors, errors=tuple(errors))


def require_source_observation_refresh_candidate_v2(packet: dict[str, Any]) -> None:
    result = validate_source_observation_refresh_candidate_v2(packet)
    if not result.ok:
        raise ValueError("invalid source observation refresh candidate v2: " + "; ".join(result.errors))


def _validate_candidate_observations(candidates: Any, affected_source_ids: Any, errors: list[str]) -> None:
    if not isinstance(affected_source_ids, list) or not affected_source_ids:
        errors.append("affected_source_ids must be a non-empty list")
    if not isinstance(candidates, list) or not candidates:
        errors.append("candidates must be a non-empty list")
        return
    for index, candidate in enumerate(candidates):
        path = f"candidates[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{path} must be an object")
            continue
        source_id = candidate.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"{path}.source_id is required")
        candidate_affected = candidate.get("affected_source_ids")
        if not isinstance(candidate_affected, list) or not candidate_affected:
            errors.append(f"{path}.affected_source_ids must be non-empty")
        if candidate.get("metadata_only") is not True:
            errors.append(f"{path}.metadata_only must be true")
        citations = candidate.get("citations")
        if not isinstance(citations, list) or not citations:
            errors.append(f"{path}.citations must be non-empty")


def _validate_skip_or_defer(items: Any, name: str, errors: list[str]) -> None:
    if items is None:
        return
    if not isinstance(items, list):
        errors.append(f"{name} must be a list")
        return
    for index, item in enumerate(items):
        path = f"{name}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        rationale = item.get("rationale") or item.get("reason") or item.get("skipped_reason") or item.get("deferred_reason")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{path}.reason is required for skip/defer rationale")
        citation = item.get("citation") or item.get("citations")
        if not citation:
            errors.append(f"{path}.citation is required")


def _allowlisted_hosts(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    hosts: set[str] = set()
    for item in value:
        if isinstance(item, str) and item.strip():
            parsed = urlparse(item if "://" in item else "https://" + item)
            if parsed.hostname:
                hosts.add(parsed.hostname.lower())
    return hosts


def _reject_unsafe_urls(value: Any, path: str, allowlisted_hosts: set[str], errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if _looks_like_url_key(str(key)) and isinstance(child, str):
                _validate_public_url(child, child_path, allowlisted_hosts, errors)
            _reject_unsafe_urls(child, child_path, allowlisted_hosts, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_urls(child, f"{path}[{index}]", allowlisted_hosts, errors)


def _looks_like_url_key(key: str) -> bool:
    lowered = key.lower()
    return lowered == "url" or lowered.endswith("_url") or lowered.endswith("_uri")


def _validate_public_url(url: str, path: str, allowlisted_hosts: set[str], errors: list[str]) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        errors.append(f"{path} must be an https public URL")
        return
    host = parsed.hostname.lower()
    if host not in allowlisted_hosts:
        errors.append(f"{path} host is not allowlisted")
    if "@" in parsed.netloc or parsed.username or parsed.password:
        errors.append(f"{path} must not contain authentication material")
    lowered_query = parsed.query.lower()
    if any(token in lowered_query for token in AUTH_QUERY_TOKENS):
        errors.append(f"{path} query appears to contain authentication material")
    lowered_path = parsed.path.lower()
    if any(token in lowered_path for token in AUTH_PATH_TOKENS):
        errors.append(f"{path} appears to reference authenticated or private source state")


def _reject_prohibited_artifacts(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if str(key).lower() in PROHIBITED_ARTIFACT_KEYS:
                errors.append(f"{child_path} is prohibited in source observation refresh candidates")
            _reject_prohibited_artifacts(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_artifacts(child, f"{path}[{index}]", errors)


def _reject_prohibited_claims(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        for term in PROHIBITED_CLAIM_TERMS:
            if term in lowered:
                errors.append(f"{path} contains prohibited live completion, legal, or permitting outcome claim")
                break
    elif isinstance(value, dict):
        for key, child in value.items():
            _reject_prohibited_claims(child, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_claims(child, f"{path}[{index}]", errors)


def _reject_mutation_flags(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if str(key) in MUTATION_FLAG_NAMES and child is True:
                errors.append(f"{child_path} must not be true in source observation refresh candidates")
            _reject_mutation_flags(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_mutation_flags(child, f"{path}[{index}]", errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fixture-first PP&D source observation refresh candidates v2.")
    parser.add_argument("--live-dry-run-acceptance-review-packet-v2", required=True)
    parser.add_argument("--public-recrawl-dry-run-evidence-envelope-v2", required=True)
    parser.add_argument("--source-freshness-drift-triage-v2", required=True)
    args = parser.parse_args()
    result = build_source_observation_refresh_candidate_v2(
        load_json(args.live_dry_run_acceptance_review_packet_v2),
        load_json(args.public_recrawl_dry_run_evidence_envelope_v2),
        load_json(args.source_freshness_drift_triage_v2),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
