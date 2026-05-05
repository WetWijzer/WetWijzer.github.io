import { parseTdfolFormula } from './parser';

export type TdfolSecurityLevel = 'low' | 'medium' | 'high' | 'paranoid';
export type TdfolThreatType =
  | 'injection'
  | 'dos'
  | 'resource_exhaustion'
  | 'malformed_input'
  | 'side_channel'
  | 'timing_attack'
  | 'recursive_bomb'
  | 'parse_error'
  | 'invalid_zkp';

export interface TdfolSecurityConfig {
  maxFormulaSize: number;
  maxFormulaDepth: number;
  maxVariables: number;
  maxOperators: number;
  maxMemoryMb: number;
  maxProofTimeSeconds: number;
  maxRequestsPerMinute: number;
  maxConcurrentRequests: number;
  securityLevel: TdfolSecurityLevel;
  allowedChars: Set<string>;
  dangerousPatterns: RegExp[];
  now: () => number;
}

export interface TdfolSecurityValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  threats: TdfolThreatType[];
  metadata: Record<string, unknown>;
}

export interface TdfolZkpAuditResult {
  passed: boolean;
  vulnerabilities: string[];
  recommendations: string[];
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  auditTime: number;
}

export interface TdfolSecurityBundleInput {
  formula: unknown;
  proofCacheEntry?: unknown;
  witness?: unknown;
  zkpPublicInputs?: unknown;
  identifier?: string;
}

export interface TdfolSecurityBundleResult extends TdfolSecurityValidationResult {
  checks: { formula: boolean; proofCache: boolean; witness: boolean; zkpPublicInputs: boolean };
}

export interface TdfolSecurityEvent {
  timestamp: string;
  threatType: TdfolThreatType;
  details: string;
  context: string;
  securityLevel: TdfolSecurityLevel;
}

export class TdfolRateLimiter {
  private readonly requests = new Map<string, number[]>();

  constructor(
    private readonly maxRequests: number,
    private readonly timeWindowMs: number,
    private readonly now: () => number = () => Date.now(),
  ) {}

  checkRateLimit(identifier: string): { allowed: boolean; error?: string } {
    const currentTime = this.now();
    const recent = (this.requests.get(identifier) ?? []).filter(
      (time) => currentTime - time < this.timeWindowMs,
    );
    if (recent.length >= this.maxRequests) {
      this.requests.set(identifier, recent);
      return {
        allowed: false,
        error: `Rate limit exceeded: ${recent.length}/${this.maxRequests} requests in ${this.timeWindowMs / 1000}s`,
      };
    }
    recent.push(currentTime);
    this.requests.set(identifier, recent);
    return { allowed: true };
  }
}

export class TdfolSecurityValidator {
  readonly config: TdfolSecurityConfig;
  readonly securityEvents: TdfolSecurityEvent[] = [];

  private readonly rateLimiter: TdfolRateLimiter;
  private concurrentRequests = 0;

  constructor(config: Partial<TdfolSecurityConfig> = {}) {
    this.config = {
      maxFormulaSize: config.maxFormulaSize ?? 10000,
      maxFormulaDepth: config.maxFormulaDepth ?? 100,
      maxVariables: config.maxVariables ?? 1000,
      maxOperators: config.maxOperators ?? 5000,
      maxMemoryMb: config.maxMemoryMb ?? 500,
      maxProofTimeSeconds: config.maxProofTimeSeconds ?? 30,
      maxRequestsPerMinute: config.maxRequestsPerMinute ?? 100,
      maxConcurrentRequests: config.maxConcurrentRequests ?? 10,
      securityLevel: config.securityLevel ?? 'medium',
      allowedChars:
        config.allowedChars ??
        new Set(
          "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()[]{}∀∃∧∨¬→↔=≠<>≤≥+-*/,.:_' ",
        ),
      dangerousPatterns: config.dangerousPatterns ?? [
        /__.*__/,
        /eval/i,
        /exec/i,
        /compile/i,
        /import/i,
        /__import__/i,
        /getattr/i,
        /setattr/i,
        /delattr/i,
      ],
      now: config.now ?? (() => Date.now()),
    };
    this.rateLimiter = new TdfolRateLimiter(
      this.config.maxRequestsPerMinute,
      60_000,
      this.config.now,
    );
  }

