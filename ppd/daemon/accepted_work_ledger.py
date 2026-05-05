"""Compatibility wrapper for PP&D accepted-work ledger helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Iterable, Optional

_IPFS_DATASETS_SUBMODULE = Path(__file__).resolve().parents[2] / "ipfs_datasets_py"
if _IPFS_DATASETS_SUBMODULE.exists() and str(_IPFS_DATASETS_SUBMODULE) not in sys.path:
    sys.path.insert(0, str(_IPFS_DATASETS_SUBMODULE))

from ipfs_datasets_py.optimizers.todo_daemon.artifacts import (
    ACCEPTED_WORK_LEDGER_SCHEMA_VERSION,
    DEFAULT_ACCEPTED_WORK_LEDGER_FILENAME,
    WorkSidecarPaths,
    append_jsonl_ledger,
    build_accepted_work_ledger_entry as build_todo_accepted_work_ledger_entry,
)


LEDGER_FILENAME = DEFAULT_ACCEPTED_WORK_LEDGER_FILENAME
SCHEMA_VERSION = ACCEPTED_WORK_LEDGER_SCHEMA_VERSION
AcceptedWorkArtifacts = WorkSidecarPaths


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
    """Build a PP&D accepted-work ledger entry using shared todo-daemon logic."""

    return build_todo_accepted_work_ledger_entry(
        repo_root=repo_root,
        target_task=target_task,
        summary=summary,
        impact=impact,
        changed_files=changed_files,
        transport=transport,
        artifacts=artifacts,
        validation_results=validation_results,
        diff_text=diff_text,
        promotion_verified=promotion_verified,
        promotion_errors=promotion_errors,
        ledger_path=ledger_path or repo_root / "ppd/daemon/accepted-work" / LEDGER_FILENAME,
        created_at=created_at,
        ledger_filename=LEDGER_FILENAME,
    )


def append_accepted_work_ledger(accepted_dir: Path, entry: dict[str, Any]) -> Path:
    """Append one JSON object to the PP&D accepted-work ledger."""

    return append_jsonl_ledger(accepted_dir, entry, filename=LEDGER_FILENAME)
