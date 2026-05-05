import {
  getLocalWasmProverEvaluations,
  getLogicRuntimeCapabilities,
  getRecommendedLocalWasmProvers,
} from './runtimeCapabilities';
import {
  ML_CONFIDENCE_FEATURE_NAMES,
  MLConfidenceModelArtifact,
  loadMLConfidenceModelArtifact,
  unloadMLConfidenceModel,
} from './mlConfidence';
import { convertLegalTextToDeontic } from './deontic';
import { parseFolText } from './fol';

describe('logic runtime capabilities', () => {
  beforeEach(() => {
    unloadMLConfidenceModel();
  });

  it('declares browser-native mode with no server calls', () => {
    expect(getLogicRuntimeCapabilities()).toMatchObject({
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
        mlConfidenceSource: 'heuristic',
        mlConfidenceModelLoaded: false,
      },
      deontic: {
        ruleExtractor: true,
        mlStatus: 'complete',
        browserNativeMlConfidence: true,
        localModelArtifactLoading: true,
        mlConfidenceSource: 'heuristic',
        mlConfidenceModelLoaded: false,
      },
      proving: {
        lightweightReasoning: true,
        wasmProverStatus: 'incomplete',
        externalProverUnavailable: true,
        browserWasmProver: true,
        recommendedLocalProvers: ['z3', 'cvc5', 'tau-prolog'],
      },
    });
  });

  it('evaluates local WASM prover routes without server or Python wrappers', () => {
    const evaluations = getLocalWasmProverEvaluations();

    expect(evaluations.map((prover) => prover.id)).toEqual([
      'z3',
      'cvc5',
      'tau-prolog',
      'lean',
      'coq',
    ]);
    expect(evaluations.every((prover) => prover.serverCallsAllowed === false)).toBe(true);
    expect(
      evaluations.filter((prover) => prover.status !== 'blocked').map((prover) => prover.id),
    ).toEqual(['z3', 'cvc5', 'tau-prolog']);
    expect(
      evaluations.filter((prover) => prover.status === 'blocked').map((prover) => prover.id),
    ).toEqual(['lean', 'coq']);
  });

  it('selects deterministic browser-native prover candidates by workflow', () => {
    expect(getRecommendedLocalWasmProvers('smt').map((prover) => prover.id)).toEqual([
      'z3',
      'cvc5',
    ]);
    expect(getRecommendedLocalWasmProvers('logic-programming').map((prover) => prover.id)).toEqual([
      'tau-prolog',
    ]);
    expect(getRecommendedLocalWasmProvers('proof-checking')).toEqual([]);
  });

  it('surfaces browser-native FOL NLP and ML capabilities in converter outputs', () => {
    expect(parseFolText('All humans are mortal').capabilities).toEqual({
      nlpUnavailable: false,
      browserNativeMlConfidence: true,
      localModelArtifactLoading: true,
      mlUnavailable: false,
      serverCallsAllowed: false,
    });
    expect(parseFolText('All humans are mortal').nlp).toMatchObject({
      provider: 'deterministic-token-classifier',
      serverCallsAllowed: false,
      pythonSpacy: false,
      fallback: 'none',
      predicateCandidates: ['humans', 'mortal'],
    });

    expect(convertLegalTextToDeontic('The tenant must pay rent.').capabilities).toEqual({
      browserNativeMlConfidence: true,
      localModelArtifactLoading: true,
      mlUnavailable: false,
      serverCallsAllowed: false,
    });
  });

  it('reports explicit local ML artifact loading without mlUnavailable branches', () => {
    const artifact: MLConfidenceModelArtifact = {
      format: 'deterministic-linear-v1',
      version: 'runtime-capability-fixture',
      featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice(),
      weights: ML_CONFIDENCE_FEATURE_NAMES.map((name) => (name === 'total_predicates' ? 0.1 : 0)),
      bias: 0.4,
    };

    loadMLConfidenceModelArtifact(artifact);
    expect(getLogicRuntimeCapabilities()).toMatchObject({
      fol: {
        browserNativeMlConfidence: true,
        localModelArtifactLoading: true,
        mlConfidenceSource: 'artifact',
        mlConfidenceModelLoaded: true,
      },
      deontic: {
        browserNativeMlConfidence: true,
        localModelArtifactLoading: true,
        mlConfidenceSource: 'artifact',
        mlConfidenceModelLoaded: true,
      },
    });
    unloadMLConfidenceModel();
  });

  it('omits deprecated unavailable flags from runtime capability reporting', () => {
    const capabilities = getLogicRuntimeCapabilities();

    expect(Object.prototype.hasOwnProperty.call(capabilities.fol, 'nlpUnavailable')).toBe(false);
    expect(Object.prototype.hasOwnProperty.call(capabilities.fol, 'mlUnavailable')).toBe(false);
    expect(Object.prototype.hasOwnProperty.call(capabilities.deontic, 'mlUnavailable')).toBe(false);
    expect(capabilities.fol).toMatchObject({
      nlpStatus: 'complete',
      browserNativeNlp: true,
      mlStatus: 'complete',
      browserNativeMlConfidence: true,
    });
  });
});
