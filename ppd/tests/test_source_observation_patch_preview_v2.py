from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.source_observation_patch_preview_v2 import (
    PreviewValidationError,
    preview_v2_errors,
    validate_source_observation_patch_preview_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "source_observation_patch_preview_v2_invalid.json"


def _fixtures() -> dict[str, dict]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_preview_v2_accepts_valid_minimal_preview() -> None:
    result = validate_source_observation_patch_preview_v2(_fixtures()["valid_minimal"])

    assert result.ok is True
    assert result.errors == ()


def test_preview_v2_rejects_missing_required_row_and_preview_metadata() -> None:
    with pytest.raises(PreviewValidationError) as excinfo:
        validate_source_observation_patch_preview_v2(_fixtures()["missing_required"])

    errors = excinfo.value.errors
    assert any("citations are required" in error for error in errors)
    assert any("before_metadata is required" in error for error in errors)
    assert any("after_metadata is required" in error for error in errors)
    assert any("affected_source_ids are required" in error for error in errors)
    assert any("rollback_checkpoint is required" in error for error in errors)
    assert any(error == "affected source ids are required" for error in errors)
    assert any(error == "rollback checkpoints are required" for error in errors)


def test_preview_v2_rejects_blocked_content_and_mutation_flags() -> None:
    errors = preview_v2_errors(_fixtures()["blocked_content"])

    assert any("non-allowlisted URLs are not allowed" in error for error in errors)
    assert any("raw/download/archive/browser artifacts are not allowed" in error for error in errors)
    assert any("live crawler or processor completion claims" in error for error in errors)
    assert any("legal or permitting outcome guarantees" in error for error in errors)
    assert any("active mutation flags are not allowed" in error for error in errors)


def test_preview_v2_rejects_authenticated_allowlisted_urls() -> None:
    payload = _fixtures()["valid_minimal"]
    payload["preview_rows"][0]["citations"][0]["url"] = "https://user:pass@www.portland.gov/bds"

    errors = preview_v2_errors(payload)

    assert any("authenticated URLs are not allowed" in error for error in errors)
