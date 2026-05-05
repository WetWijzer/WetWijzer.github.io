import {
  FeatureExtractor,
  ML_CONFIDENCE_FEATURE_NAMES,
  MLConfidenceCalibrationMetadata,
  MLConfidenceArtifactManifest,
  MLConfidenceModelArtifact,
  MLConfidenceScorer,
  getMLConfidenceArtifactCacheState,
  getMLConfidenceModelState,
  loadMLConfidenceModelFromCache,
  loadMLConfidenceModelArtifact,
  registerMLConfidenceArtifactManifest,
  predictMLConfidence,
  unloadMLConfidenceModel,
} from './mlConfidence';
import fixtures from './parity/python-parity-fixtures.json';

type MLConfidenceFixture = {
  id: string;
  kind: 'ml_confidence';
  sentence: string;
  fol_formula: string;
  predicates: {
    nouns?: string[];
    verbs?: string[];
    adjectives?: string[];
    relations?: string[];
  };
  quantifiers: string[];
  operators: string[];
  python_heuristic_confidence: number;
};

const mlFixture = (fixtures as Array<{ kind: string }>).find(
  (fixture) => fixture.kind === 'ml_confidence',
) as MLConfidenceFixture | undefined;

const calibrationMetadata = (fixture: MLConfidenceFixture): MLConfidenceCalibrationMetadata => ({
  sourcePythonModule: 'logic/ml_confidence.py',
  fixtureIds: [fixture.id],
  expectedConfidence: fixture.python_heuristic_confidence,
  tolerance: 1e-10,
  calibratedAt: '2026-05-05T00:00:00.000Z',
  runtime: 'browser-native-typescript',
  serverCallsAllowed: false,
  pythonRuntimeAllowed: false,
  notes: 'Deterministic parity capture from Python ml_confidence.py fallback scoring.',
});

