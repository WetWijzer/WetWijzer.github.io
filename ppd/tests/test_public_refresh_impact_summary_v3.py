from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.public_refresh_impact_summary_v3 import (
    MUTATION_BOUNDARIES,
    OFFLINE_VALIDATION_COMMANDS,
    ROW_TYPES,
    build_packet_from_fixture,
    load_replay_outcomes,
    require_valid_public_refresh_impact_summary_v3,
    validate_public_refresh_impact_summary_v3,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_refresh_impact_summary_v3" / "replay_outcomes.json"


def test_fixture_loads_synthetic_replay_outcomes() -> None:
    outcomes = load_replay_outcomes(FIXTURE_PATH)

    assert len(outcomes) == 10
    assert {outcome.row_type for outcome in outcomes} == set(ROW_TYPES)
    assert all(outcome.affected_ids for outcome in outcomes)


def test_packet_has_one_ordered_row_for_each_required_summary_type() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    assert packet["packet_version"] == "public-refresh-impact-summary-v3"
    assert packet["offline_only"] is True
    assert [row["row_type"] for row in packet["rows"]] == list(ROW_TYPES)
    assert packet["totals"] == {
        "row_count": 10,
        "synthetic_outcome_count": 10,
        "affected_id_count": 17,
        "rows_with_holds": 6,
    }
    require_valid_public_refresh_impact_summary_v3(packet)


def test_packet_records_exact_offline_validation_commands_on_packet_and_rows() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)
    expected_commands = [list(command) for command in OFFLINE_VALIDATION_COMMANDS]

    assert packet["validation_commands"] == expected_commands
    assert expected_commands == [
        ["python3", "-m", "py_compile", "ppd/public_refresh_impact_summary_v3.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_public_refresh_impact_summary_v3.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
    assert all(row["validation_commands"] == expected_commands for row in packet["rows"])


def test_packet_declares_no_live_access_or_mutation_boundaries() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    assert packet["mutation_boundaries"] == MUTATION_BOUNDARIES
    assert set(packet["mutation_boundaries"].values()) == {"forbidden"}
    assert packet["mutation_boundaries"]["network_access"] == "forbidden"
    assert packet["mutation_boundaries"]["raw_downloads"] == "forbidden"
    assert packet["mutation_boundaries"]["processor_execution"] == "forbidden"
    assert packet["mutation_boundaries"]["devhub_access"] == "forbidden"
    assert packet["mutation_boundaries"]["release_state_mutation"] == "forbidden"


def test_packet_is_deterministic_json_serializable() -> None:
    first = build_packet_from_fixture(FIXTURE_PATH)
    second = build_packet_from_fixture(FIXTURE_PATH)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_category_rows_include_expected_affected_ids() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)
    rows = {row["row_type"]: row for row in packet["rows"]}

    assert rows["source"]["affected_ids"] == ["src-ppd-apply-permits", "src-ppd-devhub-faq"]
    assert rows["guardrail"]["affected_count"] == 3
    assert rows["agent_readiness"]["outcome_counts"] == {"blocked": 1}
    assert rows["retry_backoff"]["outcome_counts"] == {"retry_scheduled": 1}
    assert rows["release_hold"]["outcome_counts"] == {"held": 1}


def test_validation_rejects_missing_required_rows() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    for row_type in ROW_TYPES:
        candidate = copy.deepcopy(packet)
        candidate["rows"] = [row for row in candidate["rows"] if row["row_type"] != row_type]

        errors = validate_public_refresh_impact_summary_v3(candidate)

        assert f"missing required {row_type} row" in errors


def test_validation_rejects_missing_affected_ids_for_each_required_row() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    for row_type in ROW_TYPES:
        candidate = copy.deepcopy(packet)
        row = next(item for item in candidate["rows"] if item["row_type"] == row_type)
        row["affected_ids"] = []
        row["affected_count"] = 0

        errors = validate_public_refresh_impact_summary_v3(candidate)

        assert any(f"{row_type}" in str(row) for row in candidate["rows"])
        assert any("affected_ids must include at least one value" in error for error in errors)


def test_validation_rejects_missing_validation_commands_on_packet_or_rows() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)
    missing_packet_commands = copy.deepcopy(packet)
    missing_packet_commands["validation_commands"] = []

    missing_row_commands = copy.deepcopy(packet)
    missing_row_commands["rows"][0]["validation_commands"] = []

    assert "validation_commands must include exact offline validation commands" in validate_public_refresh_impact_summary_v3(missing_packet_commands)
    assert any("rows[0].validation_commands must include exact offline validation commands" == error for error in validate_public_refresh_impact_summary_v3(missing_row_commands))


def test_validation_rejects_private_session_browser_raw_and_downloaded_artifacts() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    cases = [
        ("private_file_path", "/private/devhub/user-case.json"),
        ("session_state", {"path": "state.json"}),
        ("browser_trace", "trace.zip"),
        ("raw_crawl_output", "raw/body.html"),
        ("downloaded_document", "downloads/source.pdf"),
    ]
    for key, value in cases:
        candidate = copy.deepcopy(packet)
        candidate["rows"][0][key] = value

        errors = validate_public_refresh_impact_summary_v3(candidate)

        assert any("private/session/browser/raw/downloaded artifact" in error for error in errors)


def test_validation_rejects_live_crawl_claims_guarantees_and_active_mutation_flags() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)

    live_claim = copy.deepcopy(packet)
    live_claim["rows"][0]["notes"].append("The live crawl completed and the processor executed.")

    guarantee = copy.deepcopy(packet)
    guarantee["rows"][0]["notes"].append("This guarantees permit approval and legal compliance.")

    mutation = copy.deepcopy(packet)
    mutation["rows"][0]["active_source_mutation"] = True

    assert any("live crawl or live automation claim" in error for error in validate_public_refresh_impact_summary_v3(live_claim))
    assert any("legal or permitting guarantee" in error for error in validate_public_refresh_impact_summary_v3(guarantee))
    assert any("active mutation flag" in error for error in validate_public_refresh_impact_summary_v3(mutation))


def test_require_valid_raises_for_invalid_packet() -> None:
    packet = build_packet_from_fixture(FIXTURE_PATH)
    packet["rows"] = []

    with pytest.raises(ValueError, match="invalid public refresh impact summary v3"):
        require_valid_public_refresh_impact_summary_v3(packet)
