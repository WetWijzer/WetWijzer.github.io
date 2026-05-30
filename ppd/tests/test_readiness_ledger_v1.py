from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ppd.agent_readiness.readiness_ledger_v1 import validate_readiness_ledger_v1


class ReadinessLedgerV1ValidationTests(unittest.TestCase):
    def test_accepts_commit_safe_cited_readiness_ledger(self) -> None:
        ledger = {
            "ledger_version": "ppd-readiness-ledger-v1",
            "readiness_rows": [
                {
                    "row_id": "ready-row",
                    "source_evidence_ids": ["ppd-source-devhub-faq"],
                    "readiness_packet_ref": "packet://ppd/readiness/ready-row",
                    "validator_ref": "ppd.agent_readiness.readiness_ledger_v1.validate_readiness_ledger_v1",
                    "manual_review_blockers": ["operator_review_required_before_promotion"],
                    "fixture_version_claim": {
                        "fixture_id": "ppd/tests/fixtures/readiness_ledger_v1/safe.json",
                        "fixture_version": "2026-05-29",
                        "freshness_status": "current",
                        "last_verified_at": "2026-05-29T00:00:00Z",
                    },
                    "artifacts": ["metadata-only archive manifest", "normalized citation spans"],
                    "mutation_policy": "read_only",
                }
            ],
        }

        result = validate_readiness_ledger_v1(
            ledger,
            now=datetime(2026, 5, 30, tzinfo=timezone.utc),
        )

        self.assertTrue(result.ready, result.problems)

    def test_rejects_uncited_missing_refs_missing_blockers_and_stale_fixture_claims(self) -> None:
        ledger = {
            "ledger_version": "ppd-readiness-ledger-v1",
            "readiness_rows": [
                {
                    "row_id": "bad-row",
                    "fixture_version_claim": {
                        "fixture_id": "ppd/tests/fixtures/readiness_ledger_v1/bad.json",
                        "fixture_version": "2026-03-01",
                        "freshness_status": "stale",
                        "last_verified_at": "2026-03-01T00:00:00Z",
                    },
                }
            ],
        }

        result = validate_readiness_ledger_v1(
            ledger,
            now=datetime(2026, 5, 30, tzinfo=timezone.utc),
        )

        self.assertFalse(result.ready)
        joined = "\n".join(result.problems)
        self.assertIn("must cite source_evidence_ids or citations", joined)
        self.assertIn("missing readiness packet reference", joined)
        self.assertIn("missing validator reference", joined)
        self.assertIn("must include manual_review_blockers", joined)
        self.assertIn("fixture_version_claim is stale", joined)

    def test_rejects_private_raw_guarantee_and_mutation_content_from_fixture(self) -> None:
        fixture_path = Path(__file__).parent / "fixtures" / "readiness_ledger_v1" / "invalid_readiness_ledger_v1.json"
        ledger = json.loads(fixture_path.read_text(encoding="utf-8"))

        result = validate_readiness_ledger_v1(
            ledger,
            now=datetime(2026, 5, 30, tzinfo=timezone.utc),
        )

        self.assertFalse(result.ready)
        joined = "\n".join(result.problems)
        self.assertIn("private or authenticated artifact", joined)
        self.assertIn("raw crawl, PDF, session, or browser artifact", joined)
        self.assertIn("legal or permitting outcome guarantee", joined)
        self.assertIn("active mutation flag", joined)


if __name__ == "__main__":
    unittest.main()
