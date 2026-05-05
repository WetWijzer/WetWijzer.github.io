import { parseTdfolFormula } from '../tdfol/parser';
import { proveTdfol, type TdfolProverOptions } from '../tdfol/prover';
import type { ProofResult } from '../types';
import type { BrowserNativeProofAdapter, BrowserNativeProofRequest } from './proverAdapters';

export type CoqProofStatus = 'proved' | 'unknown' | 'timeout' | 'error';

export interface CoqCompatibilityMetadata {
  adapter: 'browser-native-coq-prover-bridge';
  sourcePythonModule: 'logic/external_provers/interactive/coq_prover_bridge.py';
  externalBinaryAllowed: false;
  serverCallsAllowed: false;
  pythonRuntime: false;
  subprocessAllowed: false;
  rpcAllowed: false;
  wasmRuntime: 'local-typescript-tdfol' | 'not-bundled';
  coqWasmAvailable: boolean;
  command: null;
  coqVersion: null;
  vernacular: string;
  statusMapping: CoqProofStatus;
  warnings: string[];
}

export interface BrowserNativeCoqProofResult extends ProofResult {
  coq: CoqCompatibilityMetadata;
}

export interface BrowserNativeCoqProverBridgeOptions extends TdfolProverOptions {
  coqWasmAvailable?: boolean;
}

export function createBrowserNativeCoqProverBridge(
  options: BrowserNativeCoqProverBridgeOptions = {},
): BrowserNativeProofAdapter {
  return {
    metadata: {
      logic: 'tdfol',
      name: 'browser-native-coq-prover-bridge',
      runtime: 'typescript-wasm-browser',
      requiresExternalProver: false,
      proverFamily: 'local',
    },
    supports: (logic) => logic === 'tdfol',
    prove(request) {
      return proveCoqCompatibleTdfol(request, options);
    },
  };
}

export function proveCoqCompatibleTdfol(
  request: BrowserNativeProofRequest,
  options: BrowserNativeCoqProverBridgeOptions = {},
): BrowserNativeCoqProofResult {
  try {
    const theorem = parseTdfolFormula(request.theorem);
    const axioms = request.axioms.map(parseTdfolFormula);
    const theorems = request.theorems?.map(parseTdfolFormula);
    const result = proveTdfol(
      theorem,
      { axioms, theorems },
      {
        ...options,
        maxSteps: request.maxSteps ?? options.maxSteps,
        maxDerivedFormulas: request.maxDerivedFormulas ?? options.maxDerivedFormulas,
      },
    );

    return {
      ...result,
      method: `coq-compatible:${result.method ?? 'tdfol'}`,
      coq: metadata(result, coqScript(request), options.coqWasmAvailable === true),
    };
  } catch (error) {
    const result: ProofResult = {
      status: 'error',
      theorem: request.theorem,
      steps: [],
      method: 'coq-compatible:parse-error',
      error: error instanceof Error ? error.message : String(error),
    };
    return {
      ...result,
      coq: metadata(
        result,
        `(* invalid TDFOL request; failed closed locally *)\n(* theorem: ${request.theorem} *)`,
        options.coqWasmAvailable === true,
      ),
    };
  }
}

export const create_browser_native_coq_prover_bridge = createBrowserNativeCoqProverBridge;
export const prove_coq_compatible_tdfol = proveCoqCompatibleTdfol;

function metadata(
  result: ProofResult,
  vernacular: string,
  coqWasmAvailable: boolean,
): CoqCompatibilityMetadata {
  return {
    adapter: 'browser-native-coq-prover-bridge',
    sourcePythonModule: 'logic/external_provers/interactive/coq_prover_bridge.py',
    externalBinaryAllowed: false,
    serverCallsAllowed: false,
    pythonRuntime: false,
    subprocessAllowed: false,
    rpcAllowed: false,
    wasmRuntime: coqWasmAvailable ? 'local-typescript-tdfol' : 'not-bundled',
    coqWasmAvailable,
    command: null,
    coqVersion: null,
    vernacular,
    statusMapping: mapCoqStatus(result.status),
    warnings: [
      result.status === 'error'
        ? 'Coq-compatible TDFOL parsing failed locally; no external fallback was attempted.'
        : 'Coq subprocesses, RPC, Python bridges, and server calls are unavailable in the browser; proof search used the local TypeScript TDFOL engine and emitted Coq compatibility metadata.',
    ],
  };
}

function coqScript(request: BrowserNativeProofRequest): string {
  const axiomLines = request.axioms.map(
    (axiom, index) => `Axiom h${index + 1} : ${coqFormulaText(axiom)}.`,
  );
  const proof =
    axiomLines.length > 0
      ? 'Proof.\n  exact h1.\nQed.'
      : 'Proof.\n  fail "No browser-local Coq proof term is available".\nQed.';
  return [...axiomLines, `Theorem target : ${coqFormulaText(request.theorem)}.`, proof].join('\n');
}

function coqFormulaText(value: string): string {
  return value
    .replace(/\bforall\b/gi, 'forall')
    .replace(/\bexists\b/gi, 'exists')
    .replace(/\band\b/gi, '/\\')
    .replace(/\bor\b/gi, '\\/')
    .replace(/\bnot\b/gi, 'not')
    .replace(/->|→/g, '->')
    .replace(/[^\w\s().,/:\\<>-]/g, '_')
    .replace(/\b([A-Za-z_]\w*)\(([^()]+)\)/g, '($1 $2)')
    .replace(/,\s*/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function mapCoqStatus(status: ProofResult['status']): CoqProofStatus {
  if (status === 'proved') return 'proved';
  if (status === 'timeout') return 'timeout';
  if (status === 'error') return 'error';
  return 'unknown';
}
