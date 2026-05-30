"""Fixture-first public freshness scheduler rehearsal v4.

This module turns public freshness watch plans, registry promotion previews,
and registry fixtures into metadata-only recrawl schedule candidates. It is
intentionally offline-only: callers provide already-committed JSON fixtures and
receive deterministic rehearsal output with attestations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

JsonMap = Dict[str, Any]

ATTESTATIONS = {
    "fixture_first": True,
    "metadata_only": True,
    "no_live_crawl": True,
    "no_download": True,
    "no_processor": True,
    "no_raw_body": True,
    "no_active_source_registry_mutation": True,
}


def load_json(path: Path) -> JsonMap:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def _source_id(item: Mapping[str, Any]) -> str:
    for key in ("source_id", "id", "slug", "name"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown-source"


def _records(document: Mapping[str, Any], keys: Iterable[str]) -> List[Mapping[str, Any]]:
    for key in keys:
        value = document.get(key)
        rows = _as_list(value)
        if rows:
            return [row for row in rows if isinstance(row, dict)]
    return []


def _index_by_source(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    indexed: Dict[str, Mapping[str, Any]] = {}
    for row in rows:
        indexed[_source_id(row)] = row
    return indexed


def _citations(*items: Optional[Mapping[str, Any]]) -> List[JsonMap]:
    citations: List[JsonMap] = []
    seen = set()
    for item in items:
        if not item:
            continue
        raw = item.get("citations") or item.get("metadata_citations") or item.get("evidence") or []
        for citation in _as_list(raw):
            if isinstance(citation, str):
                normalized = {"label": citation, "fixture_only": True}
            elif isinstance(citation, dict):
                normalized = dict(citation)
                normalized["fixture_only"] = True
            else:
                continue
            marker = json.dumps(normalized, sort_keys=True)
            if marker not in seen:
                seen.add(marker)
                citations.append(normalized)
    return citations


def _reviewer_owner(source_id: str, watch: Mapping[str, Any], preview: Optional[Mapping[str, Any]]) -> JsonMap:
    owner = watch.get("reviewer_owner") or watch.get("owner")
    if not owner and preview:
        owner = preview.get("reviewer_owner") or preview.get("owner")
    if isinstance(owner, dict):
        result = dict(owner)
    else:
        result = {"team": str(owner) if owner else "ppd-public-source-review"}
    result.setdefault("source_id", source_id)
    result.setdefault("review_required", True)
    return result


def _rollback(source_id: str, preview: Optional[Mapping[str, Any]]) -> JsonMap:
    checkpoint = None
    if preview:
        checkpoint = preview.get("rollback_checkpoint") or preview.get("registry_snapshot")
    if isinstance(checkpoint, dict):
        result = dict(checkpoint)
    else:
        result = {"checkpoint_id": checkpoint or f"fixture-registry-before-{source_id}"}
    result.setdefault("source_id", source_id)
    result.setdefault("mutation_allowed", False)
    return result


def build_rehearsal(watch_plan: Mapping[str, Any], promotion_preview: Mapping[str, Any], registry: Mapping[str, Any]) -> JsonMap:
    watch_rows = _records(watch_plan, ("watch_plan", "sources", "items", "entries"))
    preview_rows = _records(promotion_preview, ("promotion_preview", "sources", "items", "entries"))
    registry_rows = _records(registry, ("sources", "registry", "items", "entries"))

    previews = _index_by_source(preview_rows)
    registered = _index_by_source(registry_rows)

    candidates: List[JsonMap] = []
    skip_defer: List[JsonMap] = []
    dependency_order: List[JsonMap] = []
    reviewer_owner_fields: List[JsonMap] = []
    rollback_checkpoints: List[JsonMap] = []

    ordered_watch_rows = sorted(watch_rows, key=lambda row: (int(row.get("priority", 100)), _source_id(row)))
    for position, watch in enumerate(ordered_watch_rows, start=1):
        source_id = _source_id(watch)
        preview = previews.get(source_id)
        registry_row = registered.get(source_id)
        cadence = str(watch.get("freshness_cadence") or watch.get("cadence") or "manual-review")
        action = str(watch.get("action") or "candidate")
        reason = watch.get("skip_reason") or watch.get("defer_reason")

        dependency_order.append({
            "order": position,
            "source_id": source_id,
            "requires": list(watch.get("requires", [])) if isinstance(watch.get("requires"), list) else [],
        })
        reviewer_owner_fields.append(_reviewer_owner(source_id, watch, preview))
        rollback_checkpoints.append(_rollback(source_id, preview))

        if reason or action in {"skip", "defer"} or preview is None or registry_row is None:
            skip_defer.append({
                "source_id": source_id,
                "status": "deferred" if action == "defer" else "skipped",
                "reason": reason or ("missing promotion preview" if preview is None else "missing source registry fixture"),
                "citations": _citations(watch, preview, registry_row),
            })
            continue

        candidates.append({
            "source_id": source_id,
            "schedule_status": "candidate",
            "cadence": cadence,
            "metadata_fields": {
                "public_url": registry_row.get("public_url") or registry_row.get("url"),
                "last_seen_metadata_at": watch.get("last_seen_metadata_at"),
                "freshness_signal": watch.get("freshness_signal") or watch.get("signal"),
                "promotion_action": preview.get("promotion_action") or preview.get("action") or "preview-only",
            },
            "citations": _citations(watch, preview, registry_row),
            "attestations": dict(ATTESTATIONS),
        })

    return {
        "schema": "ppd.public_freshness_scheduler_rehearsal.v4",
        "inputs": {
            "watch_plan_schema": watch_plan.get("schema"),
            "promotion_preview_schema": promotion_preview.get("schema"),
            "registry_schema": registry.get("schema"),
        },
        "cited_metadata_only_recrawl_schedule_candidates": candidates,
        "skip_defer_reasons": skip_defer,
        "dependency_order": dependency_order,
        "reviewer_owner_fields": reviewer_owner_fields,
        "rollback_checkpoints": rollback_checkpoints,
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/public_freshness_scheduler_rehearsal_v4.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_public_freshness_scheduler_rehearsal_v4.py"],
        ],
        "attestations": dict(ATTESTATIONS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fixture-first public freshness scheduler rehearsal v4")
    parser.add_argument("--watch-plan", required=True, type=Path)
    parser.add_argument("--promotion-preview", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = build_rehearsal(
        load_json(args.watch_plan),
        load_json(args.promotion_preview),
        load_json(args.registry),
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
