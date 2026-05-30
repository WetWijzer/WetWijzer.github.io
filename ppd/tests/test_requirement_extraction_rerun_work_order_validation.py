from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest
from typing import Any, Mapping

from ppd.extraction.requirement_extraction_rerun_work_order import (
    build_requirement_extraction_rerun_work_order_packet,
    validate_requirement_extraction_rerun_work_order_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "requirement_extraction_rerun_work_order" / "validation_packets.json"


class RequirementExtractionRerunWorkOrderValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
            self.fixture = json.load(handle)

    def test_valid_metadata_only_work_order_packet_passes(self) -> None:
        result = validate_requirement_extraction_rerun_work_order_packet(self.fixture["valid_packet"])

        self.assertTrue(result.valid, result.errors)

    def test_invalid_work_order_packets_are_rejected(self) -> None:
        for case in self.fixture["invalid_cases"]:
            with self.subTest(case["name"]):
                packet = copy.deepcopy(self.fixture["valid_packet"])
                _merge_patch(packet, case["patch"])

                result = validate_requirement_extraction_rerun_work_order_packet(packet)

                self.assertFalse(result.valid)
                self.assertIn(case["expected_error"], "; ".join(result.errors))

    def test_builder_skips_uncited_or_requirementless_source_delta_items(self) -> None:
        packet = build_requirement_extraction_rerun_work_order_packet(
            impact_precheck={
                "packet_id": "impact-precheck-fixture",
                "impacted_requirements": [
                    {
                        "requirement_id": "req-impact",
                        "source_id": "src-impact",
                        "guardrail_id": "guardrail-impact",
                    },
                    {
                        "requirement_id": "req-missing-source",
                    },
                ],
            },
            source_freshness_delta={
                "packet_id": "source-freshness-delta-fixture",
                "source_deltas": [
                    {
                        "source_id": "src-delta",
                        "affected_requirement_id": "req-delta",
                        "affected_guardrail_id": "guardrail-delta",
                    },
                    {
                        "source_id": "src-delta-without-requirement",
                    },
                ],
            },
            traceability_review={
                "packet_id": "traceability-review-fixture",
                "traceability_findings": [
                    {
                        "requirement_id": "req-trace",
                        "source_id": "src-trace",
                        "guardrail_id": "guardrail-trace",
                    },
                    {
                        "requirement_id": "req-trace-without-source",
                    },
                ],
            },
        )

        result = validate_requirement_extraction_rerun_work_order_packet(packet)
        self.assertTrue(result.valid, result.errors)
        ids = {item["requirement_ids"][0] for item in packet["work_items"]}
        self.assertEqual(ids, {"req-impact", "req-delta", "req-trace"})


def _merge_patch(target: dict[str, Any], patch: Mapping[str, Any]) -> None:
    for key, value in patch.items():
        if key == "work_items" and isinstance(value, list):
            for index, item_patch in enumerate(value):
                if index < len(target["work_items"]) and isinstance(item_patch, Mapping):
                    _merge_patch(target["work_items"][index], item_patch)
                else:
                    target["work_items"].append(copy.deepcopy(item_patch))
        elif isinstance(value, Mapping) and isinstance(target.get(key), dict):
            _merge_patch(target[key], value)
        else:
            target[key] = copy.deepcopy(value)


if __name__ == "__main__":
    unittest.main()
