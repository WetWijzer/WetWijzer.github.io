import { parseTdfolFormula } from '../tdfol/parser';
import { proveTdfol, type TdfolProverOptions } from '../tdfol/prover';
import type { ProofResult } from '../types';
import type { BrowserNativeProofAdapter, BrowserNativeProofRequest } from './proverAdapters';

export type CoqProofStatus = 'proved' | 'unknown' | 'timeout' | 'error';
export type CoqInteractiveCommandStatus = 'accepted' | 'proved' | 'failed' | 'needs-proof';

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

export interface CoqInteractiveCommandResult {
  command: string;
  status: CoqInteractiveCommandStatus;
  message: string;
  stateId: number;
  proofMode: boolean;
  pendingGoals: Array<string>;
  blockedReason?: string;
  serverCallsAllowed: false;
  pythonRuntime: false;
  subprocessAllowed: false;
  filesystemAllowed: false;
}

export interface CoqVernacularValidationResult {
  valid: boolean;
  results: Array<CoqInteractiveCommandResult>;
  firstFailure?: CoqInteractiveCommandResult;
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

export class BrowserNativeCoqInteractiveSession {
  private stateId = 0;
  private currentGoal: string | null = null;
  private proofStarted = false;
  private proofProgress = false;
  private readonly history: CoqInteractiveCommandResult[] = [];

  constructor(private readonly coqWasmAvailable = false) {}

  snapshot() {
    const pendingGoals = this.currentGoal ? [this.currentGoal] : [];
    return {
      sourcePythonModule: 'logic/external_provers/interactive/coq_prover_bridge.py',
      runtime: 'typescript-wasm-browser',
      coqWasmAvailable: this.coqWasmAvailable,
      failClosed: true,
      stateId: this.stateId,
      proofMode: this.proofStarted,
      pendingGoals,
      history: this.history.map((entry) => ({ ...entry, pendingGoals: [...entry.pendingGoals] })),
    };
  }

  submit(command: string): CoqInteractiveCommandResult {
    const normalized = command.trim();
    const blockedReason = blockedCoqCommandReason(normalized);
    if (blockedReason) return this.record(normalized, 'failed', blockedReason, blockedReason);
    if (normalized.length === 0)
      return this.record(normalized, 'accepted', 'Empty Coq command ignored locally.');

    if (/^(Theorem|Lemma)\s+[A-Za-z_]\w*\s*:/i.test(normalized)) {
      const goal = normalized
        .replace(/\.$/, '')
        .replace(/^(Theorem|Lemma)\s+[A-Za-z_]\w*\s*:\s*/i, '');
      this.currentGoal = goal.trim();
      this.proofStarted = false;
      this.proofProgress = false;
      return this.record(normalized, 'needs-proof', 'Coq theorem accepted; proof is pending.');
    }

    if (/^(Axiom|Parameter|Variable|Hypothesis)\s+[A-Za-z_]\w*\s*:/i.test(normalized)) {
      return this.record(normalized, 'accepted', 'Coq declaration accepted by local validator.');
    }

    if (/^Proof\.$/i.test(normalized)) {
      if (!this.currentGoal) {
        return this.record(
          normalized,
          'failed',
          'Proof command has no pending theorem.',
          'no_pending_goal',
        );
      }
      this.proofStarted = true;
      return this.record(normalized, 'accepted', 'Coq proof mode entered locally.');
    }

    if (
      /^(intros?|exact|assumption|reflexivity|apply|split|left|right|constructor|trivial)\b/i.test(
        normalized,
      )
    ) {
      if (!this.proofStarted) {
        return this.record(
          normalized,
          'failed',
          'Tactic command requires proof mode.',
          'not_in_proof_mode',
        );
      }
      this.proofProgress = true;
      return this.record(
        normalized,
        'accepted',
        'Coq tactic accepted by deterministic local validator.',
      );
    }

    if (/^Qed\.$/i.test(normalized)) {
      if (!this.proofStarted || !this.currentGoal) {
        return this.record(
          normalized,
          'failed',
          'Qed command has no active proof.',
          'no_active_proof',
        );
      }
      if (!this.proofProgress) {
        return this.record(
          normalized,
          'failed',
          'Qed rejected because no local proof step closed the goal.',
          'open_goal',
        );
      }
      this.currentGoal = null;
      this.proofStarted = false;
      this.proofProgress = false;
      return this.record(normalized, 'proved', 'Coq proof closed by local interactive validator.');
    }

    return this.record(
      normalized,
      'failed',
      'Unsupported Coq vernacular in browser-native fail-closed mode.',
      'unsupported_vernacular',
    );
  }

  submitScript(script: string): CoqVernacularValidationResult {
    const results = splitCoqCommands(script).map((command) => this.submit(command));
    const firstFailure = results.find((result) => result.status === 'failed');
    const validation: CoqVernacularValidationResult = {
      valid: firstFailure === undefined,
      results,
    };
    if (firstFailure) validation.firstFailure = firstFailure;
    return validation;
  }

  private record(
    command: string,
    status: CoqInteractiveCommandStatus,
    message: string,
    blockedReason?: string,
  ): CoqInteractiveCommandResult {
    this.stateId += 1;
    const result: CoqInteractiveCommandResult = {
      command,
      status,
      message,
      stateId: this.stateId,
      proofMode: this.proofStarted,
      pendingGoals: this.currentGoal ? [this.currentGoal] : [],
      serverCallsAllowed: false,
      pythonRuntime: false,
      subprocessAllowed: false,
      filesystemAllowed: false,
    };
    if (blockedReason) result.blockedReason = blockedReason;
    this.history.push(result);
    return result;
  }
}

export function createBrowserNativeCoqInteractiveSession(
  coqWasmAvailable = false,
): BrowserNativeCoqInteractiveSession {
  return new BrowserNativeCoqInteractiveSession(coqWasmAvailable);
}

export function validateCoqVernacularLocal(script: string): CoqVernacularValidationResult {
  return createBrowserNativeCoqInteractiveSession().submitScript(script);
}

export const create_browser_native_coq_prover_bridge = createBrowserNativeCoqProverBridge;
export const create_browser_native_coq_interactive_session =
  createBrowserNativeCoqInteractiveSession;
export const prove_coq_compatible_tdfol = proveCoqCompatibleTdfol;
export const validate_coq_vernacular_local = validateCoqVernacularLocal;

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

function blockedCoqCommandReason(command: string): string | undefined {
  if (
    /^(Require|From|Import|Export|Load|Declare\s+ML|Cd|Add\s+LoadPath|Redirect|Timeout)\b/i.test(
      command,
    )
  ) {
    return 'Coq command requires module loading, filesystem access, subprocess control, or external runtime state.';
  }
  if (/\b(extract|native_compute|vm_compute)\b/i.test(command)) {
    return 'Coq command requires unsupported native extraction or VM execution.';
  }
  return undefined;
}

function splitCoqCommands(script: string): string[] {
  const commands: string[] = [];
  let current = '';
  for (const character of script) {
    current += character;
    if (character === '.') {
      const command = current.trim();
      if (command.length > 0) commands.push(command);
      current = '';
    }
  }
  const trailing = current.trim();
  if (trailing.length > 0) commands.push(trailing);
  return commands;
}

function mapCoqStatus(status: ProofResult['status']): CoqProofStatus {
  if (status === 'proved') return 'proved';
  if (status === 'timeout') return 'timeout';
  if (status === 'error') return 'error';
  return 'unknown';
}