describe('browser-native ML confidence parity slice', () => {
  beforeEach(() => {
    unloadMLConfidenceModel({ clearCache: true });
  });

  it('extracts the same 22 feature slots as the Python FeatureExtractor', () => {
    const features = FeatureExtractor.extractFeatures(
      'All tenants must pay rent, and some landlords may inspect.',
      '∀x (Tenant(x) → PayRent(x))',
      { nouns: ['Tenant'], verbs: ['PayRent', 'Inspect'], adjectives: [] },
      ['∀'],
      ['→', '∧'],
    );

    expect(features).toHaveLength(ML_CONFIDENCE_FEATURE_NAMES.length);
    expect(features[1]).toBe(10);
    expect(features[7]).toBe(3);
    expect(features[13]).toBe(1);
    expect(features[17]).toBe(1);
    expect(features[21]).toBeGreaterThanOrEqual(3);
  });

  it('scores logical conversions locally without server dependencies', () => {
    const high = predictMLConfidence(
      'If a tenant receives notice then the tenant must respond.',
      '∀x (Notice(x) → Respond(x))',
      { nouns: ['Tenant'], verbs: ['Respond'], adjectives: ['Notice'] },
      ['∀'],
      ['→'],
    );
    const low = predictMLConfidence('', 'P', {}, [], []);

    expect(high).toBeGreaterThan(low);
    expect(high).toBeGreaterThanOrEqual(0.7);
    expect(low).toBeLessThanOrEqual(0.3);
  });

  it('provides an in-browser training-compatible facade and importance map', () => {
    const scorer = new MLConfidenceScorer();
    const good = FeatureExtractor.extractFeatures(
      'All people are mortal.',
      '∀x (Person(x) → Mortal(x))',
      { nouns: ['Person'], adjectives: ['Mortal'] },
      ['∀'],
      ['→'],
    );
    const weak = FeatureExtractor.extractFeatures('hello', 'P', {}, [], []);
    const metrics = scorer.train([good, weak], [0.95, 0.1], 0.5);

    expect(metrics).toMatchObject({ n_train: 1, n_val: 1 });
    expect(scorer.isTrained).toBe(true);
    expect(scorer.getFeatureImportance()).toHaveProperty('sentence_length');
  });

  it('loads deterministic local model artifacts and unloads back to heuristic mode', () => {
    const artifact: MLConfidenceModelArtifact = {
      format: 'deterministic-logistic-v1',
      version: 'python-ml-confidence-parity-v1',
      featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice(),
      weights: ML_CONFIDENCE_FEATURE_NAMES.map((name) => (name === 'total_predicates' ? 1.6 : 0)),
      bias: -2,
      metadata: calibrationMetadata(mlFixture as MLConfidenceFixture),
    };

    const scorer = new MLConfidenceScorer();
    expect(scorer.loadModelArtifact(artifact)).toMatchObject({
      loaded: true,
      source: 'artifact',
      format: 'deterministic-logistic-v1',
      version: 'python-ml-confidence-parity-v1',
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });

    const confident = scorer.predictConfidence(
      'All tenants must pay rent.',
      '∀x (Tenant(x) → PayRent(x))',
      { nouns: ['Tenant'], verbs: ['PayRent'] },
      ['∀'],
      ['→'],
    );
    const weak = scorer.predictConfidence('hello', 'P', {}, [], []);

    expect(confident).toBeGreaterThan(weak);
    expect(scorer.unloadModel()).toMatchObject({ loaded: false, source: 'heuristic' });
  });

  it('validates local artifacts fail-closed without runtime fallbacks', () => {
    const scorer = new MLConfidenceScorer();
    const artifact: MLConfidenceModelArtifact = {
      format: 'deterministic-linear-v1',
      version: 'bad-order',
      featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice().reverse(),
      weights: ML_CONFIDENCE_FEATURE_NAMES.map(() => 0),
      bias: 0.5,
    };

    expect(() => scorer.loadModelArtifact(artifact)).toThrow(/feature order mismatch/);
    expect(scorer.modelState).toMatchObject({
      loaded: false,
      source: 'heuristic',
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });
  });

  it('exposes default artifact lifecycle helpers for browser callers', () => {
    expect(mlFixture).toBeDefined();
    const artifact: MLConfidenceModelArtifact = {
      format: 'deterministic-linear-v1',
      version: 'linear-fixture',
      featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice(),
      weights: ML_CONFIDENCE_FEATURE_NAMES.map((name) => (name === 'keyword_count' ? 0.2 : 0)),
      bias: 0.1,
      metadata: calibrationMetadata(mlFixture as MLConfidenceFixture),
    };

    expect(loadMLConfidenceModelArtifact(artifact)).toMatchObject({
      loaded: true,
      source: 'artifact',
      version: 'linear-fixture',
    });
    expect(getMLConfidenceModelState()).toMatchObject({ loaded: true, source: 'artifact' });
    expect(unloadMLConfidenceModel()).toMatchObject({ loaded: false, source: 'heuristic' });
  });

  it('scores fixture-backed calibrated artifacts with local browser metadata', () => {
    expect(mlFixture).toBeDefined();
    const fixture = mlFixture as MLConfidenceFixture;
    const artifact: MLConfidenceModelArtifact = {
      format: 'deterministic-linear-v1',
      version: 'python-ml-confidence-fixture-calibrated-v1',
      featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice(),
      weights: ML_CONFIDENCE_FEATURE_NAMES.map(() => 0),
      bias: fixture.python_heuristic_confidence,
      metadata: calibrationMetadata(fixture),
    };

    const scorer = new MLConfidenceScorer();
    scorer.loadModelArtifact(artifact);

    const result = scorer.scoreWithCalibration(
      fixture.sentence,
      fixture.fol_formula,
      fixture.predicates,
      fixture.quantifiers,
      fixture.operators,
    );

    expect(result.confidence).toBeCloseTo(fixture.python_heuristic_confidence, 10);
    expect(result.calibration).toMatchObject({
      expectedConfidence: fixture.python_heuristic_confidence,
      tolerance: 1e-10,
      withinTolerance: true,
      fixtureIds: [fixture.id],
    });
    expect(result.modelState.calibration).toMatchObject({
      runtime: 'browser-native-typescript',
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });
  });

  it('registers local artifact manifests, enforces versions, and clears cache on unload', () => {
    const manifest: MLConfidenceArtifactManifest = {
      manifestVersion: 'ml-confidence-artifacts-v1',
      runtimeVersion: 'browser-native-ml-confidence-v1',
      activeArtifactId: 'python-parity-linear',
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      artifacts: [
        {
          artifactId: 'python-parity-linear',
          format: 'deterministic-linear-v1',
          version: '2026-05-05.fixture-v1',
          featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice(),
          weights: ML_CONFIDENCE_FEATURE_NAMES.map((name) => (name === 'keyword_count' ? 0.05 : 0)),
          bias: 0.2,
        },
      ],
    };

    expect(registerMLConfidenceArtifactManifest(manifest)).toMatchObject({
      manifestVersion: 'ml-confidence-artifacts-v1',
      runtimeVersion: 'browser-native-ml-confidence-v1',
      cachedArtifactIds: ['python-parity-linear'],
      loadedArtifactId: 'python-parity-linear',
      loadedVersion: '2026-05-05.fixture-v1',
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });

    expect(
      loadMLConfidenceModelFromCache('python-parity-linear', '2026-05-05.fixture-v1'),
    ).toMatchObject({
      loaded: true,
      source: 'artifact',
      artifactId: 'python-parity-linear',
      version: '2026-05-05.fixture-v1',
    });
    expect(() => loadMLConfidenceModelFromCache('python-parity-linear', 'wrong-version')).toThrow(
      /version mismatch/,
    );

    unloadMLConfidenceModel({ clearCache: true });
    expect(getMLConfidenceArtifactCacheState()).toMatchObject({
      cachedArtifactIds: [],
      loadedArtifactId: undefined,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });
  });
});
