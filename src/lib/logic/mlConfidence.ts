export interface MLConfidenceConfig {
  modelPath?: string;
  useXgboost?: boolean;
  nEstimators?: number;
  maxDepth?: number;
  learningRate?: number;
  fallbackToHeuristic?: boolean;
}

export interface ConfidencePredicates {
  nouns?: string[];
  verbs?: string[];
  adjectives?: string[];
  relations?: string[];
}

export type ConfidenceTaskType = 'regression' | 'classification';

export interface ConfidenceTrainingMetrics {
  train_accuracy: number;
  val_accuracy: number;
  n_train: number;
  n_val: number;
}

export interface MLConfidenceModelArtifact {
  artifactId?: string;
  format:
    | 'deterministic-linear-v1'
    | 'deterministic-logistic-v1'
    | 'deterministic-python-heuristic-v1';
  version: string;
  featureNames: Array<MLConfidenceFeatureName>;
  weights: Array<number>;
  bias: number;
  threshold?: number;
  metadata?: MLConfidenceCalibrationMetadata;
}

export interface MLConfidenceCalibrationMetadata {
  sourcePythonModule: 'logic/ml_confidence.py';
  fixtureIds: Array<string>;
  expectedConfidence: number;
  tolerance: number;
  calibratedAt?: string;
  runtime: 'browser-native-typescript';
  serverCallsAllowed: false;
  pythonRuntimeAllowed: false;
  notes?: string;
}

export interface MLConfidenceArtifactManifestEntry extends MLConfidenceModelArtifact {
  artifactId: string;
}

export interface MLConfidenceArtifactManifest {
  manifestVersion: 'ml-confidence-artifacts-v1';
  runtimeVersion: 'browser-native-ml-confidence-v1';
  activeArtifactId?: string;
  artifacts: Array<MLConfidenceArtifactManifestEntry>;
  serverCallsAllowed: false;
  pythonRuntimeAllowed: false;
}

export interface MLConfidenceModelState {
  loaded: boolean;
  source: 'heuristic' | 'trained' | 'artifact';
  artifactId?: string;
  format?: MLConfidenceModelArtifact['format'];
  version?: string;
  featureCount: number;
  serverCallsAllowed: false;
  pythonRuntimeAllowed: false;
  calibration?: MLConfidenceCalibrationMetadata;
}

export interface MLConfidenceScoreResult {
  confidence: number;
  modelState: MLConfidenceModelState;
  calibration?: {
    expectedConfidence: number;
    tolerance: number;
    delta: number;
    withinTolerance: boolean;
    fixtureIds: Array<string>;
  };
}

export interface MLConfidenceArtifactCacheState {
  manifestVersion?: MLConfidenceArtifactManifest['manifestVersion'];
  runtimeVersion: 'browser-native-ml-confidence-v1';
  cachedArtifactIds: Array<string>;
  loadedArtifactId?: string;
  loadedVersion?: string;
  serverCallsAllowed: false;
  pythonRuntimeAllowed: false;
}

export const ML_CONFIDENCE_FEATURE_NAMES = [
  'sentence_length',
  'word_count',
  'comma_count',
  'period_count',
  'formula_length',
  'parenthesis_depth',
  'quantifier_count_formula',
  'total_predicates',
  'noun_predicates',
  'verb_predicates',
  'adj_predicates',
  'quantifier_count',
  'operator_count',
  'universal_quantifiers',
  'existential_quantifiers',
  'and_operators',
  'or_operators',
  'implies_operators',
  'not_operators',
  'formula_sentence_ratio',
  'predicates_per_word',
  'keyword_count',
] as const;

export type MLConfidenceFeatureName = (typeof ML_CONFIDENCE_FEATURE_NAMES)[number];
export type MLConfidenceFeatureVector = number[];

