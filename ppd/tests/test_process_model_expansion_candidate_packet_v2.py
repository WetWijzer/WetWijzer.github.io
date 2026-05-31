from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "process_model_expansion_candidate_packet_v2.py"
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "process_model_expansion_candidate_packet_v2" / "candidate_packet.json"

spec = importlib.util.spec_from_file_location("process_model_expansion_candidate_packet_v2", MODULE_PATH)
assert spec is not None
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


def _packet() -> dict:
    return validator.load_packet(FIXTURE_PATH)


def _fails(packet: dict) -> str:
    with pytest.raises(ValueError) as excinfo:
        validator.validate_packet(packet)
    return str(excinfo.value)


def test_candidate_packet_fixture_is_valid() -> None:
    validator.validate_packet(_packet())


def test_candidate_packet_covers_required_workflows_only_as_inactive_synthetic_rows() -> None:
    packet = _packet()
    rows = packet["delta_rows"]
    workflows = {row["workflow"] for row in rows}

    assert workflows == {
        "building",
        "trade",
        "solar",
        "demolition",
        "sign",
        "urban_forestry",
        "corrections",
    }
    assert all(row["status"] == "inactive_candidate" for row in rows)
    assert all(row["synthetic"] is True for row in rows)
    assert packet["live_source_crawl_permitted"] is False
    assert packet["devhub_access_permitted"] is False
    assert packet["mutates_active_models"] is False


def test_candidate_packet_embeds_exact_offline_validation_commands() -> None:
    packet = _packet()
    commands = packet["exact_offline_validation_commands"]

    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in commands
    assert ["python3", "ppd/process_model_expansion_candidate_packet_v2.py", "ppd/tests/fixtures/process_model_expansion_candidate_packet_v2/candidate_packet.json"] in commands
    assert all(isinstance(command, list) for command in commands)


def test_rejects_missing_permit_family_rows() -> None:
    packet = _packet()
    packet["delta_rows"] = [row for row in packet["delta_rows"] if row["workflow"] != "building"]

    assert "missing permit-family rows" in _fails(packet)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("required_facts", "missing required-fact rows"),
        ("required_documents", "missing document rows"),
        ("fee_triggers", "missing fee rows"),
        ("deadlines", "missing deadline rows"),
        ("unsupported_paths", "missing unsupported-path rows"),
        ("source_evidence_placeholders", "missing source-evidence placeholders"),
    ],
)
def test_rejects_missing_required_row_lists(field: str, expected: str) -> None:
    packet = _packet()
    packet["delta_rows"][0][field] = []

    assert expected in _fails(packet)


def test_rejects_missing_reviewer_disposition_placeholder() -> None:
    packet = _packet()
    packet["delta_rows"][0].pop("reviewer_disposition_placeholder")

    assert "reviewer_disposition_placeholder" in _fails(packet)


def test_rejects_incomplete_reviewer_disposition_placeholder() -> None:
    packet = _packet()
    packet["delta_rows"][0]["reviewer_disposition_placeholder"] = {"status": "unreviewed"}

    assert "missing reviewer disposition placeholder fields" in _fails(packet)


def test_rejects_missing_validation_commands() -> None:
    packet = _packet()
    packet.pop("exact_offline_validation_commands")

    assert "exact_offline_validation_commands must be non-empty" in _fails(packet)


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("browser_state_path", "state.json", "must not include private"),
        ("raw_crawl_output", "raw html", "must not include private"),
        ("downloaded_document_path", "permit.pdf", "must not include private"),
        ("session_trace", "trace.zip", "must not include private"),
        ("live_claim", "live crawl completed", "must not claim live crawl"),
        ("devhub_claim", "DevHub access completed", "must not claim live crawl"),
        ("guarantee", "permit will be approved", "must not guarantee"),
        ("legal_claim", "legal advice", "must not guarantee"),
    ],
)
def test_rejects_private_artifacts_live_claims_and_guarantees(key: str, value: str, expected: str) -> None:
    packet = _packet()
    packet[key] = value

    assert expected in _fails(packet)


@pytest.mark.parametrize(
    "flag",
    [
        "active_process_model_mutation",
        "active_requirement_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_contract_mutation",
        "active_source_mutation",
        "active_devhub_surface_mutation",
        "active_release_state_mutation",
    ],
)
def test_rejects_active_mutation_flags(flag: str) -> None:
    packet = _packet()
    packet[flag] = True

    assert f"packet.{flag} must be false" in _fails(packet)


def test_rejects_nested_active_mutation_flags() -> None:
    packet = _packet()
    packet["delta_rows"][0]["active_process_model_mutation"] = True

    assert "active_process_model_mutation must be false" in _fails(packet)


if __name__ == "__main__":
    test_candidate_packet_fixture_is_valid()
    test_candidate_packet_covers_required_workflows_only_as_inactive_synthetic_rows()
    test_candidate_packet_embeds_exact_offline_validation_commands()
    print("process-model expansion candidate packet v2 tests passed")
