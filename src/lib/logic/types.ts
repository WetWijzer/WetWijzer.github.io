export type ConfidenceScore = number;
export type ComplexityScore = number;

export type CommonLogicOperator = 'AND' | 'OR' | 'NOT' | 'IMPLIES' | 'IFF' | 'EXISTS' | 'FORALL';
export type LogicOperator = CommonLogicOperator | 'XOR';
export type Quantifier = 'FORALL' | 'EXISTS' | 'UNIVERSAL' | 'EXISTENTIAL';
export type FormulaType =
  | 'first_order_logic'
  | 'modal_logic'
  | 'temporal_logic'
  | 'deontic_logic'
  | 'mixed_logic'
  | 'arithmetic'
  | 'quantified'
  | 'propositional';

export const COMMON_TYPES_PORT_METADATA = {
  sourcePythonModule: 'logic/types/common_types.py',
  browserNative: true,
  serverCallsAllowed: false,
  pythonRuntimeAllowed: false,
  runtimeDependencies: [],
} as const;

export const LOGIC_OPERATOR_SYMBOLS: Record<LogicOperator, string> = {
  AND: '∧',
  OR: '∨',
  NOT: '¬',
  IMPLIES: '→',
  IFF: '↔',
  EXISTS: '∃',
  FORALL: '∀',
  XOR: '⊕',
};

export const QUANTIFIER_SYMBOLS: Record<Quantifier, string> = {
  FORALL: '∀',
  EXISTS: '∃',
  UNIVERSAL: '∀',
  EXISTENTIAL: '∃',
};

export const FORMULA_TYPE_VALUES = {
  FOL: 'first_order_logic',
  MODAL: 'modal_logic',
  TEMPORAL: 'temporal_logic',
  DEONTIC: 'deontic_logic',
  MIXED: 'mixed_logic',
  ARITHMETIC: 'arithmetic',
  QUANTIFIED: 'quantified',
  PROPOSITIONAL: 'propositional',
} as const satisfies Record<string, FormulaType>;

export interface ComplexityMetrics {
  quantifierDepth: number;
  nestingLevel: number;
  operatorCount: number;
  variableCount: number;
  predicateCount: number;
  complexityScore: ComplexityScore;
}

export interface PythonComplexityMetrics {
  quantifier_depth: number;
  nesting_level: number;
  operator_count: number;
  variable_count: number;
  predicate_count: number;
  complexity_score: ComplexityScore;
}

export const EMPTY_COMPLEXITY_METRICS: ComplexityMetrics = {
  quantifierDepth: 0,
  nestingLevel: 0,
  operatorCount: 0,
  variableCount: 0,
  predicateCount: 0,
  complexityScore: 0,
};

export function createComplexityMetrics(input: Partial<ComplexityMetrics> = {}): ComplexityMetrics {
  return {
    quantifierDepth: input.quantifierDepth ?? 0,
    nestingLevel: input.nestingLevel ?? 0,
    operatorCount: input.operatorCount ?? 0,
    variableCount: input.variableCount ?? 0,
    predicateCount: input.predicateCount ?? 0,
    complexityScore: input.complexityScore ?? 0,
  };
}

export function complexityMetricsToDict(metrics: ComplexityMetrics): PythonComplexityMetrics {
  return {
    quantifier_depth: metrics.quantifierDepth,
    nesting_level: metrics.nestingLevel,
    operator_count: metrics.operatorCount,
    variable_count: metrics.variableCount,
    predicate_count: metrics.predicateCount,
    complexity_score: Math.trunc(metrics.complexityScore),
  };
}

export interface FormulaLike {
  toString(): string;
  getComplexity?(): ComplexityMetrics;
}

export interface PythonFormulaProtocol {
  to_string(): string;
  get_complexity(): ComplexityMetrics;
}

export interface FormulaProtocol {
  toString(): string;
  getComplexity(): ComplexityMetrics;
}