export class FeatureExtractor {
  static extractFeatures(
    sentence: string,
    folFormula: string,
    predicates: ConfidencePredicates,
    quantifiers: string[],
    operators: string[],
  ): MLConfidenceFeatureVector {
    const words = sentence.trim().split(/\s+/).filter(Boolean);
    const totalPredicates = countPredicates(predicates);
    const lower = sentence.toLowerCase();
    const keywords = ['all', 'some', 'if', 'then', 'and', 'or', 'not', 'every', 'each'];

    return [
      sentence.length,
      words.length,
      countOccurrences(sentence, ','),
      countOccurrences(sentence, '.'),
      folFormula.length,
      countOccurrences(folFormula, '('),
      countOccurrences(folFormula, '∀') + countOccurrences(folFormula, '∃'),
      totalPredicates,
      predicates.nouns?.length ?? 0,
      predicates.verbs?.length ?? 0,
      predicates.adjectives?.length ?? 0,
      quantifiers.length,
      operators.length,
      quantifiers.filter((value) => value === '∀').length,
      quantifiers.filter((value) => value === '∃').length,
      operators.filter((value) => value === '∧').length,
      operators.filter((value) => value === '∨').length,
      operators.filter((value) => value === '→').length,
      operators.filter((value) => value === '¬').length,
      folFormula.length / Math.max(sentence.length, 1),
      totalPredicates / Math.max(words.length, 1),
      keywords.reduce((total, keyword) => total + countKeyword(lower, keyword), 0),
    ];
  }
}

export class MLConfidenceScorer {
  readonly config: Required<Omit<MLConfidenceConfig, 'modelPath'>> &
    Pick<MLConfidenceConfig, 'modelPath'>;
  readonly featureExtractor = FeatureExtractor;
  private trainedWeights?: number[];
  private trainedBias = 0;
  private artifact?: MLConfidenceModelArtifact;

  constructor(config: MLConfidenceConfig = {}) {
    this.config = {
      modelPath: config.modelPath,
      useXgboost: config.useXgboost ?? true,
      nEstimators: config.nEstimators ?? 100,
      maxDepth: config.maxDepth ?? 6,
      learningRate: config.learningRate ?? 0.1,
      fallbackToHeuristic: config.fallbackToHeuristic ?? true,
    };
  }

  get isTrained(): boolean {
    return Boolean(this.trainedWeights) || Boolean(this.artifact);
  }

  get modelState(): MLConfidenceModelState {
    if (this.artifact) {
      return {
        loaded: true,
        source: 'artifact',
        artifactId: this.artifact.artifactId,
        format: this.artifact.format,
        version: this.artifact.version,
        featureCount: this.artifact.weights.length,
        serverCallsAllowed: false,
        pythonRuntimeAllowed: false,
        calibration: this.artifact.metadata,
      };
    }
    return {
      loaded: Boolean(this.trainedWeights),
      source: this.trainedWeights ? 'trained' : 'heuristic',
      featureCount: this.trainedWeights?.length ?? ML_CONFIDENCE_FEATURE_NAMES.length,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    };
  }

  extractFeatures(
    sentence: string,
    folFormula: string,
    predicates: ConfidencePredicates,
    quantifiers: string[],
    operators: string[],
  ): MLConfidenceFeatureVector {
    return FeatureExtractor.extractFeatures(
      sentence,
      folFormula,
      predicates,
      quantifiers,
      operators,
    );
  }

  predictConfidence(
    sentence: string,
    folFormula: string,
    predicates: ConfidencePredicates,
    quantifiers: string[],
    operators: string[],
  ): number {
    const features = this.extractFeatures(sentence, folFormula, predicates, quantifiers, operators);
    if (this.artifact) {
      return scoreFeatureVector(
        features,
        this.artifact.weights,
        this.artifact.bias,
        this.artifact.format,
      );
    }
    if (!this.trainedWeights) {
      if (this.config.fallbackToHeuristic) {
        return this.heuristicConfidence(sentence, folFormula, predicates, quantifiers, operators);
      }
      return 0.5;
    }

    const raw = features.reduce(
      (total, feature, index) => total + feature * (this.trainedWeights?.[index] ?? 0),
      this.trainedBias,
    );
    return clamp01(1 / (1 + Math.exp(-raw)));
  }

