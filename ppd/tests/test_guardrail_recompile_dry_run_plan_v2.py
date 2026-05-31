from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.guardrail_recompile_dry_run_plan_v2 import (
    EXPECTED_PACKET_VERSION,
    OFFLINE_VALIDATION_COMMANDS,
    PLAN_VERSION,
    REQUIRED_ROW_KEYS,
    compile_guardrail_recompile_dry_run_plan_v2,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "guardrail_recompile_dry_run_plan_v2"
    / "requirement_reextraction_dry_run_packet_v2.json"
)

FORBIDDEN_MUTATION_TARGETS = (
    "src/lib/logic/",
    "public/corpus/portland-or/current/",
    "ipfs_datasets_py/.daemon/",
    "ppd/prompts/",
    "ppd/source_registries/active",
    "ppd/process_models/active",
    "ppd/surfaces/active",
    "ppd/release_state/",
)


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_packet_compiles_to_ordered_synthetic_delta_rows() -> None:
    plan = compile_guardrail_recompile_dry_run_plan_v2(_load_fixture())

    assert plan["plan_version"] == PLAN_VERSION
    assert plan["input_packet_version"] == EXPECTED_PACKET_VERSION
    assert plan["mode"] == "fixture_first_offline_dry_run"
    assert plan["active_bundle_mutation"] == "forbidden"

    rows = plan["ordered_synthetic_guardrail_bundle_delta_rows"]
    assert [row["row_order"] for row in rows] == [1, 2, 3]
    assert [row["requirement_id"] for row in rows] == sorted(
        row["requirement_id"] for row in rows
    )
    for row in rows:
        assert set(REQUIRED_ROW_KEYS).issubset(row)
        assert row["synthetic_guardrail_bundle_delta"]["status"] == "synthetic_inactive_delta_only"
        assert row["synthetic_guardrail_bundle_delta"]["writes_active_bundle"] == "false"
        assert row["deterministic_predicate_impact_placeholders"]
        assert row["deontic_rule_placeholders"]
        assert row["temporal_rule_placeholders"]
        assert row["reversible_action_predicate_placeholders"]
        assert row["exact_confirmation_predicate_placeholders"]
        assert row["refused_action_predicate_placeholders"]
        assert row["migration_risk_notes"]
        assert row["reviewer_disposition_placeholders"]["review_status"] == "pending"


def test_plan_exposes_exact_offline_validation_commands() -> None:
    plan = compile_guardrail_recompile_dry_run_plan_v2(_load_fixture())

    assert plan["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in plan[
        "offline_validation_commands"
    ]
    for command in plan["offline_validation_commands"]:
        assert command[0] == "python3"
        command_text = " ".join(command)
        assert not any(target in command_text for target in FORBIDDEN_MUTATION_TARGETS)


def test_rejects_non_v2_requirement_reextraction_packets() -> None:
    packet = _load_fixture()
    packet["packet_version"] = "requirement-reextraction-dry-run-packet-v1"

    with pytest.raises(ValueError, match="packet_version"):
        compile_guardrail_recompile_dry_run_plan_v2(packet)
