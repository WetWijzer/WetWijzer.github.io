"""Source-backed contract for PP&D public archival capability.

The contract is intentionally side-effect-free: it names the implementation
surfaces the daemon must wire together before any live crawl is allowed.
"""

from __future__ import annotations


def archival_contract() -> dict[str, object]:
    return {
        "capability": "whole_site_public_archival",
        "entrypoints": [
            "ppd.crawler.live_public_preflight",
            "ppd.crawler.whole_site_archival",
            "ipfs_datasets_py.processors",
        ],
        "requiredOutputs": [
            "archive_manifest",
            "normalized_document_record",
            "source_evidence_id",
            "requirement_batch",
        ],
        "defaultMode": "fixture_only",
        "liveCrawlAllowedByDefault": False,
    }
