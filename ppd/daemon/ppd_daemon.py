#!/usr/bin/env python3
"""Autonomous PP&D implementation daemon.

This daemon borrows the safe operating pattern from the TypeScript logic-port
daemon, but keeps all PP&D work in the isolated ``ppd/`` workspace.

It accepts model output only as JSON file replacements and never executes
commands returned by the model.
"""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Optional
from urllib.parse import urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
_IPFS_DATASETS_SUBMODULE = Path(__file__).resolve().parents[2] / "ipfs_datasets_py"
if _IPFS_DATASETS_SUBMODULE.exists() and str(_IPFS_DATASETS_SUBMODULE) not in sys.path:
    sys.path.insert(0, str(_IPFS_DATASETS_SUBMODULE))
_IPFS_DATASETS_PACKAGE = _IPFS_DATASETS_SUBMODULE / "ipfs_datasets_py"
_CACHED_IPFS_PACKAGE = sys.modules.get("ipfs_datasets_py")
if (
    _CACHED_IPFS_PACKAGE is not None
    and getattr(_CACHED_IPFS_PACKAGE, "__file__", None) is None
    and _IPFS_DATASETS_PACKAGE.exists()
):
    sys.modules.pop("ipfs_datasets_py", None)

from ppd.daemon.syntax_preflight import run_apply_flow_syntax_preflight
from ppd.daemon.deterministic_fallback import (  # noqa: E402
    build_deterministic_task_fallback_proposal as build_ppd_deterministic_task_fallback_proposal,
    DETERMINISTIC_FALLBACK_VALIDATION_COMMANDS,
    DETERMINISTIC_PLATFORM_INIT,
    DETERMINISTIC_PROGRESS_SOURCE_PATH,
    DETERMINISTIC_SOURCE_FILES,
    DETERMINISTIC_TASK_FALLBACK_TITLES,
    DETERMINISTIC_TASK_SOURCE_EVIDENCE_IDS,
    compact_deterministic_progress_source_payload,
    deterministic_artifact_contracts,
    deterministic_progress_manifest,
    deterministic_progress_record,
    deterministic_progress_source_content,
    deterministic_task_fallback_kind,
    has_deterministic_task_fallback,
    has_open_deterministic_task_fallback,
)
from ppd.daemon.failure_policy import (  # noqa: E402
    FORBIDDEN_ABSENCE_MARKERS,
    LLM_TERMINATION_ERROR_MARKERS,
    PreLlmBlockDecision,
    effective_prompt_limit,
    exception_diagnostic,
    failure_block_threshold,
    format_failure_context,
    is_forbidden_absence_marker_validation_failure,
    is_llm_termination_failure_record,
    is_retryable_failure,
    llm_termination_failure_count,
    pre_llm_block_decision,
    read_result_and_diagnostic_log,
    read_result_log,
    recent_task_failures,
    should_block_task_before_llm,
    should_skip_validation_for_no_file_failure,
    should_use_compact_prompt,
    task_failure_count,
)
from ppd.daemon.path_policy import (  # noqa: E402
    ALLOWED_WRITE_PREFIXES,
    DISALLOWED_WRITE_PREFIXES,
    PPD_PATH_POLICY,
    PRIVATE_WRITE_PATH_FRAGMENTS,
    PRIVATE_WRITE_PATH_TOKENS,
    RUNTIME_ONLY_CHANGE_PATHS,
    has_visible_source_change,
    is_private_write_path,
    validate_write_path,
)
from ppd.daemon.prompt_builder import build_prompt  # noqa: E402
from ppd.daemon.task_board import (  # noqa: E402
    CHECKBOX_RE,
    PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS,
    TASK_BOARD_STATUS_END,
    TASK_BOARD_STATUS_START,
    count_unmanaged_generated_status_sections,
    parse_tasks,
    replace_task_mark,
    select_task,
    select_task_for_config,
    should_sleep_between_watch_cycles,
    strip_unmanaged_generated_status_sections,
    update_generated_status,
)
from ipfs_datasets_py.optimizers.todo_daemon.engine import (  # noqa: E402
    CommandResult,
    Proposal,
    Task,
    append_jsonl,
    atomic_write_json,
    command_results_from_objects,
    compact_message,
    cleanup_stale_config_validation_worktrees,
    config_validation_commands_for_proposal,
    dataclass_worktree_config,
    diff_for_file as todo_diff_for_file,
    extract_json as todo_extract_json,
    normalized_relative_path as todo_normalized_relative_path,
    parse_json_proposal,
    read_text,
    run_config_validation_commands,
    run_command as todo_run_command,
    temporary_config_validation_worktree,
    utc_now,
    worktree_marker_payload as todo_worktree_marker_payload,
)
from ipfs_datasets_py.optimizers.todo_daemon.artifacts import (  # noqa: E402
    DEFAULT_ACCEPTED_WORK_LEDGER_FILENAME as LEDGER_FILENAME,
    WorkSidecarPaths as AcceptedWorkArtifacts,
)
from ipfs_datasets_py.optimizers.todo_daemon.file_replacement import (  # noqa: E402
    FileReplacementHooks,
    FileReplacementTodoDaemonRunner,
    attempt_file_replacement_validation_repair,
    build_config_file_replacement_hooks,
    build_file_replacement_apply_proposal,
    build_file_replacement_validation_repair_prompt,
    config_persist_accepted_file_replacement_work,
    config_persist_failed_file_replacement_work,
    config_promote_worktree_files,
)
from ipfs_datasets_py.optimizers.todo_daemon.app import (  # noqa: E402
    print_todo_daemon_result,
    run_todo_daemon,
    todo_daemon_exit_code,
)
from ipfs_datasets_py.optimizers.todo_daemon.runner import (  # noqa: E402
    PreTaskBlock,
    TodoDaemonHooks,
)
from ipfs_datasets_py.optimizers.todo_daemon.llm import (  # noqa: E402
    LlmRouterInvocation,
    call_llm_router,
    collect_descendant_pids,
    install_active_llm_signal_handlers,
    process_groups_for_family,
    terminate_process_group,
)


