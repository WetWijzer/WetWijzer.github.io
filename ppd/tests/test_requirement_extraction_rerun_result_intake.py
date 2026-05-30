import json
from pathlib import Path

import pytest

from ppd.requirement_extraction_rerun_result_intake import build_result_intake_packet


FIXTURES = Path(__file__).parent / "fixtures" / "requirement_extraction_rerun_result_intake"


def _load(name: str):
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_builds_expected_fixture_first_result_intake_packet():
    packet = build_result_intake_packet(
        _load("work_order_packet.json"),
        _load("synthetic_rerun_output.json"),
    )

    assert packet == _load("expected_result_intake_packet.json")
    assert {item["decision"] for item in packet["result_decisions"]} == {
        "accepted",
        "deferred",
        "rejected",
    }
    assert packet["attestations"] == {
        "no_live_extraction": True,
        "no_processor_execution": True,
        "no_active_artifact_mutation": True,
    }


def test_rejects_unknown_decision_before_intake():
    work_order = _load("work_order_packet.json")
    rerun_output = _load("synthetic_rerun_output.json")
    rerun_output["results"][0]["decision"] = "maybe"

    with pytest.raises(ValueError, match="unsupported decision"):
        build_result_intake_packet(work_order, rerun_output)