  scoreWithCalibration(
    sentence: string,
    folFormula: string,
    predicates: ConfidencePredicates,
    quantifiers: string[],
    operators: string[],
  ): MLConfidenceScoreResult {
    const confidence = this.predictConfidence(
      sentence,
      folFormula,
      predicates,
      quantifiers,
      operators,
    );
    const metadata = this.artifact?.metadata;
    if (!metadata) {
      return { confidence, modelState: this.modelState };
    }
    const delta = Math.abs(confidence - metadata.expectedConfidence);
    return {
      confidence,
      modelState: this.modelState,
      calibration: {
        expectedConfidence: metadata.expectedConfidence,
        tolerance: metadata.tolerance,
        delta,
        withinTolerance: delta <= metadata.tolerance,
        fixtureIds: metadata.fixtureIds.slice(),
      },
    };
  }

  loadModelArtifact(artifact: MLConfidenceModelArtifact): MLConfidenceModelState {
    const normalized = validateModelArtifact(artifact);
    this.artifact = normalized;
    this.trainedWeights = normalized.weights.slice();
    this.trainedBias = normalized.bias;
    return this.modelState;
  }

  unloadModel(): MLConfidenceModelState {
    this.artifact = undefined;
    this.trainedWeights = undefined;
    this.trainedBias = 0;
    return this.modelState;
  }

  heuristicConfidence(
    sentence: string,
    folFormula: string,
    predicates: ConfidencePredicates,
    quantifiers: string[],
    operators: string[],
  ): number {
    let score = 0;
    const totalPredicates = countPredicates(predicates);

    if (totalPredicates > 0) score += 0.3;
    if (quantifiers.length > 0) score += 0.2;
    if (operators.length > 0) score += 0.2;

    const lower = sentence.toLowerCase();
    const keywordCount = ['all', 'some', 'if', 'then', 'and', 'or', 'not'].reduce(
      (total, keyword) => total + countKeyword(lower, keyword),
      0,
    );
    score += Math.min(0.2, keywordCount * 0.05);

    if (folFormula.length < 5) score -= 0.2;
    if (folFormula.length > 200) score -= 0.1;

    return clamp01(score);
  }

  train(
    matrix: number[][],
    labels: number[],
    validationSplit = 0.2,
    taskType: ConfidenceTaskType = 'regression',
  ): ConfidenceTrainingMetrics {
    if (taskType !== 'regression' && taskType !== 'classification') {
      throw new Error(`taskType must be 'regression' or 'classification', got ${taskType}`);
    }
    if (matrix.length !== labels.length || matrix.length === 0) {
      throw new Error('Training data must include one label for each feature vector');
    }

    const splitIndex = Math.max(
      1,
      Math.min(matrix.length - 1, Math.floor(matrix.length * (1 - validationSplit))),
    );
    const trainX = matrix.slice(0, splitIndex);
    const trainY = labels.slice(0, splitIndex).map(clamp01);
    const valX = matrix.slice(splitIndex);
    const valY = labels.slice(splitIndex).map(clamp01);

    const featureCount = matrix[0]?.length ?? ML_CONFIDENCE_FEATURE_NAMES.length;
    const means = Array.from({ length: featureCount }, (_, index) =>
      mean(trainX.map((row) => row[index] ?? 0)),
    );
    const yMean = mean(trainY);
    const weights = means.map((featureMean, index) => {
      const covariance = mean(
        trainX.map(
          (row, rowIndex) => ((row[index] ?? 0) - featureMean) * (trainY[rowIndex] - yMean),
        ),
      );
      const variance = mean(trainX.map((row) => Math.pow((row[index] ?? 0) - featureMean, 2))) || 1;
      return covariance / variance;
    });

    this.artifact = undefined;
    this.trainedWeights = weights;
    this.trainedBias =
      logit(yMean) - weights.reduce((total, weight, index) => total + weight * means[index], 0);

    return {
      train_accuracy: scorePredictions(trainX, trainY, weights, this.trainedBias, taskType),
      val_accuracy:
        valX.length > 0 ? scorePredictions(valX, valY, weights, this.trainedBias, taskType) : 0,
      n_train: trainX.length,
      n_val: valX.length,
    };
  }

