import type { Groth16Proof, Groth16PublicSignals } from '../groth16';
import type { Eip1193Provider } from './ethIntegration';
import { buildVerifierReadCall, callEth } from './ethIntegration';
import { packPublicInputsForEvm, type EvmPublicInputTuple } from './evmPublicInputs';
import { keccak256Hex } from './ethVkRegistryPayloads';
export const EVM_HARNESS_METADATA = {
  pythonSource: 'logic/zkp/evm_harness.py',
  runtime: 'browser-native',
  proofSystem: 'Groth16',
  requiresPythonRuntime: false,
  allowsServerRpcFallback: false,
  providerContract: 'eip1193-injected',
} as const;
export interface EvmGroth16VerificationInput {
  verifierAddress: string;
  proof: Groth16Proof;
  publicSignals?: Groth16PublicSignals;
  publicInputs?: EvmPublicInputTuple;
}
export function encodeGroth16VerifierCalldata(options: {
  proof: Groth16Proof;
  publicInputs: Array<string>;
}): string {
  const selector = keccak256Hex('verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[])').slice(
    2,
    10,
  );
  const staticWords = [
    ...readTuple(options.proof.pi_a, 2, 'pi_a'),
    ...readTuple(options.proof.pi_b[0], 2, 'pi_b[0]'),
    ...readTuple(options.proof.pi_b[1], 2, 'pi_b[1]'),
    ...readTuple(options.proof.pi_c, 2, 'pi_c'),
    BigInt(256),
  ];
  return [
    '0x',
    selector,
    ...staticWords.map(uint256Word),
    uint256Word(options.publicInputs.length),
    ...options.publicInputs.map(fieldHexToWord),
  ].join('');
}
export async function buildEvmGroth16VerificationRequest(input: EvmGroth16VerificationInput) {
  const publicInputs =
    input.publicSignals === undefined
      ? await packRequiredPublicInputs(input.publicInputs)
      : input.publicSignals.map(signalToWordHex);
  const calldata = encodeGroth16VerifierCalldata({ proof: input.proof, publicInputs });
  return {
    calldata,
    metadata: EVM_HARNESS_METADATA,
    publicInputs,
    readCall: buildVerifierReadCall({ verifierAddress: input.verifierAddress, calldata }),
  };
}
export async function verifyGroth16ProofOnEvm(
  provider: Eip1193Provider | undefined,
  input: EvmGroth16VerificationInput,
): Promise<boolean> {
  const request = await buildEvmGroth16VerificationRequest(input);
  return decodeEvmBool(await callEth(provider, request.readCall));
}
export const encode_groth16_verifier_calldata = encodeGroth16VerifierCalldata;
export const build_evm_groth16_verification_request = buildEvmGroth16VerificationRequest;
export const verify_groth16_proof_on_evm = verifyGroth16ProofOnEvm;
async function packRequiredPublicInputs(
  input: EvmPublicInputTuple | undefined,
): Promise<Array<string>> {
  if (input === undefined) {
    throw new Error('publicInputs or publicSignals are required');
  }
  return packPublicInputsForEvm(input);
}
function readTuple(value: unknown, length: number, field: string): Array<bigint> {
  if (!Array.isArray(value) || value.length < length) {
    throw new Error(`${field} must contain ${length} field elements`);
  }
  return value.slice(0, length).map((entry, index) => scalarToBigInt(entry, `${field}[${index}]`));
}
function scalarToBigInt(value: unknown, field: string): bigint {
  if (typeof value === 'number' && Number.isInteger(value) && value >= 0) return BigInt(value);
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    if (/^0x[0-9a-f]+$/.test(normalized) || /^[0-9]+$/.test(normalized)) {
      return BigInt(normalized);
    }
  }
  throw new Error(`${field} must be a decimal or 0x-prefixed integer`);
}
function uint256Word(value: number | bigint): string {
  const bigintValue = BigInt(value);
  if (bigintValue < BigInt(0)) {
    throw new Error('uint256 value must be non-negative');
  }
  return bigintValue.toString(16).padStart(64, '0');
}
function signalToWordHex(value: unknown): string {
  return `0x${uint256Word(scalarToBigInt(value, 'publicSignals[]'))}`;
}
function fieldHexToWord(value: string): string {
  const normalized = value.trim().toLowerCase();
  if (!/^0x[0-9a-f]{64}$/.test(normalized))
    throw new Error('public input must be 32-byte 0x-prefixed hex');
  return normalized.slice(2);
}
function decodeEvmBool(value: unknown): boolean {
  if (typeof value !== 'string' || !/^0x[0-9a-f]*$/i.test(value) || value.length < 66) {
    return false;
  }
  return BigInt(`0x${value.slice(-64)}`) === BigInt(1);
}