DEFAULT_VALIDATION_COMMANDS = (
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
    ("python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"),
    (
        "bash",
        "-lc",
        "files=$(find ppd -name '*.ts' -not -path '*/node_modules/*' -print); "
        "test -z \"$files\" || npx tsc --noEmit --target ES2020 --module ESNext "
        "--moduleResolution node --strict --skipLibCheck --types node $files",
    ),
)

@dataclass
class Config:
    repo_root: Path
    task_board: Path = Path("ppd/daemon/task-board.md")
    plan_doc: Path = Path("docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md")
    readme: Path = Path("ppd/README.md")
    status_file: Path = Path("ppd/daemon/status.json")
    progress_file: Path = Path("ppd/daemon/progress.json")
    deterministic_progress_file: Path = Path("ppd/daemon/deterministic-progress.json")
    result_log: Path = Path("ppd/daemon/ppd-daemon.jsonl")
    accepted_dir: Path = Path("ppd/daemon/accepted-work")
    failed_dir: Path = Path("ppd/daemon/failed-patches")
    worktree_dir: Path = Path("ppd/daemon/worktrees")
    model_name: str = "gpt-5.5"
    provider: Optional[str] = None
    apply: bool = False
    watch: bool = False
    iterations: int = 1
    interval_seconds: float = 0.0
    heartbeat_seconds: float = 30.0
    command_timeout_seconds: int = 300
    llm_timeout_seconds: int = 300
    max_prompt_chars: int = 60000
    max_compact_prompt_chars: int = 4200
    llm_max_new_tokens: int = 2048
    allow_local_fallback: bool = False
    revisit_blocked: bool = False
    max_task_failures_before_block: int = 3
    repair_validation_failures: bool = False
    max_validation_repair_attempts: int = 1
    write_accepted_work_sidecars: bool = False
    worktree_stale_seconds: int = 7200
    crash_backoff_seconds: float = 5.0
    validation_repair_callback: Optional[Callable[[str, "Config"], str]] = None
    validation_commands: tuple[tuple[str, ...], ...] = DEFAULT_VALIDATION_COMMANDS

    def resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self.repo_root / path


def build_deterministic_task_fallback_proposal(config: Config, selected: Task) -> Optional[Proposal]:
    return build_ppd_deterministic_task_fallback_proposal(
        config,
        selected,
        default_validation_commands=DEFAULT_VALIDATION_COMMANDS,
    )

extract_json = todo_extract_json
parse_proposal = parse_json_proposal
normalized_relative_path = todo_normalized_relative_path
run_command = todo_run_command


def validation_commands_for_proposal(proposal: Proposal, config: Config) -> tuple[tuple[str, ...], ...]:
    return config_validation_commands_for_proposal(proposal, config)


def run_validation(
    config: Config,
    commands: Optional[tuple[tuple[str, ...], ...]] = None,
) -> list[CommandResult]:
    return run_config_validation_commands(
        config,
        commands=commands,
        run_command_fn=run_command,
    )


