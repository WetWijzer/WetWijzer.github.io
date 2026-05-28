from pathlib import Path

from ppd.logic.agent_response_contracts import (
    is_valid_agent_response_contract,
    redact_private_values,
    validate_agent_response_contract,
    violation_codes,
)


def test_accepts_narrow_fact_gap_questions_with_cited_explanations_and_confirmation() -> None:
    contract = {
        "questions": [
            {"prompt": "What permit number is missing from the record?", "reason": "missing"},
            {"prompt": "Which of these two hearing dates is correct?", "reason": "conflicting"},
        ],
        "explanations": [
            {
                "text": "The permit status is listed in the public record.",
                "citations": [{"url": "https://www.portland.gov/example", "title": "Public record"}],
            }
        ],
        "actions": [
            {
                "kind": "submit",
                "description": "Submit a final form to PP&D only after review.",
                "requires_explicit_confirmation": True,
            }
        ],
    }

    assert is_valid_agent_response_contract(contract)


def test_rejects_questions_outside_allowed_fact_gap_scope() -> None:
    contract = {"questions": [{"prompt": "What should I do next?", "reason": "preference"}]}

    codes = violation_codes(validate_agent_response_contract(contract))

    assert "question_scope" in codes


def test_redacts_private_values_and_local_paths() -> None:
    payload = {
        "notes": "Saved at /home/alex/private/session.json for owner alex@example.com",
        "api_token": "sk-testtoken1234567890",
    }

    redacted = redact_private_values(payload)

    assert redacted["notes"] == "Saved at [REDACTED] for owner [REDACTED]"
    assert redacted["api_token"] == "[REDACTED]"


def test_rejects_credentials_payment_details_and_auth_state() -> None:
    contract = {
        "questions": [
            {"prompt": "What is the account password?", "reason": "missing"},
            {"prompt": "What card number 4111 1111 1111 1111 should be used?", "reason": "ambiguous"},
            {"prompt": "Paste the browser cookie for this permit session.", "reason": "missing"},
        ]
    }

    codes = violation_codes(validate_agent_response_contract(contract))

    assert "question_sensitive_content" in codes
    assert "sensitive_content" in codes


def test_rejects_uncited_explanations() -> None:
    contract = {"explanations": [{"text": "This parcel is eligible.", "citations": []}]}

    codes = violation_codes(validate_agent_response_contract(contract))

    assert "uncited_explanation" in codes


def test_blocks_consequential_actions_without_confirmation_requirement() -> None:
    contract = {
        "actions": [
            {
                "kind": "payment",
                "description": "Pay the permit fee.",
                "requires_explicit_confirmation": False,
            }
        ]
    }

    codes = violation_codes(validate_agent_response_contract(contract))

    assert "confirmation_required" in codes


def test_fixture_path_pattern_stays_under_ppd_tests() -> None:
    fixture_root = Path(__file__).parent / "fixtures"

    assert "ppd/tests/fixtures" in fixture_root.as_posix()