  validateFormula(
    formula: unknown,
    identifier = 'default',
    options: { parse?: boolean } = {},
  ): TdfolSecurityValidationResult {
    const result = createSecurityValidationResult();
    const rate = this.rateLimiter.checkRateLimit(identifier);
    if (!rate.allowed) {
      result.valid = false;
      result.errors.push(rate.error ?? 'Rate limit exceeded');
      result.threats.push('dos');
      this.logSecurityEvent('dos', rate.error ?? 'Rate limit exceeded', identifier);
      return result;
    }
    if (!this.acquireConcurrentSlot()) {
      result.valid = false;
      result.errors.push('Too many concurrent requests');
      result.threats.push('dos');
      return result;
    }

    try {
      this.validateInput(formula, result);
      if (typeof formula === 'string') {
        this.checkSizeLimits(formula, result);
        this.validateCharacters(formula, result);
        this.detectInjection(formula, result);
        this.detectDosPatterns(formula, result);
        this.detectRecursiveBombs(formula, result);
        if (options.parse ?? true) this.validateParse(formula, result);
        result.metadata = {
          formula_length: formula.length,
          formula_depth: calculateDepth(formula),
          variable_count: countVariables(formula),
          operator_count: countOperators(formula),
          validation_time: this.config.now(),
          security_level: this.config.securityLevel,
        };
      }
    } finally {
      this.concurrentRequests = Math.max(0, this.concurrentRequests - 1);
    }

    return result;
  }

  sanitizeInput(input: string): string {
    if (!input) return '';
    let sanitized = input.replace(/\x00/g, '');
    for (const pattern of this.config.dangerousPatterns) {
      let previous = '';
      while (previous !== sanitized) {
        previous = sanitized;
        sanitized = sanitized.replace(pattern, '');
      }
    }
    sanitized = sanitized.replace(/\s+/g, ' ');
    sanitized = [...sanitized].filter((char) => /[\n\t]/.test(char) || char >= ' ').join('');
    return sanitized.slice(0, this.config.maxFormulaSize).trim();
  }

  checkResourceLimits(formula: string, memoryMb?: number, timeSeconds?: number): boolean {
    if (memoryMb !== undefined && memoryMb > this.config.maxMemoryMb) return false;
    if (timeSeconds !== undefined && timeSeconds > this.config.maxProofTimeSeconds) return false;
    const result = createSecurityValidationResult();
    this.checkSizeLimits(formula, result);
    return result.valid;
  }

  auditZkpProof(proof: Record<string, unknown>): TdfolZkpAuditResult {
    const startedAt = performance.now();
    const result: TdfolZkpAuditResult = {
      passed: true,
      vulnerabilities: [],
      recommendations: [],
      riskLevel: 'low',
      auditTime: 0,
    };
    this.validateProofStructure(proof, result);
    this.checkCryptoParameters(proof, result);
    this.checkProofIntegrity(proof, result);
    this.analyzeSideChannels(proof, result);
    result.riskLevel = calculateRiskLevel(result);
    result.auditTime = performance.now() - startedAt;
    return result;
  }

  validateSecurityBundle(input: TdfolSecurityBundleInput): TdfolSecurityBundleResult {
    const formulaResult = this.validateFormula(input.formula, input.identifier ?? 'bundle');
    const result: TdfolSecurityBundleResult = {
      ...formulaResult,
      errors: [...formulaResult.errors],
      warnings: [...formulaResult.warnings],
      threats: [...formulaResult.threats],
      metadata: { ...formulaResult.metadata },
      checks: {
        formula: formulaResult.valid,
        proofCache: true,
        witness: true,
        zkpPublicInputs: true,
      },
    };

    validateProofCacheEntry(input.proofCacheEntry, result);
    validateWitnessInput(input.witness, result);
    validateZkpPublicInputs(input.zkpPublicInputs, result);
    result.valid = result.valid && Object.values(result.checks).every(Boolean);
    result.metadata = {
      ...result.metadata,
      security_bundle_checked: true,
      proof_cache_checked: input.proofCacheEntry !== undefined,
      witness_checked: input.witness !== undefined,
      zkp_public_inputs_checked: input.zkpPublicInputs !== undefined,
    };
    return result;
  }

  detectDosPattern(formula: string): boolean {
    const result = createSecurityValidationResult();
    this.detectDosPatterns(formula, result);
    this.detectRecursiveBombs(formula, result);
    return result.threats.includes('dos') || result.threats.includes('recursive_bomb');
  }

  getSecurityReport(): Record<string, unknown> {
    const threatCounts = this.securityEvents.reduce<Record<string, number>>((counts, event) => {
      counts[event.threatType] = (counts[event.threatType] ?? 0) + 1;
      return counts;
    }, {});
    return {
      total_events: this.securityEvents.length,
      threat_counts: threatCounts,
      recent_events: this.securityEvents.slice(-20),
      security_level: this.config.securityLevel,
    };
  }

