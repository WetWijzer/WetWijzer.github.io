import json
import unittest
from pathlib import Path

from ppd.requirement_extraction_impact_precheck_packet import (
    build_requirement_extraction_impact_precheck_packet,
    validate_requirement_extraction_impact_precheck_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "requirement_extraction_impact_precheck" / "packet.json"


def load_fixture() -> dict:
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class RequirementExtractionImpactPrecheckPacketTest(unittest.TestCase):
    def test_builds_expected_candidate_extraction_rerun_scopes(self) -> None:
        fixture = load_fixture()

        packet = build_requirement_extraction_impact_precheck_packet(fixture)

        self.assertEqual(packet, fixture["expected_packet"])

    def test_requires_no_live_extraction_attestation(self) -> None:
        fixture = load_fixture()
        packet = build_requirement_extraction_impact_precheck_packet(fixture)
        packet["attestations"]["no_live_extraction_performed"] = False

        with self.assertRaisesRegex(ValueError, "no_live_extraction_performed"):
            validate_requirement_extraction_impact_precheck_packet(packet)

    def test_requires_metadata_only_outputs(self) -> None:
        fixture = load_fixture()
        packet = build_requirement_extraction_impact_precheck_packet(fixture)
        packet["expected_metadata_only_outputs"][0]["metadata_only"] = False

        with self.assertRaisesRegex(ValueError, "metadata_only"):
            validate_requirement_extraction_impact_precheck_packet(packet)

    def test_rejects_active_artifact_mutation_flags(self) -> None:
        fixture = load_fixture()
        packet = build_requirement_extraction_impact_precheck_packet(fixture)
        packet["candidate_extraction_rerun_scopes"][0]["active_artifact_mutation"] = True

        with self.assertRaisesRegex(ValueError, "active artifact mutation"):
            validate_requirement_extraction_impact_precheck_packet(packet)


if __name__ == "__main__":
    unittest.main()
