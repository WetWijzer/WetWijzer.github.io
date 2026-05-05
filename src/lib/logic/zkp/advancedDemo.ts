import { createImplicationCircuit } from './circuits';
import { ZKPProver, ZKPVerifier, type ZKPProverStats, type ZKPVerifierStats } from './facade';
import { backendIsAvailable, listBackends, ZKPProof, type ZKPProofDict } from './simulatedBackend';

export interface AdvancedZkpDemoOptions {
  theorem?: string;
  axioms?: Array<string>;
  seed?: string;
  securityLevel?: number;
}

export interface AdvancedZkpDemoResult {
  module: 'logic/zkp/examples/zkp_advanced_demo.py';
  runtime: 'browser-native-typescript';
  backend: 'simulated';
  cryptographic: false;
  theorem: string;
  axiom_count: number;
  proof: ZKPProofDict;
  cached_proof: ZKPProofDict;
  verified: boolean;
  cached_verified: boolean;
  tampered_verified: boolean;
  circuit: {
    kind: 'implication';
    hash: string;
    num_gates: number;
    num_inputs: number;
    num_wires: number;
    r1cs_constraints: number;
  };
  backends: Record<string, { available: boolean; description: string }>;
  prover_stats: ZKPProverStats;
  verifier_stats: ZKPVerifierStats;
  warnings: Array<string>;
}

const DEFAULT_THEOREM = 'Q';
const DEFAULT_AXIOMS = ['P', 'P -> Q'];

export async function runAdvancedZkpDemo(
  options: AdvancedZkpDemoOptions = {},
): Promise<AdvancedZkpDemoResult> {
  const theorem = options.theorem ?? DEFAULT_THEOREM;
  const axioms = options.axioms ?? DEFAULT_AXIOMS;
  const securityLevel = options.securityLevel ?? 128;
  const seed = options.seed ?? 'advanced-demo';

  const prover = new ZKPProver({ enableCaching: true, securityLevel });
  const verifier = new ZKPVerifier({ securityLevel });
  const metadata: Record<string, unknown> = {
    circuit_ref: 'knowledge_of_axioms@1',
    circuit_version: 1,
    demo_module: 'zkp_advanced_demo',
    ruleset_id: 'TDFOL_v1',
    seed,
  };

  const proof = await prover.generateProof(theorem, axioms, metadata);
  const cachedProof = await prover.generateProof(` ${theorem} `, [...axioms].reverse(), metadata);
  const verified = await verifier.verifyWithPublicInputs(proof, theorem);
  const cachedVerified = await verifier.verifyProof(cachedProof);
  const tamperedVerified = await verifier.verifyProof(
    ZKPProof.fromDict(proofWithPublicInput(proof.toDict(), 'theorem_hash', '0'.repeat(64))),
  );

  const circuit = createImplicationCircuit(Math.max(1, axioms.length - 1));
  const r1cs = circuit.toR1cs();
  const backendMetadata = listBackends();

  return {
    axiom_count: axioms.length,
    backend: 'simulated',
    backends: Object.fromEntries(
      Object.entries(backendMetadata).map(([backendId, metadataForBackend]) => [
        backendId,
        {
          available: backendIsAvailable(backendId),
          description: metadataForBackend.description,
        },
      ]),
    ),
    cached_proof: cachedProof.toDict(),
    cached_verified: cachedVerified,
    circuit: {
      hash: await circuit.getCircuitHash(),
      kind: 'implication',
      num_gates: circuit.numGates(),
      num_inputs: circuit.numInputs(),
      num_wires: circuit.numWires(),
      r1cs_constraints: r1cs.num_constraints,
    },
    cryptographic: false,
    module: 'logic/zkp/examples/zkp_advanced_demo.py',
    proof: proof.toDict(),
    prover_stats: prover.getStats(),
    runtime: 'browser-native-typescript',
    tampered_verified: tamperedVerified,
    theorem,
    verified,
    verifier_stats: verifier.getStats(),
    warnings: [
      'Simulated educational ZKP proof; not cryptographically secure.',
      'No Python runtime, server, filesystem, subprocess, RPC, or Node-only browser dependency is used by the runtime module.',
    ],
  };
}

export const run_advanced_zkp_demo = runAdvancedZkpDemo;

function proofWithPublicInput(proof: ZKPProofDict, key: string, value: unknown): ZKPProofDict {
  return {
    ...proof,
    public_inputs: {
      ...proof.public_inputs,
      [key]: value,
    },
  };
}
