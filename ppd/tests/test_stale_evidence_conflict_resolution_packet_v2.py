from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.validation.stale_evidence_conflict_resolution_packet_v2 import (
    assert_valid_packet,
    validate_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "stale_evidence_conflict_resolution_packet_v2"


def _load_valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


def _codes(packet: dict) -> set[str]:
    return {finding.code for finding in validate_packet(packet)}


def test_valid_packet_is_accepted() -> None:
    assert_valid_packet(_load_valid_packet())


@pytest.mark.parametrize(
    ("field_name", "expected_code"),
    [
        ("stale_source_cases", "missing_stale_source_cases"),
        ("changed_hash_cases", "missing_changed_hash_cases"),
        ("conflicting_requirement_cases", "missing_conflicting_requirement_cases"),
        ("missing_document_cases", "missing_missing_document_cases"),
        ("unsupported_path_cases", "missing_unsupported_path_cases"),
        ("user_gap_questions", "missing_user_gap_questions"),
        ("holds_and_refusals", "missing_holds_refusals"),
        ("next_safe_action_summaries", "missing_next_safe_action_summaries"),
        ("reviewer_dispositions", "missing_reviewer_dispositions"),
    ],
)
def test_rejects_missing_required_case_lists(field_name: str, expected_code: str) -> None:
    packet = _load_valid_packet()
    packet[field_name] = []

    assert expected_code in _codes(packet)


def test_rejects_missing_validation_commands() -> None:
    packet = _load_valid_packet()
    packet.pop("validation_commands")

    assert "missing_validation_commands" in _codes(packet)


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ({"artifacts": {"storage_state": "private-state.json"}}, "private_session_or_browser_artifact"),
        ({"notes": "browser automation ran against DevHub after signed in to DevHub"}, "live_crawl_or_devhub_claim"),
        ({"notes": "submitted the application and payment completed"}, "official_action_completion_claim"),
        ({"notes": "permit will be approved and compliance guaranteed"}, "legal_or_permitting_guarantee"),
        ({"active_registry_mutation": True}, "active_mutation_flag"),
        ({"evidence": {"raw_body": "raw"}}, "raw_or_downloaded_artifact"),
        ({"downloaded_document": "/tmp/private.pdf"}, "raw_or_downloaded_artifact"),
        ({"citation_url": "https://devhub.portlandoregon.gov/account?session_id=secret"}, "private_session_or_browser_artifact"),
        ({"citation_url": "https://example.com/not-ppd"}, "unsupported_path_or_host"),
    ],
)
def test_rejects_safety_boundary_violations(mutation: dict, expected_code: str) -> None:
    packet = _load_valid_packet()
    packet.update(mutation)

    assert expected_code in _codes(packet)


def test_assert_valid_packet_reports_codes() -> None:
    packet = _load_valid_packet()
    packet["reviewer_dispositions"] = [copy.deepcopy(packet["reviewer_dispositions"][0])]
    packet["reviewer_dispositions"][0].pop("evidence_refs")

    with pytest.raises(ValueError, match="uncited_reviewer_disposition"):
        assert_valid_packet(packet)
