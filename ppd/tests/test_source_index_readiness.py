from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ppd.source_index_readiness import (
    SourceIndexReadinessError,
    require_source_index_ready,
    validate_source_index_readiness,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_index_readiness"
NOW = datetime(2026, 5, 15, tzinfo=timezone.utc)


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_ready_source_index_passes() -> None:
    index = _fixture("ready_source_index.json")

    result = validate_source_index_readiness(index, now=NOW)

    assert result.ready is True
    assert result.failures == ()
    require_source_index_ready(index, now=NOW)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda index: index.pop("freshness"), "missing freshness status"),
        (lambda index: index["freshness"].update({"status": "stale"}), "stale freshness status"),
        (lambda index: index["freshness"].update({"checked_at": "2026-03-01T00:00:00Z"}), "stale freshness timestamp"),
        (lambda index: index.pop("owning_surface"), "missing owning surface"),
        (lambda index: index["sources"][0].pop("citation_spans"), "missing citation spans for source 0"),
        (lambda index: index["sources"][0]["citation_spans"][0].update({"end": 0}), "invalid citation span for source 0 span 0"),
        (lambda index: index.pop("processor"), "missing processor metadata"),
        (lambda index: index["processor"].update({"version": ""}), "missing processor metadata"),
        (lambda index: index["processor"].update({"processed_at": "2026-03-01T00:00:00Z"}), "stale processor metadata"),
    ],
)
def test_unready_source_index_blocks_requirement_extraction(mutation, expected: str) -> None:
    index = copy.deepcopy(_fixture("ready_source_index.json"))
    mutation(index)

    result = validate_source_index_readiness(index, now=NOW)

    assert result.ready is False
    assert expected in result.failures
    with pytest.raises(SourceIndexReadinessError) as exc_info:
        require_source_index_ready(index, now=NOW)
    assert expected in exc_info.value.failures


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda index: index.pop("official_source_anchors"), "missing official source anchor coverage"),
        (lambda index: index["official_source_anchors"].pop(), "missing canonical URLs"),
        (lambda index: index["official_source_anchors"][1].update({"canonical_url": index["official_source_anchors"][0]["canonical_url"]}), "duplicate canonical_url"),
        (lambda index: index["official_source_anchors"][0].update({"canonical_url": "https://example.com/ppd"}), "unsupported host"),
        (lambda index: index["official_source_anchors"][0].update({"freshness_status": "stale"}), "stale official source anchor freshness_status"),
        (lambda index: index["official_source_anchors"][0].pop("freshness_status"), "missing required fields"),
        (lambda index: index["official_source_anchors"][0].pop("owning_surface"), "missing required fields"),
        (lambda index: index["official_source_anchors"][0].update({"canonical_url": "https://www.portland.gov/account?session=abc"}), "private or authenticated canonical_url"),
    ],
)
def test_source_index_readiness_requires_safe_official_anchor_coverage(mutation, expected: str) -> None:
    index = copy.deepcopy(_fixture("ready_source_index.json"))
    mutation(index)

    result = validate_source_index_readiness(index, now=NOW)

    assert result.ready is False
    assert any(expected in failure for failure in result.failures)
    with pytest.raises(SourceIndexReadinessError) as exc_info:
        require_source_index_ready(index, now=NOW)
    assert any(expected in failure for failure in exc_info.value.failures)
