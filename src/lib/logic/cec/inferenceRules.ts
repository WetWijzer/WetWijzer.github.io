import type {
  CecApplication,
  CecBinaryExpression,
  CecExpression,
  CecQuantifiedExpression,
  CecUnaryExpression,
} from './ast';
import { formatCecExpression } from './formatter';

export interface CecInferenceRule {
  name: string;
  description: string;
  arity: 1 | 2 | 3;
  canApply(...expressions: CecExpression[]): boolean;
  apply(...expressions: CecExpression[]): CecExpression;
}

export interface CecRuleApplication {
  rule: string;
  premises: CecExpression[];
  conclusion: CecExpression;
}

export type CecDeonticPythonRuleName =
  | 'ObligationDistribution'
  | 'ObligationImplication'
  | 'PermissionFromNonObligation'
  | 'ObligationConjunction'
  | 'PermissionDistribution'
  | 'ObligationConsistency'
  | 'ProhibitionEquivalence';

export interface CecDeonticPythonRuleApplication {
  rule: string;
  pythonRuleName: CecDeonticPythonRuleName;
  premises: CecExpression[];
  conclusions: CecExpression[];
  status: 'SUCCESS';
  metadata: {
    sourcePythonModule: 'logic/CEC/native/inference_rules/deontic.py';
    browserNative: true;
    pythonRuntime: false;
  };
}

export type CecNativeInferencePythonModule =
  | 'logic/CEC/native/inference_rules/base.py'
  | 'logic/CEC/native/inference_rules/cognitive.py'
  | 'logic/CEC/native/inference_rules/modal.py';

export type CecNativeInferenceRuleGroup = 'base' | 'cognitive' | 'modal';

export type CecNativeBasePythonRuleName =
  | 'ModusPonens'
  | 'HypotheticalSyllogism'
  | 'ConjunctionIntroduction'
  | 'ConjunctionEliminationLeft'
  | 'ConjunctionEliminationRight'
  | 'DoubleNegationElimination';

export type CecNativeCognitivePythonRuleName =
  | 'BeliefDistribution'
  | 'BeliefConjunction'
  | 'BeliefMonotonicity'
  | 'BeliefNegation'
  | 'BeliefRevision'
  | 'KnowledgeImpliesBelief'
  | 'KnowledgeDistribution'
  | 'KnowledgeConjunction'
  | 'KnowledgeMonotonicity'
  | 'CommonBeliefIntroduction'
  | 'CommonKnowledgeDistribution'
  | 'CommonKnowledgeImpliesKnowledge'
  | 'CommonKnowledgeIntroduction'
  | 'CommonKnowledgeMonotonicity'
  | 'CommonKnowledgeNegation'
  | 'CommonKnowledgeTransitivity'
  | 'IntentionCommitment'
  | 'IntentionMeansEnd'
  | 'IntentionPersistence'
  | 'PerceptionImpliesKnowledge'
  | 'TemporallyInducedCommonKnowledge';

export type CecNativeModalPythonRuleName =
  | 'NecessityElimination'
  | 'NecessityDistribution'
  | 'PossibilityIntroduction'
  | 'PossibilityDuality'
  | 'NecessityConjunction'
  | 'NecessitationIntroduction';

export type CecNativePythonRuleName =
  | CecNativeBasePythonRuleName
  | CecNativeCognitivePythonRuleName
  | CecNativeModalPythonRuleName;

export interface CecNativePythonProofStepMetadata {
  stepId: number;
  rule: string;
  pythonRuleName: CecNativePythonRuleName;
  ruleGroup: CecNativeInferenceRuleGroup;
  sourcePythonModule: CecNativeInferencePythonModule;
  premiseCount: number;
  conclusionCount: 1;
  status: 'SUCCESS';
  browserNative: true;
  pythonRuntime: false;
}

export interface CecNativePythonRuleApplication {
  rule: string;
  pythonRuleName: CecNativePythonRuleName;
  ruleGroup: CecNativeInferenceRuleGroup;
  sourcePythonModule: CecNativeInferencePythonModule;
  premises: CecExpression[];
  conclusion: CecExpression;
  status: 'SUCCESS';
  proofStep: CecNativePythonProofStepMetadata;
}

type CecNativePythonRuleSpec = {
  pythonRuleName: CecNativePythonRuleName;
  ruleGroup: CecNativeInferenceRuleGroup;
  rule: CecInferenceRule;
};

type CecRuleSpec = {
  name: string;
  description: string;
  arity: 1 | 2 | 3;
  canApply: (...expressions: CecExpression[]) => boolean;
  apply: (...expressions: CecExpression[]) => CecExpression;
};

export class CecRule implements CecInferenceRule {
  readonly name: string;
  readonly description: string;
  readonly arity: 1 | 2 | 3;
  private readonly canApplyImpl: CecRuleSpec['canApply'];
  private readonly applyImpl: CecRuleSpec['apply'];

  constructor(spec: CecRuleSpec) {
    this.name = spec.name;
    this.description = spec.description;
    this.arity = spec.arity;
    this.canApplyImpl = spec.canApply;
    this.applyImpl = spec.apply;
  }

  canApply(...expressions: CecExpression[]): boolean {
    return expressions.length === this.arity && this.canApplyImpl(...expressions);
  }

  apply(...expressions: CecExpression[]): CecExpression {
    if (!this.canApply(...expressions)) {
      throw new Error(`CEC rule ${this.name} cannot be applied to the supplied expressions`);
    }
    return this.applyImpl(...expressions);
  }
}

export const CecModusPonensRule = new CecRule({
  name: 'CecModusPonens',
  description: 'From phi and (implies phi psi), infer psi',
  arity: 2,
  canApply: (left, right) => isBinary(right, 'implies') && cecExpressionEquals(right.left, left),
  apply: (_left, right) => (right as CecBinaryExpression).right,
});

export const CecHypotheticalSyllogismRule = new CecRule({
  name: 'CecHypotheticalSyllogism',
  description: 'From (implies phi psi) and (implies psi chi), infer (implies phi chi)',
  arity: 2,
  canApply: (first, second) =>
    isBinary(first, 'implies') &&
    isBinary(second, 'implies') &&
    cecExpressionEquals(first.right, second.left),
  apply: (first, second) => ({
    kind: 'binary',
    operator: 'implies',
    left: (first as CecBinaryExpression).left,
    right: (second as CecBinaryExpression).right,
  }),
});

export const CecConjunctionIntroductionRule = new CecRule({
  name: 'CecConjunctionIntroduction',
  description: 'From phi and psi, infer (and phi psi)',
  arity: 2,
  canApply: (left, right) => !cecExpressionEquals(left, right),
  apply: (left, right) => ({ kind: 'binary', operator: 'and', left, right }),
});

export const CecConjunctionEliminationLeftRule = new CecRule({
  name: 'CecConjunctionEliminationLeft',
  description: 'From (and phi psi), infer phi',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'and'),
  apply: (expression) => (expression as CecBinaryExpression).left,
});

export const CecConjunctionEliminationRightRule = new CecRule({
  name: 'CecConjunctionEliminationRight',
  description: 'From (and phi psi), infer psi',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'and'),
  apply: (expression) => (expression as CecBinaryExpression).right,
});

export const CecDoubleNegationEliminationRule = new CecRule({
  name: 'CecDoubleNegationElimination',
  description: 'From (not (not phi)), infer phi',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'not') &&
    expression.expression.kind === 'unary' &&
    expression.expression.operator === 'not',
  apply: (expression) => {
    if (!isUnary(expression, 'not') || !isUnary(expression.expression, 'not')) {
      throw new Error('Invalid CEC double negation premise');
    }
    return expression.expression.expression;
  },
});

export const CecTemporalTRule = new CecRule({
  name: 'CecTemporalT',
  description: 'From (always phi), infer phi',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'always'),
  apply: (expression) => {
    if (!isUnary(expression, 'always')) throw new Error('Invalid CEC temporal premise');
    return expression.expression;
  },
});

export const CecEventuallyIntroductionRule = new CecRule({
  name: 'CecEventuallyIntroduction',
  description: 'From phi, infer (eventually phi)',
  arity: 1,
  canApply: (expression) => !isUnary(expression, 'eventually'),
  apply: (expression) => ({ kind: 'unary', operator: 'eventually', expression }),
});

export const CecAlwaysDistributionRule = new CecRule({
  name: 'CecAlwaysDistribution',
  description: 'From (always (and phi psi)), infer (and (always phi) (always psi))',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'always') && isBinary(expression.expression, 'and'),
  apply: (expression) => {
    if (!isUnary(expression, 'always') || !isBinary(expression.expression, 'and')) {
      throw new Error('Invalid CEC always distribution premise');
    }
    return {
      kind: 'binary',
      operator: 'and',
      left: { kind: 'unary', operator: 'always', expression: expression.expression.left },
      right: { kind: 'unary', operator: 'always', expression: expression.expression.right },
    };
  },
});

export const CecAlwaysImplicationRule = new CecRule({
  name: 'CecAlwaysImplication',
  description: 'From (always phi) and (always (implies phi psi)), infer (always psi)',
  arity: 2,
  canApply: (left, right) => findUnaryImplicationPremises('always', left, right) !== undefined,
  apply: (left, right) => {
    const premises = findUnaryImplicationPremises('always', left, right);
    if (!premises) throw new Error('Invalid CEC always implication premises');
    return { kind: 'unary', operator: 'always', expression: premises.implication.expression.right };
  },
});

export const CecAlwaysTransitiveRule = new CecRule({
  name: 'CecAlwaysTransitive',
  description: 'From (always (always phi)), infer (always phi)',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'always') && isUnary(expression.expression, 'always'),
  apply: (expression) => {
    if (!isUnary(expression, 'always') || !isUnary(expression.expression, 'always')) {
      throw new Error('Invalid CEC always transitive premise');
    }
    return { kind: 'unary', operator: 'always', expression: expression.expression.expression };
  },
});

export const CecAlwaysImpliesNextRule = new CecRule({
  name: 'CecAlwaysImpliesNext',
  description: 'From (always phi), infer (next phi)',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'always'),
  apply: (expression) => {
    if (!isUnary(expression, 'always')) throw new Error('Invalid CEC always-next premise');
    return { kind: 'unary', operator: 'next', expression: expression.expression };
  },
});

