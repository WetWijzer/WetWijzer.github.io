# Testing and Validation

This repository has two validation surfaces:

1. Frontend (TypeScript/Vite/Jest)
2. PP&D workspace (`ppd/`) deterministic validation

## Frontend commands (run from repository root)

```bash
npm ci --legacy-peer-deps
npm run lint
npm run build
npm test -- --runInBand
```

### What each command covers

- `npm run lint` — ESLint across repository JS/TS sources.
- `npm run build` — TypeScript compile + Vite production bundle.
- `npm test -- --runInBand` — Jest suite (logic engine + app/unit/integration-style tests under `src/`).

## PP&D commands (run from repository root)

```bash
python3 ppd/tests/validate_ppd.py
python3 ppd/daemon/ppd_daemon.py --self-test
python3 ppd/daemon/ppd_supervisor.py --self-test
python3 -m unittest discover -s ppd/tests -p 'test_*.py'
```

`validate_ppd.py` is fixture-only and should not run live crawl/authenticated/submission flows.

## Daemon operational checks

```bash
bash ppd/daemon/control.sh start
bash ppd/daemon/control.sh status
bash ppd/daemon/control.sh stop
bash ppd/daemon/control.sh supervisor-start
bash ppd/daemon/control.sh supervisor-status
bash ppd/daemon/control.sh supervisor-stop
```

## Current baseline notes (this branch)

Recent baseline run in this environment produced:

- `npm run build`: passing
- `npm run lint`: failing due to TSConfig/ESLint project inclusion mismatch for `api/openrouter/chat/completions.js`
- `npm test -- --runInBand`: 3 failing suites, 172 passing suites (`src/lib/logic/cec/parser.test.ts`, `src/lib/chatPromptStarters.test.ts`, `src/lib/logic/fol/expansionRules.test.ts`)
- `python3 ppd/tests/validate_ppd.py`: failing because `ipfs_datasets_py.optimizers` module path is unavailable in this environment

Treat these as baseline status unless/until the underlying code or environment is changed.