  getFeatureImportance(): Record<MLConfidenceFeatureName, number> | null {
    const weights = this.artifact?.weights ?? this.trainedWeights;
    if (!weights) {
      return null;
    }
    const total = weights.reduce((sum, value) => sum + Math.abs(value), 0) || 1;
    return Object.fromEntries(
      ML_CONFIDENCE_FEATURE_NAMES.map((name, index) => [
        name,
        Math.abs(weights[index] ?? 0) / total,
      ]),
    ) as Record<MLConfidenceFeatureName, number>;
  }
}

export const defaultMLConfidenceScorer = new MLConfidenceScorer();
const ML_CONFIDENCE_RUNTIME_VERSION = 'browser-native-ml-confidence-v1' as const;
let cachedManifestVersion: MLConfidenceArtifactManifest['manifestVersion'] | undefined;
const mlConfidenceArtifactCache = new Map<string, MLConfidenceModelArtifact>();

export function extractMLConfidenceFeatures(
  sentence: string,
  folFormula: string,
  predicates: ConfidencePredicates,
  quantifiers: string[],
  operators: string[],
): MLConfidenceFeatureVector {
  return FeatureExtractor.extractFeatures(sentence, folFormula, predicates, quantifiers, operators);
}

export function predictMLConfidence(
  sentence: string,
  folFormula: string,
  predicates: ConfidencePredicates,
  quantifiers: string[],
  operators: string[],
): number {
  return defaultMLConfidenceScorer.predictConfidence(
    sentence,
    folFormula,
    predicates,
    quantifiers,
    operators,
  );
}

export const extract_ml_confidence_features = extractMLConfidenceFeatures;
export const predict_ml_confidence = predictMLConfidence;

export function createMLConfidencePythonHeuristicArtifact(
  options: {
    artifactId?: string;
    version?: string;
    metadata?: MLConfidenceCalibrationMetadata;
  } = {},
): MLConfidenceModelArtifact {
  return {
    artifactId: options.artifactId,
    format: 'deterministic-python-heuristic-v1',
    version: options.version ?? 'python-ml-confidence-heuristic-v1',
    featureNames: ML_CONFIDENCE_FEATURE_NAMES.slice(),
    weights: ML_CONFIDENCE_FEATURE_NAMES.map(() => 0),
    bias: 0,
    metadata: options.metadata,
  };
}

export function loadMLConfidenceModelArtifact(
  artifact: MLConfidenceModelArtifact,
): MLConfidenceModelState {
  return defaultMLConfidenceScorer.loadModelArtifact(artifact);
}

export function registerMLConfidenceArtifactManifest(
  manifest: MLConfidenceArtifactManifest,
): MLConfidenceArtifactCacheState {
  validateArtifactManifest(manifest);
  cachedManifestVersion = manifest.manifestVersion;
  for (const artifact of manifest.artifacts) {
    mlConfidenceArtifactCache.set(artifact.artifactId, validateModelArtifact(artifact));
  }
  if (manifest.activeArtifactId) {
    loadMLConfidenceModelFromCache(manifest.activeArtifactId);
  }
  return getMLConfidenceArtifactCacheState();
}

export function loadMLConfidenceModelFromCache(
  artifactId: string,
  expectedVersion?: string,
): MLConfidenceModelState {
  const artifact = mlConfidenceArtifactCache.get(artifactId);
  if (!artifact) {
    throw new Error(`ML confidence artifact is not cached: ${artifactId}`);
  }
  if (expectedVersion !== undefined && artifact.version !== expectedVersion) {
    throw new Error(
      `ML confidence artifact version mismatch for ${artifactId}: expected ${expectedVersion}, got ${artifact.version}`,
    );
  }
  return loadMLConfidenceModelArtifact(artifact);
}

export function getMLConfidenceArtifactCacheState(): MLConfidenceArtifactCacheState {
  const modelState = getMLConfidenceModelState();
  return {
    manifestVersion: cachedManifestVersion,
    runtimeVersion: ML_CONFIDENCE_RUNTIME_VERSION,
    cachedArtifactIds: Array.from(mlConfidenceArtifactCache.keys()).sort(),
    loadedArtifactId: modelState.artifactId,
    loadedVersion: modelState.version,
    serverCallsAllowed: false,
    pythonRuntimeAllowed: false,
  };
}