export const CecAlwaysInductionRule = new CecRule({
  name: 'CecAlwaysInduction',
  description: 'From phi and (always (implies phi (next phi))), infer (always phi)',
  arity: 2,
  canApply: (left, right) => findAlwaysInductionPremises(left, right) !== undefined,
  apply: (left, right) => {
    const premise = findAlwaysInductionPremises(left, right);
    if (!premise) throw new Error('Invalid CEC always induction premises');
    return { kind: 'unary', operator: 'always', expression: premise };
  },
});

export const CecEventuallyFromAlwaysRule = new CecRule({
  name: 'CecEventuallyFromAlways',
  description: 'From (always phi), infer (eventually phi)',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'always'),
  apply: (expression) => {
    if (!isUnary(expression, 'always'))
      throw new Error('Invalid CEC eventually-from-always premise');
    return { kind: 'unary', operator: 'eventually', expression: expression.expression };
  },
});

export const CecEventuallyDistributionRule = new CecRule({
  name: 'CecEventuallyDistribution',
  description: 'From (eventually (or phi psi)), infer (or (eventually phi) (eventually psi))',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'eventually') && isBinary(expression.expression, 'or'),
  apply: (expression) => {
    if (!isUnary(expression, 'eventually') || !isBinary(expression.expression, 'or')) {
      throw new Error('Invalid CEC eventually distribution premise');
    }
    return {
      kind: 'binary',
      operator: 'or',
      left: { kind: 'unary', operator: 'eventually', expression: expression.expression.left },
      right: { kind: 'unary', operator: 'eventually', expression: expression.expression.right },
    };
  },
});

export const CecEventuallyTransitiveRule = new CecRule({
  name: 'CecEventuallyTransitive',
  description: 'From (eventually (eventually phi)), infer (eventually phi)',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'eventually') && isUnary(expression.expression, 'eventually'),
  apply: (expression) => {
    if (!isUnary(expression, 'eventually') || !isUnary(expression.expression, 'eventually')) {
      throw new Error('Invalid CEC eventually transitive premise');
    }
    return { kind: 'unary', operator: 'eventually', expression: expression.expression.expression };
  },
});

export const CecEventuallyImplicationRule = new CecRule({
  name: 'CecEventuallyImplication',
  description: 'From (eventually phi) and (always (implies phi psi)), infer (eventually psi)',
  arity: 2,
  canApply: (eventual, alwaysImplication) =>
    findEventuallyImplicationPremises(eventual, alwaysImplication) !== undefined,
  apply: (eventual, alwaysImplication) => {
    const premises = findEventuallyImplicationPremises(eventual, alwaysImplication);
    if (!premises) throw new Error('Invalid CEC eventually implication premises');
    return {
      kind: 'unary',
      operator: 'eventually',
      expression: premises.implication.expression.right,
    };
  },
});

export const CecNextDistributionRule = new CecRule({
  name: 'CecNextDistribution',
  description: 'From (next (and phi psi)), infer (and (next phi) (next psi))',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'next') && isBinary(expression.expression, 'and'),
  apply: (expression) => {
    if (!isUnary(expression, 'next') || !isBinary(expression.expression, 'and')) {
      throw new Error('Invalid CEC next distribution premise');
    }
    return {
      kind: 'binary',
      operator: 'and',
      left: { kind: 'unary', operator: 'next', expression: expression.expression.left },
      right: { kind: 'unary', operator: 'next', expression: expression.expression.right },
    };
  },
});

export const CecNextImplicationRule = new CecRule({
  name: 'CecNextImplication',
  description: 'From (next phi) and (next (implies phi psi)), infer (next psi)',
  arity: 2,
  canApply: (left, right) => findUnaryImplicationPremises('next', left, right) !== undefined,
  apply: (left, right) => {
    const premises = findUnaryImplicationPremises('next', left, right);
    if (!premises) throw new Error('Invalid CEC next implication premises');
    return { kind: 'unary', operator: 'next', expression: premises.implication.expression.right };
  },
});

export const CecUntilWeakeningRule = new CecRule({
  name: 'CecUntilWeakening',
  description: 'From (until phi psi), infer (eventually psi)',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'until'),
  apply: (expression) => {
    if (!isBinary(expression, 'until')) throw new Error('Invalid CEC until weakening premise');
    return { kind: 'unary', operator: 'eventually', expression: expression.right };
  },
});

export const CecSinceWeakeningRule = new CecRule({
  name: 'CecSinceWeakening',
  description: 'From (since phi psi), infer psi',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'since'),
  apply: (expression) => {
    if (!isBinary(expression, 'since')) throw new Error('Invalid CEC since weakening premise');
    return expression.right;
  },
});

export const CecTemporalUntilEliminationRule = new CecRule({
  name: 'CecTemporalUntilElimination',
  description: 'From (until phi psi) and psi, infer psi',
  arity: 2,
  canApply: (untilExpression, current) =>
    isBinary(untilExpression, 'until') && cecExpressionEquals(untilExpression.right, current),
  apply: (_untilExpression, current) => current,
});

export const CecTemporalNegationRule = new CecRule({
  name: 'CecTemporalNegation',
  description: 'From (not (always phi)), infer (eventually (not phi))',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'not') && isUnary(expression.expression, 'always'),
  apply: (expression) => {
    if (!isUnary(expression, 'not') || !isUnary(expression.expression, 'always')) {
      throw new Error('Invalid CEC temporal negation premise');
    }
    return {
      kind: 'unary',
      operator: 'eventually',
      expression: { kind: 'unary', operator: 'not', expression: expression.expression.expression },
    };
  },
});

export const CecNecessityEliminationRule = new CecRule({
  name: 'CecNecessityElimination',
  description: 'From necessary phi, represented as (always phi), infer phi',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'always'),
  apply: (expression) => {
    if (!isUnary(expression, 'always'))
      throw new Error('Invalid CEC necessity elimination premise');
    return expression.expression;
  },
});

export const CecPossibilityIntroductionRule = new CecRule({
  name: 'CecPossibilityIntroduction',
  description:
    'From phi, infer possible phi, represented as (eventually phi); kept opt-in because it generates modal formulas',
  arity: 1,
  canApply: (expression) => !isUnary(expression, 'eventually'),
  apply: (expression) => ({ kind: 'unary', operator: 'eventually', expression }),
});

export const CecNecessityDistributionRule = new CecRule({
  name: 'CecNecessityDistribution',
  description: 'From (always (implies phi psi)) and (always phi), infer (always psi)',
  arity: 2,
  canApply: (left, right) => findUnaryImplicationPremises('always', left, right) !== undefined,
  apply: (left, right) => {
    const premises = findUnaryImplicationPremises('always', left, right);
    if (!premises) throw new Error('Invalid CEC necessity distribution premises');
    return { kind: 'unary', operator: 'always', expression: premises.implication.expression.right };
  },
});

export const CecPossibilityDualityRule = new CecRule({
  name: 'CecPossibilityDuality',
  description: 'From (not (always (not phi))), infer (eventually phi)',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'not') &&
    isUnary(expression.expression, 'always') &&
    isUnary(expression.expression.expression, 'not'),
  apply: (expression) => {
    if (
      !isUnary(expression, 'not') ||
      !isUnary(expression.expression, 'always') ||
      !isUnary(expression.expression.expression, 'not')
    ) {
      throw new Error('Invalid CEC possibility duality premise');
    }
    return {
      kind: 'unary',
      operator: 'eventually',
      expression: expression.expression.expression.expression,
    };
  },
});

export const CecNecessityConjunctionRule = new CecRule({
  name: 'CecNecessityConjunction',
  description:
    'From (always phi) and (always psi), infer (always (and phi psi)); kept opt-in because it generates conjunctions',
  arity: 2,
  canApply: (left, right) =>
    isUnary(left, 'always') &&
    isUnary(right, 'always') &&
    !cecExpressionEquals(left.expression, right.expression),
  apply: (left, right) => {
    if (!isUnary(left, 'always') || !isUnary(right, 'always')) {
      throw new Error('Invalid CEC necessity conjunction premises');
    }
    return {
      kind: 'unary',
      operator: 'always',
      expression: {
        kind: 'binary',
        operator: 'and',
        left: left.expression,
        right: right.expression,
      },
    };
  },
});

export const CecDeonticDRule = new CecRule({
  name: 'CecDeonticD',
  description: 'From (O phi), infer (P phi)',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'O'),
  apply: (expression) => {
    if (!isUnary(expression, 'O')) throw new Error('Invalid CEC deontic premise');
    return { kind: 'unary', operator: 'P', expression: expression.expression };
  },
});

export const CecProhibitionEquivalenceRule = new CecRule({
  name: 'CecProhibitionEquivalence',
  description: 'From (F phi), infer (O (not phi))',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'F'),
  apply: (expression) => {
    if (!isUnary(expression, 'F')) throw new Error('Invalid CEC prohibition premise');
    return {
      kind: 'unary',
      operator: 'O',
      expression: { kind: 'unary', operator: 'not', expression: expression.expression },
    };
  },
});

export const CecProhibitionFromObligationRule = new CecRule({
  name: 'CecProhibitionFromObligation',
  description: 'From (O (not phi)), infer (F phi)',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'O') &&
    expression.expression.kind === 'unary' &&
    expression.expression.operator === 'not',
  apply: (expression) => {
    if (!isUnary(expression, 'O') || !isUnary(expression.expression, 'not')) {
      throw new Error('Invalid CEC obligation prohibition premise');
    }
    return { kind: 'unary', operator: 'F', expression: expression.expression.expression };
  },
});

export const CecObligationDistributionRule = new CecRule({
  name: 'CecObligationDistribution',
  description: 'From (O (and phi psi)), infer (and (O phi) (O psi))',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'O') && isBinary(expression.expression, 'and'),
  apply: (expression) => {
    if (!isUnary(expression, 'O') || !isBinary(expression.expression, 'and')) {
      throw new Error('Invalid CEC obligation distribution premise');
    }
    return {
      kind: 'binary',
      operator: 'and',
      left: { kind: 'unary', operator: 'O', expression: expression.expression.left },
      right: { kind: 'unary', operator: 'O', expression: expression.expression.right },
    };
  },
});

export const CecObligationImplicationRule = new CecRule({
  name: 'CecObligationImplication',
  description: 'From (O phi) and (implies phi psi), infer (O psi)',
  arity: 2,
  canApply: (obligation, implication) =>
    isUnary(obligation, 'O') &&
    isBinary(implication, 'implies') &&
    cecExpressionEquals(obligation.expression, implication.left),
  apply: (obligation, implication) => {
    if (!isUnary(obligation, 'O') || !isBinary(implication, 'implies')) {
      throw new Error('Invalid CEC obligation implication premises');
    }
    return { kind: 'unary', operator: 'O', expression: implication.right };
  },
});