export interface ProverProtocol {
  prove(formula: string, timeout?: number): ProofResult;
  getName(): string;
}

export interface PythonProverProtocol {
  prove(formula: string, timeout?: number): ProofResult;
  get_name(): string;
}

export interface ConverterProtocol {
  convert(formula: string, sourceFormat: string, targetFormat: string): string;
}

export interface PythonConverterProtocol {
  convert(formula: string, source_format: string, target_format: string): string;
}

export function isCommonLogicOperator(value: unknown): value is CommonLogicOperator {
  return (
    typeof value === 'string' &&
    ['AND', 'OR', 'NOT', 'IMPLIES', 'IFF', 'EXISTS', 'FORALL'].includes(value)
  );
}

export function isQuantifier(value: unknown): value is Quantifier {
  return (
    typeof value === 'string' && ['FORALL', 'EXISTS', 'UNIVERSAL', 'EXISTENTIAL'].includes(value)
  );
}

export function isFormulaType(value: unknown): value is FormulaType {
  return (
    typeof value === 'string' && Object.values(FORMULA_TYPE_VALUES).includes(value as FormulaType)
  );
}

export function getLogicOperatorSymbol(operator: LogicOperator): string {
  return LOGIC_OPERATOR_SYMBOLS[operator];
}

export function getQuantifierSymbol(quantifier: Quantifier): string {
  return QUANTIFIER_SYMBOLS[quantifier];
}

export function formulaProtocolToString(formula: FormulaProtocol | PythonFormulaProtocol): string {
  if ('to_string' in formula) return formula.to_string();
  return formula.toString();
}

export function formulaProtocolComplexity(
  formula: FormulaProtocol | PythonFormulaProtocol,
): ComplexityMetrics {
  if ('get_complexity' in formula) return formula.get_complexity();
  return formula.getComplexity();
}

export type ProofStatus = 'proved' | 'disproved' | 'unknown' | 'timeout' | 'error';

export interface ProofStep {
  id: string;
  rule: string;
  premises: string[];
  conclusion: string;
  explanation?: string;
}

export interface ProofResult {
  status: ProofStatus;
  theorem: string;
  steps: ProofStep[];
  method?: string;
  timeMs?: number;
  error?: string;
}

export interface LogicValidationIssue {
  severity: 'error' | 'warning';
  field?: string;
  message: string;
}

export interface LogicValidationResult {
  valid: boolean;
  issues: LogicValidationIssue[];
}

export interface ParsePosition {
  offset: number;
  line: number;
  column: number;
}

export type BridgeCapability =
  | 'bidirectional'
  | 'incremental'
  | 'rule_extraction'
  | 'optimization'
  | 'parallel';
export type BridgeConversionStatus = 'success' | 'partial' | 'failed' | 'unsupported';

export const BRIDGE_TYPES_PORT_METADATA = {
  sourcePythonModule: 'logic/types/bridge_types.py',
  browserNative: true,
  serverCallsAllowed: false,
  pythonRuntimeAllowed: false,
  runtimeDependencies: [],
} as const;

export const BRIDGE_CAPABILITIES = {
  BIDIRECTIONAL_CONVERSION: 'bidirectional',
  INCREMENTAL_PROVING: 'incremental',
  RULE_EXTRACTION: 'rule_extraction',
  OPTIMIZATION: 'optimization',
  PARALLEL_PROVING: 'parallel',
} as const satisfies Record<string, BridgeCapability>;

export const BRIDGE_CONVERSION_STATUSES = {
  SUCCESS: 'success',
  PARTIAL: 'partial',
  FAILED: 'failed',
  UNSUPPORTED: 'unsupported',
} as const satisfies Record<string, BridgeConversionStatus>;

export class BridgeMetadata {
  constructor(
    readonly name: string,
    readonly version: string,
    readonly targetSystem: string,
    readonly capabilities: BridgeCapability[],
    readonly requiresExternalProver: boolean,
    readonly description: string,
  ) {}

