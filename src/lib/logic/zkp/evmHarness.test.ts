import { webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import type { Groth16Proof } from '../groth16';
import {
  EVM_HARNESS_METADATA,
  buildEvmGroth16VerificationRequest,
  encodeGroth16VerifierCalldata,
  verifyGroth16ProofOnEvm,
} from './evmHarness';

Object.defineProperty(globalThis, 'crypto', { value: webcrypto, configurable: true });
Object.defineProperty(globalThis, 'TextEncoder', { value: TextEncoder, configurable: true });

describe('EVM Groth16 harness', () => {
  const verifierAddress = `0x${'ab'.repeat(20)}`;
  const proof: Groth16Proof = {
    pi_a: ['1', '2', '1'],
    pi_b: [
      ['3', '4'],
      ['5', '6'],
      ['1', '0'],
    ],
    pi_c: ['7', '8', '1'],
    protocol: 'groth16',
  };

  it('declares and ABI-encodes the evm_harness.py browser-native contract', () => {
    expect(EVM_HARNESS_METADATA.pythonSource).toBe('logic/zkp/evm_harness.py');
    expect(EVM_HARNESS_METADATA.allowsServerRpcFallback).toBe(false);
    const calldata = encodeGroth16VerifierCalldata({
      proof,
      publicInputs: [`0x${'09'.padStart(64, '0')}`, `0x${'0a'.padStart(64, '0')}`],
    });
    expect(calldata).toMatch(/^0x[0-9a-f]{8}/);
    expect(calldata).toContain((8 * 32).toString(16).padStart(64, '0'));
    expect(calldata.endsWith(`${'09'.padStart(64, '0')}${'0a'.padStart(64, '0')}`)).toBe(true);
  });

  it('packs logical public inputs and delegates eth_call only to an injected provider', async () => {
    const request = await buildEvmGroth16VerificationRequest({
      proof,
      publicInputs: {
        axiomsCommitmentHex: `0x${'22'.repeat(32)}`,
        circuitVersion: 2,
        rulesetId: 'TDFOL_v1',
        theoremHashHex: '11'.repeat(32),
      },
      verifierAddress,
    });
    expect(request.publicInputs).toHaveLength(4);
    expect(request.readCall).toEqual({
      blockTag: 'latest',
      data: request.calldata,
      to: verifierAddress,
    });

    const calls: Array<{ method: string; params?: Array<unknown> }> = [];
    const provider = {
      request: async (args: { method: string; params?: Array<unknown> }): Promise<string> => {
        calls.push(args);
        return `0x${'1'.padStart(64, '0')}`;
      },
    };
    await expect(
      verifyGroth16ProofOnEvm(provider, { proof, publicSignals: ['9', '10'], verifierAddress }),
    ).resolves.toBe(true);
    expect(calls[0].method).toBe('eth_call');
    await expect(
      verifyGroth16ProofOnEvm(undefined, { proof, publicSignals: ['9'], verifierAddress }),
    ).rejects.toThrow('no server RPC fallback');
  });

  it('rejects malformed proof and public input shapes', () => {
    expect(() =>
      encodeGroth16VerifierCalldata({ proof: { ...proof, pi_a: ['nope'] }, publicInputs: [] }),
    ).toThrow('pi_a');
    expect(() => encodeGroth16VerifierCalldata({ proof, publicInputs: ['0x1234'] })).toThrow(
      '32-byte',
    );
  });
});
