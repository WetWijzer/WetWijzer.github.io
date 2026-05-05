export const DcecDeonticOperator = {
  OBLIGATION: 'O',
  OBLIGATORY: 'O',
  PERMISSION: 'P',
  PROHIBITION: 'F',
  SUPEREROGATION: 'S',
  RIGHT: 'R',
  LIBERTY: 'L',
  POWER: 'POW',
  IMMUNITY: 'IMM',
} as const;

export const DcecCognitiveOperator = {
  BELIEF: 'B',
  BELIEVES: 'B',
  KNOWLEDGE: 'K',
  KNOWS: 'K',
  INTENTION: 'I',
  DESIRE: 'D',
  GOAL: 'G',
  PERCEPTION: 'P',
} as const;

export const DcecLogicalConnective = {
  AND: 'and',
  OR: 'or',
  NOT: 'not',
  IMPLIES: 'implies',
  BICONDITIONAL: 'iff',
  IFF: 'iff',
  EXISTS: 'exists',
  FORALL: 'forAll',
} as const;

export const DcecTemporalOperator = {
  ALWAYS: 'always',
  EVENTUALLY: 'eventually',
  NEXT: 'next',
  UNTIL: 'until',
  SINCE: 'since',
} as const;

export type DcecDeonticOperatorValue =
  (typeof DcecDeonticOperator)[keyof typeof DcecDeonticOperator];
export type DcecCognitiveOperatorValue =
  (typeof DcecCognitiveOperator)[keyof typeof DcecCognitiveOperator];
export type DcecLogicalConnectiveValue =
  (typeof DcecLogicalConnective)[keyof typeof DcecLogicalConnective];
export type DcecTemporalOperatorValue =
  (typeof DcecTemporalOperator)[keyof typeof DcecTemporalOperator];

export const DCEC_TYPES_METADATA = {
  sourcePythonModule: 'logic/CEC/native/dcec_types.py',
  runtime: 'browser-native-typescript',
  implementation: 'deterministic-dcec-type-descriptors',
  browserNative: true,
  pythonRuntime: false,
  serverRuntime: false,
  filesystem: false,
  subprocess: false,
  rpc: false,
  supportedOperations: [
    'operatorFamily',
    'describeType',
    'validateSymbolContainer',
    'deserializeSymbolContainer',
    'serializeSymbolContainer',
  ],
} as const;

export interface DcecSortJson {
  readonly kind: 'sort';
  readonly name: string;
  readonly parent?: string;
}

export interface DcecVariableJson {
  readonly kind: 'variable';
  readonly name: string;
  readonly sort: string;
}

export interface DcecFunctionSymbolJson {
  readonly kind: 'function';
  readonly name: string;
  readonly argumentSorts: string[];
  readonly returnSort: string;
}

export interface DcecPredicateSymbolJson {
  readonly kind: 'predicate';
  readonly name: string;
  readonly argumentSorts: string[];
}

export type DcecSymbolJson =
  | DcecSortJson
  | DcecVariableJson
  | DcecFunctionSymbolJson
  | DcecPredicateSymbolJson;

export interface DcecSymbolContainerJson {
  readonly sorts: DcecSortJson[];
  readonly variables: DcecVariableJson[];
  readonly functions: DcecFunctionSymbolJson[];
  readonly predicates: DcecPredicateSymbolJson[];
}

export interface DcecSymbolContainerInput {
  readonly sorts?: Iterable<DcecSort>;
  readonly variables?: Iterable<DcecVariable>;
  readonly functions?: Iterable<DcecFunctionSymbol>;
  readonly predicates?: Iterable<DcecPredicateSymbol>;
}

export type DcecOperatorFamily = 'deontic' | 'cognitive' | 'logical' | 'temporal';

export interface DcecNativeTypeDescriptor {
  readonly kind: DcecSymbolJson['kind'] | 'operator';
  readonly name: string;
  readonly parent?: string;
  readonly sort?: string;
  readonly argumentSorts?: string[];
  readonly returnSort?: string;
  readonly arity?: number;
  readonly operatorFamily?: DcecOperatorFamily;
  readonly symbol?: string;
  readonly metadata: typeof DCEC_TYPES_METADATA;
}

export class DcecSort {
  readonly name: string;
  readonly parent?: DcecSort;

  constructor(name: string, parent?: DcecSort) {
    this.name = name;
    this.parent = parent;
  }

  isSubtypeOf(other: DcecSort): boolean {
    if (this.name === other.name) return true;
    return this.parent?.isSubtypeOf(other) ?? false;
  }

  toString(): string {
    return this.name;
  }
}

export class DcecVariable {
  readonly name: string;
  readonly sort: DcecSort;

  constructor(name: string, sort: DcecSort) {
    this.name = name;
    this.sort = sort;
  }

  toString(): string {
    return `${this.name}:${this.sort.name}`;
  }
}

export class DcecFunctionSymbol {
  readonly name: string;
  readonly argumentSorts: DcecSort[];
  readonly returnSort: DcecSort;

