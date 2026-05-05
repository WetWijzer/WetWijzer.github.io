import {
  auditPythonMlSpacyExpectations,
  validateBrowserNativeLogicRuntime,
} from './browserNativeValidation';
import {
  ML_CONFIDENCE_FEATURE_NAMES,
  type MLConfidenceModelArtifact,
  loadMLConfidenceModelArtifact,
  unloadMLConfidenceModel,
} from './mlConfidence';

describe('browser-native end-to-end logic validation', () => {
  beforeEach(() => unloadMLConfidenceModel());
  afterEach(() => unloadMLConfidenceModel());

  it('proves FOL NLP, ML confidence, and deontic conversion avoid Python and server calls', () => {
    const report = validateBrowserNativeLogicRuntime({
      folText: 'All tenants are protected and some landlords must comply.',
      deonticText: 'The landlord must provide notice before entry.',
    });

    expect(report.valid).toBe(true);
    expect(report.failures).toEqual([]);
    expect(report.runtime).toMatchObject({
      mode: 'browser_native',
      serverCallsAllowed: false,
      mlConfidenceSource: 'heuristic',
      mlConfidenceModelLoaded: false,
    });
    expect(report.nlp).toMatchObject({
      provider: 'deterministic-token-classifier',
      backend: 'typescript-token-classifier',
      pythonSpacy: false,
      serverCallsAllowed: false,
    });
    expect(report.nlp.predicateCandidates).toEqual(['tenants', 'protected', 'landlords', 'comply']);
    expect(report.nlp.predicateCandidates).toEqual(report.nlp.repeatedPredicateCandidates);
    expect(report.ml).toMatchObject({
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      source: 'heuristic',
    });
    expect(report.ml.deterministicScore).toBe(report.ml.repeatedScore);
    expect(report.deontic).toMatchObject({
      success: true,
      browserNativeMlConfidence: true,
      serverCallsAllowed: false,
    });
  });

  it('keeps validation deterministic with a local ML artifact loaded', () => {
    const artifact: MLConfidenceModelArtifact = {
      format: 'deterministic-linear-v1',
      version: 'browser-native-e2e-fixture',
      featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice(),
      weights: ML_CONFIDENCE_FEATURE_NAMES.map((name) => (name === 'keyword_count' ? 0.15 : 0)),
      bias: 0.25,
      metadata: {
        sourcePythonModule: 'logic/ml_confidence.py',
        fixtureIds: ['browser-native-e2e-fixture'],
        expectedConfidence: 0.25,
        tolerance: 0.75,
        runtime: 'browser-native-typescript',
        serverCallsAllowed: false,
        pythonRuntimeAllowed: false,
      },
    };

    loadMLConfidenceModelArtifact(artifact);
    const report = validateBrowserNativeLogicRuntime();

    expect(report.valid).toBe(true);
    expect(report.runtime.mlConfidenceSource).toBe('artifact');
    expect(report.runtime.mlConfidenceModelLoaded).toBe(true);
    expect(report.ml.source).toBe('artifact');
    expect(report.ml.deterministicScore).toBe(report.ml.repeatedScore);
    expect(report.nlp.pythonSpacy).toBe(false);
    expect(report.deontic.serverCallsAllowed).toBe(false);
  });

  it('audits Python ML and spaCy expectations against browser-native behavior', () => {
    const audit = auditPythonMlSpacyExpectations();

    expect(audit).toMatchObject({
      valid: true,
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });
    expect(audit.checks.map((check) => [check.expectation, check.status])).toEqual([
      ['logic/ml_confidence.py FeatureExtractor vector', 'matched'],
      ['logic/ml_confidence.py fallback heuristic confidence', 'matched'],
      ['spaCy-style predicate extraction fixture', 'matched'],
      ['spaCy-style relation extraction fixture', 'matched'],
      ['trained Python XGBoost/LightGBM model weights', 'local_artifact_required'],
      ['full spaCy dependency parser and model weights', 'unsupported_fail_closed'],
    ]);
    expect(audit.localModelArtifactLoadingTasks).toEqual([
      'Export trained Python ML confidence weights into deterministic-linear-v1 or deterministic-logistic-v1 browser artifact metadata.',
      'Add a browser-native token-classification or dependency artifact if exact spaCy dependency labels become required.',
    ]);
    expect(audit.unsupported.every((check) => check.status !== 'matched')).toBe(true);
  });
});