export function clearMLConfidenceArtifactCache(): MLConfidenceArtifactCacheState {
  mlConfidenceArtifactCache.clear();
  cachedManifestVersion = undefined;
  return getMLConfidenceArtifactCacheState();
}

export function unloadMLConfidenceModel(
  options: { clearCache?: boolean } = {},
): MLConfidenceModelState {
  if (options.clearCache) {
    clearMLConfidenceArtifactCache();
  }
  return defaultMLConfidenceScorer.unloadModel();
}

export function getMLConfidenceModelState(): MLConfidenceModelState {
  return defaultMLConfidenceScorer.modelState;
}

function countOccurrences(text: string, value: string): number {
  return text.split(value).length - 1;
}

function countPredicates(predicates: ConfidencePredicates): number {
  return ['nouns', 'verbs', 'adjectives', 'relations'].reduce(
    (total, key) => total + (predicates[key as keyof ConfidencePredicates]?.length ?? 0),
    0,
  );
}

function countKeyword(lowerText: string, keyword: string): number {
  return lowerText.match(new RegExp(`\\b${escapeRegExp(keyword)}\\b`, 'g'))?.length ?? 0;
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function validateModelArtifact(artifact: MLConfidenceModelArtifact): MLConfidenceModelArtifact {
  if (artifact.artifactId !== undefined && !artifact.artifactId.trim()) {
    throw new Error('ML confidence artifactId must be non-empty when provided');
  }
  if (
    artifact.format !== 'deterministic-linear-v1' &&
    artifact.format !== 'deterministic-logistic-v1' &&
    artifact.format !== 'deterministic-python-heuristic-v1'
  ) {
    throw new Error(`Unsupported ML confidence artifact format: ${artifact.format}`);
  }
  if (!artifact.version.trim()) {
    throw new Error('ML confidence artifact version is required');
  }
  if (artifact.featureNames.length !== ML_CONFIDENCE_FEATURE_NAMES.length) {
    throw new Error('ML confidence artifact featureNames length mismatch');
  }
  if (artifact.weights.length !== ML_CONFIDENCE_FEATURE_NAMES.length) {
    throw new Error('ML confidence artifact weights length mismatch');
  }
  for (let index = 0; index < ML_CONFIDENCE_FEATURE_NAMES.length; index += 1) {
    if (artifact.featureNames[index] !== ML_CONFIDENCE_FEATURE_NAMES[index]) {
      throw new Error(`ML confidence artifact feature order mismatch at ${index}`);
    }
    if (!Number.isFinite(artifact.weights[index])) {
      throw new Error(`ML confidence artifact weight ${index} must be finite`);
    }
  }
  if (!Number.isFinite(artifact.bias)) {
    throw new Error('ML confidence artifact bias must be finite');
  }
  const metadata = artifact.metadata ? validateCalibrationMetadata(artifact.metadata) : undefined;
  return {
    ...artifact,
    artifactId: artifact.artifactId,
    featureNames: artifact.featureNames.slice(),
    weights: artifact.weights.slice(),
    metadata,
  };
}

function validateArtifactManifest(manifest: MLConfidenceArtifactManifest): void {
  if (manifest.manifestVersion !== 'ml-confidence-artifacts-v1') {
    throw new Error(`Unsupported ML confidence manifest version: ${manifest.manifestVersion}`);
  }
  if (manifest.runtimeVersion !== ML_CONFIDENCE_RUNTIME_VERSION) {
    throw new Error(`Unsupported ML confidence runtime version: ${manifest.runtimeVersion}`);
  }
  if (manifest.serverCallsAllowed !== false || manifest.pythonRuntimeAllowed !== false) {
    throw new Error(
      'ML confidence artifact manifest must disallow server and Python runtime calls',
    );
  }
  if (manifest.artifacts.length === 0) {
    throw new Error('ML confidence artifact manifest requires at least one artifact');
  }
  const ids = new Set<string>();
  for (const artifact of manifest.artifacts) {
    if (!artifact.artifactId.trim()) {
      throw new Error('ML confidence manifest artifactId must be non-empty');
    }
    if (ids.has(artifact.artifactId)) {
      throw new Error(`Duplicate ML confidence artifactId: ${artifact.artifactId}`);
    }
    ids.add(artifact.artifactId);
    validateModelArtifact(artifact);
  }
  if (manifest.activeArtifactId !== undefined && !ids.has(manifest.activeArtifactId)) {
    throw new Error(
      `Active ML confidence artifact is not in manifest: ${manifest.activeArtifactId}`,
    );
  }
}

function validateCalibrationMetadata(
  metadata: MLConfidenceCalibrationMetadata,
): MLConfidenceCalibrationMetadata {
  if (metadata.sourcePythonModule !== 'logic/ml_confidence.py') {
    throw new Error('ML confidence calibration must cite logic/ml_confidence.py');
  }
  if (metadata.runtime !== 'browser-native-typescript') {
    throw new Error('ML confidence calibration runtime must be browser-native-typescript');
  }
  if (metadata.serverCallsAllowed !== false || metadata.pythonRuntimeAllowed !== false) {
    throw new Error('ML confidence calibration must disallow server and Python runtime calls');
  }
  if (metadata.fixtureIds.length === 0 || metadata.fixtureIds.some((id) => !id.trim())) {
    throw new Error('ML confidence calibration requires at least one fixture id');
  }
  if (!Number.isFinite(metadata.expectedConfidence)) {
    throw new Error('ML confidence calibration expectedConfidence must be finite');
  }
  if (!Number.isFinite(metadata.tolerance) || metadata.tolerance < 0) {
    throw new Error('ML confidence calibration tolerance must be a non-negative finite number');
  }
  return {
    ...metadata,
    fixtureIds: metadata.fixtureIds.slice(),
  };
}

function scoreFeatureVector(
  features: MLConfidenceFeatureVector,
  weights: Array<number>,
  bias: number,
  format: MLConfidenceModelArtifact['format'],
): number {
  if (format === 'deterministic-python-heuristic-v1') {
    return scorePythonHeuristicFeatureVector(features);
  }
  const raw = features.reduce(
    (total, feature, index) => total + feature * (weights[index] ?? 0),
    bias,
  );
  if (format === 'deterministic-linear-v1') {
    return clamp01(raw);
  }
  return clamp01(1 / (1 + Math.exp(-raw)));
}

function scorePythonHeuristicFeatureVector(features: MLConfidenceFeatureVector): number {
  let score = 0;
  const formulaLength = features[4] ?? 0;
  const totalPredicates = features[7] ?? 0;
  const quantifierCount = features[11] ?? 0;
  const operatorCount = features[12] ?? 0;
  const keywordCount = features[21] ?? 0;

  if (totalPredicates > 0) score += 0.3;
  if (quantifierCount > 0) score += 0.2;
  if (operatorCount > 0) score += 0.2;
  score += Math.min(0.2, keywordCount * 0.05);
  if (formulaLength < 5) score -= 0.2;
  if (formulaLength > 200) score -= 0.1;

  return clamp01(score);
}

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, Number.isFinite(value) ? value : 0.5));
}

function mean(values: number[]): number {
  return values.length > 0 ? values.reduce((total, value) => total + value, 0) / values.length : 0;
}

function logit(value: number): number {
  const clamped = Math.min(0.999, Math.max(0.001, value));
  return Math.log(clamped / (1 - clamped));
}

function scorePredictions(
  matrix: number[][],
  labels: number[],
  weights: number[],
  bias: number,
  taskType: ConfidenceTaskType,
): number {
  const predictions = matrix.map((row) =>
    clamp01(
      1 /
        (1 +
          Math.exp(
            -row.reduce((total, value, index) => total + value * (weights[index] ?? 0), bias),
          )),
    ),
  );
  if (taskType === 'classification') {
    return mean(
      predictions.map((prediction, index) =>
        Number(prediction >= 0.5) === Number(labels[index] >= 0.5) ? 1 : 0,
      ),
    );
  }
  const yMean = mean(labels);
  const variance = mean(labels.map((label) => Math.pow(label - yMean, 2))) || 1;
  const mse = mean(predictions.map((prediction, index) => Math.pow(prediction - labels[index], 2)));
  return 1 - mse / variance;
}
