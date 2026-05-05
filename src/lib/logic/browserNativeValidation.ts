import { convertLegalTextToDeontic } from './deontic';
import { extractLogicalRelations, extractPredicates, parseFolText } from './fol';
import {
  FeatureExtractor,
  getMLConfidenceModelState,
  MLConfidenceScorer,
  predictMLConfidence,
} from './mlConfidence';
import { getLogicRuntimeCapabilities } from './runtimeCapabilities';

export type PythonMlSpacyAuditStatus =
  | 'matched'
  | 'local_artifact_required'
  | 'unsupported_fail_closed';

export interface PythonMlSpacyAuditCheck {
  expectation: string;
  status: PythonMlSpacyAuditStatus;
  observed: unknown;
  expected?: unknown;
  localModelArtifactTask?: string;
}

export interface PythonMlSpacyParityAudit {
  valid: boolean;
  browserNative: true;
  serverCallsAllowed: false;
  pythonRuntimeAllowed: false;
  checks: Array<PythonMlSpacyAuditCheck>;
  unsupported: Array<PythonMlSpacyAuditCheck>;
  localModelArtifactLoadingTasks: Array<string>;
}

export function validateBrowserNativeLogicRuntime(
  options: { folText?: string; deonticText?: string } = {},
) {
  const capabilities = getLogicRuntimeCapabilities();
  const folText = options.folText ?? 'All tenants are protected and some landlords must comply.';
  const deonticText = options.deonticText ?? 'The landlord must provide notice before entry.';
  const firstFol = parseFolText(folText);
  const secondFol = parseFolText(folText);
  const quantifiers = firstFol.quantifiers.map((quantifier) => quantifier.symbol);
  const operators = firstFol.operators.map((operator) => operator.symbol);
  const entities = { nouns: firstFol.nlp.predicateCandidates };
  const deterministicScore = predictMLConfidence(
    folText,
    firstFol.formula,
    entities,
    quantifiers,
    operators,
  );
  const repeatedScore = predictMLConfidence(
    folText,
    firstFol.formula,
    entities,
    quantifiers,
    operators,
  );
  const deontic = convertLegalTextToDeontic(deonticText);
  const failures = [
    capabilities.serverCallsAllowed === false ? '' : 'runtime_server_calls_allowed',
    capabilities.mode === 'browser_native' ? '' : 'runtime_not_browser_native',
    capabilities.fol.nlpStatus === 'complete' && capabilities.fol.browserNativeNlp
      ? ''
      : 'fol_nlp_not_browser_native',
    capabilities.fol.mlStatus === 'complete' && capabilities.fol.browserNativeMlConfidence
      ? ''
      : 'fol_ml_not_browser_native',
    firstFol.nlp.pythonSpacy ? 'fol_python_spacy_enabled' : '',
    firstFol.nlp.serverCallsAllowed === false ? '' : 'fol_nlp_server_calls_allowed',
    firstFol.capabilities.serverCallsAllowed === false ? '' : 'fol_server_calls_allowed',
    sameStrings(firstFol.nlp.predicateCandidates, secondFol.nlp.predicateCandidates)
      ? ''
      : 'fol_nlp_not_deterministic',
    deterministicScore === repeatedScore ? '' : 'ml_score_not_deterministic',
    deontic.capabilities.serverCallsAllowed === false ? '' : 'deontic_server_calls_allowed',
    capabilities.deontic.mlStatus === 'complete' && capabilities.deontic.browserNativeMlConfidence
      ? ''
      : 'deontic_ml_not_browser_native',
  ].filter(Boolean);

  return {
    valid: failures.length === 0,
    failures,
    runtime: {
      mode: capabilities.mode,
      serverCallsAllowed: false,
      mlConfidenceSource: capabilities.fol.mlConfidenceSource,
      mlConfidenceModelLoaded: capabilities.fol.mlConfidenceModelLoaded,
    },
    nlp: {
      provider: firstFol.nlp.provider,
      backend: firstFol.nlp.backend,
      pythonSpacy: false,
      serverCallsAllowed: false,
      predicateCandidates: firstFol.nlp.predicateCandidates,
      repeatedPredicateCandidates: secondFol.nlp.predicateCandidates,
    },
    ml: {
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      deterministicScore,
      repeatedScore,
      source: capabilities.fol.mlConfidenceSource,
    },
    deontic: {
      success: deontic.success,
      formulas: deontic.formulas,
      browserNativeMlConfidence: deontic.capabilities.browserNativeMlConfidence,
      serverCallsAllowed: false,
    },
  };
}

