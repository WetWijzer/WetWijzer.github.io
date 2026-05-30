import json
import unittest
from pathlib import Path

from ppd.release_candidate_evidence_v1 import (
    build_release_candidate_evidence_bundle_v1,
    validate_release_candidate_evidence_bundle_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "release_candidate_evidence_v1"


class ReleaseCandidateEvidenceBundleV1Test(unittest.TestCase):
    def test_fixture_inputs_build_expected_bundle(self):
        inputs = json.loads((FIXTURE_DIR / "inputs.json").read_text(encoding="utf-8"))
        expected = json.loads((FIXTURE_DIR / "expected_bundle.json").read_text(encoding="utf-8"))

        actual = build_release_candidate_evidence_bundle_v1(inputs)

        self.assertEqual(actual, expected)
        validate_release_candidate_evidence_bundle_v1(actual)

    def test_missing_required_packet_is_rejected(self):
        inputs = json.loads((FIXTURE_DIR / "inputs.json").read_text(encoding="utf-8"))
        inputs.pop("readiness_gap_report_v1")

        with self.assertRaisesRegex(ValueError, "missing release candidate input packet"):
            build_release_candidate_evidence_bundle_v1(inputs)

    def test_attestations_are_required(self):
        inputs = json.loads((FIXTURE_DIR / "inputs.json").read_text(encoding="utf-8"))
        bundle = build_release_candidate_evidence_bundle_v1(inputs)
        bundle["attestations"]["no_live_crawl"] = False

        with self.assertRaisesRegex(ValueError, "attestation no_live_crawl"):
            validate_release_candidate_evidence_bundle_v1(bundle)


if __name__ == "__main__":
    unittest.main()
