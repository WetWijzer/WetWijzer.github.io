from copy import deepcopy
from pathlib import Path

from ppd.coverage_gap_prioritization_packet_v1 import (
    GROUP_ORDER,
    PACKET_VERSION,
    build_packet_from_paths,
    validate_coverage_gap_prioritization_packet_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "coverage_gap_prioritization_packet_v1"
QUEUE_PATH = FIXTURE_DIR / "requirement_extraction_coverage_gap_queue_v1.json"
POLICY_PATH = FIXTURE_DIR / "reviewer_policy_v1.json"


def _packet() -> dict:
    return build_packet_from_paths(QUEUE_PATH, POLICY_PATH)


def _first_candidate(packet: dict) -> dict:
    return packet["review_groups"][0]["candidates"][0]


def _codes(packet: dict) -> set[str]:
    return {violation.code for violation in validate_coverage_gap_prioritization_packet_v1(packet)}


def test_builds_fixture_first_packet_with_expected_groups() -> None:
    packet = _packet()

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["fixture_first"] is True
    assert packet["source_queue_id"] == "fixture-coverage-gap-queue-v1-20260530"
    assert packet["group_order"] == GROUP_ORDER
    assert packet["candidate_count"] == 7

    groups = [group["group"] for group in packet["review_groups"]]
    assert groups == [
        "forms",
        "pdfs",
        "fee_triggers",
        "deadlines",
        "file_rules",
        "permit_type_exceptions",
        "action_gates",
    ]
    assert validate_coverage_gap_prioritization_packet_v1(packet) == []


def test_candidates_include_required_review_fields() -> None:
    packet = _packet()

    for group in packet["review_groups"]:
        for candidate in group["candidates"]:
            assert candidate["candidate_id"].startswith("gap-")
            assert candidate["priority_row_id"] == candidate["candidate_id"]
            assert candidate["category"] == candidate["group"]
            assert candidate["severity"] in {"critical", "high", "medium", "low"}
            assert isinstance(candidate["dependency_order"], int)
            assert candidate["reviewer_owner"]
            assert candidate["expected_follow_up_fixture_family"].startswith("ppd/tests/fixtures/")
            assert candidate["rollback_note"]
            assert candidate["requirement_id"].startswith("req-")
            assert candidate["coverage_reason"]
            assert candidate["missing_detail"]
            assert candidate["offline_validation_commands"]
            assert candidate["citations"]
            for citation in candidate["citations"]:
                assert citation["source_id"]
                assert citation["title"]
                assert citation["url"].startswith("https://")
                assert citation["citation"]


def test_candidates_are_ordered_by_severity_then_dependency_then_id() -> None:
    packet = _packet()
    action_group = next(group for group in packet["review_groups"] if group["group"] == "action_gates")
    exception_group = next(group for group in packet["review_groups"] if group["group"] == "permit_type_exceptions")
    fee_group = next(group for group in packet["review_groups"] if group["group"] == "fee_triggers")

    assert action_group["candidates"][0]["candidate_id"] == "gap-action-gate-submit-certification"
    assert action_group["candidates"][0]["severity"] == "critical"
    assert exception_group["candidates"][0]["severity"] == "high"
    assert fee_group["candidates"][0]["dependency_order"] == 2


def test_packet_remains_offline_and_non_mutating() -> None:
    packet = _packet()

    assert "does not change active requirements" in packet["scope_note"]
    assert "no active PP&D artifacts" in packet["rollback_note"]
    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/coverage_gap_prioritization_packet_v1.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_coverage_gap_prioritization_packet_v1.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_validation_rejects_uncited_priority_rows() -> None:
    packet = _packet()
    _first_candidate(packet)["citations"] = []

    assert "uncited_priority_row" in _codes(packet)


def test_validation_rejects_missing_category_severity_dependency_owner_and_rollback() -> None:
    packet = _packet()
    candidate = _first_candidate(packet)
    candidate.pop("category")
    candidate.pop("group")
    candidate.pop("severity")
    candidate.pop("dependency_order")
    candidate.pop("reviewer_owner")
    candidate.pop("rollback_note")

    assert {
        "missing_category",
        "missing_severity",
        "missing_dependency_order",
        "missing_reviewer_owner",
        "missing_rollback_note",
    }.issubset(_codes(packet))


def test_validation_rejects_private_authenticated_session_and_browser_artifacts() -> None:
    packet = _packet()
    packet["auth_state"] = "ppd/tests/fixtures/auth.json"
    packet["browser_artifact"] = "trace.zip"
    _first_candidate(packet)["notes"] = "Stored session and browser artifact are available."

    assert "forbidden_private_authenticated_session_or_browser_artifact" in _codes(packet)


def test_validation_rejects_raw_crawl_pdf_or_downloaded_data() -> None:
    packet = _packet()
    packet["raw_crawl_output"] = "raw-body.html"
    _first_candidate(packet)["notes"] = "Downloaded PDF and raw crawl output were saved."

    assert "forbidden_raw_crawl_pdf_or_downloaded_data" in _codes(packet)


def test_validation_rejects_live_extraction_or_promotion_claims() -> None:
    packet = _packet()
    packet["live_extraction"] = True
    _first_candidate(packet)["notes"] = "Release promoted after live extraction."

    assert "forbidden_live_extraction_or_promotion_claim" in _codes(packet)


def test_validation_rejects_legal_or_permitting_outcome_guarantees() -> None:
    packet = _packet()
    _first_candidate(packet)["approval_guarantee"] = True
    _first_candidate(packet)["notes"] = "Permit will be approved after this row is reviewed."

    assert "forbidden_legal_or_permitting_outcome_guarantee" in _codes(packet)


def test_validation_rejects_consequential_action_language() -> None:
    packet = _packet()
    _first_candidate(packet)["submit_permit"] = True
    _first_candidate(packet)["notes"] = "Submit the application after this prioritization step."

    assert "forbidden_consequential_action_language" in _codes(packet)


def test_validation_rejects_active_state_mutation_flags() -> None:
    packet = _packet()
    packet["active_source_mutation"] = True
    packet["active_document_mutation"] = True
    packet["active_requirement_mutation"] = True
    packet["active_process_mutation"] = True
    packet["active_guardrail_mutation"] = True
    packet["active_release_state_mutation"] = True
    packet["active_agent_state_mutation"] = True

    assert "active_ppd_state_mutation" in _codes(packet)


def test_validation_does_not_mutate_input_packet() -> None:
    packet = _packet()
    before = deepcopy(packet)

    assert validate_coverage_gap_prioritization_packet_v1(packet) == []
    assert packet == before
