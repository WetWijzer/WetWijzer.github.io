import { webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import {
  axiomsCommitmentHex,
  tdfolV1AxiomsCommitmentHexV2,
  theoremHashHex,
} from './canonicalization';
import {
  FormCircuit,
  MVPCircuit,
  TDFOLv1DerivationCircuit,
  ZKPCircuit,
  createFormCircuit,
  createImplicationCircuit,
  createKnowledgeOfAxiomsCircuit,
} from './circuits';
import type { ZkpStatement, ZkpWitness } from './statement';

Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextEncoder', {
  value: TextEncoder,
  configurable: true,
});

describe('ZKP circuit helpers', () => {
  it('models high-level Boolean circuits and simplified R1CS output', async () => {
    const circuit = new ZKPCircuit();
    const p = circuit.addInput('P');
    const q = circuit.addInput('Q');
    const r = circuit.addInput('R');
    const pq = circuit.addAndGate(p, q);
    const result = circuit.addImpliesGate(pq, r);
    circuit.setOutput(result);

    expect(circuit.numInputs()).toBe(3);
    expect(circuit.numGates()).toBe(2);
    expect(circuit.numWires()).toBe(5);
    expect(circuit.toString()).toBe('ZKPCircuit(inputs=3, gates=2, wires=5)');
    expect(circuit.toR1cs()).toEqual({
      constraints: [
        { A: 0, B: 1, C: 3, type: 'multiplication' },
        { inputs: [3, 2], output: 4, type: 'implies_composition' },
      ],
      num_constraints: 2,
      num_variables: 5,
      public_inputs: [4],
    });
    await expect(circuit.getCircuitHash()).resolves.toMatch(/^[0-9a-f]{64}$/);
  });

  it('creates implication circuits with Python-compatible wire counts', () => {
    const circuit = createImplicationCircuit(2);

    expect(circuit.numInputs()).toBe(3);
    expect(circuit.numGates()).toBe(2);
    expect(circuit.numWires()).toBe(5);
    expect(circuit.toR1cs().public_inputs).toEqual([4]);
    expect(() => createImplicationCircuit(0)).toThrow('numPremises must be a positive integer');
  });

  it('compiles and evaluates MVP knowledge-of-axioms constraints locally', async () => {
    const circuit = createKnowledgeOfAxiomsCircuit();
    const axioms = ['P', 'P -> Q'].sort();
    const commitment = await axiomsCommitmentHex(axioms);
    const witness: ZkpWitness = {
      axioms,
      axiomsCommitmentHex: commitment,
      circuitVersion: 1,
      rulesetId: 'TDFOL_v1',
    };
    const statement: ZkpStatement = {
      theoremHash: await theoremHashHex('Q'),
      axiomsCommitment: commitment,
      circuitVersion: 1,
      rulesetId: 'TDFOL_v1',
    };

    expect(circuit).toBeInstanceOf(MVPCircuit);
    expect(circuit.compile()).toEqual({
      description: 'Prove knowledge of axioms matching a commitment',
      num_constraints: 1,
      num_inputs: 4,
      type: 'knowledge_of_axioms',
      version: 1,
    });
    await expect(circuit.verifyConstraints(witness, statement)).resolves.toBe(true);
    await expect(
      circuit.verifyConstraints({ ...witness, axioms: ['P -> Q', 'P'] }, statement),
    ).resolves.toBe(false);
  });

  it('evaluates TDFOL_v1 Horn derivation constraints without a cryptographic backend', async () => {
    const circuit = new TDFOLv1DerivationCircuit();
    const axioms = ['P', 'P -> Q'];
    const commitment = await tdfolV1AxiomsCommitmentHexV2(axioms);
    const statement: ZkpStatement = {
      theoremHash: await theoremHashHex('Q'),
      axiomsCommitment: commitment,
      circuitVersion: 2,
      rulesetId: 'TDFOL_v1',
    };
    const witness: ZkpWitness = {
      axioms,
      theorem: 'Q',
      intermediateSteps: ['P', 'Q'],
      axiomsCommitmentHex: commitment,
      circuitVersion: 2,
      rulesetId: 'TDFOL_v1',
    };

    expect(circuit.compile()).toEqual({
      description:
        'Prove theorem holds under TDFOL_v1 Horn-fragment semantics using a derivation trace',
      num_inputs: 4,
      type: 'tdfol_v1_horn_derivation',
      version: 2,
    });
    await expect(circuit.verifyConstraints(witness, statement)).resolves.toBe(true);
    await expect(
      circuit.verifyConstraints({ ...witness, intermediateSteps: ['R'] }, statement),
    ).resolves.toBe(false);
    await expect(
      circuit.verifyConstraints({ ...witness, intermediateSteps: ['P', 'P', 'Q'] }, statement),
    ).resolves.toBe(false);
  });

  it('ports form_circuit.py as a local TDFOL_v1 form validator bound to public inputs', async () => {
    const circuit = createFormCircuit();
    const axioms = ['P', 'P -> Q'];
    const commitment = await tdfolV1AxiomsCommitmentHexV2(axioms);
    const statement: ZkpStatement = {
      theoremHash: await theoremHashHex('Q'),
      axiomsCommitment: commitment,
      circuitVersion: 3,
      rulesetId: 'TDFOL_v1',
    };
    const witness: ZkpWitness = {
      axioms,
      theorem: 'Q',
      axiomsCommitmentHex: commitment,
      circuitVersion: 3,
      rulesetId: 'TDFOL_v1',
    };

    expect(circuit).toBeInstanceOf(FormCircuit);
    expect(circuit.compile()).toEqual({
      constraints: [
        'ruleset_version',
        'canonical_axiom_order',
        'tdfol_v1_axiom_form',
        'public_input_binding',
      ],
      description:
        'Prove a TDFOL_v1 theorem/axiom bundle is locally well formed and bound to public inputs',
      num_constraints: 4,
      num_inputs: 4,
      type: 'tdfol_v1_form',
      version: 3,
    });
    await expect(circuit.verifyConstraints(witness, statement)).resolves.toBe(true);
    await expect(circuit.verify_constraints(witness, statement)).resolves.toBe(true);
  });

  it('fails closed for malformed or noncanonical form circuit witnesses', async () => {
    const circuit = createFormCircuit();
    const axioms = ['P', 'P -> Q'];
    const commitment = await tdfolV1AxiomsCommitmentHexV2(axioms);
    const statement: ZkpStatement = {
      theoremHash: await theoremHashHex('Q'),
      axiomsCommitment: commitment,
      circuitVersion: 3,
      rulesetId: 'TDFOL_v1',
    };
    const witness: ZkpWitness = {
      axioms,
      theorem: 'Q',
      axiomsCommitmentHex: commitment,
      circuitVersion: 3,
      rulesetId: 'TDFOL_v1',
    };

    await expect(
      circuit.verifyConstraints({ ...witness, axioms: ['P -> Q', 'P'] }, statement),
    ).resolves.toBe(false);
    await expect(
      circuit.verifyConstraints({ ...witness, axioms: ['P ->'] }, statement),
    ).resolves.toBe(false);
    await expect(
      circuit.verifyConstraints({ ...witness, theorem: 'P -> Q' }, statement),
    ).resolves.toBe(false);
    await expect(
      circuit.verifyConstraints(witness, { ...statement, theoremHash: await theoremHashHex('R') }),
    ).resolves.toBe(false);
  });
});
