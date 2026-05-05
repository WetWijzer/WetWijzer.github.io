import {
  DCEC_TYPES_METADATA,
  DcecDeonticOperator,
  DcecFunctionSymbol,
  DcecLogicalConnective,
  DcecPredicateSymbol,
  DcecSort,
  DcecVariable,
  describeDcecNativeType,
  deserializeDcecSymbolContainer,
  getDcecOperatorFamily,
  serializeDcecSymbolContainer,
  validateDcecSymbolContainerJson,
} from './dcecTypes';

describe('DCEC native type descriptors', () => {
  it('exposes dcec_types.py metadata and operator/type descriptors', () => {
    const entity = new DcecSort('Entity');
    const agent = new DcecSort('Agent', entity);
    const func = new DcecFunctionSymbol('owner', [agent], entity);
    const pred = new DcecPredicateSymbol('authorized', [agent, entity]);

    expect(DCEC_TYPES_METADATA).toMatchObject({
      sourcePythonModule: 'logic/CEC/native/dcec_types.py',
      browserNative: true,
      pythonRuntime: false,
      serverRuntime: false,
      subprocess: false,
      rpc: false,
    });
    expect(getDcecOperatorFamily(DcecDeonticOperator.OBLIGATION)).toBe('deontic');
    expect(getDcecOperatorFamily(DcecLogicalConnective.IMPLIES)).toBe('logical');
    expect(describeDcecNativeType(agent)).toMatchObject({
      kind: 'sort',
      name: 'Agent',
      parent: 'Entity',
    });
    expect(describeDcecNativeType(new DcecVariable('a', agent))).toMatchObject({
      kind: 'variable',
      sort: 'Agent',
    });
    expect(describeDcecNativeType(func)).toMatchObject({
      kind: 'function',
      arity: 1,
      returnSort: 'Entity',
    });
    expect(describeDcecNativeType(pred)).toMatchObject({ kind: 'predicate', arity: 2 });
    expect(describeDcecNativeType(DcecDeonticOperator.PERMISSION)).toMatchObject({
      kind: 'operator',
      operatorFamily: 'deontic',
      symbol: 'P',
    });
  });

  it('validates and revives serialized symbol containers fail-closed', () => {
    const entity = new DcecSort('Entity');
    const agent = new DcecSort('Agent', entity);
    const payload = serializeDcecSymbolContainer({
      sorts: [entity, agent],
      variables: [new DcecVariable('tenant', agent)],
      functions: [new DcecFunctionSymbol('delegate', [agent], agent)],
      predicates: [new DcecPredicateSymbol('pays', [agent])],
    });
    const restored = deserializeDcecSymbolContainer(payload)!;

    expect(validateDcecSymbolContainerJson(payload)).toEqual({
      ok: true,
      errors: [],
      metadata: DCEC_TYPES_METADATA,
    });
    expect(restored.sorts[1].parent?.name).toBe('Entity');
    expect(String(restored.variables[0])).toBe('tenant:Agent');
    expect(String(restored.functions[0])).toBe('delegate(Agent) -> Agent');
    expect(String(restored.predicates[0])).toBe('pays(Agent)');

    const invalid = {
      ...payload,
      predicates: [{ kind: 'predicate', name: 'ghost', argumentSorts: ['Missing'] }],
    };
    expect(validateDcecSymbolContainerJson(invalid)).toMatchObject({
      ok: false,
      errors: ["predicate 'ghost' references missing sort 'Missing'"],
    });
    expect(deserializeDcecSymbolContainer(invalid)).toBeUndefined();
  });
});