export const CecPermissionFromNonObligationRule = new CecRule({
  name: 'CecPermissionFromNonObligation',
  description: 'From (not (O (not phi))), infer (P phi)',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'not') &&
    isUnary(expression.expression, 'O') &&
    isUnary(expression.expression.expression, 'not'),
  apply: (expression) => {
    if (
      !isUnary(expression, 'not') ||
      !isUnary(expression.expression, 'O') ||
      !isUnary(expression.expression.expression, 'not')
    ) {
      throw new Error('Invalid CEC permission duality premise');
    }
    return {
      kind: 'unary',
      operator: 'P',
      expression: expression.expression.expression.expression,
    };
  },
});

export const CecObligationConjunctionRule = new CecRule({
  name: 'CecObligationConjunction',
  description:
    'From (O phi) and (O psi), infer (O (and phi psi)); kept opt-in because it generates conjunctions',
  arity: 2,
  canApply: (left, right) =>
    isUnary(left, 'O') &&
    isUnary(right, 'O') &&
    !cecExpressionEquals(left.expression, right.expression),
  apply: (left, right) => {
    if (!isUnary(left, 'O') || !isUnary(right, 'O'))
      throw new Error('Invalid CEC obligation conjunction premises');
    return {
      kind: 'unary',
      operator: 'O',
      expression: {
        kind: 'binary',
        operator: 'and',
        left: left.expression,
        right: right.expression,
      },
    };
  },
});

export const CecPermissionDistributionRule = new CecRule({
  name: 'CecPermissionDistribution',
  description: 'From (P (or phi psi)), infer (or (P phi) (P psi))',
  arity: 1,
  canApply: (expression) => isUnary(expression, 'P') && isBinary(expression.expression, 'or'),
  apply: (expression) => {
    if (!isUnary(expression, 'P') || !isBinary(expression.expression, 'or')) {
      throw new Error('Invalid CEC permission distribution premise');
    }
    return {
      kind: 'binary',
      operator: 'or',
      left: { kind: 'unary', operator: 'P', expression: expression.expression.left },
      right: { kind: 'unary', operator: 'P', expression: expression.expression.right },
    };
  },
});

export const CecObligationConsistencyRule = new CecRule({
  name: 'CecObligationConsistency',
  description: 'From (O phi) and (O (not phi)), infer contradiction',
  arity: 2,
  canApply: (left, right) =>
    isUnary(left, 'O') &&
    isUnary(right, 'O') &&
    (isNegationOf(left.expression, right.expression) ||
      isNegationOf(right.expression, left.expression)),
  apply: () => ({ kind: 'atom', name: 'contradiction' }),
});

export const CecUniversalModusPonensRule = new CecRule({
  name: 'CecUniversalModusPonens',
  description: 'From (forall x (implies phi(x) psi(x))) and phi(a), infer psi(a)',
  arity: 2,
  canApply: (universal, premise) => {
    if (!isQuantified(universal, 'forall') || !isBinary(universal.expression, 'implies')) {
      return false;
    }
    return (
      matchCecExpressionForVariable(universal.expression.left, premise, universal.variable) !==
      undefined
    );
  },
  apply: (universal, premise) => {
    if (!isQuantified(universal, 'forall') || !isBinary(universal.expression, 'implies')) {
      throw new Error('Invalid CEC universal premise');
    }
    const binding = matchCecExpressionForVariable(
      universal.expression.left,
      premise,
      universal.variable,
    );
    if (!binding) throw new Error('CEC universal premise does not match supplied fact');
    return substituteCecAtom(universal.expression.right, universal.variable, binding);
  },
});

export const CecExistentialInstantiationRule = new CecRule({
  name: 'CecExistentialInstantiation',
  description: 'From (exists x phi(x)), infer phi(skolem_x)',
  arity: 1,
  canApply: (expression) => isQuantified(expression, 'exists'),
  apply: (expression) => {
    if (!isQuantified(expression, 'exists')) throw new Error('Invalid CEC existential premise');
    return substituteCecAtom(
      expression.expression,
      expression.variable,
      `skolem_${expression.variable}`,
    );
  },
});

export const CecExistentialGeneralizationRule = new CecRule({
  name: 'CecExistentialGeneralization',
  description: 'From phi(a), infer (exists x phi(x)) by replacing the first atom argument',
  arity: 1,
  canApply: (expression) => findFirstSubstitutableAtom(expression) !== undefined,
  apply: (expression) => {
    const atom = findFirstSubstitutableAtom(expression);
    if (!atom) throw new Error('No CEC atom available for existential generalization');
    return {
      kind: 'quantified',
      quantifier: 'exists',
      variable: 'x',
      expression: substituteCecAtom(expression, atom, 'x'),
    };
  },
});

export const CecUniversalGeneralizationRule = new CecRule({
  name: 'CecUniversalGeneralization',
  description: 'From phi(x), infer (forall x phi(x)) for a free variable-like atom',
  arity: 1,
  canApply: (expression) => findFirstVariableLikeAtom(expression) !== undefined,
  apply: (expression) => {
    const variable = findFirstVariableLikeAtom(expression);
    if (!variable)
      throw new Error('No CEC variable-like atom available for universal generalization');
    return {
      kind: 'quantified',
      quantifier: 'forall',
      variable,
      expression,
    };
  },
});

export const CecBeliefDistributionRule = new CecRule({
  name: 'CecBeliefDistribution',
  description: 'From (B agent (and phi psi)), infer (and (B agent phi) (B agent psi))',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'B') && isBinary(expression.args[1], 'and'),
  apply: (expression) => {
    const belief = requireCognitive(expression, 'B');
    if (!isBinary(belief.args[1], 'and'))
      throw new Error('Invalid CEC belief distribution premise');
    return {
      kind: 'binary',
      operator: 'and',
      left: cognitiveApplication('B', belief.args[0], belief.args[1].left),
      right: cognitiveApplication('B', belief.args[0], belief.args[1].right),
    };
  },
});

export const CecKnowledgeImpliesBeliefRule = new CecRule({
  name: 'CecKnowledgeImpliesBelief',
  description: 'From (K agent phi), infer (B agent phi)',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'K'),
  apply: (expression) => {
    const knowledge = requireCognitive(expression, 'K');
    return cognitiveApplication('B', knowledge.args[0], knowledge.args[1]);
  },
});

export const CecBeliefMonotonicityRule = new CecRule({
  name: 'CecBeliefMonotonicity',
  description: 'From (B agent phi) and (implies phi psi), infer (B agent psi)',
  arity: 2,
  canApply: (belief, implication) =>
    isCognitive(belief, 'B') &&
    isBinary(implication, 'implies') &&
    cecExpressionEquals(belief.args[1], implication.left),
  apply: (belief, implication) => {
    const premise = requireCognitive(belief, 'B');
    if (!isBinary(implication, 'implies'))
      throw new Error('Invalid CEC belief monotonicity implication');
    return cognitiveApplication('B', premise.args[0], implication.right);
  },
});

export const CecIntentionCommitmentRule = new CecRule({
  name: 'CecIntentionCommitment',
  description: 'From (I agent phi) and (B agent (implies phi psi)), infer (I agent psi)',
  arity: 2,
  canApply: (intention, belief) =>
    isCognitive(intention, 'I') &&
    isCognitive(belief, 'B') &&
    cecExpressionEquals(intention.args[0], belief.args[0]) &&
    isBinary(belief.args[1], 'implies') &&
    cecExpressionEquals(intention.args[1], belief.args[1].left),
  apply: (intention, belief) => {
    const intent = requireCognitive(intention, 'I');
    const believed = requireCognitive(belief, 'B');
    if (!isBinary(believed.args[1], 'implies'))
      throw new Error('Invalid CEC intention commitment premise');
    return cognitiveApplication('I', intent.args[0], believed.args[1].right);
  },
});

export const CecBeliefConjunctionRule = new CecRule({
  name: 'CecBeliefConjunction',
  description: 'From (B agent phi) and (B agent psi), infer (B agent (and phi psi))',
  arity: 2,
  canApply: (left, right) =>
    isCognitive(left, 'B') &&
    isCognitive(right, 'B') &&
    cecExpressionEquals(left.args[0], right.args[0]) &&
    !cecExpressionEquals(left.args[1], right.args[1]),
  apply: (left, right) => {
    const leftBelief = requireCognitive(left, 'B');
    const rightBelief = requireCognitive(right, 'B');
    return cognitiveApplication('B', leftBelief.args[0], {
      kind: 'binary',
      operator: 'and',
      left: leftBelief.args[1],
      right: rightBelief.args[1],
    });
  },
});

export const CecKnowledgeDistributionRule = new CecRule({
  name: 'CecKnowledgeDistribution',
  description: 'From (K agent (and phi psi)), infer (and (K agent phi) (K agent psi))',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'K') && isBinary(expression.args[1], 'and'),
  apply: (expression) => {
    const knowledge = requireCognitive(expression, 'K');
    if (!isBinary(knowledge.args[1], 'and'))
      throw new Error('Invalid CEC knowledge distribution premise');
    return {
      kind: 'binary',
      operator: 'and',
      left: cognitiveApplication('K', knowledge.args[0], knowledge.args[1].left),
      right: cognitiveApplication('K', knowledge.args[0], knowledge.args[1].right),
    };
  },
});

export const CecIntentionMeansEndRule = new CecRule({
  name: 'CecIntentionMeansEnd',
  description: 'From (I agent goal) and (B agent (implies action goal)), infer (I agent action)',
  arity: 2,
  canApply: (intention, belief) =>
    isCognitive(intention, 'I') &&
    isCognitive(belief, 'B') &&
    cecExpressionEquals(intention.args[0], belief.args[0]) &&
    isBinary(belief.args[1], 'implies') &&
    cecExpressionEquals(intention.args[1], belief.args[1].right),
  apply: (intention, belief) => {
    const intent = requireCognitive(intention, 'I');
    const believed = requireCognitive(belief, 'B');
    if (!isBinary(believed.args[1], 'implies'))
      throw new Error('Invalid CEC intention means-end premise');
    return cognitiveApplication('I', intent.args[0], believed.args[1].left);
  },
});

export const CecPerceptionImpliesKnowledgeRule = new CecRule({
  name: 'CecPerceptionImpliesKnowledge',
  description: 'From (Perceives agent phi), infer (K agent phi)',
  arity: 1,
  canApply: (expression) =>
    isCognitive(expression, 'Perceives') || isCognitive(expression, 'Perception'),
  apply: (expression) => {
    const perception = requireAnyCognitive(expression, ['Perceives', 'Perception']);
    return cognitiveApplication('K', perception.args[0], perception.args[1]);
  },
});

