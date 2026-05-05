import {
  DcecAtomicFormula,
  DcecCognitiveFormula,
  DcecConnectiveFormula,
  DcecDeonticFormula,
  DcecFormula,
  DcecTemporalFormula,
  DcecVariableTerm,
} from './dcecCore';
import {
  DcecCognitiveOperator,
  DcecDeonticOperator,
  DcecLogicalConnective,
  DcecSort,
  DcecVariable,
} from './dcecTypes';

export interface DcecAdvancedInferenceRule {
  name(): string;
  canApply(formulas: DcecFormula[]): boolean;
  apply(formulas: DcecFormula[]): DcecFormula[];
}

export type DcecAdvancedRuleGroup = 'modal' | 'temporal' | 'deontic' | 'cognitive' | 'combined';

export interface DcecAdvancedInferenceRuleDescriptor {
  readonly id: string;
  readonly pythonName: string;
  readonly group: DcecAdvancedRuleGroup;
  readonly sourcePythonModule: 'logic/CEC/native/advanced_inference.py';
  readonly rule: DcecAdvancedInferenceRule;
}

export interface DcecFormulaClassification {
  readonly cognitive: boolean;
  readonly modal: boolean;
  readonly temporal: boolean;
  readonly deontic: boolean;
}

export interface DcecAdvancedInferenceOptions {
  readonly maxRounds?: number;
  readonly maxDerivedFormulas?: number;
}

export interface DcecAdvancedInferenceStep {
  readonly stepId: number;
  readonly ruleId: string;
  readonly ruleName: string;
  readonly pythonName: string;
  readonly group: DcecAdvancedRuleGroup;
  readonly sourcePythonModule: 'logic/CEC/native/advanced_inference.py';
  readonly premiseIndexes: number[];
  readonly conclusions: DcecFormula[];
  readonly status: 'SUCCESS';
  readonly browserNative: true;
  readonly pythonRuntime: false;
}

export interface DcecAdvancedInferenceResult {
  readonly assumptions: DcecFormula[];
  readonly derived: DcecFormula[];
  readonly closure: DcecFormula[];
  readonly steps: DcecAdvancedInferenceStep[];
  readonly saturated: boolean;
}

export class DcecModalKAxiom implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Modal K Axiom';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some((formula) => isKnowledgeImplication(formula));
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas.flatMap((formula) => {
      if (!isKnowledgeImplication(formula)) return [];
      const implication = formula.formula;
      const [antecedent, consequent] = implication.formulas;
      return [
        new DcecConnectiveFormula(DcecLogicalConnective.IMPLIES, [
          new DcecCognitiveFormula(DcecCognitiveOperator.KNOWLEDGE, formula.agent, antecedent),
          new DcecCognitiveFormula(DcecCognitiveOperator.KNOWLEDGE, formula.agent, consequent),
        ]),
      ];
    });
  }
}

export class DcecModalTAxiom implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Modal T Axiom';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some(isKnowledgeFormula);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas.flatMap((formula) => (isKnowledgeFormula(formula) ? [formula.formula] : []));
  }
}

export class DcecModalS4Axiom implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Modal S4 Axiom';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some(isKnowledgeFormula);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas.flatMap((formula) =>
      isKnowledgeFormula(formula)
        ? [new DcecCognitiveFormula(DcecCognitiveOperator.KNOWLEDGE, formula.agent, formula)]
        : [],
    );
  }
}

export class DcecModalNecessitation implements DcecAdvancedInferenceRule {
  private readonly systemAgent = new DcecVariableTerm(
    new DcecVariable('system', new DcecSort('System')),
  );

  name(): string {
    return 'Necessitation';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some((formula) => !(formula instanceof DcecCognitiveFormula));
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas
      .filter((formula) => !(formula instanceof DcecCognitiveFormula))
      .slice(0, 5)
      .map(
        (formula) =>
          new DcecCognitiveFormula(DcecCognitiveOperator.KNOWLEDGE, this.systemAgent, formula),
      );
  }
}

export class DcecTemporalInduction implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Temporal Induction';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.length >= 2 && formulas.some(isImplicationFormula);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    const results: DcecFormula[] = [];
    for (const candidate of formulas) {
      for (const implication of formulas) {
        if (!isImplicationFormula(implication)) continue;
        const [antecedent, consequent] = implication.formulas;
        if (candidate.toString() === antecedent.toString()) results.push(consequent);
      }
    }
    return results.slice(0, 3);
  }
}

