"""PP&D daemon LLM prompt construction."""

from __future__ import annotations

from typing import Any

from ipfs_datasets_py.optimizers.todo_daemon.engine import Task, read_text

from ppd.daemon.failure_policy import (
    effective_prompt_limit,
    format_failure_context,
    recent_task_failures,
    should_use_compact_prompt,
)


def build_prompt(config: Any, selected: Task) -> str:
    failures = recent_task_failures(config, selected.label)
    compact_prompt = should_use_compact_prompt(failures)
    plan = read_text(config.resolve(config.plan_doc), limit=900 if compact_prompt else 22000)
    board = read_text(config.resolve(config.task_board), limit=1800 if compact_prompt else 14000)
    readme = (
        read_text(config.resolve(config.readme), limit=1200 if compact_prompt else 8000)
        if config.resolve(config.readme).exists()
        else ""
    )
    failure_context = format_failure_context(failures)
    context_files: list[str] = []
    if compact_prompt:
        context_files.append(
            "Compact retry mode: omitted broad workspace file contents after repeated LLM parse/runtime failures. "
            "Return a minimal JSON proposal with one fixture and one focused test when possible."
        )
    else:
        for path in sorted((config.repo_root / "ppd").glob("**/*")):
            if not path.is_file():
                continue
            rel = path.relative_to(config.repo_root).as_posix()
            if rel.startswith("ppd/data/") or rel.startswith("ppd/daemon/accepted-work/") or rel.startswith("ppd/daemon/failed-patches/"):
                continue
            if rel.endswith((".py", ".md", ".json", ".ts", ".tsx", ".js", ".mjs")):
                context_files.append(f"--- {rel} ---\n{read_text(path, limit=8000)}")
            if len("\n".join(context_files)) > 18000:
                break

    prompt = f"""
You are improving the isolated PP&D implementation workspace in a repository.

Current task:
{selected.label}

Prompt mode:
{"Compact retry mode: repeated LLM parse/runtime failures were recorded for this task. Return the smallest useful JSON file replacements and avoid broad context." if compact_prompt else "Full context mode."}

Hard constraints:
- Return ONLY one JSON object; no markdown fences and no prose outside JSON.
- Use complete file replacements in a `files` array. Do not return shell commands.
- Edit only files under `ppd/`, or `docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md` if the task specifically requires plan updates.
- Do not edit `src/lib/logic/`, `public/corpus/portland-or/current/`, `ipfs_datasets_py/.daemon/`, or the TypeScript logic daemon ledgers.
- Do not create private DevHub session files, auth state, traces, raw crawl output, or downloaded documents.
- Keep the change narrow and directly useful for the selected task.
- Prefer deterministic fixtures and validation before any live crawl or authenticated automation.
- Before returning JSON, ensure every Python file is syntactically valid Python and every TypeScript file is syntactically valid TypeScript. Do not mix TypeScript syntax into Python or Python typing/control-flow syntax into TypeScript.
- Prefer adding narrow new modules and tests over rewriting stable shared contracts such as `ppd/contracts/documents.py`, unless the selected task directly requires a shared contract extension.
- If recent failure context includes `SyntaxError`, `py_compile`, `TS1005`, `TS1109`, or `TS1128`, return a smaller proposal with only the files needed for a syntax-valid implementation or repair.
- Put committed PP&D fixtures under `ppd/tests/fixtures/...`. Tests in `ppd/tests/` should derive fixture paths from their own file location, for example `Path(__file__).parent / "fixtures" / ...`, so they do not accidentally point at repository-root `tests/fixtures`.
- Do not mark task-board checkboxes complete in the same proposal unless the implementation, fixtures, and validation code for the selected task are all included. The daemon will mark the selected task complete after validation passes.
- Do not automate CAPTCHA, MFA, account creation, payment, submission, certification, cancellation, or upload actions.
- If compact retry mode is active, do not inspect or request additional context. Return the smallest useful JSON file replacements for the current task.

JSON schema:
{{
  "summary": "short summary",
  "impact": "why this advances the PP&D plan",
  "files": [
    {{"path": "ppd/...", "content": "complete replacement file content"}}
  ],
  "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
}}

Recent failure context for this task:
{failure_context}

PP&D plan:
{plan}

PP&D task board:
{board}

PP&D workspace context:
{readme}

Current files:
{chr(10).join(context_files)}
"""
    prompt_limit = effective_prompt_limit(config, compact_prompt=compact_prompt)
    if len(prompt) > prompt_limit:
        prompt = prompt[:prompt_limit] + "\n\n[truncated]\n"
    return prompt
