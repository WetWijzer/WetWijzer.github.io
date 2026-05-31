"""Deterministic fixture for fee/deadline trigger matrix packet v2 tests."""

from __future__ import annotations


def valid_packet() -> dict:
    return {
        "packet_version": "fee_deadline_trigger_matrix_packet_v2",
        "packet_id": "fixture-fee-deadline-trigger-matrix-v2",
        "fee_trigger_rows": [
            {
                "row_id": "fee-trigger-placeholder-001",
                "permit_scope": "fixture permit scope pending source review",
                "fee_trigger_cue": "fee cue placeholder pending cited source extraction",
                "source_evidence_placeholder": "SOURCE_EVIDENCE_PLACEHOLDER:fee-trigger-001",
                "reviewer_disposition": "needs_source_review",
            }
        ],
        "deadline_or_expiration_cues": [
            {
                "cue_id": "deadline-placeholder-001",
                "cue_text": "deadline or expiration cue placeholder pending cited source extraction",
                "source_evidence_placeholder": "SOURCE_EVIDENCE_PLACEHOLDER:deadline-001",
            }
        ],
        "payment_boundary_warnings": [
            "Do not enter, store, infer, or submit payment details; fee payment remains attended and exact-confirmation gated."
        ],
        "source_evidence_placeholders": [
            "SOURCE_EVIDENCE_PLACEHOLDER:fee-trigger-001",
            "SOURCE_EVIDENCE_PLACEHOLDER:deadline-001",
        ],
        "stale_source_hold_notes": [
            "Hold promotion when source freshness is stale, missing, ambiguous, or awaiting reviewer disposition."
        ],
        "blocked_financial_action_reminders": [
            "Block purchase, payment-detail entry, final submit-payment, certification tied to payment, and any financial action."
        ],
        "reviewer_dispositions": [
            {
                "reviewer": "fixture-reviewer",
                "disposition": "needs_source_review",
                "note": "Fixture packet is not a source of authority and does not mutate requirements.",
            }
        ],
        "validation_commands": [
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]
        ],
        "mutation_flags": {
            "active_requirement_mutation": False,
            "active_process_model_mutation": False,
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_contract_mutation": False,
            "active_source_mutation": False,
            "active_devhub_surface_mutation": False,
            "active_release_state_mutation": False,
        },
    }
