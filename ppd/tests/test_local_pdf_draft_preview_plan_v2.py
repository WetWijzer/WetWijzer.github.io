from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


FIXTURE_DIR = Path(__file__).parent / "fixtures"
PACKET_PATH = FIXTURE_DIR / "local_pdf_draft_preview_plan_v2" / "fixture_first_packet.json"
PRIVATE_PATH_PATTERNS = (
    re.compile(r"/home/[^\s]+"),
    re.compile(r"/Users/[^\s]+"),
    re.compile(r"[A-Za-z]:\\\\[^\s]+"),
    re.compile(r"file://"),
)
REQUIRED_ATTESTATIONS = {
    "no_private_document",
    "no_pdf_read",
    "no_pdf_write",
    "no_upload",
    "no_devhub",
    "no_guardrail_mutation",
}
REQUIRED_CONSUMED_FIXTURES = {
    "ppd/tests/fixtures/draft_preview_readiness_v2/source_packets.json",
    "ppd/tests/fixtures/file_preparation_guardrails/synthetic_metadata_findings.json",
    "ppd/tests/fixtures/pdf_draft_preview/synthetic_permit_draft_form.json",
}


def load_packet() -> dict[str, Any]:
    with PACKET_PATH.open(encoding="utf-8") as packet_file:
        return json.load(packet_file)


def walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


def test_plan_v2_consumes_required_fixture_packets() -> None:
    packet = load_packet()

    assert packet["packet_type"] == "local_pdf_draft_preview_plan_v2"
    assert packet["fixture_first"] is True
    assert packet["preview_only"] is True

    consumed_paths = {item["path"] for item in packet["consumed_fixture_packets"]}
    assert REQUIRED_CONSUMED_FIXTURES.issubset(consumed_paths)

    for item in packet["consumed_fixture_packets"]:
        assert (Path(__file__).parents[1] / item["path"]).exists()
        assert item["consumed_sections"]
        assert item["use_in_plan"]


def test_field_mapping_decisions_are_cited_and_withheld_fields_have_reasons() -> None:
    packet = load_packet()
    evidence_ids = {item["evidence_id"] for item in packet["source_evidence"]}
    owner_fields = {item["field"] for item in packet["reviewer_owner_fields"]}

    assert packet["field_mapping_decisions"]
    assert any(item["decision"].startswith("withhold") for item in packet["field_mapping_decisions"])

    for decision in packet["field_mapping_decisions"]:
        assert decision["pdf_field_name"]
        assert set(decision["source_evidence_ids"]).issubset(evidence_ids)
        assert decision["reviewer_owner_field"] in owner_fields
        if decision["decision"].startswith("withhold"):
            assert decision["withheld_reason"]


def test_missing_fact_and_document_blockers_are_cited_and_owned() -> None:
    packet = load_packet()
    evidence_ids = {item["evidence_id"] for item in packet["source_evidence"]}
    owner_fields = {item["field"] for item in packet["reviewer_owner_fields"]}

    assert packet["missing_fact_blockers"]
    assert packet["missing_document_blockers"]

    for blocker in packet["missing_fact_blockers"]:
        assert blocker["blocker_id"]
        assert blocker["reason"]
        assert blocker["blocks_field_names"]
        assert set(blocker["source_evidence_ids"]).issubset(evidence_ids)
        assert blocker["reviewer_owner_field"] in owner_fields

    for blocker in packet["missing_document_blockers"]:
        assert blocker["blocker_id"]
        assert blocker["document_label"]
        assert blocker["source_fixture_finding_ids"]
        assert blocker["blocks_actions"]
        assert set(blocker["source_evidence_ids"]).issubset(evidence_ids)
        assert blocker["reviewer_owner_field"] in owner_fields


def test_preview_artifact_expectations_and_attestations_block_side_effects() -> None:
    packet = load_packet()
    expectations = packet["preview_only_artifact_expectations"]
    attestations = packet["attestations"]
    generated_from = packet["generated_from"]

    assert expectations["expected_artifact_kind"] == "metadata_only_local_pdf_draft_preview_plan_v2"
    assert expectations["may_read_synthetic_field_fixture_json"] is True
    assert expectations["may_read_pdf_binary"] is False
    assert expectations["may_write_pdf_binary"] is False
    assert expectations["may_create_private_document_copy"] is False
    assert expectations["may_upload_to_devhub"] is False
    assert expectations["may_mutate_guardrail_bundle"] is False

    assert REQUIRED_ATTESTATIONS.issubset(attestations)
    assert all(attestations[name] is True for name in REQUIRED_ATTESTATIONS)
    assert generated_from["private_document"] is False
    assert generated_from["raw_pdf_read"] is False
    assert generated_from["pdf_binary_written"] is False
    assert generated_from["official_upload"] is False
    assert generated_from["guardrail_mutation"] is False


def test_packet_has_offline_validation_commands_without_live_devhub_or_pdf_write() -> None:
    packet = load_packet()
    command_text = " ".join(" ".join(command) for command in packet["offline_validation_commands"])

    assert "ppd/tests/test_local_pdf_draft_preview_plan_v2.py" in command_text
    assert "ppd/daemon/ppd_daemon.py --self-test" in command_text
    assert "devhub.portlandoregon.gov" not in command_text
    assert "upload" not in command_text.lower()
    assert "write_pdf" not in command_text.lower()


def test_packet_omits_private_paths_and_raw_pdf_payload_markers() -> None:
    packet = load_packet()
    strings = list(walk_strings(packet))

    for value in strings:
        assert not any(pattern.search(value) for pattern in PRIVATE_PATH_PATTERNS)

    serialized = json.dumps(packet).lower()
    assert "pdf_base64" not in serialized
    assert "%%eof" not in serialized
    assert "private_document_path" not in serialized
    assert "password" not in serialized
    assert "session_token" not in serialized
