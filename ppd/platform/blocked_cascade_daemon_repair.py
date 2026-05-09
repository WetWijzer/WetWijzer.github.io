"""Deterministic PP&D contract for blocked_cascade_daemon_repair.

This module is source-backed evidence for a reopened comprehensive PP&D goal
task. It is intentionally side-effect-free and does not perform live DevHub,
official action, upload, payment, or real PDF filling work.
"""

from __future__ import annotations

import json
from typing import Any


CONTRACT_JSON = '{\n  "capability": "blocked_cascade_daemon_repair",\n  "defaultMode": "fixture_only",\n  "exactConfirmationBeforeOfficialAction": true,\n  "fallbackKind": "blocked_cascade_daemon_repair",\n  "liveCrawlAllowedByDefault": false,\n  "officialDevhubActionAllowedByDefault": false,\n  "privateArtifactPersistence": "forbidden",\n  "requiredOutputs": [\n    "blocked_task_quarantine",\n    "fresh_repair_validation",\n    "llm_termination_storm_guard"\n  ],\n  "requiresHumanAttendanceBeforeBrowserUse": true,\n  "schemaVersion": 1,\n  "surfaces": [\n    "blocked_domain_backlog",\n    "generated_repair_tranche",\n    "supervisor_retry_policy"\n  ]\n}'


def contract() -> dict[str, Any]:
    return json.loads(CONTRACT_JSON)