  supportsCapability(capability: BridgeCapability): boolean {
    return this.capabilities.includes(capability);
  }

  toDict(): Record<string, unknown> {
    return {
      name: this.name,
      version: this.version,
      target_system: this.targetSystem,
      capabilities: [...this.capabilities],
      requires_external_prover: this.requiresExternalProver,
      description: this.description,
    };
  }
}

export function isBridgeCapability(value: unknown): value is BridgeCapability {
  return (
    typeof value === 'string' &&
    Object.values(BRIDGE_CAPABILITIES).includes(value as BridgeCapability)
  );
}

export function isBridgeConversionStatus(value: unknown): value is BridgeConversionStatus {
  return (
    typeof value === 'string' &&
    Object.values(BRIDGE_CONVERSION_STATUSES).includes(value as BridgeConversionStatus)
  );
}

export function bridgeMetadataFromDict(value: Record<string, unknown>): BridgeMetadata {
  const capabilities = Array.isArray(value.capabilities)
    ? value.capabilities.filter(isBridgeCapability)
    : [];
  return new BridgeMetadata(
    stringField(value, 'name'),
    stringField(value, 'version'),
    stringField(value, 'target_system', stringField(value, 'targetSystem')),
    capabilities,
    booleanField(value, 'requires_external_prover', booleanField(value, 'requiresExternalProver')),
    stringField(value, 'description'),
  );
}

export class LogicBridgeConversionResult {
  constructor(
    readonly status: BridgeConversionStatus,
    readonly sourceFormula: string,
    readonly targetFormula: string,
    readonly sourceFormat: string,
    readonly targetFormat: string,
    readonly confidence = 1.0,
    readonly warnings: string[] = [],
    readonly metadata: Record<string, unknown> = {},
  ) {}

  isSuccessful(): boolean {
    return this.status === 'success';
  }

  hasWarnings(): boolean {
    return this.warnings.length > 0;
  }

  toDict(): Record<string, unknown> {
    return {
      status: this.status,
      source_formula: this.sourceFormula,
      target_formula: this.targetFormula,
      source_format: this.sourceFormat,
      target_format: this.targetFormat,
      confidence: this.confidence,
      warnings: [...this.warnings],
      metadata: { ...this.metadata },
    };
  }
}

export function bridgeConversionResultFromDict(
  value: Record<string, unknown>,
): LogicBridgeConversionResult {
  const status = isBridgeConversionStatus(value.status) ? value.status : 'failed';
  const warnings = Array.isArray(value.warnings)
    ? value.warnings.filter((item) => typeof item === 'string')
    : [];
  return new LogicBridgeConversionResult(
    status,
    stringField(value, 'source_formula', stringField(value, 'sourceFormula')),
    stringField(value, 'target_formula', stringField(value, 'targetFormula')),
    stringField(value, 'source_format', stringField(value, 'sourceFormat')),
    stringField(value, 'target_format', stringField(value, 'targetFormat')),
    numberField(value, 'confidence', status === 'success' ? 1 : 0),
    warnings,
    recordField(value, 'metadata'),
  );
}

export class BridgeConfig {
  constructor(
    readonly name: string,
    readonly targetSystem: string,
    readonly timeout = 30,
    readonly maxRetries = 3,
    readonly enableCaching = true,
    readonly cacheTtl = 3600,
    readonly customSettings: Record<string, unknown> = {},
  ) {}

  getSetting<T = unknown>(key: string, defaultValue?: T): T | undefined {
    return (key in this.customSettings ? this.customSettings[key] : defaultValue) as T | undefined;
  }

  toDict(): Record<string, unknown> {
    return {
      name: this.name,
      target_system: this.targetSystem,
      timeout: this.timeout,
      max_retries: this.maxRetries,
      enable_caching: this.enableCaching,
      cache_ttl: this.cacheTtl,
      custom_settings: { ...this.customSettings },
    };
  }
}

