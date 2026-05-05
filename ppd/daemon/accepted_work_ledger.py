"""Append-only accepted-work ledger support for the PP&D daemon.

The daemon keeps accepted-work evidence compact by default. Older runs wrote a
manifest, workspace record, diff, and stat file for every accepted task; new
runs write one JSONL ledger entry per accepted task and store only compact
digests plus promotion status unless an operator explicitly enables sidecars.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


LEDGER_FILENAME = "accepted-work.jsonl"
SCHEMA_VERSION = 2


@dataclass(frozen=True)
class AcceptedWorkArtifacts:
    manifest: Path
    workspace: Path
    diff: Path
    stat: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_repo_path(path: Path, repo_root: Path) -> str:
    resolved_root = repo_root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return path.as_posix()


def _compact_validation_result(result: dict[str, Any]) -> dict[str, Any]:
    command = result.get("command", [])
    if not isinstance(command, list):
        command = []
    returncode = result.get("returncode", 0)
    try:
        returncode = int(returncode)
    except (TypeError, ValueError):
        returncode = 1
    return {
        "command": [str(part) for part in command],
        "returncode": returncode,
    }


def build_accepted_work_ledger_entry(
    *,
    repo_root: Path,
    target_task: str,
    summary: str,
    impact: str,
    changed_files: Iterable[str],
    transport: str,
    artifacts: Optional[AcceptedWorkArtifacts],
    validation_results: Iterable[dict[str, Any]],
    diff_text: str = "",
    promotion_verified: bool = False,
    promotion_errors: Optional[Iterable[str]] = None,
    ledger_path: Optional[Path] = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a stable accepted-work ledger entry.

    The ledger intentionally stores artifact paths and validation command status,
    not raw crawl output, auth state, or downloaded source content.
    """

    compact_results = [_compact_validation_result(result) for result in validation_results]
    if artifacts is None:
        artifact_payload = {
            "mode": "ledger_only",
            "ledger": _as_repo_path(ledger_path or repo_root / "ppd/daemon/accepted-work" / LEDGER_FILENAME, repo_root),
        }
    else:
        artifact_payload = {
            "mode": "sidecars",
            "manifest": _as_repo_path(artifacts.manifest, repo_root),
            "workspace": _as_repo_path(artifacts.workspace, repo_root),
            "diff": _as_repo_path(artifacts.diff, repo_root),
            "stat": _as_repo_path(artifacts.stat, repo_root),
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": created_at or utc_now(),
        "target_task": str(target_task),
        "summary": str(summary),
        "impact": str(impact),
        "changed_files": sorted(str(path) for path in changed_files),
        "transport": str(transport),
        "artifacts": artifact_payload,
        "diff": {
            "sha256": hashlib.sha256(diff_text.encode("utf-8")).hexdigest(),
            "line_count": len(diff_text.splitlines()),
        },
        "promotion": {
            "verified": bool(promotion_verified),
            "errors": [str(error) for error in (promotion_errors or [])],
        },
        "validation_results": compact_results,
        "validation_passed": bool(compact_results) and all(result["returncode"] == 0 for result in compact_results),
    }


def append_accepted_work_ledger(accepted_dir: Path, entry: dict[str, Any]) -> Path:
    """Append one JSON object to the PP&D accepted-work ledger."""

    accepted_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = accepted_dir / LEDGER_FILENAME
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return ledger_path
