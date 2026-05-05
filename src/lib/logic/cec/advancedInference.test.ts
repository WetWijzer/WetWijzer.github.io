import {
  DcecCognitiveFormula,
  DcecDeonticFormula,
  DcecTemporalFormula,
  dcecAtom,
  dcecConjunction,
  dcecImplication,
} from './dcecCore';
import {
  DcecCognitiveOperator,
  DcecDeonticOperator,
  DcecSort,
  DcecTemporalOperator,
  DcecVariable,
} from './dcecTypes';
import { DcecVariableTerm } from './dcecCore';
import {
  classifyDcecAdvancedFormula,
  classifyDcecAdvancedFormulas,
  DcecDeonticDRule,
  DcecDeonticDistribution,
  DcecDeonticPermissionObligation,
  DcecFrameAxiom,
  deriveDcecAdvancedInferences,
  getDcecAdvancedInferenceRegistry,
  DcecKnowledgeObligation,
  DcecModalKAxiom,
  DcecModalNecessitation,
  DcecModalS4Axiom,
  DcecModalTAxiom,
  DcecTemporalInduction,
  DcecTemporalObligation,
  getAllDcecAdvancedRules,
  getDcecCombinedRules,
  getDcecDeonticRules,
  getDcecModalRules,
  getDcecTemporalRules,
  selectDcecAdvancedInferenceRules,
} from './advancedInference';

const agent = new DcecVariableTerm(new DcecVariable('agent', new DcecSort('Agent')));
const p = dcecAtom('p');
const q = dcecAtom('q');

