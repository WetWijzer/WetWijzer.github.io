from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.public_refresh.source_freshness_evidence_packet_v4 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    assert_valid_source_freshness_evidence_packet_v4,
    build_source_freshness_evidence_packet_v4,
    build_source_freshness_evidence_packet_v4_from_file,
    validate_source_freshness_evidence_packet_v4,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_freshness_evidence_packet_v4"
VALID_INPUTS_PATH = FIXTURE_DIR / "valid_inputs.json"


def _packet() -> dict[str, object]:
    return build_source_freshness_evidence_packet_v4_from_file(VALID_INPUTS_PATH)


def _errors(packet: dict[str, object]) -> str:
    problems = validate_source_freshness_evidence_packet_v4(packet)
    assert problems
    return "\n".join(problems)


def test_builds_valid_fixture_first_source_freshness_evidence_packet_v4() -> None:
    packet = _packet()
    assert validate_source_freshness_evidence_packet_v4(packet) == []
    assert_valid_source_freshness_evidence_packet_v4(packet)
    rows = packet["freshness_evidence_rows"]
    assert isinstance(rows, list)
    statuses = {row["freshness_status"] for row in rows if isinstance(row, dict)}
    assert statuses == {"stale", "changed", "skipped", "unchanged"}
    assert packet["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS


def test_consumes_only_committed_registry_and_archive_manifest_placeholders() -> None:
    packet = _packet()
    assert packet["input_contract"] == "committed_source_registry_rows_and_archive_manifest_placeholders_only"
    assert packet["boundary_flags"] == {
        "live_sites_crawled": False,
        "documents_downloaded": False,
        "raw_bodies_stored": False,
        "devhub_opened": False,
        "authenticated_surfaces_opened": False,
        "source_registry_mutated": False,
        "archive_manifest_mutated": False,
        "official_actions_performed": False,
    }


def test_rejects_missing_archive_manifest_placeholder_for_registry_source() -> None:
    fixture = json.loads(VALID_INPUTS_PATH.read_text(encoding="utf-8"))
    fixture["committed_archive_manifest_placeholders"] = fixture["committed_archive_manifest_placeholders"][:-1]
    with pytest.raises(ValueError, match="missing archive manifest placeholder"):
        build_source_freshness_evidence_packet_v4(fixture)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("source_registry_row_refs", "source_registry_row_refs must be a non-empty list"),
        ("archive_manifest_placeholder_refs", "archive_manifest_placeholder_refs must be a non-empty list"),
        ("freshness_evidence_rows", "freshness_evidence_rows must be a non-empty list"),
        ("reviewer_holds", "reviewer_holds must be a non-empty list"),
        ("rollback_notes", "rollback_notes must be a non-empty list"),
    ],
)
def test_rejects_missing_required_packet_sections(field: str, expected: str) -> None:
    packet = _packet()
    packet[field] = []
    assert expected in _errors(packet)


def test_rejects_missing_source_registry_reference_for_evidence_row() -> None:
    packet = _packet()
    refs = packet["source_registry_row_refs"]
    assert isinstance(refs, list)
    packet["source_registry_row_refs"] = refs[1:]
    assert "source_registry_row_refs missing references: registry-row-ppd-apply-permits" in _errors(packet)


def test_rejects_missing_archive_manifest_reference_for_evidence_row() -> None:
    packet = _packet()
    refs = packet["archive_manifest_placeholder_refs"]
    assert isinstance(refs, list)
    packet["archive_manifest_placeholder_refs"] = refs[1:]
    assert "archive_manifest_placeholder_refs missing references: manifest-placeholder-ppd-apply-permits" in _errors(packet)


def test_rejects_missing_status_coverage() -> None:
    packet = _packet()
    rows = packet["freshness_evidence_rows"]
    assert isinstance(rows, list)
    packet["freshness_evidence_rows"] = [row for row in rows if isinstance(row, dict) and row.get("freshness_status") != "skipped"]
    assert "freshness_evidence_rows missing statuses: skipped" in _errors(packet)


