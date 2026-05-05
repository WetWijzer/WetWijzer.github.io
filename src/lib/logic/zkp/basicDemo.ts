import { ZKPProver, ZKPVerifier, type ZKPProverStats, type ZKPVerifierStats } from './facade';
import { ZKPProof, type ZKPProofDict } from './simulatedBackend';

export interface BasicZkpDemoOptions {
  theorem?: string;
  axioms?: Array<string>;
  seed?: string;
  securityLevel?: number;
}

export interface BasicZkpDemoResult {
  module: 'logic/zkp/examples/zkp_basic_demo.py';
  runtime: 'browser-native-typescript';
  backend: 'simulated';
  cryptographic: false;
  theorem: string;
  axioms: Array<string>;
  proof: ZKPProofDict;
  verified: boolean;
  tampered_verified: boolean;
  prover_stats: ZKPProverStats;
  verifier_stats: ZKPVerifierStats;
  warnings: Array<string>;
}

const DEFAULT_THEOREM = 'Q';
const DEFAULT_AXIOMS = ['P', 'P -> Q'];

export async function runBasicZkpDemo(
  options: BasicZkpDemoOptions = {},
): Promise<BasicZkpDemoResult> {
  const theorem = options.theorem ?? DEFAULT_THEOREM;
  const axioms = options.axioms ?? DEFAULT_AXIOMS;
  const securityLevel = options.securityLevel ?? 128;
  const seed = options.seed ?? 'basic-demo';
  const prover = new ZKPProver({ enableCaching: false, securityLevel });
  const verifier = new ZKPVerifier({ securityLevel });
  const metadata: Record<string, unknown> = {
    circuit_ref: 'knowledge_of_axioms@1',
    circuit_version: 1,
    demo_module: 'zkp_basic_demo',
    ruleset_id: 'TDFOL_v1',
    seed,
  };

  const proof = await prover.generateProof(theorem, axioms, metadata);
  const verified = await verifier.verifyWithPublicInputs(proof, theorem);
  const tamperedVerified = await verifier.verifyProof(
    ZKPProof.fromDict(proofWithPublicInput(proof.toDict(), 'theorem_hash', 'f'.repeat(64))),
  );

  return {
    axioms: [...axioms],
    backend: 'simulated',
    cryptographic: false,
    module: 'logic/zkp/examples/zkp_basic_demo.py',
    proof: proof.toDict(),
    prover_stats: prover.getStats(),
    runtime: 'browser-native-typescript',
    tampered_verified: tamperedVerified,
    theorem,
    verified,
    verifier_stats: verifier.getStats(),
    warnings: [
      'Simulated educational ZKP proof; not cryptographically secure.',
      'Runs entirely in browser-native TypeScript/WASM-compatible code without Python, server, filesystem, subprocess, or RPC fallbacks.',
    ],
  };
}

export const run_basic_zkp_demo = runBasicZkpDemo;

function proofWithPublicInput(proof: ZKPProofDict, key: string, value: unknown): ZKPProofDict {
  return {
    ...proof,
    public_inputs: {
      ...proof.public_inputs,
      [key]: value,
    },
  };
}
