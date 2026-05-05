# IPFS Datasets Logic TypeScript Port Improvement Plan

## Executive Summary

This project already contains the Portland City Code corpus, generated search assets, knowledge graph artifacts, and machine-generated logic proof summaries. The improvement track is to port the full `ipfs_datasets_py/ipfs_datasets_py/logic` module into a browser-native TypeScript/WASM logic stack. Heavyweight theorem provers, NLP dependencies, ML confidence scoring, cryptographic proof systems, and chain integrations should be replaced with TypeScript or WebAssembly implementations rather than external server-side calls.

The practical goal is to translate the entire Python logic surface area into TypeScript/WASM in phases. The runtime target is browser-native TypeScript/WebAssembly only. The app must not depend on external server-side services for logic conversion, ML/NLP confidence, proving, or verification.

Update: Python ML confidence scoring and spaCy-style NLP extraction are required porting targets. They must be ported to browser-native equivalents using TypeScript, WebAssembly, Transformers.js, ONNX/WebGPU, or other local browser-compatible packages. Python can only serve as the source implementation and fixture generator during development.

## Current Project Fit

The repository is a Vite/React/TypeScript static app with existing Portland corpus support:

- `src/lib/portlandCorpus.ts` loads sections, BM25 documents, embeddings, entities, relationships, and graph adjacency from `public/corpus/portland-or/current/generated/`.
- `public/corpus/portland-or/current/generated/logic-proof-summaries.json` already exposes per-section formalization data, including `deontic_temporal_fol`, `deontic_cognitive_event_calculus`, `frame_logic_ergo`, `norm_operator`, `norm_type`, `zkp_backend`, `zkp_security_note`, and `zkp_verified`.
- `package.json` already includes browser-oriented foundations that help this port: TypeScript, Jest, Playwright, DuckDB-WASM, parquet-wasm, Transformers.js, hnswlib-wasm, and Vite workers.
- `docs/PORTLAND_LEGAL_CORPUS_IMPLEMENTATION_PLAN.md` already identifies proof artifact exploration and browser theorem-prover research as future phases.

The Python source tree has a broad logic surface:

- Foundation: `logic/types`, `logic/common`, `logic/config.py`, `logic/batch_processing.py`.
- FOL: `logic/fol`, including text-to-FOL conversion, parser utilities, predicate extraction, and output formatters.
- Deontic: `logic/deontic`, including legal-text-to-deontic conversion and normative conflict helpers.
- TDFOL: `logic/TDFOL`, including AST types, parser, converter, prover, inference rules, proof cache, proof visualization, security validator, and performance tooling.
- CEC/DCEC: `logic/CEC`, including event calculus, modal/cognitive inference, native prover machinery, NL policy compilers, and bridges.
- F-logic: `logic/flogic`, including frame/class/query/ontology types and ErgoAI rendering.
- Integration: `logic/integration`, `logic/integrations`, `search/logic_integration`, and GraphRAG-specific bridge code.
- ZKP: `logic/zkp`, including deterministic canonicalization, statement/witness structures, verifier/prover abstractions, Groth16/FFI backends, EVM integration, and simulated backends.
- External provers: `logic/external_provers`, including Z3, CVC5, E Prover, Vampire, Lean, Coq, and routing.
- Operational modules: API server, CLI, security, observability, monitoring, dashboards, benchmarks.

## Full Python Module Coverage Inventory

The full-port target is the entire `ipfs_datasets_py/ipfs_datasets_py/logic` tree, currently 304 Python files. The TypeScript/WASM work should track every area below until it has browser-native parity, a browser-native replacement, or a documented blocking issue.

| Python area | File count | Browser-native port target |
| --- | ---: | --- |
| `logic/CEC` | 71 | Full CEC/DCEC AST, parser, native inference, event calculus, NL policy compiler, optimization, and prover parity. |
| `logic/TDFOL` | 52 | Full TDFOL AST, parser, converters, inference rules, prover, strategies, security, visualization, P2P, and NL parity. |
| `logic/integration` | 78 | Full bridge, converter, cache, domain, interactive, reasoning, and symbolic integration parity routed to TS/WASM cores. |
| `logic/zkp` | 27 | Full canonicalization, statement, witness, Groth16, verifier/prover, backend, circuit, and browser crypto parity. |
| `logic/external_provers` | 13 | Browser-native WASM/local adapters for supported prover workflows and routing semantics. |
| `logic/fol` | 9 | Full FOL parser, converter, predicate extraction, NLP extraction, output format, batch, cache, and validation parity. |
| `logic/deontic` | 9 | Full deontic parser, converter, knowledge base, conflict detection, ML confidence, exception, and temporal parity. |
| `logic/common` | 8 | Full cache, validation, converter lifecycle, config, error, and utility parity. |
| `logic/types` | 7 | Full dataclass/enum/protocol parity as TypeScript discriminated unions and interfaces. |
| `logic/flogic` | 6 | Full F-logic frame, class, ontology, query, semantic normalization, and Ergo rendering parity. |
| `logic/security` | 5 | Browser-safe validation, rate limiting, circuit breaker, audit semantics, and policy checks. |
| `logic/integrations` | 4 | Browser-compatible integration adapters. |
| `logic/observability` | 4 | In-browser metrics, traces, diagnostics, and developer panels. |
| Top-level modules | 11 | `api.py`, `api_server.py`, `cli.py`, `batch_processing.py`, `benchmarks.py`, `monitoring.py`, `ml_confidence.py`, `config.py`, validation scripts, and package entry points reworked as TS APIs, local dev scripts, or browser tools. |

## Guiding Principle

Port behavior first, but account for every file.

The TypeScript target should be a clean client-side domain library that preserves the Python module's semantics without blindly copying Python layout. Browser code should be deterministic, inspectable, offline-capable, and tested against Python parity fixtures. Anything that depends on subprocesses, Python ML packages, prover binaries, secrets, chain RPC, or native dependencies must receive a TypeScript/WASM replacement. Temporary capability reporting is allowed only while a module is mid-port, not as the final state.

## Target Outcomes

1. Add first-class TypeScript types for Portland logic artifacts.
2. Load and index proof summaries alongside existing corpus data.
3. Parse the generated TDFOL, DCEC, and F-logic strings into lightweight ASTs or structured views.
4. Validate formulas and proof metadata deterministically in the browser.
5. Add norm-aware filters and ranking signals to search.
6. Add a proof explorer UI that explains obligations, permissions, prohibitions, temporal operators, supporting code sections, and generated certificate metadata.
7. Add client-side reasoning that grows from bounded forward chaining into full TDFOL/CEC/DCEC parity.
8. Replace Python as the authoritative formalization generator once TypeScript/WASM parity is proven.
9. Port Python ML confidence scoring and spaCy NLP extraction to browser-native ML/NLP.
10. Port external prover bridges and ZKP backends to browser-native WASM or equivalent local packages.

## Portability Matrix

| Python area | TypeScript/WASM port recommendation | Why |
| --- | --- | --- |
| `logic/types` | Port directly | Mostly enums, dataclasses, protocol-like shapes. These map well to TypeScript discriminated unions and interfaces. |
| `logic/types/common_types.py`, `proof_types.py`, `bridge_types.py`, `fol_types.py`, `translation_types.py` | Port directly | Initial TypeScript port now covers complexity metrics, proof result shapes, bridge metadata/config/conversion/recommendation helpers, FOL predicate/formula/conversion/extraction helpers, and translation result/abstract formula helpers. |
| `logic/common/errors.py` | Port directly | Standard error hierarchy improves client diagnostics. |
| `logic/common/bounded_cache.py` | Port directly | Useful for parsed formula caches and proof summary indexes. Browser implementation is straightforward with `Map`, TTL, and LRU bookkeeping. |
| `logic/common/validators.py` | Ported | Browser-native parity covers formula string, axiom list, logic system, timeout, format, and complete logic problem payload validators with Python-style errors. |
| `logic/config.py` | Port as browser-native config objects | Initial TypeScript parity now covers prover/cache/security/monitoring config defaults, Python-compatible dictionary serialization, object loading, and explicit env-record loading without YAML/filesystem/process runtime dependencies. |
| `logic/common/converters.py` | Port fully as idiomatic TS interfaces/classes | Preserve converter lifecycle, validation, caching, batch behavior, and result shapes in browser-native form. |
| `logic/batch_processing.py` | Port as browser-native async batching | TypeScript parity now covers batch result stats, bounded async processing, FOL conversion batches, local bridge proof batches, chunked large-batch aggregation, and browser-native dict/JSON/CSV result exports without Python thread/process pools, filesystem writes, or server workers. |
| `logic/monitoring.py` | Port as browser-native telemetry objects | Initial TypeScript parity now covers operation metrics, operation tracking, error/warning counters, health checks, reset, operation summaries, global monitor helper, and optional Prometheus text export without server daemons or threads. |
| `logic/benchmarks.py` | Port as browser-native benchmark helpers | Initial TypeScript parity now covers benchmark result stats, sync/async benchmark runners, comparisons, summaries, FOL conversion benchmarks, proof-cache benchmarks, and comprehensive local benchmark runs with browser timing APIs. |
| `logic/api.py` | Port as browser-native public API facade | Initial TypeScript parity now covers stable FOL/deontic conversion wrappers, generic bridge conversion/proving, monitoring integration, local benchmark entrypoint, Python-compatible aliases, NL policy compile/evaluate helpers, and explicit unsupported UCAN signing status without server fallback. |
| `logic/TDFOL/tdfol_core.py` | Port directly | AST, operators, terms, formulas, substitution, and free-variable analysis are the best TypeScript core. |
| `logic/TDFOL/tdfol_parser.py` | Port directly, with tests | Recursive descent parsing and tokenization are portable. This unlocks proof explorer and validation. |
| `logic/TDFOL/tdfol_converter.py` | Port fully | TDFOL to DCEC/FOL/TPTP conversion must match Python outputs. Initial browser converter supports stable TDFOL, FOL projection, DCEC s-expression, TPTP, JSON, metadata, and projection warnings. |
| `logic/TDFOL/tdfol_inference_rules.py` | Port fully | All propositional, first-order, temporal, deontic, and combined rules need TS parity. |
| `logic/TDFOL/expansion_rules.py` | Port directly | Tableaux expansion rules are deterministic and reusable across modal tableaux and inference systems. |
| `logic/TDFOL/tdfol_prover.py` | Port fully | Start with bounded reasoning, then complete proof search parity and strategy selection. |
| `logic/TDFOL/strategies/base.py`, `forward_chaining.py`, `modal_tableaux.py`, `strategy_selector.py` | Port fully | Browser-native proof strategy selection keeps prover behavior modular without Python strategy classes. |
| `logic/TDFOL/tdfol_optimization.py` | Port fully in browser form | Indexed KB, cache-aware proving, strategy heuristics, and stats are portable; ZKP/parallel search require TS/WASM equivalents. |
| `logic/TDFOL/modal_tableaux.py` | Port fully in browser form | K/T/D/S4/S5 tableaux, branch expansion, accessibility handling, and countermodel open branches are portable. |
| `logic/TDFOL/countermodels.py`, `countermodel_visualizer.py` | Port fully in browser form | Kripke structures, countermodel extraction, DOT/JSON/ASCII/HTML exports, and accessibility property checks are browser-native. |
| `logic/TDFOL/performance_profiler.py` | Port fully in browser form | Repeated timing profiles, memory snapshots, bottleneck classification, benchmark suites, and report generation can run with browser performance APIs. |
| `logic/TDFOL/performance_dashboard.py` | Port fully in browser form | Proof metrics, time-series metrics, aggregation, strategy comparison, JSON export, and self-contained dashboard HTML are browser-native. |
| `logic/TDFOL/tdfol_performance_engine.py` | Port fully in browser form | Metrics, profiling, dashboards, strategy comparison, and regression checks can run in memory with browser-safe exports. |
| `logic/TDFOL/proof_tree_visualizer.py` | Port fully in browser form | Render proof trees in React/canvas/SVG and preserve exportable DOT/JSON where useful. |
| `logic/fol/utils/fol_parser.py` | Port directly | Regex-based quantifier/operator parsing and formatting are browser-friendly. |
| `logic/fol/utils/predicate_extractor.py` | Port fully | Regex and rule-based extraction are portable. |
| `logic/fol/utils/nlp_predicate_extractor.py` | Port fully via browser-native NLP | Reproduce spaCy extraction behavior with Transformers.js, ONNX/WebGPU, compromise-like parsers, or WASM NLP. |
| `logic/fol/converter.py` | Port fully | Preserve cache, batch, validation, ML confidence, NLP mode, output formats, and monitoring-compatible metadata. |
| `logic/deontic/utils/deontic_parser.py` | Port directly if regex/pattern-based | Norm extraction from legal text is valuable for Portland sections and can be tested against generated artifacts. |
| `logic/deontic/converter.py` | Port fully | Deontic extraction, exception handling, obligations, permissions, prohibitions, confidence, batch, and cache behavior need parity. |
| `logic/ml_confidence.py` | Port fully via browser-native ML | Initial deterministic TypeScript port now covers Python-compatible feature extraction, fallback scoring, training facade, and feature importance. Next step is local browser artifact loading for trained XGBoost/LightGBM-equivalent weights through TS/WASM/ONNX where needed. |
| `logic/deontic/knowledge_base.py` | Port fully | Browser-native indexed norms and query APIs are required. |
| `logic/deontic/graph.py`, `support_map.py` | Port fully | Initial TypeScript port now covers deontic graph nodes/rules, assessments, summaries, conflict detection, graph builders, serialization, and support-map entries for facts/filings. |
| `logic/flogic/flogic_types.py` | Port directly | Frame, class, query, ontology, and Ergo rendering are simple and valuable for display. |
| `logic/flogic/semantic_normalizer.py` | Port fully | Dictionary mode ports directly; SymAI behavior needs browser-native semantic similarity replacement. |
| `logic/zkp/canonicalization.py` | Port directly | Deterministic canonicalization, hashing, and field mapping are useful for verifying generated metadata consistency. Use Web Crypto or a small SHA-256 fallback. |
| `logic/zkp/statement.py` | Port directly | Initial TypeScript parity now covers statement/witness/proof-statement JSON schemas, circuit reference parsing/formatting, field-element mapping, and Python-compatible witness defaults. |
| `logic/zkp/circuits.py` | Port metadata and local constraint evaluators first | Initial TypeScript parity now covers high-level Boolean circuit construction, simplified R1CS export, MVP knowledge-of-axioms circuit metadata, and local TDFOL v1 Horn-derivation constraint checks without cryptographic backend claims. |
| `logic/zkp/backends/simulated.py` and `logic/zkp/backends/__init__.py` | Port as browser-native simulated backend and registry | TypeScript parity now covers simulated `ZKPProof` dictionary serialization and validation, 160-byte `SIMZKP/1` proof layout generation, deterministic seeded browser fixtures, segment commitment public inputs, fail-closed simulated verification, backend metadata, aliases, availability checks, cache reset, and explicit unsupported Groth16 status without server fallback. |
| `logic/zkp/zkp_prover.py` and `logic/zkp/zkp_verifier.py` | Port simulated facades first, then real browser-native verification for supported circuits | Initial TypeScript parity now covers async browser-native prover/verifier facades, backend routing, canonicalized proof cache keys, cached theorem adaptation, `prove()` alias witness handling, public-input validation, expected-theorem checks, statistics, reset, and fail-closed unsupported-backend behavior. |
| `logic/zkp/legal_theorem_semantics.py` and `logic/zkp/witness_manager.py` | Port directly as browser-native witness helpers | Initial TypeScript parity now covers TDFOL v1 Horn atom/axiom/theorem parsing, deterministic forward-chaining evaluation, derivation traces, witness generation, commitment validation, proof-statement creation, witness consistency checks, cache lookup, and Python-compatible aliases. |
| `logic/zkp/evm_public_inputs.py` | Port directly as browser-native field packing | Initial TypeScript parity now covers BN254 Fr modulus export, 0x normalization, 32-byte hex-to-field reduction, SHA-256 text-to-field hashing, single public-input packing, batch packing, and Python-style validation errors without chain/RPC calls. |
| `logic/zkp/vk_registry.py`, `logic/zkp/eth_vk_registry_payloads.py`, and `logic/zkp/eth_contract_artifacts.py` | Port off-chain registry, payload validation, and artifact parsing first | Initial TypeScript parity now covers stable VK hashing, in-memory VK registry registration/lookup/serialization, circuit-ref lookup, bytes32 normalization, registerVK payload validation, contract ABI/bytecode artifact parsing from object/JSON values, and explicit unsupported filesystem/calldata/keccak status until local browser replacements land. |
| `logic/zkp/groth16*`, remaining EVM files | Port to WASM/browser crypto | Use snarkjs, noble/viem/ethers browser APIs, or generated WASM circuits. |
| `logic/CEC/native` | Port fully to TS/WASM | Large inference engine with many rules; split into AST/parser/rules/prover packages and use WASM only where needed. |
| `logic/CEC/nl` | Port fully via browser-native NLP | Policy compilers and language detectors need TS/NLP equivalents. |
| `logic/external_provers` | Port bridge layer to browser-native WASM provers | Z3/cvc5/Tau Prolog/Lean/Coq bridges should target local WASM packages or local in-browser adapters only. |
| `logic/integration/*bridge*` | Port fully | Bridge types and implementation should route to TS/WASM cores, not Python. |
| `logic/integration/*bridge*` initial browser facade | Port directly | `BrowserNativeLogicBridge` now routes text-to-FOL/deontic, TDFOL conversion, CEC formatting, and TDFOL/CEC proof requests to local TypeScript cores with explicit unsupported-route status and no server calls. |
| `logic/security`, `observability`, `api_server`, `cli` | Port as browser/runtime equivalents | Initial shared security TypeScript port now covers input validation, sliding-window rate limiting, LLM-style circuit breakers, global breaker registry, and structured in-memory audit events. Initial observability TypeScript port now covers structured logs, context propagation, Prometheus-style metrics text, and in-memory OTel-style traces. Dashboards and CLI-like developer tools remain follow-up TS/browser/devtool modules. |

