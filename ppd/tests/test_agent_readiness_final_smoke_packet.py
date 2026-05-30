import json
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness_final_smoke_packet.json"


def load_packet():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_final_smoke_packet_consumes_required_packets():
    packet = load_packet()
    consumed = {entry["packet_id"] for entry in packet["consumes_packets"]}

    assert consumed == {
        "agent-freshness-regression-acceptance-packet",
        "release-blocker-closure-review-packet",
        "safe-read-only-agent-action-transcript-packet",
    }
    for entry in packet["consumes_packets"]:
        assert entry["citation"].startswith("ppd/tests/fixtures/")
        assert entry["citation"].endswith(".json")


def test_final_smoke_packet_is_offline_and_non_mutating():
    packet = load_packet()
    attestations = packet["offline_attestations"]

    for key in (
        "no_live_llm",
        "no_devhub",
        "no_prompt_capture",
        "no_guardrail_mutation",
        "no_agent_state_mutation",
        "no_network_required",
        "fixture_only_inputs",
    ):
        assert attestations[key] is True


def test_final_smoke_packet_covers_required_scenarios_with_citations():
    packet = load_packet()
    scenarios = packet["smoke_scenarios"]
    covered = {item for scenario in scenarios for item in scenario["covers"]}

    assert {
        "missing_facts",
        "stale_evidence",
        "refusal_explanations",
        "reversible_draft_previews",
        "blocked_consequential_actions",
        "reviewer_owner_fields",
        "no_live_llm",
        "no_devhub",
        "no_prompt",
        "no_guardrail",
        "no_agent_state_mutation",
    }.issubset(covered)

    for scenario in scenarios:
        assert scenario["id"]
        assert scenario["given"]
        assert scenario["expect"]
        assert scenario["citations"]
        assert all(":" in citation for citation in scenario["citations"])


def test_final_smoke_packet_preserves_reviewer_owner_decision():
    packet = load_packet()
    review = packet["review"]

    assert review["reviewer"]
    assert review["owner"]
    assert review["decision"] == "ready-for-offline-validation"
    assert "does not authorize live crawl" in review["notes"]