  constructor(name: string, argumentSorts: DcecSort[], returnSort: DcecSort) {
    this.name = name;
    this.argumentSorts = [...argumentSorts];
    this.returnSort = returnSort;
  }

  arity(): number {
    return this.argumentSorts.length;
  }

  toString(): string {
    return `${this.name}(${this.argumentSorts.map((sort) => sort.name).join(', ')}) -> ${this.returnSort.name}`;
  }
}

export class DcecPredicateSymbol {
  readonly name: string;
  readonly argumentSorts: DcecSort[];

  constructor(name: string, argumentSorts: DcecSort[]) {
    this.name = name;
    this.argumentSorts = [...argumentSorts];
  }

  arity(): number {
    return this.argumentSorts.length;
  }

  toString(): string {
    return `${this.name}(${this.argumentSorts.map((sort) => sort.name).join(', ')})`;
  }
}

export const isDcecSort = (value: unknown): value is DcecSort => value instanceof DcecSort;
export const isDcecVariable = (value: unknown): value is DcecVariable =>
  value instanceof DcecVariable;
export const isDcecFunctionSymbol = (value: unknown): value is DcecFunctionSymbol =>
  value instanceof DcecFunctionSymbol;
export const isDcecPredicateSymbol = (value: unknown): value is DcecPredicateSymbol =>
  value instanceof DcecPredicateSymbol;

export function isDcecSymbolJson(value: unknown): value is DcecSymbolJson {
  if (!isRecord(value) || typeof value.kind !== 'string' || typeof value.name !== 'string') {
    return false;
  }

  if (value.kind === 'sort') {
    return value.parent === undefined || typeof value.parent === 'string';
  }
  if (value.kind === 'variable') {
    return typeof value.sort === 'string';
  }
  if (value.kind === 'function') {
    return (
      Array.isArray(value.argumentSorts) &&
      value.argumentSorts.every((sort) => typeof sort === 'string') &&
      typeof value.returnSort === 'string'
    );
  }
  if (value.kind === 'predicate') {
    return (
      Array.isArray(value.argumentSorts) &&
      value.argumentSorts.every((sort) => typeof sort === 'string')
    );
  }
  return false;
}

export function getDcecOperatorFamily(value: unknown): DcecOperatorFamily | undefined {
  if (typeof value !== 'string') return undefined;
  if (objectValues(DcecDeonticOperator).some((operator) => operator === value)) return 'deontic';
  if (objectValues(DcecCognitiveOperator).some((operator) => operator === value))
    return 'cognitive';
  if (objectValues(DcecLogicalConnective).some((operator) => operator === value)) return 'logical';
  if (objectValues(DcecTemporalOperator).some((operator) => operator === value)) return 'temporal';
  return undefined;
}

export function describeDcecNativeType(value: unknown): DcecNativeTypeDescriptor | undefined {
  if (value instanceof DcecSort) {
    return {
      kind: 'sort',
      name: value.name,
      parent: value.parent?.name,
      metadata: DCEC_TYPES_METADATA,
    };
  }
  if (value instanceof DcecVariable) {
    return {
      kind: 'variable',
      name: value.name,
      sort: value.sort.name,
      metadata: DCEC_TYPES_METADATA,
    };
  }
  if (value instanceof DcecFunctionSymbol) {
    return {
      kind: 'function',
      name: value.name,
      argumentSorts: value.argumentSorts.map((sort) => sort.name),
      returnSort: value.returnSort.name,
      arity: value.arity(),
      metadata: DCEC_TYPES_METADATA,
    };
  }
  if (value instanceof DcecPredicateSymbol) {
    return {
      kind: 'predicate',
      name: value.name,
      argumentSorts: value.argumentSorts.map((sort) => sort.name),
      arity: value.arity(),
      metadata: DCEC_TYPES_METADATA,
    };
  }

  const operatorFamily = getDcecOperatorFamily(value);
  if (operatorFamily !== undefined) {
    return {
      kind: 'operator',
      name: String(value),
      operatorFamily,
      symbol: String(value),
      metadata: DCEC_TYPES_METADATA,
    };
  }
  return undefined;
}

export function serializeDcecSort(sort: DcecSort): DcecSortJson {
  const json: { kind: 'sort'; name: string; parent?: string } = {
    kind: 'sort',
    name: sort.name,
  };
  if (sort.parent !== undefined) json.parent = sort.parent.name;
  return json;
}

export function serializeDcecVariable(variable: DcecVariable): DcecVariableJson {
  return {
    kind: 'variable',
    name: variable.name,
    sort: variable.sort.name,
  };
}

export function serializeDcecFunctionSymbol(symbol: DcecFunctionSymbol): DcecFunctionSymbolJson {
  return {
    kind: 'function',
    name: symbol.name,
    argumentSorts: symbol.argumentSorts.map((sort) => sort.name),
    returnSort: symbol.returnSort.name,
  };
}