export class DcecFrameAxiom implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Frame Axiom';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some((formula) => formula instanceof DcecAtomicFormula);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas
      .filter((formula): formula is DcecAtomicFormula => formula instanceof DcecAtomicFormula)
      .slice(0, 5);
  }
}

export class DcecDeonticDRule implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Deontic D Axiom';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some(isObligationFormula);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas.flatMap((formula) => {
      if (!isObligationFormula(formula)) return [];
      const negatedInner = new DcecConnectiveFormula(DcecLogicalConnective.NOT, [formula.formula]);
      const obligationOfNegation = new DcecDeonticFormula(
        DcecDeonticOperator.OBLIGATION,
        negatedInner,
        formula.agent,
      );
      return [new DcecConnectiveFormula(DcecLogicalConnective.NOT, [obligationOfNegation])];
    });
  }
}

export class DcecDeonticPermissionObligation implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Permission-Obligation Duality';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some(
      (formula) =>
        formula instanceof DcecDeonticFormula &&
        (formula.operator === DcecDeonticOperator.PERMISSION ||
          formula.operator === DcecDeonticOperator.OBLIGATION),
    );
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas.flatMap((formula) => {
      if (!(formula instanceof DcecDeonticFormula)) return [];
      const negatedInner = new DcecConnectiveFormula(DcecLogicalConnective.NOT, [formula.formula]);
      if (formula.operator === DcecDeonticOperator.PERMISSION) {
        const obligationOfNegation = new DcecDeonticFormula(
          DcecDeonticOperator.OBLIGATION,
          negatedInner,
          formula.agent,
        );
        return [new DcecConnectiveFormula(DcecLogicalConnective.NOT, [obligationOfNegation])];
      }
      if (formula.operator === DcecDeonticOperator.OBLIGATION) {
        const permissionOfNegation = new DcecDeonticFormula(
          DcecDeonticOperator.PERMISSION,
          negatedInner,
          formula.agent,
        );
        return [new DcecConnectiveFormula(DcecLogicalConnective.NOT, [permissionOfNegation])];
      }
      return [];
    });
  }
}

export class DcecDeonticDistribution implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Deontic Distribution';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some(isObligationConjunction);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas.flatMap((formula) => {
      if (!isObligationConjunction(formula)) return [];
      const obligations = formula.formula.formulas.map(
        (conjunct) => new DcecDeonticFormula(formula.operator, conjunct, formula.agent),
      );
      return obligations.length >= 2
        ? [new DcecConnectiveFormula(DcecLogicalConnective.AND, obligations)]
        : [];
    });
  }
}

export class DcecKnowledgeObligation implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Knowledge-Obligation Interaction';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some(isKnowledgeOfDeonticFormula);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas.flatMap((formula) => {
      if (!isKnowledgeOfDeonticFormula(formula)) return [];
      const deontic = formula.formula;
      const knownContent = new DcecCognitiveFormula(
        DcecCognitiveOperator.KNOWLEDGE,
        formula.agent,
        deontic.formula,
      );
      return [new DcecDeonticFormula(deontic.operator, knownContent, deontic.agent)];
    });
  }
}

export class DcecTemporalObligation implements DcecAdvancedInferenceRule {
  name(): string {
    return 'Temporal-Deontic Interaction';
  }

  canApply(formulas: DcecFormula[]): boolean {
    return formulas.some((formula) => formula instanceof DcecDeonticFormula);
  }

  apply(formulas: DcecFormula[]): DcecFormula[] {
    return formulas
      .filter((formula): formula is DcecDeonticFormula => formula instanceof DcecDeonticFormula)
      .slice(0, 3);
  }
}

export function getAllDcecAdvancedRules(): DcecAdvancedInferenceRule[] {
  return getDcecAdvancedInferenceRegistry().map((entry) => entry.rule);
}

