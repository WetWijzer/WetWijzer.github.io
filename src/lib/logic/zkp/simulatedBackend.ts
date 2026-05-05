import { axiomsCommitmentHex, normalizeProofText, theoremHashHex } from './canonicalization';
import type { BrowserNativeZkpBackendProtocol } from './backendProtocol';

const SIMULATED_MAGIC = new Uint8Array([0x53, 0x49, 0x4d, 0x5a, 0x4b, 0x50, 0x00, 0x01]);

export class ZKPError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ZKPError';
  }
}

export interface ZKPProofDict {
  proof_data: string;
  public_inputs: Record<string, unknown>;
  metadata: Record<string, unknown>;
  timestamp: number;
  size_bytes: number;
}

export class ZKPProof {
  readonly proofData: Uint8Array;
  readonly publicInputs: Record<string, unknown>;
  readonly metadata: Record<string, unknown>;
  readonly timestamp: number;
  readonly sizeBytes: number;

  constructor(input: {
    proofData: Uint8Array | number[];
    publicInputs: Record<string, unknown>;
    metadata: Record<string, unknown>;
    timestamp: number;
    sizeBytes?: number;
  }) {
    this.proofData =
      input.proofData instanceof Uint8Array
        ? new Uint8Array(input.proofData)
        : new Uint8Array(input.proofData);
    this.publicInputs = { ...input.publicInputs };
    this.metadata = { ...input.metadata };
    this.timestamp = input.timestamp;
    this.sizeBytes = input.sizeBytes ?? this.proofData.byteLength;
  }

  toDict(): ZKPProofDict {
    return {
      metadata: { ...this.metadata },
      proof_data: bytesToHex(this.proofData),
      public_inputs: { ...this.publicInputs },
      size_bytes: this.sizeBytes,
      timestamp: this.timestamp,
    };
  }

  to_dict(): ZKPProofDict {
    return this.toDict();
  }

  static fromDict(data: ZKPProofDict): ZKPProof {
    return new ZKPProof({
      metadata: data.metadata,
      proofData: hexToBytes(data.proof_data),
      publicInputs: data.public_inputs,
      sizeBytes: data.size_bytes,
      timestamp: data.timestamp,
    });
  }

  static from_dict(data: ZKPProofDict): ZKPProof {
    return ZKPProof.fromDict(data);
  }
}

export type SimulatedZKPProof = ZKPProof;

export interface ZKBackend extends BrowserNativeZkpBackendProtocol {
  backendId: string;
  generateProof(
    theorem: string,
    privateAxioms: Array<string>,
    metadata?: Record<string, unknown>,
  ): Promise<ZKPProof>;
  verifyProof(proof: ZKPProof): Promise<boolean>;
}

export interface SimulatedProofLayoutSegment {
  tag: string;
  offset: number;
  length: number;
  description?: string;
}

export interface SimulatedProofLayoutMetadata {
  format: 'SIMZKP/1';
  byte_length: 160;
  magic_hex: string;
  segments: SimulatedProofLayoutSegment[];
}

export class SimulatedBackend implements ZKBackend {
  readonly backendId = 'simulated';
  readonly backend_id = 'simulated';

  simulatedProofLayoutMetadata(): SimulatedProofLayoutMetadata {
    return {
      byte_length: 160,
      format: 'SIMZKP/1',
      magic_hex: bytesToHex(SIMULATED_MAGIC),
      segments: [
        { length: 8, offset: 0, tag: 'magic' },
        {
          description: 'SHA256(circuit_hash || witness || normalize_text(theorem))',
          length: 32,
          offset: 8,
          tag: 'proof_hash',
        },
        {
          description: 'SHA256(circuit metadata derived from theorem + axioms)',
          length: 32,
          offset: 40,
          tag: 'circuit_hash',
        },
        {
          description: 'SHA256(canonicalized axioms JSON)',
          length: 32,
          offset: 72,
          tag: 'witness',
        },
        { description: 'random bytes', length: 56, offset: 104, tag: 'padding' },
      ],
    };
  }

  _simulated_proof_layout_metadata(): SimulatedProofLayoutMetadata {
    return this.simulatedProofLayoutMetadata();
  }