diff_for_file = todo_diff_for_file
worktree_marker_payload = todo_worktree_marker_payload


def cleanup_stale_validation_worktrees(config: Config, *, max_age_seconds: Optional[int] = None) -> list[str]:
    """Remove old PP&D validation worktrees left by interrupted daemon runs."""

    return cleanup_stale_config_validation_worktrees(
        config,
        marker_name="ppd-worktree.json",
        max_age_seconds=max_age_seconds,
    )


def _ignore_validation_tree_entries(directory: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}
    path = Path(directory)
    if path.name == "daemon":
        ignored.update({"worktrees", "failed-patches", "accepted-work"})
        ignored.update(name for name in names if name.endswith(".pid") or name.endswith(".out") or name.endswith(".jsonl"))
        ignored.update({"status.json", "progress.json", "supervisor-status.json", "supervisor-actions.jsonl"})
    return {name for name in names if name in ignored}


def temporary_validation_worktree(config: Config):
    """Create an isolated PP&D validation tree and remove it after the cycle."""

    return temporary_config_validation_worktree(
        config,
        marker_name="ppd-worktree.json",
        copy_paths=(Path("ppd"), config.plan_doc),
        root_files=("package.json", "package-lock.json", "tsconfig.json"),
        external_reference_paths=(Path("ipfs_datasets_py/ipfs_datasets_py"),),
        ignore=_ignore_validation_tree_entries,
    )


def validation_results_from_syntax_preflight(worktree: Path, changed: list[str], config: Config) -> tuple[list[CommandResult], list[str], str]:
    syntax_preflight = run_apply_flow_syntax_preflight(
        worktree,
        changed,
        timeout=config.command_timeout_seconds,
    )
    results = command_results_from_objects(syntax_preflight.validation_results)
    return results, list(syntax_preflight.errors), syntax_preflight.failure_kind


def promote_worktree_files(config: Config, worktree: Path, changed: Iterable[str]) -> None:
    """Promote accepted worktree files; kept as a PP&D test/extension hook."""

    config_promote_worktree_files(config, worktree, changed)


def validation_repair_worktree_config(config: Config, worktree: Path) -> Config:
    return dataclass_worktree_config(
        config,
        worktree,
        repair_validation_failures=False,
        validation_repair_callback=None,
    )


def build_validation_repair_prompt(proposal: Proposal, config: Config) -> str:
    return build_file_replacement_validation_repair_prompt(
        proposal,
        subject="PP&D daemon candidate",
        repair_rules=(
            "Edit only files under ppd/ or docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md.",
            "Keep the repair smaller than the failed candidate when possible.",
            "Do not create private DevHub artifacts, raw crawl output, downloaded documents, browser traces, screenshots, credentials, or payment data.",
        ),
        response_shape='{"summary":"short repair summary","impact":"why this fixes validation","files":[{"path":"ppd/...","content":"complete replacement"}]}',
    )


def call_validation_repair_llm(prompt: str, config: Config) -> str:
    if config.validation_repair_callback is not None:
        return config.validation_repair_callback(prompt, config)
    return call_llm(prompt, config)


def attempt_validation_repair_pass(
    proposal: Proposal,
    config: Config,
    worktree: Path,
) -> tuple[bool, list[str], str]:
    return attempt_file_replacement_validation_repair(
        proposal,
        config,
        worktree,
        enabled=config.repair_validation_failures,
        max_attempts=config.max_validation_repair_attempts,
        build_prompt=build_validation_repair_prompt,
        call_repair_model=call_validation_repair_llm,
        parse_repair=parse_proposal,
        validate_write_path=validate_write_path,
        syntax_preflight=validation_results_from_syntax_preflight,
        run_validation=run_validation,
        validation_commands_for_proposal=validation_commands_for_proposal,
        worktree_config=validation_repair_worktree_config,
    )


def ppd_file_replacement_hooks() -> FileReplacementHooks:
    return build_config_file_replacement_hooks(
        validate_write_path=validate_write_path,
        temporary_validation_worktree=temporary_validation_worktree,
        validation_commands_for_proposal=validation_commands_for_proposal,
        run_validation=run_validation,
        syntax_preflight=validation_results_from_syntax_preflight,
        has_visible_source_change=has_visible_source_change,
        attempt_validation_repair=attempt_validation_repair_pass,
        promote_worktree_files=promote_worktree_files,
        accepted_dir_field="accepted_dir",
        failed_dir_field="failed_dir",
        sidecars_enabled_field="write_accepted_work_sidecars",
        no_visible_source_change_message=(
            "Accepted work must promote at least one visible PP&D source or fixture file; "
            "runtime-only progress records are not sufficient."
        ),
    )