## Proposed TypeScript Architecture

Add a new `src/lib/logic/` package:

```text
src/lib/logic/
  index.ts
  types.ts
  errors.ts
  cache.ts
  proofArtifacts.ts
  tdfol/
    ast.ts
    lexer.ts
    parser.ts
    formatter.ts
    validate.ts
    converter.ts
    reasoner.ts
  fol/
    parser.ts
    predicateExtractor.ts
    formatter.ts
    converter.ts
  deontic/
    types.ts
    parser.ts
    converter.ts
    conflicts.ts
  flogic/
    types.ts
    parser.ts
    formatter.ts
  zkp/
    canonicalization.ts
    statement.ts
    simulatedVerifier.ts
  graph/
    proofGraph.ts
    normIndex.ts
```

The public API should stay small:

```ts
loadLogicProofSummaries(): Promise<LogicProofSummary[]>
getLogicProofForSection(ipfsCid: string): Promise<LogicProofSummary | null>
parseTdfolFormula(source: string): TdfolFormula
validateLogicProofSummary(summary: LogicProofSummary): LogicValidationResult
buildNormIndex(summaries: LogicProofSummary[]): NormIndex
searchByNorm(query: NormQuery): LogicProofSummary[]
explainNorm(summary: LogicProofSummary): LogicExplanation
verifySimulatedCertificate(summary: LogicProofSummary): SimulatedVerificationResult
```

## Data Model Improvements

Add TypeScript contracts for the existing generated artifact:

```ts
export type NormOperator = 'O' | 'P' | 'F' | 'unknown';
export type NormType = 'obligation' | 'permission' | 'prohibition' | 'unknown';
export type FormalizationStatus = 'success' | 'partial' | 'failed' | 'unknown';

export interface LogicProofSummary {
  ipfs_cid: string;
  identifier: string;
  title: string;
  formalization_scope: string;
  fol_status: FormalizationStatus;
  deontic_status: FormalizationStatus;
  deontic_temporal_fol: string;
  deontic_cognitive_event_calculus: string;
  frame_logic_ergo: string;
  norm_operator: NormOperator;
  norm_type: NormType;
  zkp_backend: 'simulated' | 'groth16' | 'unknown';
  zkp_security_note: string;
  zkp_verified: boolean;
}
```

Derived indexes:

- `proofByCid`: map section CID to proof summary.
- `proofByIdentifier`: map Portland citation to proof summary.
- `normByOperator`: `O`, `P`, `F`.
- `formalizationStatusCounts`: success/partial/failed/unknown counts.
- `proofParseStatus`: TDFOL/DCEC/F-logic parse success by section.
- `sectionLogicSignals`: search ranking signals derived from norm type, status, and operator.

## Integration With Existing Corpus Service

Extend `src/lib/portlandCorpus.ts` or add a sibling `src/lib/portlandLogic.ts`.

Recommended split:

- Keep `portlandCorpus.ts` focused on sections, BM25, embeddings, and KG.
- Add `portlandLogic.ts` for proof summaries, norm indexes, and parsed formula caches.
- Add shared ID helpers for `ipfs_cid`, `identifier`, and Portland citation normalization.

New corpus-level APIs:

```ts
getSectionWithLogic(ipfsCid: string): Promise<{
  section: CorpusSection | null;
  proof: LogicProofSummary | null;
  relatedGraph: { entities: CorpusEntity[]; relationships: CorpusRelationship[] };
}>

searchCorpusWithLogic(
  query: string,
  filters: SearchFilters & LogicSearchFilters,
  mode: SearchMode,
  queryEmbedding?: Float32Array | number[],
): Promise<SearchResult[]>
```

Logic-aware search filters:

```ts
export interface LogicSearchFilters {
  normOperators?: NormOperator[];
  normTypes?: NormType[];
  formalizationStatuses?: FormalizationStatus[];
  requireVerifiedCertificate?: boolean;
  requireParseableTdfol?: boolean;
}
```

## UI Improvements Enabled By The Port

1. Proof artifact explorer
   - Section-level panel showing TDFOL, DCEC, F-logic, norm type, operator, status, and certificate note.
   - Parse status badges with precise errors.
   - Toggle between raw source, formatted AST, and plain-English explanation.

2. Norm-aware search
   - Filters for obligations, permissions, prohibitions, formalization status, and certificate metadata.
   - Search result badges for norm type and proof status.
   - Ranking boost when query terms match norm semantics such as "must", "may", "prohibited", "deadline", or "penalty".

3. Logic graph view
   - Start with the existing KG adjacency.
   - Add proof-derived nodes: section, norm, actor, action, condition, temporal operator, certificate.
   - Keep this bounded and inspectable for the first implementation slice.

4. Explanation layer
   - Translate `O`, `P`, `F`, `always`, `eventually`, `SubjectTo`, and `ComplyWith` into short user-facing labels.
   - Always label generated formalizations as machine-generated candidates.
   - Always distinguish simulated educational certificates from cryptographic proof verification.

5. GraphRAG improvements
   - Add logic facts to the evidence pack.
   - Prefer citations with successful formalizations when the user asks normative questions.
   - Let the answer cite both code text and logic metadata, with clear caveats.

## Implementation Phases

### Phase 0: Inventory And Baseline

- [x] Add this plan to `docs/`.
- [x] Record the exact generated proof summary schema from `public/corpus/portland-or/current/generated/logic-proof-summaries.json`.
- [x] Add a small script or test fixture with 10 representative proof summaries: obligation, permission, prohibition, parse success, parse failure, simulated certificate, missing logic, long F-logic, citation match, KG-linked section.
- [x] Decide whether logic code lives in `src/lib/logic/` or a package-style `src/logic/`.

Acceptance criteria:

- There is a typed inventory of all fields consumed by the app.
- No runtime dependency on the Python package is introduced.
- Existing search behavior remains unchanged.

### Phase 1: Proof Summary Loader And Types

- [x] Add `src/lib/portlandLogic.ts`.
- [x] Add `LogicProofSummary` and related enums/unions.
- [x] Implement `loadLogicProofSummaries()`, `getLogicProofForSection()`, and summary count helpers.
- [x] Cache the loaded proof summaries like the existing corpus service does.
- [x] Add Jest tests for loading, indexing, and missing-section behavior.

Acceptance criteria:

- The app can join any section to its proof summary by `ipfs_cid`.
- Tests verify at least one known citation such as `Portland City Code 1.01.010`.
- Logic artifacts remain lazy-loaded.

### Phase 2: TypeScript Logic Foundation

- [x] Port common logic enums and data shapes from `logic/types`.
- [x] Add `LogicError`, `LogicParseError`, `LogicValidationError`, and `LogicVerificationError`.
- [x] Port `logic/config.py` dataclass-style prover/cache/security/monitoring config defaults, `to_dict` output, object loading, and explicit env-record loading without browser runtime filesystem/YAML/process dependencies.
- [x] Port `logic/common/validators.py` formula string, axiom list, logic system, timeout, and format validators with Python-style validation errors.
- [x] Port bounded TTL/LRU cache for parsed formulas.
- [x] Port `logic/batch_processing.py` batch result stats, bounded async processing, FOL conversion batches, local bridge proof batches, and chunked large-batch aggregation in browser-native TypeScript.
- [x] Port `logic/benchmarks.py` benchmark result stats, sync/async timing runners, comparison, summaries, local FOL benchmark suite, local proof-cache benchmark suite, and comprehensive benchmark runner.
- [x] Port initial `logic/api.py` public facade with stable browser-native conversion/proof wrappers, Python-compatible aliases, monitoring integration, local benchmark entrypoint, and explicit unsupported UCAN-signing result.
- [x] Port `logic/common/converters.py` lifecycle concepts: conversion statuses, standardized results, validation, local cache, batch conversion, async wrapper, and chained converters.
- [x] Port browser-native `logic/common/proof_cache.py` concepts: deterministic content IDs, prover-specific lookup, TTL, LRU eviction, invalidation, global cache, and stats.
- [x] Port browser-native `logic/common/feature_detection.py` and `logic/common/utility_monitor.py` concepts without importing Python-only optional dependencies.
- [x] Add schema guards for proof summary fields.
- [x] Add normalization helpers for identifiers, predicate names, and citations.

Acceptance criteria:

- Invalid artifact rows fail with actionable validation errors.
- Parsed formula cache has deterministic eviction and no unbounded growth.
- TypeScript exposes discriminated unions instead of loose `Record<string, unknown>` where possible.

### Phase 3: TDFOL AST, Lexer, Parser, Formatter

- [x] Port the TDFOL term/formula model from `tdfol_core.py`.
- [x] Port tokenization and recursive descent parsing from `tdfol_parser.py`.
- [x] Port initial `tdfol_converter.py` browser converter for stable TDFOL, FOL projection, DCEC s-expression, TPTP, JSON, metadata, and batch conversion.
- [x] Support ASCII and symbolic operator aliases where feasible.
- [x] Format ASTs back to compact source and display-friendly JSON.
- [x] Implement free variable analysis and basic substitution.
- [x] Port initial `TDFOL/inference_rules` browser-native rule interface and deterministic propositional, temporal, deontic, and first-order rules.
- [x] Port `expansion_rules.py` browser-native rule registry for AND, OR, IMPLIES, IFF, and NOT tableaux expansions.
- [x] Port initial `tdfol_prover.py` forward-chaining proof engine with step and derived-formula budgets.
- [x] Port initial `TDFOL/strategies/base.py`, `forward_chaining.py`, `backward_chaining.py`, `bidirectional.py`, `modal_tableaux.py`, `cec_delegate.py`, and `strategy_selector.py` browser strategy layer with priority/cost selection.
- [x] Port initial `tdfol_optimization.py` browser facade with indexed KB, cache-aware proving, strategy heuristics, and optimization stats.
- [x] Port initial `modal_tableaux.py` browser tableaux core for K/T/D/S4/S5, branch expansion, closure checks, modal worlds, and countermodel-compatible open branches.
- [x] Port initial `countermodels.py` and `countermodel_visualizer.py` browser equivalents for Kripke structures, branch extraction, DOT/JSON/ASCII/HTML exports, and modal property checks.
- [x] Port initial `proof_explainer.py`, `formula_dependency_graph.py`, and `proof_tree_visualizer.py` browser equivalents for text, JSON, DOT, HTML, ASCII tree, and graph exports.
- [x] Port initial `security_validator.py` browser equivalents for formula validation, rate limiting, resource limits, sanitization, ZKP audit checks, and security reports.
- [x] Port initial `performance_metrics.py` browser metrics collector for timings, memory samples, counters, gauges, histograms, summaries, and exports.
- [x] Port initial `performance_profiler.py` browser profiler for repeated timing samples, optional browser memory snapshots, bottleneck classification, benchmark suites, and text/JSON/HTML reports.
- [x] Port initial `performance_dashboard.py` browser dashboard for proof metrics, time-series metrics, aggregation, strategy comparison, JSON export, and self-contained HTML.
- [x] Port initial `tdfol_performance_engine.py` browser engine for metrics aggregation, profiling operations, dashboard HTML strings, statistics export, strategy comparison, regression checks, and reset.
- [x] Add fixtures from generated Portland formulas.

Acceptance criteria:

- At least 95 percent of generated `deontic_temporal_fol` strings parse or produce classified parse errors.
- Parsed formulas round-trip to a stable normalized string.
- Parser errors include position, token, and expected token class.

### Phase 4: FOL And Deontic Lightweight Conversion

- [x] Port regex-based quantifier and logical operator parsing from `fol/utils/fol_parser.py`.
- [x] Port `fol/utils/predicate_extractor.py` regex predicate, relation, and variable extraction.
- [x] Port `fol/utils/logic_formatter.py` FOL/deontic JSON, Prolog, TPTP, defeasible, text, and aggregate formatting helpers.
- [x] Port predicate-name normalization and simple FOL formatting.
- [x] Port deontic operator extraction for must/shall/required/may/permitted/prohibited/shall not.
- [x] Port `deontic/knowledge_base.py` browser-native primitives: parties, actions, intervals, propositions, statements, rule inference, and compliance checks.
- [x] Port `deontic/analyzer.py` extraction, entity grouping, statistics, action similarity, and direct/conditional/jurisdictional/temporal conflict detection.
- [x] Add browser FOL and deontic converter facades for short clauses.
- [x] Add converter cache, batch, async, output-format helper, metadata, confidence, and warning behavior tests.
- [x] Add confidence heuristics but do not port Python ML scoring.
- [x] Add explicit Python ML confidence and spaCy NLP parity fixtures.
- [x] Decide which parity path to use: browser-native replacement or WASM only for runtime; Python fixtures are development-only.

Acceptance criteria:

- The TypeScript converter can classify simple Portland-style legal clauses as obligation, permission, or prohibition.
- It can explain why an operator was selected using matched phrases.
- It never overwrites the authoritative generated artifact without explicit user action.
- It documents where browser heuristics differ from Python ML/spaCy outputs.

### Phase 4B: Browser-Native Python ML And spaCy Parity Track

- [x] Capture Python `FOLConverter(use_ml=True, use_nlp=True)` outputs for representative legal clauses as development fixtures only.
- [x] Capture Python `DeonticConverter(use_ml=True)` confidence outputs for the same fixtures as development fixtures only.
- [x] Add parity fixtures with raw text, regex-only output, spaCy-enabled output, ML confidence, and expected tolerances.
- [x] Evaluate browser substitutes for spaCy predicate extraction, including Transformers.js token classification or dependency-light NLP packages.
- [x] Decide that ML confidence must run in-browser or from precomputed static artifacts; no runtime Python service is allowed.
- [x] Add a compatibility mode that surfaces `nlpUnavailable` or `mlUnavailable` rather than silently pretending full parity.
- [x] Define acceptance thresholds: exact matches for operator classification, approximate matches for confidence scores, and documented divergences for predicate spans.

Acceptance criteria:

- Python ML/spaCy parity is measurable with fixtures, but runtime execution remains browser-native.
- Temporary incomplete-port behavior is explicit in API results and UI copy until browser-native parity lands.
- The TypeScript implementation can run without Python; Python-enhanced outputs may be compared only in development or CI fixture-generation workflows.

### Phase 5: F-Logic Display And Semantic Normalization

- [x] Port `FLogicFrame`, `FLogicClass`, `FLogicQuery`, and `FLogicOntology` concepts.
- [x] Parse the subset of `frame_logic_ergo` currently generated for Portland sections.
- [x] Render frames as structured tables: object, class, attributes, rules.
- [x] Normalize generated object IDs back to Portland citations when possible.

Acceptance criteria:

- F-logic strings in proof summaries can be displayed as structured metadata.
- Ergo syntax not yet ported remains available as raw source with a parse warning and a tracked parity gap.

### Phase 6: Simulated Certificate And Canonicalization Checks

- [x] Port text normalization and deterministic hashing concepts from `zkp/canonicalization.py`.
- [x] Port `Statement`, `Witness`, and `ProofStatement` shapes, dictionary serialization, circuit reference parsing/formatting, and field-element mapping from `zkp/statement.py`.
- [x] Port initial `zkp/circuits.py` circuit metadata, Boolean circuit construction, simplified R1CS export, knowledge-of-axioms constraint checks, and TDFOL v1 Horn derivation constraint checks.
- [x] Port simulated ZKP backend proof shape, demo proof layout, backend registry metadata, availability checks, and fail-closed verification semantics from `zkp/backends`.
- [x] Port initial `zkp_prover.py` and `zkp_verifier.py` browser-native facades with backend routing, proof caching, public-input validation, expected-theorem checks, and statistics.
- [x] Port `legal_theorem_semantics.py` and `witness_manager.py` browser-native TDFOL v1 Horn semantics, witness generation/validation, proof statement creation, consistency checks, and witness cache helpers.
- [x] Port `evm_public_inputs.py` browser-native BN254 field packing helpers for EVM public inputs without chain calls.
- [x] Port `vk_registry.py` and initial `eth_vk_registry_payloads.py` browser-native VK hashing, registry, bytes32 normalization, and registerVK payload validation without RPC calls.
- [x] Port `eth_contract_artifacts.py` as browser-native contract artifact object/JSON parsing for ABI and bytecode without filesystem path loading.
- [x] Add `verifySimulatedCertificate()` that checks metadata consistency only.
- [x] Rename UI language so `zkp_verified: true` with `zkp_backend: simulated` is shown as "simulated certificate present", not "cryptographically verified".

Acceptance criteria:

- The app cannot accidentally imply real cryptographic verification for simulated artifacts.
- Hash/canonicalization helpers are deterministic across browsers.
- Tests cover whitespace normalization and axiom ordering behavior.

### Phase 7: Lightweight Reasoning

- [x] Add a small in-memory `LogicKnowledgeBase` keyed by section CID.
- [x] Add bounded forward chaining for facts and simple implications.
- [x] Add contradiction hints for obvious norm conflicts: same actor/action/condition with `O` and `F`.
- [x] Add temporal summary helpers for always/eventually/next/until.
- [x] Add proof trace output for any inferred result.

