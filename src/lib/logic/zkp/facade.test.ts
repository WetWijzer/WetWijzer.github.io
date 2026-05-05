import { webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import type { BrowserGroth16Backend, Groth16Proof, Groth16VerificationKey } from '../groth16';
import { runBasicZkpDemo, run_basic_zkp_demo } from './basicDemo';
import { ZKPProver, ZKPVerifier } from './facade';
import { ONCHAIN_PIPELINE_METADATA, buildOnchainProofPipeline } from './onchainPipeline';
import { ZKPError, ZKPProof } from './simulatedBackend';
import {
  UCAN_ZKP_BRIDGE_METADATA,
  proveUcanDelegationZkp,
  verifyUcanDelegationZkp,
  type UcanZkpDelegation,
} from './ucanZkpBridge';

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

  it('generates batch proofs with Python-style request keys and per-item errors', async () => {
    const prover = new ZKPProver({ enableCaching: true });
    const results = await prover.generate_batch_proofs([
      { theorem: 'Q', private_axioms: ['P'], metadata: { seed: 'batch' } },
      { theorem: 'R', axioms: [] },
      { theorem: ' Q ', privateAxioms: ['P'], metadata: { seed: 'batch' } },
    ]);

    expect(results).toHaveLength(3);
    expect(results[0]).toMatchObject({ index: 0, ok: true });
    expect(results[0].proof).toBeInstanceOf(ZKPProof);
    expect(results[1]).toMatchObject({
      index: 1,
      ok: false,
      error: 'Proof generation failed: At least one axiom required',
    });
    expect(results[2]).toMatchObject({ index: 2, ok: true });
    expect(results[2].proof?.publicInputs.theorem).toBe(' Q ');
    expect(results[2].proof?.publicInputs.theorem_hash).toBe(
      results[0].proof?.publicInputs.theorem_hash,
    );
    expect(prover.get_stats()).toMatchObject({
      cache_hits: 1,
      proofs_generated: 1,
    });
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

  it('returns structured verifier results and batch failures without runtime fallbacks', async () => {
    const prover = new ZKPProver();
    const verifier = new ZKPVerifier();
    const proof = await prover.generateProof('Q', ['P']);
    const malformed = new ZKPProof({
      metadata: { ...proof.metadata },
      proofData: proof.proofData,
      publicInputs: { ...proof.publicInputs, theorem_hash: 'not-a-hash' },
      timestamp: proof.timestamp,
    });

    await expect(
      verifier.verify_proof_detailed(proof, { expected_theorem: 'Q' }),
    ).resolves.toMatchObject({
      backend: 'simulated',
      expected_theorem: 'Q',
      ok: true,
      public_inputs_valid: true,
      structure_valid: true,
      theorem: 'Q',
      verified: true,
    });

    const batch = await verifier.verify_batch_proofs([
      { proof, expected_theorem: 'Q' },
      { proof, expectedTheorem: 'R' },
      malformed,
    ]);

    expect(batch).toHaveLength(3);
    expect(batch[0]).toMatchObject({ index: 0, ok: true, verified: true });
    expect(batch[1]).toMatchObject({ index: 1, ok: false, reason: 'expected_theorem_mismatch' });
    expect(batch[2]).toMatchObject({
      index: 2,
      ok: false,
      public_inputs_valid: false,
      reason: 'invalid_public_inputs',
    });
    expect(verifier.getStats()).toMatchObject({ proofs_rejected: 2, proofs_verified: 2 });
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

  it('builds the onchain_pipeline.py browser-native proof and verifier request', async () => {
    const verificationKey: Groth16VerificationKey = { protocol: 'groth16' };
    const backend: BrowserGroth16Backend = {
      prove: async () => ({
        ok: true,
        proof: {
          pi_a: ['1', '2'],
          pi_b: [
            ['3', '4'],
            ['5', '6'],
          ],
          pi_c: ['7', '8'],
          protocol: 'groth16',
        } as Groth16Proof,
        publicSignals: ['Q'],
      }),
      verify: async () => true,
    };

    const result = await buildOnchainProofPipeline({
      backend,
      privateAxioms: ['P', 'P -> Q'],
      provider: { request: async (): Promise<string> => `0x${'1'.padStart(64, '0')}` },
      provingArtifacts: { wasm: 'wasm', zkey: 'zkey' },
      theorem: 'Q',
      verificationKey,
      verifierAddress: `0x${'ab'.repeat(20)}`,
      verifyOnchain: true,
      vkHashHex: `0x${'cd'.repeat(32)}`,
    });

    expect(ONCHAIN_PIPELINE_METADATA).toMatchObject({
      allowsServerRpcFallback: false,
      pythonSource: 'logic/zkp/onchain_pipeline.py',
      requiresPythonRuntime: false,
    });
    expect(result.metadata).toMatchObject({
      circuitId: 'legal_theorem_groth16',
      registerVkPrepared: true,
    });
    expect(result.evmPublicInputs).toHaveLength(4);
    expect(result.verifierCalldata).toMatch(/^0x[0-9a-f]+$/);
    expect(result.verifierReadCall).toMatchObject({ blockTag: 'latest' });
    expect(result.registryPayload?.vkHashBytes32).toBe(`0x${'cd'.repeat(32)}`);
    expect(result.registryCalldata).toMatch(/^0x[0-9a-f]+$/);
    expect(result.onchainVerified).toBe(true);
    await expect(
      buildOnchainProofPipeline({
        backend,
        privateAxioms: ['P'],
        provingArtifacts: { wasm: 'wasm', zkey: 'zkey' },
        theorem: 'Q',
        verifierAddress: `0x${'ab'.repeat(20)}`,
        verifyOnchain: true,
      }),
    ).rejects.toThrow('no server RPC fallback');
  });

  it('binds and verifies unsigned UCAN delegations through local ZKP proofs', async () => {
    const delegation: UcanZkpDelegation = {
      iss: 'did:key:issuer',
      aud: 'did:key:audience',
      att: [
        {
          with: 'urn:policy:tenant',
          can: 'policy/maintain',
          nb: { requirement: 'OBLIGATION', subject: 'tenant' },
        },
      ],
      prf: ['bafyproof'],
      signed: false,
    };
    const bundle = await proveUcanDelegationZkp(delegation, { theorem: 'tenant_must_maintain' });
    const verified = await verifyUcanDelegationZkp(delegation, bundle.proof!, {
      theorem: 'tenant_must_maintain',
    });
    const tampered = await verifyUcanDelegationZkp(
      { ...delegation, aud: 'did:key:other-audience' },
      bundle.proof!,
      { theorem: 'tenant_must_maintain' },
    );

    expect(UCAN_ZKP_BRIDGE_METADATA).toMatchObject({
      sourcePythonModule: 'logic/zkp/ucan_zkp_bridge.py',
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });
    expect(bundle).toMatchObject({ ok: true, verified: true, theorem: 'tenant_must_maintain' });
    expect(bundle.proof?.metadata).toMatchObject({
      audience: 'did:key:audience',
      capability_count: 1,
      circuit_ref: 'ucan_capability_binding@v1',
      issuer: 'did:key:issuer',
      ruleset_id: 'UCAN_ZKP_v1',
      source_python_module: 'logic/zkp/ucan_zkp_bridge.py',
    });
    expect(verified.ok).toBe(true);
    expect(tampered).toMatchObject({
      ok: false,
      fail_closed_reason: 'ucan_zkp_binding_verification_failed',
    });
  });

  it('fails closed for invalid UCAN ZKP bridge inputs', async () => {
    const invalid: UcanZkpDelegation = {
      iss: 'issuer',
      aud: 'did:key:audience',
      att: [{ with: 'urn:policy:tenant', can: 'policy/maintain' }],
    };

    await expect(proveUcanDelegationZkp(invalid)).resolves.toMatchObject({
      ok: false,
      fail_closed_reason: 'ucan_zkp_invalid_delegation',
    });
    await expect(
      proveUcanDelegationZkp({ ...invalid, iss: 'did:key:issuer' }, { requireSigned: true }),
    ).resolves.toMatchObject({
      ok: false,
      errors: ['signed UCAN verification is not available in this browser-native bridge.'],
    });
  });
});
