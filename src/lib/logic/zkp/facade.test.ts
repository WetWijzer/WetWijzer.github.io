import { webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import { runBasicZkpDemo, run_basic_zkp_demo } from './basicDemo';
import { ZKPProver, ZKPVerifier } from './facade';
import { ZKPError, ZKPProof } from './simulatedBackend';

Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextEncoder', {
  value: TextEncoder,
  configurable: true,
});

describe('ZKP prover and verifier browser-native facades', () => {
  it('generates simulated proofs through the backend and tracks cache statistics', async () => {
    const prover = new ZKPProver({ securityLevel: 128 });
    const proof = await prover.generateProof('Q', ['P', 'P -> Q'], { circuit_version: 2 });
    const cached = await prover.generateProof(' Q ', ['P -> Q', 'P'], { circuit_version: 2 });

    expect(proof.sizeBytes).toBe(160);
    expect(proof.metadata).toMatchObject({
      proof_system: 'Groth16 (simulated)',
      security_level: 128,
    });
    expect(cached.publicInputs.theorem).toBe(' Q ');
    expect(cached.publicInputs.theorem_hash).toBe(proof.publicInputs.theorem_hash);
    expect(prover.getStats()).toMatchObject({
      proofs_generated: 1,
      cache_hits: 1,
      cache_hit_rate: 0.5,
    });
  });

  it('supports the Python-style prove alias witness forms', async () => {
    const prover = new ZKPProver();

    await expect(prover.prove('Q', { axioms: ['P'] })).resolves.toBeInstanceOf(ZKPProof);
    await expect(prover.prove('Q', 'P')).resolves.toBeInstanceOf(ZKPProof);
    await expect(prover.prove('Q', ['P'])).resolves.toBeInstanceOf(ZKPProof);
    await expect(prover.prove('Q')).rejects.toThrow('At least one axiom required');
  });

  it('wraps invalid proof generation in ZKPError', async () => {
    const prover = new ZKPProver();

    await expect(prover.generateProof('', ['P'])).rejects.toThrow(ZKPError);
    await expect(prover.generateProof('', ['P'])).rejects.toThrow(
      'Proof generation failed: Theorem cannot be empty',
    );
  });

  it('validates and verifies proofs with public input checks and stats', async () => {
    const prover = new ZKPProver();
    const verifier = new ZKPVerifier();
    const proof = await prover.generateProof('Q', ['P'], {
      circuit_ref: 'knowledge_of_axioms@v1',
      circuit_version: 1,
    });

    await expect(verifier.verifyProof(proof)).resolves.toBe(true);
    await expect(verifier.verifyWithPublicInputs(proof, 'Q')).resolves.toBe(true);
    await expect(verifier.verifyWithPublicInputs(proof, 'R')).resolves.toBe(false);
    expect(verifier.getStats()).toMatchObject({
      proofs_verified: 3,
      proofs_rejected: 0,
      acceptance_rate: 1,
    });
  });

  it('rejects malformed public inputs and insufficient security', async () => {
    const prover = new ZKPProver({ securityLevel: 64 });
    const verifier = new ZKPVerifier({ securityLevel: 128 });
    const proof = await prover.generateProof('Q', ['P']);
    const invalidRef = new ZKPProof({
      metadata: { ...proof.metadata, security_level: 128 },
      proofData: proof.proofData,
      publicInputs: { ...proof.publicInputs, circuit_ref: 'c@v2', circuit_version: 1 },
      timestamp: proof.timestamp,
    });

    expect(verifier._validate_public_inputs(invalidRef.publicInputs)).toBe(false);
    await expect(verifier.verifyProof(proof)).resolves.toBe(false);
    expect(verifier.getStats()).toMatchObject({ proofs_rejected: 1 });

    verifier.resetStats();
    expect(verifier.getStats()).toMatchObject({ proofs_rejected: 0, proofs_verified: 0 });
  });

  it('runs the basic ZKP demo as a browser-native TypeScript port', async () => {
    const first = await runBasicZkpDemo({ seed: 'fixture' });
    const second = await runBasicZkpDemo({ seed: 'fixture' });

    expect(first).toMatchObject({
      axioms: ['P', 'P -> Q'],
      backend: 'simulated',
      cryptographic: false,
      module: 'logic/zkp/examples/zkp_basic_demo.py',
      runtime: 'browser-native-typescript',
      tampered_verified: false,
      theorem: 'Q',
      verified: true,
    });
    expect(first.proof.proof_data).toBe(second.proof.proof_data);
    expect(first.proof.public_inputs).toMatchObject({
      circuit_version: 1,
      ruleset_id: 'TDFOL_v1',
      theorem: 'Q',
    });
    expect(first.proof.metadata.circuit_ref).toBe('knowledge_of_axioms@1');
    expect(first.prover_stats).toMatchObject({
      cache_hits: 0,
      proofs_generated: 1,
    });
    expect(first.verifier_stats).toMatchObject({
      acceptance_rate: 0.5,
      proofs_rejected: 1,
      proofs_verified: 1,
    });
    expect(first.warnings.join(' ')).toContain('without Python');
  });

  it('keeps the Python-style basic demo alias available', async () => {
    const result = await run_basic_zkp_demo({
      axioms: ['Permit(Alice)', 'Permit(Alice) -> Access(Alice)'],
      seed: 'alias',
      theorem: 'Access(Alice)',
    });

    expect(result.verified).toBe(true);
    expect(result.proof.public_inputs.theorem).toBe('Access(Alice)');
    expect(result.proof.public_inputs.ruleset_id).toBe('TDFOL_v1');
  });
});
