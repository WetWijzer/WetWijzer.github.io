from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.validation.public_source_change_reviewer_disposition_queue_v1 import (
    assert_valid_queue,
    validate_queue,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_queue_fixture_is_accepted() -> None:
    queue = _load_fixture("public_source_change_reviewer_disposition_queue_v1_valid.json")

    assert validate_queue(queue) == []
    assert_valid_queue(queue)


@pytest.mark.parametrize(
    ("mutation_key"),
    [
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_release_state_mutation",
        "active_prompt_mutation",
        "active_fixture_mutation",
        "active_agent_state_mutation",
    ],
)
def test_active_mutation_flags_are_rejected(mutation_key: str) -> None:
    queue = _load_fixture("public_source_change_reviewer_disposition_queue_v1_valid.json")
    queue["mutation_flags"][mutation_key] = True

    errors = validate_queue(queue)

    assert any("active mutation flags" in error for error in errors)


def test_invalid_fixture_rejects_required_failure_categories() -> None:
    queue = _load_fixture("public_source_change_reviewer_disposition_queue_v1_invalid.json")

    errors = validate_queue(queue)
    joined = "\n".join(errors)

    assert "buckets.unchanged" in joined
    assert "buckets.needs_review" in joined
    assert "must include citation" in joined
    assert "blocked_promotion_reason" in joined
    assert "rollback_checkpoints" in joined
    assert "validation_commands" in joined
    assert "private, authenticated, session, or browser artifacts" in joined
    assert "raw crawl, PDF, or downloaded data" in joined
    assert "live crawl or refresh completion" in joined
    assert "legal or permitting outcome guarantees" in joined
    assert "consequential action language" in joined
    assert "active mutation flags" in joined


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("reviewer_decision_rows", [], "reviewer_decision_rows"),
        ("buckets", {"changed": [], "unchanged": [], "needs_review": []}, "reviewer_decision_rows"),
    ],
)
def test_missing_reviewer_decision_rows_are_rejected(field: str, value: object, expected: str) -> None:
    queue = _load_fixture("public_source_change_reviewer_disposition_queue_v1_valid.json")
    queue[field] = value
    if field != "reviewer_decision_rows":
        queue["reviewer_decision_rows"] = []

    errors = validate_queue(queue)

    assert any(expected in error for error in errors)


def test_assert_valid_queue_raises_value_error_with_errors() -> None:
    queue = _load_fixture("public_source_change_reviewer_disposition_queue_v1_invalid.json")

    with pytest.raises(ValueError, match="public source change reviewer disposition queue rejected"):
        assert_valid_queue(queue)