def apply_files_with_validation(proposal: Proposal, config: Config) -> Proposal:
    return build_file_replacement_apply_proposal(ppd_file_replacement_hooks())(proposal, config)


def persist_accepted_work(proposal: Proposal, config: Config, *, diff_text: str, transport: str = "direct") -> None:
    config_persist_accepted_file_replacement_work(
        proposal,
        config,
        diff_text,
        transport,
        accepted_dir_field="accepted_dir",
        sidecars_enabled_field="write_accepted_work_sidecars",
    )


def persist_failed_work(proposal: Proposal, config: Config, *, diff_text: str, reason: str, transport: str = "direct") -> None:
    config_persist_failed_file_replacement_work(
        proposal,
        config,
        diff_text,
        reason,
        transport,
        failed_dir_field="failed_dir",
    )


def call_llm(prompt: str, config: Config) -> str:
    return call_llm_router(
        prompt,
        LlmRouterInvocation(
            repo_root=config.repo_root,
            model_name=config.model_name,
            provider=config.provider,
            allow_local_fallback=config.allow_local_fallback,
            timeout_seconds=config.llm_timeout_seconds,
            max_new_tokens=config.llm_max_new_tokens,
            max_prompt_chars=config.max_prompt_chars,
            backend_env_name="PPD_LLM_BACKEND",
            backend_label="PP&D LLM backend",
            env_prefix="PPD_LLM",
            prompt_file_prefix="ppd-llm-prompt-",
        ),
    )


def install_daemon_signal_handlers() -> None:
    install_active_llm_signal_handlers()


def ppd_pre_task_block(config: Config, selected: Task) -> Optional[PreTaskBlock]:
    deterministic_fallback_available = has_deterministic_task_fallback(selected)
    if not (
        config.apply
        and selected.status in {"needed", "in-progress"}
        and not deterministic_fallback_available
    ):
        return None
    decision = pre_llm_block_decision(config, selected.label)
    if decision is None:
        return None
    return PreTaskBlock(
        summary=decision.summary,
        failure_kind=decision.failure_kind,
        result=decision.result,
    )


def ppd_produce_proposal(config: Config, selected: Task, write_status: Any) -> Proposal:
    proposal = build_deterministic_task_fallback_proposal(config, selected)
    if proposal is not None:
        write_status("deterministic_fallback", target_task=selected.label)
        return proposal
    write_status("calling_llm", target_task=selected.label)
    try:
        raw = call_llm(build_prompt(config, selected), config)
        return parse_proposal(raw)
    except KeyboardInterrupt:
        raise
    except BaseException as exc:
        return Proposal(summary="LLM proposal failed.", errors=[compact_message(exc)], failure_kind="llm")


def ppd_run_proposal_validation(config: Config, proposal: Proposal) -> list[CommandResult]:
    return run_validation(
        config,
        commands=validation_commands_for_proposal(proposal, config),
    )


def ppd_failure_count_for_block(config: Config, task_label: str) -> int:
    return task_failure_count(
        config,
        task_label,
        kinds={"validation", "preflight", "no_change", "syntax_preflight"},
    )


def build_ppd_daemon_hooks() -> TodoDaemonHooks:
    return TodoDaemonHooks(
        parse_tasks=parse_tasks,
        select_task=lambda tasks, config: select_task_for_config(tasks, config),
        replace_task_mark=replace_task_mark,
        update_generated_status=lambda markdown, latest, tasks: update_generated_status(
            markdown,
            latest=latest,
            tasks=tasks,
        ),
        produce_proposal=ppd_produce_proposal,
        apply_proposal=apply_files_with_validation,
        run_validation=ppd_run_proposal_validation,
        should_skip_validation=should_skip_validation_for_no_file_failure,
        is_retryable_failure=is_retryable_failure,
        failure_block_threshold=failure_block_threshold,
        failure_count_for_block=ppd_failure_count_for_block,
        should_sleep_between_cycles=lambda markdown, config: should_sleep_between_watch_cycles(
            markdown,
            revisit_blocked=config.revisit_blocked,
        ),
        exception_diagnostic=exception_diagnostic,
        pre_task_block=ppd_pre_task_block,
        no_eligible_summary="No eligible PP&D tasks remain.",
    )


