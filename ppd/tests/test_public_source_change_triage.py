from __future__ import annotations

import unittest

from ppd.public_source_change_triage import (
    PublicSourceChangeTriageError,
    assert_valid_public_source_change_triage_packet_v1,
    validate_public_source_change_triage_packet_v1,
)


def valid_packet() -> dict[str, object]:
    return {
        "packet_version": "public-source-change-triage-v1",
        "rows": [
            {
                "row_id": "changed-fee-guide-step",
                "disposition": "changed",
                "citations": ["source:fee-guide#step-3"],
                "impact_references": ["requirement:fee-payment-gate"],
            },
            {
                "row_id": "unchanged-single-pdf-rule",
                "disposition": "unchanged",
                "citations": ["source:single-pdf#rule"],
            },
            {
                "row_id": "review-upload-copy",
                "disposition": "needs-review",
                "citations": ["source:upload-corrections#copy"],
            },
            {
                "row_id": "blocked-devhub-private-step",
                "disposition": "blocked",
                "citations": ["source:devhub-public-guide#auth-boundary"],
            },
        ],
        "impact_references": ["guardrail:fee-payment", "process:upload-corrections"],
        "citation_preservation_checks": ["all changed rows retain source anchors"],
        "blocked_promotion_explanations": ["authenticated DevHub details are excluded from public promotion"],
        "rollback_notes": ["remove generated triage artifact and rerun deterministic fixture validation"],
        "validation_replay_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "active_mutation": False,
    }


class PublicSourceChangeTriageValidationTests(unittest.TestCase):
    def test_accepts_complete_packet(self) -> None:
        assert_valid_public_source_change_triage_packet_v1(valid_packet())

    def test_rejects_uncited_changed_rows_and_missing_dispositions(self) -> None:
        packet = valid_packet()
        packet["rows"] = [
            {
                "row_id": "changed-without-citation",
                "disposition": "changed",
                "impact_references": ["requirement:changed"],
            }
        ]

        codes = {issue.code for issue in validate_public_source_change_triage_packet_v1(packet)}

        self.assertIn("row.changed.uncited", codes)
        self.assertIn("rows.unchanged_disposition.missing", codes)
        self.assertIn("rows.needs_review_disposition.missing", codes)

    def test_rejects_missing_required_packet_fields(self) -> None:
        packet = valid_packet()
        for key in (
            "impact_references",
            "citation_preservation_checks",
            "blocked_promotion_explanations",
            "rollback_notes",
            "validation_replay_commands",
        ):
            packet[key] = []

        codes = {issue.code for issue in validate_public_source_change_triage_packet_v1(packet)}

        self.assertIn("packet.impact_references.missing", codes)
        self.assertIn("packet.citation_preservation_checks.missing", codes)
        self.assertIn("packet.blocked_promotion_explanations.missing", codes)
        self.assertIn("packet.rollback_notes.missing", codes)
        self.assertIn("packet.validation_replay_commands.missing", codes)

    def test_rejects_private_raw_live_guarantee_and_action_language(self) -> None:
        packet = valid_packet()
        packet["notes"] = [
            "contains session storage_state details",
            "contains raw crawl output and downloaded PDF material",
            "claims a live crawl was performed",
            "says the permit will issue",
            "tells the worker to click submit",
        ]

        codes = {issue.code for issue in validate_public_source_change_triage_packet_v1(packet)}

        self.assertIn("packet.forbidden_text.private_artifact", codes)
        self.assertIn("packet.forbidden_text.raw_artifact", codes)
        self.assertIn("packet.forbidden_text.live_crawl_claim", codes)
        self.assertIn("packet.forbidden_text.outcome_guarantee", codes)
        self.assertIn("packet.forbidden_text.consequential_action", codes)

    def test_rejects_active_artifact_mutation_flags(self) -> None:
        packet = valid_packet()
        packet["promotion"] = {"promote_to_current": True}

        codes = {issue.code for issue in validate_public_source_change_triage_packet_v1(packet)}

        self.assertIn("packet.active_mutation_flag", codes)

    def test_raises_compact_error_for_invalid_packet(self) -> None:
        packet = valid_packet()
        packet["packet_version"] = "wrong"

        with self.assertRaises(PublicSourceChangeTriageError):
            assert_valid_public_source_change_triage_packet_v1(packet)


if __name__ == "__main__":
    unittest.main()
