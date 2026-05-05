import {
  checkDcecParens,
  cleanDcecLegalText,
  cleanDcecExpression,
  consolidateDcecParens,
  cleanupDcecTokens,
  functorizeDcecSymbols,
  getMatchingDcecCloseParen,
  normalizeDcecText,
  removeDcecSemicolonComments,
  stripDcecComments,
  stripDcecWhitespace,
  tuckDcecFunctions,
} from './dcecCleaning';

describe('DCEC cleaning utilities', () => {
  it('normalizes whitespace, commas, and bracket spacing', () => {
    expect(stripDcecWhitespace('  ( a  b  c )  ')).toBe('(a,b,c)');
    expect(stripDcecWhitespace('func( arg1 , arg2 )')).toBe('func(arg1,arg2)');
    expect(stripDcecWhitespace('[x] (a)(b)')).toBe(',[x],(a),(b)');
  });

  it('strips hash and semicolon comments independently', () => {
    expect(stripDcecComments('(and a b) # comment')).toBe('(and a b) ');
    expect(stripDcecComments('no comment')).toBe('no comment');
    expect(removeDcecSemicolonComments('(and a b) ; comment')).toBe('(and a b) ');
    expect(removeDcecSemicolonComments('no comment')).toBe('no comment');
  });

  it('checks and locates ordered matching parentheses', () => {
    expect(checkDcecParens('(and a b)')).toBe(true);
    expect(checkDcecParens('(and a b')).toBe(false);
    expect(checkDcecParens(')and a b(')).toBe(false);
    expect(getMatchingDcecCloseParen('(a (b c) d)', 0)).toBe(10);
    expect(getMatchingDcecCloseParen('(a (b c) d)', 3)).toBe(7);
    expect(getMatchingDcecCloseParen('(a (b c)', 0)).toBeUndefined();
  });

  it('consolidates redundant parentheses and preserves meaningful grouping', () => {
    expect(consolidateDcecParens('((a))')).toBe('(a)');
    expect(consolidateDcecParens('((and a b))')).toBe('(and a b)');
    expect(consolidateDcecParens('(and (a) (b))')).toBe('(and a b)');
  });

  it('tucks nested F-expression function calls into S-expression-style notation', () => {
    expect(tuckDcecFunctions('B(a,b)')).toBe('(B,a,b)');
    expect(tuckDcecFunctions('Event(e1)')).toBe('(Event,e1)');
    expect(tuckDcecFunctions('not(P)')).toBe('(not,(P))');
    expect(tuckDcecFunctions('Happens(Attack(e),t1)')).toBe('(Happens,(Attack,e),t1)');
  });

  it('functorizes symbolic operators with longest-match replacements', () => {
    expect(functorizeDcecSymbols('a -> b')).toBe('a  implies  b');
    expect(functorizeDcecSymbols('x + y')).toBe('x  add  y');
    expect(functorizeDcecSymbols('~p')).toBe(' not p');
    expect(functorizeDcecSymbols('a >= b')).toBe('a  greaterOrEqual  b');
    expect(functorizeDcecSymbols('a <-> b')).toBe('a  ifAndOnlyIf  b');
  });

  it('runs the standard cleaning pipeline without Python or server fallbacks', () => {
    expect(cleanDcecExpression('  ((and a b)) # comment')).toBe('(and,a,b)');
    expect(cleanDcecExpression('Happens(Attack(e),t1) ; ignored')).toBe('(Happens,(Attack,e),t1)');
    expect(cleanDcecExpression('(a -> b)')).toBe('(a,implies,b)');
    expect(cleanDcecExpression('(∀ x) (Permitted(x) → Safe(x))')).toBe(
      '((forall,x),((Permitted,x),implies,(Safe,x)))',
    );
    expect(cleanDcecExpression(')and a b(')).toBe('');
  });

  it('normalizes legal-text punctuation and Unicode formula operators', () => {
    expect(normalizeDcecText(' “Duty” — (¬Breach(x) ∧ Notice(x)); trailing note')).toBe(
      '"Duty" - ( not Breach(x) and Notice(x))',
    );
    expect(cleanupDcecTokens('(Claim(x) iff Defense(y)) # docket note')).toEqual([
      '(',
      'Claim',
      '(',
      'x',
      ')',
      'ifAndOnlyIf',
      'Defense',
      '(',
      'y',
      ')',
      ')',
    ]);
  });

  it('returns fail-closed fixture results for malformed legal-text inputs', () => {
    const malformedFixtures = [
      {
        input: 'Section 12(a) says (Obligated(agent,act) → Done(act)',
        warning: 'unbalanced-parentheses',
      },
      {
        input: '   # only a margin comment',
        warning: 'empty-input',
      },
    ];

    for (const fixture of malformedFixtures) {
      const result = cleanDcecLegalText(fixture.input);
      expect(result.cleaned).toBe('');
      expect(result.rejected).toBe(true);
      expect(result.warnings).toContain(fixture.warning);
    }
  });

  it('cleans normalized legal formulas while preserving browser-native token metadata', () => {
    const result = cleanDcecLegalText('Happens(“Filing”(case_1), t1) ∧ Valid(case_1) ; clerk note');

    expect(result.cleaned).toBe('((Happens,(Filing,case_1),t1),and,(Valid,case_1))');
    expect(result.rejected).toBe(false);
    expect(result.tokens).toContain('and');
    expect(result.normalizedText).toBe('Happens("Filing"(case_1), t1) and Valid(case_1)');
  });
});