Acceptance criteria:

- Reasoning is bounded by step count and time budget.
- Every inferred hint includes source sections and rule names.
- The UI labels these outputs as heuristic/local reasoning unless backed by generated artifacts.

### Phase 8: Search And GraphRAG Integration

- [x] Add logic filters to the search service layer. UI wiring is deferred to the Portland research screen.
- [x] Add norm-aware score parts to logic-aware search results.
- [x] Add proof facts to GraphRAG evidence packs.
- [x] Add prompts or answer formatting that distinguish code text, KG facts, generated formalization, and local reasoning.
- [x] Add unsupported-question handling for queries not grounded in retrieved code.

Acceptance criteria:

- Search can answer "show prohibitions about retaliation" with norm-aware results.
- GraphRAG evidence includes citations and proof metadata.
- Answers remain grounded in retrieved Portland Code sections.

### Phase 9: Python Parity Harness

- [x] Create a parity test fixture generated from selected Python outputs.
- [x] Compare TypeScript parser/formatter/converter outputs against Python outputs for fixed examples.
- [x] Add a validation command that can be run after corpus regeneration.
- [x] Track intentional divergences in a markdown table.

Acceptance criteria:

- Parity failures are visible in CI or local test output.
- The TypeScript port can evolve without silently drifting from generated artifacts.

### Phase 10: WASM Or Service Research

- [x] Evaluate whether any external prover should run in-browser via WASM.
- [x] Evaluate `z3-solver`/Z3 WASM, cvc5 WASM availability, Tau Prolog, or custom Datalog for limited use cases.
- [x] Evaluate `snarkjs` only if real browser-side proof verification becomes a product requirement.
- [x] Reject hosted runtime dependencies; use browser-native WASM only when a prover is truly required.

Acceptance criteria:

- A written decision record exists before adding heavy prover dependencies.
- Bundle-size, offline behavior, security, and legal-copy implications are documented.

### Phase 11: Full TDFOL Parity

- [x] Port every TDFOL inference rule from `logic/TDFOL/tdfol_inference_rules.py`.
  - [x] Initial first-order rule slice: universal modus ponens, existential instantiation, existential generalization, and universal generalization.
- [x] Port propositional tableaux expansion rules from `logic/TDFOL/expansion_rules.py`.
- [x] Complete proof strategies, strategy selector, performance engine, proof cache, dependency graph, proof explainer, and proof tree visualizer parity.
  - [x] Initial forward-chaining strategy and selector parity.
  - [x] Initial backward-chaining strategy parity for direct goals, conjunctive goals, and implication-goal reduction.
  - [x] Initial bidirectional strategy parity with backward-first proof search and bounded forward fallback.
  - [x] Initial modal tableaux strategy parity with local TS tableaux, modal-logic auto-selection, and priority/cost selection.
  - [x] Initial local CEC delegate replacement that translates TDFOL to browser-native CEC expressions and returns explicit unknown results instead of calling Python or a server.
  - [x] Initial indexed-KB and cache-aware optimization facade.
  - [x] Deeper CEC delegate parity for native CEC inference rule groups and proof traces.
  - [!] Browser-native ZKP acceleration and parallel proof search parity.
- [!] Complete modal tableaux and countermodel generation/visualization parity.
  - [x] Initial modal tableaux proof search for propositional, temporal, deontic modal formulas and K/T/D/S4/S5 accessibility.
  - [x] Initial countermodel model, extractor, and self-contained visual exports.
  - [x] Full expansion-rule parity, richer branch diagnostics, strategy integration, and richer interactive renderer parity.
  - [x] Modal tableaux countermodel export payloads for serializing TDFOL and CEC open branches into visualization-ready Kripke data.
- [x] Complete TDFOL security validator parity.
  - [x] Added deterministic browser-native TDFOL proof-result auditing for theorem/step integrity, non-browser runtime method leakage, premise fan-out, and proof-time budget recommendations.
- [x] Add Python parity fixtures for each TDFOL rule category.
- [x] Add browser performance budgets for proof search.
  - [x] Initial in-memory performance engine and strategy profiler.
  - [x] Initial browser performance dashboard data model and renderer.
  - [x] Initial browser performance profiler with repeated timing samples, memory snapshots, bottleneck classification, benchmark suites, and report strings.
  - [x] Full profiler/dashboard parity with browser performance timelines, flamegraph-style views, and richer bottleneck reports.

### Phase 12: Full CEC/DCEC Parity

- [x] Port CEC syntax tree, grammar loader, grammar engine, problem parser, and DCEC parsers.
  - [x] Initial browser-native CEC/DCEC s-expression AST, parser, formatter, validator, and Portland DCEC unit coverage.
  - [x] Initial CEC/DCEC expression analyzer for predicates, atoms, section refs, quantifiers, deontic operators, temporal operators, and expression complexity.
  - [x] Initial CEC ShadowProver problem parser with browser-native TPTP `fof`/`cnf` parsing, include tracking, custom `LOGIC`/`ASSUMPTIONS`/`GOALS` format parsing, format auto-detection, and parser-specific errors.
  - [x] Initial CEC syntax tree utility with typed node kinds, parent-aware construction, traversal/search helpers, transform/map/filter, JSON round-trip, leaf/height/size metrics, and ASCII pretty printing.
  - [x] Initial CEC grammar loader and engine with embedded browser-native default grammar data, static grammar-data loading, operator word/semantic/example lookup, validation, lexical entries, grammar rules, bottom-up chart parsing, ambiguity resolution, and linearization fallback.
  - [x] Initial DCEC enhanced grammar parser with DCEC grammar categories, terminals, CFG rules, parse-tree helpers, Earley-style chart states, mutable lexicon/rules, built-in deontic/cognitive/temporal grammar fragments, parse extraction, and grammar validation.
  - [x] Initial DCEC English grammar facade with browser-native lexicon/rule setup, compositional local parsing for atomic/deontic/cognitive/temporal/connective fragments, dependency-free domain-vocabulary fallback parsing, Python-style semantic dictionary linearization, semantic-to-DCEC conversion, DCEC-to-semantic conversion, formula-to-English rendering, and factory construction.
  - [x] Initial DCEC cleaning/preprocessing utilities with whitespace/comment normalization, redundant-parentheses consolidation, balanced-paren checks, matching close-paren lookup, function-call tucking, symbolic-operator functorization, and a standard cleaning pipeline.
  - [x] Initial DCEC parsing utility layer with Python-compatible parse tokens, S-expression/F-expression rendering, depth/width metrics, synonym normalization, logical prefixing, arithmetic PEMDAS prefixing, and atomic sort tracking.
  - [x] Initial DCEC type, namespace, and container layer with deontic/cognitive/logical/temporal operator constants, sort subtyping, variable/function/predicate symbols, built-in sorts, duplicate/missing-sort errors, statement labels, axioms, theorems, clear/statistics behavior, and CEC AST-compatible formulas.
  - [x] Initial DCEC core formula layer with variable/function terms, atomic/deontic/cognitive/temporal/connective/quantified formulas, Python-compatible rendering, arity validation, free-variable tracking, substitution, statement formatting, structural string equality, and convenience constructors.
  - [x] Initial DCEC integration pipeline with browser-native string-to-parse-token conversion, recursive comma-S-expression parsing, token-to-formula conversion, prefix `not` normalization, deontic/cognitive/temporal mapping, object/agent term inference, and formula validation.
  - [x] Initial DCEC prototype namespace with sort inheritance, overloaded function prototypes, atomic type definitions, text prototype parsing, base DCEC/logical/numeric vocabularies, type-conflict checks, quantifier map state, statistics, and printable snapshots.
  - [x] Initial DCEC temporal evaluator/state layer with finite-trace `ALWAYS`/`EVENTUALLY`/`NEXT`/`UNTIL`/`SINCE`/`YESTERDAY` evaluation, unary/binary arity validation, DCEC atom proposition extraction, negated-atom handling, symbolic rendering, and convenience constructors.
  - [x] Initial DCEC natural-language converter with browser-native pattern matching for deontic/cognitive/temporal/logical phrases, DCEC namespace reuse, conversion result history/statistics, formula-to-English linearization, deterministic precedence, and local dependency-free grammar placeholders.
- [x] Add CEC/DCEC parity fixtures and generated Portland DCEC parse coverage.
- [x] Port native inference rule groups: propositional, modal, temporal, deontic, cognitive, specialized, and resolution.
  - [x] Initial CEC native inference rule slice: modus ponens, conjunction elimination, double-negation elimination, temporal T, deontic D, and prohibition equivalence.
  - [x] Expanded deterministic CEC inference slice: hypothetical syllogism, conjunction introduction as an opt-in generative rule, eventuality introduction as an opt-in generative rule, prohibition-from-obligation, universal modus ponens, existential instantiation, existential generalization, and universal generalization.
  - [x] Expanded CEC temporal/deontic inference rule slice with always/eventually/next distribution and implication, temporal transitivity, always induction, temporal negation, until/since weakening, obligation/permission distribution, obligation implication, permission duality, obligation consistency, and opt-in obligation conjunction.
  - [x] Initial CEC modal inference rule group with necessity elimination, necessity distribution, possibility-necessity duality, opt-in possibility introduction, and opt-in necessity conjunction generation.
  - [x] Initial CEC cognitive inference rule group with belief/knowledge distribution, knowledge-implies-belief, belief/knowledge monotonicity, intention commitment, intention means-end, perception-to-knowledge, belief negation, intention persistence, belief revision, and opt-in belief/knowledge conjunction generation.
  - [x] Initial CEC resolution inference rule group with binary resolution, unit resolution, factoring, subsumption, case analysis/disjunction elimination, proof-by-contradiction signaling, and three-premise rule enumeration.
  - [x] Initial CEC specialized inference rule group with biconditional introduction/elimination, constructive/destructive dilemma, exportation, absorption, tautology simplification, conjunction commutativity, and opt-in addition/disjunction introduction.
  - [x] Expanded CEC extended prover-core rule parity with disjunction commutativity, distribution, association, transposition, material implication round-tripping, Clavius law, and conjunction/disjunction idempotence.
  - [x] Expanded CEC common-knowledge/common-belief rule parity with common knowledge/belief introduction, common knowledge distribution, common-knowledge-to-knowledge, monotonicity, negation, transitivity, fixed-point induction, temporally induced common knowledge, and modal necessitation introduction.
- [x] Port event calculus, fluents, context manager, ambiguity resolver, shadow prover, and modal tableaux.
  - [x] Initial CEC fluent/event state manager with fluent types, persistence rules, event transitions, frame-problem persistence, conflict resolution, timelines, statistics, and validation.
  - [x] Initial CEC event calculus with browser-native discrete event occurrences, initiation/termination/release rules, `Happens`, `Initiates`, `Terminates`, `Releases`, `ReleasedAt`, `HoldsAt`, `Clipped`, parsed predicate loading/evaluation, timelines, all-fluent queries, caching, and validation.
  - [x] Initial CEC context manager with discourse state, entity tracking, focus management, pronoun/anaphora resolution, parsed CEC expression ingestion, discourse segmentation, coherence scoring, snapshots, and validation.
  - [x] Initial CEC ambiguity resolver with syntax-tree adapters, minimal-attachment/right-association/balance scoring, ranked parse explanations, custom preference rules, semantic pattern scoring, statistical bigram scoring, and CEC AST-to-tree conversion.
  - [x] Initial CEC ShadowProver facade with K/T/D/S4/S5 local modal tableaux, forward-prover fallback, problem-object proving, proof cache/statistics, direct-assumption proofs, unsupported-LP diagnostics, and browser-native cognitive rule subset.
  - [x] Initial CEC modal tableaux with K/T/D/S4/S5 world/branch model, contradiction closure, box/diamond expansion, deontic O/P/F mapping, proof steps, and open-branch countermodel support.
  - [x] Initial CEC countermodel extraction and visualization from open tableaux branches with Kripke JSON, DOT, ASCII, compact ASCII, HTML, valuation extraction, and modal property checks.
- [x] Port CEC proof cache, proof strategies, advanced inference, and error handling.
  - [x] Initial CEC native shared-type layer with Python `types.py`-style formula/proof/conversion/namespace/config dictionaries, protocol guards for formulas/provers/converters/knowledge bases, generic result/cache/stat records, callable aliases, and unified proof statistics with incremental averages.
  - [x] Initial DCEC advanced inference layer with modal K/T/S4/necessitation, temporal induction/frame, deontic D/permission-obligation/distribution, knowledge-obligation interaction, temporal-obligation persistence, and grouped rule registries.
  - [x] Initial CEC native error-handling layer with CEC-specific parse/proof/conversion/validation/namespace/grammar/knowledge-base errors, Python-style context/suggestion formatting, safe-call wrappers, parse/proof handler wrappers, operation error formatting, and DCEC formula-shape validation.
  - [x] Initial CEC lemma-generation layer with reusable lemma objects, deterministic pattern hashing, LRU lemma cache, pattern lookup, proof-tree lemma discovery, cached lemma reuse during CEC proving, discovery/reuse statistics, and clear/reset behavior.
  - [x] Initial CEC proof-optimization layer with proof-node trees, depth/redundancy pruning, optimization metrics, duplicate/subsumption elimination, browser-native async batch search, combined optimizer coordination, and metrics export.
  - [x] Initial CEC/ZKP integration layer with unified standard/ZKP/cached proof results, simulated educational CEC ZKP certificates, private axiom hiding, deterministic browser Web Crypto commitments, local standard fallback, cache-first hybrid proving, statistics, clear/reset helpers, and explicit non-cryptographic simulated-backend language.
  - [x] Initial bounded CEC forward prover with proof steps, unknown results, and derived-expression budget handling.
  - [x] Initial CEC prover support for Portland-style quantified DCEC facts through browser-native universal modus ponens, without Python delegation.
  - [x] Initial CEC proof cache with normalized theorem/axiom keys, prover-config sensitivity, invalidation, global helper, TTL/LRU stats, and cached prove facade.
  - [x] Initial CEC strategy selector with forward and cached-forward strategies, priority/cost selection, metadata, and convenience proving facade.
  - [x] Expanded CEC proof strategy parity with backward chaining, bidirectional backward-first/forward-fallback search, hybrid adaptive strategy selection using Python axiom-count heuristics, Python-style strategy factory, strategy costs, and direct/cached default selection.
  - [x] Initial CEC proof explainer with rule descriptions, natural-language steps, inference chains, rendered text, and proof statistics.
  - [x] Initial CEC dependency graph and proof tree visualizer with JSON, DOT, HTML, ASCII, topological order, path lookup, and unused-axiom diagnostics.
  - [x] Initial CEC performance metrics and engine with timing collectors, strategy profiling, dashboard HTML export, JSON/Prometheus-style export, regression checks, and profiler history.
  - [x] Initial CEC performance dashboard with proof metrics, time-series metrics, expression classification, aggregate stats, strategy comparison, JSON export, and self-contained HTML.
  - [x] Initial CEC performance profiler with repeated-run profiling, bottleneck detection, browser memory snapshots, benchmark suites, baseline regression accounting, and text/JSON/HTML reports.
  - [x] Initial CEC security validator and error-hardening facade with rate limits, input sanitization, size/depth/operator guards, injection/DoS detection, parse validation, resource checks, proof-result audit, and security reports.
- [x] Port CEC NL policy compilers and language detection with browser-native NLP.
- [x] Add deeper CEC/DCEC parity fixtures against Python parser and prover outputs.

### Phase 13: Browser-Native ML/NLP Parity

- [x] Replace spaCy extraction with browser-native NLP: Transformers.js token classification, dependency-light NLP, ONNX/WebGPU, or WASM NLP.
- [x] Port `ml_confidence.py` to local browser inference or an equivalent deterministic TypeScript model.
- [x] Add local model artifact loading, caching, versioning, and unload controls.
- [x] Add exact/tolerance parity tests against Python ML/spaCy development fixtures.
- [!] Remove `nlpUnavailable` and `mlUnavailable` capability flags once browser-native parity is implemented.

### Phase 14: External Provers And ZKP WASM Parity

- [x] Port external prover router and bridge contracts to local browser adapters.
- [x] Evaluate and integrate local WASM provers for Z3/cvc5/Tau Prolog/Lean/Coq-style workflows where feasible.
- [x] Port Groth16 verification/proving path using browser-native cryptographic libraries where feasible.
- [x] Port EVM/public-input/vk-registry helpers using browser-compatible crypto and chain libraries.
- [x] Add strict UI/API language distinguishing simulated, heuristic, proof-checking, and cryptographic outputs.

### Phase 15: Integration, Security, Observability, And Developer Tools

- [x] Port logic integration bridges to route to TS/WASM cores.
  - [x] Initial browser-native bridge facade for local route inventory, FOL/deontic/TDFOL/CEC conversion routing, TDFOL/CEC proof routing, and explicit unsupported-route results with `server_calls_allowed: false`.
  - [x] Port deeper domain-specific integration bridges, interactive workflows, and parity fixtures.
- [x] Port security input validation, circuit breaker, rate limiting, and audit-log semantics to browser-local equivalents.
- [x] Port observability structured logging, Prometheus-style metrics, and OTel-style tracing to browser-local equivalents.
- [x] Port monitoring/metrics to in-browser telemetry objects and developer panels.
  - [x] Initial top-level `logic/monitoring.py` parity for operation metrics, tracking helpers, health checks, error/warning counters, global monitor, reset, operation summaries, and optional Prometheus text export.
  - [x] Add richer developer-panel integration for live UI inspection.
