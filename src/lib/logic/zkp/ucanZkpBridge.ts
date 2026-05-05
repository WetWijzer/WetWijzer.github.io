import type { ZKPProofDict } from './simulatedBackend';
import { ZKPProof } from './simulatedBackend';
import { ZKPProver, ZKPVerifier } from './facade';

export interface UcanZkpCapability {
  readonly with: string;
  readonly can: string;
  readonly nb?: Record<string, unknown>;
}

export interface UcanZkpDelegation {
  readonly iss: string;
  readonly aud: string;
  readonly att: readonly UcanZkpCapability[];
  readonly exp?: number;
  readonly nbf?: number;
  readonly prf?: readonly string[];
  readonly signed?: boolean;
}

export interface UcanZkpBridgeOptions {
  readonly theorem?: string;
  readonly privateAxioms?: readonly string[];
  readonly backend?: string;
  readonly securityLevel?: number;
  readonly requireSigned?: boolean;
}

export interface UcanZkpProofBundle {
  readonly ok: boolean;
  readonly success: boolean;
  readonly theorem: string;
  readonly delegation?: UcanZkpDelegation;
  readonly proof?: ZKPProofDict;
  readonly verified: boolean;
  readonly errors: readonly string[];
  readonly fail_closed_reason?: string;
  readonly metadata: typeof UCAN_ZKP_BRIDGE_METADATA;
}

export const UCAN_ZKP_BRIDGE_METADATA = {
  sourcePythonModule: 'logic/zkp/ucan_zkp_bridge.py',
  runtime: 'browser-native-typescript',
  browserNative: true,
  serverCallsAllowed: false,
  pythonRuntimeAllowed: false,
  filesystemAllowed: false,
  subprocessAllowed: false,
  rpcAllowed: false,
  proofBinding: 'local-ucan-capability-commitment',
} as const;

export class BrowserNativeUcanZkpBridge {
  readonly metadata = UCAN_ZKP_BRIDGE_METADATA;

  async proveDelegation(
    delegation: UcanZkpDelegation,
    options: UcanZkpBridgeOptions = {},
  ): Promise<UcanZkpProofBundle> {
    const errors = validateDelegation(delegation, options);
    const theorem =
      options.theorem ?? (errors.length === 0 ? theoremForDelegation(delegation) : 'ucan:invalid');
    if (errors.length > 0) return closed(theorem, errors, 'ucan_zkp_invalid_delegation');

    const ucanCommitment = await hashJson(canonicalDelegation(delegation));
    const privateAxioms = options.privateAxioms ?? axiomsForDelegation(delegation);
    const prover = new ZKPProver({
      backend: options.backend ?? 'simulated',
      securityLevel: options.securityLevel ?? 128,
    });
    const proof = await prover.generateProof(theorem, [...privateAxioms], {
      capability_count: delegation.att.length,
      circuit_ref: 'ucan_capability_binding@v1',
      circuit_version: 1,
      issuer: delegation.iss,
      audience: delegation.aud,
      ruleset_id: 'UCAN_ZKP_v1',
      source_python_module: UCAN_ZKP_BRIDGE_METADATA.sourcePythonModule,
      ucan_commitment: ucanCommitment,
    });
    const verified = await new ZKPVerifier({
      backend: options.backend ?? 'simulated',
      securityLevel: options.securityLevel ?? 128,
    }).verifyProof(proof);

    return {
      ok: verified,
      success: verified,
      theorem,
      delegation,
      proof: proof.toDict(),
      verified,
      errors: verified ? [] : ['Generated UCAN ZKP proof failed local verification.'],
      fail_closed_reason: verified ? undefined : 'ucan_zkp_local_verification_failed',
      metadata: this.metadata,
    };
  }

