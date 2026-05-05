import {
  LegalTheoremSyntaxError,
  deriveTdfolV1Trace,
  evaluateTdfolV1Holds,
  parseTdfolV1HornAxiom,
  parseTdfolV1Theorem,
  proveTdfolV1Theorem,
} from './legalTheoremSemantics';

describe('TDFOL_v1 legal theorem semantics', () => {
  it('parses facts, implications, and theorem atoms', () => {
    expect(parseTdfolV1HornAxiom('P')).toEqual({ consequent: 'P' });
    expect(parseTdfolV1HornAxiom('P -> Q')).toEqual({ antecedent: 'P', consequent: 'Q' });
    expect(parseTdfolV1HornAxiom('P & Q -> R')).toEqual({
      antecedents: ['P', 'Q'],
      consequent: 'R',
    });
    expect(parseTdfolV1Theorem('Q')).toBe('Q');
  });

  it('rejects syntax outside the MVP Horn fragment', () => {
    expect(() => parseTdfolV1HornAxiom('')).toThrow(LegalTheoremSyntaxError);
    expect(() => parseTdfolV1HornAxiom('P -> Q -> R')).toThrow("at most one '->'");
    expect(() => parseTdfolV1HornAxiom('1P')).toThrow('must be an atom');
    expect(() => parseTdfolV1HornAxiom('P & 1Q -> R')).toThrow('must be an atom');
    expect(() => parseTdfolV1Theorem('P(x)')).toThrow('must be an atom');
  });

  it('evaluates Horn-fragment derivability by deterministic forward chaining', () => {
    expect(evaluateTdfolV1Holds(['P', 'P -> Q', 'Q -> R'], 'R')).toBe(true);
    expect(evaluateTdfolV1Holds(['P', 'Q', 'P & Q -> R'], 'R')).toBe(true);
    expect(evaluateTdfolV1Holds(['P', 'Q -> R'], 'R')).toBe(false);
    expect(evaluateTdfolV1Holds(['P', 'P & Q -> R'], 'R')).toBe(false);
  });

  it('derives sorted fact-first traces for constraint witnesses', () => {
    expect(deriveTdfolV1Trace(['B -> C', 'A -> B', 'A'], 'C')).toEqual(['A', 'B', 'C']);
    expect(deriveTdfolV1Trace(['B', 'A', 'A & B -> C'], 'C')).toEqual(['A', 'B', 'C']);
    expect(deriveTdfolV1Trace(['B -> C', 'A'], 'C')).toBeUndefined();
  });

  it('returns Python-style proof summaries without external runtimes', () => {
    expect(proveTdfolV1Theorem(['A', 'B', 'A and B -> C'], 'C')).toEqual({
      theorem: 'C',
      holds: true,
      knownFacts: ['A', 'B', 'C'],
      trace: ['A', 'B', 'C'],
    });
    expect(proveTdfolV1Theorem(['A', 'A and B -> C'], 'C')).toEqual({
      theorem: 'C',
      holds: false,
      knownFacts: ['A'],
      trace: undefined,
    });
  });
});