def test_rejects_missing_freshness_status_reason() -> None:
    packet = _packet()
    rows = packet["freshness_evidence_rows"]
    assert isinstance(rows, list)
    broken = deepcopy(rows[0])
    assert isinstance(broken, dict)
    broken["freshness_status_reason"] = ""
    rows[0] = broken
    assert "freshness_evidence_rows[0].freshness_status_reason must be present" in _errors(packet)


def test_rejects_missing_citation_placeholders_and_requirement_ids() -> None:
    packet = _packet()
    rows = packet["freshness_evidence_rows"]
    assert isinstance(rows, list)
    broken = deepcopy(rows[0])
    assert isinstance(broken, dict)
    broken["citation_placeholders"] = []
    broken["affected_requirement_ids"] = []
    rows[0] = broken
    errors = _errors(packet)
    assert "freshness_evidence_rows[0].citation_placeholders must include citation-placeholder entries" in errors
    assert "freshness_evidence_rows[0].affected_requirement_ids must be a non-empty list" in errors


def test_rejects_missing_reviewer_hold_for_stale_changed_or_skipped_evidence() -> None:
    packet = _packet()
    holds = packet["reviewer_holds"]
    assert isinstance(holds, list)
    packet["reviewer_holds"] = holds[1:]
    assert "reviewer_holds missing required evidence references: freshness-evidence-v4-ppd-apply-permits" in _errors(packet)


def test_rejects_missing_rollback_note_for_any_evidence_row() -> None:
    packet = _packet()
    notes = packet["rollback_notes"]
    assert isinstance(notes, list)
    packet["rollback_notes"] = notes[1:]
    assert "rollback_notes missing required evidence references: freshness-evidence-v4-ppd-apply-permits" in _errors(packet)


def test_rejects_validation_command_drift() -> None:
    packet = _packet()
    packet["exact_offline_validation_commands"] = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    assert "exact_offline_validation_commands must match the allowed offline validation command list" in _errors(packet)


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        (("raw_body",), "private body", "private, raw, downloaded, browser, session, or DevHub artifacts"),
        (("session_state",), {"cookie": "redacted"}, "private, raw, downloaded, browser, session, or DevHub artifacts"),
        (("downloaded_document_claim",), "none", "private, raw, downloaded, browser, session, or DevHub artifacts"),
        (("freshness_evidence_rows", 0, "freshness_status_reason"), "raw crawl output observed", "forbidden claim: raw crawl output"),
        (("freshness_evidence_rows", 0, "freshness_status_reason"), "downloaded document reviewed", "forbidden claim: downloaded document"),
        (("freshness_evidence_rows", 0, "freshness_status_reason"), "live crawl completed", "forbidden claim: live crawl completed"),
        (("freshness_evidence_rows", 0, "freshness_status_reason"), "permit approval guaranteed", "forbidden claim: permit approval guaranteed"),
        (("freshness_evidence_rows", 0, "freshness_status_reason"), "DevHub opened for review", "forbidden claim: devhub opened"),
        (("active_source_registry_mutation",), True, "active mutation flags"),
        (("source_registry_mutated_by_packet",), True, "active mutation flags"),
    ],
)
def test_rejects_private_runtime_claims_guarantees_and_active_mutation_flags(
    path: tuple[object, ...], value: object, expected: str
) -> None:
    packet = _packet()
    target: object = packet
    for part in path[:-1]:
        if isinstance(part, int):
            assert isinstance(target, list)
            target = target[part]
        else:
            assert isinstance(target, dict)
            target = target.setdefault(part, {})
    last = path[-1]
    if isinstance(last, int):
        assert isinstance(target, list)
        target[last] = value
    else:
        assert isinstance(target, dict)
        target[last] = value
    assert expected in _errors(packet)


def test_assert_raises_for_invalid_packet() -> None:
    packet = _packet()
    packet["freshness_evidence_rows"] = []
    with pytest.raises(ValueError, match="invalid public source freshness evidence packet v4"):
        assert_valid_source_freshness_evidence_packet_v4(packet)
