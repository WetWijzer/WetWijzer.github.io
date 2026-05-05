import {
  CecGrammarEngine,
  CecGrammarLoader,
  CecGrammarRule,
  CecLexicalEntry,
  createDefaultCecGrammarEngine,
  createDefaultCecGrammarLoader,
} from './grammarEngine';

describe('CEC grammar loader and engine', () => {
  it('loads default grammar sections and operator metadata without filesystem access', () => {
    const loader = createDefaultCecGrammarLoader();
    const artifact = loader.getArtifact();

    expect(loader.getConfig()).toMatchObject({
      version: '1.0',
      language: 'en',
      caseSensitive: false,
    });
    expect(loader.validate()).toBe(true);
    expect(loader.validateDetailed()).toEqual({ valid: true, issues: [] });
    expect(artifact.source).toBe('in-memory');
    expect(artifact.runtime).toBe('browser-native');
    expect(artifact.externalResourcePolicy).toBe('none');
    expect(artifact.allWords).toEqual(
      expect.arrayContaining(['and', 'must', 'believes', 'always', 'every']),
    );
    expect(loader.getWordsForOperator('deontic', 'obligation')).toEqual([
      'must',
      'obligated',
      'should',
      'required',
    ]);
    expect(loader.getWordsForOperator('connectives', 'and')).toEqual(['and']);
    expect(loader.getSemantics('temporal', 'always')).toEqual({
      type: 'temporal',
      operator: 'always',
    });
    expect(loader.getExamples('connectives', 'and')).toEqual(['Alice loves Bob and Carol']);
    expect(loader.getProductionRules().compound[0].pattern).toBe(
      '{sentence} {connective} {sentence}',
    );
    expect(loader.getAllWords()).toEqual(
      expect.arrayContaining(['and', 'must', 'believes', 'always', 'every']),
    );
  });

  it('accepts static browser-native grammar data and validates required sections', () => {
    const loader = new CecGrammarLoader({
      config: { version: '2.0', language: 'en-GB', case_sensitive: true },
      connectives: {},
      deontic: {},
      cognitive: {},
      temporal: {},
      quantifiers: {},
    });
    const invalid = new CecGrammarLoader({ connectives: {} });

    expect(loader.getConfig()).toMatchObject({
      version: '2.0',
      language: 'en-GB',
      caseSensitive: true,
    });
    expect(loader.validate()).toBe(true);
    expect(invalid.validate()).toBe(false);
  });

  it('reports loader validation issues for malformed static artifacts without fetching fallbacks', () => {
    const originalFetch = (globalThis as unknown as { fetch?: () => Promise<unknown> }).fetch;
    (globalThis as unknown as { fetch?: () => Promise<unknown> }).fetch = () => {
      throw new Error('network access is not allowed in CEC grammar tests');
    };

    try {
      const loader = new CecGrammarLoader({
        config: { version: '', language: '' },
        connectives: {
          and: { word: 'and' },
          duplicateAnd: { word: 'and' },
          empty: { word: '' },
        },
        deontic: {
          obligation: {},
        },
        cognitive: {},
        temporal: {},
        quantifiers: {},
        production_rules: {
          sentence: [{ pattern: '' }],
        },
      });

      const validation = loader.validateDetailed();
      const artifact = loader.getArtifact();

      expect(loader.validate()).toBe(false);
      expect(validation.valid).toBe(false);
      expect(validation.issues.map((issue) => issue.code)).toEqual([
        'missing-config-version',
        'missing-config-language',
        'duplicate-operator-word',
        'empty-operator-word',
        'missing-operator-surface',
        'empty-production-pattern',
      ]);
      expect(artifact.source).toBe('in-memory');
      expect(artifact.externalResourcePolicy).toBe('none');
      expect(artifact.sections.connectives.and.word).toBe('and');
    } finally {
      (globalThis as unknown as { fetch?: () => Promise<unknown> }).fetch = originalFetch;
    }
  });

  it('applies grammar rules and parses with bottom-up chart parsing', () => {
    const engine = new CecGrammarEngine();
    engine.addLexicalEntry(
      new CecLexicalEntry({ word: 'alice', category: 'Agent', semantics: 'alice' }),
    );
    engine.addLexicalEntry(
      new CecLexicalEntry({ word: 'appeal', category: 'ActionType', semantics: 'appeal' }),
    );
    engine.addLexicalEntry(new CecLexicalEntry({ word: 'may', category: 'V', semantics: 'P' }));
    engine.addRule(
      new CecGrammarRule({
        name: 'AgentToSentence',
        category: 'Sentence',
        constituents: ['Agent'],
        semanticFn: ([agent]) => agent,
      }),
    );
    engine.addRule(
      new CecGrammarRule({
        name: 'ModalAction',
        category: 'VP',
        constituents: ['V', 'ActionType'],
        semanticFn: ([modal, action]) => ({ modal, action }),
      }),
    );
    engine.addRule(
      new CecGrammarRule({
        name: 'SentenceVP',
        category: 'Utterance',
        constituents: ['Sentence', 'VP'],
        semanticFn: ([agent, vp]) => ({ agent, ...(vp as Record<string, unknown>) }),
        linearizeFn: (value) => {
          const record = value as { agent: string; modal: string; action: string };
          return `${record.agent} ${record.modal === 'P' ? 'may' : record.modal} ${record.action}`;
        },
      }),
    );

    const parses = engine.parse('Alice may appeal');

    expect(parses).toHaveLength(1);
    expect(parses[0].semantics).toEqual({ agent: 'alice', modal: 'P', action: 'appeal' });
    expect(parses[0].span).toEqual([0, 3]);
    expect(parses[0].linearize()).toBe('alice may appeal');
    expect(engine.linearize(parses[0].semantics, 'Utterance')).toBe('alice may appeal');
  });

  it('parses Python-style n-ary grammar productions without runtime services', () => {
    const engine = new CecGrammarEngine();
    engine.addLexicalEntry(
      new CecLexicalEntry({ word: 'alice', category: 'Agent', semantics: 'alice' }),
    );
    engine.addLexicalEntry(new CecLexicalEntry({ word: 'must', category: 'V', semantics: 'O' }));
    engine.addLexicalEntry(
      new CecLexicalEntry({ word: 'appeal', category: 'ActionType', semantics: 'appeal' }),
    );
    engine.addRule(
      new CecGrammarRule({
        name: 'ModalSentence',
        category: 'Utterance',
        constituents: ['Agent', 'V', 'ActionType'],
        semanticFn: ([agent, modal, action]) => ({ agent, modal, action }),
        linearizeFn: (value) => {
          const record = value as { agent: string; modal: string; action: string };
          return `${record.agent} ${record.modal === 'O' ? 'must' : record.modal} ${record.action}`;
        },
      }),
    );

    const parses = engine.parse('Alice must appeal');

    expect(parses).toHaveLength(1);
    expect(parses[0].semantics).toEqual({ agent: 'alice', modal: 'O', action: 'appeal' });
    expect(parses[0].span).toEqual([0, 3]);
    expect(parses[0].children.map((child) => child.category)).toEqual(['Agent', 'V', 'ActionType']);
    expect(engine.validateGrammar()).toEqual({ valid: true, issues: [] });
  });

  it('sets up default Python grammar_engine-style lexicon and production rules in browser-native TypeScript', () => {
    const engine = createDefaultCecGrammarEngine();
    engine.addLexicalEntries([
      { word: 'alice', category: 'Agent', semantics: 'alice' },
      { word: 'bob', category: 'Agent', semantics: 'bob' },
      { word: 'appeal', category: 'ActionType', semantics: 'appeal' },
      { word: 'respond', category: 'ActionType', semantics: 'respond' },
      { word: 'ready', category: 'Fluent', semantics: 'ready' },
      { word: 'records', category: 'N', semantics: 'records' },
      { word: 'home', category: 'Object', semantics: 'home' },
    ]);

    expect(engine.validateGrammar()).toEqual({ valid: true, issues: [] });
    expect(engine.parse('Alice must appeal')[0].semantics).toEqual({
      type: 'deontic',
      agent: 'alice',
      modality: 'obligated',
      action: 'appeal',
    });
    expect(engine.parse('Alice must not appeal')[0].semantics).toEqual({
      type: 'deontic',
      agent: 'alice',
      modality: 'forbidden',
      action: 'appeal',
    });
    expect(engine.parse('every records')[0].semantics).toEqual({
      type: 'quantified_entity',
      quantifier: 'forall',
      noun: 'records',
    });
    expect(engine.parse('Alice must appeal and Bob may respond')[0].semantics).toMatchObject({
      type: 'compound',
      connective: 'AND',
    });
  });

  it('compiles placeholder-only Python production_rules and records unsupported literal patterns', () => {
    const engine = createDefaultCecGrammarEngine();
    engine.addLexicalEntries([
      { word: 'alice', category: 'Agent', semantics: 'alice' },
      { word: 'appeal', category: 'ActionType', semantics: 'appeal' },
      { word: 'home', category: 'Object', semantics: 'home' },
      { word: 'ready', category: 'Fluent', semantics: 'ready' },
      { word: 'records', category: 'N', semantics: 'records' },
    ]);

    const productionRule = engine.rules.find(
      (rule) => rule.name === 'CecPythonProduction:sentence:0',
    );
    const parses = engine.parse('Alice appeal home');

    expect(productionRule?.constituents).toEqual(['Agent', 'ActionType', 'Object']);
    expect(productionRule?.sourcePattern).toBe('{subject} {verb} {object}');
    expect(parses[0].semantics).toEqual({
      type: 'production',
      group: 'sentence',
      pattern: '{subject} {verb} {object}',
      values: ['alice', 'appeal', 'home'],
    });
    expect(engine.unsupportedProductionPatterns).toEqual([
      expect.objectContaining({
        code: 'unsupported-production-pattern',
        ruleName: 'compound.1',
        pattern: 'if {condition} then {consequence}',
      }),
    ]);
    expect(engine.validateGrammar()).toEqual({ valid: true, issues: [] });
  });

  it('supports browser-native bulk grammar setup and optional case-sensitive tokenization', () => {
    const engine = new CecGrammarEngine({ caseSensitive: true });
    engine.addLexicalEntries([
      { word: 'Alice', category: 'Agent', semantics: 'Alice' },
      { word: 'must', category: 'V', semantics: 'O' },
      { word: 'appeal', category: 'ActionType', semantics: 'appeal' },
    ]);
    engine.addRules([
      {
        name: 'CaseSensitiveModalSentence',
        category: 'Utterance',
        constituents: ['Agent', 'V', 'ActionType'],
        semanticFn: ([agent, modal, action]) => ({ agent, modal, action }),
      },
    ]);

    expect(engine.parse('Alice must appeal')[0].semantics).toEqual({
      agent: 'Alice',
      modal: 'O',
      action: 'appeal',
    });
    expect(engine.parse('alice must appeal')).toEqual([]);
    expect(engine.validateGrammar()).toEqual({ valid: true, issues: [] });
  });

  it('validates fail-closed grammar contracts before parsing', () => {
    const engine = new CecGrammarEngine();
    engine.addLexicalEntry(
      new CecLexicalEntry({ word: 'alice', category: 'Agent', semantics: 'alice' }),
    );
    engine.addRule(
      new CecGrammarRule({
        name: 'BrokenModalSentence',
        category: 'Utterance',
        constituents: ['Agent', 'V', 'ActionType'],
        semanticFn: ([agent, modal, action]) => ({ agent, modal, action }),
      }),
    );

    const validation = engine.validateGrammar();

    expect(validation.valid).toBe(false);
    expect(validation.issues.map((issue) => issue.code)).toEqual([
      'unreachable-constituent',
      'unreachable-start-category',
    ]);
    expect(engine.parse('Alice must appeal')).toEqual([]);
  });

  it('resolves ambiguity by first, shortest, and most specific strategies', () => {
    const engine = new CecGrammarEngine();
    const short = {
      category: 'Utterance' as const,
      children: [],
      semantics: 'short',
      span: [0, 1] as [number, number],
      isLexical: () => false,
      linearize: () => 'short',
    };
    const specific = {
      category: 'Utterance' as const,
      children: [
        {
          category: 'Agent' as const,
          children: [],
          semantics: 'alice',
          span: [0, 1] as [number, number],
          isLexical: () => true,
          linearize: () => 'alice',
        },
        {
          category: 'ActionType' as const,
          children: [],
          semantics: 'appeal',
          span: [1, 2] as [number, number],
          isLexical: () => true,
          linearize: () => 'appeal',
        },
      ],
      semantics: 'specific',
      span: [0, 2] as [number, number],
      isLexical: () => false,
      linearize: () => 'specific',
    };

    expect(engine.resolveAmbiguity([specific as never, short as never], 'first')).toBe(specific);
    expect(engine.resolveAmbiguity([specific as never, short as never], 'shortest')).toBe(short);
    expect(engine.resolveAmbiguity([short as never, specific as never], 'most_specific')).toBe(
      specific,
    );
    expect(engine.resolveAmbiguity([])).toBeUndefined();
  });

  it('falls back to string linearization when no rule handles a category', () => {
    const engine = new CecGrammarEngine();
    expect(engine.parse('unknown tokens')).toEqual([]);
    expect(engine.linearize({ raw: true }, 'Sentence')).toBe('[object Object]');
  });
});