  private acquireConcurrentSlot(): boolean {
    if (this.concurrentRequests >= this.config.maxConcurrentRequests) return false;
    this.concurrentRequests += 1;
    return true;
  }

  private validateInput(formula: unknown, result: TdfolSecurityValidationResult): void {
    if (typeof formula !== 'string') {
      result.valid = false;
      result.errors.push('Formula must be a string');
      result.threats.push('malformed_input');
      return;
    }
    if (!formula) {
      result.valid = false;
      result.errors.push('Empty formula');
      result.threats.push('malformed_input');
    }
    if (formula.includes('\x00')) {
      result.valid = false;
      result.errors.push('Null bytes not allowed');
      result.threats.push('injection');
    }
  }

  private checkSizeLimits(formula: string, result: TdfolSecurityValidationResult): void {
    if (formula.length > this.config.maxFormulaSize) {
      result.valid = false;
      result.errors.push(`Formula too large: ${formula.length} > ${this.config.maxFormulaSize}`);
      result.threats.push('resource_exhaustion');
    }
    const depth = calculateDepth(formula);
    if (depth > this.config.maxFormulaDepth) {
      result.valid = false;
      result.errors.push(`Formula too deep: ${depth} > ${this.config.maxFormulaDepth}`);
      result.threats.push('resource_exhaustion');
    }
    const variableCount = countVariables(formula);
    if (variableCount > this.config.maxVariables) {
      result.valid = false;
      result.errors.push(`Too many variables: ${variableCount} > ${this.config.maxVariables}`);
      result.threats.push('resource_exhaustion');
    }
    const operatorCount = countOperators(formula);
    if (operatorCount > this.config.maxOperators) {
      result.valid = false;
      result.errors.push(`Too many operators: ${operatorCount} > ${this.config.maxOperators}`);
      result.threats.push('resource_exhaustion');
    }
  }

  private validateCharacters(formula: string, result: TdfolSecurityValidationResult): void {
    if (this.config.securityLevel !== 'high' && this.config.securityLevel !== 'paranoid') return;
    const invalidChars = [
      ...new Set([...formula].filter((char) => !this.config.allowedChars.has(char))),
    ];
    if (invalidChars.length === 0) return;
    const message = `Invalid characters: ${invalidChars.map((char) => JSON.stringify(char)).join(', ')}`;
    if (this.config.securityLevel === 'paranoid') {
      result.valid = false;
      result.errors.push(message);
      result.threats.push('injection');
    } else {
      result.warnings.push(message);
    }
  }

  private detectInjection(formula: string, result: TdfolSecurityValidationResult): void {
    for (const pattern of this.config.dangerousPatterns) {
      if (pattern.test(formula)) {
        result.valid = false;
        result.errors.push(`Dangerous pattern detected: ${pattern.source}`);
        result.threats.push('injection');
        this.logSecurityEvent('injection', `Pattern: ${pattern.source}`, formula.slice(0, 100));
      }
    }
    for (const sequence of ['$(', '`', '${', '|', ';', '&&', '||']) {
      if (!formula.includes(sequence)) continue;
      if (this.config.securityLevel === 'high' || this.config.securityLevel === 'paranoid') {
        result.valid = false;
        result.errors.push(`Dangerous sequence detected: ${sequence}`);
        result.threats.push('injection');
      } else {
        result.warnings.push(`Potentially dangerous sequence: ${sequence}`);
      }
    }
  }

  private detectDosPatterns(formula: string, result: TdfolSecurityValidationResult): void {
    if (hasExcessiveRepetition(formula)) {
      result.valid = false;
      result.errors.push('Excessive character repetition detected');
      result.threats.push('dos');
    }
    if (hasExponentialPattern(formula)) {
      result.warnings.push('Potentially expensive formula detected');
      if (this.config.securityLevel === 'paranoid') {
        result.valid = false;
        result.threats.push('dos');
      }
    }
  }

  private detectRecursiveBombs(formula: string, result: TdfolSecurityValidationResult): void {
    if (/(\w+)\s*=.*\1/.test(formula)) {
      result.warnings.push('Self-referential pattern detected');
      if (this.config.securityLevel === 'high' || this.config.securityLevel === 'paranoid') {
        result.threats.push('recursive_bomb');
      }
    }
    const variables = [...formula.matchAll(/\b[a-z][a-z0-9_]*\b/g)].map((match) => match[0]);
    const duplicates = variables.length - new Set(variables).size;
    if (duplicates > 10) result.warnings.push(`High variable reuse: ${duplicates} duplicates`);
  }

