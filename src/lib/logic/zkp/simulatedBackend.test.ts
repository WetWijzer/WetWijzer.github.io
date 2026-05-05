import { webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import {
  SimulatedBackend,
  ZKPError,
  ZKPProof,
  backendIsAvailable,
  clearBackendCache,
  getBackend,
  listBackends,
} from './simulatedBackend';
import {
  BACKEND_PROTOCOL_METADATA,
  assertBackendProtocol,
  backendSatisfiesProtocol,
  describeBackendProtocol,
  validateBackendProtocol,
} from './backendProtocol';

Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextEncoder', {
  value: TextEncoder,
  configurable: true,
});

describe('browser-native simulated ZKP backend', () => {
  beforeEach(() => {
    clearBackendCache();
  });

  it('serializes simulated proof dataclasses with Python-compatible field names', () => {
    const proof = new ZKPProof({
      metadata: { proof_system: 'Groth16 (simulated)' },
      proofData: [0, 1, 2, 255],
      publicInputs: { theorem: 'Q' },
      timestamp: 123,
    });

    const serialized = proof.toDict();

    expect(serialized).toEqual({
      metadata: { proof_system: 'Groth16 (simulated)' },
      proof_data: '000102ff',
      public_inputs: { theorem: 'Q' },
      size_bytes: 4,
      timestamp: 123,
    });
    expect(ZKPProof.fromDict(serialized).toDict()).toEqual(serialized);
    expect(() => ZKPProof.fromDict({ ...serialized, proof_data: 'abc' })).toThrow('proof_data');
  });

  it('generates and verifies simulated 160-byte proofs without cryptographic claims', async () => {
    const backend = new SimulatedBackend();
    const proof = await backend.generateProof('Q', ['P', 'P -> Q'], { circuit_version: 2 });

    expect(proof.proofData.byteLength).toBe(160);
    expect(proof.toDict().proof_data.startsWith('53494d5a4b500001')).toBe(true);
    expect(proof.publicInputs).toMatchObject({
      circuit_version: 2,
      ruleset_id: 'TDFOL_v1',
      theorem: 'Q',
    });
    expect(proof.metadata).toMatchObject({
      num_axioms: 2,
      proof_system: 'Groth16 (simulated)',
    });
    expect(proof.metadata.simulated_proof_layout).toMatchObject({
      byte_length: 160,
      format: 'SIMZKP/1',
      magic_hex: '53494d5a4b500001',
    });
    await expect(backend.verifyProof(proof)).resolves.toBe(true);
  });

  it('fails closed for malformed proofs and invalid proof requests', async () => {
    const backend = new SimulatedBackend();
    await expect(backend.generateProof('', ['P'])).rejects.toThrow(ZKPError);
    await expect(backend.generateProof('Q', [])).rejects.toThrow('At least one axiom required');

    const proof = await backend.generateProof('Q', ['P']);
    const wrongHashProof = new ZKPProof({
      metadata: proof.metadata,
      proofData: proof.proofData,
      publicInputs: { ...proof.publicInputs, theorem_hash: '00' },
      timestamp: proof.timestamp,
    });
    const missingSystemProof = new ZKPProof({
      metadata: {},
      proofData: proof.proofData,
      publicInputs: proof.publicInputs,
      timestamp: proof.timestamp,
    });

    await expect(backend.verifyProof(wrongHashProof)).resolves.toBe(false);
    await expect(backend.verifyProof(missingSystemProof)).resolves.toBe(false);
  });

  it('exposes browser-native backend registry semantics', () => {
    const simulated = getBackend('sim');

    expect(simulated).toBe(getBackend('simulated'));
    expect(listBackends()).toMatchObject({
      groth16: { curve: 'bn254' },
      simulated: { curve: 'simulation' },
    });
    expect(backendIsAvailable('simulated')).toBe(true);
    expect(backendIsAvailable('groth16')).toBe(false);
    expect(() => getBackend('unknown')).toThrow('Unknown ZKP backend');
    expect(() => getBackend('groth16')).toThrow('browser-native WASM');
  });

  it('ports the Python backend_protocol contract as a fail-closed browser-native validator', () => {
    const backend = new SimulatedBackend();

    expect(BACKEND_PROTOCOL_METADATA).toEqual({
      browserNative: true,
      pythonRuntimeAllowed: false,
      requiredMethods: ['generateProof', 'verifyProof'],
      serverCallsAllowed: false,
      sourcePythonModule: 'logic/zkp/backends/backend_protocol.py',
    });
    expect(backendSatisfiesProtocol(backend)).toBe(true);
    expect(validateBackendProtocol(backend)).toMatchObject({
      backendId: 'simulated',
      errors: [],
      ok: true,
    });
    expect(
      describeBackendProtocol({ backend_id: 'legacy', generateProof: async () => undefined }),
    ).toMatchObject({
      backendId: 'legacy',
      errors: ['verifyProof must be a function'],
      ok: false,
    });
    expect(() =>
      assertBackendProtocol({ backendId: 'broken', verifyProof: async () => false }),
    ).toThrow('generateProof must be a function');
  });
});