- [x] Replace Python API/CLI surfaces with TypeScript developer scripts or browser devtools.
  - [x] Initial browser-native public API facade for `logic/api.py` import-surface parity.
  - [x] Add CLI/devtools command adapter parity for `logic/cli.py`.
- [x] Port IPFS/IPLD proof cache semantics to browser-native storage/IPFS clients where possible.

## Full-Port Completion Definition

The port is complete only when every Python logic capability has one of these browser-native outcomes:

- TypeScript implementation with parity tests.
- WebAssembly/browser-library implementation with parity tests.
- Tracked incomplete capability with a blocking issue, temporary capability flag, and no silent fallback.

Python may remain as a fixture generator and source reference, but not as a production runtime dependency.

## TypeScript Port Estimate

Current completed TypeScript/WASM port slice:

- 100 percent of shared types needed by the UI.
- 75-85 percent of common module behavior: cache, converter lifecycle, browser feature detection, proof cache, utility monitoring, validation, and error surfaces.
- 100 percent of proof summary loading, indexing, validation, and display helpers.
- 80-90 percent of TDFOL core AST/parser/formatter behavior needed for generated Portland formulas.
- 70-80 percent of TDFOL inference/prover/explanation/operations behavior: initial converter outputs, propositional, first-order, temporal, deontic rules, tableaux expansion rules, bounded forward/backward/bidirectional chaining, local CEC delegation, modal tableaux, strategy selection, indexed-KB optimization, countermodels, proof explanations, dependency graphs, proof tree views, security validation, metrics collection, profiling, dashboarding, and performance-engine orchestration.
- 75-85 percent of regex FOL/deontic extraction, formatter, analyzer, and knowledge-base behavior, focused on legal-code clauses.
- 70-80 percent of F-logic data modeling and display rendering for generated frame snippets.
- 50-60 percent of ZKP canonicalization/statement metadata behavior.
- 10-20 percent of prover behavior, currently limited to bounded local reasoning and explanation traces.

Remaining full-port work:

- Full CEC native prover parity.
- Full TDFOL prover parity across all inference rules.
- External prover bridge parity through browser-native WASM/local packages.
- Cryptographic proof generation and verification through browser-native libraries.
- Python NLP/ML parity through browser-native NLP/ML implementations.

## Python-To-TypeScript Parity Matrix

This matrix is the current browser-native parity ledger for the Python logic tree. It maps Python module groups to TypeScript/WASM runtime files, validation evidence, accepted daemon work, and remaining local-only tasks. The machine-readable form is exported by `src/lib/logic/pythonLogicInventory.ts` through `buildLogicPortParityMatrix()` and exercised by `src/lib/logic/pythonLogicInventory.test.ts`.

| Python logic modules | TypeScript/WASM runtime files | Validation evidence | Accepted work | Remaining browser-native tasks |
| --- | --- | --- | --- | --- |
| `logic/fol`, `logic/deontic` | `src/lib/logic/fol`, `src/lib/logic/deontic`, `src/lib/logic/mlConfidence.ts` | `src/lib/logic/fol/converter.test.ts`, `src/lib/logic/deontic/parser.test.ts`, `src/lib/logic/mlConfidence.test.ts`, `src/lib/logic/parity/parity.test.ts` | FOL and spaCy-style NLP extraction; ML confidence scoring; CEC, DCEC, and deontic reasoning | Load optional browser-native model artifacts for trained ML/spaCy-equivalent behavior. |
| `logic/TDFOL` | `src/lib/logic/tdfol`, `src/lib/logic/modalTableaux.ts` | `src/lib/logic/tdfol/prover.test.ts`, `src/lib/logic/tdfol/modalTableaux.test.ts`, `src/lib/logic/modalTableaux.test.ts` | CEC, DCEC, and deontic reasoning | Replace remaining P2P, dashboard, and visualization helper surfaces with browser-local state and serializable exports. |
| `logic/CEC`, `logic/integration` | `src/lib/logic/deontic`, `src/lib/logic/integration` | `src/lib/logic/integration/bridge.test.ts`, `src/lib/logic/integration/coreBridge.test.ts`, `src/lib/logic/integration/domain/deonticQueryEngine.test.ts` | CEC, DCEC, and deontic reasoning | Complete browser-native CEC grammar loading, cognitive/modal rule groups, namespace diagnostics, and selected native prover behavior. |
| `logic/zkp` | `src/lib/logic/zkp`, `src/lib/logic/groth16.ts` | `src/lib/logic/zkp/facade.test.ts`, `src/lib/logic/zkp/witnessManager.test.ts`, `src/lib/logic/groth16.test.ts` | ZKP and verifier surfaces | Finish browser crypto and chain-library parity for Groth16, EVM public inputs, and VK registry helpers. |
| `logic/external_provers`, top-level operational modules | `src/lib/logic/integration/proverAdapters.ts`, `src/lib/logic/cli.ts`, `src/lib/logic/monitoring.ts`, `src/lib/logic/security` | `src/lib/logic/cli.test.ts`, `src/lib/logic/monitoring.test.ts`, `src/lib/logic/security/security.test.ts` | Public API, CLI/devtools, config, monitoring, and security | Map remaining external prover routing to WASM-capable local adapters or explicit unsupported-local results; convert remaining benchmark and validation script behavior into browser/devtools TypeScript entry points. |

## Testing Strategy

Unit tests:

- Proof summary schema guards and indexes.
- TDFOL tokenization, parsing, formatting, substitution, and free-variable analysis.
- FOL quantifier/operator parsing and predicate normalization.
- Deontic phrase extraction and norm classification.
- F-logic frame parsing/rendering.
- ZKP canonicalization and simulated verification wording.
- Cache TTL/LRU behavior.

Integration tests:

- Load corpus plus logic proofs and join by CID.
- Search with norm filters.
- Build a GraphRAG evidence pack with logic metadata.
- Validate generated proof summaries and report parse failures.

Playwright tests:

- Proof panel renders on desktop and mobile.
- Search filters do not overlap or resize unexpectedly.
- Raw and structured logic views remain readable for long formulas.
- Simulated certificate copy is visible where relevant.

Parity tests:

- Fixed fixtures from `ipfs_datasets_py` outputs.
- Generated Portland proof summary samples.
- Round-trip normalized formulas.
- Known failures documented instead of ignored.

## Risk Register

| Risk | Mitigation |
| --- | --- |
| Porting the entire Python module creates a large browser bundle. | Preserve the full parity target, but split implementations with dynamic imports, optional local model artifacts, and WASM chunks. |
| Formalization output may be machine-generated and imperfect. | Label all logic artifacts as candidate formalizations and keep original legal text primary. |
| Simulated ZKP metadata may be mistaken for real crypto verification. | Use explicit UI copy and API names such as `verifySimulatedCertificate`. |
| Parser parity may drift from Python. | Add fixture-based parity tests and document intentional differences. |
| TDFOL syntax includes Unicode operators. | Support both symbolic and ASCII aliases; normalize internally. |
| External prover expectations may creep into client code. | Define a `ProverBackend` interface and route only to browser-native TypeScript/WASM adapters. |
| Licensing may affect reuse. | Review `ipfs_datasets_py/LICENSE` and this repo's `LICENSE` before copying substantive code. Prefer clean-room TypeScript where needed. |

## Documentation Deliverables

- `docs/IPFS_DATASETS_LOGIC_TYPESCRIPT_PORT_PLAN.md`: this plan.
- `docs/LOGIC_ARTIFACT_SCHEMA.md`: generated proof summary schema and examples.
- `docs/LOGIC_PORT_PARITY.md`: Python-to-TypeScript parity matrix and divergences.
- `docs/LOGIC_REASONING_LIMITATIONS.md`: user-facing limitations, safety notes, and certificate wording.
- `docs/LOGIC_WASM_RESEARCH.md`: decision record for any prover or crypto WASM dependency.

## Recommended First Pull Request

The first implementation PR should be intentionally small:

1. Add `src/lib/portlandLogic.ts`.
2. Add TypeScript proof summary types and lazy loader.
3. Add indexes by CID, identifier, norm operator, and norm type.
4. Add validation with warnings for simulated certificates.
5. Add Jest tests using a tiny fixture.
6. Add a minimal proof metadata panel to the existing Portland section detail UI, if that UI is already ready.

That PR gives the project immediate product value without committing to a full theorem prover port.


## Daemon-Discovered Implementation Gaps

Last replenished: 2026-05-02 06:31:29 UTC

These tasks were added automatically after the daemon found no eligible unchecked port-plan items. They are derived from the current Python logic inventory, TypeScript/WASM implementation state, accepted-work evidence, and the original browser-native parity goal.

- [x] Port remaining Python logic module `logic/CEC/cec_framework.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/dcec_wrapper.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/eng_dcec_wrapper.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/advanced_inference.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/ambiguity_resolver.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/cec_proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/cec_zkp_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/context_manager.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/dcec_cleaning.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/dcec_core.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/dcec_english_grammar.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/dcec_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/dcec_namespace.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/dcec_parsing.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/dcec_prototypes.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/dcec_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/enhanced_grammar_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/error_handling.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/event_calculus.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/exceptions.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/grammar_engine.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/grammar_loader.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/inference_rules/base.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/inference_rules/cognitive.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/inference_rules/deontic.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/inference_rules/modal.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/inference_rules/propositional.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/inference_rules/resolution.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/inference_rules/specialized.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/lemma_generation.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/modal_tableaux.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/nl_converter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/problem_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/proof_optimization.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/proof_strategies.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/CEC/native/prover_core.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/prover_core_extended_rules.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/shadow_prover.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/native/syntax_tree.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/base_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/dcec_to_ucan_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/domain_vocabularies/domain_vocab.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/french_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/german_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/grammar_nl_policy_compiler.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/language_detector.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/nl_policy_conflict_detector.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/nl_to_policy_compiler.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/portuguese_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/nl/spanish_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/optimization/formula_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/optimization/profiling_utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/provers/e_prover_adapter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/provers/prover_manager.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/provers/tptp_utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/provers/vampire_adapter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/provers/z3_adapter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/shadow_prover_wrapper.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/CEC/talos_wrapper.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/countermodel_visualizer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/demonstrate_countermodel_visualizer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/demonstrate_performance_dashboard.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/example_formula_dependency_graph.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/example_performance_profiler.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/exceptions.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/expansion_rules.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/formula_dependency_graph.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/inference_rules/base.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/inference_rules/deontic.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/inference_rules/first_order.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/inference_rules/propositional.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/inference_rules/temporal_deontic.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/modal_tableaux.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/demonstrate_ipfs_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/llm.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/tdfol_nl_api.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/tdfol_nl_context.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/tdfol_nl_generator.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/tdfol_nl_patterns.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/tdfol_nl_preprocessor.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/nl/utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/p2p/ipfs_proof_storage.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/performance_dashboard.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/performance_metrics.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/performance_profiler.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/proof_explainer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/proof_tree_visualizer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/quickstart_visualizer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/security_validator.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/strategies/base.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/strategies/cec_delegate.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/strategies/forward_chaining.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/strategies/modal_tableaux.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/strategies/strategy_selector.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_converter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_core.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_dcec_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_inference_rules.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_optimization.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_performance_engine.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/tdfol_prover.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/TDFOL/zkp_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/api_server.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/batch_processing.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/cli.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/common/bounded_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/common/feature_detection.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/common/proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/common/utility_monitor.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/common/validators.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/decoder.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/exports.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/formula_builder.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/ir.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/knowledge_base.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/legal_text_to_deontic.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/metrics.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/prover_syntax.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/support_map.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/deontic/utils/deontic_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/e2e_validation.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/external_provers/formula_analyzer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [!] Port remaining Python logic module `logic/external_provers/interactive/coq_prover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/external_provers/interactive/lean_prover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/external_provers/neural/symbolicai_prover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/external_provers/proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/external_provers/prover_router.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/external_provers/smt/cvc5_prover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/external_provers/smt/z3_prover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/flogic/ergoai_wrapper.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/flogic/flogic_proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/flogic/flogic_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/flogic/flogic_zkp_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/flogic/semantic_normalizer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/fol/text_to_fol.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/fol/utils/deontic_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/fol/utils/fol_parser.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/fol/utils/logic_formatter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/fol/utils/nlp_predicate_extractor.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/fol/utils/predicate_extractor.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/base_prover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/bridges/base_prover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/bridges/external_provers.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/bridges/prover_installer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/bridges/symbolic_fol_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/bridges/tdfol_cec_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/bridges/tdfol_grammar_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/bridges/tdfol_shadowprover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/caching/ipfs_proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/caching/ipld_logic_storage.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/caching/proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/cec_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/converters/deontic_logic_converter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/converters/deontic_logic_core.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/converters/logic_translation_core.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/converters/modal_logic_extension.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/converters/symbolic_fol_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/demos/demo_temporal_deontic_rag.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/deontic_logic_converter.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/deontic_logic_core.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/caselaw_bulk_processor.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/deontic_query_engine.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/document_consistency_checker.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/legal_domain_knowledge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/legal_symbolic_analyzer.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/medical_theorem_framework.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/symbolic_contracts.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/temporal_deontic_api.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/domain/temporal_deontic_rag_store.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/interactive/_fol_constructor_io.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/interactive/interactive_fol_constructor.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/interactive/interactive_fol_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/interactive/interactive_fol_utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/interactive_fol_constructor.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/logic_translation_core.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/logic_verification.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/logic_verification_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/logic_verification_utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/modal_logic_extension.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/neurosymbolic.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/neurosymbolic_graphrag.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/nl_ucan_policy_compiler.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/proof_cache.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/_deontic_conflict_mixin.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/_logic_verifier_backends_mixin.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/_prover_backend_mixin.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/deontological_reasoning.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/deontological_reasoning_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/deontological_reasoning_utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/logic_verification.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/logic_verification_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/logic_verification_utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/proof_execution_engine.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/proof_execution_engine_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/reasoning/proof_execution_engine_utils.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic/neurosymbolic/embedding_prover.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic/neurosymbolic/hybrid_confidence.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic/neurosymbolic/reasoning_coordinator.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic/neurosymbolic_api.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic/neurosymbolic_graphrag.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic/symbolic_logic_primitives.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic_contracts.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic_fol_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/symbolic_logic_primitives.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/tdfol_cec_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/tdfol_grammar_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/tdfol_shadowprover_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integration/ucan_policy_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integrations/enhanced_graphrag_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integrations/phase7_complete_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/integrations/unixfs_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/ml_confidence.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/observability/metrics_prometheus.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/observability/otel_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/observability/structured_logging.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/phase7_4_benchmarks.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/security/audit_log.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/security/input_validation.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/security/llm_circuit_breaker.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/security/rate_limiting.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/types/bridge_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/types/common_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/types/deontic_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/types/fol_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/types/proof_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/types/translation_types.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/backends/backend_protocol.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/backends/groth16_backup.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/backends/groth16_ffi.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/backends/simulated.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/eth_contract_artifacts.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/eth_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/eth_vk_registry_payloads.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/evm_harness.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/evm_public_inputs.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/examples/zkp_advanced_demo.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/examples/zkp_basic_demo.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/examples/zkp_ipfs_integration.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/legal_theorem_semantics.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/onchain_pipeline.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/setup_artifacts.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/ucan_zkp_bridge.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/vk_registry.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/witness_manager.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/zkp_prover.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Port remaining Python logic module `logic/zkp/zkp_verifier.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.
- [x] Replace remaining `nlpUnavailable` capability paths with browser-native NLP parity or explicit local model artifact loading.
- [x] Replace remaining `mlUnavailable` capability paths with browser-native ML confidence parity or explicit local model artifact loading.
- [x] Audit remaining TypeScript logic `unsupported` paths and convert feasible ones into browser-native TypeScript/WASM implementations.
- [x] Reconcile the Python logic inventory (269 files) with the TypeScript/WASM implementation (253 files) and add browser-native port tasks for uncovered behavior.
  - Reconciliation source: `src/lib/logic/pythonLogicInventory.ts`.
  - Uncovered behavior tasks added from the 16-file gap:
    - Port CEC native grammar loader and external grammar registry semantics to deterministic in-memory TypeScript artifacts.
    - Complete CEC cognitive, deontic, modal, and base inference-rule parity using browser-native rule tables.
    - Port CEC native error-handling and namespace diagnostics as fail-closed TypeScript validation results.
    - Replace TDFOL P2P, dashboard, and visualization helper surfaces with browser-local state and serializable exports.
    - Map remaining external prover routing modules to WASM-capable local adapters or explicit unsupported-local results.
    - Convert remaining operational benchmark and validation script behavior into browser/devtools TypeScript entry points.
- [x] Review the accepted TypeScript logic changes against the original browser-native TypeScript/WASM port goal, then add or implement any missing parity tasks for Python logic behavior that lacks accepted-work evidence.
  - Review source: `src/lib/logic/pythonLogicInventory.ts` now maps accepted-work evidence for FOL/NLP, ML confidence, ZKP/verifier, CEC/DCEC/deontic, and public API/security surfaces back to runtime and validation files.
  - Missing parity tasks remain explicit from the 16-file inventory gap and retain browser-native/no-server/no-Python constraints for subsequent implementation cycles.
- [x] Add end-to-end browser-native validation proving the converted logic runs without Python, spaCy, or server-side calls, including deterministic coverage for ML and NLP capability surfaces.
- [x] Audit Python ML and spaCy expectations against the TypeScript/WASM implementation and add focused parity tests or local-model artifact loading tasks for unsupported browser-native behavior.
- [x] Refresh the TypeScript port plan with a parity matrix mapping Python logic modules, TypeScript/WASM files, validation evidence, accepted work, and remaining browser-native tasks.
- [x] Compare TypeScript logic public exports against Python logic module public APIs and add missing browser-native compatibility adapters or parity tests.
- [x] Port remaining Python logic module `logic/zkp/form_circuit.py` to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.

## Manual Unblock Queue

Last unblocked: 2026-05-05 05:00 UTC

The daemon completed all currently eligible TypeScript port-plan checkboxes, then stopped with only blocked items remaining. These recovery slices intentionally create fresh task labels for capabilities that were blocked under older router, patch, or validation conditions. Each item must land a small browser-native TypeScript/WASM-compatible implementation slice with focused tests, no Python runtime dependency, and no external server-side calls. When a slice proves parity for an older blocked item, update the older item as complete or replace it with the next concrete gap.

- [x] Manual unblock: implement a browser-native TDFOL ZKP acceleration scheduler slice with worker-safe proof-search queues, deterministic simulated prover fallback, and tests covering parallel-search metadata without requiring server crypto.
- [x] Manual unblock: complete a modal tableaux countermodel export slice that turns proof search branches into serializable visualization data and validates it against existing TDFOL/CEC examples.
- [x] Manual unblock: add a TDFOL security validator parity slice covering fail-closed formula, proof-cache, witness, and ZKP input checks in browser-safe TypeScript.
- [x] Manual unblock: port the next deterministic `ml_confidence.py` parity slice with fixture-backed scoring, calibration metadata, and local browser execution only.
- [x] Manual unblock: add local model artifact manifest, cache lifecycle, version checks, and unload controls for browser-native ML/NLP parity without server calls.
- [x] Manual unblock: remove the next `nlpUnavailable` or `mlUnavailable` capability path by replacing it with local TypeScript/WASM, Transformers.js, ONNX/WebGPU, or deterministic fixture parity.
- [x] Manual unblock: complete an EVM public-input and verification-key registry helper slice using browser-compatible crypto abstractions and deterministic tests.
- [x] Manual unblock: add developer-panel live inspection snapshots for logic parse, proof, cache, ML/NLP, and ZKP capability state.
- [x] Manual unblock: add CLI/devtools command adapter parity for `logic/cli.py` as browser/devtools-safe TypeScript entry points.
- [x] Manual unblock: port IPFS/IPLD proof cache semantics to browser-native storage and content-addressed cache adapters with deterministic tests.
- [x] Manual unblock: port `logic/CEC/native/advanced_inference.py` by adding a TypeScript advanced-inference registry, rule classification helpers, and parity tests for cognitive, modal, and deontic rule selection.
- [x] Manual unblock: port `logic/CEC/native/cec_proof_cache.py` by adding CEC proof cache keys, TTL/LRU behavior, validation metadata, and deterministic browser storage tests.
- [x] Manual unblock: port `logic/CEC/native/cec_zkp_integration.py` by adding an educational local ZKP integration facade with simulated backend parity and fail-closed unsupported-backend results.
- [x] Manual unblock: port `logic/CEC/native/context_manager.py` by adding discourse/context snapshots, entity bindings, temporal scopes, and deterministic merge/rollback tests.
- [x] Manual unblock: port `logic/CEC/native/dcec_cleaning.py` by adding DCEC text/formula normalization, token cleanup, and fixture tests for malformed legal-text inputs.
- [x] Manual unblock: port `logic/CEC/native/dcec_integration.py` by adding DCEC token/formula conversion helpers, CEC bridge metadata, and round-trip validation tests.
- [x] Manual unblock: port `logic/CEC/native/dcec_namespace.py` by adding namespace registration, symbol statistics, validation diagnostics, and collision tests.
- [x] Manual unblock: port `logic/CEC/native/dcec_parsing.py` by adding parser utility parity for DCEC atom, connective, quantifier, and modal/deontic forms.
- [x] Manual unblock: port `logic/CEC/native/dcec_prototypes.py` by adding prototype/type-conflict checks and deterministic validation fixtures.
- [x] Manual unblock: port `logic/CEC/native/dcec_types.py` by adding DCEC container helpers, type guards, serialization, and compatibility tests.
- [x] Manual unblock: port `logic/CEC/native/enhanced_grammar_parser.py` by adding chart-parser style diagnostics, parse alternatives, and grammar fixture tests.
- [!] Manual unblock: port `logic/CEC/native/error_handling.py` by adding fail-closed CEC error facades, recovery metadata, and validation result adapters.
- [x] Manual unblock: port `logic/CEC/native/event_calculus.py` by adding event, fluent, happens, holds, initiates, terminates, and timeline query helpers with parity tests.
- [x] Manual unblock: port `logic/CEC/native/grammar_engine.py` and `grammar_loader.py` by adding deterministic in-memory grammar artifacts, loader validation, and no-network browser tests.
- [x] Manual unblock: port `logic/CEC/native/inference_rules/base.py`, `cognitive.py`, and `modal.py` by adding rule tables, applicability checks, proof-step metadata, and focused parity tests.
- [!] Manual unblock: port `logic/CEC/native/prover_core.py` by adding a bounded browser-native proof facade, deterministic search limits, proof summaries, and failure diagnostics.
- [x] Manual unblock: port `logic/external_provers/interactive/coq_prover_bridge.py` by adding a local adapter contract that reports WASM-capable support when available and fail-closed unsupported-local results otherwise.

<!-- logic-port-daemon-task-board:start -->
## Daemon Task Board

Last updated: 2026-05-05 09:30:41 UTC

Selection policy: choose the first needed or in-progress port-plan checkbox; if none remain, revisit blocked checkboxes with `fewest-failures` strategy because blocked-task revisit mode is enabled.

Current target: `Task checkbox-202: Port remaining Python logic module 'logic/CEC/native/cec_proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`

