from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ppd.extraction.public_source_freshness_review_v2 import (
    PACKET_VERSION,
    build_public_source_freshness_review_packet_v2,
    offline_validation_commands,
    parse_archive_manifest,
    validate_public_source_freshness_review_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_freshness_v2"
SOURCE_REGISTRY_FIXTURE = FIXTURE_DIR / "source_registry.json"
ARCHIVE_MANIFEST_FIXTURE = FIXTURE_DIR / "archive_manifest.json"


class PublicSourceFreshnessReviewPacketV2Tests(unittest.TestCase):
    def test_builds_fixture_first_packet_without_live_collection(self) -> None:
        packet = build_public_source_freshness_review_packet_v2(
            SOURCE_REGISTRY_FIXTURE,
            ARCHIVE_MANIFEST_FIXTURE,
        )

        self.assertEqual(packet["packet_version"], PACKET_VERSION)
        self.assertFalse(packet["live_crawl_performed"])
        self.assertFalse(packet["documents_downloaded"])
        self.assertFalse(packet["raw_bodies_persisted"])
        self.assertFalse(packet["raw_downloaded_body_artifacts_present"])
        self.assertFalse(packet["crawl_output_persisted"])
        self.assertFalse(packet["devhub_automation_performed"])
        self.assertFalse(packet["unauthenticated_devhub_automation_claimed"])
        self.assertFalse(packet["authenticated_devhub_automation_claimed"])
        self.assertFalse(packet["legal_or_permitting_guarantees_made"])
        self.assertFalse(packet["active_sources_mutated"])
        self.assertFalse(packet["active_requirements_mutated"])
        self.assertFalse(packet["active_guardrails_mutated"])
        self.assertFalse(packet["active_prompts_mutated"])
        self.assertFalse(packet["active_contracts_mutated"])
        self.assertFalse(packet["active_release_state_mutated"])
        self.assertEqual(packet["offline_validation_commands"], offline_validation_commands())
        self.assertTrue(validate_public_source_freshness_review_packet_v2(packet).ok)

    def test_orders_rows_by_official_anchor_sequence(self) -> None:
        packet = build_public_source_freshness_review_packet_v2(
            SOURCE_REGISTRY_FIXTURE,
            ARCHIVE_MANIFEST_FIXTURE,
        )
        rows = packet["ordered_synthetic_freshness_rows"]

        self.assertEqual(
            [row["source_id"] for row in rows],
            [
                "ppd-bureau-landing",
                "ppd-online-tools",
                "ppd-devhub-faq",
                "ppd-submit-plans-online",
            ],
        )
        self.assertEqual([row["row_order"] for row in rows], [1, 2, 3, 4])
        self.assertTrue(all(row["is_official_ppd_anchor"] for row in rows))

    def test_rows_include_required_review_placeholders(self) -> None:
        packet = build_public_source_freshness_review_packet_v2(
            SOURCE_REGISTRY_FIXTURE,
            ARCHIVE_MANIFEST_FIXTURE,
        )

        for row in packet["ordered_synthetic_freshness_rows"]:
            self.assertIn("official_anchor_trace", row)
            self.assertTrue(row["official_anchor_trace"]["matched_official_anchor"])
            self.assertIn("last_seen_placeholder", row)
            self.assertIn("hash_change_placeholder", row)
            self.assertEqual(
                row["affected_requirement_placeholders"],
                ["PLACEHOLDER_AFFECTED_REQUIREMENT_IDS_PENDING_DIFF_REVIEW"],
            )
            self.assertEqual(
                row["affected_guardrail_bundle_placeholders"],
                ["PLACEHOLDER_AFFECTED_GUARDRAIL_BUNDLE_IDS_PENDING_DIFF_REVIEW"],
            )
            self.assertEqual(
                row["reviewer_disposition_placeholder"]["status"],
                "PLACEHOLDER_REVIEWER_DISPOSITION_PENDING",
            )
            self.assertEqual(row["offline_validation_commands"], offline_validation_commands())

    def test_missing_last_seen_uses_placeholder(self) -> None:
        packet = build_public_source_freshness_review_packet_v2(
            SOURCE_REGISTRY_FIXTURE,
            ARCHIVE_MANIFEST_FIXTURE,
        )
        online_tools = next(
            row for row in packet["ordered_synthetic_freshness_rows"] if row["source_id"] == "ppd-online-tools"
        )

        self.assertIsNone(online_tools["registry_last_seen_at"])
        self.assertEqual(
            online_tools["last_seen_placeholder"],
            "PLACEHOLDER_LAST_SEEN_PENDING_OFFLINE_FIXTURE_CAPTURE",
        )

    def test_archive_manifest_fixture_declares_no_raw_body_persistence(self) -> None:
        manifests = parse_archive_manifest(_load_fixture(ARCHIVE_MANIFEST_FIXTURE))

        self.assertTrue(manifests)
        self.assertTrue(all(manifest.no_raw_body_persisted for manifest in manifests))

    def test_validation_rejects_missing_required_packet_sections(self) -> None:
        packet = _valid_packet()
        cases = [
            ("ordered_synthetic_freshness_rows", "freshness row"),
            ("official_anchor_order", "official anchor"),
            ("offline_validation_commands", "validation command"),
        ]

        for key, expected in cases:
            candidate = copy.deepcopy(packet)
            candidate.pop(key)
            result = validate_public_source_freshness_review_packet_v2(candidate)
            self.assertFalse(result.ok, key)
            self.assertIn(expected, " ".join(result.errors))

    def test_validation_rejects_missing_required_row_placeholders(self) -> None:
        packet = _valid_packet()
        cases = [
            ("official_anchor_trace", "official_anchor_trace"),
            ("last_seen_placeholder", "last_seen_placeholder"),
            ("hash_change_placeholder", "hash_change_placeholder"),
            ("affected_requirement_placeholders", "affected_requirement_placeholders"),
            ("affected_guardrail_bundle_placeholders", "affected_guardrail_bundle_placeholders"),
            ("reviewer_disposition_placeholder", "reviewer_disposition_placeholder"),
            ("offline_validation_commands", "offline_validation_commands"),
        ]

        for key, expected in cases:
            candidate = copy.deepcopy(packet)
            candidate["ordered_synthetic_freshness_rows"][0].pop(key)
            result = validate_public_source_freshness_review_packet_v2(candidate)
            self.assertFalse(result.ok, key)
            self.assertIn(expected, " ".join(result.errors))

    def test_validation_rejects_raw_downloaded_artifacts_and_live_claims(self) -> None:
        packet = _valid_packet()
        cases = [
            ("raw_downloaded_body_artifacts_present", True, "raw_downloaded_body_artifacts_present"),
            ("documents_downloaded", True, "documents_downloaded"),
            ("live_crawl_performed", True, "live_crawl_performed"),
            ("crawl_output_persisted", True, "crawl_output_persisted"),
        ]

        for key, value, expected in cases:
            candidate = copy.deepcopy(packet)
            candidate[key] = value
            result = validate_public_source_freshness_review_packet_v2(candidate)
            self.assertFalse(result.ok, key)
            self.assertIn(expected, " ".join(result.errors))

        candidate = copy.deepcopy(packet)
        candidate["ordered_synthetic_freshness_rows"][0]["downloaded_body"] = "raw"
        result = validate_public_source_freshness_review_packet_v2(candidate)
        self.assertFalse(result.ok)
        self.assertIn("downloaded_body", " ".join(result.errors))

    def test_validation_rejects_devhub_automation_claims_and_guarantees(self) -> None:
        packet = _valid_packet()
        cases = [
            "devhub_automation_performed",
            "unauthenticated_devhub_automation_claimed",
            "authenticated_devhub_automation_claimed",
            "legal_or_permitting_guarantees_made",
            "legal_guarantee_claimed",
            "permitting_guarantee_claimed",
            "permit_approval_guaranteed",
        ]

        for key in cases:
            candidate = copy.deepcopy(packet)
            candidate[key] = True
            result = validate_public_source_freshness_review_packet_v2(candidate)
            self.assertFalse(result.ok, key)
            self.assertIn(key, " ".join(result.errors))

    def test_validation_rejects_active_mutation_flags(self) -> None:
        packet = _valid_packet()
        cases = [
            "active_sources_mutated",
            "active_requirements_mutated",
            "active_guardrails_mutated",
            "active_prompts_mutated",
            "active_contracts_mutated",
            "active_release_state_mutated",
            "active_source_mutation_flag",
            "active_requirement_mutation_flag",
            "active_guardrail_mutation_flag",
            "active_prompt_mutation_flag",
            "active_contract_mutation_flag",
            "active_release_state_mutation_flag",
        ]

        for key in cases:
            candidate = copy.deepcopy(packet)
            candidate[key] = True
            result = validate_public_source_freshness_review_packet_v2(candidate)
            self.assertFalse(result.ok, key)
            self.assertIn(key, " ".join(result.errors))


def _valid_packet() -> dict[str, object]:
    return build_public_source_freshness_review_packet_v2(
        SOURCE_REGISTRY_FIXTURE,
        ARCHIVE_MANIFEST_FIXTURE,
    )


def _load_fixture(path: Path) -> object:
    import json

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    unittest.main()
