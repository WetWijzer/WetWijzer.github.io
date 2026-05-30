import copy
import json
from pathlib import Path

import pytest

from ppd.readiness_gap_report import ATTESTATIONS, build_readiness_gap_report, load_packet_file

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "readiness_gap_report_v1"


def load_packets():
    return load_packet_file(FIXTURE_DIR / "input_packets.json")


def test_readiness_gap_report_matches_fixture() -> None:
    packets = load_packets()
    expected = json.loads((FIXTURE_DIR / "expected_report.json").read_text(encoding="utf-8"))

    assert build_readiness_gap_report(packets) == expected


def test_report_contains_only_remaining_gaps_with_dependency_order() -> None:
    report = build_readiness_gap_report(load_packets())

    assert report["dependency_order"] == [
        "gap-source-citation-coverage",
        "gap-reversible-draft-preview",
    ]
    assert [row["gap_id"] for row in report["remaining_gap_rows"]] == report["dependency_order"]
    assert "ready-offline-fixtures-present" not in report["dependency_order"]


def test_each_gap_row_has_citations_owner_commands_and_attestations() -> None:
    report = build_readiness_gap_report(load_packets())

    for row in report["remaining_gap_rows"]:
        assert row["reviewer_owner"]
        assert row["reviewer_role"]
        assert row["citations"]
        assert row["offline_validation_commands"]
        assert row["attestations"] == ATTESTATIONS


def test_missing_required_packet_is_rejected() -> None:
    packets = load_packets()
    packets.pop("action_journal_replay_validator_v1")

    with pytest.raises(ValueError, match="action_journal_replay_validator_v1"):
        build_readiness_gap_report(packets)


def test_dependency_cycle_is_rejected() -> None:
    packets = load_packets()
    items = packets["readiness_ledger_v1"]["readiness_items"]
    items[0]["dependencies"] = ["gap-reversible-draft-preview"]

    with pytest.raises(ValueError, match="cycle detected"):
        build_readiness_gap_report(packets)


def test_uncited_gap_is_rejected() -> None:
    packets = load_packets()
    item = packets["readiness_ledger_v1"]["readiness_items"][0]
    item["source_requirement_ids"] = []
    item["guardrail_ids"] = []
    item["draft_preview_ids"] = []
    item["journal_validator_ids"] = []
    item["devhub_runbook_step_ids"] = []

    with pytest.raises(ValueError, match="has no citations"):
        build_readiness_gap_report(packets)


def test_unknown_citation_reference_is_rejected() -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"]["readiness_items"][0]["source_requirement_ids"].append("REQ-MISSING")

    with pytest.raises(ValueError, match="unresolved citation ids"):
        build_readiness_gap_report(packets)


def test_unsupported_readiness_topic_is_rejected() -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"]["readiness_items"][0]["readiness_topic"] = "live_devhub_submission"

    with pytest.raises(ValueError, match="unsupported readiness topic"):
        build_readiness_gap_report(packets)


@pytest.mark.parametrize("field_name", ["reviewer_owner", "reviewer_role", "blocker"])
def test_missing_owner_or_manual_review_blocker_field_is_rejected(field_name: str) -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"]["readiness_items"][0][field_name] = ""

    with pytest.raises(ValueError, match="required non-empty string field missing"):
        build_readiness_gap_report(packets)


def test_missing_dependency_is_rejected() -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"]["readiness_items"][1]["dependencies"] = ["gap-does-not-exist"]

    with pytest.raises(ValueError, match="missing dependency"):
        build_readiness_gap_report(packets)


def test_declared_dependency_order_must_include_every_remaining_gap() -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"]["dependency_order"] = ["gap-source-citation-coverage"]

    with pytest.raises(ValueError, match="dependency_order must include every remaining gap"):
        build_readiness_gap_report(packets)


def test_declared_dependency_order_must_place_dependencies_first() -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"]["dependency_order"] = [
        "gap-reversible-draft-preview",
        "gap-source-citation-coverage",
    ]

    with pytest.raises(ValueError, match="places gap-reversible-draft-preview before"):
        build_readiness_gap_report(packets)


@pytest.mark.parametrize(
    ("field_name", "field_value", "message"),
    [
        ("auth_state", {"cookie": "redacted-but-still-private"}, "private or raw artifact field"),
        ("raw_crawl_output", "raw html body", "private or raw artifact field"),
        ("raw_pdf_path", "/tmp/public-form.pdf", "private or raw artifact field"),
        ("browser_state", {"storage": "state"}, "private or raw artifact field"),
    ],
)
def test_private_authenticated_raw_or_browser_artifact_fields_are_rejected(
    field_name: str, field_value: object, message: str
) -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"][field_name] = field_value

    with pytest.raises(ValueError, match=message):
        build_readiness_gap_report(packets)


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "The live crawl completed and refreshed the report.",
        "The report guarantees permit approval for this case.",
        "The agent may submit the application as the next step.",
        "next safe action: upload corrections to DevHub",
        "The worker logged in to DevHub and captured the case.",
    ],
)
def test_unsafe_live_guarantee_or_consequential_language_is_rejected(unsafe_text: str) -> None:
    packets = load_packets()
    packets["readiness_ledger_v1"]["readiness_items"][0]["blocker"] = unsafe_text

    with pytest.raises(ValueError):
        build_readiness_gap_report(packets)


@pytest.mark.parametrize(
    "flag_name",
    [
        "active_source_mutation",
        "source_registry_mutation",
        "surface_registry_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "release_state_mutation",
        "agent_state_mutation",
    ],
)
def test_active_mutation_flags_are_rejected(flag_name: str) -> None:
    packets = load_packets()
    mutated = copy.deepcopy(packets)
    mutated["readiness_ledger_v1"][flag_name] = True

    with pytest.raises(ValueError, match="active mutation flag"):
        build_readiness_gap_report(mutated)
