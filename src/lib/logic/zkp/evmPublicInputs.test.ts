import { createHash, webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import {
  BN254_FR_MODULUS,
  EVM_PUBLIC_INPUTS_METADATA,
  bytes32HexToIntModFr,
  hashTextToFieldSha256,
  intTo0x32,
  normalizeEvmPublicInputTuple,
  packManyPublicInputsForEvm,
  packPublicInputRecordForEvm,
  packPublicInputsForEvm,
  strip0x,
} from './evmPublicInputs';

Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextEncoder', {
  value: TextEncoder,
  configurable: true,
});

describe('EVM public input packing', () => {
  const theoremHashHex = '11'.repeat(32);
  const axiomsCommitmentHex = `0x${'22'.repeat(32)}`;

  it('exposes browser-native Python module metadata', () => {
    expect(EVM_PUBLIC_INPUTS_METADATA.pythonSource).toBe('logic/zkp/evm_public_inputs.py');
    expect(EVM_PUBLIC_INPUTS_METADATA.requiresPythonRuntime).toBe(false);
    expect(EVM_PUBLIC_INPUTS_METADATA.allowsServerRpcFallback).toBe(false);
  });

  it('normalizes 0x-prefixed hex and packs integers as 32-byte field elements', () => {
    expect(strip0x(' 0xAB ')).toBe('ab');
    expect(intTo0x32(2)).toBe(`0x${'0'.repeat(63)}2`);
    expect(intTo0x32(BN254_FR_MODULUS + BigInt(1))).toBe(`0x${'0'.repeat(63)}1`);
    expect(bytes32HexToIntModFr(`0x${'ff'.repeat(32)}`)).toBe(
      BigInt(`0x${'ff'.repeat(32)}`) % BN254_FR_MODULUS,
    );
  });

  it('hashes text to BN254 field elements using SHA-256', async () => {
    const digest = createHash('sha256').update('TDFOL_v1', 'utf8').digest('hex');
    const expected = `0x${(BigInt(`0x${digest}`) % BN254_FR_MODULUS).toString(16).padStart(64, '0')}`;

    await expect(hashTextToFieldSha256('TDFOL_v1')).resolves.toBe(expected);
  });

  it('packs logical public inputs into four EVM-friendly field scalars', async () => {
    const packed = await packPublicInputsForEvm({
      axiomsCommitmentHex,
      circuitVersion: 2,
      rulesetId: 'TDFOL_v1',
      theoremHashHex,
    });

    expect(packed).toHaveLength(4);
    expect(packed[0]).toBe(`0x${theoremHashHex}`);
    expect(packed[1]).toBe(`0x${'22'.repeat(32)}`);
    expect(packed[2]).toBe(`0x${'0'.repeat(63)}2`);
    expect(packed[3]).toMatch(/^0x[0-9a-f]{64}$/);
  });

  it('normalizes Python-style public input dictionaries', async () => {
    const normalized = normalizeEvmPublicInputTuple({
      axioms_commitment: axiomsCommitmentHex,
      circuit_version: BigInt(3),
      ruleset_id: 'TDFOL_v2',
      theorem_hash: theoremHashHex,
    });

    expect(normalized).toEqual({
      axiomsCommitmentHex,
      circuitVersion: BigInt(3),
      rulesetId: 'TDFOL_v2',
      theoremHashHex,
    });

    const packed = await packPublicInputRecordForEvm({
      axioms_commitment: axiomsCommitmentHex,
      circuit_version: 3,
      ruleset_id: 'TDFOL_v2',
      theorem_hash: theoremHashHex,
    });

    expect(packed[0]).toBe(`0x${theoremHashHex}`);
    expect(packed[1]).toBe(`0x${'22'.repeat(32)}`);
    expect(packed[2]).toBe(`0x${'0'.repeat(63)}3`);
    expect(packed[3]).toMatch(/^0x[0-9a-f]{64}$/);
  });

  it('packs many public input tuples in order', async () => {
    const packed = await packManyPublicInputsForEvm([
      { theoremHashHex, axiomsCommitmentHex, circuitVersion: 1, rulesetId: 'A' },
      {
        theorem_hash_hex: '33'.repeat(32),
        axioms_commitment_hex: '44'.repeat(32),
        circuit_version: BigInt(2),
        ruleset_id: 'B',
      },
    ]);

    expect(packed).toHaveLength(2);
    expect(packed[0][2]).toBe(`0x${'0'.repeat(63)}1`);
    expect(packed[1][0]).toBe(
      `0x${(BigInt(`0x${'33'.repeat(32)}`) % BN254_FR_MODULUS).toString(16).padStart(64, '0')}`,
    );
  });

  it('rejects malformed values like the Python helper', async () => {
    expect(() => intTo0x32(-1)).toThrow('non-negative');
    expect(() => bytes32HexToIntModFr('abc')).toThrow('expected 32-byte hex string');
    expect(() => bytes32HexToIntModFr(`${'zz'.repeat(32)}`)).toThrow('invalid hex');
    await expect(
      packPublicInputsForEvm({
        axiomsCommitmentHex,
        circuitVersion: -1,
        rulesetId: 'TDFOL_v1',
        theoremHashHex,
      }),
    ).rejects.toThrow('circuit_version must be non-negative');
    await expect(
      packPublicInputsForEvm({
        axiomsCommitmentHex,
        circuitVersion: BN254_FR_MODULUS,
        rulesetId: 'TDFOL_v1',
        theoremHashHex,
      }),
    ).rejects.toThrow('circuit_version must be < BN254_FR_MODULUS');
    expect(() =>
      normalizeEvmPublicInputTuple({
        axioms_commitment_hex: axiomsCommitmentHex,
        circuit_version: 1.5,
        ruleset_id: 'TDFOL_v1',
        theorem_hash_hex: theoremHashHex,
      }),
    ).toThrow('circuit_version must be int');
    expect(() =>
      normalizeEvmPublicInputTuple({
        axioms_commitment_hex: axiomsCommitmentHex,
        circuit_version: 1,
        ruleset_id: '',
        theorem_hash_hex: theoremHashHex,
      }),
    ).toThrow('ruleset_id must be non-empty');
  });
});
