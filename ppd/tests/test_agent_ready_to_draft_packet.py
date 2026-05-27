from pathlib import Path

import pytest

from ppd.agent_ready_to_draft_packet import ReadyToDraftPacketError, load_packet, validate_packet

FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "agent_ready_to_draft"
    / "synthetic_devhub_trade_permit_packet.json"
)


def test_ready_to_draft_fixture_loads_and_is_metadata_only() -> None:
    packet = load_packet(FIXTURE)

    assert packet["metadata_only"] is True
    assert packet["synthetic_workflow"] is True
    assert packet["process_model_version_readiness"]["status"] == "ready_for_fixture_draft"
    assert packet["reversible_draft_planning"]["status"] == "draft_plan_ready_without_submission"


def test_ready_to_draft_fixture_has_ranked_missing_information() -> None:
    packet = load_packet(FIXTURE)
    priorities = packet["missing_information_prioritization"]["priorities"]

    assert [item["rank"] for item in priorities] == [1, 2, 3]
    assert priorities[0]["blocking_level"] == "blocks_field_mapping"


def test_validator_rejects_raw_or_private_fields() -> None:
    packet = load_packet(FIXTURE)
    packet["devhub_surface_map_readiness"]["raw_crawl_output"] = "not allowed"

    with pytest.raises(ReadyToDraftPacketError, match="forbidden raw/private field"):
        validate_packet(packet)


def test_validator_requires_known_metadata_citations() -> None:
    packet = load_packet(FIXTURE)
    packet["action_journal_expectations"]["citation_ids"] = ["missing-citation"]

    with pytest.raises(ReadyToDraftPacketError, match="unknown citations"):
        validate_packet(packet)


def test_validator_requires_reversible_non_submission_draft_steps() -> None:
    packet = load_packet(FIXTURE)
    packet["reversible_draft_planning"]["draft_steps"][0]["requires_submission"] = True

    with pytest.raises(ReadyToDraftPacketError, match="must not require submission"):
        validate_packet(packet)