Legend: `[ ]` needed, `[~]` in progress, `[x]` complete, `[!]` blocked or failing.

### Checklist

- [x] `Task checkbox-1: Add this plan to 'docs/'.` - complete
- [x] `Task checkbox-2: Record the exact generated proof summary schema from 'public/corpus/portland-or/current/generated/logic-proof-summaries.json'.` - complete
- [x] `Task checkbox-3: Add a small script or test fixture with 10 representative proof summaries: obligation, permission, prohibition, parse success, parse failure, simulated certificate, missing logic, long F-logic, citation match, KG-linked section.` - complete
- [x] `Task checkbox-4: Decide whether logic code lives in 'src/lib/logic/' or a package-style 'src/logic/'.` - complete
- [x] `Task checkbox-5: Add 'src/lib/portlandLogic.ts'.` - complete
- [x] `Task checkbox-6: Add 'LogicProofSummary' and related enums/unions.` - complete
- [x] `Task checkbox-7: Implement 'loadLogicProofSummaries()', 'getLogicProofForSection()', and summary count helpers.` - complete
- [x] `Task checkbox-8: Cache the loaded proof summaries like the existing corpus service does.` - complete
- [x] `Task checkbox-9: Add Jest tests for loading, indexing, and missing-section behavior.` - complete
- [x] `Task checkbox-10: Port common logic enums and data shapes from 'logic/types'.` - complete
- [x] `Task checkbox-11: Add 'LogicError', 'LogicParseError', 'LogicValidationError', and 'LogicVerificationError'.` - complete
- [x] `Task checkbox-12: Port 'logic/config.py' dataclass-style prover/cache/security/monitoring config defaults, 'to_dict' output, object loading, and explicit env-record loading without browser runtime filesystem/YAML/process dependencies.` - complete
- [x] `Task checkbox-13: Port 'logic/common/validators.py' formula string, axiom list, logic system, timeout, and format validators with Python-style validation errors.` - complete
- [x] `Task checkbox-14: Port bounded TTL/LRU cache for parsed formulas.` - complete
- [x] `Task checkbox-15: Port 'logic/batch_processing.py' batch result stats, bounded async processing, FOL conversion batches, local bridge proof batches, and chunked large-batch aggregation in browser-native TypeScript.` - complete
- [x] `Task checkbox-16: Port 'logic/benchmarks.py' benchmark result stats, sync/async timing runners, comparison, summaries, local FOL benchmark suite, local proof-cache benchmark suite, and comprehensive benchmark runner.` - complete
- [x] `Task checkbox-17: Port initial 'logic/api.py' public facade with stable browser-native conversion/proof wrappers, Python-compatible aliases, monitoring integration, local benchmark entrypoint, and explicit unsupported UCAN-signing result.` - complete
- [x] `Task checkbox-18: Port 'logic/common/converters.py' lifecycle concepts: conversion statuses, standardized results, validation, local cache, batch conversion, async wrapper, and chained converters.` - complete
- [x] `Task checkbox-19: Port browser-native 'logic/common/proof_cache.py' concepts: deterministic content IDs, prover-specific lookup, TTL, LRU eviction, invalidation, global cache, and stats.` - complete
- [x] `Task checkbox-20: Port browser-native 'logic/common/feature_detection.py' and 'logic/common/utility_monitor.py' concepts without importing Python-only optional dependencies.` - complete
- [x] `Task checkbox-21: Add schema guards for proof summary fields.` - complete
- [x] `Task checkbox-22: Add normalization helpers for identifiers, predicate names, and citations.` - complete
- [x] `Task checkbox-23: Port the TDFOL term/formula model from 'tdfol_core.py'.` - complete
- [x] `Task checkbox-24: Port tokenization and recursive descent parsing from 'tdfol_parser.py'.` - complete
- [x] `Task checkbox-25: Port initial 'tdfol_converter.py' browser converter for stable TDFOL, FOL projection, DCEC s-expression, TPTP, JSON, metadata, and batch conversion.` - complete
- [x] `Task checkbox-26: Support ASCII and symbolic operator aliases where feasible.` - complete
- [x] `Task checkbox-27: Format ASTs back to compact source and display-friendly JSON.` - complete
- [x] `Task checkbox-28: Implement free variable analysis and basic substitution.` - complete
- [x] `Task checkbox-29: Port initial 'TDFOL/inference_rules' browser-native rule interface and deterministic propositional, temporal, deontic, and first-order rules.` - complete
- [x] `Task checkbox-30: Port 'expansion_rules.py' browser-native rule registry for AND, OR, IMPLIES, IFF, and NOT tableaux expansions.` - complete
- [x] `Task checkbox-31: Port initial 'tdfol_prover.py' forward-chaining proof engine with step and derived-formula budgets.` - complete
- [x] `Task checkbox-32: Port initial 'TDFOL/strategies/base.py', 'forward_chaining.py', 'backward_chaining.py', 'bidirectional.py', 'modal_tableaux.py', 'cec_delegate.py', and 'strategy_selector.py' browser strategy layer with priority/cost selection.` - complete
- [x] `Task checkbox-33: Port initial 'tdfol_optimization.py' browser facade with indexed KB, cache-aware proving, strategy heuristics, and optimization stats.` - complete
- [x] `Task checkbox-34: Port initial 'modal_tableaux.py' browser tableaux core for K/T/D/S4/S5, branch expansion, closure checks, modal worlds, and countermodel-compatible open branches.` - complete
- [x] `Task checkbox-35: Port initial 'countermodels.py' and 'countermodel_visualizer.py' browser equivalents for Kripke structures, branch extraction, DOT/JSON/ASCII/HTML exports, and modal property checks.` - complete
- [x] `Task checkbox-36: Port initial 'proof_explainer.py', 'formula_dependency_graph.py', and 'proof_tree_visualizer.py' browser equivalents for text, JSON, DOT, HTML, ASCII tree, and graph exports.` - complete
- [x] `Task checkbox-37: Port initial 'security_validator.py' browser equivalents for formula validation, rate limiting, resource limits, sanitization, ZKP audit checks, and security reports.` - complete
- [x] `Task checkbox-38: Port initial 'performance_metrics.py' browser metrics collector for timings, memory samples, counters, gauges, histograms, summaries, and exports.` - complete
- [x] `Task checkbox-39: Port initial 'performance_profiler.py' browser profiler for repeated timing samples, optional browser memory snapshots, bottleneck classification, benchmark suites, and text/JSON/HTML reports.` - complete
- [x] `Task checkbox-40: Port initial 'performance_dashboard.py' browser dashboard for proof metrics, time-series metrics, aggregation, strategy comparison, JSON export, and self-contained HTML.` - complete
- [x] `Task checkbox-41: Port initial 'tdfol_performance_engine.py' browser engine for metrics aggregation, profiling operations, dashboard HTML strings, statistics export, strategy comparison, regression checks, and reset.` - complete
- [x] `Task checkbox-42: Add fixtures from generated Portland formulas.` - complete
- [x] `Task checkbox-43: Port regex-based quantifier and logical operator parsing from 'fol/utils/fol_parser.py'.` - complete
- [x] `Task checkbox-44: Port 'fol/utils/predicate_extractor.py' regex predicate, relation, and variable extraction.` - complete
- [x] `Task checkbox-45: Port 'fol/utils/logic_formatter.py' FOL/deontic JSON, Prolog, TPTP, defeasible, text, and aggregate formatting helpers.` - complete
- [x] `Task checkbox-46: Port predicate-name normalization and simple FOL formatting.` - complete
- [x] `Task checkbox-47: Port deontic operator extraction for must/shall/required/may/permitted/prohibited/shall not.` - complete
- [x] `Task checkbox-48: Port 'deontic/knowledge_base.py' browser-native primitives: parties, actions, intervals, propositions, statements, rule inference, and compliance checks.` - complete
- [x] `Task checkbox-49: Port 'deontic/analyzer.py' extraction, entity grouping, statistics, action similarity, and direct/conditional/jurisdictional/temporal conflict detection.` - complete
- [x] `Task checkbox-50: Add browser FOL and deontic converter facades for short clauses.` - complete
- [x] `Task checkbox-51: Add converter cache, batch, async, output-format helper, metadata, confidence, and warning behavior tests.` - complete
- [x] `Task checkbox-52: Add confidence heuristics but do not port Python ML scoring.` - complete
- [x] `Task checkbox-53: Add explicit Python ML confidence and spaCy NLP parity fixtures.` - complete
- [x] `Task checkbox-54: Decide which parity path to use: browser-native replacement or WASM only for runtime; Python fixtures are development-only.` - complete
- [x] `Task checkbox-55: Capture Python 'FOLConverter(use_ml=True, use_nlp=True)' outputs for representative legal clauses as development fixtures only.` - complete
- [x] `Task checkbox-56: Capture Python 'DeonticConverter(use_ml=True)' confidence outputs for the same fixtures as development fixtures only.` - complete
- [x] `Task checkbox-57: Add parity fixtures with raw text, regex-only output, spaCy-enabled output, ML confidence, and expected tolerances.` - complete
- [x] `Task checkbox-58: Evaluate browser substitutes for spaCy predicate extraction, including Transformers.js token classification or dependency-light NLP packages.` - complete
- [x] `Task checkbox-59: Decide that ML confidence must run in-browser or from precomputed static artifacts; no runtime Python service is allowed.` - complete
- [x] `Task checkbox-60: Add a compatibility mode that surfaces 'nlpUnavailable' or 'mlUnavailable' rather than silently pretending full parity.` - complete
- [x] `Task checkbox-61: Define acceptance thresholds: exact matches for operator classification, approximate matches for confidence scores, and documented divergences for predicate spans.` - complete
- [x] `Task checkbox-62: Port 'FLogicFrame', 'FLogicClass', 'FLogicQuery', and 'FLogicOntology' concepts.` - complete
- [x] `Task checkbox-63: Parse the subset of 'frame_logic_ergo' currently generated for Portland sections.` - complete
- [x] `Task checkbox-64: Render frames as structured tables: object, class, attributes, rules.` - complete
- [x] `Task checkbox-65: Normalize generated object IDs back to Portland citations when possible.` - complete
- [x] `Task checkbox-66: Port text normalization and deterministic hashing concepts from 'zkp/canonicalization.py'.` - complete
- [x] `Task checkbox-67: Port 'Statement', 'Witness', and 'ProofStatement' shapes, dictionary serialization, circuit reference parsing/formatting, and field-element mapping from 'zkp/statement.py'.` - complete
- [x] `Task checkbox-68: Port initial 'zkp/circuits.py' circuit metadata, Boolean circuit construction, simplified R1CS export, knowledge-of-axioms constraint checks, and TDFOL v1 Horn derivation constraint checks.` - complete
- [x] `Task checkbox-69: Port simulated ZKP backend proof shape, demo proof layout, backend registry metadata, availability checks, and fail-closed verification semantics from 'zkp/backends'.` - complete
- [x] `Task checkbox-70: Port initial 'zkp_prover.py' and 'zkp_verifier.py' browser-native facades with backend routing, proof caching, public-input validation, expected-theorem checks, and statistics.` - complete
- [x] `Task checkbox-71: Port 'legal_theorem_semantics.py' and 'witness_manager.py' browser-native TDFOL v1 Horn semantics, witness generation/validation, proof statement creation, consistency checks, and witness cache helpers.` - complete
- [x] `Task checkbox-72: Port 'evm_public_inputs.py' browser-native BN254 field packing helpers for EVM public inputs without chain calls.` - complete
- [x] `Task checkbox-73: Port 'vk_registry.py' and initial 'eth_vk_registry_payloads.py' browser-native VK hashing, registry, bytes32 normalization, and registerVK payload validation without RPC calls.` - complete
- [x] `Task checkbox-74: Port 'eth_contract_artifacts.py' as browser-native contract artifact object/JSON parsing for ABI and bytecode without filesystem path loading.` - complete
- [x] `Task checkbox-75: Add 'verifySimulatedCertificate()' that checks metadata consistency only.` - complete
- [x] `Task checkbox-76: Rename UI language so 'zkp_verified: true' with 'zkp_backend: simulated' is shown as "simulated certificate present", not "cryptographically verified".` - complete
- [x] `Task checkbox-77: Add a small in-memory 'LogicKnowledgeBase' keyed by section CID.` - complete
- [x] `Task checkbox-78: Add bounded forward chaining for facts and simple implications.` - complete
- [x] `Task checkbox-79: Add contradiction hints for obvious norm conflicts: same actor/action/condition with 'O' and 'F'.` - complete
- [x] `Task checkbox-80: Add temporal summary helpers for always/eventually/next/until.` - complete
- [x] `Task checkbox-81: Add proof trace output for any inferred result.` - complete
- [x] `Task checkbox-82: Add logic filters to the search service layer. UI wiring is deferred to the Portland research screen.` - complete
- [x] `Task checkbox-83: Add norm-aware score parts to logic-aware search results.` - complete
- [x] `Task checkbox-84: Add proof facts to GraphRAG evidence packs.` - complete
- [x] `Task checkbox-85: Add prompts or answer formatting that distinguish code text, KG facts, generated formalization, and local reasoning.` - complete
- [x] `Task checkbox-86: Add unsupported-question handling for queries not grounded in retrieved code.` - complete
- [x] `Task checkbox-87: Create a parity test fixture generated from selected Python outputs.` - complete
- [x] `Task checkbox-88: Compare TypeScript parser/formatter/converter outputs against Python outputs for fixed examples.` - complete
- [x] `Task checkbox-89: Add a validation command that can be run after corpus regeneration.` - complete
- [x] `Task checkbox-90: Track intentional divergences in a markdown table.` - complete
- [x] `Task checkbox-91: Evaluate whether any external prover should run in-browser via WASM.` - complete
- [x] `Task checkbox-92: Evaluate 'z3-solver'/Z3 WASM, cvc5 WASM availability, Tau Prolog, or custom Datalog for limited use cases.` - complete
- [x] `Task checkbox-93: Evaluate 'snarkjs' only if real browser-side proof verification becomes a product requirement.` - complete
- [x] `Task checkbox-94: Reject hosted runtime dependencies; use browser-native WASM only when a prover is truly required.` - complete
- [x] `Task checkbox-95: Port every TDFOL inference rule from 'logic/TDFOL/tdfol_inference_rules.py'.` - complete
- [x] `Task checkbox-96: Initial first-order rule slice: universal modus ponens, existential instantiation, existential generalization, and universal generalization.` - complete
- [x] `Task checkbox-97: Port propositional tableaux expansion rules from 'logic/TDFOL/expansion_rules.py'.` - complete
- [x] `Task checkbox-98: Complete proof strategies, strategy selector, performance engine, proof cache, dependency graph, proof explainer, and proof tree visualizer parity.` - complete
- [x] `Task checkbox-99: Initial forward-chaining strategy and selector parity.` - complete
- [x] `Task checkbox-100: Initial backward-chaining strategy parity for direct goals, conjunctive goals, and implication-goal reduction.` - complete
- [x] `Task checkbox-101: Initial bidirectional strategy parity with backward-first proof search and bounded forward fallback.` - complete
- [x] `Task checkbox-102: Initial modal tableaux strategy parity with local TS tableaux, modal-logic auto-selection, and priority/cost selection.` - complete
- [x] `Task checkbox-103: Initial local CEC delegate replacement that translates TDFOL to browser-native CEC expressions and returns explicit unknown results instead of calling Python or a server.` - complete
- [x] `Task checkbox-104: Initial indexed-KB and cache-aware optimization facade.` - complete
- [x] `Task checkbox-105: Deeper CEC delegate parity for native CEC inference rule groups and proof traces.` - complete
- [!] `Task checkbox-106: Browser-native ZKP acceleration and parallel proof search parity.` - blocked
- [!] `Task checkbox-107: Complete modal tableaux and countermodel generation/visualization parity.` - blocked
- [x] `Task checkbox-108: Initial modal tableaux proof search for propositional, temporal, deontic modal formulas and K/T/D/S4/S5 accessibility.` - complete
- [x] `Task checkbox-109: Initial countermodel model, extractor, and self-contained visual exports.` - complete
- [x] `Task checkbox-110: Full expansion-rule parity, richer branch diagnostics, strategy integration, and richer interactive renderer parity.` - complete
- [x] `Task checkbox-111: Modal tableaux countermodel export payloads for serializing TDFOL and CEC open branches into visualization-ready Kripke data.` - complete
- [x] `Task checkbox-112: Complete TDFOL security validator parity.` - complete
- [x] `Task checkbox-113: Added deterministic browser-native TDFOL proof-result auditing for theorem/step integrity, non-browser runtime method leakage, premise fan-out, and proof-time budget recommendations.` - complete
- [x] `Task checkbox-114: Add Python parity fixtures for each TDFOL rule category.` - complete
- [x] `Task checkbox-115: Add browser performance budgets for proof search.` - complete
- [x] `Task checkbox-116: Initial in-memory performance engine and strategy profiler.` - complete
- [x] `Task checkbox-117: Initial browser performance dashboard data model and renderer.` - complete
- [x] `Task checkbox-118: Initial browser performance profiler with repeated timing samples, memory snapshots, bottleneck classification, benchmark suites, and report strings.` - complete
- [x] `Task checkbox-119: Full profiler/dashboard parity with browser performance timelines, flamegraph-style views, and richer bottleneck reports.` - complete
- [x] `Task checkbox-120: Port CEC syntax tree, grammar loader, grammar engine, problem parser, and DCEC parsers.` - complete
- [x] `Task checkbox-121: Initial browser-native CEC/DCEC s-expression AST, parser, formatter, validator, and Portland DCEC unit coverage.` - complete
- [x] `Task checkbox-122: Initial CEC/DCEC expression analyzer for predicates, atoms, section refs, quantifiers, deontic operators, temporal operators, and expression complexity.` - complete
- [x] `Task checkbox-123: Initial CEC ShadowProver problem parser with browser-native TPTP 'fof'/'cnf' parsing, include tracking, custom 'LOGIC'/'ASSUMPTIONS'/'GOALS' format parsing, format auto-detection, and parser-specific errors.` - complete
- [x] `Task checkbox-124: Initial CEC syntax tree utility with typed node kinds, parent-aware construction, traversal/search helpers, transform/map/filter, JSON round-trip, leaf/height/size metrics, and ASCII pretty printing.` - complete
- [x] `Task checkbox-125: Initial CEC grammar loader and engine with embedded browser-native default grammar data, static grammar-data loading, operator word/semantic/example lookup, validation, lexical entries, grammar rules, bottom-up chart parsing, ambiguity resolution, and linearization fallback.` - complete
- [x] `Task checkbox-126: Initial DCEC enhanced grammar parser with DCEC grammar categories, terminals, CFG rules, parse-tree helpers, Earley-style chart states, mutable lexicon/rules, built-in deontic/cognitive/temporal grammar fragments, parse extraction, and grammar validation.` - complete
- [x] `Task checkbox-127: Initial DCEC English grammar facade with browser-native lexicon/rule setup, compositional local parsing for atomic/deontic/cognitive/temporal/connective fragments, dependency-free domain-vocabulary fallback parsing, Python-style semantic dictionary linearization, semantic-to-DCEC conversion, DCEC-to-semantic conversion, formula-to-English rendering, and factory construction.` - complete
- [x] `Task checkbox-128: Initial DCEC cleaning/preprocessing utilities with whitespace/comment normalization, redundant-parentheses consolidation, balanced-paren checks, matching close-paren lookup, function-call tucking, symbolic-operator functorization, and a standard cleaning pipeline.` - complete
- [x] `Task checkbox-129: Initial DCEC parsing utility layer with Python-compatible parse tokens, S-expression/F-expression rendering, depth/width metrics, synonym normalization, logical prefixing, arithmetic PEMDAS prefixing, and atomic sort tracking.` - complete
- [x] `Task checkbox-130: Initial DCEC type, namespace, and container layer with deontic/cognitive/logical/temporal operator constants, sort subtyping, variable/function/predicate symbols, built-in sorts, duplicate/missing-sort errors, statement labels, axioms, theorems, clear/statistics behavior, and CEC AST-compatible formulas.` - complete
- [x] `Task checkbox-131: Initial DCEC core formula layer with variable/function terms, atomic/deontic/cognitive/temporal/connective/quantified formulas, Python-compatible rendering, arity validation, free-variable tracking, substitution, statement formatting, structural string equality, and convenience constructors.` - complete
- [x] `Task checkbox-132: Initial DCEC integration pipeline with browser-native string-to-parse-token conversion, recursive comma-S-expression parsing, token-to-formula conversion, prefix 'not' normalization, deontic/cognitive/temporal mapping, object/agent term inference, and formula validation.` - complete
- [x] `Task checkbox-133: Initial DCEC prototype namespace with sort inheritance, overloaded function prototypes, atomic type definitions, text prototype parsing, base DCEC/logical/numeric vocabularies, type-conflict checks, quantifier map state, statistics, and printable snapshots.` - complete
- [x] `Task checkbox-134: Initial DCEC temporal evaluator/state layer with finite-trace 'ALWAYS'/'EVENTUALLY'/'NEXT'/'UNTIL'/'SINCE'/'YESTERDAY' evaluation, unary/binary arity validation, DCEC atom proposition extraction, negated-atom handling, symbolic rendering, and convenience constructors.` - complete
- [x] `Task checkbox-135: Initial DCEC natural-language converter with browser-native pattern matching for deontic/cognitive/temporal/logical phrases, DCEC namespace reuse, conversion result history/statistics, formula-to-English linearization, deterministic precedence, and local dependency-free grammar placeholders.` - complete
- [x] `Task checkbox-136: Add CEC/DCEC parity fixtures and generated Portland DCEC parse coverage.` - complete
- [x] `Task checkbox-137: Port native inference rule groups: propositional, modal, temporal, deontic, cognitive, specialized, and resolution.` - complete
- [x] `Task checkbox-138: Initial CEC native inference rule slice: modus ponens, conjunction elimination, double-negation elimination, temporal T, deontic D, and prohibition equivalence.` - complete
- [x] `Task checkbox-139: Expanded deterministic CEC inference slice: hypothetical syllogism, conjunction introduction as an opt-in generative rule, eventuality introduction as an opt-in generative rule, prohibition-from-obligation, universal modus ponens, existential instantiation, existential generalization, and universal generalization.` - complete
- [x] `Task checkbox-140: Expanded CEC temporal/deontic inference rule slice with always/eventually/next distribution and implication, temporal transitivity, always induction, temporal negation, until/since weakening, obligation/permission distribution, obligation implication, permission duality, obligation consistency, and opt-in obligation conjunction.` - complete
- [x] `Task checkbox-141: Initial CEC modal inference rule group with necessity elimination, necessity distribution, possibility-necessity duality, opt-in possibility introduction, and opt-in necessity conjunction generation.` - complete
- [x] `Task checkbox-142: Initial CEC cognitive inference rule group with belief/knowledge distribution, knowledge-implies-belief, belief/knowledge monotonicity, intention commitment, intention means-end, perception-to-knowledge, belief negation, intention persistence, belief revision, and opt-in belief/knowledge conjunction generation.` - complete
- [x] `Task checkbox-143: Initial CEC resolution inference rule group with binary resolution, unit resolution, factoring, subsumption, case analysis/disjunction elimination, proof-by-contradiction signaling, and three-premise rule enumeration.` - complete
- [x] `Task checkbox-144: Initial CEC specialized inference rule group with biconditional introduction/elimination, constructive/destructive dilemma, exportation, absorption, tautology simplification, conjunction commutativity, and opt-in addition/disjunction introduction.` - complete
- [x] `Task checkbox-145: Expanded CEC extended prover-core rule parity with disjunction commutativity, distribution, association, transposition, material implication round-tripping, Clavius law, and conjunction/disjunction idempotence.` - complete
- [x] `Task checkbox-146: Expanded CEC common-knowledge/common-belief rule parity with common knowledge/belief introduction, common knowledge distribution, common-knowledge-to-knowledge, monotonicity, negation, transitivity, fixed-point induction, temporally induced common knowledge, and modal necessitation introduction.` - complete
- [x] `Task checkbox-147: Port event calculus, fluents, context manager, ambiguity resolver, shadow prover, and modal tableaux.` - complete
- [x] `Task checkbox-148: Initial CEC fluent/event state manager with fluent types, persistence rules, event transitions, frame-problem persistence, conflict resolution, timelines, statistics, and validation.` - complete
- [x] `Task checkbox-149: Initial CEC event calculus with browser-native discrete event occurrences, initiation/termination/release rules, 'Happens', 'Initiates', 'Terminates', 'Releases', 'ReleasedAt', 'HoldsAt', 'Clipped', parsed predicate loading/evaluation, timelines, all-fluent queries, caching, and validation.` - complete
- [x] `Task checkbox-150: Initial CEC context manager with discourse state, entity tracking, focus management, pronoun/anaphora resolution, parsed CEC expression ingestion, discourse segmentation, coherence scoring, snapshots, and validation.` - complete
- [x] `Task checkbox-151: Initial CEC ambiguity resolver with syntax-tree adapters, minimal-attachment/right-association/balance scoring, ranked parse explanations, custom preference rules, semantic pattern scoring, statistical bigram scoring, and CEC AST-to-tree conversion.` - complete
- [x] `Task checkbox-152: Initial CEC ShadowProver facade with K/T/D/S4/S5 local modal tableaux, forward-prover fallback, problem-object proving, proof cache/statistics, direct-assumption proofs, unsupported-LP diagnostics, and browser-native cognitive rule subset.` - complete
- [x] `Task checkbox-153: Initial CEC modal tableaux with K/T/D/S4/S5 world/branch model, contradiction closure, box/diamond expansion, deontic O/P/F mapping, proof steps, and open-branch countermodel support.` - complete
- [x] `Task checkbox-154: Initial CEC countermodel extraction and visualization from open tableaux branches with Kripke JSON, DOT, ASCII, compact ASCII, HTML, valuation extraction, and modal property checks.` - complete
- [x] `Task checkbox-155: Port CEC proof cache, proof strategies, advanced inference, and error handling.` - complete
- [x] `Task checkbox-156: Initial CEC native shared-type layer with Python 'types.py'-style formula/proof/conversion/namespace/config dictionaries, protocol guards for formulas/provers/converters/knowledge bases, generic result/cache/stat records, callable aliases, and unified proof statistics with incremental averages.` - complete
- [x] `Task checkbox-157: Initial DCEC advanced inference layer with modal K/T/S4/necessitation, temporal induction/frame, deontic D/permission-obligation/distribution, knowledge-obligation interaction, temporal-obligation persistence, and grouped rule registries.` - complete
- [x] `Task checkbox-158: Initial CEC native error-handling layer with CEC-specific parse/proof/conversion/validation/namespace/grammar/knowledge-base errors, Python-style context/suggestion formatting, safe-call wrappers, parse/proof handler wrappers, operation error formatting, and DCEC formula-shape validation.` - complete
- [x] `Task checkbox-159: Initial CEC lemma-generation layer with reusable lemma objects, deterministic pattern hashing, LRU lemma cache, pattern lookup, proof-tree lemma discovery, cached lemma reuse during CEC proving, discovery/reuse statistics, and clear/reset behavior.` - complete
- [x] `Task checkbox-160: Initial CEC proof-optimization layer with proof-node trees, depth/redundancy pruning, optimization metrics, duplicate/subsumption elimination, browser-native async batch search, combined optimizer coordination, and metrics export.` - complete
- [x] `Task checkbox-161: Initial CEC/ZKP integration layer with unified standard/ZKP/cached proof results, simulated educational CEC ZKP certificates, private axiom hiding, deterministic browser Web Crypto commitments, local standard fallback, cache-first hybrid proving, statistics, clear/reset helpers, and explicit non-cryptographic simulated-backend language.` - complete
- [x] `Task checkbox-162: Initial bounded CEC forward prover with proof steps, unknown results, and derived-expression budget handling.` - complete
- [x] `Task checkbox-163: Initial CEC prover support for Portland-style quantified DCEC facts through browser-native universal modus ponens, without Python delegation.` - complete
- [x] `Task checkbox-164: Initial CEC proof cache with normalized theorem/axiom keys, prover-config sensitivity, invalidation, global helper, TTL/LRU stats, and cached prove facade.` - complete
- [x] `Task checkbox-165: Initial CEC strategy selector with forward and cached-forward strategies, priority/cost selection, metadata, and convenience proving facade.` - complete
- [x] `Task checkbox-166: Expanded CEC proof strategy parity with backward chaining, bidirectional backward-first/forward-fallback search, hybrid adaptive strategy selection using Python axiom-count heuristics, Python-style strategy factory, strategy costs, and direct/cached default selection.` - complete
- [x] `Task checkbox-167: Initial CEC proof explainer with rule descriptions, natural-language steps, inference chains, rendered text, and proof statistics.` - complete
- [x] `Task checkbox-168: Initial CEC dependency graph and proof tree visualizer with JSON, DOT, HTML, ASCII, topological order, path lookup, and unused-axiom diagnostics.` - complete
- [x] `Task checkbox-169: Initial CEC performance metrics and engine with timing collectors, strategy profiling, dashboard HTML export, JSON/Prometheus-style export, regression checks, and profiler history.` - complete
- [x] `Task checkbox-170: Initial CEC performance dashboard with proof metrics, time-series metrics, expression classification, aggregate stats, strategy comparison, JSON export, and self-contained HTML.` - complete
- [x] `Task checkbox-171: Initial CEC performance profiler with repeated-run profiling, bottleneck detection, browser memory snapshots, benchmark suites, baseline regression accounting, and text/JSON/HTML reports.` - complete
- [x] `Task checkbox-172: Initial CEC security validator and error-hardening facade with rate limits, input sanitization, size/depth/operator guards, injection/DoS detection, parse validation, resource checks, proof-result audit, and security reports.` - complete
- [x] `Task checkbox-173: Port CEC NL policy compilers and language detection with browser-native NLP.` - complete
- [x] `Task checkbox-174: Add deeper CEC/DCEC parity fixtures against Python parser and prover outputs.` - complete
- [x] `Task checkbox-175: Replace spaCy extraction with browser-native NLP: Transformers.js token classification, dependency-light NLP, ONNX/WebGPU, or WASM NLP.` - complete
- [x] `Task checkbox-176: Port 'ml_confidence.py' to local browser inference or an equivalent deterministic TypeScript model.` - complete
- [x] `Task checkbox-177: Add local model artifact loading, caching, versioning, and unload controls.` - complete
- [x] `Task checkbox-178: Add exact/tolerance parity tests against Python ML/spaCy development fixtures.` - complete
- [!] `Task checkbox-179: Remove 'nlpUnavailable' and 'mlUnavailable' capability flags once browser-native parity is implemented.` - blocked
- [x] `Task checkbox-180: Port external prover router and bridge contracts to local browser adapters.` - complete
- [x] `Task checkbox-181: Evaluate and integrate local WASM provers for Z3/cvc5/Tau Prolog/Lean/Coq-style workflows where feasible.` - complete
- [x] `Task checkbox-182: Port Groth16 verification/proving path using browser-native cryptographic libraries where feasible.` - complete
- [x] `Task checkbox-183: Port EVM/public-input/vk-registry helpers using browser-compatible crypto and chain libraries.` - complete
- [x] `Task checkbox-184: Add strict UI/API language distinguishing simulated, heuristic, proof-checking, and cryptographic outputs.` - complete
- [x] `Task checkbox-185: Port logic integration bridges to route to TS/WASM cores.` - complete
- [x] `Task checkbox-186: Initial browser-native bridge facade for local route inventory, FOL/deontic/TDFOL/CEC conversion routing, TDFOL/CEC proof routing, and explicit unsupported-route results with 'server_calls_allowed: false'.` - complete
- [x] `Task checkbox-187: Port deeper domain-specific integration bridges, interactive workflows, and parity fixtures.` - complete
- [x] `Task checkbox-188: Port security input validation, circuit breaker, rate limiting, and audit-log semantics to browser-local equivalents.` - complete
- [x] `Task checkbox-189: Port observability structured logging, Prometheus-style metrics, and OTel-style tracing to browser-local equivalents.` - complete
- [x] `Task checkbox-190: Port monitoring/metrics to in-browser telemetry objects and developer panels.` - complete
- [x] `Task checkbox-191: Initial top-level 'logic/monitoring.py' parity for operation metrics, tracking helpers, health checks, error/warning counters, global monitor, reset, operation summaries, and optional Prometheus text export.` - complete
- [x] `Task checkbox-192: Add richer developer-panel integration for live UI inspection.` - complete
- [x] `Task checkbox-193: Replace Python API/CLI surfaces with TypeScript developer scripts or browser devtools.` - complete
- [x] `Task checkbox-194: Initial browser-native public API facade for 'logic/api.py' import-surface parity.` - complete
- [x] `Task checkbox-195: Add CLI/devtools command adapter parity for 'logic/cli.py'.` - complete
- [x] `Task checkbox-196: Port IPFS/IPLD proof cache semantics to browser-native storage/IPFS clients where possible.` - complete
- [x] `Task checkbox-197: Port remaining Python logic module 'logic/CEC/cec_framework.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-198: Port remaining Python logic module 'logic/CEC/dcec_wrapper.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-199: Port remaining Python logic module 'logic/CEC/eng_dcec_wrapper.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-200: Port remaining Python logic module 'logic/CEC/native/advanced_inference.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - validated by latest daemon round
- [x] `Task checkbox-201: Port remaining Python logic module 'logic/CEC/native/ambiguity_resolver.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [!] `Task checkbox-202: Port remaining Python logic module 'logic/CEC/native/cec_proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-203: Port remaining Python logic module 'logic/CEC/native/cec_zkp_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-204: Port remaining Python logic module 'logic/CEC/native/context_manager.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-205: Port remaining Python logic module 'logic/CEC/native/dcec_cleaning.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [x] `Task checkbox-206: Port remaining Python logic module 'logic/CEC/native/dcec_core.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-207: Port remaining Python logic module 'logic/CEC/native/dcec_english_grammar.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [!] `Task checkbox-208: Port remaining Python logic module 'logic/CEC/native/dcec_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-209: Port remaining Python logic module 'logic/CEC/native/dcec_namespace.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-210: Port remaining Python logic module 'logic/CEC/native/dcec_parsing.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-211: Port remaining Python logic module 'logic/CEC/native/dcec_prototypes.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-212: Port remaining Python logic module 'logic/CEC/native/dcec_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-213: Port remaining Python logic module 'logic/CEC/native/enhanced_grammar_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-214: Port remaining Python logic module 'logic/CEC/native/error_handling.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-215: Port remaining Python logic module 'logic/CEC/native/event_calculus.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [x] `Task checkbox-216: Port remaining Python logic module 'logic/CEC/native/exceptions.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [!] `Task checkbox-217: Port remaining Python logic module 'logic/CEC/native/grammar_engine.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-218: Port remaining Python logic module 'logic/CEC/native/grammar_loader.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-219: Port remaining Python logic module 'logic/CEC/native/inference_rules/base.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [!] `Task checkbox-220: Port remaining Python logic module 'logic/CEC/native/inference_rules/cognitive.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [x] `Task checkbox-221: Port remaining Python logic module 'logic/CEC/native/inference_rules/deontic.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [!] `Task checkbox-222: Port remaining Python logic module 'logic/CEC/native/inference_rules/modal.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [x] `Task checkbox-223: Port remaining Python logic module 'logic/CEC/native/inference_rules/propositional.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-224: Port remaining Python logic module 'logic/CEC/native/inference_rules/resolution.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-225: Port remaining Python logic module 'logic/CEC/native/inference_rules/specialized.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-226: Port remaining Python logic module 'logic/CEC/native/lemma_generation.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-227: Port remaining Python logic module 'logic/CEC/native/modal_tableaux.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-228: Port remaining Python logic module 'logic/CEC/native/nl_converter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-229: Port remaining Python logic module 'logic/CEC/native/problem_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-230: Port remaining Python logic module 'logic/CEC/native/proof_optimization.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-231: Port remaining Python logic module 'logic/CEC/native/proof_strategies.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [!] `Task checkbox-232: Port remaining Python logic module 'logic/CEC/native/prover_core.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [x] `Task checkbox-233: Port remaining Python logic module 'logic/CEC/native/prover_core_extended_rules.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-234: Port remaining Python logic module 'logic/CEC/native/shadow_prover.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-235: Port remaining Python logic module 'logic/CEC/native/syntax_tree.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-236: Port remaining Python logic module 'logic/CEC/nl/base_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-237: Port remaining Python logic module 'logic/CEC/nl/dcec_to_ucan_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-238: Port remaining Python logic module 'logic/CEC/nl/domain_vocabularies/domain_vocab.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-239: Port remaining Python logic module 'logic/CEC/nl/french_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-240: Port remaining Python logic module 'logic/CEC/nl/german_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-241: Port remaining Python logic module 'logic/CEC/nl/grammar_nl_policy_compiler.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-242: Port remaining Python logic module 'logic/CEC/nl/language_detector.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-243: Port remaining Python logic module 'logic/CEC/nl/nl_policy_conflict_detector.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-244: Port remaining Python logic module 'logic/CEC/nl/nl_to_policy_compiler.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-245: Port remaining Python logic module 'logic/CEC/nl/portuguese_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-246: Port remaining Python logic module 'logic/CEC/nl/spanish_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-247: Port remaining Python logic module 'logic/CEC/optimization/formula_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-248: Port remaining Python logic module 'logic/CEC/optimization/profiling_utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-249: Port remaining Python logic module 'logic/CEC/provers/e_prover_adapter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-250: Port remaining Python logic module 'logic/CEC/provers/prover_manager.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-251: Port remaining Python logic module 'logic/CEC/provers/tptp_utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-252: Port remaining Python logic module 'logic/CEC/provers/vampire_adapter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-253: Port remaining Python logic module 'logic/CEC/provers/z3_adapter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-254: Port remaining Python logic module 'logic/CEC/shadow_prover_wrapper.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-255: Port remaining Python logic module 'logic/CEC/talos_wrapper.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-256: Port remaining Python logic module 'logic/TDFOL/countermodel_visualizer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-257: Port remaining Python logic module 'logic/TDFOL/demonstrate_countermodel_visualizer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-258: Port remaining Python logic module 'logic/TDFOL/demonstrate_performance_dashboard.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-259: Port remaining Python logic module 'logic/TDFOL/example_formula_dependency_graph.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-260: Port remaining Python logic module 'logic/TDFOL/example_performance_profiler.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-261: Port remaining Python logic module 'logic/TDFOL/exceptions.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-262: Port remaining Python logic module 'logic/TDFOL/expansion_rules.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-263: Port remaining Python logic module 'logic/TDFOL/formula_dependency_graph.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-264: Port remaining Python logic module 'logic/TDFOL/inference_rules/base.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-265: Port remaining Python logic module 'logic/TDFOL/inference_rules/deontic.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-266: Port remaining Python logic module 'logic/TDFOL/inference_rules/first_order.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-267: Port remaining Python logic module 'logic/TDFOL/inference_rules/propositional.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-268: Port remaining Python logic module 'logic/TDFOL/inference_rules/temporal_deontic.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-269: Port remaining Python logic module 'logic/TDFOL/modal_tableaux.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-270: Port remaining Python logic module 'logic/TDFOL/nl/demonstrate_ipfs_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-271: Port remaining Python logic module 'logic/TDFOL/nl/llm.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-272: Port remaining Python logic module 'logic/TDFOL/nl/tdfol_nl_api.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-273: Port remaining Python logic module 'logic/TDFOL/nl/tdfol_nl_context.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-274: Port remaining Python logic module 'logic/TDFOL/nl/tdfol_nl_generator.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-275: Port remaining Python logic module 'logic/TDFOL/nl/tdfol_nl_patterns.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-276: Port remaining Python logic module 'logic/TDFOL/nl/tdfol_nl_preprocessor.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-277: Port remaining Python logic module 'logic/TDFOL/nl/utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-278: Port remaining Python logic module 'logic/TDFOL/p2p/ipfs_proof_storage.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-279: Port remaining Python logic module 'logic/TDFOL/performance_dashboard.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-280: Port remaining Python logic module 'logic/TDFOL/performance_metrics.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-281: Port remaining Python logic module 'logic/TDFOL/performance_profiler.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-282: Port remaining Python logic module 'logic/TDFOL/proof_explainer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-283: Port remaining Python logic module 'logic/TDFOL/proof_tree_visualizer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-284: Port remaining Python logic module 'logic/TDFOL/quickstart_visualizer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-285: Port remaining Python logic module 'logic/TDFOL/security_validator.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-286: Port remaining Python logic module 'logic/TDFOL/strategies/base.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-287: Port remaining Python logic module 'logic/TDFOL/strategies/cec_delegate.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-288: Port remaining Python logic module 'logic/TDFOL/strategies/forward_chaining.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-289: Port remaining Python logic module 'logic/TDFOL/strategies/modal_tableaux.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-290: Port remaining Python logic module 'logic/TDFOL/strategies/strategy_selector.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-291: Port remaining Python logic module 'logic/TDFOL/tdfol_converter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-292: Port remaining Python logic module 'logic/TDFOL/tdfol_core.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-293: Port remaining Python logic module 'logic/TDFOL/tdfol_dcec_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-294: Port remaining Python logic module 'logic/TDFOL/tdfol_inference_rules.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-295: Port remaining Python logic module 'logic/TDFOL/tdfol_optimization.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-296: Port remaining Python logic module 'logic/TDFOL/tdfol_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-297: Port remaining Python logic module 'logic/TDFOL/tdfol_performance_engine.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-298: Port remaining Python logic module 'logic/TDFOL/tdfol_proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-299: Port remaining Python logic module 'logic/TDFOL/tdfol_prover.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-300: Port remaining Python logic module 'logic/TDFOL/zkp_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-301: Port remaining Python logic module 'logic/api_server.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-302: Port remaining Python logic module 'logic/batch_processing.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-303: Port remaining Python logic module 'logic/cli.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-304: Port remaining Python logic module 'logic/common/bounded_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-305: Port remaining Python logic module 'logic/common/feature_detection.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-306: Port remaining Python logic module 'logic/common/proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-307: Port remaining Python logic module 'logic/common/utility_monitor.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-308: Port remaining Python logic module 'logic/common/validators.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-309: Port remaining Python logic module 'logic/deontic/decoder.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-310: Port remaining Python logic module 'logic/deontic/exports.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-311: Port remaining Python logic module 'logic/deontic/formula_builder.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-312: Port remaining Python logic module 'logic/deontic/ir.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-313: Port remaining Python logic module 'logic/deontic/knowledge_base.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-314: Port remaining Python logic module 'logic/deontic/legal_text_to_deontic.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-315: Port remaining Python logic module 'logic/deontic/metrics.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-316: Port remaining Python logic module 'logic/deontic/prover_syntax.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-317: Port remaining Python logic module 'logic/deontic/support_map.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-318: Port remaining Python logic module 'logic/deontic/utils/deontic_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-319: Port remaining Python logic module 'logic/e2e_validation.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-320: Port remaining Python logic module 'logic/external_provers/formula_analyzer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [!] `Task checkbox-321: Port remaining Python logic module 'logic/external_provers/interactive/coq_prover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - blocked
- [x] `Task checkbox-322: Port remaining Python logic module 'logic/external_provers/interactive/lean_prover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-323: Port remaining Python logic module 'logic/external_provers/neural/symbolicai_prover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-324: Port remaining Python logic module 'logic/external_provers/proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-325: Port remaining Python logic module 'logic/external_provers/prover_router.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-326: Port remaining Python logic module 'logic/external_provers/smt/cvc5_prover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-327: Port remaining Python logic module 'logic/external_provers/smt/z3_prover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-328: Port remaining Python logic module 'logic/flogic/ergoai_wrapper.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-329: Port remaining Python logic module 'logic/flogic/flogic_proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-330: Port remaining Python logic module 'logic/flogic/flogic_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-331: Port remaining Python logic module 'logic/flogic/flogic_zkp_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-332: Port remaining Python logic module 'logic/flogic/semantic_normalizer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-333: Port remaining Python logic module 'logic/fol/text_to_fol.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-334: Port remaining Python logic module 'logic/fol/utils/deontic_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-335: Port remaining Python logic module 'logic/fol/utils/fol_parser.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-336: Port remaining Python logic module 'logic/fol/utils/logic_formatter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-337: Port remaining Python logic module 'logic/fol/utils/nlp_predicate_extractor.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-338: Port remaining Python logic module 'logic/fol/utils/predicate_extractor.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-339: Port remaining Python logic module 'logic/integration/base_prover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-340: Port remaining Python logic module 'logic/integration/bridges/base_prover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-341: Port remaining Python logic module 'logic/integration/bridges/external_provers.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-342: Port remaining Python logic module 'logic/integration/bridges/prover_installer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-343: Port remaining Python logic module 'logic/integration/bridges/symbolic_fol_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-344: Port remaining Python logic module 'logic/integration/bridges/tdfol_cec_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-345: Port remaining Python logic module 'logic/integration/bridges/tdfol_grammar_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-346: Port remaining Python logic module 'logic/integration/bridges/tdfol_shadowprover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-347: Port remaining Python logic module 'logic/integration/caching/ipfs_proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-348: Port remaining Python logic module 'logic/integration/caching/ipld_logic_storage.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-349: Port remaining Python logic module 'logic/integration/caching/proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-350: Port remaining Python logic module 'logic/integration/cec_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-351: Port remaining Python logic module 'logic/integration/converters/deontic_logic_converter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-352: Port remaining Python logic module 'logic/integration/converters/deontic_logic_core.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-353: Port remaining Python logic module 'logic/integration/converters/logic_translation_core.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-354: Port remaining Python logic module 'logic/integration/converters/modal_logic_extension.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-355: Port remaining Python logic module 'logic/integration/converters/symbolic_fol_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-356: Port remaining Python logic module 'logic/integration/demos/demo_temporal_deontic_rag.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-357: Port remaining Python logic module 'logic/integration/deontic_logic_converter.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-358: Port remaining Python logic module 'logic/integration/deontic_logic_core.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-359: Port remaining Python logic module 'logic/integration/domain/caselaw_bulk_processor.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-360: Port remaining Python logic module 'logic/integration/domain/deontic_query_engine.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-361: Port remaining Python logic module 'logic/integration/domain/document_consistency_checker.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-362: Port remaining Python logic module 'logic/integration/domain/legal_domain_knowledge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-363: Port remaining Python logic module 'logic/integration/domain/legal_symbolic_analyzer.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-364: Port remaining Python logic module 'logic/integration/domain/medical_theorem_framework.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-365: Port remaining Python logic module 'logic/integration/domain/symbolic_contracts.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-366: Port remaining Python logic module 'logic/integration/domain/temporal_deontic_api.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-367: Port remaining Python logic module 'logic/integration/domain/temporal_deontic_rag_store.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-368: Port remaining Python logic module 'logic/integration/interactive/_fol_constructor_io.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-369: Port remaining Python logic module 'logic/integration/interactive/interactive_fol_constructor.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-370: Port remaining Python logic module 'logic/integration/interactive/interactive_fol_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-371: Port remaining Python logic module 'logic/integration/interactive/interactive_fol_utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-372: Port remaining Python logic module 'logic/integration/interactive_fol_constructor.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-373: Port remaining Python logic module 'logic/integration/logic_translation_core.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-374: Port remaining Python logic module 'logic/integration/logic_verification.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-375: Port remaining Python logic module 'logic/integration/logic_verification_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-376: Port remaining Python logic module 'logic/integration/logic_verification_utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-377: Port remaining Python logic module 'logic/integration/modal_logic_extension.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-378: Port remaining Python logic module 'logic/integration/neurosymbolic.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-379: Port remaining Python logic module 'logic/integration/neurosymbolic_graphrag.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-380: Port remaining Python logic module 'logic/integration/nl_ucan_policy_compiler.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-381: Port remaining Python logic module 'logic/integration/proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-382: Port remaining Python logic module 'logic/integration/reasoning/_deontic_conflict_mixin.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-383: Port remaining Python logic module 'logic/integration/reasoning/_logic_verifier_backends_mixin.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-384: Port remaining Python logic module 'logic/integration/reasoning/_prover_backend_mixin.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-385: Port remaining Python logic module 'logic/integration/reasoning/deontological_reasoning.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-386: Port remaining Python logic module 'logic/integration/reasoning/deontological_reasoning_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-387: Port remaining Python logic module 'logic/integration/reasoning/deontological_reasoning_utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-388: Port remaining Python logic module 'logic/integration/reasoning/logic_verification.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-389: Port remaining Python logic module 'logic/integration/reasoning/logic_verification_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-390: Port remaining Python logic module 'logic/integration/reasoning/logic_verification_utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-391: Port remaining Python logic module 'logic/integration/reasoning/proof_execution_engine.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-392: Port remaining Python logic module 'logic/integration/reasoning/proof_execution_engine_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-393: Port remaining Python logic module 'logic/integration/reasoning/proof_execution_engine_utils.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-394: Port remaining Python logic module 'logic/integration/symbolic/neurosymbolic/embedding_prover.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-395: Port remaining Python logic module 'logic/integration/symbolic/neurosymbolic/hybrid_confidence.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-396: Port remaining Python logic module 'logic/integration/symbolic/neurosymbolic/reasoning_coordinator.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-397: Port remaining Python logic module 'logic/integration/symbolic/neurosymbolic_api.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-398: Port remaining Python logic module 'logic/integration/symbolic/neurosymbolic_graphrag.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-399: Port remaining Python logic module 'logic/integration/symbolic/symbolic_logic_primitives.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-400: Port remaining Python logic module 'logic/integration/symbolic_contracts.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-401: Port remaining Python logic module 'logic/integration/symbolic_fol_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-402: Port remaining Python logic module 'logic/integration/symbolic_logic_primitives.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-403: Port remaining Python logic module 'logic/integration/tdfol_cec_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-404: Port remaining Python logic module 'logic/integration/tdfol_grammar_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-405: Port remaining Python logic module 'logic/integration/tdfol_shadowprover_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-406: Port remaining Python logic module 'logic/integration/ucan_policy_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-407: Port remaining Python logic module 'logic/integrations/enhanced_graphrag_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-408: Port remaining Python logic module 'logic/integrations/phase7_complete_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-409: Port remaining Python logic module 'logic/integrations/unixfs_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-410: Port remaining Python logic module 'logic/ml_confidence.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-411: Port remaining Python logic module 'logic/observability/metrics_prometheus.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-412: Port remaining Python logic module 'logic/observability/otel_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-413: Port remaining Python logic module 'logic/observability/structured_logging.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-414: Port remaining Python logic module 'logic/phase7_4_benchmarks.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-415: Port remaining Python logic module 'logic/security/audit_log.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-416: Port remaining Python logic module 'logic/security/input_validation.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-417: Port remaining Python logic module 'logic/security/llm_circuit_breaker.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-418: Port remaining Python logic module 'logic/security/rate_limiting.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-419: Port remaining Python logic module 'logic/types/bridge_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-420: Port remaining Python logic module 'logic/types/common_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-421: Port remaining Python logic module 'logic/types/deontic_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-422: Port remaining Python logic module 'logic/types/fol_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-423: Port remaining Python logic module 'logic/types/proof_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-424: Port remaining Python logic module 'logic/types/translation_types.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-425: Port remaining Python logic module 'logic/zkp/backends/backend_protocol.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-426: Port remaining Python logic module 'logic/zkp/backends/groth16_backup.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-427: Port remaining Python logic module 'logic/zkp/backends/groth16_ffi.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-428: Port remaining Python logic module 'logic/zkp/backends/simulated.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-429: Port remaining Python logic module 'logic/zkp/eth_contract_artifacts.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-430: Port remaining Python logic module 'logic/zkp/eth_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-431: Port remaining Python logic module 'logic/zkp/eth_vk_registry_payloads.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-432: Port remaining Python logic module 'logic/zkp/evm_harness.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-433: Port remaining Python logic module 'logic/zkp/evm_public_inputs.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-434: Port remaining Python logic module 'logic/zkp/examples/zkp_advanced_demo.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-435: Port remaining Python logic module 'logic/zkp/examples/zkp_basic_demo.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-436: Port remaining Python logic module 'logic/zkp/examples/zkp_ipfs_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-437: Port remaining Python logic module 'logic/zkp/legal_theorem_semantics.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-438: Port remaining Python logic module 'logic/zkp/onchain_pipeline.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-439: Port remaining Python logic module 'logic/zkp/setup_artifacts.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-440: Port remaining Python logic module 'logic/zkp/ucan_zkp_bridge.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-441: Port remaining Python logic module 'logic/zkp/vk_registry.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-442: Port remaining Python logic module 'logic/zkp/witness_manager.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-443: Port remaining Python logic module 'logic/zkp/zkp_prover.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-444: Port remaining Python logic module 'logic/zkp/zkp_verifier.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-445: Replace remaining 'nlpUnavailable' capability paths with browser-native NLP parity or explicit local model artifact loading.` - complete
- [x] `Task checkbox-446: Replace remaining 'mlUnavailable' capability paths with browser-native ML confidence parity or explicit local model artifact loading.` - complete
- [x] `Task checkbox-447: Audit remaining TypeScript logic 'unsupported' paths and convert feasible ones into browser-native TypeScript/WASM implementations.` - complete
- [x] `Task checkbox-448: Reconcile the Python logic inventory (269 files) with the TypeScript/WASM implementation (253 files) and add browser-native port tasks for uncovered behavior.` - complete
- [x] `Task checkbox-449: Review the accepted TypeScript logic changes against the original browser-native TypeScript/WASM port goal, then add or implement any missing parity tasks for Python logic behavior that lacks accepted-work evidence.` - complete
- [x] `Task checkbox-450: Add end-to-end browser-native validation proving the converted logic runs without Python, spaCy, or server-side calls, including deterministic coverage for ML and NLP capability surfaces.` - complete
- [x] `Task checkbox-451: Audit Python ML and spaCy expectations against the TypeScript/WASM implementation and add focused parity tests or local-model artifact loading tasks for unsupported browser-native behavior.` - complete
- [x] `Task checkbox-452: Refresh the TypeScript port plan with a parity matrix mapping Python logic modules, TypeScript/WASM files, validation evidence, accepted work, and remaining browser-native tasks.` - complete
- [x] `Task checkbox-453: Compare TypeScript logic public exports against Python logic module public APIs and add missing browser-native compatibility adapters or parity tests.` - complete
- [x] `Task checkbox-454: Port remaining Python logic module 'logic/zkp/form_circuit.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.` - complete
- [x] `Task checkbox-455: Manual unblock: implement a browser-native TDFOL ZKP acceleration scheduler slice with worker-safe proof-search queues, deterministic simulated prover fallback, and tests covering parallel-search metadata without requiring server crypto.` - complete
- [x] `Task checkbox-456: Manual unblock: complete a modal tableaux countermodel export slice that turns proof search branches into serializable visualization data and validates it against existing TDFOL/CEC examples.` - complete
- [x] `Task checkbox-457: Manual unblock: add a TDFOL security validator parity slice covering fail-closed formula, proof-cache, witness, and ZKP input checks in browser-safe TypeScript.` - complete
- [x] `Task checkbox-458: Manual unblock: port the next deterministic 'ml_confidence.py' parity slice with fixture-backed scoring, calibration metadata, and local browser execution only.` - complete
- [x] `Task checkbox-459: Manual unblock: add local model artifact manifest, cache lifecycle, version checks, and unload controls for browser-native ML/NLP parity without server calls.` - complete
- [x] `Task checkbox-460: Manual unblock: remove the next 'nlpUnavailable' or 'mlUnavailable' capability path by replacing it with local TypeScript/WASM, Transformers.js, ONNX/WebGPU, or deterministic fixture parity.` - complete
- [x] `Task checkbox-461: Manual unblock: complete an EVM public-input and verification-key registry helper slice using browser-compatible crypto abstractions and deterministic tests.` - complete
- [x] `Task checkbox-462: Manual unblock: add developer-panel live inspection snapshots for logic parse, proof, cache, ML/NLP, and ZKP capability state.` - complete
- [x] `Task checkbox-463: Manual unblock: add CLI/devtools command adapter parity for 'logic/cli.py' as browser/devtools-safe TypeScript entry points.` - complete
- [x] `Task checkbox-464: Manual unblock: port IPFS/IPLD proof cache semantics to browser-native storage and content-addressed cache adapters with deterministic tests.` - complete
- [x] `Task checkbox-465: Manual unblock: port 'logic/CEC/native/advanced_inference.py' by adding a TypeScript advanced-inference registry, rule classification helpers, and parity tests for cognitive, modal, and deontic rule selection.` - complete
- [x] `Task checkbox-466: Manual unblock: port 'logic/CEC/native/cec_proof_cache.py' by adding CEC proof cache keys, TTL/LRU behavior, validation metadata, and deterministic browser storage tests.` - complete
- [x] `Task checkbox-467: Manual unblock: port 'logic/CEC/native/cec_zkp_integration.py' by adding an educational local ZKP integration facade with simulated backend parity and fail-closed unsupported-backend results.` - complete
- [x] `Task checkbox-468: Manual unblock: port 'logic/CEC/native/context_manager.py' by adding discourse/context snapshots, entity bindings, temporal scopes, and deterministic merge/rollback tests.` - complete
- [x] `Task checkbox-469: Manual unblock: port 'logic/CEC/native/dcec_cleaning.py' by adding DCEC text/formula normalization, token cleanup, and fixture tests for malformed legal-text inputs.` - complete
- [x] `Task checkbox-470: Manual unblock: port 'logic/CEC/native/dcec_integration.py' by adding DCEC token/formula conversion helpers, CEC bridge metadata, and round-trip validation tests.` - complete
- [x] `Task checkbox-471: Manual unblock: port 'logic/CEC/native/dcec_namespace.py' by adding namespace registration, symbol statistics, validation diagnostics, and collision tests.` - complete
- [x] `Task checkbox-472: Manual unblock: port 'logic/CEC/native/dcec_parsing.py' by adding parser utility parity for DCEC atom, connective, quantifier, and modal/deontic forms.` - complete
- [x] `Task checkbox-473: Manual unblock: port 'logic/CEC/native/dcec_prototypes.py' by adding prototype/type-conflict checks and deterministic validation fixtures.` - complete
- [x] `Task checkbox-474: Manual unblock: port 'logic/CEC/native/dcec_types.py' by adding DCEC container helpers, type guards, serialization, and compatibility tests.` - complete
- [x] `Task checkbox-475: Manual unblock: port 'logic/CEC/native/enhanced_grammar_parser.py' by adding chart-parser style diagnostics, parse alternatives, and grammar fixture tests.` - complete
- [!] `Task checkbox-476: Manual unblock: port 'logic/CEC/native/error_handling.py' by adding fail-closed CEC error facades, recovery metadata, and validation result adapters.` - blocked
- [x] `Task checkbox-477: Manual unblock: port 'logic/CEC/native/event_calculus.py' by adding event, fluent, happens, holds, initiates, terminates, and timeline query helpers with parity tests.` - complete
- [x] `Task checkbox-478: Manual unblock: port 'logic/CEC/native/grammar_engine.py' and 'grammar_loader.py' by adding deterministic in-memory grammar artifacts, loader validation, and no-network browser tests.` - complete
- [x] `Task checkbox-479: Manual unblock: port 'logic/CEC/native/inference_rules/base.py', 'cognitive.py', and 'modal.py' by adding rule tables, applicability checks, proof-step metadata, and focused parity tests.` - complete
- [!] `Task checkbox-480: Manual unblock: port 'logic/CEC/native/prover_core.py' by adding a bounded browser-native proof facade, deterministic search limits, proof summaries, and failure diagnostics.` - blocked
- [x] `Task checkbox-481: Manual unblock: port 'logic/external_provers/interactive/coq_prover_bridge.py' by adding a local adapter contract that reports WASM-capable support when available and fail-closed unsupported-local results otherwise.` - complete

