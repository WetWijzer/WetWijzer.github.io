from __future__ import annotations

from pathlib import Path
import unittest

from ppd.crawler.freshness_refresh_plan import load_freshness_refresh_intentions, plan_freshness_refresh_intentions


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "freshness_refresh_plan" / "source_index.json"


class FreshnessRefreshPlanTest(unittest.TestCase):
    def test_fixture_converts_stale_and_hash_changed_sources_to_metadata_only_intentions(self) -> None:
        intentions = {item["source_id"]: item for item in load_freshness_refresh_intentions(FIXTURE_PATH)}

        self.assertEqual(set(intentions), {"ppd:public:devhub-faq", "ppd:public:file-standards", "ppd:public:forms-index"})

        stale = intentions["ppd:public:devhub-faq"]
        self.assertEqual(stale["refresh_reason"], "freshness_status:stale_guidance")
        self.assertEqual(stale["recrawl_mode"], "metadata_only")
        self.assertFalse(stale["network_requests_made"])
        self.assertEqual(stale["allowlist_policy"]["decision"], "allow")
        self.assertTrue(stale["robots_preflight_policy"]["required_before_live_crawl"])
        self.assertFalse(stale["robots_preflight_policy"]["live_robots_fetch_performed"])
        self.assertEqual(stale["processor_policy"]["handoff_mode"], "metadata_only_recrawl_intention")
        self.assertFalse(stale["processor_policy"]["persist_raw_body"])
        self.assertTrue(stale["no_raw_body_policy"]["no_raw_body_persisted"])
        self.assertIn("network_request", stale["blocked_actions"])
        self.assertIn("raw_body_persistence", stale["blocked_actions"])

        changed = intentions["ppd:public:file-standards"]
        self.assertEqual(changed["refresh_reason"], "content_hash_changed")
        self.assertEqual(changed["rate_limit_policy"]["bucket"], "www.portland.gov")
        self.assertEqual(changed["rate_limit_policy"]["minimum_delay_seconds"], 10)

    def test_policy_blocked_and_authenticated_sources_are_not_planned(self) -> None:
        intentions = load_freshness_refresh_intentions(FIXTURE_PATH)
        source_ids = {item["source_id"] for item in intentions}
        self.assertNotIn("ppd:public:blocked-robots", source_ids)
        self.assertNotIn("ppd:devhub:account-home", source_ids)

    def test_raw_body_fixture_fields_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "raw body"):
            plan_freshness_refresh_intentions(
                [
                    {
                        "source_id": "ppd:public:bad-raw-body",
                        "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                        "source_type": "public_html",
                        "allowlist_policy": "allow",
                        "robots_policy": "allow",
                        "crawl_frequency": "daily",
                        "processor_policy": "metadata_only",
                        "freshness_status": "stale_guidance",
                        "no_raw_body_persisted": True,
                        "raw_body": "not commit safe",
                    }
                ]
            )

    def test_raw_body_persistence_policy_fails_closed(self) -> None:
        intentions = plan_freshness_refresh_intentions(
            [
                {
                    "source_id": "ppd:public:raw-processor",
                    "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                    "source_type": "public_html",
                    "allowlist_policy": "allow",
                    "robots_policy": "allow",
                    "crawl_frequency": "daily",
                    "processor_policy": "persist_raw_body",
                    "freshness_status": "stale_guidance",
                    "no_raw_body_persisted": True,
                }
            ]
        )
        self.assertEqual(intentions, [])


if __name__ == "__main__":
    unittest.main()
