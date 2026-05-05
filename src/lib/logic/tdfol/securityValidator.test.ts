import {
  TdfolRateLimiter,
  TdfolSecurityValidator,
  calculateDepth,
  simpleHash,
} from './securityValidator';

describe('TdfolSecurityValidator', () => {
  it('validates ordinary formulas and reports metadata', () => {
    const validator = new TdfolSecurityValidator({ now: () => 0 });

    expect(validator.validateFormula('∀x (Person(x) → O(Comply(x)))')).toMatchObject({
      valid: true,
      errors: [],
      metadata: {
        formula_length: 29,
        formula_depth: 3,
        variable_count: 3,
        operator_count: 2,
        security_level: 'medium',
      },
    });
  });

  it('detects malformed input, null bytes, size, depth, variable, and operator limits', () => {
    expect(new TdfolSecurityValidator().validateFormula(null)).toMatchObject({
      valid: false,
      threats: ['malformed_input'],
    });
    expect(new TdfolSecurityValidator().validateFormula('P(x)\x00')).toMatchObject({
      valid: false,
      threats: ['injection'],
    });

    const validator = new TdfolSecurityValidator({
      maxFormulaSize: 5,
      maxFormulaDepth: 1,
      maxVariables: 1,
      maxOperators: 1,
    });
    const result = validator.validateFormula('∀x (P(y) ∧ Q(z))');

    expect(result.valid).toBe(false);
    expect(result.threats).toContain('resource_exhaustion');
  });

  it('fails closed on parser errors while allowing explicit structural-only validation', () => {
    const validator = new TdfolSecurityValidator({ now: () => 0 });

    expect(validator.validateFormula('forall x. Person(')).toMatchObject({
      valid: false,
      threats: expect.arrayContaining(['parse_error']),
    });
    expect(validator.validateFormula('forall x. Person(', 'draft', { parse: false })).toMatchObject(
      {
        valid: true,
        threats: [],
        metadata: {
          formula_depth: 1,
          variable_count: 2,
        },
      },
    );
  });

  it('detects injection and DoS patterns according to security level', () => {
    const validator = new TdfolSecurityValidator({ securityLevel: 'high' });

    expect(validator.validateFormula('P(eval(x))')).toMatchObject({
      valid: false,
      threats: expect.arrayContaining(['injection']),
    });
    expect(validator.validateFormula('P(x); rm -rf /')).toMatchObject({
      valid: false,
      threats: expect.arrayContaining(['injection']),
    });
    expect(validator.detectDosPattern('a'.repeat(120))).toBe(true);
  });

  it('sanitizes input and checks resource limits', () => {
    const validator = new TdfolSecurityValidator({ maxFormulaSize: 8 });

    expect(validator.sanitizeInput(' eval(P(x))\x00 '.repeat(2))).toBe('(P(x))');
    expect(validator.checkResourceLimits('P(x)', 1, 1)).toBe(true);
    expect(validator.checkResourceLimits('P(x)', 999, 1)).toBe(false);
    expect(calculateDepth('A(B(C))')).toBe(2);
  });

  it('rate limits repeated identifiers', () => {
    let now = 0;
    const limiter = new TdfolRateLimiter(2, 1000, () => now);

    expect(limiter.checkRateLimit('a').allowed).toBe(true);
    expect(limiter.checkRateLimit('a').allowed).toBe(true);
    expect(limiter.checkRateLimit('a').allowed).toBe(false);
    now = 1001;
    expect(limiter.checkRateLimit('a').allowed).toBe(true);
  });

  it('audits ZKP proof structure and metadata', () => {
    const validator = new TdfolSecurityValidator();
    const proof = {
      commitment: 'a'.repeat(32),
      challenge: 'abcdef123456',
      response: 'response',
      metadata: {
        hash: simpleHash(
          JSON.stringify(
            Object.entries({
              commitment: 'a'.repeat(32),
              challenge: 'abcdef123456',
              response: 'response',
            }).sort(),
          ),
        ),
      },
    };

    expect(validator.auditZkpProof(proof)).toMatchObject({
      passed: true,
      riskLevel: 'low',
    });
    expect(
      validator.auditZkpProof({
        commitment: 'short',
        challenge: 'aaaa',
        response: 'r',
        metadata: { privateKey: 'x' },
      }),
    ).toMatchObject({
      passed: false,
      riskLevel: 'critical',
    });
  });

  it('fails closed across formula, proof-cache, witness, and ZKP public input checks', () => {
    const validator = new TdfolSecurityValidator({ now: () => 0 });
    const validHash = 'a'.repeat(64);
    const accepted = validator.validateSecurityBundle({
      formula: 'P(alice)',
      proofCacheEntry: { theorem: 'P(alice)', status: 'proved', steps: [] },
      witness: { axioms: ['P(alice)'], theorem: 'P(alice)', intermediate_steps: [] },
      zkpPublicInputs: {
        theorem_hash: validHash,
        axioms_commitment: validHash,
        circuit_version: 1,
        ruleset_id: 'TDFOL_v1',
      },
    });
    expect(accepted).toMatchObject({
      valid: true,
      checks: { formula: true, proofCache: true, witness: true, zkpPublicInputs: true },
      metadata: {
        security_bundle_checked: true,
        proof_cache_checked: true,
        witness_checked: true,
        zkp_public_inputs_checked: true,
      },
    });

    const rejected = validator.validateSecurityBundle({
      formula: 'forall x. Person(',
      proofCacheEntry: { theorem: 'Person(alice)', status: 'proved', method: 'python-rpc' },
      witness: { axioms: ['Person(alice)'], privateKey: 'leak' },
      zkpPublicInputs: {
        theorem_hash: 'short',
        axioms_commitment: validHash,
        circuit_version: 0,
      },
    });

    expect(rejected.valid).toBe(false);
    expect(rejected.checks).toEqual({
      formula: false,
      proofCache: false,
      witness: false,
      zkpPublicInputs: false,
    });
    expect(rejected.threats).toEqual(
      expect.arrayContaining(['parse_error', 'malformed_input', 'side_channel', 'invalid_zkp']),
    );
  });

  it('records security events in reports', () => {
    const validator = new TdfolSecurityValidator({ maxRequestsPerMinute: 1, now: () => 0 });
    validator.validateFormula('P(x)', 'id');
    validator.validateFormula('P(x)', 'id');

    expect(validator.getSecurityReport()).toMatchObject({
      total_events: 1,
      threat_counts: { dos: 1 },
    });
  });
});
