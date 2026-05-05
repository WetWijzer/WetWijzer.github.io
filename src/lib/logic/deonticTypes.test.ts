import {
  DEONTIC_OPERATORS,
  DEONTIC_TYPES_PORT_METADATA,
  DeonticFormulaType,
  DeonticRuleSetType,
  LegalAgentType,
  TemporalConditionType,
  deonticFormulaFromDict,
  validateDeonticTypesPort,
} from './deonticTypes';

describe('deontic_types.py browser-native parity types', () => {
  it('serializes formula records and renders Python-compatible FOL strings', () => {
    const agent = new LegalAgentType('tenant', 'Tenant', 'role', { party: 'lessee' });
    const formula = new DeonticFormulaType(
      DEONTIC_OPERATORS.OBLIGATION,
      'PayRent(x)',
      agent,
      undefined,
      ['LeaseActive(x)'],
      [new TemporalConditionType('□', 'during lease')],
      undefined,
      0.82,
      'Tenant must pay rent.',
      { x: 'Tenant' },
      [['∀', 'x', 'Tenant']],
      'formula-1',
      '2026-01-01T00:00:00.000Z',
    );

    expect(DEONTIC_TYPES_PORT_METADATA.sourcePythonModule).toBe('logic/types/deontic_types.py');
    expect(agent.hash).toHaveLength(8);
    expect(formula.formula).toBe('O[tenant](□((LeaseActive(x)) → (∀x:Tenant (PayRent(x)))))');
    expect(formula.toDict()).toMatchObject({
      formula_id: 'formula-1',
      operator: 'O',
      agent: { identifier: 'tenant', agent_type: 'role', properties: { party: 'lessee' } },
      confidence: 0.82,
      fol_string: 'O[tenant](□((LeaseActive(x)) → (∀x:Tenant (PayRent(x)))))',
    });
  });

  it('hydrates dict records, checks conflicts, and fails closed on runtime escapes', () => {
    const obligation = deonticFormulaFromDict({
      formula_id: 'obligation-1',
      operator: 'O',
      proposition: 'FileReport(x)',
      agent: { identifier: 'agency', name: 'Agency', agent_type: 'organization' },
      conditions: ['HasNotice(x)'],
      temporal_conditions: [{ operator: 'X', condition: 'next period' }],
      quantifiers: [['∀', 'x', 'Agency']],
    });
    const prohibition = deonticFormulaFromDict({
      formula_id: 'prohibition-1',
      operator: 'F',
      proposition: 'FileReport(x)',
      agent: { identifier: 'agency', name: 'Agency', agent_type: 'organization' },
    });
    const ruleSet = new DeonticRuleSetType('reporting', [obligation, prohibition]);

    expect(obligation.toFolString()).toContain('X((HasNotice(x)) → (∀x:Agency (FileReport(x))))');
    expect(ruleSet.findFormulasByAgent('agency')).toHaveLength(2);
    expect(ruleSet.findFormulasByOperator('F')).toEqual([prohibition]);
    expect(ruleSet.checkConsistency()).toEqual([
      [obligation, prohibition, 'Direct conflict: obligation vs prohibition'],
    ]);
    expect(ruleSet.removeFormula('prohibition-1')).toBe(true);
    expect(validateDeonticTypesPort({ operator: 'POW' })).toMatchObject({ valid: true });
    expect(
      validateDeonticTypesPort({ operator: 'MUST', server_calls_allowed: true }),
    ).toMatchObject({ valid: false });
  });
});