describe('DCEC advanced inference parity rules', () => {
  it('applies modal K, T, S4, and necessitation rules', () => {
    const knowledgeImplication = new DcecCognitiveFormula(
      DcecCognitiveOperator.KNOWLEDGE,
      agent,
      dcecImplication(p, q),
    );

    const k = new DcecModalKAxiom();
    const t = new DcecModalTAxiom();
    const s4 = new DcecModalS4Axiom();
    const necessitation = new DcecModalNecessitation();

    expect(k.canApply([knowledgeImplication])).toBe(true);
    expect(k.apply([knowledgeImplication]).map(String)).toEqual([
      '(K(agent:Agent, p()) → K(agent:Agent, q()))',
    ]);
    expect(t.apply([knowledgeImplication]).map(String)).toEqual(['(p() → q())']);
    expect(s4.apply([knowledgeImplication]).map(String)).toEqual([
      'K(agent:Agent, K(agent:Agent, (p() → q())))',
    ]);
    expect(necessitation.apply([p, knowledgeImplication]).map(String)).toEqual([
      'K(system:System, p())',
    ]);
  });

  it('applies temporal induction and frame axiom rules', () => {
    const temporal = new DcecTemporalInduction();
    const frame = new DcecFrameAxiom();

    expect(temporal.canApply([p, dcecImplication(p, q)])).toBe(true);
    expect(temporal.apply([p, dcecImplication(p, q)]).map(String)).toEqual(['q()']);
    expect(frame.canApply([p])).toBe(true);
    expect(frame.apply([p, dcecImplication(p, q)]).map(String)).toEqual(['p()']);
  });

  it('applies deontic D, permission-obligation duality, and distribution rules', () => {
    const obligation = new DcecDeonticFormula(DcecDeonticOperator.OBLIGATION, p, agent);
    const permission = new DcecDeonticFormula(DcecDeonticOperator.PERMISSION, p, agent);
    const distributed = new DcecDeonticFormula(
      DcecDeonticOperator.OBLIGATION,
      dcecConjunction(p, q),
      agent,
    );

    expect(new DcecDeonticDRule().apply([obligation]).map(String)).toEqual([
      '¬(O[agent:Agent](¬(p())))',
    ]);
    expect(
      new DcecDeonticPermissionObligation().apply([permission, obligation]).map(String),
    ).toEqual(['¬(O[agent:Agent](¬(p())))', '¬(P[agent:Agent](¬(p())))']);
    expect(new DcecDeonticDistribution().apply([distributed]).map(String)).toEqual([
      '(O[agent:Agent](p()) ∧ O[agent:Agent](q()))',
    ]);
  });

  it('applies combined knowledge-obligation and temporal-obligation rules', () => {
    const obligation = new DcecDeonticFormula(DcecDeonticOperator.OBLIGATION, p, agent);
    const knownObligation = new DcecCognitiveFormula(
      DcecCognitiveOperator.KNOWLEDGE,
      agent,
      obligation,
    );

    expect(new DcecKnowledgeObligation().apply([knownObligation]).map(String)).toEqual([
      'O[agent:Agent](K(agent:Agent, p()))',
    ]);
    expect(new DcecTemporalObligation().apply([obligation]).map(String)).toEqual([
      'O[agent:Agent](p())',
    ]);
  });

  it('returns grouped advanced rule registries', () => {
    expect(getDcecModalRules().map((rule) => rule.name())).toEqual([
      'Modal K Axiom',
      'Modal T Axiom',
      'Modal S4 Axiom',
      'Necessitation',
    ]);
    expect(getDcecTemporalRules()).toHaveLength(2);
    expect(getDcecDeonticRules()).toHaveLength(3);
    expect(getDcecCombinedRules()).toHaveLength(2);
    expect(getAllDcecAdvancedRules()).toHaveLength(11);
  });

  it('exposes Python-compatible advanced inference registry metadata', () => {
    const registry = getDcecAdvancedInferenceRegistry();

    expect(registry).toHaveLength(11);
    expect(registry.map((entry) => entry.id)).toContain('knowledge_obligation_interaction');
    expect(
      registry.every(
        (entry) => entry.sourcePythonModule === 'logic/CEC/native/advanced_inference.py',
      ),
    ).toBe(true);
  });

  it('classifies nested cognitive, temporal, and deontic formulas for rule selection', () => {
    const obligation = new DcecDeonticFormula(DcecDeonticOperator.OBLIGATION, p, agent);
    const knownObligation = new DcecCognitiveFormula(
      DcecCognitiveOperator.KNOWLEDGE,
      agent,
      obligation,
    );
    const temporalObligation = new DcecTemporalFormula(DcecTemporalOperator.ALWAYS, obligation);

    expect(classifyDcecAdvancedFormula(knownObligation)).toEqual({
      cognitive: true,
      modal: true,
      temporal: false,
      deontic: true,
    });
    expect(classifyDcecAdvancedFormulas([temporalObligation])).toEqual({
      cognitive: false,
      modal: false,
      temporal: true,
      deontic: true,
    });
  });

  it('selects cognitive/modal, deontic, and temporal-deontic advanced rules deterministically', () => {
    const implication = new DcecCognitiveFormula(
      DcecCognitiveOperator.KNOWLEDGE,
      agent,
      dcecImplication(p, q),
    );
    const obligation = new DcecDeonticFormula(DcecDeonticOperator.OBLIGATION, p, agent);
    const knownObligation = new DcecCognitiveFormula(
      DcecCognitiveOperator.KNOWLEDGE,
      agent,
      obligation,
    );
    const temporalObligation = new DcecTemporalFormula(DcecTemporalOperator.ALWAYS, obligation);

    expect(selectDcecAdvancedInferenceRules([implication]).map((entry) => entry.id)).toEqual([
      'modal_k_axiom',
      'modal_t_axiom',
      'modal_s4_axiom',
    ]);
    expect(selectDcecAdvancedInferenceRules([obligation]).map((entry) => entry.id)).toEqual([
      'deontic_d_axiom',
      'permission_obligation_duality',
    ]);
    expect(selectDcecAdvancedInferenceRules([knownObligation]).map((entry) => entry.id)).toEqual([
      'modal_t_axiom',
      'modal_s4_axiom',
      'knowledge_obligation_interaction',
    ]);
    expect(
      selectDcecAdvancedInferenceRules([temporalObligation, obligation]).map((entry) => entry.id),
    ).toEqual(['deontic_d_axiom', 'permission_obligation_duality', 'temporal_deontic_interaction']);
  });

  it('derives a bounded browser-native closure with Python-compatible proof metadata', () => {
    const implication = new DcecCognitiveFormula(
      DcecCognitiveOperator.KNOWLEDGE,
      agent,
      dcecImplication(p, q),
    );

    const result = deriveDcecAdvancedInferences([implication], { maxRounds: 1 });

    expect(result.assumptions.map(String)).toEqual(['K(agent:Agent, (p() → q()))']);
    expect(result.derived.map(String)).toEqual([
      '(K(agent:Agent, p()) → K(agent:Agent, q()))',
      '(p() → q())',
      'K(agent:Agent, K(agent:Agent, (p() → q())))',
    ]);
    expect(result.closure.map(String)).toEqual([
      'K(agent:Agent, (p() → q()))',
      '(K(agent:Agent, p()) → K(agent:Agent, q()))',
      '(p() → q())',
      'K(agent:Agent, K(agent:Agent, (p() → q())))',
    ]);
    expect(result.steps.map((step) => step.ruleId)).toEqual([
      'modal_k_axiom',
      'modal_t_axiom',
      'modal_s4_axiom',
    ]);
    expect(
      result.steps.every(
        (step) =>
          step.sourcePythonModule === 'logic/CEC/native/advanced_inference.py' &&
          step.browserNative === true &&
          step.pythonRuntime === false &&
          step.status === 'SUCCESS',
      ),
    ).toBe(true);
    expect(result.saturated).toBe(true);
  });

  it('fail-closes advanced inference derivation at the configured local bound', () => {
    const implication = new DcecCognitiveFormula(
      DcecCognitiveOperator.KNOWLEDGE,
      agent,
      dcecImplication(p, q),
    );

    const result = deriveDcecAdvancedInferences([implication], {
      maxRounds: 2,
      maxDerivedFormulas: 2,
    });

    expect(result.derived.map(String)).toEqual([
      '(K(agent:Agent, p()) → K(agent:Agent, q()))',
      '(p() → q())',
    ]);
    expect(result.closure).toHaveLength(3);
    expect(result.saturated).toBe(false);
  });
});
