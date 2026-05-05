import { isGroth16ProvingArtifacts, isGroth16VerificationKey } from '../groth16';
import type {
  Groth16ArtifactBytes,
  Groth16BackupBackendOptions,
  Groth16ProvingArtifacts,
  Groth16VerificationKey,
} from '../groth16';

interface JsonRecord extends Record<string, unknown> {}
export interface Groth16SetupArtifactInput {
  wasm?: Groth16ArtifactBytes;
  circuitWasm?: Groth16ArtifactBytes;
  circuit_wasm?: Groth16ArtifactBytes;
  zkey?: Groth16ArtifactBytes;
  provingKey?: Groth16ArtifactBytes;
  proving_key?: Groth16ArtifactBytes;
  verificationKey?: Groth16VerificationKey | string;
  verification_key?: Groth16VerificationKey | string;
  vk?: Groth16VerificationKey | string;
  circuitId?: string;
  circuit_id?: string;
  circuitVersion?: number;
  circuit_version?: number;
  rulesetId?: string;
  ruleset_id?: string;
}
export interface Groth16SetupArtifacts {
  provingArtifacts: Groth16ProvingArtifacts;
  verificationKey: Groth16VerificationKey;
  circuitId: string;
  circuitVersion: number;
  rulesetId: string;
  metadata: {
    browser_native: true;
    python_runtime_allowed: false;
    server_calls_allowed: false;
    source_python_module: 'logic/zkp/setup_artifacts.py';
  };
}
function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
function parseInput(input: Groth16SetupArtifactInput | string): Groth16SetupArtifactInput {
  if (typeof input !== 'string') {
    if (isRecord(input)) return input;
    throw new Error('Groth16 setup artifacts must be an object');
  }
  try {
    const parsed = JSON.parse(input) as unknown;
    if (isRecord(parsed)) return parsed as Groth16SetupArtifactInput;
  } catch (error) {
    throw new Error(
      `Groth16 setup artifacts JSON could not be parsed: ${(error as Error).message}`,
    );
  }
  throw new Error('Groth16 setup artifacts JSON must be an object');
}
function isArtifactBytes(value: unknown): value is Groth16ArtifactBytes {
  return typeof value === 'string' || value instanceof Uint8Array || value instanceof ArrayBuffer;
}
function cloneArtifactBytes(value: Groth16ArtifactBytes): Groth16ArtifactBytes {
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return value.slice(0);
  return value;
}
function readArtifactBytes(
  input: Groth16SetupArtifactInput,
  keys: Array<keyof Groth16SetupArtifactInput>,
): Groth16ArtifactBytes {
  for (const key of keys) {
    const value = input[key];
    if (isArtifactBytes(value)) return cloneArtifactBytes(value);
  }
  throw new Error(`Groth16 setup artifacts missing ${keys.join('/')} bytes`);
}
function parseJson(input: string, label: string): unknown {
  try {
    return JSON.parse(input) as unknown;
  } catch (error) {
    throw new Error(`${label} JSON could not be parsed: ${(error as Error).message}`);
  }
}
function readVerificationKey(input: Groth16SetupArtifactInput): Groth16VerificationKey {
  const candidate = input.verificationKey ?? input.verification_key ?? input.vk;
  const parsed =
    typeof candidate === 'string' ? parseJson(candidate, 'Groth16 verification key') : candidate;
  if (!isGroth16VerificationKey(parsed)) {
    throw new Error('Groth16 setup artifacts missing valid verification key');
  }
  return JSON.parse(JSON.stringify(parsed)) as Groth16VerificationKey;
}
function readString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : fallback;
}
function readVersion(value: unknown): number {
  return typeof value === 'number' && Number.isInteger(value) && value > 0 ? value : 1;
}
export function prepareGroth16SetupArtifacts(
  raw: Groth16SetupArtifactInput | string,
): Groth16SetupArtifacts {
  const input = parseInput(raw);
  const provingArtifacts = {
    wasm: readArtifactBytes(input, ['wasm', 'circuitWasm', 'circuit_wasm']),
    zkey: readArtifactBytes(input, ['zkey', 'provingKey', 'proving_key']),
  };
  if (!isGroth16ProvingArtifacts(provingArtifacts)) {
    throw new Error('Groth16 setup artifacts contain invalid proving artifacts');
  }
  return {
    circuitId: readString(input.circuitId ?? input.circuit_id, 'legal_theorem_groth16'),
    circuitVersion: readVersion(input.circuitVersion ?? input.circuit_version),
    metadata: {
      browser_native: true,
      python_runtime_allowed: false,
      server_calls_allowed: false,
      source_python_module: 'logic/zkp/setup_artifacts.py',
    },
    provingArtifacts,
    rulesetId: readString(input.rulesetId ?? input.ruleset_id, 'TDFOL_v1'),
    verificationKey: readVerificationKey(input),
  };
}
export function buildGroth16BackendOptionsFromSetup(
  raw: Groth16SetupArtifactInput | string,
): Groth16BackupBackendOptions {
  const setup = prepareGroth16SetupArtifacts(raw);
  return {
    circuitId: setup.circuitId,
    circuitVersion: setup.circuitVersion,
    provingArtifacts: setup.provingArtifacts,
    rulesetId: setup.rulesetId,
    verificationKey: setup.verificationKey,
  };
}
export const setupGroth16Artifacts = prepareGroth16SetupArtifacts;
export const setup_groth16_artifacts = prepareGroth16SetupArtifacts;
export const build_groth16_backend_options_from_setup = buildGroth16BackendOptionsFromSetup;
export function loadGroth16SetupArtifacts(_path: string): never {
  throw new Error(
    'Filesystem setup artifact loading is not browser-native; pass setup artifact JSON/object instead.',
  );
}
export const load_groth16_setup_artifacts = loadGroth16SetupArtifacts;