  private validateParse(formula: string, result: TdfolSecurityValidationResult): void {
    if (!result.valid) return;
    try {
      parseTdfolFormula(formula);
    } catch (error) {
      result.valid = false;
      result.errors.push(error instanceof Error ? error.message : 'Invalid TDFOL formula');
      result.threats.push('parse_error');
    }
  }

  private validateProofStructure(
    proof: Record<string, unknown>,
    result: TdfolZkpAuditResult,
  ): void {
    for (const field of ['commitment', 'challenge', 'response']) {
      if (!(field in proof)) {
        result.passed = false;
        result.vulnerabilities.push(`Missing required field: ${field}`);
      }
    }
    const unexpected = Object.keys(proof).filter(
      (key) =>
        !['commitment', 'challenge', 'response', 'metadata', 'timestamp', 'version'].includes(key),
    );
    if (unexpected.length > 0)
      result.recommendations.push(`Unexpected fields in proof: ${unexpected.join(', ')}`);
  }

  private checkCryptoParameters(proof: Record<string, unknown>, result: TdfolZkpAuditResult): void {
    if (typeof proof.commitment === 'string' && proof.commitment.length < 32) {
      result.passed = false;
      result.vulnerabilities.push('Commitment too short (< 32 bytes)');
    }
    if (
      typeof proof.challenge === 'string' &&
      new Set(proof.challenge).size < proof.challenge.length / 4
    ) {
      result.recommendations.push('Challenge appears to have low entropy');
    }
  }

  private checkProofIntegrity(proof: Record<string, unknown>, result: TdfolZkpAuditResult): void {
    const metadata = proof.metadata;
    if (!metadata || typeof metadata !== 'object' || !('hash' in metadata)) return;
    const proofData = Object.fromEntries(
      Object.entries(proof).filter(([key]) => key !== 'metadata'),
    );
    const calculatedHash = simpleHash(JSON.stringify(Object.entries(proofData).sort()));
    if ((metadata as { hash?: unknown }).hash !== calculatedHash) {
      result.passed = false;
      result.vulnerabilities.push('Proof integrity check failed');
    }
  }

  private analyzeSideChannels(proof: Record<string, unknown>, result: TdfolZkpAuditResult): void {
    const metadata = proof.metadata;
    if (!metadata || typeof metadata !== 'object') return;
    if (JSON.stringify(metadata).length > 1000)
      result.recommendations.push('Large metadata could leak information');
    for (const key of Object.keys(metadata)) {
      if (
        ['secret', 'private', 'key', 'password'].some((keyword) =>
          key.toLowerCase().includes(keyword),
        )
      ) {
        result.passed = false;
        result.vulnerabilities.push(`Potentially sensitive metadata field: ${key}`);
      }
    }
  }

  private logSecurityEvent(threatType: TdfolThreatType, details: string, context: string): void {
    this.securityEvents.push({
      timestamp: new Date(this.config.now()).toISOString(),
      threatType,
      details,
      context,
      securityLevel: this.config.securityLevel,
    });
  }
}

export function createSecurityValidationResult(): TdfolSecurityValidationResult {
  return { valid: true, errors: [], warnings: [], threats: [], metadata: {} };
}

export function calculateDepth(formula: string): number {
  let maxDepth = 0;
  let currentDepth = 0;
  for (const char of formula) {
    if ('([{'.includes(char)) {
      currentDepth += 1;
      maxDepth = Math.max(maxDepth, currentDepth);
    } else if (')]}'.includes(char)) {
      currentDepth = Math.max(0, currentDepth - 1);
    }
  }
  return maxDepth;
}

