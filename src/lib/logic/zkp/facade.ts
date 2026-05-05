import { canonicalizeAxioms, canonicalizeTheorem, theoremHashHex } from './canonicalization';
import { getBackend, type ZKBackend, ZKPError, ZKPProof } from './simulatedBackend';
import { parseCircuitRefLenient } from './statement';

export interface ZKPProverStats {
  proofs_generated: number;
  cache_hits: number;
  total_proving_time: number;
  avg_proving_time: number;
  cache_hit_rate: number;
}

export interface ZKPBatchProofRequest {
  theorem: string;
  privateAxioms?: string[];
  private_axioms?: string[];
  axioms?: string[];
  metadata?: Record<string, unknown>;
}

export interface ZKPBatchProofResult {
  index: number;
  ok: boolean;
  proof?: ZKPProof;
  error?: string;
}

export interface ZKPVerifierStats {
  proofs_verified: number;
  proofs_rejected: number;
  total_verification_time: number;
  avg_verification_time: number;
  acceptance_rate: number;
}

export interface ZKPVerificationResult {
  ok: boolean;
  verified: boolean;
  backend: string;
  elapsed_seconds: number;
  public_inputs_valid: boolean;
  structure_valid: boolean;
  security_level: number;
  theorem?: string;
  expected_theorem?: string;
  reason?: string;
  error?: string;
}

export interface ZKPBatchVerificationRequest {
  proof: ZKPProof;
  expectedTheorem?: string;
  expected_theorem?: string;
}

export interface ZKPBatchVerificationResult extends ZKPVerificationResult {
  index: number;
}

export type ZKPBatchVerificationItem = ZKPProof | ZKPBatchVerificationRequest;

export class ZKPProver {
  readonly securityLevel: number;
  readonly security_level: number;
  readonly enableCaching: boolean;
  readonly enable_caching: boolean;
  readonly backend: string;
  private readonly backendInstance: ZKBackend;
  private readonly proofCache = new Map<string, ZKPProof>();
  private readonly stats = {
    cache_hits: 0,
    proofs_generated: 0,
    total_proving_time: 0,
  };

  constructor(options: { securityLevel?: number; enableCaching?: boolean; backend?: string } = {}) {
    this.securityLevel = options.securityLevel ?? 128;
    this.security_level = this.securityLevel;
    this.enableCaching = options.enableCaching ?? true;
    this.enable_caching = this.enableCaching;
    this.backend = options.backend ?? 'simulated';
    this.backendInstance = getBackend(this.backend);
  }

  getBackendInstance(): ZKBackend {
    return this.backendInstance;
  }

  get_backend_instance(): ZKBackend {
    return this.getBackendInstance();
  }

