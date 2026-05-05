import type { ZKPProof } from './simulatedBackend';

export interface BackendProtocolMetadata {
  sourcePythonModule: 'logic/zkp/backends/backend_protocol.py';
  browserNative: true;
  serverCallsAllowed: false;
  pythonRuntimeAllowed: false;
  requiredMethods: Array<'generateProof' | 'verifyProof'>;
}

export interface BrowserNativeZkpBackendProtocol {
  readonly backendId: string;
  readonly backend_id?: string;
  generateProof(
    theorem: string,
    privateAxioms: Array<string>,
    metadata?: Record<string, unknown>,
  ): Promise<ZKPProof>;
  verifyProof(proof: ZKPProof): Promise<boolean>;
}

export interface BackendProtocolValidation {
  ok: boolean;
  backendId?: string;
  errors: Array<string>;
  metadata: BackendProtocolMetadata;
}

export const BACKEND_PROTOCOL_METADATA: BackendProtocolMetadata = {
  browserNative: true,
  pythonRuntimeAllowed: false,
  requiredMethods: ['generateProof', 'verifyProof'],
  serverCallsAllowed: false,
  sourcePythonModule: 'logic/zkp/backends/backend_protocol.py',
};

export function validateBackendProtocol(candidate: unknown): BackendProtocolValidation {
  const errors: Array<string> = [];
  const record = isRecord(candidate) ? candidate : undefined;
  const backendId = record ? readBackendId(record) : undefined;

  if (!record) {
    errors.push('backend must be an object');
  } else {
    if (!backendId) {
      errors.push('backendId or backend_id must be a non-empty string');
    }
    if (typeof record.generateProof !== 'function') {
      errors.push('generateProof must be a function');
    }
    if (typeof record.verifyProof !== 'function') {
      errors.push('verifyProof must be a function');
    }
  }

  return {
    backendId,
    errors,
    metadata: BACKEND_PROTOCOL_METADATA,
    ok: errors.length === 0,
  };
}

export function assertBackendProtocol(
  candidate: unknown,
): asserts candidate is BrowserNativeZkpBackendProtocol {
  const validation = validateBackendProtocol(candidate);
  if (!validation.ok) {
    throw new TypeError(`Invalid ZKP backend protocol: ${validation.errors.join('; ')}`);
  }
}

export function backendSatisfiesProtocol(
  candidate: unknown,
): candidate is BrowserNativeZkpBackendProtocol {
  return validateBackendProtocol(candidate).ok;
}

export function describeBackendProtocol(candidate: unknown): BackendProtocolValidation {
  return validateBackendProtocol(candidate);
}

export const validate_backend_protocol = validateBackendProtocol;
export const assert_backend_protocol = assertBackendProtocol;
export const backend_satisfies_protocol = backendSatisfiesProtocol;
export const describe_backend_protocol = describeBackendProtocol;

function readBackendId(record: Record<string, unknown>): string | undefined {
  const camelId = record.backendId;
  if (typeof camelId === 'string' && camelId.trim() !== '') {
    return camelId;
  }

  const snakeId = record.backend_id;
  if (typeof snakeId === 'string' && snakeId.trim() !== '') {
    return snakeId;
  }

  return undefined;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}
