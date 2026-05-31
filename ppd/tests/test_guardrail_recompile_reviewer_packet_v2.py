from __future__ import annotations

import copy
import unittest

from ppd.agent_readiness.guardrail_recompile_reviewer_packet_v2 import (
    finding_codes,
    require_valid_guardrail_recompile_reviewer_packet_v2,
    validate_guardrail_recompile_reviewer_packet_v2,
)


def _valid_packet() -> dict[str, object]:
    return {
        "packet_version": "guardrail_recompile_reviewer_packet_v2",
        "reviewer_rows": [
            {
                "row_id": "review-row-single-pdf-upload-001",
                "requirement_delta_traces": ["requirement-delta-trace-single-pdf-upload"],
                "predicate_impact_review_note": "Predicate impact reviewed against the inactive single PDF upload staging fixture.",
                "migration_risk_disposition": "no_active_migration_allowed_review_only",
                "stale_source_hold_carry_forward_decision": "carry_forward_existing_hold_until_public_source_refresh",
                "blocked_action_reminder_check": "verified_consequential_actions_remain_blocked",
            }
        ],
        "active_source_mutation_enabled": False,
        "active_requirement_mutation_enabled": False,
        "active_process_model_mutation_enabled": False,
        "active_guardrail_mutation_enabled": False,
        "active_prompt_mutation_enabled": False,
        "active_contract_mutation_enabled": False,
        "active_devhub_surface_mutation_enabled": False,
        "active_release_state_mutation_enabled": False,
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
    }


class GuardrailRecompileReviewerPacketV2Test(unittest.TestCase):
    def test_accepts_minimal_valid_packet(self) -> None:
        require_valid_guardrail_recompile_reviewer_packet_v2(_valid_packet())
        self.assertEqual(validate_guardrail_recompile_reviewer_packet_v2(_valid_packet()), [])

    def test_rejects_missing_reviewer_rows(self) -> None:
        packet = _valid_packet()
        packet["reviewer_rows"] = []

        codes = finding_codes(validate_guardrail_recompile_reviewer_packet_v2(packet))

        self.assertIn("missing_reviewer_rows", codes)

    def test_rejects_missing_required_row_review_fields(self) -> None:
        packet = _valid_packet()
        packet["reviewer_rows"] = [{"row_id": "incomplete-row"}]

        codes = finding_codes(validate_guardrail_recompile_reviewer_packet_v2(packet))

        self.assertIn("missing_requirement_delta_traces", codes)
        self.assertIn("missing_predicate_impact_review_notes", codes)
        self.assertIn("missing_migration_risk_dispositions", codes)
        self.assertIn("missing_stale_source_hold_carry_forward_decisions", codes)
        self.assertIn("missing_blocked_action_reminder_checks", codes)

    def test_rejects_missing_validation_commands(self) -> None:
        packet = _valid_packet()
        packet["validation_commands"] = []

        codes = finding_codes(validate_guardrail_recompile_reviewer_packet_v2(packet))

        self.assertIn("missing_validation_commands", codes)

    def test_rejects_private_session_browser_raw_or_downloaded_artifacts(self) -> None:
        packet = _valid_packet()
        packet["review_artifacts"] = {
            "session_file": "ppd/data/private/devhub-session.json",
            "browser_state_path": "ppd/data/private/browser-state.json",
            "raw_crawl_output": "ppd/data/raw/public-crawl.html",
            "downloaded_document_path": "ppd/downloads/fee-guide.pdf",
            "trace_file": "trace.zip",
        }

        codes = finding_codes(validate_guardrail_recompile_reviewer_packet_v2(packet))

        self.assertIn("private_session_browser_raw_or_downloaded_artifact", codes)

    def test_rejects_live_crawl_or_devhub_claims(self) -> None:
        packet = _valid_packet()
        packet["live_crawl_claimed"] = True
        packet["notes"] = "Reviewer opened DevHub during this packet build."

        codes = finding_codes(validate_guardrail_recompile_reviewer_packet_v2(packet))

        self.assertIn("live_crawl_or_devhub_claim", codes)

    def test_rejects_legal_or_permitting_guarantees(self) -> None:
        packet = _valid_packet()
        packet["approval_guarantee"] = True
        packet["reviewer_rows"] = copy.deepcopy(packet["reviewer_rows"])
        packet["reviewer_rows"][0]["predicate_impact_review_note"] = "This permit will be approved after recompilation."

        codes = finding_codes(validate_guardrail_recompile_reviewer_packet_v2(packet))

        self.assertIn("legal_or_permitting_guarantee", codes)

    def test_rejects_active_mutation_flags_for_all_guarded_surfaces(self) -> None:
        guarded_flags = [
            "active_source_mutation_enabled",
            "active_requirement_mutation_enabled",
            "active_process_model_mutation_enabled",
            "active_guardrail_mutation_enabled",
            "active_prompt_mutation_enabled",
            "active_contract_mutation_enabled",
            "active_devhub_surface_mutation_enabled",
            "active_release_state_mutation_enabled",
        ]
        for flag in guarded_flags:
            with self.subTest(flag=flag):
                packet = _valid_packet()
                packet[flag] = True

                codes = finding_codes(validate_guardrail_recompile_reviewer_packet_v2(packet))

                self.assertIn("active_state_mutation_flag", codes)


if __name__ == "__main__":
    unittest.main()
