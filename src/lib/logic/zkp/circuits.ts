import {
  axiomsCommitmentHex,
  canonicalizeAxioms,
  canonicalizeTheorem,
  normalizeProofText,
  parseTdfolV1Axiom,
  tdfolV1AxiomsCommitmentHexV2,
  theoremHashHex,
} from './canonicalization';
import type { ZkpStatement, ZkpWitness } from './statement';

export type CircuitGateType = 'AND' | 'OR' | 'NOT' | 'IMPLIES' | 'XOR';

export interface CircuitGate {
  gateType: CircuitGateType;
  inputs: number[];
  output: number;
}

export interface R1csConstraint {
  type:
    | 'multiplication'
    | 'or_composition'
    | 'not_composition'
    | 'implies_composition'
    | 'xor_composition';
  A?: number;
  B?: number;
  C?: number;
  inputs?: number[];
  output?: number;
}

export interface R1csRepresentation {
  num_constraints: number;
  num_variables: number;
  constraints: R1csConstraint[];
  public_inputs: number[];
}

export class ZKPCircuit {
  private readonly gates: CircuitGate[] = [];
  private readonly inputs = new Map<string, number>();
  private readonly outputs: number[] = [];
  private nextWire = 0;

  addInput(name: string): number {
    const wire = this.nextWire;
    this.nextWire += 1;
    this.inputs.set(name, wire);
    return wire;
  }

  add_input(name: string): number {
    return this.addInput(name);
  }

  addAndGate(wireA: number, wireB: number): number {
    return this.addGate('AND', [wireA, wireB]);
  }

  add_and_gate(wireA: number, wireB: number): number {
    return this.addAndGate(wireA, wireB);
  }

  addOrGate(wireA: number, wireB: number): number {
    return this.addGate('OR', [wireA, wireB]);
  }

  add_or_gate(wireA: number, wireB: number): number {
    return this.addOrGate(wireA, wireB);
  }

  addNotGate(wire: number): number {
    return this.addGate('NOT', [wire]);
  }

  add_not_gate(wire: number): number {
    return this.addNotGate(wire);
  }

  addImpliesGate(wireA: number, wireB: number): number {
    return this.addGate('IMPLIES', [wireA, wireB]);
  }

  add_implies_gate(wireA: number, wireB: number): number {
    return this.addImpliesGate(wireA, wireB);
  }

  addXorGate(wireA: number, wireB: number): number {
    return this.addGate('XOR', [wireA, wireB]);
  }

  add_xor_gate(wireA: number, wireB: number): number {
    return this.addXorGate(wireA, wireB);
  }

  setOutput(wire: number): void {
    this.outputs.push(wire);
  }

  set_output(wire: number): void {
    this.setOutput(wire);
  }

  numGates(): number {
    return this.gates.length;
  }

  num_gates(): number {
    return this.numGates();
  }

  numInputs(): number {
    return this.inputs.size;
  }

  num_inputs(): number {
    return this.numInputs();
  }

  numWires(): number {
    return this.nextWire;
  }

  num_wires(): number {
    return this.numWires();
  }

  getGates(): CircuitGate[] {
    return this.gates.map((gate) => ({ ...gate, inputs: [...gate.inputs] }));
  }

  async getCircuitHash(): Promise<string> {
    const circuitData = {
      gates: this.gates.map((gate) => ({
        inputs: gate.inputs,
        output: gate.output,
        type: gate.gateType,
      })),
      num_gates: this.gates.length,
      num_inputs: this.inputs.size,
      num_wires: this.nextWire,
    };
    return sha256Hex(stableJsonStringify(circuitData));
  }

  get_circuit_hash(): Promise<string> {
    return this.getCircuitHash();
  }

  toR1cs(): R1csRepresentation {
    const constraints = this.gates.map((gate): R1csConstraint => {
      if (gate.gateType === 'AND') {
        return {
          A: gate.inputs[0],
          B: gate.inputs[1],
          C: gate.output,
          type: 'multiplication',
        };
      }
      const typeByGate = {
        IMPLIES: 'implies_composition',
        NOT: 'not_composition',
        OR: 'or_composition',
        XOR: 'xor_composition',
      } as const;
      return {
        inputs: [...gate.inputs],
        output: gate.output,
        type: typeByGate[gate.gateType],
      };
    });

    return {
      constraints,
      num_constraints: constraints.length,
      num_variables: this.nextWire,
      public_inputs: [...this.outputs],
    };
  }

  to_r1cs(): R1csRepresentation {
    return this.toR1cs();
  }

