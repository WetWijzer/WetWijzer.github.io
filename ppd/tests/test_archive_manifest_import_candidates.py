from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.archive_manifest_import_candidates import build_packet, load_packet_fixture

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "archive_manifest_import_candidates"
    / "processor_metadata_rows_v1.json"
)


def _fixture_rows() -> list[dict[str, object]]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    rows = payload["processor_metadata_rows"]
    assert isinstance(rows, list)
    return rows


def test_fixture_maps_metadata_only_archive_and_normalized_candidates() -> None:
    packet = load_packet_fixture(FIXTURE_PATH)

    assert packet["packet_version"] == "archive-manifest-import-candidate-packet-v1"
    assert packet["mode"] == "fixture-first-offline-validation-only"
    assert packet["mutation_policy"] == "metadata-only-candidate-rows-no-active-state-mutation"
    assert packet["validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/archive_manifest_import_candidates.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_archive_manifest_import_candidates.py"],
    ]

    archive_rows = packet["archive_manifest_candidates"]
    normalized_rows = packet["normalized_document_candidates"]
    assert len(archive_rows) == 2
    assert len(normalized_rows) == 2

    first_archive = archive_rows[0]
    assert first_archive == {
        "candidate_id": "archive-candidate-001",
        "source_url": "https://example.invalid/portland/devhub/documents/alpha",
        "final_url": "https://example.invalid/portland/archive/documents/alpha.pdf",
        "redirect_chain": [
            {
                "from_url": "https://example.invalid/portland/devhub/documents/alpha",
                "to_url": "https://example.invalid/portland/archive/documents/alpha",
                "status": 301,
            },
            {
                "from_url": "https://example.invalid/portland/archive/documents/alpha",
                "to_url": "https://example.invalid/portland/archive/documents/alpha.pdf",
                "status": 302,
            },
        ],
        "http_status": 200,
        "content_type": "application/pdf",
        "content_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        "processor_name": "synthetic-ppd-fixture-processor",
        "processor_version": "1.0.0-fixture",
        "skipped_reasons": [],
        "no_raw_body": True,
        "reviewer_hold": False,
    }

    second_archive = archive_rows[1]
    assert second_archive["http_status"] == 403
    assert second_archive["skipped_reasons"] == ["access-requires-review-before-fetch"]
    assert second_archive["reviewer_hold"] is True
    assert second_archive["no_raw_body"] is True

    first_normalized = normalized_rows[0]
    assert first_normalized["candidate_id"] == "normalized-document-candidate-001"
    assert first_normalized["archive_manifest_candidate_id"] == "archive-candidate-001"
    assert first_normalized["document_title"] == "Synthetic Alpha Permit Document"
    assert first_normalized["processor_name"] == "synthetic-ppd-fixture-processor"
    assert first_normalized["processor_version"] == "1.0.0-fixture"
    assert first_normalized["no_raw_body"] is True


def test_rejects_raw_body_fields() -> None:
    rows = _fixture_rows()
    row_with_body = dict(rows[0])
    row_with_body["raw_body"] = "not allowed"

    with pytest.raises(ValueError, match="contains raw body fields: raw_body"):
        build_packet([row_with_body])


def test_requires_no_raw_body_true() -> None:
    rows = _fixture_rows()
    row_with_raw_body_allowed = dict(rows[0])
    row_with_raw_body_allowed["no_raw_body"] = False

    with pytest.raises(ValueError, match="must set no_raw_body to true"):
        build_packet([row_with_raw_body_allowed])


def test_rejects_missing_required_metadata() -> None:
    rows = _fixture_rows()
    row_without_hash = dict(rows[0])
    del row_without_hash["content_hash"]

    with pytest.raises(ValueError, match="missing required fields: content_hash"):
        build_packet([row_without_hash])
