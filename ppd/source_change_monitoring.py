"""Fixture-first source change monitoring for PP&D extraction review.

The module intentionally avoids live crawling. It compares reviewed source records
with extracted candidate fixtures and emits a deterministic human-review report.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

FEE_LANGUAGE_RE = re.compile(r"\b(fee|fees|surcharge|valuation|payment|cost)\b", re.IGNORECASE)
DEADLINE_LANGUAGE_RE = re.compile(
    r"\b(deadline|expires?|expiration|within\s+\d+\s+days?|before\s+\w+\s+\d{1,2})\b",
    re.IGNORECASE,
)


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_source_change_report(
    reviewed_sources: list[dict[str, Any]],
    extraction_candidates: list[dict[str, Any]],
    *,
    as_of: str,
) -> dict[str, Any]:
    """Build a deterministic source monitoring report from local fixtures."""

    as_of_date = _parse_date(as_of)
    candidates_by_source: dict[str, list[dict[str, Any]]] = {}
    for candidate in extraction_candidates:
        candidates_by_source.setdefault(str(candidate["source_id"]), []).append(candidate)

    source_reports = []
    affected_requirement_ids: set[str] = set()
    affected_guardrail_bundle_ids: set[str] = set()

    for source in sorted(reviewed_sources, key=lambda item: str(item["source_id"])):
        source_id = str(source["source_id"])
        source_candidates = sorted(
            candidates_by_source.get(source_id, []),
            key=lambda item: str(item.get("candidate_id", "")),
        )
        reviewed_hash = str(source.get("reviewed_hash", ""))
        current_hash = str(source.get("current_hash", reviewed_hash))
        hash_changed = reviewed_hash != current_hash
        cadence_days = int(source.get("recrawl_days", 0))
        days_since_review = (as_of_date - _parse_date(str(source["last_reviewed_at"]))).days
        recrawl_overdue = cadence_days > 0 and days_since_review > cadence_days

        changed_file_rules = sorted(
            {
                str(rule)
                for candidate in source_candidates
                for rule in candidate.get("changed_file_rules", [])
            }
        )
        fee_language_candidates = _candidate_ids_matching(source_candidates, FEE_LANGUAGE_RE)
        deadline_language_candidates = _candidate_ids_matching(source_candidates, DEADLINE_LANGUAGE_RE)

        candidate_hashes = sorted({str(candidate.get("candidate_hash", "")) for candidate in source_candidates})
        candidate_hash_changed = any(candidate_hash and candidate_hash != reviewed_hash for candidate_hash in candidate_hashes)
        needs_review = any(
            [
                hash_changed,
                candidate_hash_changed,
                recrawl_overdue,
                bool(changed_file_rules),
                bool(fee_language_candidates),
                bool(deadline_language_candidates),
            ]
        )

        requirement_ids = sorted(
            {
                str(requirement_id)
                for candidate in source_candidates
                for requirement_id in candidate.get("requirement_node_ids", [])
            }
        )
        guardrail_ids = sorted(
            {
                str(bundle_id)
                for candidate in source_candidates
                for bundle_id in candidate.get("guardrail_bundle_ids", [])
            }
        )

        if needs_review:
            affected_requirement_ids.update(requirement_ids)
            affected_guardrail_bundle_ids.update(guardrail_ids)

        source_reports.append(
            {
                "source_id": source_id,
                "url": source.get("url", ""),
                "reviewed_hash": reviewed_hash,
                "current_hash": current_hash,
                "candidate_hashes": candidate_hashes,
                "hash_changed": hash_changed or candidate_hash_changed,
                "recrawl": {
                    "last_reviewed_at": source["last_reviewed_at"],
                    "recrawl_days": cadence_days,
                    "days_since_review": days_since_review,
                    "overdue": recrawl_overdue,
                },
                "changed_file_rules": changed_file_rules,
                "changed_fee_language_candidates": fee_language_candidates,
                "changed_deadline_language_candidates": deadline_language_candidates,
                "affected_requirement_node_ids": requirement_ids if needs_review else [],
                "affected_guardrail_bundle_ids": guardrail_ids if needs_review else [],
                "human_review_prompts": _human_review_prompts(
                    source_id=source_id,
                    hash_changed=hash_changed or candidate_hash_changed,
                    recrawl_overdue=recrawl_overdue,
                    changed_file_rules=changed_file_rules,
                    fee_language_candidates=fee_language_candidates,
                    deadline_language_candidates=deadline_language_candidates,
                    requirement_ids=requirement_ids,
                    guardrail_ids=guardrail_ids,
                ),
            }
        )

    return {
        "as_of": as_of,
        "report_kind": "ppd_source_change_monitoring",
        "summary": {
            "sources_checked": len(reviewed_sources),
            "sources_requiring_review": sum(1 for item in source_reports if item["human_review_prompts"]),
            "affected_requirement_node_ids": sorted(affected_requirement_ids),
            "affected_guardrail_bundle_ids": sorted(affected_guardrail_bundle_ids),
        },
        "sources": source_reports,
    }


def build_report_from_files(reviewed_path: str | Path, candidates_path: str | Path, *, as_of: str) -> dict[str, Any]:
    return build_source_change_report(load_json(reviewed_path), load_json(candidates_path), as_of=as_of)


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _candidate_ids_matching(candidates: list[dict[str, Any]], pattern: re.Pattern[str]) -> list[str]:
    return sorted(
        str(candidate.get("candidate_id", ""))
        for candidate in candidates
        if pattern.search(str(candidate.get("text", "")))
    )


def _human_review_prompts(
    *,
    source_id: str,
    hash_changed: bool,
    recrawl_overdue: bool,
    changed_file_rules: list[str],
    fee_language_candidates: list[str],
    deadline_language_candidates: list[str],
    requirement_ids: list[str],
    guardrail_ids: list[str],
) -> list[str]:
    prompts: list[str] = []
    if hash_changed:
        prompts.append(f"Review {source_id}: source hash differs from the reviewed baseline.")
    if recrawl_overdue:
        prompts.append(f"Review {source_id}: source is past its recrawl cadence.")
    if changed_file_rules:
        prompts.append(f"Review {source_id}: changed file rules detected: {', '.join(changed_file_rules)}.")
    if fee_language_candidates:
        prompts.append(f"Review {source_id}: fee language changed in candidates: {', '.join(fee_language_candidates)}.")
    if deadline_language_candidates:
        prompts.append(f"Review {source_id}: deadline language changed in candidates: {', '.join(deadline_language_candidates)}.")
    if prompts:
        prompts.append(
            "Confirm affected RequirementNode IDs "
            f"{', '.join(requirement_ids) or 'none'} and GuardrailBundle IDs "
            f"{', '.join(guardrail_ids) or 'none'} before promotion."
        )
    return prompts
