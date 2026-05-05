export type DeonticOperatorType = 'O' | 'P' | 'F' | 'S' | 'R' | 'L' | 'POW' | 'IMM';
export type TemporalOperatorType = '□' | '◊' | 'X' | 'U' | 'S';
export type DeonticConflictTuple = [DeonticFormulaType, DeonticFormulaType, string];

export const DEONTIC_TYPES_PORT_METADATA = {
  sourcePythonModule: 'logic/types/deontic_types.py',
  browserNative: true,
  serverCallsAllowed: false,
  pythonRuntimeAllowed: false,
  runtimeDependencies: [],
} as const;

export const DEONTIC_OPERATORS = {
  OBLIGATION: 'O',
  PERMISSION: 'P',
  PROHIBITION: 'F',
  SUPEREROGATION: 'S',
  RIGHT: 'R',
  LIBERTY: 'L',
  POWER: 'POW',
  IMMUNITY: 'IMM',
} as const satisfies Record<string, DeonticOperatorType>;

export const TEMPORAL_OPERATORS = {
  ALWAYS: '□',
  EVENTUALLY: '◊',
  NEXT: 'X',
  UNTIL: 'U',
  SINCE: 'S',
} as const satisfies Record<string, TemporalOperatorType>;

export class LegalAgentType {
  readonly hash: string;
  constructor(
    readonly identifier: string,
    readonly name: string,
    readonly agentType: string,
    readonly properties: Record<string, unknown> = {},
  ) {
    this.hash = stableShortHash(`${identifier}:${name}:${agentType}`, 8);
  }
  toDict(): Record<string, unknown> {
    return {
      identifier: this.identifier,
      name: this.name,
      agent_type: this.agentType,
      properties: { ...this.properties },
    };
  }
}

export class TemporalConditionType {
  constructor(
    readonly operator: TemporalOperatorType,
    readonly condition: string,
  ) {}
}

export class LegalContextType {
  constructor(
    readonly jurisdiction?: string,
    readonly legalDomain?: string,
    readonly applicableLaw?: string,
    readonly precedents: string[] = [],
    readonly exceptions: string[] = [],
  ) {}
  toDict(): Record<string, unknown> {
    return {
      jurisdiction: this.jurisdiction,
      legal_domain: this.legalDomain,
      applicable_law: this.applicableLaw,
      precedents: [...this.precedents],
      exceptions: [...this.exceptions],
    };
  }
}

export class DeonticFormulaType {
  readonly formulaId: string;
  readonly creationTimestamp: string;
  constructor(
    readonly operator: DeonticOperatorType,
    readonly proposition: string,
    readonly agent?: LegalAgentType,
    readonly beneficiary?: LegalAgentType,
    readonly conditions: string[] = [],
    readonly temporalConditions: TemporalConditionType[] = [],
    readonly legalContext?: LegalContextType,
    readonly confidence = 1.0,
    readonly sourceText = '',
    readonly variables: Record<string, string> = {},
    readonly quantifiers: Array<[string, string, string]> = [],
    formulaId?: string,
    creationTimestamp?: string,
  ) {
    this.formulaId =
      formulaId ??
      stableShortHash(
        `${operator}:${proposition}:${agent?.hash ?? ''}:${conditions.join('|')}`,
        12,
      );
    this.creationTimestamp = creationTimestamp ?? new Date().toISOString();
  }
  get formula(): string {
    return this.toFolString();
  }
  toFolString(): string {
    let prop = this.proposition;
    for (const [quantifier, variable, domain] of this.quantifiers)
      prop = `${quantifier}${variable}:${domain} (${prop})`;
    if (this.conditions.length > 0) prop = `(${this.conditions.join(' ∧ ')}) → (${prop})`;
    for (const temporal of this.temporalConditions) prop = `${temporal.operator}(${prop})`;
    return `${this.operator}${this.agent ? `[${this.agent.identifier}]` : ''}(${prop})`;
  }
  toDict(): Record<string, unknown> {
    return {
      formula_id: this.formulaId,
      operator: this.operator,
      proposition: this.proposition,
      agent: this.agent?.toDict() ?? null,
      beneficiary: this.beneficiary?.toDict() ?? null,
      conditions: [...this.conditions],
      temporal_conditions: this.temporalConditions.map((item) => ({
        operator: item.operator,
        condition: item.condition,
      })),
      legal_context: this.legalContext?.toDict() ?? null,
      confidence: this.confidence,
      source_text: this.sourceText,
      variables: { ...this.variables },
      quantifiers: this.quantifiers.map((item) => [...item]),
      fol_string: this.toFolString(),
      creation_timestamp: this.creationTimestamp,
    };
  }
}