export const CecBeliefNegationRule = new CecRule({
  name: 'CecBeliefNegation',
  description: 'From (B agent (not phi)), infer (not (B agent phi))',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'B') && isUnary(expression.args[1], 'not'),
  apply: (expression) => {
    const belief = requireCognitive(expression, 'B');
    if (!isUnary(belief.args[1], 'not')) throw new Error('Invalid CEC belief negation premise');
    return {
      kind: 'unary',
      operator: 'not',
      expression: cognitiveApplication('B', belief.args[0], belief.args[1].expression),
    };
  },
});

export const CecKnowledgeConjunctionRule = new CecRule({
  name: 'CecKnowledgeConjunction',
  description: 'From (K agent phi) and (K agent psi), infer (K agent (and phi psi))',
  arity: 2,
  canApply: (left, right) =>
    isCognitive(left, 'K') &&
    isCognitive(right, 'K') &&
    cecExpressionEquals(left.args[0], right.args[0]) &&
    !cecExpressionEquals(left.args[1], right.args[1]),
  apply: (left, right) => {
    const leftKnowledge = requireCognitive(left, 'K');
    const rightKnowledge = requireCognitive(right, 'K');
    return cognitiveApplication('K', leftKnowledge.args[0], {
      kind: 'binary',
      operator: 'and',
      left: leftKnowledge.args[1],
      right: rightKnowledge.args[1],
    });
  },
});

export const CecIntentionPersistenceRule = new CecRule({
  name: 'CecIntentionPersistence',
  description: 'From (I agent phi) and (not (B agent phi)), infer (I agent phi)',
  arity: 2,
  canApply: (intention, notBelief) =>
    isCognitive(intention, 'I') &&
    isUnary(notBelief, 'not') &&
    isCognitive(notBelief.expression, 'B') &&
    cecExpressionEquals(intention.args[0], notBelief.expression.args[0]) &&
    cecExpressionEquals(intention.args[1], notBelief.expression.args[1]),
  apply: (intention) => intention,
});

export const CecBeliefRevisionRule = new CecRule({
  name: 'CecBeliefRevision',
  description: 'From (B agent phi) and (Perceives agent (not phi)), infer (B agent (not phi))',
  arity: 2,
  canApply: (belief, perception) =>
    isCognitive(belief, 'B') &&
    (isCognitive(perception, 'Perceives') || isCognitive(perception, 'Perception')) &&
    cecExpressionEquals(belief.args[0], perception.args[0]) &&
    isUnary(perception.args[1], 'not') &&
    cecExpressionEquals(belief.args[1], perception.args[1].expression),
  apply: (belief, perception) => {
    const premise = requireCognitive(belief, 'B');
    const perceived = requireAnyCognitive(perception, ['Perceives', 'Perception']);
    return cognitiveApplication('B', premise.args[0], perceived.args[1]);
  },
});

export const CecKnowledgeMonotonicityRule = new CecRule({
  name: 'CecKnowledgeMonotonicity',
  description: 'From (K agent phi) and (implies phi psi), infer (K agent psi)',
  arity: 2,
  canApply: (knowledge, implication) =>
    isCognitive(knowledge, 'K') &&
    isBinary(implication, 'implies') &&
    cecExpressionEquals(knowledge.args[1], implication.left),
  apply: (knowledge, implication) => {
    const premise = requireCognitive(knowledge, 'K');
    if (!isBinary(implication, 'implies'))
      throw new Error('Invalid CEC knowledge monotonicity implication');
    return cognitiveApplication('K', premise.args[0], implication.right);
  },
});

export const CecCommonKnowledgeIntroductionRule = new CecRule({
  name: 'CecCommonKnowledgeIntroduction',
  description: 'From (K agent1 phi) and (K agent2 phi), infer (C all phi)',
  arity: 2,
  canApply: (left, right) =>
    isCognitive(left, 'K') &&
    isCognitive(right, 'K') &&
    !cecExpressionEquals(left.args[0], right.args[0]) &&
    cecExpressionEquals(left.args[1], right.args[1]),
  apply: (left, right) => {
    const first = requireCognitive(left, 'K');
    const second = requireCognitive(right, 'K');
    if (!cecExpressionEquals(first.args[1], second.args[1]))
      throw new Error('Invalid CEC common knowledge premises');
    return cognitiveApplication('C', atom('all'), first.args[1]);
  },
});

export const CecCommonBeliefIntroductionRule = new CecRule({
  name: 'CecCommonBeliefIntroduction',
  description: 'From (B agent1 phi) and (B agent2 phi), infer (CB all phi)',
  arity: 2,
  canApply: (left, right) =>
    isCognitive(left, 'B') &&
    isCognitive(right, 'B') &&
    !cecExpressionEquals(left.args[0], right.args[0]) &&
    cecExpressionEquals(left.args[1], right.args[1]),
  apply: (left, right) => {
    const first = requireCognitive(left, 'B');
    const second = requireCognitive(right, 'B');
    if (!cecExpressionEquals(first.args[1], second.args[1]))
      throw new Error('Invalid CEC common belief premises');
    return cognitiveApplication('CB', atom('all'), first.args[1]);
  },
});

export const CecCommonKnowledgeDistributionRule = new CecRule({
  name: 'CecCommonKnowledgeDistribution',
  description: 'From (C agent (and phi psi)), infer (and (C agent phi) (C agent psi))',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'C') && isBinary(expression.args[1], 'and'),
  apply: (expression) => {
    const common = requireCognitive(expression, 'C');
    if (!isBinary(common.args[1], 'and'))
      throw new Error('Invalid CEC common knowledge distribution premise');
    return {
      kind: 'binary',
      operator: 'and',
      left: cognitiveApplication('C', common.args[0], common.args[1].left),
      right: cognitiveApplication('C', common.args[0], common.args[1].right),
    };
  },
});

export const CecCommonKnowledgeImpliesKnowledgeRule = new CecRule({
  name: 'CecCommonKnowledgeImpliesKnowledge',
  description: 'From (C agent phi), infer (K agent phi)',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'C'),
  apply: (expression) => {
    const common = requireCognitive(expression, 'C');
    return cognitiveApplication('K', common.args[0], common.args[1]);
  },
});

export const CecCommonKnowledgeMonotonicityRule = new CecRule({
  name: 'CecCommonKnowledgeMonotonicity',
  description: 'From (C agent phi) and (implies phi psi), infer (C agent psi)',
  arity: 2,
  canApply: (common, implication) =>
    isCognitive(common, 'C') &&
    isBinary(implication, 'implies') &&
    cecExpressionEquals(common.args[1], implication.left),
  apply: (common, implication) => {
    const premise = requireCognitive(common, 'C');
    if (!isBinary(implication, 'implies'))
      throw new Error('Invalid CEC common knowledge monotonicity implication');
    return cognitiveApplication('C', premise.args[0], implication.right);
  },
});

export const CecCommonKnowledgeNegationRule = new CecRule({
  name: 'CecCommonKnowledgeNegation',
  description: 'From (C agent (not phi)), infer (not (C agent phi))',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'C') && isUnary(expression.args[1], 'not'),
  apply: (expression) => {
    const common = requireCognitive(expression, 'C');
    if (!isUnary(common.args[1], 'not'))
      throw new Error('Invalid CEC common knowledge negation premise');
    return {
      kind: 'unary',
      operator: 'not',
      expression: cognitiveApplication('C', common.args[0], common.args[1].expression),
    };
  },
});

export const CecCommonKnowledgeTransitivityRule = new CecRule({
  name: 'CecCommonKnowledgeTransitivity',
  description: 'From (C agent (C other phi)), infer (C agent phi)',
  arity: 1,
  canApply: (expression) => isCognitive(expression, 'C') && isCognitive(expression.args[1], 'C'),
  apply: (expression) => {
    const outer = requireCognitive(expression, 'C');
    const inner = requireCognitive(outer.args[1], 'C');
    return cognitiveApplication('C', outer.args[0], inner.args[1]);
  },
});

export const CecFixedPointInductionRule = new CecRule({
  name: 'CecFixedPointInduction',
  description: 'From phi and (implies phi (K everyone phi)), infer (C everyone phi)',
  arity: 2,
  canApply: (fact, implication) =>
    isBinary(implication, 'implies') &&
    cecExpressionEquals(implication.left, fact) &&
    isCognitive(implication.right, 'K') &&
    cecExpressionEquals(implication.right.args[1], fact),
  apply: (fact, implication) => {
    if (!isBinary(implication, 'implies') || !isCognitive(implication.right, 'K')) {
      throw new Error('Invalid CEC fixed point induction premises');
    }
    return cognitiveApplication('C', implication.right.args[0], fact);
  },
});

export const CecTemporallyInducedCommonKnowledgeRule = new CecRule({
  name: 'CecTemporallyInducedCommonKnowledge',
  description: 'From (always (K all phi)), infer (C all phi)',
  arity: 1,
  canApply: (expression) =>
    isUnary(expression, 'always') && isCognitive(expression.expression, 'K'),
  apply: (expression) => {
    if (!isUnary(expression, 'always') || !isCognitive(expression.expression, 'K')) {
      throw new Error('Invalid CEC temporally induced common knowledge premise');
    }
    return cognitiveApplication('C', expression.expression.args[0], expression.expression.args[1]);
  },
});

export const CecModalNecessitationIntroductionRule = new CecRule({
  name: 'CecModalNecessitationIntroduction',
  description: 'From a tautology (or phi (not phi)), infer (always (or phi (not phi)))',
  arity: 1,
  canApply: (expression) =>
    isBinary(expression, 'or') &&
    (isNegationOf(expression.left, expression.right) ||
      isNegationOf(expression.right, expression.left)),
  apply: (expression) => {
    if (!isBinary(expression, 'or')) throw new Error('Invalid CEC modal necessitation premise');
    return { kind: 'unary', operator: 'always', expression };
  },
});

export const CecResolutionRule = new CecRule({
  name: 'CecResolution',
  description: 'From (or phi psi) and (or (not phi) chi), infer (or psi chi)',
  arity: 2,
  canApply: (left, right) => findComplementaryDisjunctPair(left, right) !== undefined,
  apply: (left, right) => {
    const pair = findComplementaryDisjunctPair(left, right);
    if (!pair) throw new Error('Invalid CEC resolution clauses');
    const remaining = [
      ...getDisjuncts(left).filter((_, index) => index !== pair.leftIndex),
      ...getDisjuncts(right).filter((_, index) => index !== pair.rightIndex),
    ];
    return buildDisjunction(uniqueExpressions(remaining));
  },
});