export function bridgeConfigFromDict(value: Record<string, unknown>): BridgeConfig {
  return new BridgeConfig(
    stringField(value, 'name'),
    stringField(value, 'target_system', stringField(value, 'targetSystem')),
    numberField(value, 'timeout', 30),
    numberField(value, 'max_retries', numberField(value, 'maxRetries', 3)),
    booleanField(value, 'enable_caching', booleanField(value, 'enableCaching', true)),
    numberField(value, 'cache_ttl', numberField(value, 'cacheTtl', 3600)),
    recordField(value, 'custom_settings', recordField(value, 'customSettings')),
  );
}

export class ProverRecommendation {
  constructor(
    readonly proverName: string,
    readonly confidence: number,
    readonly reasons: string[],
    readonly estimatedTime?: number,
  ) {}

  compare(other: ProverRecommendation): number {
    return other.confidence - this.confidence;
  }

  toDict(): Record<string, unknown> {
    return {
      prover_name: this.proverName,
      confidence: this.confidence,
      reasons: [...this.reasons],
      estimated_time: this.estimatedTime,
    };
  }
}

export function proverRecommendationFromDict(value: Record<string, unknown>): ProverRecommendation {
  const reasons = Array.isArray(value.reasons)
    ? value.reasons.filter((item) => typeof item === 'string')
    : [];
  return new ProverRecommendation(
    stringField(value, 'prover_name', stringField(value, 'proverName')),
    numberField(value, 'confidence', 0),
    reasons,
    optionalNumberField(value, 'estimated_time', optionalNumberField(value, 'estimatedTime')),
  );
}

export function validateBridgeTypesPort(value: unknown) {
  const issues: Array<LogicValidationIssue> = [];
  if (!isRecord(value)) {
    issues.push({ severity: 'error', message: 'expected_object' });
    return { valid: false, issues, metadata: BRIDGE_TYPES_PORT_METADATA };
  }

  if ('capabilities' in value) {
    const capabilities = value.capabilities;
    if (!Array.isArray(capabilities) || capabilities.some((item) => !isBridgeCapability(item))) {
      issues.push({
        severity: 'error',
        field: 'capabilities',
        message: 'expected_bridge_capability_array',
      });
    }
  }
  if ('status' in value && !isBridgeConversionStatus(value.status)) {
    issues.push({
      severity: 'error',
      field: 'status',
      message: 'expected_bridge_conversion_status',
    });
  }
  if ('server_calls_allowed' in value && value.server_calls_allowed !== false) {
    issues.push({
      severity: 'error',
      field: 'server_calls_allowed',
      message: 'server_calls_not_allowed',
    });
  }
  if ('python_runtime_allowed' in value && value.python_runtime_allowed !== false) {
    issues.push({
      severity: 'error',
      field: 'python_runtime_allowed',
      message: 'python_runtime_not_allowed',
    });
  }
  return { valid: issues.length === 0, issues, metadata: BRIDGE_TYPES_PORT_METADATA };
}

export type FolOutputFormatType =
  | 'prolog'
  | 'tptp'
  | 'json'
  | 'defeasible'
  | 'smtlib'
  | 'natural_language';
export type PredicateCategoryType =
  | 'entity'
  | 'action'
  | 'relation'
  | 'property'
  | 'temporal'
  | 'modal'
  | 'unknown';

export class PredicateType {
  constructor(
    readonly name: string,
    readonly arity: number,
    readonly category: PredicateCategoryType = 'unknown',
    readonly definition?: string,
  ) {}

  toString(): string {
    if (this.arity === 0) return this.name;
    return `${this.name}(${Array.from({ length: this.arity }, (_, index) => `x${index}`).join(', ')})`;
  }
}

export class FOLFormulaType {
  constructor(
    readonly formulaString: string,
    readonly predicates: PredicateType[] = [],
    readonly quantifiers: Quantifier[] = [],
    readonly operators: LogicOperator[] = [],
    readonly variables: string[] = [],
    readonly complexity: ComplexityMetrics | undefined = undefined,
    readonly confidence: ConfidenceScore = 1.0,
    readonly metadata: Record<string, unknown> = {},
  ) {}

