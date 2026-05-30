from __future__ import annotations

import json
from pathlib import Path

from ppd.public_source_refresh_reviewer_queue_v1 import (
    assert_valid_public_source_refresh_reviewer_queue_v1,
    validate_public_source_refresh_reviewer_queue_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_reviewer_queue_v1"


def _load_fixture(name: str) -> object:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _codes(payload: object) -> set[str]:
    return {issue.code for issue in validate_public_source_refresh_reviewer_queue_v1(payload)}


def test_valid_queue_item_is_accepted() -> None:
    payload = _load_fixture("valid_queue.json")

    assert validate_public_source_refresh_reviewer_queue_v1(payload) == []
    assert_valid_public_source_refresh_reviewer_queue_v1(payload)


def test_rejects_uncited_queue_items() -> None:
    payload = _load_fixture("valid_queue.json")
    payload["items"][0].pop("citations")

    assert "missing_citation" in _codes(payload)


def test_rejects_non_allowlisted_and_authenticated_urls() -> None:
    payload = _load_fixture("valid_queue.json")
    payload["items"][0]["source_url"] = "https://example.com/ppd"
    payload["items"][0]["citations"][0]["url"] = "https://devhub.portlandoregon.gov/account/my-permits?token=secret"

    codes = _codes(payload)

    assert "url_not_allowlisted" in codes
    assert "authenticated_url" in codes


def test_rejects_raw_page_bodies_and_downloaded_documents() -> None:
    payload = _load_fixture("valid_queue.json")
    payload["items"][0]["raw_html"] = "raw public page body"
    payload["items"][0]["downloaded_documents"] = [{"pdf_path": "/tmp/fee-guide.pdf"}]

    codes = _codes(payload)

    assert "raw_page_body_present" in codes
    assert "downloaded_document_present" in codes


def test_rejects_processor_and_archive_completion_claims() -> None:
    payload = _load_fixture("valid_queue.json")
    payload["items"][0]["processor_completed"] = True
    payload["items"][0]["archive_complete"] = "yes"
    payload["items"][0]["status"] = "completed"

    assert "processor_or_archive_completion_claim" in _codes(payload)


def test_rejects_missing_affected_ids() -> None:
    payload = _load_fixture("valid_queue.json")
    payload["items"][0]["affected_ids"] = []

    assert "missing_affected_ids" in _codes(payload)


def test_rejects_missing_defer_or_rollback_rationale() -> None:
    payload = _load_fixture("valid_queue.json")
    payload["items"][0].pop("defer_rationale")
    payload["items"][0].pop("rollback_rationale", None)

    assert "missing_defer_or_rollback_rationale" in _codes(payload)


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    payload = _load_fixture("valid_queue.json")
    payload["items"][0]["review_note"] = "This permit will be approved after the refresh."

    assert "outcome_guarantee" in _codes(payload)


def test_rejects_active_mutation_flags() -> None:
    payload = _load_fixture("valid_queue.json")
    item = payload["items"][0]
    item["mutate_sources"] = True
    item["update_requirements"] = "yes"
    item["apply_process_changes"] = True
    item["commit_guardrails"] = True
    item["monitoring_mutation_enabled"] = True
    item["release_state_mutation"] = True
    item["agent_state_mutation"] = True

    assert "active_mutation_flag" in _codes(payload)