export const CecUnitResolutionRule = new CecRule({
  name: 'CecUnitResolution',
  description: 'From phi and (or (not phi) psi), infer psi',
  arity: 2,
  canApply: (unit, clause) =>
    !isBinary(unit, 'or') &&
    isBinary(clause, 'or') &&
    getDisjuncts(clause).some((literal) => isNegationOf(literal, unit)),
  apply: (unit, clause) => {
    if (!isBinary(clause, 'or')) throw new Error('Invalid CEC unit resolution clause');
    return buildDisjunction(getDisjuncts(clause).filter((literal) => !isNegationOf(literal, unit)));
  },
});

export const CecFactoringRule = new CecRule({
  name: 'CecFactoring',
  description: 'From a disjunction with duplicate literals, infer the deduplicated clause',
  arity: 1,
  canApply: (expression) =>
    isBinary(expression, 'or') &&
    uniqueExpressions(getDisjuncts(expression)).length < getDisjuncts(expression).length,
  apply: (expression) => {
    if (!isBinary(expression, 'or')) throw new Error('Invalid CEC factoring clause');
    return buildDisjunction(uniqueExpressions(getDisjuncts(expression)));
  },
});

export const CecSubsumptionRule = new CecRule({
  name: 'CecSubsumption',
  description: 'If clause C1 is a strict subset of C2, infer the shorter subsuming clause',
  arity: 2,
  canApply: (left, right) => clauseSubsumes(left, right) || clauseSubsumes(right, left),
  apply: (left, right) => {
    if (clauseSubsumes(left, right)) return left;
    if (clauseSubsumes(right, left)) return right;
    throw new Error('Invalid CEC subsumption clauses');
  },
});

export const CecCaseAnalysisRule = new CecRule({
  name: 'CecCaseAnalysis',
  description: 'From (or phi psi), (implies phi chi), and (implies psi chi), infer chi',
  arity: 3,
  canApply: (disjunction, leftImplication, rightImplication) => {
    if (
      !isBinary(disjunction, 'or') ||
      !isBinary(leftImplication, 'implies') ||
      !isBinary(rightImplication, 'implies')
    )
      return false;
    const [leftCase, rightCase] = getDisjuncts(disjunction);
    return (
      Boolean(leftCase && rightCase) &&
      cecExpressionEquals(leftImplication.left, leftCase) &&
      cecExpressionEquals(rightImplication.left, rightCase) &&
      cecExpressionEquals(leftImplication.right, rightImplication.right)
    );
  },
  apply: (_disjunction, leftImplication) => {
    if (!isBinary(leftImplication, 'implies'))
      throw new Error('Invalid CEC case analysis implication');
    return leftImplication.right;
  },
});

export const CecProofByContradictionRule = new CecRule({
  name: 'CecProofByContradiction',
  description: 'From phi and (not phi), infer contradiction',
  arity: 2,
  canApply: (left, right) => isNegationOf(left, right) || isNegationOf(right, left),
  apply: () => ({ kind: 'atom', name: 'contradiction' }),
});

export const CecBiconditionalIntroductionRule = new CecRule({
  name: 'CecBiconditionalIntroduction',
  description: 'From (implies phi psi) and (implies psi phi), infer (iff phi psi)',
  arity: 2,
  canApply: (left, right) =>
    isBinary(left, 'implies') &&
    isBinary(right, 'implies') &&
    cecExpressionEquals(left.left, right.right) &&
    cecExpressionEquals(left.right, right.left),
  apply: (left) => {
    if (!isBinary(left, 'implies'))
      throw new Error('Invalid CEC biconditional introduction premise');
    return { kind: 'binary', operator: 'iff', left: left.left, right: left.right };
  },
});

export const CecBiconditionalEliminationRule = new CecRule({
  name: 'CecBiconditionalElimination',
  description: 'From (iff phi psi), infer (and (implies phi psi) (implies psi phi))',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'iff'),
  apply: (expression) => {
    if (!isBinary(expression, 'iff'))
      throw new Error('Invalid CEC biconditional elimination premise');
    return {
      kind: 'binary',
      operator: 'and',
      left: { kind: 'binary', operator: 'implies', left: expression.left, right: expression.right },
      right: {
        kind: 'binary',
        operator: 'implies',
        left: expression.right,
        right: expression.left,
      },
    };
  },
});

export const CecConstructiveDilemmaRule = new CecRule({
  name: 'CecConstructiveDilemma',
  description:
    'From (implies phi psi), (implies chi omega), and (or phi chi), infer (or psi omega)',
  arity: 3,
  canApply: (...expressions) => findDilemmaPremises(expressions, false) !== undefined,
  apply: (...expressions) => {
    const premises = findDilemmaPremises(expressions, false);
    if (!premises) throw new Error('Invalid CEC constructive dilemma premises');
    return buildDisjunction([premises.first.right, premises.second.right]);
  },
});

export const CecDestructiveDilemmaRule = new CecRule({
  name: 'CecDestructiveDilemma',
  description:
    'From (implies phi psi), (implies chi omega), and (or (not psi) (not omega)), infer (or (not phi) (not chi))',
  arity: 3,
  canApply: (...expressions) => findDilemmaPremises(expressions, true) !== undefined,
  apply: (...expressions) => {
    const premises = findDilemmaPremises(expressions, true);
    if (!premises) throw new Error('Invalid CEC destructive dilemma premises');
    return buildDisjunction([
      { kind: 'unary', operator: 'not', expression: premises.first.left },
      { kind: 'unary', operator: 'not', expression: premises.second.left },
    ]);
  },
});

export const CecExportationRule = new CecRule({
  name: 'CecExportation',
  description: 'From (implies (and phi psi) chi), infer (implies phi (implies psi chi))',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'implies') && isBinary(expression.left, 'and'),
  apply: (expression) => {
    if (!isBinary(expression, 'implies') || !isBinary(expression.left, 'and')) {
      throw new Error('Invalid CEC exportation premise');
    }
    return {
      kind: 'binary',
      operator: 'implies',
      left: expression.left.left,
      right: {
        kind: 'binary',
        operator: 'implies',
        left: expression.left.right,
        right: expression.right,
      },
    };
  },
});

export const CecAbsorptionRule = new CecRule({
  name: 'CecAbsorption',
  description: 'From (implies phi psi), infer (implies phi (and phi psi))',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'implies'),
  apply: (expression) => {
    if (!isBinary(expression, 'implies')) throw new Error('Invalid CEC absorption premise');
    return {
      kind: 'binary',
      operator: 'implies',
      left: expression.left,
      right: { kind: 'binary', operator: 'and', left: expression.left, right: expression.right },
    };
  },
});

export const CecAdditionRule = new CecRule({
  name: 'CecAddition',
  description:
    'From phi and psi, infer (or phi psi); kept opt-in because it generates new disjunctions',
  arity: 2,
  canApply: (left, right) => !cecExpressionEquals(left, right),
  apply: (left, right) => buildDisjunction([left, right]),
});

export const CecTautologyRule = new CecRule({
  name: 'CecTautology',
  description: 'From (or phi phi), infer phi',
  arity: 1,
  canApply: (expression) =>
    isBinary(expression, 'or') &&
    getDisjuncts(expression).length > 1 &&
    uniqueExpressions(getDisjuncts(expression)).length === 1,
  apply: (expression) => {
    if (!isBinary(expression, 'or')) throw new Error('Invalid CEC tautology premise');
    return getDisjuncts(expression)[0];
  },
});

export const CecCommutativityConjunctionRule = new CecRule({
  name: 'CecCommutativityConjunction',
  description: 'From (and phi psi), infer (and psi phi)',
  arity: 1,
  canApply: (expression) =>
    isBinary(expression, 'and') && !cecExpressionEquals(expression.left, expression.right),
  apply: (expression) => {
    if (!isBinary(expression, 'and'))
      throw new Error('Invalid CEC conjunction commutativity premise');
    return { kind: 'binary', operator: 'and', left: expression.right, right: expression.left };
  },
});

export const CecCommutativityDisjunctionRule = new CecRule({
  name: 'CecCommutativityDisjunction',
  description: 'From (or phi psi), infer (or psi phi)',
  arity: 1,
  canApply: (expression) =>
    isBinary(expression, 'or') && !cecExpressionEquals(expression.left, expression.right),
  apply: (expression) => {
    if (!isBinary(expression, 'or'))
      throw new Error('Invalid CEC disjunction commutativity premise');
    return { kind: 'binary', operator: 'or', left: expression.right, right: expression.left };
  },
});

export const CecDistributionRule = new CecRule({
  name: 'CecDistribution',
  description: 'Distribute disjunction over conjunction, or conjunction over disjunction',
  arity: 1,
  canApply: (expression) =>
    (isBinary(expression, 'or') &&
      (isBinary(expression.left, 'and') || isBinary(expression.right, 'and'))) ||
    (isBinary(expression, 'and') &&
      (isBinary(expression.left, 'or') || isBinary(expression.right, 'or'))),
  apply: (expression) => {
    if (isBinary(expression, 'or')) {
      const disjunction = expression as CecBinaryExpression;
      const conjunct = isBinary(disjunction.left, 'and')
        ? disjunction.left
        : isBinary(disjunction.right, 'and')
          ? disjunction.right
          : undefined;
      const other = conjunct === disjunction.left ? disjunction.right : disjunction.left;
      if (!conjunct) throw new Error('Invalid CEC OR distribution premise');
      return buildConjunction([
        buildDisjunction([other, conjunct.left]),
        buildDisjunction([other, conjunct.right]),
      ]);
    }
    if (isBinary(expression, 'and')) {
      const conjunction = expression as CecBinaryExpression;
      const disjunct = isBinary(conjunction.left, 'or')
        ? conjunction.left
        : isBinary(conjunction.right, 'or')
          ? conjunction.right
          : undefined;
      const other = disjunct === conjunction.left ? conjunction.right : conjunction.left;
      if (!disjunct) throw new Error('Invalid CEC AND distribution premise');
      return buildDisjunction([
        buildConjunction([other, disjunct.left]),
        buildConjunction([other, disjunct.right]),
      ]);
    }
    throw new Error('Invalid CEC distribution premise');
  },
});

