from __future__ import annotations

import unittest

from ppd.official_source_anchor_audit import (
    PACKET_VERSION,
    is_valid_official_source_anchor_audit_packet_v1,
    validate_official_source_anchor_audit_packet_v1,
)


def valid_packet() -> dict[str, object]:
    return {
        "packet_version": PACKET_VERSION,
        "reviewer_owner": "ppd-source-reviewer",
        "rollback_note": "Drop this packet and keep existing source anchors unchanged.",
        "affected_source_ids": ["ppd-online-tools"],
        "anchors": [
            {
                "source_id": "ppd-online-tools",
                "url": "https://www.portland.gov/ppd/how-use-online-permitting-tools",
                "citation_ids": ["cite-online-tools-2026-05-08"],
                "anchor_label": "Online permitting tools overview",
            }
        ],
        "notes": "Metadata-only anchor audit; no live crawl or processor handoff is claimed.",
    }


class OfficialSourceAnchorAuditPacketV1Tests(unittest.TestCase):
    def codes_for(self, packet: dict[str, object]) -> set[str]:
        return {error.code for error in validate_official_source_anchor_audit_packet_v1(packet)}

    def test_accepts_metadata_only_official_anchor_packet(self) -> None:
        self.assertTrue(is_valid_official_source_anchor_audit_packet_v1(valid_packet()))

    def test_rejects_uncited_anchor_rows(self) -> None:
        packet = valid_packet()
        anchors = packet["anchors"]
        assert isinstance(anchors, list)
        anchor = anchors[0]
        assert isinstance(anchor, dict)
        anchor["citation_ids"] = []
        self.assertIn("uncited_anchor_row", self.codes_for(packet))

    def test_rejects_non_official_or_non_allowlisted_urls(self) -> None:
        packet = valid_packet()
        anchors = packet["anchors"]
        assert isinstance(anchors, list)
        anchor = anchors[0]
        assert isinstance(anchor, dict)
        anchor["url"] = "https://example.com/ppd"
        self.assertIn("non_official_or_non_allowlisted_url", self.codes_for(packet))

    def test_rejects_authenticated_or_private_urls(self) -> None:
        packet = valid_packet()
        anchors = packet["anchors"]
        assert isinstance(anchors, list)
        anchor = anchors[0]
        assert isinstance(anchor, dict)
        anchor["url"] = "https://devhub.portlandoregon.gov/account/permits?token=secret"
        self.assertIn("authenticated_or_private_url", self.codes_for(packet))

    def test_rejects_raw_page_bodies_and_downloaded_documents(self) -> None:
        packet = valid_packet()
        packet["raw_html"] = "full page body"
        packet["downloaded_documents"] = ["/tmp/private/devhub-guide.pdf"]
        codes = self.codes_for(packet)
        self.assertIn("raw_page_body_present", codes)
        self.assertIn("downloaded_document_present", codes)

    def test_rejects_processor_and_archive_completion_claims(self) -> None:
        packet = valid_packet()
        packet["processor_completed"] = True
        packet["archive_complete"] = True
        self.assertIn("processor_or_archive_completion_claim", self.codes_for(packet))

    def test_rejects_missing_affected_source_ids(self) -> None:
        packet = valid_packet()
        packet["affected_source_ids"] = []
        self.assertIn("missing_affected_source_ids", self.codes_for(packet))

    def test_rejects_missing_reviewer_owner_or_rollback_note(self) -> None:
        packet = valid_packet()
        packet["reviewer_owner"] = ""
        packet["rollback_note"] = ""
        codes = self.codes_for(packet)
        self.assertIn("missing_reviewer_owner", codes)
        self.assertIn("missing_rollback_note", codes)

    def test_rejects_live_execution_claims(self) -> None:
        packet = valid_packet()
        packet["live_execution"] = True
        self.assertIn("live_execution_claim", self.codes_for(packet))

    def test_rejects_legal_or_permitting_outcome_guarantees(self) -> None:
        packet = valid_packet()
        packet["review_note"] = "This packet says permit will be approved."
        self.assertIn("outcome_guarantee_claim", self.codes_for(packet))

    def test_rejects_active_mutation_flags(self) -> None:
        for flag in (
            "active_source_mutation",
            "active_requirement_mutation",
            "active_process_mutation",
            "active_guardrail_mutation",
            "active_monitoring_mutation",
            "active_release_state_mutation",
            "active_agent_state_mutation",
        ):
            packet = valid_packet()
            packet[flag] = True
            self.assertIn("active_mutation_flag", self.codes_for(packet), flag)


if __name__ == "__main__":
    unittest.main()
