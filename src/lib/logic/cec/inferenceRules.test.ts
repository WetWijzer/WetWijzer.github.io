import { formatCecExpression } from './formatter';
import {
  CecConjunctionIntroductionRule,
  CecConjunctionEliminationLeftRule,
  CecBeliefDistributionRule,
  CecBeliefConjunctionRule,
  CecBeliefMonotonicityRule,
  CecBeliefNegationRule,
  CecBeliefRevisionRule,
  CecAbsorptionRule,
  CecAdditionRule,
  CecAlwaysDistributionRule,
  CecAlwaysImpliesNextRule,
  CecAlwaysImplicationRule,
  CecAlwaysInductionRule,
  CecAlwaysTransitiveRule,
  CecBiconditionalEliminationRule,
  CecBiconditionalIntroductionRule,
  CecDeonticDRule,
  CecDoubleNegationEliminationRule,
  CecAssociationRule,
  CecCommutativityConjunctionRule,
  CecCommutativityDisjunctionRule,
  CecConstructiveDilemmaRule,
  CecCommonBeliefIntroductionRule,
  CecCommonKnowledgeDistributionRule,
  CecCommonKnowledgeImpliesKnowledgeRule,
  CecCommonKnowledgeIntroductionRule,
  CecCommonKnowledgeMonotonicityRule,
  CecCommonKnowledgeNegationRule,
  CecCommonKnowledgeTransitivityRule,
  CecDestructiveDilemmaRule,
  CecDistributionRule,
  CecEventuallyIntroductionRule,
  CecEventuallyDistributionRule,
  CecEventuallyFromAlwaysRule,
  CecEventuallyImplicationRule,
  CecEventuallyTransitiveRule,
  CecExistentialGeneralizationRule,
  CecExistentialInstantiationRule,
  CecExportationRule,
  CecClaviusLawRule,
  CecFixedPointInductionRule,
  CecIdempotenceRule,
  CecHypotheticalSyllogismRule,
  CecIntentionCommitmentRule,
  CecIntentionMeansEndRule,
  CecIntentionPersistenceRule,
  CecKnowledgeConjunctionRule,
  CecKnowledgeDistributionRule,
  CecKnowledgeImpliesBeliefRule,
  CecKnowledgeMonotonicityRule,
  CecModusPonensRule,
  CecNecessityConjunctionRule,
  CecNecessityDistributionRule,
  CecNecessityEliminationRule,
  CecNextDistributionRule,
  CecNextImplicationRule,
  CecMaterialImplicationRule,
  CecModalNecessitationIntroductionRule,
  CecObligationConjunctionRule,
  CecObligationConsistencyRule,
  CecObligationDistributionRule,
  CecObligationImplicationRule,
  CecPerceptionImpliesKnowledgeRule,
  CecPermissionDistributionRule,
  CecPermissionFromNonObligationRule,
  CecPossibilityDualityRule,
  CecPossibilityIntroductionRule,
  CecCaseAnalysisRule,
  CecFactoringRule,
  CecProofByContradictionRule,
  CecResolutionRule,
  CecSubsumptionRule,
  CecSinceWeakeningRule,
  CecUnitResolutionRule,
  CecProhibitionFromObligationRule,
  CecProhibitionEquivalenceRule,
  CecTemporalTRule,
  CecTemporalNegationRule,
  CecTautologyRule,
  CecTemporallyInducedCommonKnowledgeRule,
  CecTranspositionRule,
  CecTemporalUntilEliminationRule,
  CecUntilWeakeningRule,
  CecUniversalGeneralizationRule,
  CecUniversalModusPonensRule,
  CEC_DEONTIC_INFERENCE_RUNTIME,
  applyCecRules,
  applyCecDeonticPythonParityRules,
  cecExpressionEquals,
  getAllCecRules,
  getCognitiveCecRules,
  getDeonticCecRules,
  getCecDeonticPythonParityRuleNames,
  getGenerativeCecRules,
  getModalCecRules,
  getResolutionCecRules,
  getSpecializedCecRules,
  getTemporalCecRules,
} from './inferenceRules';
import { parseCecExpression } from './parser';

