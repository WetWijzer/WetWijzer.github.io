const ATOM_PATTERN = /^[A-Za-z][A-Za-z0-9_]*$/;

export class LegalTheoremSyntaxError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'LegalTheoremSyntaxError';
  }
}

export interface HornAxiom {
  antecedent?: string;
  antecedents?: string[];
  consequent: string;
}

export interface LegalTheoremProofResult {
  theorem: string;
  holds: boolean;
  knownFacts: string[];
  trace?: string[];
}

export function parseTdfolV1Atom(atom: string, label: string): string {
  const trimmed = String(atom).trim();
  if (!trimmed || !ATOM_PATTERN.test(trimmed)) {
    throw new LegalTheoremSyntaxError(`${label} must be an atom matching [A-Za-z][A-Za-z0-9_]*`);
  }
  return trimmed;
}

export function parseTdfolV1HornAxiom(text: string): HornAxiom {
  if (text === null || text === undefined) {
    throw new LegalTheoremSyntaxError('axiom must be a string');
  }
  const source = String(text).trim();
  if (!source) {
    throw new LegalTheoremSyntaxError('axiom cannot be empty');
  }

  if (source.includes('->')) {
    const parts = source.split('->');
    if (parts.length !== 2) {
      throw new LegalTheoremSyntaxError("axiom may contain at most one '->'");
    }
    const antecedents = parseTdfolV1Antecedents(parts[0]);
    if (antecedents.length === 1) {
      return {
        antecedent: antecedents[0],
        consequent: parseTdfolV1Atom(parts[1], 'axiom consequent'),
      };
    }
    return {
      antecedents,
      consequent: parseTdfolV1Atom(parts[1], 'axiom consequent'),
    };
  }

  return { consequent: parseTdfolV1Atom(source, 'axiom') };
}

export function parse_tdfol_v1_axiom(text: string): HornAxiom {
  return parseTdfolV1HornAxiom(text);
}

function parseTdfolV1Antecedents(text: string): string[] {
  const parts = String(text)
    .split(/\s*(?:&|\band\b)\s*/i)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
  if (parts.length === 0) {
    throw new LegalTheoremSyntaxError('axiom antecedent cannot be empty');
  }
  return parts.map((part) => parseTdfolV1Atom(part, 'axiom antecedent'));
}

function getAntecedents(axiom: HornAxiom): string[] {
  if (axiom.antecedents !== undefined) {
    return axiom.antecedents;
  }
  return axiom.antecedent ? [axiom.antecedent] : [];
}

export function parseTdfolV1Theorem(text: string): string {
  if (text === null || text === undefined) {
    throw new LegalTheoremSyntaxError('theorem must be a string');
  }
  return parseTdfolV1Atom(String(text), 'theorem');
}

export function parse_tdfol_v1_theorem(text: string): string {
  return parseTdfolV1Theorem(text);
}

export function evaluateTdfolV1Holds(privateAxioms: Iterable<string>, theorem: string): boolean {
  const axioms = [...privateAxioms].map(parseTdfolV1HornAxiom);
  const goal = parseTdfolV1Theorem(theorem);
  const known = new Set(
    axioms.filter((axiom) => getAntecedents(axiom).length === 0).map((axiom) => axiom.consequent),
  );
  const implications = axioms.filter((axiom) => getAntecedents(axiom).length > 0);

  let changed = true;
  while (changed) {
    changed = false;
    for (const axiom of implications) {
      const antecedents = getAntecedents(axiom);
      if (
        antecedents.every((antecedent) => known.has(antecedent)) &&
        !known.has(axiom.consequent)
      ) {
        known.add(axiom.consequent);
        changed = true;
      }
    }
  }

  return known.has(goal);
}

export function evaluate_tdfol_v1_holds(privateAxioms: Iterable<string>, theorem: string): boolean {
  return evaluateTdfolV1Holds(privateAxioms, theorem);
}

export function deriveTdfolV1Trace(
  privateAxioms: Iterable<string>,
  theorem: string,
): string[] | undefined {
  const axioms = [...privateAxioms].map(parseTdfolV1HornAxiom);
  const goal = parseTdfolV1Theorem(theorem);
  const facts = [
    ...new Set(
      axioms.filter((axiom) => getAntecedents(axiom).length === 0).map((axiom) => axiom.consequent),
    ),
  ].sort();
  const known = new Set(facts);
  const implications = axioms
    .filter((axiom) => getAntecedents(axiom).length > 0)
    .sort((left, right) =>
      `${getAntecedents(left).join('&')}\u0000${left.consequent}`.localeCompare(
        `${getAntecedents(right).join('&')}\u0000${right.consequent}`,
      ),
    );
  const trace = [...facts];

  let changed = true;
  while (changed) {
    changed = false;
    for (const axiom of implications) {
      const antecedents = getAntecedents(axiom);
      if (
        antecedents.every((antecedent) => known.has(antecedent)) &&
        !known.has(axiom.consequent)
      ) {
        known.add(axiom.consequent);
        trace.push(axiom.consequent);
        changed = true;
      }
    }
  }

  return known.has(goal) ? trace : undefined;
}

export function derive_tdfol_v1_trace(
  privateAxioms: Iterable<string>,
  theorem: string,
): string[] | undefined {
  return deriveTdfolV1Trace(privateAxioms, theorem);
}

export function proveTdfolV1Theorem(
  privateAxioms: Iterable<string>,
  theorem: string,
): LegalTheoremProofResult {
  const axioms = [...privateAxioms].map(parseTdfolV1HornAxiom);
  const goal = parseTdfolV1Theorem(theorem);
  const trace = deriveTdfolV1Trace(axiomsToText(axioms), goal);
  const knownFacts =
    trace ??
    [
      ...new Set(
        axioms
          .filter((axiom) => getAntecedents(axiom).length === 0)
          .map((axiom) => axiom.consequent),
      ),
    ].sort();
  return {
    theorem: goal,
    holds: trace !== undefined,
    knownFacts,
    trace,
  };
}

export function prove_tdfol_v1_theorem(
  privateAxioms: Iterable<string>,
  theorem: string,
): LegalTheoremProofResult {
  return proveTdfolV1Theorem(privateAxioms, theorem);
}

function axiomsToText(axioms: HornAxiom[]): string[] {
  return axioms.map((axiom) => {
    const antecedents = getAntecedents(axiom);
    return antecedents.length === 0
      ? axiom.consequent
      : `${antecedents.join(' & ')} -> ${axiom.consequent}`;
  });
}
