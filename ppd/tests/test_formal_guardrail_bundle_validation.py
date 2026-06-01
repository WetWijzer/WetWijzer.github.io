import copy
import json
import unittest
from pathlib import Path

from ppd.logic.formal_guardrail_bundle_validation import (
    formal_guardrail_bundle_allows_autonomous_planning,
    validate_formal_guardrail_bundle,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "formal_guardrail_bundle_validation" / "bundles.json"


class FormalGuardrailBundleValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_valid_bundle_allows_autonomous_planning(self):
        bundle = self.fixture["valid_bundle"]

        self.assertEqual([], validate_formal_guardrail_bundle(bundle))
        self.assertTrue(formal_guardrail_bundle_allows_autonomous_planning(bundle))

    def test_fail_closed_cases_reject_autonomous_planning(self):
        for case in self.fixture["invalid_cases"]:
            with self.subTest(case=case["name"]):
                bundle = copy.deepcopy(self.fixture["valid_bundle"])
                _deep_update(bundle, case["patch"])

                findings = validate_formal_guardrail_bundle(bundle)
                codes = {finding["code"] for finding in findings}

                self.assertFalse(formal_guardrail_bundle_allows_autonomous_planning(bundle))
                self.assertIn(case["expected_code"], codes)



def _deep_update(target, patch):
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = value


if __name__ == "__main__":
    unittest.main()