describe('CEC inference rules', () => {
  it('applies propositional CEC rules', () => {
    const premise = parseCecExpression('(subject_to agent code)');
    const implication = parseCecExpression(
      '(implies (subject_to agent code) (comply_with agent code))',
    );
    const conjunction = parseCecExpression('(and (subject_to agent code) (active code))');
    const doubleNegation = parseCecExpression('(not (not (active code)))');

    expect(CecModusPonensRule.canApply(premise, implication)).toBe(true);
    expect(formatCecExpression(CecModusPonensRule.apply(premise, implication))).toBe(
      '(comply_with agent code)',
    );
    expect(
      formatCecExpression(
        CecHypotheticalSyllogismRule.apply(
          parseCecExpression('(implies (a) (b))'),
          parseCecExpression('(implies (b) (c))'),
        ),
      ),
    ).toBe('(implies (a) (c))');
    expect(
      formatCecExpression(
        CecConjunctionIntroductionRule.apply(parseCecExpression('(a)'), parseCecExpression('(b)')),
      ),
    ).toBe('(and (a) (b))');
    expect(formatCecExpression(CecConjunctionEliminationLeftRule.apply(conjunction))).toBe(
      '(subject_to agent code)',
    );
    expect(formatCecExpression(CecDoubleNegationEliminationRule.apply(doubleNegation))).toBe(
      '(active code)',
    );
  });

  it('applies temporal and deontic CEC rules', () => {
    const always = parseCecExpression('(always (comply_with agent code))');
    const obligation = parseCecExpression('(O (comply_with agent code))');
    const prohibition = parseCecExpression('(F (enter agent code))');

    expect(formatCecExpression(CecTemporalTRule.apply(always))).toBe('(comply_with agent code)');
    expect(
      formatCecExpression(CecEventuallyIntroductionRule.apply(parseCecExpression('(active code)'))),
    ).toBe('(eventually (active code))');
    expect(formatCecExpression(CecDeonticDRule.apply(obligation))).toBe(
      '(P (comply_with agent code))',
    );
    expect(formatCecExpression(CecProhibitionEquivalenceRule.apply(prohibition))).toBe(
      '(O (not (enter agent code)))',
    );
    expect(
      formatCecExpression(
        CecProhibitionFromObligationRule.apply(parseCecExpression('(O (not (enter agent code)))')),
      ),
    ).toBe('(F (enter agent code))');
  });

  it('applies expanded temporal CEC rules', () => {
    expect(
      formatCecExpression(
        CecAlwaysDistributionRule.apply(parseCecExpression('(always (and (p) (q)))')),
      ),
    ).toBe('(and (always (p)) (always (q)))');

    expect(
      formatCecExpression(
        CecAlwaysImplicationRule.apply(
          parseCecExpression('(always (p))'),
          parseCecExpression('(always (implies (p) (q)))'),
        ),
      ),
    ).toBe('(always (q))');

    expect(
      formatCecExpression(
        CecAlwaysTransitiveRule.apply(parseCecExpression('(always (always (p)))')),
      ),
    ).toBe('(always (p))');

    expect(
      formatCecExpression(CecAlwaysImpliesNextRule.apply(parseCecExpression('(always (p))'))),
    ).toBe('(next (p))');

    expect(
      formatCecExpression(
        CecAlwaysInductionRule.apply(
          parseCecExpression('(p)'),
          parseCecExpression('(always (implies (p) (next (p))))'),
        ),
      ),
    ).toBe('(always (p))');

    expect(
      formatCecExpression(CecEventuallyFromAlwaysRule.apply(parseCecExpression('(always (p))'))),
    ).toBe('(eventually (p))');

    expect(
      formatCecExpression(
        CecEventuallyDistributionRule.apply(parseCecExpression('(eventually (or (p) (q)))')),
      ),
    ).toBe('(or (eventually (p)) (eventually (q)))');

    expect(
      formatCecExpression(
        CecEventuallyTransitiveRule.apply(parseCecExpression('(eventually (eventually (p)))')),
      ),
    ).toBe('(eventually (p))');

    expect(
      formatCecExpression(
        CecEventuallyImplicationRule.apply(
          parseCecExpression('(eventually (p))'),
          parseCecExpression('(always (implies (p) (q)))'),
        ),
      ),
    ).toBe('(eventually (q))');

    expect(
      formatCecExpression(
        CecNextDistributionRule.apply(parseCecExpression('(next (and (p) (q)))')),
      ),
    ).toBe('(and (next (p)) (next (q)))');

    expect(
      formatCecExpression(
        CecNextImplicationRule.apply(
          parseCecExpression('(next (p))'),
          parseCecExpression('(next (implies (p) (q)))'),
        ),
      ),
    ).toBe('(next (q))');

    expect(
      formatCecExpression(CecUntilWeakeningRule.apply(parseCecExpression('(until (p) (q))'))),
    ).toBe('(eventually (q))');

    expect(
      formatCecExpression(CecSinceWeakeningRule.apply(parseCecExpression('(since (p) (q))'))),
    ).toBe('(q)');

    expect(
      formatCecExpression(
        CecTemporalUntilEliminationRule.apply(
          parseCecExpression('(until (p) (q))'),
          parseCecExpression('(q)'),
        ),
      ),
    ).toBe('(q)');

    expect(
      formatCecExpression(CecTemporalNegationRule.apply(parseCecExpression('(not (always (p)))'))),
    ).toBe('(eventually (not (p)))');
  });

  it('applies modal CEC rules', () => {
    expect(
      formatCecExpression(CecNecessityEliminationRule.apply(parseCecExpression('(always (p))'))),
    ).toBe('(p)');

    expect(
      formatCecExpression(CecPossibilityIntroductionRule.apply(parseCecExpression('(p)'))),
    ).toBe('(eventually (p))');

    expect(
      formatCecExpression(
        CecNecessityDistributionRule.apply(
          parseCecExpression('(always (implies (p) (q)))'),
          parseCecExpression('(always (p))'),
        ),
      ),
    ).toBe('(always (q))');

    expect(
      formatCecExpression(
        CecPossibilityDualityRule.apply(parseCecExpression('(not (always (not (p))))')),
      ),
    ).toBe('(eventually (p))');

    expect(
      formatCecExpression(
        CecNecessityConjunctionRule.apply(
          parseCecExpression('(always (p))'),
          parseCecExpression('(always (q))'),
        ),
      ),
    ).toBe('(always (and (p) (q)))');
  });

  it('applies expanded deontic CEC rules', () => {
    expect(
      formatCecExpression(
        CecObligationDistributionRule.apply(
          parseCecExpression('(O (and (file_report agent) (pay_fee agent)))'),
        ),
      ),
    ).toBe('(and (O (file_report agent)) (O (pay_fee agent)))');

    expect(
      formatCecExpression(
        CecObligationImplicationRule.apply(
          parseCecExpression('(O (file_report agent))'),
          parseCecExpression('(implies (file_report agent) (retain_record agent))'),
        ),
      ),
    ).toBe('(O (retain_record agent))');

    expect(
      formatCecExpression(
        CecPermissionFromNonObligationRule.apply(
          parseCecExpression('(not (O (not (speak agent))))'),
        ),
      ),
    ).toBe('(P (speak agent))');

    expect(
      formatCecExpression(
        CecObligationConjunctionRule.apply(
          parseCecExpression('(O (file_report agent))'),
          parseCecExpression('(O (pay_fee agent))'),
        ),
      ),
    ).toBe('(O (and (file_report agent) (pay_fee agent)))');

    expect(
      formatCecExpression(
        CecPermissionDistributionRule.apply(parseCecExpression('(P (or (coffee) (tea)))')),
      ),
    ).toBe('(or (P (coffee)) (P (tea)))');

    expect(
      formatCecExpression(
        CecObligationConsistencyRule.apply(
          parseCecExpression('(O (speak agent))'),
          parseCecExpression('(O (not (speak agent)))'),
        ),
      ),
    ).toBe('contradiction');
  });

  it('ports the Python deontic.py rule class surface as a browser-native batch adapter', () => {
    const applications = applyCecDeonticPythonParityRules([
      parseCecExpression('(O (and (file_report agent) (pay_fee agent)))'),
      parseCecExpression('(O (file_report agent))'),
      parseCecExpression('(implies (file_report agent) (retain_record agent))'),
      parseCecExpression('(not (O (not (speak agent))))'),
      parseCecExpression('(O (pay_fee agent))'),
      parseCecExpression('(P (or (coffee) (tea)))'),
      parseCecExpression('(O (not (file_report agent)))'),
      parseCecExpression('(F (enter agent code))'),
    ]);

    expect(CEC_DEONTIC_INFERENCE_RUNTIME).toEqual({
      sourcePythonModule: 'logic/CEC/native/inference_rules/deontic.py',
      browserNative: true,
      pythonRuntime: false,
    });
    expect(getCecDeonticPythonParityRuleNames()).toEqual([
      'ObligationDistribution',
      'ObligationImplication',
      'PermissionFromNonObligation',
      'ObligationConjunction',
      'PermissionDistribution',
      'ObligationConsistency',
      'ProhibitionEquivalence',
    ]);
    expect(applications.map((application) => application.pythonRuleName)).toEqual([
      'ObligationDistribution',
      'ObligationImplication',
      'PermissionFromNonObligation',
      'ObligationConjunction',
      'PermissionDistribution',
      'ObligationConsistency',
      'ProhibitionEquivalence',
    ]);
    expect(
      applications.every((application) => application.metadata === CEC_DEONTIC_INFERENCE_RUNTIME),
    ).toBe(true);
    expect(
      applications.map((application) => formatCecExpression(application.conclusions[0])),
    ).toEqual([
      '(and (O (file_report agent)) (O (pay_fee agent)))',
      '(O (retain_record agent))',
      '(P (speak agent))',
      '(O (and (and (file_report agent) (pay_fee agent)) (file_report agent)))',
      '(or (P (coffee)) (P (tea)))',
      'contradiction',
      '(O (not (enter agent code)))',
    ]);
  });

  it('applies quantified CEC rules', () => {
    expect(
      formatCecExpression(
        CecUniversalModusPonensRule.apply(
          parseCecExpression(
            '(forall agent (implies (subject_to agent code) (P (always (comply_with agent code)))))',
          ),
          parseCecExpression('(subject_to ada code)'),
        ),
      ),
    ).toBe('(P (always (comply_with ada code)))');

    expect(
      formatCecExpression(
        CecExistentialInstantiationRule.apply(
          parseCecExpression('(exists agent (subject_to agent code))'),
        ),
      ),
    ).toBe('(subject_to skolem_agent code)');

    expect(
      formatCecExpression(
        CecExistentialGeneralizationRule.apply(parseCecExpression('(subject_to ada code)')),
      ),
    ).toBe('(exists x (subject_to x code))');

    expect(
      formatCecExpression(
        CecUniversalGeneralizationRule.apply(parseCecExpression('(subject_to agent code)')),
      ),
    ).toBe('(forall agent (subject_to agent code))');
  });

  it('applies cognitive CEC belief and knowledge rules', () => {
    expect(
      formatCecExpression(
        CecBeliefDistributionRule.apply(parseCecExpression('(B alice (and (raining) (cold)))')),
      ),
    ).toBe('(and (B alice (raining)) (B alice (cold)))');

    expect(
      formatCecExpression(
        CecKnowledgeImpliesBeliefRule.apply(parseCecExpression('(K alice (true_fact))')),
      ),
    ).toBe('(B alice (true_fact))');

    expect(
      formatCecExpression(
        CecBeliefMonotonicityRule.apply(
          parseCecExpression('(B alice (raining))'),
          parseCecExpression('(implies (raining) (wet))'),
        ),
      ),
    ).toBe('(B alice (wet))');

    expect(
      formatCecExpression(
        CecKnowledgeDistributionRule.apply(parseCecExpression('(K alice (and (p) (q)))')),
      ),
    ).toBe('(and (K alice (p)) (K alice (q)))');

    expect(
      formatCecExpression(
        CecBeliefNegationRule.apply(parseCecExpression('(B alice (not (raining)))')),
      ),
    ).toBe('(not (B alice (raining)))');

    expect(
      formatCecExpression(
        CecKnowledgeMonotonicityRule.apply(
          parseCecExpression('(K alice (human socrates))'),
          parseCecExpression('(implies (human socrates) (mortal socrates))'),
        ),
      ),
    ).toBe('(K alice (mortal socrates))');
  });

  it('applies cognitive CEC intention and perception rules', () => {
    expect(
      formatCecExpression(
        CecIntentionCommitmentRule.apply(
          parseCecExpression('(I alice (go_store))'),
          parseCecExpression('(B alice (implies (go_store) (buy_milk)))'),
        ),
      ),
    ).toBe('(I alice (buy_milk))');

    expect(
      formatCecExpression(
        CecIntentionMeansEndRule.apply(
          parseCecExpression('(I alice (arrive_work))'),
          parseCecExpression('(B alice (implies (take_bus) (arrive_work)))'),
        ),
      ),
    ).toBe('(I alice (take_bus))');

    expect(
      formatCecExpression(
        CecPerceptionImpliesKnowledgeRule.apply(parseCecExpression('(Perceives alice (light_on))')),
      ),
    ).toBe('(K alice (light_on))');

    expect(
      formatCecExpression(
        CecIntentionPersistenceRule.apply(
          parseCecExpression('(I alice (go_store))'),
          parseCecExpression('(not (B alice (go_store)))'),
        ),
      ),
    ).toBe('(I alice (go_store))');

    expect(
      formatCecExpression(
        CecBeliefRevisionRule.apply(
          parseCecExpression('(B alice (light_off))'),
          parseCecExpression('(Perceives alice (not (light_off)))'),
        ),
      ),
    ).toBe('(B alice (not (light_off)))');
  });

  it('keeps cognitive conjunction generation opt-in', () => {
    expect(
      formatCecExpression(
        CecBeliefConjunctionRule.apply(
          parseCecExpression('(B alice (raining))'),
          parseCecExpression('(B alice (cold))'),
        ),
      ),
    ).toBe('(B alice (and (raining) (cold)))');

    expect(
      formatCecExpression(
        CecKnowledgeConjunctionRule.apply(
          parseCecExpression('(K alice (p))'),
          parseCecExpression('(K alice (q))'),
        ),
      ),
    ).toBe('(K alice (and (p) (q)))');
  });

  it('applies common knowledge and common belief CEC rules', () => {
    expect(
      formatCecExpression(
        CecCommonKnowledgeIntroductionRule.apply(
          parseCecExpression('(K alice (p))'),
          parseCecExpression('(K bob (p))'),
        ),
      ),
    ).toBe('(C all (p))');

    expect(
      formatCecExpression(
        CecCommonBeliefIntroductionRule.apply(
          parseCecExpression('(B alice (p))'),
          parseCecExpression('(B bob (p))'),
        ),
      ),
    ).toBe('(CB all (p))');

    expect(
      formatCecExpression(
        CecCommonKnowledgeDistributionRule.apply(parseCecExpression('(C all (and (p) (q)))')),
      ),
    ).toBe('(and (C all (p)) (C all (q)))');

    expect(
      formatCecExpression(
        CecCommonKnowledgeImpliesKnowledgeRule.apply(parseCecExpression('(C all (p))')),
      ),
    ).toBe('(K all (p))');

    expect(
      formatCecExpression(
        CecCommonKnowledgeMonotonicityRule.apply(
          parseCecExpression('(C all (p))'),
          parseCecExpression('(implies (p) (q))'),
        ),
      ),
    ).toBe('(C all (q))');

    expect(
      formatCecExpression(
        CecCommonKnowledgeNegationRule.apply(parseCecExpression('(C all (not (p)))')),
      ),
    ).toBe('(not (C all (p)))');

    expect(
      formatCecExpression(
        CecCommonKnowledgeTransitivityRule.apply(parseCecExpression('(C all (C all (p)))')),
      ),
    ).toBe('(C all (p))');

    expect(
      formatCecExpression(
        CecFixedPointInductionRule.apply(
          parseCecExpression('(p)'),
          parseCecExpression('(implies (p) (K everyone (p)))'),
        ),
      ),
    ).toBe('(C everyone (p))');

    expect(
      formatCecExpression(
        CecTemporallyInducedCommonKnowledgeRule.apply(parseCecExpression('(always (K all (p)))')),
      ),
    ).toBe('(C all (p))');

    expect(
      formatCecExpression(
        CecModalNecessitationIntroductionRule.apply(parseCecExpression('(or (p) (not (p)))')),
      ),
    ).toBe('(always (or (p) (not (p))))');
  });

  it('applies resolution CEC rules', () => {
    expect(
      formatCecExpression(
        CecResolutionRule.apply(
          parseCecExpression('(or (home alice) (work alice))'),
          parseCecExpression('(or (not (home alice)) (busy alice))'),
        ),
      ),
    ).toBe('(or (work alice) (busy alice))');

    expect(
      formatCecExpression(
        CecUnitResolutionRule.apply(
          parseCecExpression('(home alice)'),
          parseCecExpression('(or (not (home alice)) (busy alice))'),
        ),
      ),
    ).toBe('(busy alice)');

    expect(
      formatCecExpression(
        CecFactoringRule.apply(parseCecExpression('(or (busy alice) (busy alice))')),
      ),
    ).toBe('(busy alice)');

    expect(
      formatCecExpression(
        CecSubsumptionRule.apply(
          parseCecExpression('(or (p) (q))'),
          parseCecExpression('(or (p) (or (q) (r)))'),
        ),
      ),
    ).toBe('(or (p) (q))');

    expect(
      formatCecExpression(
        CecCaseAnalysisRule.apply(
          parseCecExpression('(or (home alice) (work alice))'),
          parseCecExpression('(implies (home alice) (reachable alice))'),
          parseCecExpression('(implies (work alice) (reachable alice))'),
        ),
      ),
    ).toBe('(reachable alice)');

    expect(
      formatCecExpression(
        CecProofByContradictionRule.apply(
          parseCecExpression('(busy alice)'),
          parseCecExpression('(not (busy alice))'),
        ),
      ),
    ).toBe('contradiction');
  });

  it('applies specialized CEC rules', () => {
    expect(
      formatCecExpression(
        CecBiconditionalIntroductionRule.apply(
          parseCecExpression('(implies (rains) (wet))'),
          parseCecExpression('(implies (wet) (rains))'),
        ),
      ),
    ).toBe('(iff (rains) (wet))');

    expect(
      formatCecExpression(
        CecBiconditionalEliminationRule.apply(parseCecExpression('(iff (rains) (wet))')),
      ),
    ).toBe('(and (implies (rains) (wet)) (implies (wet) (rains)))');

    expect(
      formatCecExpression(
        CecConstructiveDilemmaRule.apply(
          parseCecExpression('(implies (rains) (umbrella))'),
          parseCecExpression('(implies (sunny) (sunglasses))'),
          parseCecExpression('(or (rains) (sunny))'),
        ),
      ),
    ).toBe('(or (umbrella) (sunglasses))');

    expect(
      formatCecExpression(
        CecDestructiveDilemmaRule.apply(
          parseCecExpression('(implies (rains) (umbrella))'),
          parseCecExpression('(implies (sunny) (sunglasses))'),
          parseCecExpression('(or (not (umbrella)) (not (sunglasses)))'),
        ),
      ),
    ).toBe('(or (not (rains)) (not (sunny)))');

    expect(
      formatCecExpression(
        CecExportationRule.apply(
          parseCecExpression('(implies (and (home alice) (calls bob)) (answers alice))'),
        ),
      ),
    ).toBe('(implies (home alice) (implies (calls bob) (answers alice)))');

    expect(
      formatCecExpression(CecAbsorptionRule.apply(parseCecExpression('(implies (rains) (wet))'))),
    ).toBe('(implies (rains) (and (rains) (wet)))');

    expect(
      formatCecExpression(
        CecAdditionRule.apply(parseCecExpression('(rains)'), parseCecExpression('(snowing)')),
      ),
    ).toBe('(or (rains) (snowing))');

    expect(
      formatCecExpression(CecTautologyRule.apply(parseCecExpression('(or (rains) (rains))'))),
    ).toBe('(rains)');

    expect(
      formatCecExpression(
        CecCommutativityConjunctionRule.apply(parseCecExpression('(and (home alice) (busy bob))')),
      ),
    ).toBe('(and (busy bob) (home alice))');

    expect(
      formatCecExpression(
        CecCommutativityDisjunctionRule.apply(parseCecExpression('(or (home alice) (busy bob))')),
      ),
    ).toBe('(or (busy bob) (home alice))');

    expect(
      formatCecExpression(CecDistributionRule.apply(parseCecExpression('(or (p) (and (q) (r)))'))),
    ).toBe('(and (or (p) (q)) (or (p) (r)))');

    expect(
      formatCecExpression(CecDistributionRule.apply(parseCecExpression('(and (p) (or (q) (r)))'))),
    ).toBe('(or (and (p) (q)) (and (p) (r)))');

    expect(
      formatCecExpression(CecAssociationRule.apply(parseCecExpression('(and (and (p) (q)) (r))'))),
    ).toBe('(and (p) (and (q) (r)))');

    expect(
      formatCecExpression(CecTranspositionRule.apply(parseCecExpression('(implies (p) (q))'))),
    ).toBe('(implies (not (q)) (not (p)))');

    expect(
      formatCecExpression(
        CecMaterialImplicationRule.apply(parseCecExpression('(implies (p) (q))')),
      ),
    ).toBe('(or (not (p)) (q))');

    expect(
      formatCecExpression(
        CecMaterialImplicationRule.apply(parseCecExpression('(or (not (p)) (q))')),
      ),
    ).toBe('(implies (p) (q))');

    expect(
      formatCecExpression(CecClaviusLawRule.apply(parseCecExpression('(implies (not (p)) (p))'))),
    ).toBe('(p)');

    expect(formatCecExpression(CecIdempotenceRule.apply(parseCecExpression('(and (p) (p))')))).toBe(
      '(p)',
    );
  });

  it('enumerates three-premise resolution applications', () => {
    const applications = applyCecRules(
      [
        parseCecExpression('(or (home alice) (work alice))'),
        parseCecExpression('(implies (home alice) (reachable alice))'),
        parseCecExpression('(implies (work alice) (reachable alice))'),
      ],
      [CecCaseAnalysisRule],
    );

    expect(applications).toHaveLength(1);
    expect(applications[0].premises).toHaveLength(3);
    expect(formatCecExpression(applications[0].conclusion)).toBe('(reachable alice)');
  });

  it('enumerates CEC rule applications and compares expressions by normalized form', () => {
    const premise = parseCecExpression('(subject_to agent code)');
    const implication = parseCecExpression(
      '(implies (subject_to agent code) (comply_with agent code))',
    );
    const applications = applyCecRules([premise, implication], [CecModusPonensRule]);

    expect(applications).toHaveLength(1);
    expect(
      cecExpressionEquals(
        applications[0].conclusion,
        parseCecExpression('(comply_with agent code)'),
      ),
    ).toBe(true);
    expect(getAllCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecModusPonens',
        'CecHypotheticalSyllogism',
        'CecTemporalT',
        'CecDeonticD',
        'CecProhibitionEquivalence',
        'CecUniversalModusPonens',
      ]),
    );
    expect(getAllCecRules().map((rule) => rule.name)).not.toContain('CecConjunctionIntroduction');
    expect(getAllCecRules().map((rule) => rule.name)).not.toContain('CecBeliefConjunction');
    expect(getCognitiveCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecKnowledgeImpliesBelief',
        'CecBeliefMonotonicity',
        'CecPerceptionImpliesKnowledge',
        'CecBeliefRevision',
      ]),
    );
    expect(getGenerativeCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecConjunctionIntroduction',
        'CecEventuallyIntroduction',
        'CecBeliefConjunction',
        'CecAddition',
        'CecObligationConjunction',
        'CecPossibilityIntroduction',
        'CecNecessityConjunction',
      ]),
    );
    expect(getModalCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecNecessityElimination',
        'CecNecessityDistribution',
        'CecPossibilityDuality',
      ]),
    );
    expect(getModalCecRules().map((rule) => rule.name)).not.toContain('CecPossibilityIntroduction');
    expect(getTemporalCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecAlwaysDistribution',
        'CecEventuallyImplication',
        'CecUntilWeakening',
        'CecTemporalNegation',
      ]),
    );
    expect(getDeonticCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecObligationDistribution',
        'CecObligationImplication',
        'CecPermissionFromNonObligation',
        'CecObligationConsistency',
      ]),
    );
    expect(getResolutionCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecResolution',
        'CecUnitResolution',
        'CecFactoring',
        'CecCaseAnalysis',
      ]),
    );
    expect(getSpecializedCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecBiconditionalIntroduction',
        'CecConstructiveDilemma',
        'CecExportation',
        'CecTautology',
        'CecDistribution',
        'CecMaterialImplication',
        'CecIdempotence',
      ]),
    );
    expect(getCognitiveCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecCommonKnowledgeDistribution',
        'CecCommonKnowledgeImpliesKnowledge',
        'CecCommonKnowledgeMonotonicity',
        'CecCommonKnowledgeTransitivity',
      ]),
    );
    expect(getGenerativeCecRules().map((rule) => rule.name)).toEqual(
      expect.arrayContaining([
        'CecCommonKnowledgeIntroduction',
        'CecCommonBeliefIntroduction',
        'CecFixedPointInduction',
        'CecModalNecessitationIntroduction',
      ]),
    );
    expect(getSpecializedCecRules().map((rule) => rule.name)).not.toContain('CecAddition');
  });
});
