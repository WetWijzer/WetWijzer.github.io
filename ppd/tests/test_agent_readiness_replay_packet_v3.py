import json
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness" / "replay_packet_v3.json"


REQUIRED_AREAS = {
    "building",
    "trade",
    "solar",
    "demolition",
    "sign",
    "urban_forestry",
    "corrections",
}

REQUIRED_REFERENCES = {
    "missing-information",
    "document",
    "fee-deadline",
    "stale-evidence",
    "devhub-boundary",
    "pdf-preview",
    "public-refresh",
}

PROHIBITED_BOUNDARIES = {
    "live_devhub_access",
    "live_crawling",
    "form_filling",
    "uploads",
    "submissions",
    "certifications",
    "payments",
    "scheduling",
    "release_state_changes",
    "prompt_changes",
    "guardrail_changes",
    "process_model_changes",
    "requirement_changes",
    "contract_changes",
    "source_changes",
    "devhub_surface_changes",
}


def load_packet() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_replay_packet_v3_is_fixture_first_and_offline_only() -> None:
    packet = load_packet()

    assert packet["packet_version"] == 3
    assert packet["mode"] == "fixture_first_offline_replay"
    assert packet["privacy"] == {
        "uses_private_user_facts": False,
        "uses_synthetic_cases_only": True,
    }

    boundaries = packet["boundaries"]
    for boundary in PROHIBITED_BOUNDARIES:
        assert boundaries[boundary] is False


def test_replay_packet_v3_covers_required_cases_and_references() -> None:
    packet = load_packet()
    cases = packet["cases"]

    assert {case["permit_area"] for case in cases} == REQUIRED_AREAS
    assert set(packet["required_replay_references"]) == REQUIRED_REFERENCES

    for case in cases:
        assert set(case["replay_references"]) == REQUIRED_REFERENCES
        assert case["case_id"].startswith("synthetic-")
        assert case["expected_asks"]
        assert case["expected_holds"]
        assert case["expected_refusals"]
        assert case["next_safe_actions"]
        assert case["citation_references"]
        assert case["reviewer_disposition"]


def test_replay_packet_v3_records_exact_offline_validation_commands() -> None:
    packet = load_packet()

    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/tests/test_agent_readiness_replay_packet_v3.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_agent_readiness_replay_packet_v3.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_replay_packet_v3_refusals_block_state_changing_actions() -> None:
    packet = load_packet()
    refusal_text = " ".join(
        refusal.lower()
        for case in packet["cases"]
        for refusal in case["expected_refusals"]
    )

    for blocked_action in ("submit", "upload", "pay", "payment", "schedule", "certify"):
        assert blocked_action in refusal_text
