from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.source_anchor_matrix import (
    ORIGINAL_PUBLIC_SOURCE_ANCHORS,
    REQUIRED_MATRIX_FIELDS,
    SourceAnchorMatrixError,
    load_anchor_matrix,
    validate_anchor_matrix,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "source_anchor_coverage_matrix.json"


def test_official_source_anchor_matrix_covers_original_public_anchors():
    rows = validate_anchor_matrix(load_anchor_matrix(FIXTURE_PATH))

    canonical_urls = {row["canonical_url"] for row in rows}
    assert canonical_urls == set(ORIGINAL_PUBLIC_SOURCE_ANCHORS)


def test_official_source_anchor_matrix_has_required_policy_columns():
    rows = validate_anchor_matrix(load_anchor_matrix(FIXTURE_PATH))

    for row in rows:
        for field in REQUIRED_MATRIX_FIELDS:
            assert row[field]
        assert row["synthetic_metadata"] is True
        assert row["live_crawl_performed"] is False


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda rows: rows.pop(), "missing canonical URLs"),
        (lambda rows: rows[1].update({"canonical_url": rows[0]["canonical_url"]}), "duplicate canonical_url"),
        (lambda rows: rows[0].update({"canonical_url": "https://example.com/ppd"}), "unsupported host"),
        (lambda rows: rows[0].update({"freshness_status": "stale"}), "unsupported freshness_status"),
        (lambda rows: rows[0].pop("freshness_status"), "missing required fields"),
        (lambda rows: rows[0].pop("owning_surface"), "missing required fields"),
        (lambda rows: rows[0].update({"canonical_url": "https://www.portland.gov/login?token=abc"}), "private or authenticated canonical_url"),
    ],
)
def test_official_source_anchor_matrix_rejects_unready_coverage(mutation, expected: str):
    rows = copy.deepcopy(load_anchor_matrix(FIXTURE_PATH))
    mutation(rows)

    with pytest.raises(SourceAnchorMatrixError) as exc_info:
        validate_anchor_matrix(rows)

    assert expected in str(exc_info.value)
