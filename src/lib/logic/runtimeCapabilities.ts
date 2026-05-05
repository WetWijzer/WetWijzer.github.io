import { getMLConfidenceModelState } from './mlConfidence';

export type LogicRuntimeMode = 'browser_native';
export type LogicPortTarget = 'full_python_logic_parity_typescript_wasm';
export type LogicCapabilityStatus = 'complete' | 'incomplete';
export type LogicMlConfidenceSource = 'heuristic' | 'trained' | 'artifact';

export type LogicWasmProverId = 'z3' | 'cvc5' | 'tau-prolog' | 'lean' | 'coq';
export type LogicWasmProverWorkflow =
  | 'smt'
  | 'constraint-solving'
  | 'logic-programming'
  | 'interactive-theorem-proving'
  | 'proof-checking';
export type LogicWasmProverStatus = 'integrated' | 'candidate' | 'blocked';

export interface LocalWasmProverEvaluation {
  id: LogicWasmProverId;
  label: string;
  workflows: LogicWasmProverWorkflow[];
  status: LogicWasmProverStatus;
  browserNative: boolean;
  serverCallsAllowed: false;
  integration: 'local_wasm_adapter' | 'local_js_adapter' | 'deferred';
  notes: string;
}

export interface LogicRuntimeCapabilities {
  mode: LogicRuntimeMode;
  target: LogicPortTarget;
  serverCallsAllowed: false;
  fol: {
    regexParser: true;
    nlpStatus: LogicCapabilityStatus;
    browserNativeNlp: boolean;
    mlStatus: LogicCapabilityStatus;
    browserNativeMlConfidence: boolean;
    localModelArtifactLoading: boolean;
    mlConfidenceSource: LogicMlConfidenceSource;
    mlConfidenceModelLoaded: boolean;
  };
  deontic: {
    ruleExtractor: true;
    mlStatus: LogicCapabilityStatus;
    browserNativeMlConfidence: boolean;
    localModelArtifactLoading: boolean;
    mlConfidenceSource: LogicMlConfidenceSource;
    mlConfidenceModelLoaded: boolean;
  };
  proving: {
    lightweightReasoning: true;
    wasmProverStatus: LogicCapabilityStatus;
    externalProverUnavailable: true;
    browserWasmProver: boolean;
    localWasmProvers: LocalWasmProverEvaluation[];
    recommendedLocalProvers: LogicWasmProverId[];
  };
}

const LOCAL_WASM_PROVER_EVALUATIONS: LocalWasmProverEvaluation[] = [
  {
    id: 'z3',
    label: 'Z3 WASM',
    workflows: ['smt', 'constraint-solving'],
    status: 'candidate',
    browserNative: true,
    serverCallsAllowed: false,
    integration: 'local_wasm_adapter',
    notes: 'Suitable for bounded SMT-style checking once formula lowering is added.',
  },
  {
    id: 'cvc5',
    label: 'cvc5 WASM',
    workflows: ['smt', 'constraint-solving'],
    status: 'candidate',
    browserNative: true,
    serverCallsAllowed: false,
    integration: 'local_wasm_adapter',
    notes: 'Suitable as a second local SMT backend, pending browser bundle validation.',
  },
  {
    id: 'tau-prolog',
    label: 'Tau Prolog',
    workflows: ['logic-programming'],
    status: 'candidate',
    browserNative: true,
    serverCallsAllowed: false,
    integration: 'local_js_adapter',
    notes: 'Feasible for Prolog-style rule evaluation without subprocesses.',
  },
  {
    id: 'lean',
    label: 'Lean-style proof checking',
    workflows: ['interactive-theorem-proving', 'proof-checking'],
    status: 'blocked',
    browserNative: false,
    serverCallsAllowed: false,
    integration: 'deferred',
    notes:
      'No in-repo browser-native Lean checker is integrated; keep proofs local-only until a WASM checker is available.',
  },
  {
    id: 'coq',
    label: 'Coq-style proof checking',
    workflows: ['interactive-theorem-proving', 'proof-checking'],
    status: 'blocked',
    browserNative: false,
    serverCallsAllowed: false,
    integration: 'deferred',
    notes:
      'No in-repo browser-native Coq checker is integrated; do not route browser proofs to a Python or server wrapper.',
  },
];

export function getLocalWasmProverEvaluations(): LocalWasmProverEvaluation[] {
  return LOCAL_WASM_PROVER_EVALUATIONS.map((prover) => ({
    ...prover,
    workflows: [...prover.workflows],
  }));
}

export function getRecommendedLocalWasmProvers(
  workflow?: LogicWasmProverWorkflow,
): LocalWasmProverEvaluation[] {
  return getLocalWasmProverEvaluations().filter((prover) => {
    if (!prover.browserNative || prover.status === 'blocked') return false;
    return workflow === undefined || prover.workflows.includes(workflow);
  });
}

export function getLogicRuntimeCapabilities(): LogicRuntimeCapabilities {
  const localWasmProvers = getLocalWasmProverEvaluations();
  const recommendedLocalProvers = getRecommendedLocalWasmProvers().map((prover) => prover.id);
  const mlState = getMLConfidenceModelState();

  return {
    mode: 'browser_native',
    target: 'full_python_logic_parity_typescript_wasm',
    serverCallsAllowed: false,
    fol: {
      regexParser: true,
      nlpStatus: 'complete',
      browserNativeNlp: true,
      mlStatus: 'complete',
      browserNativeMlConfidence: true,
      localModelArtifactLoading: true,
      mlConfidenceSource: mlState.source,
      mlConfidenceModelLoaded: mlState.loaded,
    },
    deontic: {
      ruleExtractor: true,
      mlStatus: 'complete',
      browserNativeMlConfidence: true,
      localModelArtifactLoading: true,
      mlConfidenceSource: mlState.source,
      mlConfidenceModelLoaded: mlState.loaded,
    },
    proving: {
      lightweightReasoning: true,
      wasmProverStatus: 'incomplete',
      externalProverUnavailable: true,
      browserWasmProver: recommendedLocalProvers.length > 0,
      localWasmProvers,
      recommendedLocalProvers,
    },
  };
}
