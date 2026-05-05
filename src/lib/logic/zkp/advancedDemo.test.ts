import { webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import { runAdvancedZkpDemo, run_advanced_zkp_demo } from './advancedDemo';

Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextEncoder', {
  value: TextEncoder,
  configurable: true,
});

describe('advanced ZKP demo browser-native parity', () => {
  it('runs the advanced demo flow with simulated proofs, cache, verifier stats, and circuit metadata', async () => {
    const first = await runAdvancedZkpDemo({ seed: 'fixture' });
    const second = await runAdvancedZkpDemo({ seed: 'fixture' });

    expect(first).toMatchObject({
      axiom_count: 2,
      backend: 'simulated',
      cached_verified: true,
      cryptographic: false,
      module: 'logic/zkp/examples/zkp_advanced_demo.py',
      runtime: 'browser-native-typescript',
      tampered_verified: false,
      theorem: 'Q',
      verified: true,
    });
    expect(first.proof.proof_data).toBe(second.proof.proof_data);
    expect(first.cached_proof.public_inputs.theorem).toBe(' Q ');
    expect(first.prover_stats).toMatchObject({
      cache_hit_rate: 0.5,
      cache_hits: 1,
      proofs_generated: 1,
    });
    expect(first.verifier_stats).toMatchObject({
      acceptance_rate: 2 / 3,
      proofs_rejected: 1,
      proofs_verified: 2,
    });
    expect(first.circuit).toMatchObject({
      kind: 'implication',
      num_gates: 1,
      num_inputs: 2,
      num_wires: 3,
      r1cs_constraints: 1,
    });
    expect(first.circuit.hash).toHaveLength(64);
    expect(first.backends.simulated.available).toBe(true);
    expect(first.backends.groth16.available).toBe(false);
    expect(first.warnings.join(' ')).toContain('not cryptographically secure');
  });

  it('keeps the Python-style alias available', async () => {
    const result = await run_advanced_zkp_demo({
      axioms: ['Permit(Alice)', 'Permit(Alice) -> Access(Alice)'],
      seed: 'alias',
      theorem: 'Access(Alice)',
    });

    expect(result.verified).toBe(true);
    expect(result.proof.public_inputs.theorem).toBe('Access(Alice)');
    expect(result.proof.public_inputs.ruleset_id).toBe('TDFOL_v1');
  });
});
