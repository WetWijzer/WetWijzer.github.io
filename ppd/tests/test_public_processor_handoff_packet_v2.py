import json
from pathlib import Path
from urllib.parse import urlparse


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "processor_handoff"
    / "public_processor_handoff_packet_v2.json"
)


ALLOWED_HOSTS = {
    "www.portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
}


def load_packet():
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_public_processor_handoff_packet_v2_is_fixture_only():
    packet = load_packet()

    assert packet["packet_version"] == "2.0"
    assert packet["fixture_only"] is True
    assert packet["live_network_access"] is False
    assert packet["processor_invocation"] is False
    assert packet["downloads_performed"] is False
    assert packet["active_crawler_behavior_changed"] is False


def test_preflight_rows_use_allowed_public_hosts_and_no_raw_body_persistence():
    packet = load_packet()
    assert set(packet["allowed_hosts"]) == ALLOWED_HOSTS

    for row in packet["preflight_rows"]:
        parsed = urlparse(row["requested_url"])
        assert parsed.scheme == "https"
        assert parsed.netloc in ALLOWED_HOSTS
        assert row["allowlist_policy"] in {
            "host_allowed_public_ppd",
            "host_allowed_reference_only",
        }
        assert row["skip_processor_invocation_in_fixture"] is True
        assert row["no_raw_body_persisted"] is True
        assert row["raw_body_persistence_allowed"] is False


def test_manifest_placeholders_match_preflight_rows_without_committed_artifacts():
    packet = load_packet()
    manifests = {
        manifest["manifest_id"]: manifest
        for manifest in packet["archive_manifest_placeholders"]
    }

    for row in packet["preflight_rows"]:
        manifest = manifests[row["archive_manifest_id"]]
        assert manifest["requested_url"] == row["requested_url"]
        assert manifest["canonical_url"] == row["canonical_url"]
        assert manifest["normalized_document_id"] == row["normalized_document_id"]
        assert manifest["skipped_reason"] == row["skipped_reason"]
        assert manifest["no_raw_body_persisted"] is True
        assert manifest["http_status"] == "fixture_not_fetched"
        assert manifest["capture_started_at"] == "fixture_not_captured"
        assert manifest["capture_finished_at"] == "fixture_not_captured"
        assert manifest["archive_artifact_ref"] in {
            None,
            "not_committed_fixture_placeholder",
        }


def test_normalized_document_placeholders_are_referenced_by_allowed_rows():
    packet = load_packet()
    documents = {
        document["document_id"]: document
        for document in packet["normalized_document_placeholders"]
    }

    for row in packet["preflight_rows"]:
        document_id = row["normalized_document_id"]
        if document_id is None:
            continue
        document = documents[document_id]
        assert document["source_id"]
        assert document["sections"] == []
        assert document["tables"] == []
        assert document["links"] == []
        assert document["pdf_pages"] == []
        assert document["form_fields"] == []
        assert document["citation_spans"] == []
        assert document["extraction_confidence"] == "fixture_placeholder_not_extracted"


def test_skipped_reason_rows_are_explicit_and_consistent():
    packet = load_packet()
    rows_by_id = {row["row_id"]: row for row in packet["preflight_rows"]}

    skipped_rows = packet["skipped_reason_rows"]
    assert skipped_rows

    for skipped in skipped_rows:
        preflight = rows_by_id[skipped["row_id"]]
        assert preflight["requested_url"] == skipped["requested_url"]
        assert preflight["skipped_reason"] == skipped["skipped_reason"]
        assert skipped["operator_action"]


def test_offline_validation_commands_are_exact_and_non_networked():
    packet = load_packet()

    assert packet["offline_validation_commands"] == [
        [
            "python3",
            "-m",
            "py_compile",
            "ppd/tests/test_public_processor_handoff_packet_v2.py",
        ],
        [
            "python3",
            "-m",
            "pytest",
            "ppd/tests/test_public_processor_handoff_packet_v2.py",
        ],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]

    forbidden_tokens = {
        "curl",
        "wget",
        "playwright",
        "browser",
        "crawl",
        "download",
        "requests",
    }
    flattened = {
        token.lower()
        for command in packet["offline_validation_commands"]
        for token in command
    }
    assert forbidden_tokens.isdisjoint(flattened)
