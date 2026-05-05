import type { BrowserNativeZkpBackendProtocol } from './zkp/backendProtocol';
import { axiomsCommitmentHex, theoremHashHex } from './zkp/canonicalization';
import { ZKPProof } from './zkp/simulatedBackend';

export type Groth16JsonScalar = string | number | boolean | null;
export type Groth16JsonValue =
  | Groth16JsonScalar
  | Groth16JsonValue[]
  | { [key: string]: Groth16JsonValue | undefined };
export type Groth16PublicSignals = Groth16JsonScalar[];
export type Groth16ArtifactBytes = Uint8Array | ArrayBuffer | string;
export type Groth16WitnessInput = { [key: string]: Groth16JsonValue | undefined };

export interface Groth16Proof {
  pi_a: Groth16JsonValue[];
  pi_b: Groth16JsonValue[][];
  pi_c: Groth16JsonValue[];
  protocol?: string;
  curve?: string;
  [key: string]: Groth16JsonValue | undefined;
}

export interface Groth16VerificationKey {
  protocol?: string;
  curve?: string;
  vk_alpha_1?: Groth16JsonValue;
  vk_beta_2?: Groth16JsonValue;
  vk_gamma_2?: Groth16JsonValue;
  vk_delta_2?: Groth16JsonValue;
  IC?: Groth16JsonValue[];
  [key: string]: Groth16JsonValue | undefined;
}

export interface Groth16ProvingArtifacts {
  wasm: Groth16ArtifactBytes;
  zkey: Groth16ArtifactBytes;
}

export interface Groth16ProvingSuccess {
  ok: true;
  proof: Groth16Proof;
  publicSignals: Groth16PublicSignals;
}

export interface Groth16ProvingFailure {
  ok: false;
  error: string;
}

export type Groth16ProvingResult = Groth16ProvingSuccess | Groth16ProvingFailure;

export interface BrowserGroth16Backend {
  verify: (
    verificationKey: Groth16VerificationKey,
    publicSignals: Groth16PublicSignals,
    proof: Groth16Proof,
  ) => unknown;
  prove?: (artifacts: Groth16ProvingArtifacts, input: Groth16WitnessInput) => unknown;
}

export interface Groth16Adapter {
  supportsVerification: boolean;
  supportsProving: boolean;
  verify: (verificationKey: unknown, publicSignals: unknown, proof: unknown) => Promise<boolean>;
  prove: (artifacts: unknown, input: unknown) => Promise<Groth16ProvingResult>;
}

export interface Groth16BackupBackendOptions {
  backend?: BrowserGroth16Backend;
  provingArtifacts?: Groth16ProvingArtifacts;
  verificationKey?: Groth16VerificationKey;
  circuitId?: string;
  circuitVersion?: number;
  rulesetId?: string;
}

export interface Groth16BackupBackendMetadata {
  sourcePythonModule: 'logic/zkp/backends/groth16_backup.py';
  backendId: 'groth16_backup';
  proofSystem: 'Groth16';
  browserNative: true;
  serverCallsAllowed: false;
  pythonRuntimeAllowed: false;
  requiresInjectedWasmBackend: true;
}

export const GROTH16_BACKUP_BACKEND_METADATA: Groth16BackupBackendMetadata = {
  backendId: 'groth16_backup',
  browserNative: true,
  proofSystem: 'Groth16',
  pythonRuntimeAllowed: false,
  requiresInjectedWasmBackend: true,
  serverCallsAllowed: false,
  sourcePythonModule: 'logic/zkp/backends/groth16_backup.py',
};

