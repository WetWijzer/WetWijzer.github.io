from __future__ import annotations

from ppd.validation.document_store_gap_analysis import issue_codes, validate_gap_analysis_packet


def valid_packet() -> dict:
    return {
        "status": "draft",
        "summary": "Gap analysis for cited public PP&D requirements.",
        "process_requirements": [
            {
                "requirement": "Provide project valuation when required by the cited public instructions.",
                "citations": [
                    {
                        "title": "Portland Permitting Public Instructions",
                        "url": "https://www.portland.gov/ppd/public-example",
                    }
                ],
            }
        ],
        "freshness_evidence": [
            {
                "claim": "Public page was checked for this packet.",
                "observed_at": "2026-05-08",
                "citations": [
                    {
                        "title": "Portland Permitting Public Instructions",
                        "url": "https://www.portland.gov/ppd/public-example",
                    }
                ],
            }
        ],
        "conflicts": [
            {"description": "Two cited public pages use different labels.", "explanation": "Treat the newer cited page as controlling until staff confirms."}
        ],
        "staleness": [
            {"source": "Cached public page", "explanation": "The cached date is older than the plan verification date."}
        ],
        "next_actions": [
            {"label": "Ask user to review cited gaps", "exact_confirmation_required": False}
        ],
    }


def test_accepts_cited_privacy_safe_draft_packet() -> None:
    assert validate_gap_analysis_packet(valid_packet()) == []


def test_rejects_private_values_paths_and_raw_document_content() -> None:
    packet = valid_packet()
    packet.update(
        {
            "email": "owner@example.test",
            "notes": "Temporary file at /home/alex/private/devhub/session.json",
            "raw_content": "Full copied permit application text belongs outside packet fixtures.",
        }
    )

    codes = issue_codes(packet)

    assert "private_value" in codes
    assert "local_private_path" in codes
    assert "raw_document_content" in codes


def test_rejects_uncited_requirements_and_invented_freshness() -> None:
    packet = valid_packet()
    packet["process_requirements"] = [{"requirement": "Upload a notarized form."}]
    packet["freshness_evidence"] = [{"claim": "Latest DevHub rule confirmed."}]

    codes = issue_codes(packet)

    assert "uncited_process_requirement" in codes
    assert "invented_freshness_evidence" in codes


def test_rejects_missing_conflict_and_staleness_explanations() -> None:
    packet = valid_packet()
    packet["conflicts"] = [{"description": "Fee mismatch"}]
    packet["staleness"] = [{"source": "Old cached page", "explanation": ""}]

    codes = issue_codes(packet)

    assert "missing_conflict_staleness_explanation" in codes


def test_rejects_premature_ready_status_and_consequential_actions_without_gate() -> None:
    packet = valid_packet()
    packet["status"] = "ready_to_submit"
    packet["next_actions"] = [{"label": "Submit permit application in DevHub"}]

    codes = issue_codes(packet)

    assert "premature_ready_to_submit" in codes
    assert "missing_exact_confirmation_gate" in codes


def test_allows_ready_and_submit_action_only_with_explicit_gates() -> None:
    packet = valid_packet()
    packet["status"] = "ready_to_submit"
    packet["ready_to_submit_gate_confirmed"] = True
    packet["next_actions"] = [
        {
            "label": "Submit permit application in DevHub",
            "exact_confirmation_required": True,
        }
    ]

    assert validate_gap_analysis_packet(packet) == []