export const CecAssociationRule = new CecRule({
  name: 'CecAssociation',
  description: 'Re-associate nested conjunctions or disjunctions with the same connective',
  arity: 1,
  canApply: (expression) =>
    (isBinary(expression, 'and') &&
      (isBinary(expression.left, 'and') || isBinary(expression.right, 'and'))) ||
    (isBinary(expression, 'or') &&
      (isBinary(expression.left, 'or') || isBinary(expression.right, 'or'))),
  apply: (expression) => {
    if (isBinary(expression, 'and')) return associateSameOperator(expression, 'and');
    if (isBinary(expression, 'or')) return associateSameOperator(expression, 'or');
    throw new Error('Invalid CEC association premise');
  },
});

export const CecTranspositionRule = new CecRule({
  name: 'CecTransposition',
  description: 'From (implies phi psi), infer (implies (not psi) (not phi))',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'implies'),
  apply: (expression) => {
    if (!isBinary(expression, 'implies')) throw new Error('Invalid CEC transposition premise');
    return {
      kind: 'binary',
      operator: 'implies',
      left: { kind: 'unary', operator: 'not', expression: expression.right },
      right: { kind: 'unary', operator: 'not', expression: expression.left },
    };
  },
});

export const CecMaterialImplicationRule = new CecRule({
  name: 'CecMaterialImplication',
  description: 'Convert between (implies phi psi) and (or (not phi) psi)',
  arity: 1,
  canApply: (expression) => isBinary(expression, 'implies') || isMaterialDisjunction(expression),
  apply: (expression) => {
    if (isBinary(expression, 'implies')) {
      const implication = expression as CecBinaryExpression;
      return {
        kind: 'binary',
        operator: 'or',
        left: { kind: 'unary', operator: 'not', expression: implication.left },
        right: implication.right,
      };
    }
    if (isMaterialDisjunction(expression)) {
      const disjunction = expression as CecBinaryExpression & { left: CecUnaryExpression };
      return {
        kind: 'binary',
        operator: 'implies',
        left: disjunction.left.expression,
        right: disjunction.right,
      };
    }
    throw new Error('Invalid CEC material implication premise');
  },
});

export const CecClaviusLawRule = new CecRule({
  name: 'CecClaviusLaw',
  description: 'From (implies (not phi) phi), infer phi',
  arity: 1,
  canApply: (expression) =>
    isBinary(expression, 'implies') &&
    isUnary(expression.left, 'not') &&
    cecExpressionEquals(expression.left.expression, expression.right),
  apply: (expression) => {
    if (!isBinary(expression, 'implies') || !isUnary(expression.left, 'not')) {
      throw new Error('Invalid CEC Clavius premise');
    }
    return expression.right;
  },
});

export const CecIdempotenceRule = new CecRule({
  name: 'CecIdempotence',
  description: 'From (and phi phi) or (or phi phi), infer phi',
  arity: 1,
  canApply: (expression) =>
    isAndOrBinary(expression) &&
    idempotentParts(expression).every((part) =>
      cecExpressionEquals(part, idempotentParts(expression)[0]),
    ),
  apply: (expression) => {
    if (!isAndOrBinary(expression)) {
      throw new Error('Invalid CEC idempotence premise');
    }
    return idempotentParts(expression)[0];
  },
});

export function getAllCecRules(): CecInferenceRule[] {
  return [
    CecModusPonensRule,
    CecHypotheticalSyllogismRule,
    CecConjunctionEliminationLeftRule,
    CecConjunctionEliminationRightRule,
    CecDoubleNegationEliminationRule,
    CecTemporalTRule,
    CecDeonticDRule,
    CecProhibitionEquivalenceRule,
    CecProhibitionFromObligationRule,
    CecUniversalModusPonensRule,
    CecExistentialInstantiationRule,
  ];
}

export function getResolutionCecRules(): CecInferenceRule[] {
  return [
    CecResolutionRule,
    CecUnitResolutionRule,
    CecFactoringRule,
    CecSubsumptionRule,
    CecCaseAnalysisRule,
    CecProofByContradictionRule,
  ];
}

export function getTemporalCecRules(): CecInferenceRule[] {
  return [
    CecTemporalTRule,
    CecAlwaysDistributionRule,
    CecAlwaysImplicationRule,
    CecAlwaysTransitiveRule,
    CecAlwaysImpliesNextRule,
    CecAlwaysInductionRule,
    CecEventuallyFromAlwaysRule,
    CecEventuallyDistributionRule,
    CecEventuallyTransitiveRule,
    CecEventuallyImplicationRule,
    CecNextDistributionRule,
    CecNextImplicationRule,
    CecUntilWeakeningRule,
    CecSinceWeakeningRule,
    CecTemporalUntilEliminationRule,
    CecTemporalNegationRule,
  ];
}

export function getDeonticCecRules(): CecInferenceRule[] {
  return [
    CecDeonticDRule,
    CecProhibitionEquivalenceRule,
    CecProhibitionFromObligationRule,
    CecObligationDistributionRule,
    CecObligationImplicationRule,
    CecPermissionFromNonObligationRule,
    CecPermissionDistributionRule,
    CecObligationConsistencyRule,
  ];
}

export const CEC_NATIVE_INFERENCE_RUNTIMES = {
  base: {
    sourcePythonModule: 'logic/CEC/native/inference_rules/base.py',
    browserNative: true,
    pythonRuntime: false,
  },
  cognitive: {
    sourcePythonModule: 'logic/CEC/native/inference_rules/cognitive.py',
    browserNative: true,
    pythonRuntime: false,
  },
  modal: {
    sourcePythonModule: 'logic/CEC/native/inference_rules/modal.py',
    browserNative: true,
    pythonRuntime: false,
  },
} as const;

const nativeSpec = (
  pythonRuleName: CecNativePythonRuleName,
  ruleGroup: CecNativeInferenceRuleGroup,
  rule: CecInferenceRule,
): CecNativePythonRuleSpec => ({ pythonRuleName, ruleGroup, rule });

const CEC_NATIVE_PYTHON_RULE_SPECS: readonly CecNativePythonRuleSpec[] = [
  nativeSpec('ModusPonens', 'base', CecModusPonensRule),
  nativeSpec('HypotheticalSyllogism', 'base', CecHypotheticalSyllogismRule),
  nativeSpec('ConjunctionIntroduction', 'base', CecConjunctionIntroductionRule),
  nativeSpec('ConjunctionEliminationLeft', 'base', CecConjunctionEliminationLeftRule),
  nativeSpec('ConjunctionEliminationRight', 'base', CecConjunctionEliminationRightRule),
  nativeSpec('DoubleNegationElimination', 'base', CecDoubleNegationEliminationRule),
  nativeSpec('BeliefDistribution', 'cognitive', CecBeliefDistributionRule),
  nativeSpec('BeliefConjunction', 'cognitive', CecBeliefConjunctionRule),
  nativeSpec('BeliefMonotonicity', 'cognitive', CecBeliefMonotonicityRule),
  nativeSpec('BeliefNegation', 'cognitive', CecBeliefNegationRule),
  nativeSpec('BeliefRevision', 'cognitive', CecBeliefRevisionRule),
  nativeSpec('KnowledgeImpliesBelief', 'cognitive', CecKnowledgeImpliesBeliefRule),
  nativeSpec('KnowledgeDistribution', 'cognitive', CecKnowledgeDistributionRule),
  nativeSpec('KnowledgeConjunction', 'cognitive', CecKnowledgeConjunctionRule),
  nativeSpec('KnowledgeMonotonicity', 'cognitive', CecKnowledgeMonotonicityRule),
  nativeSpec('CommonBeliefIntroduction', 'cognitive', CecCommonBeliefIntroductionRule),
  nativeSpec('CommonKnowledgeDistribution', 'cognitive', CecCommonKnowledgeDistributionRule),
  nativeSpec(
    'CommonKnowledgeImpliesKnowledge',
    'cognitive',
    CecCommonKnowledgeImpliesKnowledgeRule,
  ),
  nativeSpec('CommonKnowledgeIntroduction', 'cognitive', CecCommonKnowledgeIntroductionRule),
  nativeSpec('CommonKnowledgeMonotonicity', 'cognitive', CecCommonKnowledgeMonotonicityRule),
  nativeSpec('CommonKnowledgeNegation', 'cognitive', CecCommonKnowledgeNegationRule),
  nativeSpec('CommonKnowledgeTransitivity', 'cognitive', CecCommonKnowledgeTransitivityRule),
  nativeSpec('IntentionCommitment', 'cognitive', CecIntentionCommitmentRule),
  nativeSpec('IntentionMeansEnd', 'cognitive', CecIntentionMeansEndRule),
  nativeSpec('IntentionPersistence', 'cognitive', CecIntentionPersistenceRule),
  nativeSpec('PerceptionImpliesKnowledge', 'cognitive', CecPerceptionImpliesKnowledgeRule),
  nativeSpec(
    'TemporallyInducedCommonKnowledge',
    'cognitive',
    CecTemporallyInducedCommonKnowledgeRule,
  ),
  nativeSpec('NecessityElimination', 'modal', CecNecessityEliminationRule),
  nativeSpec('NecessityDistribution', 'modal', CecNecessityDistributionRule),
  nativeSpec('PossibilityIntroduction', 'modal', CecPossibilityIntroductionRule),
  nativeSpec('PossibilityDuality', 'modal', CecPossibilityDualityRule),
  nativeSpec('NecessityConjunction', 'modal', CecNecessityConjunctionRule),
  nativeSpec('NecessitationIntroduction', 'modal', CecModalNecessitationIntroductionRule),
];

export function getCecNativeInferenceRuleTables(): Record<
  CecNativeInferenceRuleGroup,
  readonly CecNativePythonRuleName[]
> {
  return {
    base: ruleNamesForGroup('base'),
    cognitive: ruleNamesForGroup('cognitive'),
    modal: ruleNamesForGroup('modal'),
  };
}

export function applyCecNativePythonParityRules(
  expressions: CecExpression[],
  ruleGroups: readonly CecNativeInferenceRuleGroup[] = ['base', 'cognitive', 'modal'],
): CecNativePythonRuleApplication[] {
  const enabled = new Set<CecNativeInferenceRuleGroup>(ruleGroups);
  const applications: CecNativePythonRuleApplication[] = [];

  for (const spec of CEC_NATIVE_PYTHON_RULE_SPECS) {
    if (!enabled.has(spec.ruleGroup)) continue;
    const application = applyFirstCecRuleMatch(expressions, spec.rule);
    if (!application) continue;
    const runtime = CEC_NATIVE_INFERENCE_RUNTIMES[spec.ruleGroup];
    applications.push({
      rule: spec.rule.name,
      pythonRuleName: spec.pythonRuleName,
      ruleGroup: spec.ruleGroup,
      sourcePythonModule: runtime.sourcePythonModule,
      premises: application.premises,
      conclusion: application.conclusion,
      status: 'SUCCESS',
      proofStep: {
        stepId: applications.length + 1,
        rule: spec.rule.name,
        pythonRuleName: spec.pythonRuleName,
        ruleGroup: spec.ruleGroup,
        sourcePythonModule: runtime.sourcePythonModule,
        premiseCount: application.premises.length,
        conclusionCount: 1,
        status: 'SUCCESS',
        browserNative: runtime.browserNative,
        pythonRuntime: runtime.pythonRuntime,
      },
    });
  }

  return applications;
}

