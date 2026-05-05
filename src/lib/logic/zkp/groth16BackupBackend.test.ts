import { webcrypto } from 'node:crypto';
import { TextDecoder, TextEncoder } from 'node:util';

import {
  GROTH16_BACKUP_BACKEND_METADATA,
  createGroth16BackupBackend,
  create_groth16_backup_backend,
} from './index';
import type { BrowserGroth16Backend, Groth16Proof, Groth16VerificationKey } from '../groth16';

Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextEncoder', {
  value: TextEncoder,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextDecoder', {
  value: TextDecoder,
  configurable: true,
});

const proof: Groth16Proof = {
  pi_a: ['1', '2', '1'],
  pi_b: [
    ['3', '4'],
    ['5', '6'],
  ],
  pi_c: ['7', '8', '1'],
  protocol: 'groth16',
};

const verificationKey: Groth16VerificationKey = {
  protocol: 'groth16',
};

describe('Groth16 backup backend', () => {
  it('is exported from the ZKP barrel with browser-native metadata', () => {
    const backend = create_groth16_backup_backend();

    expect(backend.backendId).toBe('groth16_backup');
    expect(GROTH16_BACKUP_BACKEND_METADATA).toEqual({
      backendId: 'groth16_backup',
      browserNative: true,
      proofSystem: 'Groth16',
      pythonRuntimeAllowed: false,
      requiresInjectedWasmBackend: true,
      serverCallsAllowed: false,
      sourcePythonModule: 'logic/zkp/backends/groth16_backup.py',
    });
  });

  it('wraps injected local Groth16 proving and verification without server fallback', async () => {
    const groth16: BrowserGroth16Backend = {
      prove: async (_artifacts, input) => ({
        ok: true,
        proof,
        publicSignals: [String(input.theorem)],
      }),
      verify: async (vk, publicSignals, candidateProof) =>
        vk === verificationKey &&
        publicSignals[0] === 'Q' &&
        JSON.stringify(candidateProof) === JSON.stringify(proof),
    };
    const backend = createGroth16BackupBackend({
      backend: groth16,
      provingArtifacts: { wasm: 'wasm-bytes', zkey: 'zkey-bytes' },
      verificationKey,
    });

    const zkpProof = await backend.generateProof('Q', ['P', 'P -> Q']);

    expect(zkpProof.metadata).toMatchObject({
      backend: 'groth16_backup',
      browser_native: true,
      groth16_proof: proof,
      proof_system: 'Groth16',
    });
    expect(zkpProof.publicInputs).toMatchObject({
      circuit_ref: 'legal_theorem_groth16@v1',
      groth16_public_signals: ['Q'],
      theorem: 'Q',
    });
    await expect(backend.verifyProof(zkpProof)).resolves.toBe(true);
  });

  it('fails closed when local Groth16 dependencies are missing or malformed', async () => {
    const backend = createGroth16BackupBackend();

    await expect(backend.generateProof('Q', ['P'])).rejects.toThrow(
      'groth16_proving_backend_unavailable',
    );

    const malformedVerifier = createGroth16BackupBackend({
      backend: {
        verify: async () => true,
      },
    });
    const zkpProof = await createGroth16BackupBackend({
      backend: {
        prove: async () => ({ ok: true, proof, publicSignals: ['Q'] }),
        verify: async () => true,
      },
      provingArtifacts: { wasm: 'wasm-bytes', zkey: 'zkey-bytes' },
    }).generateProof('Q', ['P']);

    await expect(malformedVerifier.verifyProof(zkpProof)).resolves.toBe(false);
  });
});