export function simpleHash(value: string): string {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

function countVariables(formula: string): number {
  return [...formula.matchAll(/\b[a-z][a-z0-9_]*\b/g)].length;
}

function countOperators(formula: string): number {
  return [...formula.matchAll(/[∀∃∧∨¬→↔=≠<>≤≥]/g)].length;
}

function hasExcessiveRepetition(formula: string, threshold = 100): boolean {
  for (let index = 0; index <= formula.length - threshold; index += 1) {
    if (new Set(formula.slice(index, index + threshold)).size < 5) return true;
  }
  return false;
}

function hasExponentialPattern(formula: string): boolean {
  let quantifierDepth = 0;
  let maxQuantifierDepth = 0;
  for (const char of formula) {
    if (char === '∀' || char === '∃') {
      quantifierDepth += 1;
      maxQuantifierDepth = Math.max(maxQuantifierDepth, quantifierDepth);
    } else if (char === '.') {
      quantifierDepth = Math.max(0, quantifierDepth - 1);
    }
  }
  return maxQuantifierDepth > 10;
}

function validateProofCacheEntry(entry: unknown, result: TdfolSecurityBundleResult): void {
  if (entry === undefined) return;
  if (!isPlainRecord(entry)) {
    failBundleCheck(result, 'proofCache', 'Proof cache entry must be an object', 'malformed_input');
    return;
  }
  const status = entry.status;
  if (
    typeof entry.theorem !== 'string' ||
    !['proved', 'disproved', 'unknown', 'timeout', 'error', 'unprovable'].includes(String(status))
  ) {
    failBundleCheck(
      result,
      'proofCache',
      'Proof cache entry must include a theorem and known status',
      'malformed_input',
    );
  }
  if (!Array.isArray(entry.steps)) {
    failBundleCheck(
      result,
      'proofCache',
      'Proof cache entry steps must be an array',
      'malformed_input',
    );
  }
  if (typeof entry.method === 'string' && /python|subprocess|rpc|server|http/i.test(entry.method)) {
    failBundleCheck(
      result,
      'proofCache',
      'Proof cache entry references a non-browser proof method',
      'side_channel',
    );
  }
}

function validateWitnessInput(witness: unknown, result: TdfolSecurityBundleResult): void {
  if (witness === undefined) return;
  if (!isPlainRecord(witness) || !Array.isArray(witness.axioms)) {
    failBundleCheck(result, 'witness', 'Witness must include an axioms array', 'invalid_zkp');
    return;
  }
  if (!witness.axioms.every((axiom) => typeof axiom === 'string' && axiom.length > 0)) {
    failBundleCheck(result, 'witness', 'Witness axioms must be non-empty strings', 'invalid_zkp');
  }
  const intermediateSteps = witness.intermediate_steps ?? witness.intermediateSteps;
  if (intermediateSteps !== undefined && !Array.isArray(intermediateSteps)) {
    failBundleCheck(
      result,
      'witness',
      'Witness intermediate steps must be an array',
      'invalid_zkp',
    );
  }
  for (const key of Object.keys(witness)) {
    if (/secret|private[_-]?key|password/i.test(key)) {
      failBundleCheck(
        result,
        'witness',
        `Witness contains sensitive field: ${key}`,
        'side_channel',
      );
    }
  }
}

function validateZkpPublicInputs(inputs: unknown, result: TdfolSecurityBundleResult): void {
  if (inputs === undefined) return;
  if (!isPlainRecord(inputs)) {
    failBundleCheck(
      result,
      'zkpPublicInputs',
      'ZKP public inputs must be an object',
      'invalid_zkp',
    );
    return;
  }
  for (const field of ['theorem_hash', 'axioms_commitment', 'circuit_version', 'ruleset_id']) {
    if (!(field in inputs)) {
      failBundleCheck(
        result,
        'zkpPublicInputs',
        `Missing ZKP public input: ${field}`,
        'invalid_zkp',
      );
    }
  }
  for (const field of ['theorem_hash', 'axioms_commitment']) {
    const value = inputs[field];
    if (typeof value !== 'string' || !/^[0-9a-f]{64}$/i.test(value)) {
      failBundleCheck(
        result,
        'zkpPublicInputs',
        `Invalid ZKP field element hash: ${field}`,
        'invalid_zkp',
      );
    }
  }
  if (!Number.isSafeInteger(inputs.circuit_version) || Number(inputs.circuit_version) <= 0) {
    failBundleCheck(result, 'zkpPublicInputs', 'Invalid ZKP circuit version', 'invalid_zkp');
  }
  if (typeof inputs.ruleset_id !== 'string' || inputs.ruleset_id.length === 0) {
    failBundleCheck(result, 'zkpPublicInputs', 'Invalid ZKP ruleset id', 'invalid_zkp');
  }
}

function failBundleCheck(
  result: TdfolSecurityBundleResult,
  check: keyof TdfolSecurityBundleResult['checks'],
  message: string,
  threat: TdfolThreatType,
): void {
  result.checks[check] = false;
  result.valid = false;
  result.errors.push(message);
  result.threats.push(threat);
}

function isPlainRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function calculateRiskLevel(result: TdfolZkpAuditResult): TdfolZkpAuditResult['riskLevel'] {
  if (!result.passed) return 'critical';
  if (result.vulnerabilities.length > 0) return 'high';
  if (result.recommendations.length > 3) return 'medium';
  return 'low';
}