def ppd_file_replacement_runner(config: Config) -> FileReplacementTodoDaemonRunner:
    return FileReplacementTodoDaemonRunner(
        config,
        build_ppd_daemon_hooks(),
        ppd_file_replacement_hooks(),
    )


class Daemon(FileReplacementTodoDaemonRunner):
    def __init__(self, config: Config) -> None:
        super().__init__(
            config,
            build_ppd_daemon_hooks(),
            ppd_file_replacement_hooks(),
        )


def self_test(repo_root: Path) -> int:
    required = [
        repo_root / "ppd/README.md",
        repo_root / "ppd/.gitignore",
        repo_root / "ppd/daemon/task-board.md",
        repo_root / "docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md",
    ]
    missing = [path.as_posix() for path in required if not path.exists()]
    errors: list[str] = []
    if missing:
        errors.append(f"missing required files: {missing}")
    board = (repo_root / "ppd/daemon/task-board.md").read_text(encoding="utf-8") if (repo_root / "ppd/daemon/task-board.md").exists() else ""
    if not parse_tasks(board):
        errors.append("task board has no checkbox tasks")
    gitignore = (repo_root / "ppd/.gitignore").read_text(encoding="utf-8") if (repo_root / "ppd/.gitignore").exists() else ""
    for needle in ("data/private/", "data/raw/", "daemon/failed-patches/", "daemon/worktrees/"):
        if needle not in gitignore:
            errors.append(f"ppd/.gitignore missing {needle}")
    for prefix in DISALLOWED_WRITE_PREFIXES:
        if not validate_write_path(prefix + "bad.ts"):
            errors.append(f"disallowed prefix unexpectedly passed preflight: {prefix}")
    compacted = CommandResult(
        command=("example",),
        returncode=1,
        stdout="<html><body><script>cloudflare challenge</script></body></html>",
        stderr="token __cf_chl_tk=secret",
    ).compact()
    if "cloudflare challenge" in compacted["stdout"] or "__cf_chl_tk=secret" in compacted["stderr"]:
        errors.append("runtime log compaction failed to redact noisy provider HTML")
    errors.extend(validate_seed_and_allowlist(repo_root))
    errors.extend(validate_python_sources(repo_root))
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "task_count": len(parse_tasks(board))}, indent=2))
    return 0


def load_json_file(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.relative_to(path.parents[2])} is invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return parsed


def validate_seed_and_allowlist(repo_root: Path) -> list[str]:
    errors: list[str] = []
    seed_path = repo_root / "ppd/crawler/seed_manifest.json"
    allowlist_path = repo_root / "ppd/crawler/allowlist.json"
    try:
        seed_manifest = load_json_file(seed_path)
        allowlist = load_json_file(allowlist_path)
    except ValueError as exc:
        return [str(exc)]
    if seed_manifest is None and allowlist is None:
        return errors
    if seed_manifest is None or allowlist is None:
        return ["seed_manifest.json and allowlist.json must be added together"]

    allowed_hosts = allowlist.get("allowed_hosts")
    if not isinstance(allowed_hosts, list) or not allowed_hosts:
        errors.append("allowlist.json must include non-empty allowed_hosts")
        allowed_hosts = []
    host_policies: dict[str, dict[str, Any]] = {}
    for entry in allowed_hosts:
        if not isinstance(entry, dict):
            errors.append("allowlist allowed_hosts entries must be objects")
            continue
        host = entry.get("host")
        if not isinstance(host, str) or not host:
            errors.append("allowlist host entry missing host")
            continue
        host_policies[host] = entry
        if entry.get("scheme") != "https":
            errors.append(f"allowlist host {host} must require https")
        prefixes = entry.get("allowed_path_prefixes")
        if not isinstance(prefixes, list) or not all(isinstance(prefix, str) and prefix.startswith("/") for prefix in prefixes):
            errors.append(f"allowlist host {host} must define allowed_path_prefixes")

    seeds = seed_manifest.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        errors.append("seed_manifest.json must include non-empty seeds")
        seeds = []
    seen_ids: set[str] = set()
    for seed in seeds:
        if not isinstance(seed, dict):
            errors.append("seed entries must be objects")
            continue
        seed_id = seed.get("id")
        url = seed.get("url")
        if not isinstance(seed_id, str) or not seed_id:
            errors.append("seed entry missing id")
        elif seed_id in seen_ids:
            errors.append(f"duplicate seed id: {seed_id}")
        else:
            seen_ids.add(seed_id)
        if not isinstance(url, str) or not url:
            errors.append(f"seed {seed_id or '<unknown>'} missing url")
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https":
            errors.append(f"seed {seed_id} must use https: {url}")
        policy = host_policies.get(parsed.netloc)
        if policy is None:
            errors.append(f"seed {seed_id} host is not allowlisted: {parsed.netloc}")
            continue
        prefixes = policy.get("allowed_path_prefixes", [])
        parsed_path = parsed.path or "/"
        if isinstance(prefixes, list) and not any(parsed_path.startswith(str(prefix)) for prefix in prefixes):
            errors.append(f"seed {seed_id} path is outside host allowlist: {parsed_path}")
        for fragment in policy.get("disallowed_path_fragments", []) or []:
            if isinstance(fragment, str) and fragment.lower() in url.lower():
                errors.append(f"seed {seed_id} includes disallowed path fragment {fragment!r}")
    return errors