### Latest Round

- Target: `Task checkbox-200: Port remaining Python logic module 'logic/CEC/native/advanced_inference.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
- Result: `valid`
- Summary: Ported the advanced_inference.py surface with a bounded browser-native DCEC derivation API and validation coverage.
- Impact: src/lib/logic/cec/advancedInference.ts now exposes deriveDcecAdvancedInferences for deterministic local closure generation with Python-compatible step metadata and explicit no-Python/no-runtime-bridge flags. src/lib/logic/cec/advancedInference.test.ts validates modal derivations, metadata, and fail-closed local bounds; the port ledger marks the selected advanced_inference.py task complete.
- Accepted changed files: `docs/IPFS_DATASETS_LOGIC_TYPESCRIPT_PORT_PLAN.md`, `src/lib/logic/cec/advancedInference.test.ts`, `src/lib/logic/cec/advancedInference.ts`

### Blocked Backlog

- `Task checkbox-106: Browser-native ZKP acceleration and parallel proof search parity.`
  - Failures since success: `5`
  - Autonomous revisit: `skipped; task failure budget exhausted`
  - Failure kinds: `{"daemon_exception": 3, "parse": 2}`
  - Latest failure kind: `daemon_exception`
  - Latest errors: llm_router could not generate with model='gpt-5.5' provider='auto'. Configure the provider credentials or pass --provider. Original error: copilot CLI binary not found on PATH (required for session/tracing flags). Install the GitHub Copilot...
- `Task checkbox-107: Complete modal tableaux and countermodel generation/visualization parity.`
  - Failures since success: `3`
  - Autonomous revisit: `skipped; task failure budget exhausted`
  - Failure kinds: `{"daemon_exception": 3}`
  - Latest failure kind: `daemon_exception`
  - Latest errors: llm_router could not generate with model='gpt-5.5' provider='auto'. Configure the provider credentials or pass --provider. Original error: copilot CLI binary not found on PATH (required for session/tracing flags). Install the GitHub Copilot...
- `Task checkbox-179: Remove 'nlpUnavailable' and 'mlUnavailable' capability flags once browser-native parity is implemented.`
  - Failures since success: `0`
- `Task checkbox-202: Port remaining Python logic module 'logic/CEC/native/cec_proof_cache.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
  - Failures since success: `0`
