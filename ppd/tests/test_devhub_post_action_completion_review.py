from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.post_action_completion_review import validate_post_action_completion_review


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub"
    / "post_action_completion_hardening_reviews.json"
)


def _fixtures() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_post_action_completion_review_accepts_user_visible_source_backed_evidence() -> None:
    errors = validate_post_action_completion_review(_fixtures()["validReview"])

    assert errors == []


def test_post_action_completion_review_rejects_click_only_completion() -> None:
    errors = validate_post_action_completion_review(_fixtures()["invalidClickOnlyReview"])

    assert any("cannot be only a click or fill attempt" in error for error in errors)
    assert any("requires source-backed classification" in error for error in errors)
    assert any("requires userVisibleOutcomeEvidence" in error for error in errors)


def test_post_action_completion_review_rejects_private_or_unredacted_journal_metadata() -> None:
    errors = validate_post_action_completion_review(_fixtures()["invalidPrivateJournalReview"])

    assert any("must be redacted" in error for error in errors)
    assert any("metadata must mark redacted=true" in error for error in errors)
    assert any("forbidden private key" in error for error in errors)
    assert any("forbidden private value" in error for error in errors)