export const CEC_DEONTIC_INFERENCE_RUNTIME = {
  sourcePythonModule: 'logic/CEC/native/inference_rules/deontic.py',
  browserNative: true,
  pythonRuntime: false,
} as const;

const CEC_DEONTIC_PYTHON_RULE_SPECS: readonly {
  pythonRuleName: CecDeonticPythonRuleName;
  rule: CecInferenceRule;
}[] = [
  { pythonRuleName: 'ObligationDistribution', rule: CecObligationDistributionRule },
  { pythonRuleName: 'ObligationImplication', rule: CecObligationImplicationRule },
  { pythonRuleName: 'PermissionFromNonObligation', rule: CecPermissionFromNonObligationRule },
  { pythonRuleName: 'ObligationConjunction', rule: CecObligationConjunctionRule },
  { pythonRuleName: 'PermissionDistribution', rule: CecPermissionDistributionRule },
  { pythonRuleName: 'ObligationConsistency', rule: CecObligationConsistencyRule },
  { pythonRuleName: 'ProhibitionEquivalence', rule: CecProhibitionEquivalenceRule },
];

export function getCecDeonticPythonParityRuleNames(): readonly CecDeonticPythonRuleName[] {
  return CEC_DEONTIC_PYTHON_RULE_SPECS.map((spec) => spec.pythonRuleName);
}

export function applyCecDeonticPythonParityRules(
  expressions: CecExpression[],
): CecDeonticPythonRuleApplication[] {
  const applications: CecDeonticPythonRuleApplication[] = [];

  for (const spec of CEC_DEONTIC_PYTHON_RULE_SPECS) {
    const application = applyFirstCecRuleMatch(expressions, spec.rule);
    if (!application) continue;
    applications.push({
      rule: spec.rule.name,
      pythonRuleName: spec.pythonRuleName,
      premises: application.premises,
      conclusions: [application.conclusion],
      status: 'SUCCESS',
      metadata: CEC_DEONTIC_INFERENCE_RUNTIME,
    });
  }

  return applications;
}

export function getModalCecRules(): CecInferenceRule[] {
  return [CecNecessityEliminationRule, CecNecessityDistributionRule, CecPossibilityDualityRule];
}

export function getSpecializedCecRules(): CecInferenceRule[] {
  return [
    CecBiconditionalIntroductionRule,
    CecBiconditionalEliminationRule,
    CecConstructiveDilemmaRule,
    CecDestructiveDilemmaRule,
    CecExportationRule,
    CecAbsorptionRule,
    CecTautologyRule,
    CecCommutativityConjunctionRule,
    CecCommutativityDisjunctionRule,
    CecDistributionRule,
    CecAssociationRule,
    CecTranspositionRule,
    CecMaterialImplicationRule,
    CecClaviusLawRule,
    CecIdempotenceRule,
  ];
}

export function getCognitiveCecRules(): CecInferenceRule[] {
  return [
    CecBeliefDistributionRule,
    CecKnowledgeImpliesBeliefRule,
    CecBeliefMonotonicityRule,
    CecIntentionCommitmentRule,
    CecKnowledgeDistributionRule,
    CecIntentionMeansEndRule,
    CecPerceptionImpliesKnowledgeRule,
    CecBeliefNegationRule,
    CecIntentionPersistenceRule,
    CecBeliefRevisionRule,
    CecKnowledgeMonotonicityRule,
    CecCommonKnowledgeDistributionRule,
    CecCommonKnowledgeImpliesKnowledgeRule,
    CecCommonKnowledgeMonotonicityRule,
    CecCommonKnowledgeNegationRule,
    CecCommonKnowledgeTransitivityRule,
    CecTemporallyInducedCommonKnowledgeRule,
  ];
}

export function getGenerativeCecRules(): CecInferenceRule[] {
  return [
    CecConjunctionIntroductionRule,
    CecEventuallyIntroductionRule,
    CecExistentialGeneralizationRule,
    CecUniversalGeneralizationRule,
    CecBeliefConjunctionRule,
    CecKnowledgeConjunctionRule,
    CecAdditionRule,
    CecObligationConjunctionRule,
    CecPossibilityIntroductionRule,
    CecNecessityConjunctionRule,
    CecCommonKnowledgeIntroductionRule,
    CecCommonBeliefIntroductionRule,
    CecFixedPointInductionRule,
    CecModalNecessitationIntroductionRule,
  ];
}

export function applyCecRules(
  expressions: CecExpression[],
  rules: CecInferenceRule[] = getAllCecRules(),
): CecRuleApplication[] {
  const applications: CecRuleApplication[] = [];
  for (const rule of rules) {
    if (rule.arity === 1) {
      for (const expression of expressions) {
        if (rule.canApply(expression)) {
          applications.push({
            rule: rule.name,
            premises: [expression],
            conclusion: rule.apply(expression),
          });
        }
      }
    } else if (rule.arity === 2) {
      for (const left of expressions) {
        for (const right of expressions) {
          if (rule.canApply(left, right)) {
            applications.push({
              rule: rule.name,
              premises: [left, right],
              conclusion: rule.apply(left, right),
            });
          }
        }
      }
    } else {
      for (const first of expressions) {
        for (const second of expressions) {
          for (const third of expressions) {
            if (rule.canApply(first, second, third)) {
              applications.push({
                rule: rule.name,
                premises: [first, second, third],
                conclusion: rule.apply(first, second, third),
              });
            }
          }
        }
      }
    }
  }
  return applications;
}

function applyFirstCecRuleMatch(
  expressions: CecExpression[],
  rule: CecInferenceRule,
): CecRuleApplication | undefined {
  if (rule.arity === 1) {
    for (const expression of expressions) {
      if (rule.canApply(expression)) {
        return { rule: rule.name, premises: [expression], conclusion: rule.apply(expression) };
      }
    }
    return undefined;
  }

  if (rule.arity === 2) {
    for (const left of expressions) {
      for (const right of expressions) {
        if (rule.canApply(left, right)) {
          return { rule: rule.name, premises: [left, right], conclusion: rule.apply(left, right) };
        }
      }
    }
    return undefined;
  }

  for (const first of expressions) {
    for (const second of expressions) {
      for (const third of expressions) {
        if (rule.canApply(first, second, third)) {
          return {
            rule: rule.name,
            premises: [first, second, third],
            conclusion: rule.apply(first, second, third),
          };
        }
      }
    }
  }
  return undefined;
}

function ruleNamesForGroup(
  ruleGroup: CecNativeInferenceRuleGroup,
): readonly CecNativePythonRuleName[] {
  return CEC_NATIVE_PYTHON_RULE_SPECS.filter((spec) => spec.ruleGroup === ruleGroup).map(
    (spec) => spec.pythonRuleName,
  );
}

export function cecExpressionEquals(left: CecExpression, right: CecExpression): boolean {
  return cecExpressionKey(left) === cecExpressionKey(right);
}

export function cecExpressionKey(expression: CecExpression): string {
  return formatCecExpression(expression);
}

function isBinary(
  expression: CecExpression,
  operator: CecBinaryExpression['operator'],
): expression is CecBinaryExpression {
  return expression.kind === 'binary' && expression.operator === operator;
}

function isAndOrBinary(
  expression: CecExpression,
): expression is CecBinaryExpression & { operator: 'and' | 'or' } {
  return isBinary(expression, 'and') || isBinary(expression, 'or');
}

function isMaterialDisjunction(
  expression: CecExpression,
): expression is CecBinaryExpression & { operator: 'or'; left: CecUnaryExpression } {
  return isBinary(expression, 'or') && isUnary((expression as CecBinaryExpression).left, 'not');
}

function isUnary(
  expression: CecExpression,
  operator: CecUnaryExpression['operator'],
): expression is CecUnaryExpression {
  return expression.kind === 'unary' && expression.operator === operator;
}

function isQuantified(
  expression: CecExpression,
  quantifier: CecQuantifiedExpression['quantifier'],
): expression is CecQuantifiedExpression {
  return expression.kind === 'quantified' && expression.quantifier === quantifier;
}

function isCognitive(expression: CecExpression, operator: string): expression is CecApplication {
  return (
    expression.kind === 'application' &&
    expression.name === operator &&
    expression.args.length === 2
  );
}

function requireCognitive(expression: CecExpression, operator: string): CecApplication {
  if (!isCognitive(expression, operator))
    throw new Error(`Invalid CEC cognitive ${operator} premise`);
  return expression;
}

function requireAnyCognitive(expression: CecExpression, operators: string[]): CecApplication {
  if (
    expression.kind === 'application' &&
    operators.includes(expression.name) &&
    expression.args.length === 2
  )
    return expression;
  throw new Error(`Invalid CEC cognitive premise; expected one of ${operators.join(', ')}`);
}

function cognitiveApplication(
  operator: string,
  agent: CecExpression,
  body: CecExpression,
): CecApplication {
  return { kind: 'application', name: operator, args: [agent, body] };
}

function atom(name: string): CecExpression {
  return { kind: 'atom', name };
}

function getDisjuncts(expression: CecExpression): CecExpression[] {
  if (!isBinary(expression, 'or')) return [expression];
  return [...getDisjuncts(expression.left), ...getDisjuncts(expression.right)];
}

function buildDisjunction(expressions: CecExpression[]): CecExpression {
  if (expressions.length === 0) return { kind: 'atom', name: 'contradiction' };
  return expressions
    .slice(1)
    .reduce<CecExpression>(
      (left, right) => ({ kind: 'binary', operator: 'or', left, right }),
      expressions[0],
    );
}

function buildConjunction(expressions: CecExpression[]): CecExpression {
  if (expressions.length === 0) return { kind: 'atom', name: 'truth' };
  return expressions
    .slice(1)
    .reduce<CecExpression>(
      (left, right) => ({ kind: 'binary', operator: 'and', left, right }),
      expressions[0],
    );
}

