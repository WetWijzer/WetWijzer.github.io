# Portland City Code Legal Research

[Live Site](https://portland-laws.github.io)

This repository has two active workstreams:

1. A static, browser-only research tool for exploring and querying the **Portland, Oregon City Code**.
2. An isolated **PP&D automation workspace** (`ppd/`) with a local daemon/supervisor stack for Portland Permitting & Development process extraction, guarded DevHub login automation, and permit-filing workflow support.

The legal-research app runs fully in the browser (no backend server required for core corpus search), while PP&D automation is intentionally constrained to the `ppd/` workspace and deterministic validation.

## What This Is

This repository is a static Vite/React/TypeScript application that provides:

- **Corpus Browser**: Browse all 3,052 sections of the Portland City Code organized by Title and Chapter
- **Hybrid Search**: Combine keyword (BM25), vector similarity, and knowledge-graph-expanded search in one query
- **GraphRAG Chat**: Ask plain-language questions and receive citation-grounded answers generated entirely in-browser
- **Knowledge Graph Explorer**: Visualize entities and relationships extracted from the legal corpus
- **Logic Proof Explorer**: Inspect formal logic artifacts (obligations, permissions, prohibitions, temporal operators, ZKP certificates) derived from each section
- **Browser Logic Engine**: A growing TypeScript/WASM port of the Python `ipfs_datasets_py` logic module, enabling deterministic browser-native theorem proving, TDFOL/CEC/DCEC parsing, deontic analysis, F-logic rendering, and ZKP metadata verification

## PP&D Agent Daemon Workspace

The `ppd/` workspace contains automation code for Portland Permitting & Development operations. It includes:

- **Daemon worker** (`ppd/daemon/ppd_daemon.py`) that advances one task-board item at a time using JSON file-replacement proposals.
- **Watchdog + control wrapper** (`ppd/daemon/control.sh`) for `start`, `stop`, `status`, `logs`, and supervisor controls.
- **Supervisor** (`ppd/daemon/ppd_supervisor.py`) that can restart/recover the daemon and run narrow repair cycles.
- **DevHub automation scaffolding** (`ppd/devhub/`) for authenticated portal login/session flows and guarded permit-related action support.
- **Fixture-first validation** (`python3 ppd/tests/validate_ppd.py`) that must remain deterministic and avoid live submission/payment actions.

Start/inspect locally from repository root:

```bash
bash ppd/daemon/control.sh start
bash ppd/daemon/control.sh status
bash ppd/daemon/control.sh supervisor-status
```

## Corpus

The corpus is sourced from the Hugging Face dataset [`justicedao/american_municipal_law`](https://huggingface.co/datasets/justicedao/american_municipal_law), specifically the Portland, OR current-code artifacts:

- **3,052 canonical sections** with full text, Bluebook citations, source URLs, and JSON-LD metadata
- **BM25 precomputed term frequencies** for fast keyword search
- **384-dimensional `thenlper/gte-small` embeddings** for semantic vector search
- **Knowledge graph entities and relationships** extracted from the corpus
- **Logic proof artifacts** — per-section TDFOL, DCEC, F-logic formalizations, norm metadata, and ZKP certificate summaries

All corpus assets are pre-generated at build time and served as static files under `public/corpus/portland-or/current/generated/`. The app never calls the Hugging Face Dataset Viewer API at runtime.

## Browser Logic Engine

The logic layer (`src/lib/logic/`) is a browser-native TypeScript port of the `ipfs_datasets_py/ipfs_datasets_py/logic` Python module. It is designed to be deterministic, offline-capable, and free of any server-side dependencies.

### Currently Ported

| Module | Description |
|---|---|
| `logic/types` | Discriminated union types and interfaces mirroring Python dataclasses and enums |
| `logic/common` | Converter lifecycle, bounded cache, proof cache, validation, feature detection, and utility monitor |
| `logic/fol` | FOL regex quantifier/operator parsing, predicate extraction, logical relation extraction, variable allocation, and output formatters |
| `logic/deontic` | Deontic operator classification, formula construction, analyzer, knowledge-base primitives, norm extraction, conflict detection, and compliance checks |
| `logic/tdfol` | TDFOL AST, parser, formatter, inference rules (Modus Ponens/Tollens, temporal K/T, deontic K/D, etc.), forward-chaining prover, proving strategies, modal tableaux, countermodels, proof explainer, dependency graph, proof tree visualizer, security validator, and performance dashboard/profiler/metrics |
| `logic/cec` | CEC/DCEC AST, parser, formatter, analyzer, DCEC cleaning and preprocessing helpers, DCEC parse-token/prefixing helpers, syntax tree utilities, grammar loader/engine, ShadowProver problem parser (TPTP `fof`/`cnf`), native inference rules (propositional/first-order/modal/temporal/deontic/cognitive/resolution/specialized), fluent/event state manager, discrete event calculus (`Happens`/`Initiates`/`Terminates`/`HoldsAt`/`Clipped`), context manager, ambiguity resolver, ShadowProver facade, bounded prover, proof cache, proof explainer, dependency graph and tree visualizer, modal tableaux, countermodels, performance dashboard/profiler/metrics, and security validator |
| `logic/flogic` | F-logic frame, class, ontology, query, semantic normalization, and ErgoAI rendering |
| `logic/zkp` | Deterministic canonicalization and simulated ZKP certificate metadata checks |

### Roadmap

- **Phase 11**: Full TDFOL prover/inference-rule parity and richer interactive visualizations
- **Phase 12**: Full CEC/DCEC advanced strategies and complete prover parity
- **Phase 13**: Browser-native ML/NLP parity for FOL/deontic confidence scoring and spaCy-style NLP extraction using Transformers.js / ONNX / WebGPU
- **Phase 14**: ZKP Groth16/EVM/browser-native crypto parity
- **Phase 15**: IPFS-backed proof cache semantics

See [`docs/LOGIC_PORT_PARITY.md`](./docs/LOGIC_PORT_PARITY.md) and [`docs/IPFS_DATASETS_LOGIC_TYPESCRIPT_PORT_PLAN.md`](./docs/IPFS_DATASETS_LOGIC_TYPESCRIPT_PORT_PLAN.md) for the full tracking document.

## Stack

| Layer | Technology |
|---|---|
| Frontend framework | [Vite](https://vitejs.dev/) + [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) |
| Styling | [Tailwind CSS](https://tailwindcss.com/) |
| Corpus loading | [DuckDB-WASM](https://github.com/duckdb/duckdb-wasm) / [parquet-wasm](https://github.com/kylebarron/parquet-wasm) |
| Vector search | [hnswlib-wasm](https://github.com/yoshoku/hnswlib-wasm) / brute-force cosine scan |
| Browser inference | [Hugging Face Transformers.js](https://huggingface.co/docs/transformers.js) (`Xenova/gte-small` for embeddings; small generative models for GraphRAG chat) |
| Hosting | [GitHub Pages](https://pages.github.com/) via GitHub Actions |

## Quick Start

```sh
git clone https://github.com/portland-laws/portland-laws.github.io.git
cd portland-laws.github.io
npm install --legacy-peer-deps
npm run dev
```

Visit http://localhost:5173 to explore the app locally.

> **Note**: The corpus assets in `public/corpus/portland-or/current/generated/` are committed to the repository and are ready to use immediately. You do not need to re-run the data pipeline to start developing.

## Corpus Build Pipeline

If you need to regenerate the static corpus assets from the upstream Hugging Face dataset:

```sh
# 1. Download and process the Portland corpus parquet artifacts
python3 scripts/extract-portland-corpus.py

# 2. Generate optimized static assets (section-index, embeddings.f32, BM25 docs, KG adjacency, etc.)
npm run prepare:portland-corpus

# 3. Validate the generated assets
npm run validate:portland-corpus
```

Generated assets are written to `public/corpus/portland-or/current/generated/`:

| File | Description |
|---|---|
| `sections.json` | Full canonical section rows |
| `section-index.json` | Lightweight index of identifiers, titles, and chapter/title metadata |
| `bm25-documents.json` | Tokenized term-frequency documents for BM25 keyword search |
| `embeddings.f32` | Packed `Float32Array` of 384-dimensional `gte-small` embeddings |
| `embedding-index.json` | `ipfs_cid` lookup map for the embedding array |
| `entities.json` | Knowledge graph entity records |
| `relationships.json` | Knowledge graph relationship records |
| `graph-adjacency.json` | Precomputed KG adjacency maps for fast one-hop/two-hop expansion |
| `logic-proof-summaries.json` | Per-section TDFOL, DCEC, F-logic formalizations, norm metadata, and ZKP certificate summaries |
| `generated-manifest.json` | Row counts, embedding dimensions, and content hashes for validation |

## Testing

```sh
# Unit and integration tests (Jest)
npm test

# Logic port parity tests against Python-generated fixtures
npm run validate:logic-port

# End-to-end tests (Playwright)
npm run test:playwright
```

## Deployment

Every push to `main` automatically builds and deploys the app to GitHub Pages via the workflow in `.github/workflows/deploy.yml`. The live site is at **https://portland-laws.github.io**.

You can also trigger a deployment manually from the GitHub Actions tab.

### OpenRouter fallback proxy

GitHub Pages is static and cannot safely proxy OpenRouter requests with a secret key. This repo includes a Vercel-compatible proxy at `api/openrouter/chat/completions.js` so GitHub can still own the code and deployment trigger while Vercel provides request-time compute and secret storage.

Recommended setup:

1. Import this GitHub repo into Vercel.
2. Add Vercel environment variables:
   - `OPENROUTER_API_KEY`
   - `OPENROUTER_SITE_URL=https://portland-laws.github.io`
   - `OPENROUTER_SITE_NAME=Portland Laws`
   - `OPENROUTER_PROXY_ALLOWED_ORIGINS=https://portland-laws.github.io,http://localhost:5173,http://127.0.0.1:5173`
3. Configure the GitHub Pages build, or local `.env`, with:
   - `VITE_OPENROUTER_BASE_URL=https://<your-vercel-app>.vercel.app/api/openrouter`
   - `VITE_OPENROUTER_ENABLED=true`

The GitHub Pages deploy workflow now defaults to this proxy URL at build time:
`https://animegf.chat:8787/api/openrouter`
This default targets the currently documented DigitalOcean/Caddy TLS setup where the OpenRouter proxy is exposed on `:8787` instead of `:443`.

You can override it by adding `VITE_OPENROUTER_BASE_URL` as a GitHub repository variable under
**Settings → Secrets and variables → Actions → Variables**.

For quick testing on an already-deployed static bundle, you can temporarily set the proxy URL in browser devtools and reload:

```js
localStorage.setItem('PORTLAND_OPENROUTER_BASE_URL', 'https://<your-vercel-app>.vercel.app/api/openrouter')
```

### Local LLM diagnostics

The app does not trust local WebGPU inference merely because the model downloaded. It now marks local inference as ready only after a tiny generation probe succeeds. Legal GraphRAG prompts are compacted for the browser model, local generation is attempted first, and OpenRouter is used only as a last-resort fallback after local probe/generation failure, timeout, or an oversized prompt outside the configured local budget.

To keep chat responsive for first-time visitors, the app can run cloud-first until local inference proves acceptable throughput. Tune these optional variables in your build environment:

- `VITE_LOCAL_MIN_TOKENS_PER_SECOND` (default `4`)
- `VITE_LOCAL_PERF_SAMPLE_MIN_TOKENS` (default `10`)
- `VITE_LOCAL_PERF_BENCH_MAX_TOKENS` (default `40`)
- `VITE_LOCAL_PERF_BENCH_TIMEOUT_MS` (default `20000`)
- `VITE_LOCAL_GENERATION_FALLBACK_MS` (default `15000`)

Useful browser console checks:

```js
__PORTLAND_LLM__.getStatus()
await __PORTLAND_LLM__.probeLocalInference()
[...performance.getEntriesByType('resource')]
  .map(e => e.name)
  .filter(n => n.includes('clientLLMWorkerService') || n.includes('clientLLMWorker') || n.includes('/assets/index-'))
```

If local generation or the probe times out, the worker is terminated and recreated so a stuck WebGPU/ORT run cannot keep blocking later requests. The status object reports `localHealth.state`, `localHealth.proven`, the last failure reason, and the cloud fallback configuration.

The proxy only permits the LiquidAI OpenRouter models used by the app:
`liquid/lfm-2.5-1.2b-instruct:free` and `liquid/lfm-2.5-1.2b-thinking:free`.

### DigitalOcean proxy setup

On a DigitalOcean droplet after cloning this repo:

```bash
cd portland-laws.github.io
OPENROUTER_API_KEY=sk-or-... sudo -E bash scripts/setup-openrouter-proxy-digitalocean.sh
```

The script writes `/etc/portland-openrouter-proxy.env` and starts a systemd service on port `8787`. It does not need a full `npm install` because the proxy uses only built-in Node modules. Point the frontend at:

```bash
VITE_OPENROUTER_BASE_URL=https://animegf.chat:8787/api/openrouter
```

By default the proxy allows browser requests from:

```bash
https://portland-laws.github.io
https://211-ai.github.io
```

Because the GitHub Pages app is served over HTTPS, the proxy URL used by the browser must also be HTTPS. If OpenVPN owns port `443`, keep the Node service on `127.0.0.1:8787` and terminate TLS on public port `8787` with Caddy or Nginx.

Example Caddyfile for direct HTTPS on `:8787` while OpenVPN keeps `:443`:

```caddy
https://animegf.chat:8787 {
   reverse_proxy 127.0.0.1:8787
}
```

If you also serve pages from `https://animegf.chat`, add that origin to `OPENROUTER_PROXY_ALLOWED_ORIGINS` before restarting the service.

To add or rotate the OpenRouter API key on the DigitalOcean VPS after setup:

```bash
sudo nano /etc/portland-openrouter-proxy.env
```

Set or replace this line:

```bash
OPENROUTER_API_KEY=sk-or-your-key-here
```

Then restart and verify the service:

```bash
sudo systemctl restart portland-openrouter-proxy
sudo systemctl status portland-openrouter-proxy
curl -fsS http://127.0.0.1:8787/health
```

### Configure GitHub Pages to use the proxy

After the proxy is reachable from the browser, configure the GitHub Pages build with the proxy base URL:

1. Open the GitHub repository.
2. Go to **Settings → Secrets and variables → Actions → Variables**.
3. Optionally add or update this repository variable to override the workflow default:
   - Name: `VITE_OPENROUTER_BASE_URL`
   - Value: `https://animegf.chat:8787/api/openrouter`

### Voice proxy setup

If you have a private voice inference service reachable from the VPS, for example:

```bash
curl -X POST \
   -H "x-api-key: ..." \
   -F "audio=@test_input.wav;type=audio/wav" \
   http://10.8.0.99:8000/infer \
   -o reply.wav
```

you can install a dedicated browser-safe proxy on a separate port:

```bash
sudo -E bash scripts/setup-voice-proxy-digitalocean.sh
```

The voice proxy listens on port `8790` by default and forwards multipart uploads to `http://10.8.0.99:8000/infer` unless you override `VOICE_PROXY_UPSTREAM_URL`. It also avoids a full `npm install` because the proxy uses only built-in Node modules. Set `VOICE_PROXY_API_KEY` only if your upstream service actually requires an `x-api-key` header.

After terminating TLS for that port, call it from the browser at:

```bash
https://animegf.chat:8790/api/voice/infer
```

Example browser-compatible curl against the proxy:

```bash
curl -X POST \
   -F "audio=@test_input.wav;type=audio/wav" \
   https://animegf.chat:8790/api/voice/infer \
   -o reply.wav
```
4. Confirm `VITE_OPENROUTER_ENABLED` is not set to `false`. The deploy workflow already builds with fallback enabled.
5. Rerun the GitHub Pages deploy workflow from **Actions**, or push a new commit to `main`.
6. Hard refresh the live page after deployment.

The value must be the proxy base path, not the full chat endpoint. The app appends `/chat/completions` itself.

For a quick browser-only test before rebuilding GitHub Pages, open DevTools on the live site and run:

```js
localStorage.setItem(
  'PORTLAND_OPENROUTER_BASE_URL',
   'https://animegf.chat/api/openrouter'
)
location.reload()
```

Then verify the app sees the proxy:

```js
__PORTLAND_LLM__.getCloudFallbackStatus()
```

It should report `configured: true` and a `baseUrl` pointing at your proxy, not `https://openrouter.ai/api/v1`.

## Documentation

| Document | Description |
|---|---|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Current architecture for the legal-research frontend and the PP&D daemon workspace |
| [`docs/PORTLAND_LEGAL_CORPUS_IMPLEMENTATION_PLAN.md`](./docs/PORTLAND_LEGAL_CORPUS_IMPLEMENTATION_PLAN.md) | Full implementation plan for the Portland corpus research UI |
| [`docs/IPFS_DATASETS_LOGIC_TYPESCRIPT_PORT_PLAN.md`](./docs/IPFS_DATASETS_LOGIC_TYPESCRIPT_PORT_PLAN.md) | Roadmap for porting the Python logic module to TypeScript/WASM |
| [`docs/LOGIC_PORT_PARITY.md`](./docs/LOGIC_PORT_PARITY.md) | Parity tracker comparing TypeScript behavior to Python targets |
| [`docs/LOGIC_WASM_RESEARCH.md`](./docs/LOGIC_WASM_RESEARCH.md) | Research notes on browser-native theorem-prover options |
| [`TESTING.md`](./TESTING.md) | Current lint/build/test and PP&D validation commands |
| [`CLIENT_LLM_IMPLEMENTATION.md`](./CLIENT_LLM_IMPLEMENTATION.md) | Browser inference architecture (Transformers.js, Web Workers) |
| [`MODEL_GUIDE.md`](./MODEL_GUIDE.md) | Guidance on supported browser-inference models and hardware requirements |
| [`ppd/README.md`](./ppd/README.md) | PP&D workspace boundaries, validation, and daemon control commands |
| [`ppd/daemon/OPERATIONS.md`](./ppd/daemon/OPERATIONS.md) | PP&D daemon/supervisor operations, runtime files, and safety constraints |

## Legal Disclaimer

This site provides **legal information, not legal advice**. All answers are grounded in the Portland City Code corpus as retrieved and should not be relied upon as authoritative legal guidance. Always consult the [official Portland City Code](https://www.portlandoregon.gov/citycode/) and a licensed attorney for legal matters.
