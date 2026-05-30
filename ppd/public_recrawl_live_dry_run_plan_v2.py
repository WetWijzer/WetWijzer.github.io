"""Fixture-first public recrawl live-dry-run plan v2.

This module intentionally builds an offline plan from committed fixtures only. It does
not crawl, download, authenticate, mutate registries, or invoke processors.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_ATTESTATIONS = {
    "no_live_crawl": True,
    "no_processor": True,
    "no_raw_body": True,
    "no_download": True,
    "no_source_registry_mutation": True,
}

METADATA_ONLY_CAPTURE_FIELDS = [
    "source_id",
    "seed_url",
    "selected_at_utc",
    "robots_policy",
    "robots_crawl_delay_seconds",
    "rate_limit_delay_seconds",
    "expected_http_status_bucket",
    "content_type_hint",
    "last_seen_header_hint",
    "etag_header_hint",
    "metadata_capture_only",
]

DEFAULT_STOP_CONDITIONS = [
    "Stop before any network request is issued.",
    "Stop if any fixture authorization is missing or not approved.",
    "Stop if robots fixture status is not allowed.",
    "Stop if a seed requires authentication, CAPTCHA, payment, upload, or form submission.",
    "Stop if capture would include raw response bodies or downloaded documents.",
]

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/public_recrawl_live_dry_run_plan_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_public_recrawl_live_dry_run_plan_v2.py"],
]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must be a JSON object: {path}")
    return data


def _citation(packet_id: str, field: str) -> dict[str, str]:
    return {"packet_id": packet_id, "field": field}


def build_plan(
    readiness_packet: dict[str, Any],
    operator_packet: dict[str, Any],
    allowlist_robots_packet: dict[str, Any],
) -> dict[str, Any]:
    readiness_id = str(readiness_packet.get("packet_id", "live-readiness-authorization-checklist-packet-v2"))
    operator_id = str(operator_packet.get("packet_id", "public-recrawl-operator-packet-v2"))
    allowlist_id = str(allowlist_robots_packet.get("packet_id", "source-allowlist-robots-fixtures-v2"))

    if readiness_packet.get("approved_for_fixture_dry_run") is not True:
        raise ValueError("readiness packet is not approved for fixture dry run")
    if operator_packet.get("mode") != "fixture_first_live_dry_run":
        raise ValueError("operator packet mode must be fixture_first_live_dry_run")

    max_seed_count = int(operator_packet.get("max_seed_count", 10))
    operator_delay = int(operator_packet.get("default_rate_limit_delay_seconds", 30))
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for source in allowlist_robots_packet.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_id = str(source.get("source_id", ""))
        allowed = source.get("allowlisted") is True
        robots = source.get("robots", {}) if isinstance(source.get("robots"), dict) else {}
        robots_allowed = robots.get("status") == "allowed"
        public = source.get("public_records_source") is True
        auth_required = source.get("requires_authentication") is True
        reason = []
        if not allowed:
            reason.append("not allowlisted")
        if not robots_allowed:
            reason.append("robots fixture is not allowed")
        if not public:
            reason.append("not marked as public records source")
        if auth_required:
            reason.append("requires authentication")

        if reason:
            rejected.append({"source_id": source_id, "reason": "; ".join(reason)})
            continue
        if len(selected) >= max_seed_count:
            rejected.append({"source_id": source_id, "reason": "operator max_seed_count reached"})
            continue

        crawl_delay = int(robots.get("crawl_delay_seconds", operator_delay))
        delay = max(operator_delay, crawl_delay)
        selected.append(
            {
                "batch_id": f"fixture-seed-batch-v2-{len(selected) + 1:03d}",
                "source_id": source_id,
                "seed_url": str(source.get("seed_url", "")),
                "selection_basis": "allowlisted public source with approved readiness and allowed robots fixture",
                "rate_limit_decision": {
                    "delay_seconds": delay,
                    "basis": "max(operator default delay, robots crawl-delay fixture)",
                    "citations": [
                        _citation(operator_id, "default_rate_limit_delay_seconds"),
                        _citation(allowlist_id, f"sources.{source_id}.robots.crawl_delay_seconds"),
                    ],
                },
                "robots_decision": {
                    "policy": "allowed",
                    "user_agent": str(robots.get("user_agent", "PPD-FixtureDryRun")),
                    "fixture_status": str(robots.get("status", "allowed")),
                    "citations": [_citation(allowlist_id, f"sources.{source_id}.robots")],
                },
                "expected_capture": {
                    "metadata_only": True,
                    "fields": list(METADATA_ONLY_CAPTURE_FIELDS),
                    "excluded_fields": ["raw_body", "response_text", "document_bytes", "download_path"],
                },
                "citations": [
                    _citation(readiness_id, "approved_for_fixture_dry_run"),
                    _citation(operator_id, "mode"),
                    _citation(allowlist_id, f"sources.{source_id}"),
                ],
            }
        )

    operator_stops = operator_packet.get("stop_conditions", [])
    stop_conditions = list(DEFAULT_STOP_CONDITIONS)
    if isinstance(operator_stops, list):
        stop_conditions.extend(str(item) for item in operator_stops)

    plan = {
        "plan_id": "public-recrawl-live-dry-run-plan-v2",
        "plan_version": 2,
        "mode": "fixture_first_public_recrawl_live_dry_run",
        "inputs": {
            "live_readiness_authorization_checklist_packet_v2": readiness_id,
            "public_recrawl_operator_packet_v2": operator_id,
            "source_allowlist_robots_fixtures_v2": allowlist_id,
        },
        "seed_batches": selected,
        "rejected_sources": rejected,
        "operator_stop_conditions": stop_conditions,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    validate_plan(plan)
    return plan


def build_plan_from_fixture_paths(
    readiness_path: Path,
    operator_path: Path,
    allowlist_robots_path: Path,
) -> dict[str, Any]:
    return build_plan(
        _load_json(readiness_path),
        _load_json(operator_path),
        _load_json(allowlist_robots_path),
    )


def validate_plan(plan: dict[str, Any]) -> None:
    if plan.get("mode") != "fixture_first_public_recrawl_live_dry_run":
        raise ValueError("unexpected plan mode")
    attestations = plan.get("attestations")
    if attestations != REQUIRED_ATTESTATIONS:
        raise ValueError("required safety attestations are missing or changed")
    batches = plan.get("seed_batches")
    if not isinstance(batches, list) or not batches:
        raise ValueError("plan must include at least one cited seed batch")
    for batch in batches:
        if batch.get("expected_capture", {}).get("metadata_only") is not True:
            raise ValueError("seed batch must be metadata-only")
        excluded = set(batch.get("expected_capture", {}).get("excluded_fields", []))
        if {"raw_body", "response_text", "document_bytes", "download_path"} - excluded:
            raise ValueError("raw body and download fields must be excluded")
        if not batch.get("citations"):
            raise ValueError("seed batch is missing citations")
        if batch.get("robots_decision", {}).get("policy") != "allowed":
            raise ValueError("seed batch has non-allowed robots decision")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fixture-first public recrawl live-dry-run plan v2")
    parser.add_argument("--readiness", required=True, type=Path)
    parser.add_argument("--operator", required=True, type=Path)
    parser.add_argument("--allowlist-robots", required=True, type=Path)
    args = parser.parse_args()
    plan = build_plan_from_fixture_paths(args.readiness, args.operator, args.allowlist_robots)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
