from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.archive_manifest_candidate_v1 import validate_candidate_packet_v1


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "archive_manifest_candidate_v1"


def _valid_packet() -> dict:
    with (FIXTURE_DIR / "minimal_valid_packet.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_candidate_packet_v1(packet)}


def test_minimal_fixture_is_valid() -> None:
    assert validate_candidate_packet_v1(_valid_packet()) == []


def test_rejects_missing_redirect_chain() -> None:
    packet = _valid_packet()
    del packet["manifest_candidates"][0]["redirect_chain"]
    assert "missing_redirect_chain" in _codes(packet)


def test_rejects_missing_http_status() -> None:
    packet = _valid_packet()
    del packet["manifest_candidates"][0]["http_status"]
    assert "missing_http_status" in _codes(packet)


def test_rejects_missing_content_type() -> None:
    packet = _valid_packet()
    del packet["manifest_candidates"][0]["content_type"]
    assert "missing_content_type" in _codes(packet)


def test_rejects_missing_content_hash() -> None:
    packet = _valid_packet()
    packet["manifest_candidates"][0]["content_hash"] = {"algorithm": "sha256"}
    assert "missing_content_hash" in _codes(packet)


def test_rejects_missing_processor_identity_rows() -> None:
    packet = _valid_packet()
    del packet["processor_identity_rows"]
    assert "missing_processor_identity_rows" in _codes(packet)


def test_rejects_missing_skipped_reason_for_skipped_candidate() -> None:
    packet = _valid_packet()
    packet["manifest_candidates"][0]["skipped"] = True
    packet["manifest_candidates"][0]["skipped_reason"] = ""
    assert "missing_skipped_reason" in _codes(packet)


def test_rejects_missing_no_raw_body_flag() -> None:
    packet = _valid_packet()
    packet["manifest_candidates"][0]["no_raw_body_persisted"] = False
    assert "missing_no_raw_body_flag" in _codes(packet)


def test_rejects_missing_reviewer_holds_array() -> None:
    packet = _valid_packet()
    del packet["reviewer_holds"]
    assert "missing_reviewer_holds" in _codes(packet)


def test_rejects_missing_validation_commands() -> None:
    packet = _valid_packet()
    packet["validation_commands"] = []
    assert "missing_validation_commands" in _codes(packet)


def test_rejects_raw_or_downloaded_artifacts() -> None:
    packet = _valid_packet()
    packet["manifest_candidates"][0]["download_path"] = "/tmp/public-page.html"
    assert "raw_or_downloaded_artifact" in _codes(packet)


def test_rejects_private_session_or_browser_artifacts() -> None:
    packet = _valid_packet()
    packet["browser"] = {"storage_state": "private-auth-state.json"}
    assert "private_session_or_browser_artifact" in _codes(packet)


def test_rejects_live_crawl_or_devhub_claims() -> None:
    packet = _valid_packet()
    packet["claims"].append("This packet was produced from a live crawl of authenticated DevHub.")
    assert "live_crawl_or_devhub_claim" in _codes(packet)


def test_rejects_legal_or_permitting_guarantees() -> None:
    packet = _valid_packet()
    packet["claims"].append("This provides legal advice and guarantees approval.")
    assert "legal_or_permitting_guarantee" in _codes(packet)


def test_rejects_active_mutation_flags() -> None:
    packet = _valid_packet()
    packet["capabilities"] = {"can_submit": True}
    assert "active_mutation_flag" in _codes(packet)


def test_detects_multiple_independent_failures() -> None:
    packet = copy.deepcopy(_valid_packet())
    del packet["processor_identity_rows"]
    packet["manifest_candidates"][0]["archive_artifact_ref"] = "raw-html-body"
    packet["manifest_candidates"][0]["mutation_enabled"] = True

    codes = _codes(packet)

    assert "missing_processor_identity_rows" in codes
    assert "raw_or_downloaded_artifact_ref" in codes
    assert "raw_or_downloaded_artifact" in codes
    assert "active_mutation_flag" in codes