  getPredicateNames(): string[] {
    return this.predicates.map((predicate) => predicate.name);
  }

  hasQuantifiers(): boolean {
    return this.quantifiers.length > 0;
  }
}

export class FOLConversionResultType {
  constructor(
    readonly sourceText: string,
    readonly folFormula: FOLFormulaType,
    readonly outputFormat: FolOutputFormatType,
    readonly formattedOutput: string,
    readonly confidence: ConfidenceScore,
    readonly warnings: string[] = [],
    readonly metadata: Record<string, unknown> = {},
  ) {}

  isHighConfidence(threshold = 0.7): boolean {
    return this.confidence >= threshold;
  }
}

export class PredicateExtractionType {
  constructor(
    readonly text: string,
    readonly predicatesByCategory: Partial<Record<PredicateCategoryType, PredicateType[]>>,
    readonly totalPredicates: number,
    readonly confidence: ConfidenceScore,
  ) {}

  getAllPredicates(): PredicateType[] {
    return Object.values(this.predicatesByCategory).flatMap((predicates) => predicates ?? []);
  }
}

export type LogicTranslationTarget =
  | 'lean'
  | 'coq'
  | 'isabelle'
  | 'smt-lib'
  | 'tptp'
  | 'z3'
  | 'vampire'
  | 'eprover'
  | 'agda'
  | 'hol'
  | 'pvs';

export class TranslationResultType {
  constructor(
    readonly target: LogicTranslationTarget,
    readonly translatedFormula: string,
    readonly success: boolean,
    readonly confidence = 1.0,
    readonly errors: string[] = [],
    readonly warnings: string[] = [],
    readonly metadata: Record<string, unknown> = {},
    readonly dependencies: string[] = [],
  ) {}

  toDict(): Record<string, unknown> {
    return {
      target: this.target,
      translated_formula: this.translatedFormula,
      success: this.success,
      confidence: this.confidence,
      errors: [...this.errors],
      warnings: [...this.warnings],
      metadata: { ...this.metadata },
      dependencies: [...this.dependencies],
    };
  }
}

export class AbstractLogicFormulaType {
  constructor(
    readonly formulaType: string,
    readonly operators: string[],
    readonly variables: Array<[string, string]>,
    readonly quantifiers: Array<[string, string, string]>,
    readonly propositions: string[],
    readonly logicalStructure: Record<string, unknown>,
    readonly sourceFormulaId?: string,
  ) {}

  toDict(): Record<string, unknown> {
    return {
      formula_type: this.formulaType,
      operators: [...this.operators],
      variables: this.variables.map((variable) => [...variable]),
      quantifiers: this.quantifiers.map((quantifier) => [...quantifier]),
      propositions: [...this.propositions],
      logical_structure: { ...this.logicalStructure },
      source_formula_id: this.sourceFormulaId,
    };
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function recordField(
  value: Record<string, unknown>,
  key: string,
  defaultValue: Record<string, unknown> = {},
): Record<string, unknown> {
  const field = value[key];
  return isRecord(field) ? { ...field } : defaultValue;
}

function stringField(value: Record<string, unknown>, key: string, defaultValue = ''): string {
  const field = value[key];
  return typeof field === 'string' ? field : defaultValue;
}

function numberField(value: Record<string, unknown>, key: string, defaultValue = 0): number {
  const field = value[key];
  return typeof field === 'number' && Number.isFinite(field) ? field : defaultValue;
}

function optionalNumberField(
  value: Record<string, unknown>,
  key: string,
  defaultValue?: number,
): number | undefined {
  const field = value[key];
  return typeof field === 'number' && Number.isFinite(field) ? field : defaultValue;
}

function booleanField(value: Record<string, unknown>, key: string, defaultValue = false): boolean {
  const field = value[key];
  return typeof field === 'boolean' ? field : defaultValue;
}
