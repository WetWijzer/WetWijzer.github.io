"""Fixture-first public source freshness watch plan v3 builder.

This module intentionally consumes committed metadata fixtures only. It does not
crawl, download, invoke processors, persist raw bodies, or mutate a source
registry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

WATCH_PLAN_VERSION = "public_source_freshness_watch_plan_v3"
REQUIRED_ATTESTATIONS = {
    "no_live_crawl": True,
    "no_download": True,
    "no_processor_invocation": True,
    "no_raw_body_persistence": True,
    "no_source_registry_mutation": True,
}
HIGH_SIGNAL_FIELDS = {
    "fee",
    "payment",
    "deadline",
    "expiration",
    "upload",
    "submission",
    "certification",
    "devhub_action",
    "required_document",
    "file_naming_rule",
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def sorted_unique(values: Iterable[Any]) -> List[str]:
    return sorted({str(value) for value in values if value not in (None, "")})


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def index_by_source(items: Sequence[Mapping[str, Any]]) -> Dict[str, List[Mapping[str, Any]]]:
    indexed: Dict[str, List[Mapping[str, Any]]] = {}
    for item in items:
        for source_id in as_list(item.get("source_id")) + as_list(item.get("source_ids")):
            if source_id:
                indexed.setdefault(str(source_id), []).append(item)
    return indexed


def inactive_reason_by_source(packet: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    inactive: Dict[str, Mapping[str, Any]] = {}
    for item in packet.get("inactive_sources", []):
        if not isinstance(item, Mapping):
            continue
        source_id = item.get("source_id")
        if source_id:
            inactive[str(source_id)] = item
    return inactive


def collect_guardrail_context(source_id: str, replay_rows: Sequence[Mapping[str, Any]]) -> Tuple[List[str], List[str], List[List[str]], List[str]]:
    requirement_ids: List[str] = []
    guardrail_ids: List[str] = []
    commands: List[List[str]] = []
    owners: List[str] = []
    for row in replay_rows:
        source_ids = {str(value) for value in as_list(row.get("source_id")) + as_list(row.get("source_ids"))}
        if source_id not in source_ids:
            continue
        requirement_ids.extend(str(value) for value in as_list(row.get("requirement_id")) + as_list(row.get("requirement_ids")))
        guardrail_ids.extend(str(value) for value in as_list(row.get("guardrail_id")) + as_list(row.get("guardrail_ids")))
        owner = row.get("owner") or row.get("reviewer_owner")
        if owner:
            owners.append(str(owner))
        for command in row.get("offline_validation_commands", []):
            if isinstance(command, list) and all(isinstance(part, str) for part in command):
                commands.append(command)
    return sorted_unique(requirement_ids), sorted_unique(guardrail_ids), commands, sorted_unique(owners)


def priority_for(candidate: Mapping[str, Any], inactive_entry: Optional[Mapping[str, Any]], guardrail_ids: Sequence[str]) -> str:
    if inactive_entry is not None:
        return "defer"
    explicit_priority = candidate.get("recrawl_priority") or candidate.get("priority")
    if explicit_priority in {"critical", "high", "medium", "low"}:
        return str(explicit_priority)
    changed_fields = {str(value).lower() for value in as_list(candidate.get("changed_fields"))}
    signals = {str(value).lower() for value in as_list(candidate.get("freshness_signal")) + as_list(candidate.get("signals"))}
    if changed_fields & HIGH_SIGNAL_FIELDS:
        return "high"
    if "hash_changed" in signals or "visible_updated_date_changed" in signals:
        return "high"
    if guardrail_ids:
        return "medium"
    return "low"


def metadata_expectations(candidate: Mapping[str, Any], inactive_entry: Optional[Mapping[str, Any]]) -> List[str]:
    if inactive_entry is not None:
        replacement = inactive_entry.get("replacement_source_id") or inactive_entry.get("migration_replacement_source_id")
        expectations = ["do not recrawl inactive source", "record fixture migration review only"]
        if replacement:
            expectations.append(f"review replacement source metadata: {replacement}")
        return expectations
    expectations = [
        "compare canonical URL and source ID only",
        "compare prior and candidate freshness metadata",
        "record changed metadata fields without persisting response bodies",
    ]
    if candidate.get("citation_ids"):
        expectations.append("preserve existing citation IDs for reviewer traceability")
    return expectations


def skip_defer_reason(candidate: Mapping[str, Any], inactive_entry: Optional[Mapping[str, Any]]) -> str:
    if inactive_entry is not None:
        reason = inactive_entry.get("migration_reason") or inactive_entry.get("reason") or "inactive source fixture migration pending"
        return str(reason)
    if candidate.get("allow_recrawl_candidate") is False:
        return str(candidate.get("skip_reason") or "candidate is metadata-only and not approved for recrawl")
    return "none; eligible for cited metadata-only recrawl planning"


def command_key(command: Sequence[str]) -> Tuple[str, ...]:
    return tuple(command)


def merge_commands(commands: Iterable[Sequence[str]]) -> List[List[str]]:
    seen: Set[Tuple[str, ...]] = set()
    merged: List[List[str]] = []
    for command in commands:
        key = command_key(command)
        if key in seen:
            continue
        seen.add(key)
        merged.append(list(command))
    return merged


def build_watch_plan(
    observation_refresh_candidate_v2: Mapping[str, Any],
    inactive_source_fixture_migration_packet_v2: Mapping[str, Any],
    guardrail_regression_replay_matrix_v3: Mapping[str, Any],
) -> Dict[str, Any]:
    candidates = observation_refresh_candidate_v2.get("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("observation refresh candidate fixture must contain a candidates list")
    replay_rows = guardrail_regression_replay_matrix_v3.get("replay_rows", [])
    if not isinstance(replay_rows, list):
        raise ValueError("guardrail replay matrix fixture must contain a replay_rows list")
    inactive_by_source = inactive_reason_by_source(inactive_source_fixture_migration_packet_v2)

    rows: List[Dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        source_id = candidate.get("source_id")
        if not source_id:
            raise ValueError("each candidate must include source_id")
        source_id_text = str(source_id)
        inactive_entry = inactive_by_source.get(source_id_text)
        matrix_requirement_ids, matrix_guardrail_ids, matrix_commands, matrix_owners = collect_guardrail_context(source_id_text, replay_rows)
        candidate_requirement_ids = as_list(candidate.get("affected_requirement_ids")) + as_list(candidate.get("requirement_ids"))
        candidate_guardrail_ids = as_list(candidate.get("affected_guardrail_ids")) + as_list(candidate.get("guardrail_ids"))
        candidate_commands = candidate.get("offline_validation_commands", [])
        valid_candidate_commands = [command for command in candidate_commands if isinstance(command, list) and all(isinstance(part, str) for part in command)]
        owner_values = as_list(candidate.get("reviewer_owner")) + as_list(candidate.get("owner")) + matrix_owners
        if inactive_entry is not None:
            owner_values.extend(as_list(inactive_entry.get("reviewer_owner")) + as_list(inactive_entry.get("owner")))
            candidate_requirement_ids.extend(as_list(inactive_entry.get("affected_requirement_ids")) + as_list(inactive_entry.get("requirement_ids")))
            candidate_guardrail_ids.extend(as_list(inactive_entry.get("affected_guardrail_ids")) + as_list(inactive_entry.get("guardrail_ids")))

        affected_requirement_ids = sorted_unique(candidate_requirement_ids + matrix_requirement_ids)
        affected_guardrail_ids = sorted_unique(candidate_guardrail_ids + matrix_guardrail_ids)
        row = {
            "watch_row_id": f"watch-v3-{source_id_text}",
            "source_id": source_id_text,
            "canonical_url": str(candidate.get("canonical_url") or ""),
            "source_type": str(candidate.get("source_type") or "public_source"),
            "citation_ids": sorted_unique(as_list(candidate.get("citation_ids")) + as_list(candidate.get("source_evidence_ids"))),
            "freshness_signal": sorted_unique(as_list(candidate.get("freshness_signal")) + as_list(candidate.get("signals"))),
            "changed_fields": sorted_unique(as_list(candidate.get("changed_fields"))),
            "recrawl_priority": priority_for(candidate, inactive_entry, affected_guardrail_ids),
            "metadata_only_watch_expectations": metadata_expectations(candidate, inactive_entry),
            "skip_defer_reason": skip_defer_reason(candidate, inactive_entry),
            "affected_requirement_ids": affected_requirement_ids,
            "affected_guardrail_ids": affected_guardrail_ids,
            "reviewer_owner": sorted_unique(owner_values) or ["ppd-source-reviewer"],
            "offline_validation_commands": merge_commands(valid_candidate_commands + matrix_commands),
            "attestations": dict(REQUIRED_ATTESTATIONS),
        }
        rows.append(row)

    rows.sort(key=lambda row: (priority_rank(row["recrawl_priority"]), row["source_id"]))
    plan = {
        "plan_version": WATCH_PLAN_VERSION,
        "inputs": {
            "public_source_observation_refresh_candidate": observation_refresh_candidate_v2.get("fixture_version", "v2"),
            "inactive_source_fixture_migration_packet": inactive_source_fixture_migration_packet_v2.get("fixture_version", "v2"),
            "guardrail_regression_replay_matrix": guardrail_regression_replay_matrix_v3.get("fixture_version", "v3"),
        },
        "watch_rows": rows,
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    validate_watch_plan(plan)
    return plan


def priority_rank(priority: str) -> int:
    ranks = {"critical": 0, "high": 1, "medium": 2, "low": 3, "defer": 4}
    return ranks.get(priority, 5)


def validate_watch_plan(plan: Mapping[str, Any]) -> None:
    if plan.get("plan_version") != WATCH_PLAN_VERSION:
        raise ValueError("unexpected watch plan version")
    for key, expected_value in REQUIRED_ATTESTATIONS.items():
        if plan.get("attestations", {}).get(key) is not expected_value:
            raise ValueError(f"missing plan attestation: {key}")
    rows = plan.get("watch_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("watch plan must contain at least one row")
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("watch plan rows must be objects")
        for field in (
            "watch_row_id",
            "source_id",
            "canonical_url",
            "recrawl_priority",
            "metadata_only_watch_expectations",
            "skip_defer_reason",
            "affected_requirement_ids",
            "affected_guardrail_ids",
            "reviewer_owner",
            "offline_validation_commands",
            "attestations",
        ):
            if field not in row:
                raise ValueError(f"watch row missing field: {field}")
        for key, expected_value in REQUIRED_ATTESTATIONS.items():
            if row.get("attestations", {}).get(key) is not expected_value:
                raise ValueError(f"watch row {row.get('source_id')} missing attestation: {key}")
        if not isinstance(row.get("metadata_only_watch_expectations"), list) or not row.get("metadata_only_watch_expectations"):
            raise ValueError(f"watch row {row.get('source_id')} must define metadata expectations")
        if not isinstance(row.get("reviewer_owner"), list) or not row.get("reviewer_owner"):
            raise ValueError(f"watch row {row.get('source_id')} must define reviewer owner")


def build_watch_plan_from_paths(candidate_path: Path, inactive_path: Path, matrix_path: Path) -> Dict[str, Any]:
    return build_watch_plan(load_json(candidate_path), load_json(inactive_path), load_json(matrix_path))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build a fixture-first PP&D public source freshness watch plan v3.")
    parser.add_argument("candidate_fixture", type=Path)
    parser.add_argument("inactive_fixture", type=Path)
    parser.add_argument("matrix_fixture", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    plan = build_watch_plan_from_paths(args.candidate_fixture, args.inactive_fixture, args.matrix_fixture)
    rendered = json.dumps(plan, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
