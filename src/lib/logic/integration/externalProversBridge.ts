import { LogicBridgeError } from '../errors';
import type { ProofResult } from '../types';
import { createBrowserNativeCoqProverBridge } from './coqProverBridge';
import { createBrowserNativeCvc5ProverBridge } from './cvc5ProverBridge';
import { createBrowserNativeLeanProverBridge } from './leanProverBridge';
import {
  BrowserNativeProverRouter,
  createBrowserNativeEProverAdapter,
  createDefaultProverAdapters,
  type BrowserNativeProofAdapter,
  type BrowserNativeProofLogic,
  type BrowserNativeProofRequest,
} from './proverAdapters';
import { createBrowserNativeSymbolicAiProverBridge } from './symbolicAiProverBridge';
import { createBrowserNativeZ3ProverBridge } from './z3ProverBridge';

export type ExternalProverBridgeName =
  | 'auto'
  | 'local'
  | 'e-prover'
  | 'cvc5'
  | 'z3'
  | 'lean'
  | 'symbolicai'
  | 'coq'
  | 'vampire';

export interface ExternalProverBridgeRequest extends BrowserNativeProofRequest {
  prover?: ExternalProverBridgeName;
}

export interface ExternalProverBridgeMetadata {
  sourcePythonModule: 'logic/integration/bridges/external_provers.py';
  runtime: 'typescript-wasm-browser';
  serverCallsAllowed: false;
  pythonRuntime: false;
  subprocessAllowed: false;
  rpcAllowed: false;
  filesystemAllowed: false;
  failClosed: true;
  defaultProver: 'auto';
  supportedProvers: Array<ExternalProverBridgeName>;
}

export interface ExternalProverBridgeInfo {
  name: ExternalProverBridgeName;
  available: boolean;
  runtime: 'typescript-wasm-browser';
  supportedLogics: Array<BrowserNativeProofLogic>;
  requiresExternalProver: false;
  failClosedReason?: string;
}

const SUPPORTED_PROVERS: Array<ExternalProverBridgeName> = [
  'auto',
  'local',
  'e-prover',
  'cvc5',
  'z3',
  'lean',
  'symbolicai',
  'coq',
  'vampire',
];

export class BrowserNativeExternalProversBridge {
  readonly metadata: ExternalProverBridgeMetadata = {
    sourcePythonModule: 'logic/integration/bridges/external_provers.py',
    runtime: 'typescript-wasm-browser',
    serverCallsAllowed: false,
    pythonRuntime: false,
    subprocessAllowed: false,
    rpcAllowed: false,
    filesystemAllowed: false,
    failClosed: true,
    defaultProver: 'auto',
    supportedProvers: SUPPORTED_PROVERS,
  };

  private readonly router: BrowserNativeProverRouter;
  private readonly adapters: Map<ExternalProverBridgeName, BrowserNativeProofAdapter>;

  constructor(adapters: Partial<Record<ExternalProverBridgeName, BrowserNativeProofAdapter>> = {}) {
    const localAdapters = createDefaultProverAdapters({ includeEProverCompatibilityAdapter: true });
    this.router = new BrowserNativeProverRouter(localAdapters);
    this.adapters = new Map<ExternalProverBridgeName, BrowserNativeProofAdapter>([
      ['local', localAdapters[0]],
      ['e-prover', createBrowserNativeEProverAdapter()],
      ['cvc5', createBrowserNativeCvc5ProverBridge()],
      ['z3', createBrowserNativeZ3ProverBridge()],
      ['lean', createBrowserNativeLeanProverBridge()],
      ['coq', createBrowserNativeCoqProverBridge()],
      ['symbolicai', createBrowserNativeSymbolicAiProverBridge()],
      ...Object.entries(adapters).filter(
        (entry): entry is [ExternalProverBridgeName, BrowserNativeProofAdapter] =>
          Boolean(entry[1]),
      ),
    ]);
  }

  listProvers(): Array<ExternalProverBridgeInfo> {
    return this.metadata.supportedProvers.map((name) => this.getProverInfo(name));
  }

  getProverInfo(name: ExternalProverBridgeName): ExternalProverBridgeInfo {
    if (name === 'auto') return info(name, true, ['tdfol', 'cec', 'dcec']);
    const adapter = this.adapters.get(name);
    if (adapter) return info(name, true, [adapter.metadata.logic]);
    return info(
      name,
      false,
      [],
      `${name} has no browser-native TypeScript/WASM adapter in this build.`,
    );
  }

  supports(name: ExternalProverBridgeName, logic: BrowserNativeProofLogic): boolean {
    return name === 'auto'
      ? this.router.supports(logic)
      : (this.adapters.get(name)?.supports(logic) ?? false);
  }

  prove(request: ExternalProverBridgeRequest): ProofResult {
    const prover = request.prover ?? 'auto';
    if (prover === 'auto') return this.router.prove(request);
    const adapter = this.adapters.get(prover);
    if (!adapter) {
      throw new LogicBridgeError(
        `Unsupported browser-native external prover bridge: ${prover}; no Python, subprocess, RPC, or server fallback is available.`,
      );
    }
    if (!adapter.supports(request.logic)) {
      throw new LogicBridgeError(
        `Browser-native external prover bridge ${prover} does not support ${request.logic}.`,
      );
    }
    const result = adapter.prove(request);
    return {
      ...result,
      method: `integration-external-provers:${prover}:${result.method ?? request.logic}`,
    };
  }
}

export function createBrowserNativeExternalProversBridge(): BrowserNativeExternalProversBridge {
  return new BrowserNativeExternalProversBridge();
}

export const create_browser_native_external_provers_bridge =
  createBrowserNativeExternalProversBridge;

function info(
  name: ExternalProverBridgeName,
  available: boolean,
  supportedLogics: Array<BrowserNativeProofLogic>,
  failClosedReason?: string,
): ExternalProverBridgeInfo {
  return {
    name,
    available,
    runtime: 'typescript-wasm-browser',
    supportedLogics,
    requiresExternalProver: false,
    failClosedReason,
  };
}
