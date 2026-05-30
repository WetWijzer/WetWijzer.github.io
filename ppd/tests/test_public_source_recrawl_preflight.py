from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "public_source_recrawl_preflight.py"
SPEC = importlib.util.spec_from_file_location("public_source_recrawl_preflight", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_source_recrawl_queue_v1.json"


def test_builds_ordered_fixture_first_preflight_rows() -> None:
    packet = preflight.build_preflight_packet(FIXTURE_PATH)

    assert packet["packet_version"] == "public_source_recrawl_preflight_packet_v1"
    assert packet["source_queue_version"] == "public_source_freshness_recrawl_queue_v1"
    assert packet["offline_only"] is True
    assert packet["live_crawl_performed"] is False
    assert packet["devhub_accessed"] is False
    assert packet["documents_downloaded"] is False
    assert packet["raw_response_bodies_stored"] is False

    rows = packet["ordered_candidate_preflight_rows"]
    assert [row["source_id"] for row in rows] == [
        "portland-permits-home-page",
        "portland-permits-zoning-code",
    ]
    assert rows[0]["row_id"] == "preflight-001"
    assert rows[0]["official_anchor_citations"][0]["citation_id"] == "A1.1"
    assert rows[0]["robots_policy_decision"]["status"] == "review_required_before_live_crawl"
    assert rows[0]["reviewer_approval"]["approved"] is False


def test_excludes_raw_bodies_and_download_artifacts() -> None:
    packet = preflight.build_preflight_packet(FIXTURE_PATH)

    assert packet["packet_level_exclusion_check"] == {
        "forbidden_fixture_keys_present": [],
        "status": "passed",
    }
    for row in packet["ordered_candidate_preflight_rows"]:
        exclusion = row["raw_body_download_exclusion_check"]
        assert exclusion["raw_response_body_stored"] is False
        assert exclusion["downloaded_document_stored"] is False
        assert exclusion["forbidden_fixture_keys_present"] == []
        assert exclusion["status"] == "passed"


def test_packet_includes_exact_offline_validation_commands() -> None:
    packet = preflight.build_preflight_packet(FIXTURE_PATH)

    assert packet["exact_offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/public_source_recrawl_preflight.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_public_source_recrawl_preflight.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