export class DeonticRuleSetType {
  constructor(
    readonly name: string,
    readonly formulas: DeonticFormulaType[],
  ) {}
  addFormula(formula: DeonticFormulaType): void {
    this.formulas.push(formula);
  }
  removeFormula(formulaId: string): boolean {
    const index = this.formulas.findIndex((formula) => formula.formulaId === formulaId);
    if (index < 0) return false;
    this.formulas.splice(index, 1);
    return true;
  }
  findFormulasByAgent(agentIdentifier: string): DeonticFormulaType[] {
    return this.formulas.filter((formula) => formula.agent?.identifier === agentIdentifier);
  }
  findFormulasByOperator(operator: DeonticOperatorType): DeonticFormulaType[] {
    return this.formulas.filter((formula) => formula.operator === operator);
  }
  checkConsistency(): DeonticConflictTuple[] {
    const conflicts: DeonticConflictTuple[] = [];
    for (let index = 0; index < this.formulas.length; index += 1) {
      for (let otherIndex = index + 1; otherIndex < this.formulas.length; otherIndex += 1) {
        const left = this.formulas[index];
        const right = this.formulas[otherIndex];
        if (
          left.proposition !== right.proposition ||
          left.agent?.identifier !== right.agent?.identifier
        )
          continue;
        if (left.operator === 'O' && right.operator === 'F')
          conflicts.push([left, right, 'Direct conflict: obligation vs prohibition']);
        if (left.operator === 'P' && right.operator === 'F')
          conflicts.push([left, right, 'Conflict: permission vs prohibition']);
      }
    }
    return conflicts;
  }
}

export function deonticFormulaFromDict(value: Record<string, unknown>): DeonticFormulaType {
  const agent = isRecord(value.agent)
    ? new LegalAgentType(
        s(value.agent, 'identifier'),
        s(value.agent, 'name'),
        s(value.agent, 'agent_type'),
      )
    : undefined;
  const temporal = Array.isArray(value.temporal_conditions)
    ? value.temporal_conditions
        .filter(isRecord)
        .map(
          (item) =>
            new TemporalConditionType(
              isTemporalOperator(item.operator) ? item.operator : 'X',
              s(item, 'condition'),
            ),
        )
    : [];
  return new DeonticFormulaType(
    isDeonticOperator(value.operator) ? value.operator : 'O',
    s(value, 'proposition'),
    agent,
    undefined,
    strings(value.conditions),
    temporal,
    undefined,
    n(value.confidence, 1),
    s(value, 'source_text'),
    {},
    tuples(value.quantifiers),
    s(value, 'formula_id'),
  );
}

export function validateDeonticTypesPort(value: unknown) {
  const valid =
    isRecord(value) &&
    (!('operator' in value) || isDeonticOperator(value.operator)) &&
    value.server_calls_allowed !== true &&
    value.python_runtime_allowed !== true;
  return {
    valid,
    issues: valid ? [] : [{ severity: 'error', message: 'invalid_deontic_types_port_record' }],
    metadata: DEONTIC_TYPES_PORT_METADATA,
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
function s(value: Record<string, unknown>, key: string): string {
  const field = value[key];
  return typeof field === 'string' ? field : '';
}
function n(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}
function strings(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item) => typeof item === 'string') : [];
}
function tuples(value: unknown): Array<[string, string, string]> {
  return Array.isArray(value)
    ? value
        .filter((item) => Array.isArray(item) && item.length >= 3)
        .map((item) => [String(item[0]), String(item[1]), String(item[2])])
    : [];
}
function isDeonticOperator(value: unknown): value is DeonticOperatorType {
  return (
    typeof value === 'string' &&
    Object.values(DEONTIC_OPERATORS).includes(value as DeonticOperatorType)
  );
}
function isTemporalOperator(value: unknown): value is TemporalOperatorType {
  return (
    typeof value === 'string' &&
    Object.values(TEMPORAL_OPERATORS).includes(value as TemporalOperatorType)
  );
}
function stableShortHash(input: string, length: number): string {
  let hash = 0x811c9dc5;
  for (let index = 0; index < input.length; index += 1)
    hash = Math.imul((hash ^ input.charCodeAt(index)) >>> 0, 0x01000193) >>> 0;
  return hash
    .toString(16)
    .padStart(8, '0')
    .repeat(Math.ceil(length / 8))
    .slice(0, length);
}