  async verifyDelegationProof(
    delegation: UcanZkpDelegation,
    proofDict: ZKPProofDict,
    options: UcanZkpBridgeOptions = {},
  ): Promise<UcanZkpProofBundle> {
    const errors = validateDelegation(delegation, options);
    const theorem =
      options.theorem ?? (errors.length === 0 ? theoremForDelegation(delegation) : 'ucan:invalid');
    if (errors.length > 0) return closed(theorem, errors, 'ucan_zkp_invalid_delegation');

    const proof = ZKPProof.fromDict(proofDict);
    const verifier = new ZKPVerifier({
      backend: options.backend ?? 'simulated',
      securityLevel: options.securityLevel ?? 128,
    });
    const ucanCommitment = await hashJson(canonicalDelegation(delegation));
    const verified =
      proof.publicInputs.theorem === theorem &&
      proof.metadata.ucan_commitment === ucanCommitment &&
      proof.metadata.source_python_module === UCAN_ZKP_BRIDGE_METADATA.sourcePythonModule &&
      (await verifier.verifyProof(proof));
    return {
      ok: verified,
      success: verified,
      theorem,
      delegation,
      proof: proof.toDict(),
      verified,
      errors: verified ? [] : ['UCAN delegation and ZKP proof binding did not verify locally.'],
      fail_closed_reason: verified ? undefined : 'ucan_zkp_binding_verification_failed',
      metadata: this.metadata,
    };
  }
}

export const proveUcanDelegationZkp = (
  delegation: UcanZkpDelegation,
  options: UcanZkpBridgeOptions = {},
): Promise<UcanZkpProofBundle> =>
  new BrowserNativeUcanZkpBridge().proveDelegation(delegation, options);
export const verifyUcanDelegationZkp = (
  delegation: UcanZkpDelegation,
  proof: ZKPProofDict,
  options: UcanZkpBridgeOptions = {},
): Promise<UcanZkpProofBundle> =>
  new BrowserNativeUcanZkpBridge().verifyDelegationProof(delegation, proof, options);
export const prove_ucan_delegation_zkp = proveUcanDelegationZkp;
export const verify_ucan_delegation_zkp = verifyUcanDelegationZkp;
export const create_ucan_zkp_bridge = () => new BrowserNativeUcanZkpBridge();

function validateDelegation(
  delegation: UcanZkpDelegation,
  options: UcanZkpBridgeOptions,
): string[] {
  if (!delegation || typeof delegation !== 'object') return ['delegation must be an object.'];
  const errors = [
    ...(!isDid(delegation.iss) ? ['delegation issuer must be a DID.'] : []),
    ...(!isDid(delegation.aud) ? ['delegation audience must be a DID.'] : []),
    ...(!Array.isArray(delegation.att) || delegation.att.length === 0
      ? ['delegation must include at least one capability.']
      : []),
    ...(options.requireSigned || delegation.signed === true
      ? ['signed UCAN verification is not available in this browser-native bridge.']
      : []),
  ];
  for (const capability of delegation.att ?? []) {
    if (!capability.with || !capability.can)
      errors.push('each capability needs with and can fields.');
  }
  return errors;
}

function theoremForDelegation(delegation: UcanZkpDelegation): string {
  return `ucan:${delegation.iss}->${delegation.aud}:${delegation.att.map((cap) => `${cap.can}:${cap.with}`).join('|')}`;
}

function axiomsForDelegation(delegation: UcanZkpDelegation): readonly string[] {
  return delegation.att.map(
    (capability, index) => `capability_${index}:${stableJson(canonicalCapability(capability))}`,
  );
}

function canonicalDelegation(delegation: UcanZkpDelegation): Record<string, unknown> {
  return {
    att: delegation.att.map(canonicalCapability),
    aud: delegation.aud,
    exp: delegation.exp ?? null,
    iss: delegation.iss,
    nbf: delegation.nbf ?? null,
    prf: [...(delegation.prf ?? [])].sort(),
    signed: delegation.signed === true,
  };
}

function canonicalCapability(capability: UcanZkpCapability): Record<string, unknown> {
  return { can: capability.can, nb: capability.nb ?? {}, with: capability.with };
}

function closed(theorem: string, errors: readonly string[], reason: string): UcanZkpProofBundle {
  return {
    ok: false,
    success: false,
    theorem,
    verified: false,
    errors,
    fail_closed_reason: reason,
    metadata: UCAN_ZKP_BRIDGE_METADATA,
  };
}

function isDid(value: string | undefined): value is string {
  return typeof value === 'string' && /^did:[a-z0-9]+:.+/iu.test(value.trim());
}

async function hashJson(value: Record<string, unknown>): Promise<string> {
  const digest = await globalThis.crypto.subtle.digest(
    'SHA-256',
    new TextEncoder().encode(stableJson(value)),
  );
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`;
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJson(record[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}