function associateSameOperator(
  expression: CecBinaryExpression,
  operator: Extract<CecBinaryExpression['operator'], 'and' | 'or'>,
): CecExpression {
  const parts = flattenSameOperator(expression, operator);
  if (parts.length < 3) return expression;
  const builder = operator === 'and' ? buildConjunction : buildDisjunction;
  return {
    kind: 'binary',
    operator,
    left: parts[0],
    right: builder(parts.slice(1)),
  };
}

function flattenSameOperator(
  expression: CecExpression,
  operator: Extract<CecBinaryExpression['operator'], 'and' | 'or'>,
): CecExpression[] {
  if (!isBinary(expression, operator)) return [expression];
  return [
    ...flattenSameOperator(expression.left, operator),
    ...flattenSameOperator(expression.right, operator),
  ];
}

function idempotentParts(
  expression: CecBinaryExpression & { operator: 'and' | 'or' },
): CecExpression[] {
  return flattenSameOperator(expression, expression.operator);
}

function isNegationOf(left: CecExpression, right: CecExpression): boolean {
  return isUnary(left, 'not') && cecExpressionEquals(left.expression, right);
}

function findUnaryImplicationPremises(
  operator: Extract<CecUnaryExpression['operator'], 'always' | 'next'>,
  left: CecExpression,
  right: CecExpression,
):
  | {
      fact: CecUnaryExpression;
      implication: CecUnaryExpression & { expression: CecBinaryExpression };
    }
  | undefined {
  const candidates = [
    [left, right],
    [right, left],
  ] as const;
  for (const [fact, implication] of candidates) {
    if (
      isUnary(fact, operator) &&
      isUnary(implication, operator) &&
      isBinary(implication.expression, 'implies') &&
      cecExpressionEquals(fact.expression, implication.expression.left)
    ) {
      return {
        fact,
        implication: implication as CecUnaryExpression & { expression: CecBinaryExpression },
      };
    }
  }
  return undefined;
}

function findEventuallyImplicationPremises(
  eventual: CecExpression,
  alwaysImplication: CecExpression,
):
  | {
      eventual: CecUnaryExpression;
      implication: CecUnaryExpression & { expression: CecBinaryExpression };
    }
  | undefined {
  const candidates = [
    [eventual, alwaysImplication],
    [alwaysImplication, eventual],
  ] as const;
  for (const [eventualCandidate, implicationCandidate] of candidates) {
    if (
      isUnary(eventualCandidate, 'eventually') &&
      isUnary(implicationCandidate, 'always') &&
      isBinary(implicationCandidate.expression, 'implies') &&
      cecExpressionEquals(eventualCandidate.expression, implicationCandidate.expression.left)
    ) {
      return {
        eventual: eventualCandidate,
        implication: implicationCandidate as CecUnaryExpression & {
          expression: CecBinaryExpression;
        },
      };
    }
  }
  return undefined;
}

function findAlwaysInductionPremises(
  left: CecExpression,
  right: CecExpression,
): CecExpression | undefined {
  const candidates = [
    [left, right],
    [right, left],
  ] as const;
  for (const [base, induction] of candidates) {
    if (
      isUnary(induction, 'always') &&
      isBinary(induction.expression, 'implies') &&
      isUnary(induction.expression.right, 'next') &&
      cecExpressionEquals(base, induction.expression.left) &&
      cecExpressionEquals(base, induction.expression.right.expression)
    ) {
      return base;
    }
  }
  return undefined;
}

function findDilemmaPremises(
  expressions: CecExpression[],
  destructive: boolean,
):
  | { first: CecBinaryExpression; second: CecBinaryExpression; disjunction: CecBinaryExpression }
  | undefined {
  const implications = expressions.filter((expression): expression is CecBinaryExpression =>
    isBinary(expression, 'implies'),
  );
  const disjunction = expressions.find((expression): expression is CecBinaryExpression =>
    isBinary(expression, 'or'),
  );
  if (implications.length !== 2 || !disjunction) return undefined;

  const disjuncts = getDisjuncts(disjunction);
  const [first, second] = implications;
  const firstTarget = destructive
    ? { kind: 'unary' as const, operator: 'not' as const, expression: first.right }
    : first.left;
  const secondTarget = destructive
    ? { kind: 'unary' as const, operator: 'not' as const, expression: second.right }
    : second.left;
  const matchesForward =
    hasExpression(disjuncts, firstTarget) && hasExpression(disjuncts, secondTarget);
  if (matchesForward) return { first, second, disjunction };

  const swappedFirstTarget = destructive
    ? { kind: 'unary' as const, operator: 'not' as const, expression: second.right }
    : second.left;
  const swappedSecondTarget = destructive
    ? { kind: 'unary' as const, operator: 'not' as const, expression: first.right }
    : first.left;
  if (
    hasExpression(disjuncts, swappedFirstTarget) &&
    hasExpression(disjuncts, swappedSecondTarget)
  ) {
    return { first: second, second: first, disjunction };
  }
  return undefined;
}

function hasExpression(expressions: CecExpression[], target: CecExpression): boolean {
  return expressions.some((expression) => cecExpressionEquals(expression, target));
}

function findComplementaryDisjunctPair(
  left: CecExpression,
  right: CecExpression,
): { leftIndex: number; rightIndex: number } | undefined {
  if (!isBinary(left, 'or') || !isBinary(right, 'or')) return undefined;
  const leftDisjuncts = getDisjuncts(left);
  const rightDisjuncts = getDisjuncts(right);
  for (let leftIndex = 0; leftIndex < leftDisjuncts.length; leftIndex += 1) {
    for (let rightIndex = 0; rightIndex < rightDisjuncts.length; rightIndex += 1) {
      if (
        isNegationOf(leftDisjuncts[leftIndex], rightDisjuncts[rightIndex]) ||
        isNegationOf(rightDisjuncts[rightIndex], leftDisjuncts[leftIndex])
      ) {
        return { leftIndex, rightIndex };
      }
    }
  }
  return undefined;
}

function uniqueExpressions(expressions: CecExpression[]): CecExpression[] {
  const seen = new Set<string>();
  return expressions.filter((expression) => {
    const key = cecExpressionKey(expression);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function clauseSubsumes(left: CecExpression, right: CecExpression): boolean {
  const leftKeys = getDisjuncts(left).map(cecExpressionKey);
  const rightKeys = getDisjuncts(right).map(cecExpressionKey);
  return leftKeys.length < rightKeys.length && leftKeys.every((key) => rightKeys.includes(key));
}

function matchCecExpressionForVariable(
  pattern: CecExpression,
  target: CecExpression,
  variableName: string,
): string | undefined {
  const bindings = new Map<string, string>();
  return matchCecExpression(pattern, target, variableName, bindings)
    ? bindings.get(variableName)
    : undefined;
}

function matchCecExpression(
  pattern: CecExpression,
  target: CecExpression,
  variableName: string,
  bindings: Map<string, string>,
): boolean {
  if (pattern.kind === 'atom' && pattern.name === variableName) {
    if (target.kind !== 'atom') return false;
    const existing = bindings.get(variableName);
    if (!existing) {
      bindings.set(variableName, target.name);
      return true;
    }
    return existing === target.name;
  }
  if (pattern.kind !== target.kind) return false;
  switch (pattern.kind) {
    case 'atom':
      return target.kind === 'atom' && pattern.name === target.name;
    case 'application':
      return (
        target.kind === 'application' &&
        pattern.name === target.name &&
        pattern.args.length === target.args.length &&
        pattern.args.every((arg, index) =>
          matchCecExpression(arg, target.args[index], variableName, bindings),
        )
      );
    case 'quantified':
      return (
        target.kind === 'quantified' &&
        pattern.quantifier === target.quantifier &&
        matchCecExpression(pattern.expression, target.expression, variableName, bindings)
      );
    case 'unary':
      return (
        target.kind === 'unary' &&
        pattern.operator === target.operator &&
        matchCecExpression(pattern.expression, target.expression, variableName, bindings)
      );
    case 'binary':
      return (
        target.kind === 'binary' &&
        pattern.operator === target.operator &&
        matchCecExpression(pattern.left, target.left, variableName, bindings) &&
        matchCecExpression(pattern.right, target.right, variableName, bindings)
      );
  }
}

function substituteCecAtom(
  expression: CecExpression,
  atomName: string,
  replacementName: string,
): CecExpression {
  switch (expression.kind) {
    case 'atom':
      return expression.name === atomName ? { kind: 'atom', name: replacementName } : expression;
    case 'application':
      return {
        ...expression,
        args: expression.args.map((arg) => substituteCecAtom(arg, atomName, replacementName)),
      } satisfies CecApplication;
    case 'quantified':
      return {
        ...expression,
        expression:
          expression.variable === atomName
            ? expression.expression
            : substituteCecAtom(expression.expression, atomName, replacementName),
      };
    case 'unary':
      return {
        ...expression,
        expression: substituteCecAtom(expression.expression, atomName, replacementName),
      };
    case 'binary':
      return {
        ...expression,
        left: substituteCecAtom(expression.left, atomName, replacementName),
        right: substituteCecAtom(expression.right, atomName, replacementName),
      };
  }
}

function findFirstSubstitutableAtom(expression: CecExpression): string | undefined {
  if (expression.kind === 'application') {
    const atomArg = expression.args.find(
      (arg) => arg.kind === 'atom' && !isVariableLikeAtom(arg.name),
    );
    if (atomArg?.kind === 'atom') return atomArg.name;
  }
  return findFirstNestedAtom(expression, (name) => !isVariableLikeAtom(name));
}

function findFirstVariableLikeAtom(expression: CecExpression): string | undefined {
  return findFirstNestedAtom(expression, isVariableLikeAtom);
}

function findFirstNestedAtom(
  expression: CecExpression,
  predicate: (name: string) => boolean,
): string | undefined {
  switch (expression.kind) {
    case 'atom':
      return predicate(expression.name) ? expression.name : undefined;
    case 'application':
      return expression.args.map((arg) => findFirstNestedAtom(arg, predicate)).find(Boolean);
    case 'quantified':
    case 'unary':
      return findFirstNestedAtom(expression.expression, predicate);
    case 'binary':
      return (
        findFirstNestedAtom(expression.left, predicate) ??
        findFirstNestedAtom(expression.right, predicate)
      );
  }
}

function isVariableLikeAtom(name: string) {
  return /^[xyzuvw]$/.test(name) || /^(agent|person|actor|subject|entity)$/i.test(name);
}