function isObject(value: unknown): value is { [key: string]: unknown } {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isScalar(value: unknown): value is Groth16JsonScalar {
  return (
    value === null ||
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  );
}

function isJsonValue(value: unknown): value is Groth16JsonValue {
  if (isScalar(value)) {
    return true;
  }

  if (Array.isArray(value)) {
    return value.every(isJsonValue);
  }

  if (!isObject(value)) {
    return false;
  }

  return Object.keys(value).every((key) => value[key] === undefined || isJsonValue(value[key]));
}

function isJsonArray(value: unknown): value is Groth16JsonValue[] {
  return Array.isArray(value) && value.every(isJsonValue);
}

function isNestedJsonArray(value: unknown): value is Groth16JsonValue[][] {
  return Array.isArray(value) && value.every(isJsonArray);
}

export function isGroth16Proof(value: unknown): value is Groth16Proof {
  if (!isObject(value)) {
    return false;
  }

  return (
    isJsonArray(value.pi_a) &&
    value.pi_a.length >= 2 &&
    isNestedJsonArray(value.pi_b) &&
    value.pi_b.length >= 2 &&
    isJsonArray(value.pi_c) &&
    value.pi_c.length >= 2 &&
    (value.protocol === undefined || value.protocol === 'groth16') &&
    (value.curve === undefined || typeof value.curve === 'string')
  );
}

export function isGroth16PublicSignals(value: unknown): value is Groth16PublicSignals {
  return Array.isArray(value) && value.every(isScalar);
}

export function isGroth16VerificationKey(value: unknown): value is Groth16VerificationKey {
  if (!isObject(value)) {
    return false;
  }

  const hasProtocol = value.protocol === 'groth16';
  const hasSnarkJsShape =
    isJsonValue(value.vk_alpha_1) &&
    isJsonValue(value.vk_beta_2) &&
    isJsonValue(value.vk_gamma_2) &&
    isJsonValue(value.vk_delta_2) &&
    isJsonArray(value.IC);

  return (
    (hasProtocol || hasSnarkJsShape) &&
    (value.curve === undefined || typeof value.curve === 'string')
  );
}

function isArtifactBytes(value: unknown): value is Groth16ArtifactBytes {
  return typeof value === 'string' || value instanceof Uint8Array || value instanceof ArrayBuffer;
}

export function isGroth16ProvingArtifacts(value: unknown): value is Groth16ProvingArtifacts {
  return isObject(value) && isArtifactBytes(value.wasm) && isArtifactBytes(value.zkey);
}

export function isGroth16WitnessInput(value: unknown): value is Groth16WitnessInput {
  if (!isObject(value)) {
    return false;
  }

  return Object.keys(value).every((key) => value[key] === undefined || isJsonValue(value[key]));
}

function normalizeProvingResult(value: unknown): Groth16ProvingResult {
  if (
    !isObject(value) ||
    !isGroth16Proof(value.proof) ||
    !isGroth16PublicSignals(value.publicSignals)
  ) {
    return { ok: false, error: 'groth16_backend_returned_invalid_result' };
  }

  return { ok: true, proof: value.proof, publicSignals: value.publicSignals };
}

export function createGroth16Adapter(backend?: BrowserGroth16Backend): Groth16Adapter {
  return {
    supportsVerification: typeof backend?.verify === 'function',
    supportsProving: typeof backend?.prove === 'function',

    async verify(verificationKey: unknown, publicSignals: unknown, proof: unknown) {
      if (
        !backend ||
        !isGroth16VerificationKey(verificationKey) ||
        !isGroth16PublicSignals(publicSignals) ||
        !isGroth16Proof(proof)
      ) {
        return false;
      }

      try {
        return (await backend.verify(verificationKey, publicSignals, proof)) === true;
      } catch {
        return false;
      }
    },

    async prove(artifacts: unknown, input: unknown) {
      if (!backend?.prove) {
        return { ok: false, error: 'groth16_proving_backend_unavailable' };
      }

      if (!isGroth16ProvingArtifacts(artifacts)) {
        return { ok: false, error: 'groth16_invalid_proving_artifacts' };
      }

      if (!isGroth16WitnessInput(input)) {
        return { ok: false, error: 'groth16_invalid_witness_input' };
      }

      try {
        return normalizeProvingResult(await backend.prove(artifacts, input));
      } catch {
        return { ok: false, error: 'groth16_backend_proving_failed' };
      }
    },
  };
}

export class Groth16BackupBackend implements BrowserNativeZkpBackendProtocol {
  readonly backendId = 'groth16_backup';
  readonly backend_id = 'groth16_backup';

  private readonly adapter: Groth16Adapter;
  private readonly provingArtifacts?: Groth16ProvingArtifacts;
  private readonly verificationKey?: Groth16VerificationKey;
  private readonly circuitId: string;
  private readonly circuitVersion: number;
  private readonly rulesetId: string;

  constructor(options: Groth16BackupBackendOptions = {}) {
    this.adapter = createGroth16Adapter(options.backend);
    this.provingArtifacts = options.provingArtifacts;
    this.verificationKey = options.verificationKey;
    this.circuitId = options.circuitId ?? 'legal_theorem_groth16';
    this.circuitVersion = options.circuitVersion ?? 1;
    this.rulesetId = options.rulesetId ?? 'TDFOL_v1';
  }

  async generateProof(
    theorem: string,
    privateAxioms: string[],
    metadata: Record<string, unknown> = {},
  ): Promise<ZKPProof> {
    if (!theorem) {
      throw new Error('Theorem cannot be empty');
    }
    if (privateAxioms.length === 0) {
      throw new Error('At least one axiom required');
    }

    const artifacts = readProvingArtifacts(metadata) ?? this.provingArtifacts;
    const provingResult = await this.adapter.prove(artifacts, {
      axioms: privateAxioms,
      metadata: metadata as Groth16WitnessInput,
      theorem,
    });

    if (!provingResult.ok) {
      throw new Error(`Groth16 proof generation failed: ${provingResult.error}`);
    }

    const publicInputs: Record<string, unknown> = {
      axioms_commitment: await axiomsCommitmentHex(privateAxioms),
      circuit_ref: `${this.circuitId}@v${this.circuitVersion}`,
      circuit_version: this.circuitVersion,
      groth16_public_signals: [...provingResult.publicSignals],
      ruleset_id: this.rulesetId,
      theorem,
      theorem_hash: await theoremHashHex(theorem),
    };

    return new ZKPProof({
      metadata: {
        ...metadata,
        backend: this.backendId,
        browser_native: true,
        groth16_proof: cloneJson(provingResult.proof),
        proof_system: 'Groth16',
        source_python_module: GROTH16_BACKUP_BACKEND_METADATA.sourcePythonModule,
      },
      proofData: encodeProofPayload(provingResult.proof, provingResult.publicSignals),
      publicInputs,
      timestamp: Date.now() / 1000,
    });
  }

  generate_proof(
    theorem: string,
    privateAxioms: string[],
    metadata: Record<string, unknown> = {},
  ): Promise<ZKPProof> {
    return this.generateProof(theorem, privateAxioms, metadata);
  }

  async verifyProof(proof: ZKPProof): Promise<boolean> {
    const verificationKey = readVerificationKey(proof.metadata) ?? this.verificationKey;
    const groth16Proof =
      readGroth16Proof(proof.metadata) ?? decodeProofPayload(proof.proofData)?.proof;
    const publicSignals =
      readPublicSignals(proof.publicInputs.groth16_public_signals) ??
      decodeProofPayload(proof.proofData)?.publicSignals;

    return this.adapter.verify(verificationKey, publicSignals, groth16Proof);
  }

  verify_proof(proof: ZKPProof): Promise<boolean> {
    return this.verifyProof(proof);
  }
}

export function createGroth16BackupBackend(
  options: Groth16BackupBackendOptions = {},
): Groth16BackupBackend {
  return new Groth16BackupBackend(options);
}

export const create_groth16_backup_backend = createGroth16BackupBackend;

export async function verifyGroth16Proof(
  verificationKey: unknown,
  publicSignals: unknown,
  proof: unknown,
  backend?: BrowserGroth16Backend,
) {
  return createGroth16Adapter(backend).verify(verificationKey, publicSignals, proof);
}

export async function proveGroth16(
  artifacts: unknown,
  input: unknown,
  backend?: BrowserGroth16Backend,
) {
  return createGroth16Adapter(backend).prove(artifacts, input);
}

function readProvingArtifacts(
  record: Record<string, unknown>,
): Groth16ProvingArtifacts | undefined {
  const candidate = record.groth16_proving_artifacts ?? record.provingArtifacts;
  return isGroth16ProvingArtifacts(candidate) ? candidate : undefined;
}

function readVerificationKey(record: Record<string, unknown>): Groth16VerificationKey | undefined {
  const candidate = record.groth16_verification_key ?? record.verificationKey;
  return isGroth16VerificationKey(candidate) ? candidate : undefined;
}

function readGroth16Proof(record: Record<string, unknown>): Groth16Proof | undefined {
  const candidate = record.groth16_proof ?? record.proof;
  return isGroth16Proof(candidate) ? candidate : undefined;
}

function readPublicSignals(value: unknown): Groth16PublicSignals | undefined {
  return isGroth16PublicSignals(value) ? value : undefined;
}

function encodeProofPayload(proof: Groth16Proof, publicSignals: Groth16PublicSignals): Uint8Array {
  return new TextEncoder().encode(JSON.stringify({ proof, publicSignals }));
}

function decodeProofPayload(
  proofData: Uint8Array,
): { proof: Groth16Proof; publicSignals: Groth16PublicSignals } | undefined {
  try {
    const decoded = JSON.parse(new TextDecoder().decode(proofData)) as unknown;
    if (
      isObject(decoded) &&
      isGroth16Proof(decoded.proof) &&
      isGroth16PublicSignals(decoded.publicSignals)
    ) {
      return { proof: decoded.proof, publicSignals: decoded.publicSignals };
    }
  } catch {
    return undefined;
  }

  return undefined;
}

function cloneJson<T extends Groth16JsonValue>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}