export function getDcecAdvancedInferenceRegistry(): DcecAdvancedInferenceRuleDescriptor[] {
  return [
    {
      id: 'modal_k_axiom',
      pythonName: 'ModalKAxiom',
      group: 'modal',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecModalKAxiom(),
    },
    {
      id: 'modal_t_axiom',
      pythonName: 'ModalTAxiom',
      group: 'modal',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecModalTAxiom(),
    },
    {
      id: 'modal_s4_axiom',
      pythonName: 'ModalS4Axiom',
      group: 'modal',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecModalS4Axiom(),
    },
    {
      id: 'modal_necessitation',
      pythonName: 'Necessitation',
      group: 'modal',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecModalNecessitation(),
    },
    {
      id: 'temporal_induction',
      pythonName: 'TemporalInduction',
      group: 'temporal',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecTemporalInduction(),
    },
    {
      id: 'frame_axiom',
      pythonName: 'FrameAxiom',
      group: 'temporal',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecFrameAxiom(),
    },
    {
      id: 'deontic_d_axiom',
      pythonName: 'DeonticDRule',
      group: 'deontic',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecDeonticDRule(),
    },
    {
      id: 'permission_obligation_duality',
      pythonName: 'DeonticPermissionObligation',
      group: 'deontic',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecDeonticPermissionObligation(),
    },
    {
      id: 'deontic_distribution',
      pythonName: 'DeonticDistribution',
      group: 'deontic',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecDeonticDistribution(),
    },
    {
      id: 'knowledge_obligation_interaction',
      pythonName: 'KnowledgeObligation',
      group: 'cognitive',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecKnowledgeObligation(),
    },
    {
      id: 'temporal_deontic_interaction',
      pythonName: 'TemporalObligation',
      group: 'combined',
      sourcePythonModule: 'logic/CEC/native/advanced_inference.py',
      rule: new DcecTemporalObligation(),
    },
  ];
}

export function getDcecModalRules(): DcecAdvancedInferenceRule[] {
  return getDcecAdvancedRulesByGroup('modal');
}

export function getDcecTemporalRules(): DcecAdvancedInferenceRule[] {
  return getDcecAdvancedRulesByGroup('temporal');
}

export function getDcecDeonticRules(): DcecAdvancedInferenceRule[] {
  return getDcecAdvancedRulesByGroup('deontic');
}

export function getDcecCombinedRules(): DcecAdvancedInferenceRule[] {
  return getDcecAdvancedInferenceRegistry()
    .filter((entry) => entry.group === 'cognitive' || entry.group === 'combined')
    .map((entry) => entry.rule);
}

export function getDcecAdvancedRulesByGroup(
  group: DcecAdvancedRuleGroup,
): DcecAdvancedInferenceRule[] {
  return getDcecAdvancedInferenceRegistry()
    .filter((entry) => entry.group === group)
    .map((entry) => entry.rule);
}

export function classifyDcecAdvancedFormula(formula: DcecFormula): DcecFormulaClassification {
  const nested = getNestedFormulaClassifications(formula);
  const cognitive =
    formula instanceof DcecCognitiveFormula || nested.some((entry) => entry.cognitive);
  const deontic = formula instanceof DcecDeonticFormula || nested.some((entry) => entry.deontic);
  const temporal = formula instanceof DcecTemporalFormula || nested.some((entry) => entry.temporal);
  return {
    cognitive,
    modal: cognitive,
    temporal,
    deontic,
  };
}

export function classifyDcecAdvancedFormulas(formulas: DcecFormula[]): DcecFormulaClassification {
  const classifications = formulas.map(classifyDcecAdvancedFormula);
  return {
    cognitive: classifications.some((entry) => entry.cognitive),
    modal: classifications.some((entry) => entry.modal),
    temporal: classifications.some((entry) => entry.temporal),
    deontic: classifications.some((entry) => entry.deontic),
  };
}

export function selectDcecAdvancedInferenceRules(
  formulas: DcecFormula[],
): DcecAdvancedInferenceRuleDescriptor[] {
  const classification = classifyDcecAdvancedFormulas(formulas);
  const selectedGroups = new Set<DcecAdvancedRuleGroup>();
  if (classification.modal) selectedGroups.add('modal');
  if (classification.temporal) selectedGroups.add('temporal');
  if (classification.deontic) selectedGroups.add('deontic');
  if (classification.cognitive) selectedGroups.add('cognitive');
  if (
    (classification.cognitive && classification.deontic) ||
    (classification.temporal && classification.deontic)
  ) {
    selectedGroups.add('combined');
  }
  return getDcecAdvancedInferenceRegistry().filter(
    (entry) => selectedGroups.has(entry.group) && entry.rule.canApply(formulas),
  );
}