  toString(): string {
    return `ZKPCircuit(inputs=${this.numInputs()}, gates=${this.numGates()}, wires=${this.numWires()})`;
  }

  private addGate(gateType: CircuitGateType, inputs: number[]): number {
    const output = this.nextWire;
    this.nextWire += 1;
    this.gates.push({ gateType, inputs: [...inputs], output });
    return output;
  }
}

export class MVPCircuit {
  constructor(
    public readonly circuitVersion = 1,
    public readonly circuitType = 'knowledge_of_axioms',
  ) {}

  numInputs(): number {
    return 4;
  }

  num_inputs(): number {
    return this.numInputs();
  }

  numConstraints(): number {
    return 1;
  }

  num_constraints(): number {
    return this.numConstraints();
  }

  compile(): Record<string, string | number> {
    return {
      description: 'Prove knowledge of axioms matching a commitment',
      num_constraints: this.numConstraints(),
      num_inputs: this.numInputs(),
      type: this.circuitType,
      version: this.circuitVersion,
    };
  }

  async verifyConstraints(witness: ZkpWitness, statement: ZkpStatement): Promise<boolean> {
    try {
      if (statement.circuitVersion !== this.circuitVersion) return false;
      if ((witness.circuitVersion ?? 1) !== statement.circuitVersion) return false;
      if ((witness.rulesetId ?? 'TDFOL_v1') !== statement.rulesetId) return false;

      const canonicalAxioms = canonicalizeAxioms(witness.axioms);
      if (!sameStringList(witness.axioms, canonicalAxioms)) return false;

      const expectedCommitmentHex = await axiomsCommitmentHex(canonicalAxioms);
      return (
        statement.axiomsCommitment === expectedCommitmentHex &&
        witness.axiomsCommitmentHex === expectedCommitmentHex
      );
    } catch {
      return false;
    }
  }

  verify_constraints(witness: ZkpWitness, statement: ZkpStatement): Promise<boolean> {
    return this.verifyConstraints(witness, statement);
  }
}

export class TDFOLv1DerivationCircuit {
  constructor(
    public readonly circuitVersion = 2,
    public readonly circuitType = 'tdfol_v1_horn_derivation',
  ) {}

  numInputs(): number {
    return 4;
  }

  num_inputs(): number {
    return this.numInputs();
  }

  compile(): Record<string, string | number> {
    return {
      description:
        'Prove theorem holds under TDFOL_v1 Horn-fragment semantics using a derivation trace',
      num_inputs: this.numInputs(),
      type: this.circuitType,
      version: this.circuitVersion,
    };
  }

  async verifyConstraints(witness: ZkpWitness, statement: ZkpStatement): Promise<boolean> {
    try {
      if (statement.circuitVersion !== this.circuitVersion) return false;
      if ((witness.circuitVersion ?? 1) !== statement.circuitVersion) return false;
      if (statement.rulesetId !== 'TDFOL_v1') return false;
      if ((witness.rulesetId ?? 'TDFOL_v1') !== statement.rulesetId) return false;
      if (!witness.theorem) return false;

      const theoremAtom = canonicalizeTheorem(witness.theorem);
      if (statement.theoremHash !== (await theoremHashHex(theoremAtom))) return false;

      const canonicalAxioms = canonicalizeAxioms(witness.axioms);
      if (!sameStringList(witness.axioms, canonicalAxioms)) return false;

      const expectedCommitmentHex = await tdfolV1AxiomsCommitmentHexV2(canonicalAxioms);
      if (statement.axiomsCommitment !== expectedCommitmentHex) return false;
      if (witness.axiomsCommitmentHex !== expectedCommitmentHex) return false;

      const intermediateSteps = witness.intermediateSteps ?? [];
      if (intermediateSteps.length === 0) return false;

      const parsedAxioms = canonicalAxioms.map(parseTdfolV1Axiom);
      const known = new Set(
        parsedAxioms.filter((axiom) => !axiom.antecedent).map((axiom) => axiom.consequent),
      );
      const implications = parsedAxioms.filter((axiom) => axiom.antecedent);
      const seen = new Set<string>();

      for (const rawStep of intermediateSteps) {
        const step = canonicalizeTheorem(rawStep);
        if (seen.has(step)) return false;
        seen.add(step);

        if (!known.has(step)) {
          const justified = implications.some(
            (axiom) =>
              axiom.consequent === step &&
              axiom.antecedent !== undefined &&
              known.has(axiom.antecedent),
          );
          if (!justified) return false;
          known.add(step);
        }
      }

      return known.has(theoremAtom);
    } catch {
      return false;
    }
  }