- `Task checkbox-203: Port remaining Python logic module 'logic/CEC/native/cec_zkp_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
  - Failures since success: `0`
- `Task checkbox-204: Port remaining Python logic module 'logic/CEC/native/context_manager.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
  - Failures since success: `0`
- `Task checkbox-205: Port remaining Python logic module 'logic/CEC/native/dcec_cleaning.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
  - Failures since success: `0`
- `Task checkbox-208: Port remaining Python logic module 'logic/CEC/native/dcec_integration.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
  - Failures since success: `0`
- `Task checkbox-209: Port remaining Python logic module 'logic/CEC/native/dcec_namespace.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
  - Failures since success: `0`
- `Task checkbox-210: Port remaining Python logic module 'logic/CEC/native/dcec_parsing.py' to browser-native TypeScript/WASM, including focused validation tests and no server or Python runtime dependency.`
  - Failures since success: `0`

### Required Daemon Behavior

- Work only on the current port-plan target unless the task is already complete in code and tests.
- For implementation tasks, accepted work must change runtime TypeScript under `src/lib/logic/`; fixture-only work is reserved for fixture/capture/documentation tasks.
- If a round fails, keep the task marked as needing follow-up and use the validation error as the next-cycle constraint.
- Mark a task complete only after TypeScript validation and logic-port tests pass for the accepted change.
- Keep browser runtime changes TypeScript/WASM-native with no server or Python service dependency.
<!-- logic-port-daemon-task-board:end -->