  async generateProof(
    theorem: string,
    privateAxioms: string[],
    metadata: Record<string, unknown> = {},
  ): Promise<ZKPProof> {
    if (!theorem) {
      throw new ZKPError('Theorem cannot be empty');
    }
    if (privateAxioms.length === 0) {
      throw new ZKPError('At least one axiom required');
    }

    const circuitHash = await this.hashCircuit(theorem, privateAxioms);
    const witness = await this.computeWitness(privateAxioms);
    const proofData = await this.simulateGroth16Proof(circuitHash, witness, theorem);
    const circuitVersion = Number(metadata.circuit_version ?? 1);
    const rulesetId = String(metadata.ruleset_id ?? 'TDFOL_v1');

    return new ZKPProof({
      metadata: {
        ...metadata,
        num_axioms: privateAxioms.length,
        proof_system: 'Groth16 (simulated)',
        simulated_proof_layout:
          metadata.simulated_proof_layout ?? this.simulatedProofLayoutMetadata(),
      },
      proofData,
      publicInputs: {
        axioms_commitment: await axiomsCommitmentHex(privateAxioms),
        circuit_version: circuitVersion,
        ruleset_id: rulesetId,
        theorem,
        theorem_hash: await theoremHashHex(theorem),
      },
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
    try {
      const theorem = proof.publicInputs.theorem;
      const theoremHash = proof.publicInputs.theorem_hash;
      if (typeof theorem !== 'string' || typeof theoremHash !== 'string') {
        return false;
      }

      const expectedHash = await theoremHashHex(theorem);
      const legacyHash = await sha256Hex(theorem);
      if (theoremHash !== expectedHash && theoremHash !== legacyHash) {
        return false;
      }

      if (proof.proofData.byteLength < 100 || proof.proofData.byteLength > 300) {
        return false;
      }
      if (
        proof.proofData.byteLength >= 8 &&
        bytesToHex(proof.proofData.slice(0, 8)) !== bytesToHex(SIMULATED_MAGIC)
      ) {
        return false;
      }
      if (!Object.prototype.hasOwnProperty.call(proof.metadata, 'proof_system')) {
        return false;
      }
      return true;
    } catch {
      return false;
    }
  }

  verify_proof(proof: ZKPProof): Promise<boolean> {
    return this.verifyProof(proof);
  }

  private async hashCircuit(theorem: string, axioms: string[]): Promise<Uint8Array> {
    const normalizedAxioms = axioms.map(normalizeProofText);
    const circuitData = stableJsonStringify({
      axiom_hashes: await Promise.all(normalizedAxioms.map(sha256Hex)),
      num_axioms: normalizedAxioms.length,
      theorem: normalizeProofText(theorem),
    });
    return sha256Bytes(circuitData);
  }

  private async computeWitness(axioms: string[]): Promise<Uint8Array> {
    return sha256Bytes(stableJsonStringify(axioms.map(normalizeProofText)));
  }

  private async simulateGroth16Proof(
    circuitHash: Uint8Array,
    witness: Uint8Array,
    theorem: string,
  ): Promise<Uint8Array> {
    const theoremBytes = new TextEncoder().encode(normalizeProofText(theorem));
    const proofHash = await sha256Bytes(concatBytes(circuitHash, witness, theoremBytes));
    const padding = new Uint8Array(56);
    globalThis.crypto.getRandomValues(padding);
    return concatBytes(SIMULATED_MAGIC, proofHash, circuitHash, witness, padding);
  }
}

export const BACKEND_METADATA: Record<string, Record<string, string>> = {
  groth16: {
    class_name: 'Groth16Backend',
    curve: 'bn254',
    description: 'Real Groth16 zkSNARK backend (BN254 curve) - browser/WASM implementation pending',
    module: 'groth16',
  },
  simulated: {
    class_name: 'SimulatedBackend',
    curve: 'simulation',
    description: 'Educational simulation (not cryptographically secure)',
    module: 'simulated',
  },
};

let simulatedBackendCache: SimulatedBackend | undefined;

export function getBackend(backend = 'simulated'): ZKBackend {
  const normalized = backend.trim().toLowerCase();
  if (normalized === '' || normalized === 'sim' || normalized === 'simulated') {
    simulatedBackendCache ??= new SimulatedBackend();
    return simulatedBackendCache;
  }
  if (normalized === 'groth16' || normalized === 'g16') {
    throw new ZKPError('Groth16 backend is not yet ported to browser-native WASM.');
  }
  throw new ZKPError(
    `Unknown ZKP backend: ${JSON.stringify(backend)}. Available backends: 'simulated', 'groth16'`,
  );
}

export function get_backend(backend = 'simulated'): ZKBackend {
  return getBackend(backend);
}

export function listBackends(): Record<string, Record<string, string>> {
  return {
    groth16: { ...BACKEND_METADATA.groth16 },
    simulated: { ...BACKEND_METADATA.simulated },
  };
}

export function list_backends(): Record<string, Record<string, string>> {
  return listBackends();
}

export function backendIsAvailable(backendId: string): boolean {
  try {
    getBackend(backendId);
    return true;
  } catch {
    return false;
  }
}

export function backend_is_available(backendId: string): boolean {
  return backendIsAvailable(backendId);
}

export function clearBackendCache(): void {
  simulatedBackendCache = undefined;
}

export function clear_backend_cache(): void {
  clearBackendCache();
}

async function sha256Hex(text: string): Promise<string> {
  return bytesToHex(await sha256Bytes(text));
}

async function sha256Bytes(input: string | Uint8Array): Promise<Uint8Array> {
  const bytes = typeof input === 'string' ? new TextEncoder().encode(input) : input;
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return new Uint8Array(digest);
}

function bytesToHex(bytes: Uint8Array): string {
  return [...bytes].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(hex: string): Uint8Array {
  if (!/^(?:[0-9a-fA-F]{2})*$/.test(hex)) {
    throw new ZKPError('proof_data must be an even-length hex string');
  }
  const bytes = new Uint8Array(hex.length / 2);
  for (let index = 0; index < bytes.length; index += 1) {
    bytes[index] = Number.parseInt(hex.slice(index * 2, index * 2 + 2), 16);
  }
  return bytes;
}

function concatBytes(...chunks: Uint8Array[]): Uint8Array {
  const totalLength = chunks.reduce((sum, chunk) => sum + chunk.byteLength, 0);
  const output = new Uint8Array(totalLength);
  let offset = 0;
  for (const chunk of chunks) {
    output.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return output;
}

function stableJsonStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(stableJsonStringify).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJsonStringify(record[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}