  verify_constraints(witness: ZkpWitness, statement: ZkpStatement): Promise<boolean> {
    return this.verifyConstraints(witness, statement);
  }
}

export class FormCircuit {
  constructor(
    public readonly circuitVersion = 3,
    public readonly circuitType = 'tdfol_v1_form',
  ) {}

  numInputs(): number {
    return 4;
  }

  num_inputs(): number {
    return this.numInputs();
  }

  numConstraints(): number {
    return 4;
  }

  num_constraints(): number {
    return this.numConstraints();
  }

  compile(): Record<string, string | number | string[]> {
    return {
      description:
        'Prove a TDFOL_v1 theorem/axiom bundle is locally well formed and bound to public inputs',
      constraints: [
        'ruleset_version',
        'canonical_axiom_order',
        'tdfol_v1_axiom_form',
        'public_input_binding',
      ],
      num_constraints: this.numConstraints(),
      num_inputs: this.numInputs(),
      type: this.circuitType,
      version: this.circuitVersion,
    };
  }

  async verifyConstraints(witness: ZkpWitness, statement: ZkpStatement): Promise<boolean> {
    try {
      if (statement.circuitVersion !== this.circuitVersion) return false;
      if ((witness.circuitVersion ?? this.circuitVersion) !== statement.circuitVersion)
        return false;
      if (statement.rulesetId !== 'TDFOL_v1') return false;
      if ((witness.rulesetId ?? 'TDFOL_v1') !== statement.rulesetId) return false;
      if (!witness.theorem || !isTdfolV1Atom(witness.theorem)) return false;

      const theoremAtom = canonicalizeTheorem(witness.theorem);
      if (statement.theoremHash !== (await theoremHashHex(theoremAtom))) return false;

      const canonicalAxioms = canonicalizeAxioms(witness.axioms);
      if (!sameStringList(witness.axioms, canonicalAxioms)) return false;
      if (!canonicalAxioms.every(isTdfolV1Formula)) return false;

      const expectedCommitmentHex = await tdfolV1AxiomsCommitmentHexV2(canonicalAxioms);
      return (
        statement.axiomsCommitment === expectedCommitmentHex &&
        witness.axiomsCommitmentHex === expectedCommitmentHex
      );
    } catch {
      return false;
    }
  }

  verify_constraints(witness: ZkpWitness, statement: ZkpStatement): Promise<boolean> {
    return this.verifyConstraints(witness, statement);
  }
}

export function createKnowledgeOfAxiomsCircuit(circuitVersion = 1): MVPCircuit {
  return new MVPCircuit(circuitVersion);
}

export function create_knowledge_of_axioms_circuit(circuitVersion = 1): MVPCircuit {
  return createKnowledgeOfAxiomsCircuit(circuitVersion);
}

export function createImplicationCircuit(numPremises: number): ZKPCircuit {
  if (!Number.isInteger(numPremises) || numPremises < 1) {
    throw new Error('numPremises must be a positive integer');
  }

  const circuit = new ZKPCircuit();
  const premiseWires = Array.from({ length: numPremises }, (_, index) =>
    circuit.addInput(`P${index}`),
  );
  const qWire = circuit.addInput('Q');

  let premisesWire = premiseWires[0];
  for (let index = 1; index < premiseWires.length; index += 1) {
    premisesWire = circuit.addAndGate(premisesWire, premiseWires[index]);
  }

  const resultWire = circuit.addImpliesGate(premisesWire, qWire);
  circuit.setOutput(resultWire);
  return circuit;
}

export function create_implication_circuit(numPremises: number): ZKPCircuit {
  return createImplicationCircuit(numPremises);
}

export function createFormCircuit(circuitVersion = 3): FormCircuit {
  return new FormCircuit(circuitVersion);
}

export function create_form_circuit(circuitVersion = 3): FormCircuit {
  return createFormCircuit(circuitVersion);
}

function sameStringList(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function isTdfolV1Formula(value: string): boolean {
  const normalized = normalizeProofText(value);
  if (!normalized) return false;
  if ((normalized.match(/(?:->|→)/g) ?? []).length > 1) return false;

  const parsed = parseTdfolV1Axiom(normalized);
  if (!isTdfolV1Atom(parsed.consequent)) return false;
  return parsed.antecedent === undefined || isTdfolV1Atom(parsed.antecedent);
}

function isTdfolV1Atom(value: string): boolean {
  const normalized = normalizeProofText(value);
  return /^[A-Za-z][A-Za-z0-9_]*(?:\([A-Za-z0-9_, ]+\))?$/.test(normalized);
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

async function sha256Hex(text: string): Promise<string> {
  const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}
