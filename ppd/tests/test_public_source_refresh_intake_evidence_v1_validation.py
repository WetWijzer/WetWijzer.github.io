from __future__ import annotations

import copy

import pytest

from ppd.crawler.public_source_refresh_intake_evidence_v1_validation import (
    PublicSourceRefreshEvidenceIntakeV1ValidationError,
    require_valid_public_source_refresh_evidence_intake_packet_v1,
    validate_public_source_refresh_evidence_intake_packet_v1,
)


def _packet() -> dict:
    return {
        "packet_type": "ppd_public_source_refresh_intake_evidence_packet",
        "packet_version": "1.0",
        "fixture_first": True,
        "metadata_only": True,
        "live_network_invoked": False,
        "processor_invoked": False,
        "archive_manifest_updated": False,
        "synthetic_reviewer_evidence": [
            {
                "evidence_id": "review-evidence-ppd-devhub-faqs",
                "source_id": "ppd-devhub-faqs",
                "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                "affected_source_ids": ["ppd-devhub-faqs"],
                "affected_requirement_ids": ["ppd-public-source-refresh-intake-v1-metadata-only"],
                "defer_or_rollback_rationale": "Fixture evidence is metadata only; discard the packet if cited source or requirement coverage is incomplete.",
                "citation_refs": [
                    {
                        "citation_id": "citation-ppd-devhub-faqs-refresh-intake",
                        "affected_source_id": "ppd-devhub-faqs",
                        "affected_requirement_id": "ppd-public-source-refresh-intake-v1-metadata-only",
                    }
                ],
                "synthetic_reviewer_evidence_fields": {
                    "refresh_reason": "fixture freshness review",
                    "expected_metadata_fields": ["content_hash", "freshness_status"],
                    "skipped_target_reason_slot": "rehearsal_only_processor_not_invoked",
                },
            }
        ],
    }


def test_public_source_refresh_evidence_intake_packet_v1_accepts_cited_metadata_only_rows() -> None:
    result = validate_public_source_refresh_evidence_intake_packet_v1(_packet())

    assert result.valid is True
    assert result.errors == ()


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"citation_refs": []}), "citation_refs must include at least one citation"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0]["citation_refs"][0].update({"affected_source_id": ""}), "affected_source_id is required"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0]["citation_refs"][0].update({"affected_requirement_id": ""}), "affected_requirement_id is required"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"affected_source_ids": []}), "affected_source_ids must include"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"affected_requirement_ids": []}), "affected_requirement_ids must include"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"defer_or_rollback_rationale": ""}), "defer_or_rollback_rationale is required"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"canonical_url": "https://example.com/ppd"}), "host must be on the PP&D public source allowlist"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"canonical_url": "http://www.portland.gov/ppd"}), "must use https"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"canonical_url": "https://devhub.portlandoregon.gov/login"}), "must not target authenticated"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"raw_page_body": "raw page body"}), "raw_page_body must be false or empty"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"downloaded_documents": ["fee-guide.pdf"]}), "downloaded_documents must be false or empty"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"processor_completed": True}), "processor_completed must be false or empty"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"archive_completed": True}), "archive_completed must be false or empty"),
        (lambda packet: packet["synthetic_reviewer_evidence"][0].update({"legal_note": "Permit will be approved after intake."}), "outcome guarantee"),
        (lambda packet: packet.update({"active_source_mutation": True}), "active_source_mutation must be false or empty"),
        (lambda packet: packet.update({"active_requirement_mutation": True}), "active_requirement_mutation must be false or empty"),
        (lambda packet: packet.update({"active_process_mutation": True}), "active_process_mutation must be false or empty"),
        (lambda packet: packet.update({"active_guardrail_mutation": True}), "active_guardrail_mutation must be false or empty"),
        (lambda packet: packet.update({"active_monitoring_mutation": True}), "active_monitoring_mutation must be false or empty"),
        (lambda packet: packet.update({"active_release_state_mutation": True}), "active_release_state_mutation must be false or empty"),
        (lambda packet: packet.update({"active_agent_state_mutation": True}), "active_agent_state_mutation must be false or empty"),
    ],
)
def test_public_source_refresh_evidence_intake_packet_v1_rejects_unsafe_or_incomplete_rows(mutation, expected: str) -> None:
    packet = copy.deepcopy(_packet())
    mutation(packet)

    with pytest.raises(PublicSourceRefreshEvidenceIntakeV1ValidationError) as exc_info:
        require_valid_public_source_refresh_evidence_intake_packet_v1(packet)

    assert expected in str(exc_info.value)
