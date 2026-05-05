import { BN254_FIELD_MODULUS } from './canonicalization';

export const BN254_FR_MODULUS = BN254_FIELD_MODULUS;

export const EVM_PUBLIC_INPUTS_METADATA = {
  pythonSource: 'logic/zkp/evm_public_inputs.py',
  runtime: 'browser-native',
  curve: 'BN254',
  hash: 'SHA-256',
  requiresPythonRuntime: false,
  allowsServerRpcFallback: false,
} as const;

export interface EvmPublicInputTuple {
  theoremHashHex: string;
  axiomsCommitmentHex: string;
  circuitVersion: number | bigint;
  rulesetId: string;
}

export interface EvmPublicInputRecord {
  theorem_hash_hex?: string;
  theoremHashHex?: string;
  theorem_hash?: string;
  theoremHash?: string;
  axioms_commitment_hex?: string;
  axiomsCommitmentHex?: string;
  axioms_commitment?: string;
  axiomsCommitment?: string;
  circuit_version?: number | bigint;
  circuitVersion?: number | bigint;
  ruleset_id?: string;
  rulesetId?: string;
}

export function strip0x(hexString: string): string {
  const value = String(hexString).trim().toLowerCase();
  return value.startsWith('0x') ? value.slice(2) : value;
}

export function intTo0x32(value: number | bigint): string {
  if (typeof value !== 'number' && typeof value !== 'bigint') {
    throw new TypeError('value must be int');
  }
  const intValue = BigInt(value);
  if (intValue < BigInt(0)) {
    throw new Error('value must be non-negative');
  }
  const reduced = intValue % BN254_FR_MODULUS;
  return `0x${reduced.toString(16).padStart(64, '0')}`;
}

export function bytes32HexToIntModFr(bytes32Hex: string): bigint {
  const value = strip0x(bytes32Hex);
  if (value.length !== 64) {
    throw new Error('expected 32-byte hex string');
  }
  if (!/^[0-9a-f]+$/.test(value)) {
    throw new Error('invalid hex');
  }
  return BigInt(`0x${value}`) % BN254_FR_MODULUS;
}

export function normalizeEvmPublicInputTuple(
  input: EvmPublicInputTuple | EvmPublicInputRecord,
): EvmPublicInputTuple {
  if (!input || typeof input !== 'object') {
    throw new TypeError('public input must be an object');
  }
  const record = input as EvmPublicInputRecord;
  const theoremHashHex =
    record.theoremHashHex ?? record.theorem_hash_hex ?? record.theoremHash ?? record.theorem_hash;
  const axiomsCommitmentHex =
    record.axiomsCommitmentHex ??
    record.axioms_commitment_hex ??
    record.axiomsCommitment ??
    record.axioms_commitment;
  const circuitVersion = record.circuitVersion ?? record.circuit_version;
  const rulesetId = record.rulesetId ?? record.ruleset_id;
  if (typeof theoremHashHex !== 'string') {
    throw new TypeError('theorem_hash_hex must be str');
  }
  if (typeof axiomsCommitmentHex !== 'string') {
    throw new TypeError('axioms_commitment_hex must be str');
  }
  if (typeof circuitVersion !== 'number' && typeof circuitVersion !== 'bigint') {
    throw new TypeError('circuit_version must be int');
  }
  if (typeof circuitVersion === 'number' && !Number.isInteger(circuitVersion)) {
    throw new TypeError('circuit_version must be int');
  }
  if (typeof rulesetId !== 'string') {
    throw new TypeError('ruleset_id must be str');
  }
  if (rulesetId.length === 0) {
    throw new Error('ruleset_id must be non-empty');
  }
  return {
    axiomsCommitmentHex,
    circuitVersion,
    rulesetId,
    theoremHashHex,
  };
}

export async function hashTextToFieldSha256(text: string): Promise<string> {
  if (typeof text !== 'string') {
    throw new TypeError('text must be str');
  }
  const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return intTo0x32(BigInt(`0x${bytesToHex(new Uint8Array(digest))}`));
}

export async function packPublicInputsForEvm(
  input: EvmPublicInputTuple | EvmPublicInputRecord,
): Promise<string[]> {
  const normalized = normalizeEvmPublicInputTuple(input);
  const circuitVersion = BigInt(normalized.circuitVersion);
  if (circuitVersion < BigInt(0)) {
    throw new Error('circuit_version must be non-negative');
  }
  if (circuitVersion >= BN254_FR_MODULUS) {
    throw new Error('circuit_version must be < BN254_FR_MODULUS');
  }

  return [
    intTo0x32(bytes32HexToIntModFr(normalized.theoremHashHex)),
    intTo0x32(bytes32HexToIntModFr(normalized.axiomsCommitmentHex)),
    intTo0x32(circuitVersion),
    await hashTextToFieldSha256(normalized.rulesetId),
  ];
}

export function pack_public_inputs_for_evm(options: {
  theorem_hash_hex: string;
  axioms_commitment_hex: string;
  circuit_version: number | bigint;
  ruleset_id: string;
}): Promise<string[]> {
  return packPublicInputsForEvm({
    axiomsCommitmentHex: options.axioms_commitment_hex,
    circuitVersion: options.circuit_version,
    rulesetId: options.ruleset_id,
    theoremHashHex: options.theorem_hash_hex,
  });
}

export async function packPublicInputRecordForEvm(input: EvmPublicInputRecord): Promise<string[]> {
  return packPublicInputsForEvm(input);
}

export const pack_public_input_record_for_evm = packPublicInputRecordForEvm;

export async function packManyPublicInputsForEvm(
  inputs: Iterable<EvmPublicInputTuple | EvmPublicInputRecord>,
): Promise<string[][]> {
  const packed: string[][] = [];
  for (const input of inputs) {
    packed.push(await packPublicInputsForEvm(input));
  }
  return packed;
}

export function pack_many_public_inputs_for_evm(
  inputs: Iterable<[string, string, number | bigint, string]>,
): Promise<string[][]> {
  return packManyPublicInputsForEvm(
    [...inputs].map(([theoremHashHex, axiomsCommitmentHex, circuitVersion, rulesetId]) => ({
      axiomsCommitmentHex,
      circuitVersion,
      rulesetId,
      theoremHashHex,
    })),
  );
}

function bytesToHex(bytes: Uint8Array): string {
  return [...bytes].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}
