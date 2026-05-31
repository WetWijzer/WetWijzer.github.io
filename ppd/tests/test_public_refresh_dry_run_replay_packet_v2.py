from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.public_refresh_dry_run_replay_packet_v2 import (
    REQUIRED_ROW_KINDS,
    assert_valid_public_refresh_dry_run_replay_packet_v2,
    validate_public_refresh_dry_run_replay_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_refresh_dry_run_replay_packet_v2"


def load_valid_packet() -> dict:
    with (FIXTURE_DIR / "valid_packet.json").open(encoding="utf-8") as packet_file:
        return json.load(packet_file)


def error_codes(packet: dict) -> set[str]:
    return {error.code for error in validate_public_refresh_dry_run_replay_packet_v2(packet)}


def test_valid_packet_fixture_passes() -> None:
    assert_valid_public_refresh_dry_run_replay_packet_v2(load_valid_packet())


@pytest.mark.parametrize("missing_kind", REQUIRED_ROW_KINDS)
def test_rejects_each_missing_required_evidence_row(missing_kind: str) -> None:
    packet = load_valid_packet()
    packet["evidence_rows"] = [row for row in packet["evidence_rows"] if row["kind"] != missing_kind]

    assert f"missing_{missing_kind}_row" in error_codes(packet)


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("session_file", "state/session-state.json"),
        ("browser_trace", "artifacts/browser-trace.zip"),
        ("raw_body_artifact", "artifacts/raw-body.html"),
        ("downloaded_document", "artifacts/downloaded-document.pdf"),
        ("private_artifact", "/tmp/private/devhub.json"),
    ],
)
def test_rejects_private_session_browser_raw_and_downloaded_artifacts(field_name: str, field_value: str) -> None:
    packet = load_valid_packet()
    packet[field_name] = field_value

    assert "private_artifact_reference" in error_codes(packet)


def test_rejects_live_crawl_claims() -> None:
    packet = load_valid_packet()
    packet["live_crawl_claim"] = True

    assert "live_crawl_claim" in error_codes(packet)


def test_rejects_textual_live_crawl_claims() -> None:
    packet = load_valid_packet()
    packet["notes"] = "The live crawl completed successfully during refresh."

    assert "live_crawl_claim" in error_codes(packet)


@pytest.mark.parametrize(
    "claim",
    [
        "Permit approval guaranteed by this packet.",
        "This is a legal guarantee for the permitting outcome.",
    ],
)
def test_rejects_legal_or_permitting_guarantees(claim: str) -> None:
    packet = load_valid_packet()
    packet["summary_claim"] = claim

    assert "legal_or_permitting_guarantee" in error_codes(packet)


@pytest.mark.parametrize(
    "flag_name",
    [
        "crawler_mutation",
        "source_mutation",
        "archive_mutation",
        "document_mutation",
        "requirement_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "contract_mutation",
        "devhub_surface_mutation",
        "release_state_mutation",
    ],
)
def test_rejects_active_mutation_flags(flag_name: str) -> None:
    packet = load_valid_packet()
    packet = copy.deepcopy(packet)
    packet["mutation_flags"][flag_name] = True

    assert "active_mutation_flag" in error_codes(packet)


def test_rejects_missing_validation_commands_even_when_validation_row_exists() -> None:
    packet = load_valid_packet()
    packet.pop("validation_commands")

    assert "missing_validation_commands" in error_codes(packet)


def test_rejects_non_dry_run_mode() -> None:
    packet = load_valid_packet()
    packet["mode"] = "live"

    assert "not_dry_run" in error_codes(packet)
