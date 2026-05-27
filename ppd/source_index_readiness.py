"""Deterministic readiness validation for PP&D source indexes.

This module is intentionally crawl-free. It validates already-materialized source
index records before requirement extraction is allowed to run.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from ppd.source_anchor_matrix import SourceAnchorMatrixError, validate_anchor_matrix


class SourceIndexReadinessError(ValueError):
    """Raised when a source index is not ready for requirement extraction."""

    def __init__(self, failures: Sequence[str]) -> None:
        self.failures = tuple(failures)
        super().__init__("source index is not ready: " + "; ".join(self.failures))


@dataclass(frozen=True)
class SourceIndexReadinessResult:
    """Validation result for a PP&D source index."""

    ready: bool
    failures: tuple[str, ...]


def validate_source_index_readiness(
    source_index: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_age_days: int = 30,
) -> SourceIndexReadinessResult:
    """Return readiness failures for a materialized PP&D source index."""

    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    failures: list[str] = []

    freshness = _mapping(source_index.get("freshness"))
    if not freshness:
        failures.append("missing freshness status")
    else:
        status = freshness.get("status")
        if status != "fresh":
            failures.append("stale freshness status")
        checked_at = _parse_time(freshness.get("checked_at"))
        if checked_at is None:
            failures.append("missing freshness timestamp")
        elif _age_days(now, checked_at) > max_age_days:
            failures.append("stale freshness timestamp")

    owning_surface = source_index.get("owning_surface")
    if not isinstance(owning_surface, str) or not owning_surface.strip():
        failures.append("missing owning surface")

    _validate_official_source_anchors(source_index.get("official_source_anchors"), failures)

    processor = _mapping(source_index.get("processor"))
    if not processor:
        failures.append("missing processor metadata")
    else:
        for key in ("name", "version", "processed_at"):
            value = processor.get(key)
            if not isinstance(value, str) or not value.strip():
                failures.append("missing processor metadata")
                break
        processed_at = _parse_time(processor.get("processed_at"))
        if processed_at is None:
            failures.append("missing processor timestamp")
        elif _age_days(now, processed_at) > max_age_days:
            failures.append("stale processor metadata")

    sources = source_index.get("sources")
    if not isinstance(sources, list) or not sources:
        failures.append("missing citation spans")
    else:
        for index, source in enumerate(sources):
            source_map = _mapping(source)
            spans = source_map.get("citation_spans") if source_map else None
            if not isinstance(spans, list) or not spans:
                failures.append(f"missing citation spans for source {index}")
                continue
            for span_index, span in enumerate(spans):
                span_map = _mapping(span)
                if not span_map or not _valid_span(span_map):
                    failures.append(f"invalid citation span for source {index} span {span_index}")

    return SourceIndexReadinessResult(ready=not failures, failures=tuple(failures))


def require_source_index_ready(
    source_index: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_age_days: int = 30,
) -> None:
    """Fail closed when requirement extraction is attempted on an unready index."""

    result = validate_source_index_readiness(source_index, now=now, max_age_days=max_age_days)
    if not result.ready:
        raise SourceIndexReadinessError(result.failures)


def _validate_official_source_anchors(value: Any, failures: list[str]) -> None:
    if not isinstance(value, list) or not value:
        failures.append("missing official source anchor coverage")
        return
    try:
        validate_anchor_matrix(value, require_ready_freshness=True)
    except SourceAnchorMatrixError as exc:
        failures.append(str(exc))


def _mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    return None


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _age_days(now: datetime, then: datetime) -> int:
    return (now.astimezone(timezone.utc) - then.astimezone(timezone.utc)).days


def _valid_span(span: Mapping[str, Any]) -> bool:
    start = span.get("start")
    end = span.get("end")
    text = span.get("text")
    return (
        isinstance(start, int)
        and isinstance(end, int)
        and start >= 0
        and end > start
        and isinstance(text, str)
        and bool(text.strip())
    )