export function deriveDcecAdvancedInferences(
  assumptions: DcecFormula[],
  options: DcecAdvancedInferenceOptions = {},
): DcecAdvancedInferenceResult {
  const maxRounds = options.maxRounds ?? 2;
  const maxDerivedFormulas = options.maxDerivedFormulas ?? 25;
  const closure = [...assumptions];
  const derived: DcecFormula[] = [];
  const steps: DcecAdvancedInferenceStep[] = [];
  const seen = new Set(closure.map((formula) => formula.toString()));
  let saturated = true;

  for (let round = 0; round < maxRounds; round += 1) {
    let roundChanged = false;
    for (const descriptor of selectDcecAdvancedInferenceRules(closure)) {
      const conclusions = descriptor.rule
        .apply(closure)
        .filter((formula) => !seen.has(formula.toString()));
      if (conclusions.length === 0) continue;

      const accepted: DcecFormula[] = [];
      for (const conclusion of conclusions) {
        if (seen.has(conclusion.toString())) continue;
        if (derived.length + accepted.length >= maxDerivedFormulas) {
          saturated = false;
          break;
        }
        seen.add(conclusion.toString());
        accepted.push(conclusion);
      }
      if (accepted.length === 0) break;

      const premiseIndexes = closure
        .map((formula, index) => (descriptor.rule.canApply([formula]) ? index : -1))
        .filter((index) => index >= 0);
      closure.push(...accepted);
      derived.push(...accepted);
      steps.push({
        stepId: steps.length + 1,
        ruleId: descriptor.id,
        ruleName: descriptor.rule.name(),
        pythonName: descriptor.pythonName,
        group: descriptor.group,
        sourcePythonModule: descriptor.sourcePythonModule,
        premiseIndexes,
        conclusions: accepted,
        status: 'SUCCESS',
        browserNative: true,
        pythonRuntime: false,
      });
      roundChanged = true;
      if (derived.length >= maxDerivedFormulas) {
        saturated = false;
        break;
      }
    }
    if (!roundChanged || derived.length >= maxDerivedFormulas) break;
  }

  return {
    assumptions: [...assumptions],
    derived,
    closure,
    steps,
    saturated,
  };
}

function getNestedFormulaClassifications(formula: DcecFormula): DcecFormulaClassification[] {
  if (
    formula instanceof DcecCognitiveFormula ||
    formula instanceof DcecDeonticFormula ||
    formula instanceof DcecTemporalFormula
  ) {
    return [classifyDcecAdvancedFormula(formula.formula)];
  }
  if (formula instanceof DcecConnectiveFormula) {
    return formula.formulas.map(classifyDcecAdvancedFormula);
  }
  return [];
}

function isKnowledgeFormula(formula: DcecFormula): formula is DcecCognitiveFormula {
  return (
    formula instanceof DcecCognitiveFormula && formula.operator === DcecCognitiveOperator.KNOWLEDGE
  );
}

function isImplicationFormula(formula: DcecFormula): formula is DcecConnectiveFormula {
  return (
    formula instanceof DcecConnectiveFormula && formula.connective === DcecLogicalConnective.IMPLIES
  );
}

function isKnowledgeImplication(
  formula: DcecFormula,
): formula is DcecCognitiveFormula & { formula: DcecConnectiveFormula } {
  return isKnowledgeFormula(formula) && isImplicationFormula(formula.formula);
}

function isObligationFormula(formula: DcecFormula): formula is DcecDeonticFormula {
  return (
    formula instanceof DcecDeonticFormula && formula.operator === DcecDeonticOperator.OBLIGATION
  );
}

function isObligationConjunction(
  formula: DcecFormula,
): formula is DcecDeonticFormula & { formula: DcecConnectiveFormula } {
  return (
    isObligationFormula(formula) &&
    formula.formula instanceof DcecConnectiveFormula &&
    formula.formula.connective === DcecLogicalConnective.AND
  );
}

function isKnowledgeOfDeonticFormula(
  formula: DcecFormula,
): formula is DcecCognitiveFormula & { formula: DcecDeonticFormula } {
  return isKnowledgeFormula(formula) && formula.formula instanceof DcecDeonticFormula;
}
