import { parseCecExpression } from './parser';
import {
  DcecContainer,
  DcecNamespace,
  DcecNamespaceError,
  isDcecNamespaceJson,
} from './dcecNamespace';
import {
  DcecCognitiveOperator,
  DcecDeonticOperator,
  DcecFunctionSymbol,
  DcecLogicalConnective,
  DcecPredicateSymbol,
  DcecSort,
  DcecTemporalOperator,
  DcecVariable,
  isDcecFunctionSymbol,
  isDcecPredicateSymbol,
  isDcecSort,
  isDcecSymbolJson,
  isDcecVariable,
  serializeDcecSymbolContainer,
} from './dcecTypes';

describe('DCEC namespace and type utilities', () => {
  it('models DCEC operator aliases as browser-native constants', () => {
    expect(DcecDeonticOperator.OBLIGATION).toBe('O');
    expect(DcecDeonticOperator.OBLIGATORY).toBe('O');
    expect(DcecCognitiveOperator.KNOWLEDGE).toBe('K');
    expect(DcecCognitiveOperator.KNOWS).toBe('K');
    expect(DcecLogicalConnective.FORALL).toBe('forAll');
    expect(DcecTemporalOperator.UNTIL).toBe('until');
  });

  it('supports subtype checks and Python-compatible symbol rendering', () => {
    const entity = new DcecSort('Entity');
    const agent = new DcecSort('Agent', entity);
    const human = new DcecSort('Human', agent);
    const variable = new DcecVariable('x', human);
    const age = new DcecFunctionSymbol('age', [human], new DcecSort('Number'));
    const eligible = new DcecPredicateSymbol('eligible', [human]);

    expect(human.isSubtypeOf(entity)).toBe(true);
    expect(entity.isSubtypeOf(human)).toBe(false);
    expect(String(variable)).toBe('x:Human');
    expect(age.arity()).toBe(1);
    expect(String(age)).toBe('age(Human) -> Number');
    expect(eligible.arity()).toBe(1);
    expect(String(eligible)).toBe('eligible(Human)');
  });

  it('serializes DCEC type symbols and guards Python-compatible JSON records', () => {
    const entity = new DcecSort('Entity');
    const agent = new DcecSort('Agent', entity);
    const variable = new DcecVariable('a', agent);
    const functionSymbol = new DcecFunctionSymbol('actorOf', [new DcecSort('Action')], agent);
    const predicate = new DcecPredicateSymbol('liable', [agent]);

    expect(isDcecSort(agent)).toBe(true);
    expect(isDcecVariable(variable)).toBe(true);
    expect(isDcecFunctionSymbol(functionSymbol)).toBe(true);
    expect(isDcecPredicateSymbol(predicate)).toBe(true);
    expect(isDcecSymbolJson({ kind: 'variable', name: 'a', sort: 'Agent' })).toBe(true);
    expect(isDcecSymbolJson({ kind: 'function', name: 'bad', argumentSorts: ['Agent'] })).toBe(
      false,
    );
  });

  it('serializes DCEC symbol containers without Python runtime support', () => {
    const namespace = new DcecNamespace();
    namespace.registerFunction('actorOf', ['Action'], 'Agent');
    namespace.registerPredicate('liable', ['Agent']);
    namespace.registerVariable('a', 'Agent');

    const serialized = serializeDcecSymbolContainer({
      sorts: namespace.sorts.values(),
      variables: namespace.variables.values(),
      functions: namespace.functions.values(),
      predicates: namespace.predicates.values(),
    });

    expect(serialized.sorts.find((sort) => sort.name === 'Agent')).toEqual({
      kind: 'sort',
      name: 'Agent',
      parent: 'Entity',
    });
    expect(serialized.variables).toEqual([{ kind: 'variable', name: 'a', sort: 'Agent' }]);
    expect(serialized.functions).toEqual([
      { kind: 'function', name: 'actorOf', argumentSorts: ['Action'], returnSort: 'Agent' },
    ]);
    expect(serialized.predicates).toEqual([
      { kind: 'predicate', name: 'liable', argumentSorts: ['Agent'] },
    ]);
    expect(serialized.functions.every(isDcecSymbolJson)).toBe(true);
  });

  it('round-trips namespace snapshots through deterministic browser-native JSON', () => {
    const namespace = new DcecNamespace();
    namespace.registerSort('Document', 'Entity');
    namespace.registerSort('Contract', 'Document');
    namespace.registerVariable('party', 'Agent');
    namespace.registerFunction('signedDocument', ['Agent'], 'Document');
    namespace.registerPredicate('validContract', ['Contract']);

    const json = namespace.toJSON();
    const restored = DcecNamespace.fromJSON(json);

    expect(isDcecNamespaceJson(json)).toBe(true);
    expect(json).toEqual({
      kind: 'namespace',
      version: 1,
      sorts: [
        { kind: 'sort', name: 'Entity' },
        { kind: 'sort', name: 'Boolean' },
        { kind: 'sort', name: 'Moment' },
        { kind: 'sort', name: 'Event' },
        { kind: 'sort', name: 'Action' },
        { kind: 'sort', name: 'Agent', parent: 'Entity' },
        { kind: 'sort', name: 'ActionType' },
        { kind: 'sort', name: 'Obligation', parent: 'Boolean' },
        { kind: 'sort', name: 'Permission', parent: 'Boolean' },
        { kind: 'sort', name: 'Document', parent: 'Entity' },
        { kind: 'sort', name: 'Contract', parent: 'Document' },
      ],
      variables: [{ kind: 'variable', name: 'party', sort: 'Agent' }],
      functions: [
        {
          kind: 'function',
          name: 'signedDocument',
          argumentSorts: ['Agent'],
          returnSort: 'Document',
        },
      ],
      predicates: [{ kind: 'predicate', name: 'validContract', argumentSorts: ['Contract'] }],
    });
    expect(restored.toJSON()).toEqual(json);
    expect(restored.getSort('Contract')?.isSubtypeOf(restored.getSort('Entity')!)).toBe(true);
    expect(restored.validate()).toEqual({ valid: true, diagnostics: [] });
  });

  it('fails closed for malformed namespace snapshots and unresolved sort parents', () => {
    expect(isDcecNamespaceJson({ kind: 'namespace', version: 1, sorts: [] })).toBe(false);
    expect(() => DcecNamespace.fromJSON({ kind: 'namespace', version: 2 })).toThrow(
      DcecNamespaceError,
    );
    expect(() =>
      DcecNamespace.fromJSON({
        kind: 'namespace',
        version: 1,
        sorts: [{ kind: 'sort', name: 'Contract', parent: 'MissingSort' }],
        variables: [],
        functions: [],
        predicates: [],
      }),
    ).toThrow(DcecNamespaceError);
  });

  it('initializes Python-compatible built-in sorts and statistics', () => {
    const namespace = new DcecNamespace();

    expect([...namespace.sorts.keys()]).toEqual([
      'Entity',
      'Boolean',
      'Moment',
      'Event',
      'Action',
      'Agent',
      'ActionType',
      'Obligation',
      'Permission',
    ]);
    expect(namespace.getSort('Agent')?.isSubtypeOf(namespace.getSort('Entity')!)).toBe(true);
    expect(namespace.getSort('Obligation')?.isSubtypeOf(namespace.getSort('Boolean')!)).toBe(true);
    expect(namespace.getStatistics()).toEqual({
      sorts: 9,
      variables: 0,
      functions: 0,
      predicates: 0,
    });
    expect(String(namespace)).toBe('DCECNamespace(sorts=9, vars=0, funcs=0, preds=0)');
  });

  it('adds and retrieves variables, functions, and predicates with sort validation', () => {
    const namespace = new DcecNamespace();
    namespace.registerSort('Number');
    const variable = namespace.registerVariable('agent', 'Agent');
    const functionSymbol = namespace.registerFunction('ownerOf', ['Action'], 'Agent');
    const predicate = namespace.registerPredicate('authorized', ['Agent', 'Action']);
    const autoPredicate = namespace.getPredicate('implicitFact', 0);

    expect(variable).toBe(namespace.getVariable('agent'));
    expect(functionSymbol).toBe(namespace.getFunction('ownerOf'));
    expect(predicate).toBe(namespace.getPredicate('authorized'));
    expect(autoPredicate?.arity()).toBe(0);
    expect(namespace.getStatistics()).toEqual({
      sorts: 10,
      variables: 1,
      functions: 1,
      predicates: 2,
    });
    expect(namespace.getSymbolStatistics()).toMatchObject({
      sorts: 10,
      variables: 1,
      functions: 1,
      predicates: 2,
      totalSymbols: 14,
      builtinSorts: 9,
      customSorts: 1,
      maxFunctionArity: 1,
      maxPredicateArity: 2,
      collisions: [],
    });
  });

  it('rejects cross-kind symbol collisions during namespace registration', () => {
    const namespace = new DcecNamespace();

    expect(() => namespace.registerVariable('Agent', 'Agent')).toThrow(DcecNamespaceError);
    try {
      namespace.registerSort('Document', 'Entity');
      namespace.registerPredicate('Document', ['Agent']);
    } catch (error) {
      expect(error).toBeInstanceOf(DcecNamespaceError);
      expect((error as DcecNamespaceError).symbol).toBe('Document');
      expect((error as DcecNamespaceError).operation).toBe('add_predicate');
      expect((error as DcecNamespaceError).suggestion).toContain(
        'unique DCEC namespace symbol name',
      );
    }
  });

  it('validates diagnostics for externally corrupted namespace maps', () => {
    const namespace = new DcecNamespace();
    const orphanSort = new DcecSort('Orphan');
    namespace.variables.set('dangling', new DcecVariable('dangling', orphanSort));
    namespace.functions.set('Agent', new DcecFunctionSymbol('Agent', [orphanSort], orphanSort));

    const validation = namespace.validate();

    expect(validation.valid).toBe(false);
    expect(validation.diagnostics.map((diagnostic) => diagnostic.code)).toEqual([
      'symbol_collision',
      'missing_sort_reference',
      'missing_sort_reference',
      'missing_sort_reference',
    ]);
    expect(validation.diagnostics[0]).toMatchObject({
      symbol: 'Agent',
      operation: 'validate',
      severity: 'error',
    });
    expect(namespace.getSymbolStatistics().collisions).toEqual([
      { name: 'Agent', kinds: ['sort', 'function'] },
    ]);
  });

  it('reports namespace errors with symbol, operation, and suggestions', () => {
    const namespace = new DcecNamespace();

    expect(() => namespace.addSort('Entity')).toThrow(DcecNamespaceError);
    try {
      namespace.addVariable('x', 'MissingSort');
    } catch (error) {
      expect(error).toBeInstanceOf(DcecNamespaceError);
      expect((error as DcecNamespaceError).symbol).toBe('MissingSort');
      expect((error as DcecNamespaceError).operation).toBe('lookup');
      expect((error as DcecNamespaceError).suggestion).toContain(
        "Register sort 'MissingSort' first",
      );
    }
  });

  it('stores statements, axioms, and theorems while preserving the namespace on clear', () => {
    const container = new DcecContainer();
    const axiom = parseCecExpression('(implies (Permit applicant) (O review))');
    const theorem = parseCecExpression('(O review)');

    const axiomStatement = container.addAxiom(axiom, 'ax1', { source: 'fixture' });
    const theoremStatement = container.addTheorem(theorem, 'th1');

    expect(container.getStatement('ax1')).toBe(axiomStatement);
    expect(container.getStatement('th1')).toBe(theoremStatement);
    expect(container.getAxioms()).toEqual([axiomStatement]);
    expect(container.getTheorems()).toEqual([theoremStatement]);
    expect(container.getStatistics()).toMatchObject({
      total_statements: 2,
      axioms: 1,
      theorems: 1,
      labeled_statements: 2,
    });
    expect(() => container.addStatement(theorem, { label: 'ax1' })).toThrow(DcecNamespaceError);

    container.clear();
    expect(container.getAllStatements()).toEqual([]);
    expect(container.namespace.getStatistics().sorts).toBe(9);
    expect(String(container)).toBe('DCECContainer(statements=0, axioms=0, theorems=0)');
  });
});