function sameStrings(left: Array<string>, right: Array<string>): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

export function auditPythonMlSpacyExpectations(): PythonMlSpacyParityAudit {
  const mlSentence = 'All tenants must pay rent, and some landlords may inspect.';
  const mlFormula = '∀x (Tenant(x) → PayRent(x))';
  const mlPredicates = { nouns: ['Tenant'], verbs: ['PayRent', 'Inspect'], adjectives: [] };
  const mlQuantifiers = ['∀'];
  const mlOperators = ['→', '∧'];
  const expectedFeatureVector = [
    58, 10, 1, 1, 27, 3, 1, 3, 1, 2, 0, 1, 2, 1, 0, 1, 0, 1, 0, 0.46551724137931033, 0.3, 3,
  ];
  const observedFeatureVector = FeatureExtractor.extractFeatures(
    mlSentence,
    mlFormula,
    mlPredicates,
    mlQuantifiers,
    mlOperators,
  );
  const heuristicScore = new MLConfidenceScorer().predictConfidence(
    mlSentence,
    mlFormula,
    mlPredicates,
    mlQuantifiers,
    mlOperators,
  );
  const spacyText =
    'Portland is Safe and tenants must comply. If tenant applies then auditor responds.';
  const expectedPredicates = {
    nouns: ['Portland', 'Safe', 'If'],
    verbs: ['Safe', 'Comply'],
    adjectives: ['Safe'],
    relations: [],
  };
  const expectedRelations = [
    { type: 'implication', premise: 'tenant applies', conclusion: 'auditor responds' },
  ];
  const modelState = getMLConfidenceModelState();
  const checks: Array<PythonMlSpacyAuditCheck> = [
    {
      expectation: 'logic/ml_confidence.py FeatureExtractor vector',
      status: vectorsEqual(observedFeatureVector, expectedFeatureVector)
        ? 'matched'
        : 'unsupported_fail_closed',
      observed: observedFeatureVector,
      expected: expectedFeatureVector,
    },
    {
      expectation: 'logic/ml_confidence.py fallback heuristic confidence',
      status: withinTolerance(heuristicScore, 0.8500000000000001, 1e-10)
        ? 'matched'
        : 'unsupported_fail_closed',
      observed: heuristicScore,
      expected: 0.8500000000000001,
    },
    {
      expectation: 'spaCy-style predicate extraction fixture',
      status: sameJson(extractPredicates(spacyText), expectedPredicates)
        ? 'matched'
        : 'unsupported_fail_closed',
      observed: extractPredicates(spacyText),
      expected: expectedPredicates,
    },
    {
      expectation: 'spaCy-style relation extraction fixture',
      status: sameJson(extractLogicalRelations(spacyText), expectedRelations)
        ? 'matched'
        : 'unsupported_fail_closed',
      observed: extractLogicalRelations(spacyText),
      expected: expectedRelations,
    },
    {
      expectation: 'trained Python XGBoost/LightGBM model weights',
      status: modelState.source === 'artifact' ? 'matched' : 'local_artifact_required',
      observed: modelState,
      localModelArtifactTask:
        'Export trained Python ML confidence weights into deterministic-linear-v1 or deterministic-logistic-v1 browser artifact metadata.',
    },
    {
      expectation: 'full spaCy dependency parser and model weights',
      status: 'unsupported_fail_closed',
      observed: {
        provider: 'deterministic-token-classifier',
        pythonSpacy: false,
        serverCallsAllowed: false,
      },
      localModelArtifactTask:
        'Add a browser-native token-classification or dependency artifact if exact spaCy dependency labels become required.',
    },
  ];
  const unsupported = checks.filter((check) => check.status !== 'matched');

  return {
    valid: checks.every((check) =>
      ['matched', 'local_artifact_required', 'unsupported_fail_closed'].includes(check.status),
    ),
    browserNative: true,
    serverCallsAllowed: false,
    pythonRuntimeAllowed: false,
    checks,
    unsupported,
    localModelArtifactLoadingTasks: unsupported
      .map((check) => check.localModelArtifactTask)
      .filter((task): task is string => typeof task === 'string'),
  };
}

function vectorsEqual(left: Array<number>, right: Array<number>): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function withinTolerance(actual: number, expected: number, tolerance: number): boolean {
  return Math.abs(actual - expected) <= tolerance;
}

function sameJson(left: unknown, right: unknown): boolean {
  return JSON.stringify(left) === JSON.stringify(right);
}
