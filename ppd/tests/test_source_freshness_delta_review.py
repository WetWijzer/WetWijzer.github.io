from __future__ import annotations

import pytest

from ppd.source_freshness_delta_review import (
    assert_source_freshness_delta_review_packet,
    validate_source_freshness_delta_review_packet,
)


def _valid_packet() -> dict:
    return {
        "packet_id": "freshness-review-fixture",
        "affected_source_ids": ["ppd-zoning-code"],
        "recommended_offline_follow_up_queues": ["ppd-human-review"],
        "reviewer_owners": ["ppd-reviewer"],
        "decisions": [
            {
                "decision": "changed",
                "affected_source_ids": ["ppd-zoning-code"],
                "citations": ["https://www.portland.gov/code/33"],
            },
            {
                "decision": "unchanged",
                "affected_source_ids": ["ppd-devhub-fees"],
                "citations": ["https://www.portland.gov/bds/permit-review-process"],
            },
            {
                "decision": "stale",
                "affected_source_ids": ["ppd-inspections"],
                "citations": ["https://www.portlandmaps.com/advanced/?action=permits"],
            },
        ],
        "notes": "Reviewer compared cited public pages using offline evidence only.",
    }


def _codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_source_freshness_delta_review_packet(packet)}


def test_valid_packet_passes() -> None:
    assert validate_source_freshness_delta_review_packet(_valid_packet()) == []
    assert_source_freshness_delta_review_packet(_valid_packet())


@pytest.mark.parametrize("decision", ["changed", "unchanged", "stale"])
def test_rejects_uncited_changed_unchanged_and_stale_decisions(decision: str) -> None:
    packet = _valid_packet()
    packet["decisions"] = [{"decision": decision, "affected_source_ids": ["ppd-zoning-code"]}]

    assert "decision_uncited" in _codes(packet)


def test_rejects_missing_affected_source_ids_follow_up_queue_and_owner() -> None:
    packet = _valid_packet()
    packet.pop("affected_source_ids")
    packet.pop("recommended_offline_follow_up_queues")
    packet.pop("reviewer_owners")
    packet["decisions"] = [{"decision": "changed", "citations": ["https://www.portland.gov/code/33"]}]

    codes = _codes(packet)

    assert "affected_source_ids_missing" in codes
    assert "offline_follow_up_queue_missing" in codes
    assert "reviewer_owner_missing" in codes
    assert "decision_affected_source_ids_missing" in codes


@pytest.mark.parametrize(
    "url, expected_code",
    [
        ("https://example.com/ppd", "url_not_allowlisted"),
        ("https://user:pass@www.portland.gov/code/33", "authenticated_url"),
        ("https://www.portland.gov/login", "authenticated_url"),
        ("https://www.portland.gov/code/33?token=secret", "authenticated_url"),
    ],
)
def test_rejects_non_allowlisted_or_authenticated_urls(url: str, expected_code: str) -> None:
    packet = _valid_packet()
    packet["decisions"][0]["citations"] = [url]

    assert expected_code in _codes(packet)


@pytest.mark.parametrize(
    "field, value, expected_code",
    [
        ("raw_body", "downloaded page", "raw_reference"),
        ("notes", "The packet includes an archive URL for comparison.", "raw_reference"),
        ("notes", "Reviewer ran crawler against DevHub this morning.", "live_execution_claim"),
        ("notes", "This guarantees approval for the permit.", "outcome_guarantee"),
    ],
)
def test_rejects_raw_references_execution_claims_and_outcome_guarantees(
    field: str, value: str, expected_code: str
) -> None:
    packet = _valid_packet()
    packet[field] = value

    assert expected_code in _codes(packet)


@pytest.mark.parametrize(
    "flag",
    [
        "active_source_mutation",
        "active_schedule_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
    ],
)
def test_rejects_active_mutation_flags(flag: str) -> None:
    packet = _valid_packet()
    packet[flag] = True

    assert "active_mutation_flag" in _codes(packet)


def test_assert_raises_with_issue_details() -> None:
    packet = _valid_packet()
    packet["decisions"] = [{"decision": "changed"}]

    with pytest.raises(ValueError, match="decision_uncited"):
        assert_source_freshness_delta_review_packet(packet)
