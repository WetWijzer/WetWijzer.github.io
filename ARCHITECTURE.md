# Architecture

This repository has two primary systems:

1. A static, browser-run Portland City Code legal-research application.
2. An isolated PP&D (`ppd/`) automation workspace with a local daemon/supervisor lifecycle.

## 1) Legal Research Frontend (GitHub Pages)

### Runtime profile

- Entry point: `src/main.tsx` → `src/AppStatic.tsx` → `src/components/PortlandLegalResearchApp.tsx`
- Hosting target: static bundle on GitHub Pages
- Core behavior: load prebuilt corpus artifacts from `public/corpus/portland-or/current/` and run retrieval/inference in-browser

### Core data flow

1. `loadPortlandCorpus()` loads manifest + sections (`src/lib/portlandCorpus.ts`).
2. Hybrid retrieval combines BM25 and vector search (`searchCorpus`).
3. Graph context is loaded from precomputed entities/relationships/adjacency JSON.
4. GraphRAG answer generation runs through `answerWithGraphRag()` (`src/lib/portlandGraphRag.ts`):
   - retrieves evidence
   - enriches with logic evidence
   - attempts local/browser generation first
   - falls back to cloud proxy or evidence-only summaries when needed

### Browser worker layer

- Embedding worker service: `src/lib/clientEmbeddingWorkerService.ts`
- LLM worker service: `src/lib/clientLLMWorkerService.ts`
- Worker implementation: `src/workers/clientLLMWorker.ts`

Workers isolate model/inference workloads from the UI thread and expose structured readiness/fallback status.

### Logic engine layer

- TypeScript logic modules under `src/lib/logic/`
- Includes FOL, deontic, TDFOL, CEC/DCEC, F-logic, and ZKP-related modules
- Used both for UI proof exploration and for parity/security/testing workflows

## 2) PP&D Automation Workspace (`ppd/`)

### Scope boundary

The PP&D system is intentionally separated from the legal corpus/frontend and keeps automation state/code under `ppd/`.

Primary references:

- Workspace overview: `ppd/README.md`
- Daemon operations: `ppd/daemon/OPERATIONS.md`
- Plan/requirements: `docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md`

### Daemon architecture

- Daemon worker: `ppd/daemon/ppd_daemon.py`
- Supervisor: `ppd/daemon/ppd_supervisor.py`
- Control wrapper: `ppd/daemon/control.sh`
- Task source: `ppd/daemon/task-board.md`

Execution model:

1. Select one narrow task-board item.
2. Generate JSON file-replacement proposals (no command execution from model output).
3. Validate in isolated temporary PP&D worktrees.
4. Promote only validated replacements.
5. Persist accepted/failed evidence under `ppd/daemon/` ledgers.

### Safety constraints

The PP&D validation/daemon flow is fixture-first and deterministic by design. It must not perform live submission/payment/certification/scheduling actions. Authenticated portal interactions are guarded and explicitly separated from unsafe autonomous actions.

## Build and deployment architecture

- Workflow: `.github/workflows/deploy.yml`
- Build job runs:
  - `npm ci --legacy-peer-deps`
  - `npx tsc --noEmit`
  - `npx vite build`
- Output: static `dist/` artifact published to GitHub Pages

## Key directories

- `src/` — frontend app, UI components, browser logic engine, tests
- `public/corpus/portland-or/current/generated/` — prebuilt corpus/search/graph/proof assets
- `ppd/` — PP&D daemon/crawler/devhub/contracts/tests/operations
- `docs/` — implementation plans and parity/roadmap notes