export function serializeDcecPredicateSymbol(symbol: DcecPredicateSymbol): DcecPredicateSymbolJson {
  return {
    kind: 'predicate',
    name: symbol.name,
    argumentSorts: symbol.argumentSorts.map((sort) => sort.name),
  };
}

export function serializeDcecSymbolContainer(
  container: DcecSymbolContainerInput,
): DcecSymbolContainerJson {
  return {
    sorts: [...(container.sorts ?? [])].map(serializeDcecSort),
    variables: [...(container.variables ?? [])].map(serializeDcecVariable),
    functions: [...(container.functions ?? [])].map(serializeDcecFunctionSymbol),
    predicates: [...(container.predicates ?? [])].map(serializeDcecPredicateSymbol),
  };
}

export function validateDcecSymbolContainerJson(value: unknown): {
  readonly ok: boolean;
  readonly errors: string[];
  readonly metadata: typeof DCEC_TYPES_METADATA;
} {
  const errors: string[] = [];
  if (!isRecord(value)) {
    return { ok: false, errors: ['container must be an object'], metadata: DCEC_TYPES_METADATA };
  }

  const keys = ['sorts', 'variables', 'functions', 'predicates'] as const;
  const arrays = Object.fromEntries(
    keys.map((key) => [key, Array.isArray(value[key]) ? value[key] : []]),
  ) as Record<(typeof keys)[number], unknown[]>;
  for (const key of keys) {
    if (!Array.isArray(value[key])) errors.push(`${key} must be an array`);
    for (const entry of arrays[key])
      if (!isDcecSymbolJson(entry)) errors.push(`${key} contains invalid symbol JSON`);
  }

  const sortNames = new Set(arrays.sorts.filter(isSortJson).map((entry) => entry.name));
  const requireSort = (sortName: string, owner: string): void => {
    if (!sortNames.has(sortName)) errors.push(`${owner} references missing sort '${sortName}'`);
  };
  for (const sort of arrays.sorts.filter(isSortJson)) {
    if (sort.parent !== undefined) requireSort(sort.parent, `sort '${sort.name}'`);
  }
  for (const variable of arrays.variables.filter(isVariableJson)) {
    requireSort(variable.sort, `variable '${variable.name}'`);
  }
  for (const func of arrays.functions.filter(isFunctionJson)) {
    for (const sortName of func.argumentSorts) requireSort(sortName, `function '${func.name}'`);
    requireSort(func.returnSort, `function '${func.name}'`);
  }
  for (const predicate of arrays.predicates.filter(isPredicateJson)) {
    for (const sortName of predicate.argumentSorts)
      requireSort(sortName, `predicate '${predicate.name}'`);
  }
  return { ok: errors.length === 0, errors, metadata: DCEC_TYPES_METADATA };
}

export function deserializeDcecSymbolContainer(json: unknown):
  | {
      readonly sorts: DcecSort[];
      readonly variables: DcecVariable[];
      readonly functions: DcecFunctionSymbol[];
      readonly predicates: DcecPredicateSymbol[];
    }
  | undefined {
  if (!validateDcecSymbolContainerJson(json).ok) return undefined;
  const container = json as DcecSymbolContainerJson;
  const sortMap = new Map<string, DcecSort>();
  for (const sort of container.sorts) {
    sortMap.set(sort.name, new DcecSort(sort.name));
  }
  const sorts = container.sorts.map((sort) => {
    const restored = new DcecSort(
      sort.name,
      sort.parent === undefined ? undefined : sortMap.get(sort.parent),
    );
    sortMap.set(sort.name, restored);
    return restored;
  });
  return {
    sorts,
    variables: container.variables.map(
      (variable) => new DcecVariable(variable.name, sortMap.get(variable.sort)!),
    ),
    functions: container.functions.map(
      (func) =>
        new DcecFunctionSymbol(
          func.name,
          func.argumentSorts.map((sortName) => sortMap.get(sortName)!),
          sortMap.get(func.returnSort)!,
        ),
    ),
    predicates: container.predicates.map(
      (predicate) =>
        new DcecPredicateSymbol(
          predicate.name,
          predicate.argumentSorts.map((sortName) => sortMap.get(sortName)!),
        ),
    ),
  };
}

const isSortJson = (entry: unknown): entry is DcecSortJson =>
  isDcecSymbolJson(entry) && entry.kind === 'sort';
const isVariableJson = (entry: unknown): entry is DcecVariableJson =>
  isDcecSymbolJson(entry) && entry.kind === 'variable';
const isFunctionJson = (entry: unknown): entry is DcecFunctionSymbolJson =>
  isDcecSymbolJson(entry) && entry.kind === 'function';
const isPredicateJson = (entry: unknown): entry is DcecPredicateSymbolJson =>
  isDcecSymbolJson(entry) && entry.kind === 'predicate';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function objectValues<T extends Record<string, string>>(value: T): Array<T[keyof T]> {
  return Object.values(value) as Array<T[keyof T]>;
}