  async generateProof(
    theorem: string,
    privateAxioms: string[],
    metadata: Record<string, unknown> = {},
  ): Promise<ZKPProof> {
    const start = nowSeconds();
    try {
      const cacheKey = await this.computeCacheKey(theorem, privateAxioms, metadata);
      if (this.enableCaching && this.proofCache.has(cacheKey)) {
        this.stats.cache_hits += 1;
        return this.adaptCachedProof(this.proofCache.get(cacheKey)!, theorem);
      }

      if (!theorem) {
        throw new ZKPError('Theorem cannot be empty');
      }
      if (privateAxioms.length === 0) {
        throw new ZKPError('At least one axiom required');
      }

      const proof = await this.backendInstance.generateProof(theorem, privateAxioms, {
        ...metadata,
        security_level: this.securityLevel,
      });

      this.stats.proofs_generated += 1;
      this.stats.total_proving_time += nowSeconds() - start;
      if (this.enableCaching) {
        this.proofCache.set(cacheKey, proof);
      }
      return proof;
    } catch (error) {
      if (error instanceof ZKPError && error.message.startsWith('Proof generation failed:')) {
        throw error;
      }
      throw new ZKPError(
        `Proof generation failed: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  generate_proof(
    theorem: string,
    privateAxioms: string[],
    metadata: Record<string, unknown> = {},
  ): Promise<ZKPProof> {
    return this.generateProof(theorem, privateAxioms, metadata);
  }

  async generateBatchProofs(requests: ZKPBatchProofRequest[]): Promise<ZKPBatchProofResult[]> {
    const results: ZKPBatchProofResult[] = [];
    for (let index = 0; index < requests.length; index += 1) {
      const request = requests[index];
      const privateAxioms = request.privateAxioms ?? request.private_axioms ?? request.axioms ?? [];
      try {
        results.push({
          index,
          ok: true,
          proof: await this.generateProof(request.theorem, privateAxioms, request.metadata ?? {}),
        });
      } catch (error) {
        results.push({
          error: error instanceof Error ? error.message : String(error),
          index,
          ok: false,
        });
      }
    }
    return results;
  }

  generate_batch_proofs(requests: ZKPBatchProofRequest[]): Promise<ZKPBatchProofResult[]> {
    return this.generateBatchProofs(requests);
  }

  async prove(
    statement: string,
    witness?: { axioms?: string[] } | string | string[],
    metadata?: Record<string, unknown>,
  ): Promise<ZKPProof> {
    let privateAxioms: string[] = [];
    if (Array.isArray(witness)) {
      privateAxioms = witness;
    } else if (typeof witness === 'string') {
      privateAxioms = [witness];
    } else if (witness && Array.isArray(witness.axioms)) {
      privateAxioms = witness.axioms;
    }
    return this.generateProof(statement, privateAxioms, metadata);
  }

  async computeCacheKey(
    theorem: string,
    axioms: string[],
    metadata: Record<string, unknown> = {},
  ): Promise<string> {
    const meta: Record<string, unknown> = { security_level: this.securityLevel };
    for (const key of ['seed', 'circuit_version', 'ruleset_id']) {
      if (Object.prototype.hasOwnProperty.call(metadata, key)) {
        meta[key] = metadata[key];
      }
    }
    return sha256Hex(
      stableJsonStringify({
        axioms: canonicalizeAxioms(axioms),
        meta,
        theorem: canonicalizeTheorem(theorem),
      }),
    );
  }

  _compute_cache_key(
    theorem: string,
    axioms: string[],
    metadata: Record<string, unknown> = {},
  ): Promise<string> {
    return this.computeCacheKey(theorem, axioms, metadata);
  }

  getStats(): ZKPProverStats {
    const totalAttempts = this.stats.proofs_generated + this.stats.cache_hits;
    return {
      ...this.stats,
      avg_proving_time:
        this.stats.proofs_generated > 0
          ? this.stats.total_proving_time / this.stats.proofs_generated
          : 0,
      cache_hit_rate: totalAttempts > 0 ? this.stats.cache_hits / totalAttempts : 0,
    };
  }

  get_stats(): ZKPProverStats {
    return this.getStats();
  }

  clearCache(): void {
    this.proofCache.clear();
  }

  clear_cache(): void {
    this.clearCache();
  }

  private async adaptCachedProof(proof: ZKPProof, theorem: string): Promise<ZKPProof> {
    if (proof.publicInputs.theorem === theorem) {
      return proof;
    }
    const publicInputs: Record<string, unknown> = { ...proof.publicInputs, theorem };
    if (typeof publicInputs.theorem_hash === 'string') {
      publicInputs.theorem_hash = await theoremHashHex(theorem);
    }
    return new ZKPProof({
      metadata: proof.metadata,
      proofData: proof.proofData,
      publicInputs,
      sizeBytes: proof.sizeBytes,
      timestamp: proof.timestamp,
    });
  }
}

export class ZKPVerifier {
  readonly securityLevel: number;
  readonly security_level: number;
  readonly backend: string;
  private readonly backendInstance: ZKBackend;
  private stats = {
    proofs_rejected: 0,
    proofs_verified: 0,
    total_verification_time: 0,
  };

  constructor(options: { securityLevel?: number; backend?: string } = {}) {
    this.securityLevel = options.securityLevel ?? 128;
    this.security_level = this.securityLevel;
    this.backend = options.backend ?? 'simulated';
    this.backendInstance = getBackend(this.backend);
  }

  async verifyProof(proof: ZKPProof): Promise<boolean> {
    const start = nowSeconds();
    try {
      if (!this.validateProofStructure(proof)) {
        this.stats.proofs_rejected += 1;
        return false;
      }

      const isValid = await this.backendInstance.verifyProof(proof);
      this.stats.total_verification_time += nowSeconds() - start;
      if (isValid) {
        this.stats.proofs_verified += 1;
      } else {
        this.stats.proofs_rejected += 1;
      }
      return isValid;
    } catch (error) {
      throw new ZKPError(
        `Proof verification failed: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  verify_proof(proof: ZKPProof): Promise<boolean> {
    return this.verifyProof(proof);
  }

  async verifyProofDetailed(
    proof: ZKPProof,
    options: { expectedTheorem?: string; expected_theorem?: string } = {},
  ): Promise<ZKPVerificationResult> {
    const expectedTheorem = options.expectedTheorem ?? options.expected_theorem;
    const start = nowSeconds();
    const publicInputsValid = this.validatePublicInputs(proof.publicInputs);
    const structureValid = publicInputsValid && this.validateProofStructure(proof);

    try {
      if (!structureValid) {
        this.stats.proofs_rejected += 1;
        return this.buildVerificationResult({
          elapsedSeconds: nowSeconds() - start,
          expectedTheorem,
          proof,
          publicInputsValid,
          reason: publicInputsValid ? 'invalid_proof_structure' : 'invalid_public_inputs',
          structureValid,
          verified: false,
        });
      }

      const backendVerified = await this.backendInstance.verifyProof(proof);
      const theoremMatches =
        expectedTheorem === undefined || proof.publicInputs.theorem === expectedTheorem;
      const verified = backendVerified && theoremMatches;
      this.stats.total_verification_time += nowSeconds() - start;
      if (verified) {
        this.stats.proofs_verified += 1;
      } else {
        this.stats.proofs_rejected += 1;
      }

      return this.buildVerificationResult({
        elapsedSeconds: nowSeconds() - start,
        expectedTheorem,
        proof,
        publicInputsValid,
        reason: backendVerified ? 'expected_theorem_mismatch' : 'backend_verification_failed',
        structureValid,
        verified,
      });
    } catch (error) {
      this.stats.proofs_rejected += 1;
      return this.buildVerificationResult({
        elapsedSeconds: nowSeconds() - start,
        error: error instanceof Error ? error.message : String(error),
        expectedTheorem,
        proof,
        publicInputsValid,
        reason: 'verification_error',
        structureValid,
        verified: false,
      });
    }
  }

  verify_proof_detailed(
    proof: ZKPProof,
    options: { expectedTheorem?: string; expected_theorem?: string } = {},
  ): Promise<ZKPVerificationResult> {
    return this.verifyProofDetailed(proof, options);
  }

  async verifyBatchProofs(
    items: ZKPBatchVerificationItem[],
  ): Promise<ZKPBatchVerificationResult[]> {
    const results: ZKPBatchVerificationResult[] = [];
    for (let index = 0; index < items.length; index += 1) {
      const item = items[index];
      const request = item instanceof ZKPProof ? { proof: item } : item;
      const result = await this.verifyProofDetailed(request.proof, {
        expectedTheorem: request.expectedTheorem,
        expected_theorem: request.expected_theorem,
      });
      results.push({ ...result, index });
    }
    return results;
  }

  verify_batch_proofs(items: ZKPBatchVerificationItem[]): Promise<ZKPBatchVerificationResult[]> {
    return this.verifyBatchProofs(items);
  }

  validateProofStructure(proof: ZKPProof): boolean {
    try {
      if (proof.proofData.byteLength === 0 || Object.keys(proof.publicInputs).length === 0) {
        return false;
      }
      if (!this.validatePublicInputs(proof.publicInputs)) {
        return false;
      }

      const proofBackend = String(
        proof.metadata.backend ?? proof.metadata.proof_system ?? '',
      ).toLowerCase();
      const maxSize =
        proofBackend.startsWith('groth16') || proofBackend.includes('groth16') ? 50_000 : 300;
      if (proof.sizeBytes < 100 || proof.sizeBytes > maxSize) {
        return false;
      }

      const proofSecurity = Number(proof.metadata.security_level ?? 0);
      return proofSecurity >= this.securityLevel;
    } catch {
      return false;
    }
  }

  _validate_proof_structure(proof: ZKPProof): boolean {
    return this.validateProofStructure(proof);
  }

  validatePublicInputs(publicInputs: unknown): boolean {
    if (!publicInputs || typeof publicInputs !== 'object' || Array.isArray(publicInputs))
      return false;
    const inputs = publicInputs as Record<string, unknown>;
    if (typeof inputs.theorem !== 'string' || inputs.theorem === '') return false;
    if (!isHex32Bytes(inputs.theorem_hash)) return false;
    if ('axioms_commitment' in inputs && !isHex32Bytes(inputs.axioms_commitment)) return false;

    if ('circuit_version' in inputs) {
      const version = inputs.circuit_version;
      if (!Number.isInteger(version) || Number(version) < 0) return false;
    }

    if ('circuit_ref' in inputs) {
      if (typeof inputs.circuit_ref !== 'string' || inputs.circuit_ref === '') return false;
      try {
        const parsed = parseCircuitRefLenient(inputs.circuit_ref);
        if (
          'circuit_version' in inputs &&
          Number(inputs.circuit_version) !== Number(parsed.version)
        )
          return false;
      } catch {
        return false;
      }
    }

    if (
      'ruleset_id' in inputs &&
      (typeof inputs.ruleset_id !== 'string' || inputs.ruleset_id === '')
    )
      return false;
    return true;
  }

  _validate_public_inputs(publicInputs: unknown): boolean {
    return this.validatePublicInputs(publicInputs);
  }

  async verifyWithPublicInputs(proof: ZKPProof, expectedTheorem: string): Promise<boolean> {
    if (!(await this.verifyProof(proof))) {
      return false;
    }
    return proof.publicInputs.theorem === expectedTheorem;
  }

  verify_with_public_inputs(proof: ZKPProof, expectedTheorem: string): Promise<boolean> {
    return this.verifyWithPublicInputs(proof, expectedTheorem);
  }

  getStats(): ZKPVerifierStats {
    const totalProofs = this.stats.proofs_verified + this.stats.proofs_rejected;
    return {
      ...this.stats,
      acceptance_rate: totalProofs > 0 ? this.stats.proofs_verified / totalProofs : 0,
      avg_verification_time: totalProofs > 0 ? this.stats.total_verification_time / totalProofs : 0,
    };
  }

  get_stats(): ZKPVerifierStats {
    return this.getStats();
  }

  resetStats(): void {
    this.stats = {
      proofs_rejected: 0,
      proofs_verified: 0,
      total_verification_time: 0,
    };
  }

  reset_stats(): void {
    this.resetStats();
  }

  private buildVerificationResult(input: {
    proof: ZKPProof;
    verified: boolean;
    elapsedSeconds: number;
    publicInputsValid: boolean;
    structureValid: boolean;
    expectedTheorem?: string;
    reason?: string;
    error?: string;
  }): ZKPVerificationResult {
    const theorem =
      typeof input.proof.publicInputs.theorem === 'string' ? input.proof.publicInputs.theorem : '';
    return {
      backend: this.backend,
      elapsed_seconds: input.elapsedSeconds,
      error: input.error,
      expected_theorem: input.expectedTheorem,
      ok: input.verified,
      public_inputs_valid: input.publicInputsValid,
      reason: input.verified ? undefined : input.reason,
      security_level: this.securityLevel,
      structure_valid: input.structureValid,
      theorem,
      verified: input.verified,
    };
  }
}

function isHex32Bytes(value: unknown): boolean {
  return typeof value === 'string' && /^[0-9a-fA-F]{64}$/.test(value);
}

function nowSeconds(): number {
  return (globalThis.performance?.now?.() ?? Date.now()) / 1000;
}

async function sha256Hex(text: string): Promise<string> {
  const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function stableJsonStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(stableJsonStringify).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJsonStringify(record[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}
