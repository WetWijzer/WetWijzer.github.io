"""Fixture-first public recrawl operator packet v2.

This module intentionally performs no network, browser, processor, or source registry work.
It converts committed fixtures into an operator packet that can be reviewed offline before
any public recrawl is considered.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


REQUIRED_INPUTS = (
    "source_freshness_drift_escalation",
    "source_refresh_runbook",
    "public_source_refresh_operator_dry_run_transcript",
)

ATTESTATIONS = {
    "no_live_crawl": True,
    "no_processor_execution": True,
    "no_raw_body_capture": True,
    "no_source_registry_mutation": True,
    "fixture_first_only": True,
}


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _citation(ref: Mapping[str, Any]) -> dict[str, str]:
    fixture = str(ref.get("fixture", "unknown-fixture"))
    anchor = str(ref.get("anchor", "unknown-anchor"))
    return {"fixture": fixture, "anchor": anchor}


def _normalize_rate_limit(source: Mapping[str, Any], runbook: Mapping[str, Any]) -> dict[str, Any]:
    default_rate = _require_mapping(runbook.get("default_rate_limit", {}), "default_rate_limit")
    override = source.get("rate_limit")
    rate = deepcopy(default_rate)
    if isinstance(override, Mapping):
        rate.update(override)
    return {
        "requests_per_minute": int(rate.get("requests_per_minute", 6)),
        "burst": int(rate.get("burst", 1)),
        "concurrency": int(rate.get("concurrency", 1)),
        "backoff_seconds": int(rate.get("backoff_seconds", 30)),
    }


def build_public_recrawl_operator_packet_v2(fixtures: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic v2 operator packet from offline fixtures."""
    fixtures = _require_mapping(fixtures, "fixtures")
    missing = [name for name in REQUIRED_INPUTS if name not in fixtures]
    if missing:
        raise ValueError("missing required fixture inputs: " + ", ".join(missing))

    drift = _require_mapping(fixtures["source_freshness_drift_escalation"], "source_freshness_drift_escalation")
    runbook = _require_mapping(fixtures["source_refresh_runbook"], "source_refresh_runbook")
    transcript = _require_mapping(
        fixtures["public_source_refresh_operator_dry_run_transcript"],
        "public_source_refresh_operator_dry_run_transcript",
    )

    dry_run_decisions = {
        str(item.get("source_id")): item
        for item in transcript.get("source_decisions", [])
        if isinstance(item, Mapping) and item.get("source_id")
    }
    runbook_sources = {
        str(item.get("source_id")): item
        for item in runbook.get("sources", [])
        if isinstance(item, Mapping) and item.get("source_id")
    }

    cited_seed_batches: list[dict[str, Any]] = []
    allowlist_robots_decisions: list[dict[str, Any]] = []
    rate_limit_expectations: list[dict[str, Any]] = []
    skip_reasons: list[dict[str, Any]] = []
    metadata_artifact_expectations: list[dict[str, Any]] = []

    for source in drift.get("escalated_sources", []):
        if not isinstance(source, Mapping):
            continue
        source_id = str(source.get("source_id"))
        citation = _citation(source.get("citation", {})) if isinstance(source.get("citation"), Mapping) else _citation({})
        runbook_source = _require_mapping(runbook_sources.get(source_id, {}), f"runbook source {source_id}")
        dry_run_source = _require_mapping(dry_run_decisions.get(source_id, {}), f"dry run source {source_id}")

        seeds = [str(seed) for seed in source.get("seed_urls", [])]
        cited_seed_batches.append(
            {
                "source_id": source_id,
                "priority": str(source.get("priority", "normal")),
                "freshness_status": str(source.get("freshness_status", "unknown")),
                "seed_urls": seeds,
                "citation": citation,
            }
        )

        allowlisted = bool(runbook_source.get("allowlisted", False))
        robots = str(dry_run_source.get("robots", "unknown"))
        decision = "skip"
        if allowlisted and robots == "allowed" and seeds:
            decision = "eligible_for_future_live_recrawl"
        allowlist_robots_decisions.append(
            {
                "source_id": source_id,
                "allowlisted": allowlisted,
                "robots": robots,
                "decision": decision,
                "citation": _citation(dry_run_source.get("citation", citation)) if isinstance(dry_run_source.get("citation", citation), Mapping) else citation,
            }
        )

        rate_limit_expectations.append(
            {
                "source_id": source_id,
                "rate_limit": _normalize_rate_limit(runbook_source, runbook),
                "citation": _citation(runbook_source.get("citation", citation)) if isinstance(runbook_source.get("citation", citation), Mapping) else citation,
            }
        )

        reasons = [str(reason) for reason in dry_run_source.get("skip_reasons", [])]
        if not allowlisted:
            reasons.append("source_not_allowlisted")
        if robots != "allowed":
            reasons.append("robots_not_allowed")
        if not seeds:
            reasons.append("no_seed_urls")
        skip_reasons.append(
            {
                "source_id": source_id,
                "skip_reasons": sorted(set(reasons)),
                "citation": _citation(dry_run_source.get("citation", citation)) if isinstance(dry_run_source.get("citation", citation), Mapping) else citation,
            }
        )

        metadata_artifact_expectations.append(
            {
                "source_id": source_id,
                "artifact_mode": "metadata_only",
                "expected_fields": [
                    "source_id",
                    "seed_url",
                    "observed_at",
                    "http_status",
                    "content_type",
                    "content_length",
                    "robots_decision",
                    "rate_limit_policy",
                ],
                "forbidden_fields": ["raw_body", "rendered_body", "auth_state", "downloaded_document_path"],
            }
        )

    return {
        "packet_version": "public-recrawl-operator-packet-v2",
        "mode": "fixture_first_offline_review",
        "input_fixtures": list(REQUIRED_INPUTS),
        "cited_seed_batches": cited_seed_batches,
        "allowlist_robots_decisions": allowlist_robots_decisions,
        "rate_limit_expectations": rate_limit_expectations,
        "skip_reasons": skip_reasons,
        "metadata_only_artifact_expectations": metadata_artifact_expectations,
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/public_recrawl_operator_packet_v2.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_public_recrawl_operator_packet_v2.py"],
        ],
        "attestations": dict(ATTESTATIONS),
    }
