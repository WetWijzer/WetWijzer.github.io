from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.rollback_activation_decision_packet import (
    assert_valid_rollback_activation_decision_packet,
    validate_rollback_activation_decision_packet,
)


FIXTURE = Path(__file__).parent / "fixtures" / "rollback_activation_decision_packet" / "valid_packet.json"


class RollbackActivationDecisionPacketTests(unittest.TestCase):
    def load_packet(self) -> dict[str, object]:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_packet_is_valid(self) -> None:
        packet = self.load_packet()
        result = validate_rollback_activation_decision_packet(packet)
        self.assertTrue(result.valid, result.problems)
        assert_valid_rollback_activation_decision_packet(packet)

    def test_rejects_missing_required_decision_review_fields(self) -> None:
        cases = {
            "uncited trigger": lambda packet: packet["trigger_evaluations"][0].pop("source_evidence_ids"),
            "missing decision": lambda packet: packet.pop("rollback_decision"),
            "missing owner acknowledgement": lambda packet: packet.__setitem__("owner_acknowledgements", []),
            "missing offline commands": lambda packet: packet.__setitem__("offline_validation_commands", []),
        }
        for label, mutate in cases.items():
            with self.subTest(label=label):
                packet = self.load_packet()
                mutate(packet)
                result = validate_rollback_activation_decision_packet(packet)
                self.assertFalse(result.valid)

    def test_rejects_unsafe_references_claims_guarantees_and_mutation_flags(self) -> None:
        cases = {
            "raw body": {"raw_body": "raw"},
            "download ref": {"download_url": "https://www.portland.gov/ppd/documents/form/download"},
            "archive ref": {"archive_artifact_ref": "capture.warc.gz"},
            "private path": {"note": "/home/example/private/session-state.json"},
            "session artifact": {"session_state": "storage_state.json"},
            "live crawler claim": {"summary": "live crawler executed for this decision"},
            "live processor claim": {"summary": "invoked processor against the source"},
            "live DevHub claim": {"summary": "submitted to DevHub"},
            "live LLM claim": {"summary": "called the LLM for approval"},
            "outcome guarantee": {"summary": "permit will be approved"},
            "source mutation": {"mutates_sources": True},
            "requirement mutation": {"mutates_requirements": True},
            "process mutation": {"mutates_process_models": True},
            "guardrail mutation": {"mutates_guardrails": True},
            "prompt mutation": {"mutates_prompts": True},
            "surface registry mutation": {"mutates_surface_registry": True},
            "monitoring mutation": {"mutates_monitoring": True},
            "release state mutation": {"mutates_release_state": True},
        }
        for label, unsafe_fragment in cases.items():
            with self.subTest(label=label):
                packet = self.load_packet()
                packet["unsafe_probe"] = copy.deepcopy(unsafe_fragment)
                result = validate_rollback_activation_decision_packet(packet)
                self.assertFalse(result.valid)


if __name__ == "__main__":
    unittest.main()