def validate_python_sources(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((repo_root / "ppd").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(repo_root).as_posix()
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{rel} failed py_compile: {compact_message(exc.msg, limit=500)}")
    return errors


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the isolated PP&D autonomous daemon.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--apply", action="store_true", help="Apply accepted file replacements after validation")
    parser.add_argument("--watch", action="store_true", help="Run repeated cycles")
    parser.add_argument("--iterations", type=int, default=1, help="Number of cycles; with --watch, 0 means unbounded")
    parser.add_argument("--interval", type=float, default=0.0, help="Seconds between watch cycles")
    parser.add_argument("--llm-timeout", type=int, default=300, help="Seconds to allow for one LLM proposal")
    parser.add_argument("--llm-max-new-tokens", type=int, default=2048, help="llm_router max_new_tokens budget")
    parser.add_argument("--max-prompt-chars", type=int, default=60000, help="Maximum prompt characters before llm_router launch")
    parser.add_argument("--max-compact-prompt-chars", type=int, default=4200, help="Maximum compact retry prompt characters")
    parser.add_argument("--model", default="gpt-5.5", help="llm_router model")
    parser.add_argument("--provider", default=None, help="llm_router provider")
    parser.add_argument("--allow-local-fallback", action="store_true", help="Allow local fallback providers")
    parser.add_argument("--revisit-blocked", action="store_true", help="Revisit blocked tasks after needed tasks are exhausted")
    parser.add_argument("--max-task-failures-before-block", type=int, default=3, help="Validation/preflight failures before marking a task blocked")
    parser.add_argument("--repair-validation-failures", action="store_true", help="Run one temporary-worktree repair pass when validation fails")
    parser.add_argument("--max-validation-repair-attempts", type=int, default=1, help="Validation repair attempts per candidate worktree")
    parser.add_argument("--crash-backoff", type=float, default=5.0, help="Seconds to pause after a contained daemon cycle exception")
    parser.add_argument("--self-test", action="store_true", help="Run daemon self-test and exit")
    return parser.parse_args(argv)


def config_from_args(args: argparse.Namespace) -> Config:
    """Build PP&D daemon config from CLI args while keeping runner startup reusable."""

    return Config(
        repo_root=Path(args.repo_root).resolve(),
        apply=bool(args.apply),
        watch=bool(args.watch),
        iterations=int(args.iterations),
        interval_seconds=float(args.interval),
        llm_timeout_seconds=int(args.llm_timeout),
        llm_max_new_tokens=max(256, int(args.llm_max_new_tokens)),
        max_prompt_chars=max(1000, int(args.max_prompt_chars)),
        max_compact_prompt_chars=max(1000, int(args.max_compact_prompt_chars)),
        model_name=str(args.model),
        provider=args.provider,
        allow_local_fallback=bool(args.allow_local_fallback),
        revisit_blocked=bool(args.revisit_blocked),
        max_task_failures_before_block=max(1, int(args.max_task_failures_before_block)),
        repair_validation_failures=bool(args.repair_validation_failures),
        max_validation_repair_attempts=max(0, int(args.max_validation_repair_attempts)),
        crash_backoff_seconds=max(0.0, float(args.crash_backoff)),
    )


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.self_test:
        return self_test(repo_root)
    install_daemon_signal_handlers()
    config = config_from_args(args)
    proposals = run_todo_daemon(config, runner_factory=ppd_file_replacement_runner)
    print_todo_daemon_result(proposals, output="proposals")
    return todo_daemon_exit_code(proposals)


if __name__ == "__main__":
    raise SystemExit(main())
