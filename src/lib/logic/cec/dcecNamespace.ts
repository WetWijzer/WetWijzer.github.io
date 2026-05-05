import type { CecExpression } from './ast';
import {
  DcecFunctionSymbol,
  DcecPredicateSymbol,
  DcecSort,
  type DcecSymbolContainerJson,
  DcecVariable,
  isDcecSymbolJson,
  serializeDcecSymbolContainer,
} from './dcecTypes';

const DCEC_BUILTIN_SORT_NAMES = [
  'Entity',
  'Boolean',
  'Moment',
  'Event',
  'Action',
  'Agent',
  'ActionType',
  'Obligation',
  'Permission',
] as const;

export interface DcecNamespaceErrorDetails {
  symbol?: string;
  operation?: string;
  suggestion?: string;
}

export class DcecNamespaceError extends Error {
  readonly symbol?: string;
  readonly operation?: string;
  readonly suggestion?: string;

  constructor(message: string, details: DcecNamespaceErrorDetails = {}) {
    super(message);
    this.name = 'DcecNamespaceError';
    this.symbol = details.symbol;
    this.operation = details.operation;
    this.suggestion = details.suggestion;
  }
}

export interface DcecNamespaceStatistics {
  sorts: number;
  variables: number;
  functions: number;
  predicates: number;
}

export type DcecNamespaceSymbolKind = 'sort' | 'variable' | 'function' | 'predicate';
export interface DcecNamespaceDiagnostic {
  code: string;
  severity: 'error' | 'warning';
  symbol: string;
  kind?: DcecNamespaceSymbolKind;
  operation: string;
  message: string;
  suggestion?: string;
}
export interface DcecNamespaceCollision {
  name: string;
  kinds: DcecNamespaceSymbolKind[];
}
export interface DcecNamespaceSymbolStatistics extends DcecNamespaceStatistics {
  totalSymbols: number;
  builtinSorts: number;
  customSorts: number;
  maxFunctionArity: number;
  maxPredicateArity: number;
  collisions: DcecNamespaceCollision[];
}
export interface DcecNamespaceValidationResult {
  valid: boolean;
  diagnostics: DcecNamespaceDiagnostic[];
}

export interface DcecNamespaceJson extends DcecSymbolContainerJson {
  readonly kind: 'namespace';
  readonly version: 1;
}

export interface DcecStatement<Formula = CecExpression | string> {
  formula: Formula;
  label?: string;
  metadata: Record<string, unknown>;
}

export interface DcecContainerStatistics {
  total_statements: number;
  axioms: number;
  theorems: number;
  labeled_statements: number;
  namespace: DcecNamespaceStatistics;
}

export class DcecNamespace {
  readonly sorts = new Map<string, DcecSort>();
  readonly variables = new Map<string, DcecVariable>();
  readonly functions = new Map<string, DcecFunctionSymbol>();
  readonly predicates = new Map<string, DcecPredicateSymbol>();

  constructor() {
    this.initBuiltinSorts();
  }

  static fromJSON(json: unknown): DcecNamespace {
    if (!isDcecNamespaceJson(json)) {
      throw new DcecNamespaceError('Invalid DCEC namespace JSON snapshot', {
        operation: 'from_json',
        suggestion: 'Provide a namespace snapshot produced by DcecNamespace.toJSON().',
      });
    }

    const namespace = new DcecNamespace();
    namespace.loadSorts(json.sorts);
    for (const variable of json.variables) {
      namespace.addVariable(variable.name, variable.sort);
    }
    for (const func of json.functions) {
      namespace.addFunction(func.name, func.argumentSorts, func.returnSort);
    }
    for (const predicate of json.predicates) {
      namespace.addPredicate(predicate.name, predicate.argumentSorts);
    }
    return namespace;
  }

  addSort(name: string, parent?: string): DcecSort {
    if (this.sorts.has(name)) {
      throw new DcecNamespaceError(`Duplicate sort name '${name}'`, {
        symbol: name,
        operation: 'add_sort',
        suggestion: `Use a different name or remove the existing sort '${name}' first`,
      });
    }
    this.ensureNoCrossKindCollision(name, 'sort', 'add_sort');

    const parentSort = parent === undefined ? undefined : this.sorts.get(parent);
    if (parent !== undefined && parentSort === undefined) {
      throw this.missingSortError(parent, 'lookup', `Parent sort '${parent}' does not exist`);
    }

    const sort = new DcecSort(name, parentSort);
    this.sorts.set(name, sort);
    return sort;
  }

  getSort(name: string): DcecSort | undefined {
    return this.sorts.get(name);
  }

  registerSort(name: string, parent?: string): DcecSort {
    return this.addSort(name, parent);
  }

  addVariable(name: string, sortName: string): DcecVariable {
    if (this.variables.has(name)) {
      throw new DcecNamespaceError(`Duplicate variable name '${name}'`, {
        symbol: name,
        operation: 'add_variable',
        suggestion: `Use a different variable name or remove the existing variable '${name}' first`,
      });
    }
    this.ensureNoCrossKindCollision(name, 'variable', 'add_variable');

    const sort = this.requireSort(
      sortName,
      'lookup',
      `Sort '${sortName}' does not exist for variable`,
    );
    const variable = new DcecVariable(name, sort);
    this.variables.set(name, variable);
    return variable;
  }

  getVariable(name: string): DcecVariable | undefined {
    return this.variables.get(name);
  }

  registerVariable(name: string, sortName: string): DcecVariable {
    return this.addVariable(name, sortName);
  }

  addFunction(
    name: string,
    argumentSortNames: string[],
    returnSortName: string,
  ): DcecFunctionSymbol {
    if (this.functions.has(name)) {
      throw new DcecNamespaceError(`Duplicate function name '${name}'`, {
        symbol: name,
        operation: 'add_function',
        suggestion: `Use a different function name or remove the existing function '${name}' first`,
      });
    }
    this.ensureNoCrossKindCollision(name, 'function', 'add_function');

    const argumentSorts = argumentSortNames.map((sortName) =>
      this.requireSort(
        sortName,
        'lookup',
        `Sort '${sortName}' does not exist for function argument`,
      ),
    );
    const returnSort = this.requireSort(
      returnSortName,
      'lookup',
      `Return sort '${returnSortName}' does not exist`,
    );
    const func = new DcecFunctionSymbol(name, argumentSorts, returnSort);
    this.functions.set(name, func);
    return func;
  }

  getFunction(name: string): DcecFunctionSymbol | undefined {
    return this.functions.get(name);
  }

  registerFunction(
    name: string,
    argumentSortNames: string[],
    returnSortName: string,
  ): DcecFunctionSymbol {
    return this.addFunction(name, argumentSortNames, returnSortName);
  }

  addPredicate(name: string, argumentSortNames: string[]): DcecPredicateSymbol {
    if (this.predicates.has(name)) {
      throw new DcecNamespaceError(`Duplicate predicate name '${name}'`, {
        symbol: name,
        operation: 'add_predicate',
        suggestion: `Use a different predicate name or remove the existing predicate '${name}' first`,
      });
    }
    this.ensureNoCrossKindCollision(name, 'predicate', 'add_predicate');

    const argumentSorts = argumentSortNames.map((sortName) =>
      this.requireSort(
        sortName,
        'lookup',
        `Sort '${sortName}' does not exist for predicate argument`,
      ),
    );
    const predicate = new DcecPredicateSymbol(name, argumentSorts);
    this.predicates.set(name, predicate);
    return predicate;
  }

  getPredicate(name: string, arity?: number): DcecPredicateSymbol | undefined {
    const predicate = this.predicates.get(name);
    if (predicate !== undefined || arity === undefined) return predicate;
    return this.addPredicate(name, []);
  }

  registerPredicate(name: string, argumentSortNames: string[]): DcecPredicateSymbol {
    return this.addPredicate(name, argumentSortNames);
  }

  getStatistics(): DcecNamespaceStatistics {
    return {
      sorts: this.sorts.size,
      variables: this.variables.size,
      functions: this.functions.size,
      predicates: this.predicates.size,
    };
  }

  getSymbolStatistics(): DcecNamespaceSymbolStatistics {
    const base = this.getStatistics();
    const functionArities = [...this.functions.values()].map((func) => func.arity());
    const predicateArities = [...this.predicates.values()].map((predicate) => predicate.arity());
    return {
      ...base,
      totalSymbols: base.sorts + base.variables + base.functions + base.predicates,
      builtinSorts: [...this.sorts.keys()].filter((name) =>
        DCEC_BUILTIN_SORT_NAMES.includes(name as (typeof DCEC_BUILTIN_SORT_NAMES)[number]),
      ).length,
      customSorts: [...this.sorts.keys()].filter(
        (name) =>
          !DCEC_BUILTIN_SORT_NAMES.includes(name as (typeof DCEC_BUILTIN_SORT_NAMES)[number]),
      ).length,
      maxFunctionArity: functionArities.length === 0 ? 0 : Math.max(...functionArities),
      maxPredicateArity: predicateArities.length === 0 ? 0 : Math.max(...predicateArities),
      collisions: this.findCollisions(),
    };
  }

  toJSON(): DcecNamespaceJson {
    return {
      kind: 'namespace',
      version: 1,
      ...serializeDcecSymbolContainer({
        sorts: this.sorts.values(),
        variables: this.variables.values(),
        functions: this.functions.values(),
        predicates: this.predicates.values(),
      }),
    };
  }

  validate(): DcecNamespaceValidationResult {
    const diagnostics: DcecNamespaceDiagnostic[] = this.findCollisions().map((collision) => ({
      code: 'symbol_collision',
      severity: 'error',
      symbol: collision.name,
      operation: 'validate',
      message: `Symbol '${collision.name}' is registered as multiple DCEC namespace kinds: ${collision.kinds.join(', ')}`,
      suggestion: 'Use unique names across sorts, variables, functions, and predicates.',
    }));

    for (const variable of this.variables.values()) {
      this.addSortReferenceDiagnostic(diagnostics, variable.name, 'variable', variable.sort);
    }
    for (const func of this.functions.values()) {
      this.addSortReferenceDiagnostic(diagnostics, func.name, 'function', func.returnSort);
      for (const sort of func.argumentSorts)
        this.addSortReferenceDiagnostic(diagnostics, func.name, 'function', sort);
    }
    for (const predicate of this.predicates.values()) {
      for (const sort of predicate.argumentSorts)
        this.addSortReferenceDiagnostic(diagnostics, predicate.name, 'predicate', sort);
    }

    return {
      valid: diagnostics.every((diagnostic) => diagnostic.severity !== 'error'),
      diagnostics,
    };
  }

  toString(): string {
    const stats = this.getStatistics();
    return `DCECNamespace(sorts=${stats.sorts}, vars=${stats.variables}, funcs=${stats.functions}, preds=${stats.predicates})`;
  }

  private initBuiltinSorts() {
    this.addSort('Entity');
    this.addSort('Boolean');
    this.addSort('Moment');
    this.addSort('Event');
    this.addSort('Action');
    this.addSort('Agent', 'Entity');
    this.addSort('ActionType');
    this.addSort('Obligation', 'Boolean');
    this.addSort('Permission', 'Boolean');
  }

  private loadSorts(sorts: DcecNamespaceJson['sorts']) {
    const pending = sorts.filter((sort) => !this.isMatchingBuiltinSort(sort.name, sort.parent));
    while (pending.length > 0) {
      const before = pending.length;
      for (let index = pending.length - 1; index >= 0; index -= 1) {
        const sort = pending[index];
        if (sort.parent !== undefined && !this.sorts.has(sort.parent)) continue;
        this.addSort(sort.name, sort.parent);
        pending.splice(index, 1);
      }
      if (pending.length === before) {
        const unresolved = pending.map((sort) => sort.name).join(', ');
        throw new DcecNamespaceError(
          `Unable to resolve namespace sort parents for: ${unresolved}`,
          {
            operation: 'from_json',
            suggestion: 'Order custom sorts after their parents or include all parent sorts.',
          },
        );
      }
    }
  }

  private isMatchingBuiltinSort(name: string, parent?: string): boolean {
    const existing = this.sorts.get(name);
    if (existing === undefined) return false;
    const existingParent = existing.parent?.name;
    if (existingParent === parent) return true;
    throw new DcecNamespaceError(`Builtin sort '${name}' has incompatible parent`, {
      symbol: name,
      operation: 'from_json',
      suggestion: `Use the browser-native builtin sort definition for '${name}'.`,
    });
  }

  private requireSort(name: string, operation: string, message: string): DcecSort {
    const sort = this.sorts.get(name);
    if (sort === undefined) throw this.missingSortError(name, operation, message);
    return sort;
  }

  private missingSortError(name: string, operation: string, message: string): DcecNamespaceError {
    return new DcecNamespaceError(message, {
      symbol: name,
      operation,
      suggestion: `Register sort '${name}' first, or use an existing sort: ${[...this.sorts.keys()].join(', ')}`,
    });
  }

  private ensureNoCrossKindCollision(
    name: string,
    kind: DcecNamespaceSymbolKind,
    operation: string,
  ) {
    const existingKinds = this.kindsForName(name).filter((existingKind) => existingKind !== kind);
    if (existingKinds.length === 0) return;
    throw new DcecNamespaceError(`Symbol '${name}' already exists as ${existingKinds.join(', ')}`, {
      symbol: name,
      operation,
      suggestion: 'Use a unique DCEC namespace symbol name across all symbol kinds.',
    });
  }

  private kindsForName(name: string): DcecNamespaceSymbolKind[] {
    const kinds: DcecNamespaceSymbolKind[] = [];
    if (this.sorts.has(name)) kinds.push('sort');
    if (this.variables.has(name)) kinds.push('variable');
    if (this.functions.has(name)) kinds.push('function');
    if (this.predicates.has(name)) kinds.push('predicate');
    return kinds;
  }

  private findCollisions(): DcecNamespaceCollision[] {
    const names = new Set<string>([
      ...this.sorts.keys(),
      ...this.variables.keys(),
      ...this.functions.keys(),
      ...this.predicates.keys(),
    ]);
    return [...names]
      .map((name) => ({ name, kinds: this.kindsForName(name) }))
      .filter((collision) => collision.kinds.length > 1);
  }

  private addSortReferenceDiagnostic(
    diagnostics: DcecNamespaceDiagnostic[],
    symbol: string,
    kind: DcecNamespaceSymbolKind,
    sort: DcecSort,
  ) {
    if (this.sorts.get(sort.name) === sort) return;
    diagnostics.push({
      code: 'missing_sort_reference',
      severity: 'error',
      symbol,
      kind,
      operation: 'validate',
      message: `${kind} '${symbol}' references unregistered sort '${sort.name}'`,
      suggestion: `Register sort '${sort.name}' before registering '${symbol}'.`,
    });
  }
}

export function isDcecNamespaceJson(value: unknown): value is DcecNamespaceJson {
  if (!isRecord(value) || value.kind !== 'namespace' || value.version !== 1) return false;
  return (
    Array.isArray(value.sorts) &&
    Array.isArray(value.variables) &&
    Array.isArray(value.functions) &&
    Array.isArray(value.predicates) &&
    value.sorts.every(isDcecSymbolJson) &&
    value.variables.every(isDcecSymbolJson) &&
    value.functions.every(isDcecSymbolJson) &&
    value.predicates.every(isDcecSymbolJson) &&
    value.sorts.every((symbol) => symbol.kind === 'sort') &&
    value.variables.every((symbol) => symbol.kind === 'variable') &&
    value.functions.every((symbol) => symbol.kind === 'function') &&
    value.predicates.every((symbol) => symbol.kind === 'predicate')
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

export class DcecContainer<Formula = CecExpression | string> {
  readonly namespace: DcecNamespace;
  private readonly statements: DcecStatement<Formula>[] = [];
  private readonly statementLabels = new Map<string, DcecStatement<Formula>>();
  private readonly axioms: DcecStatement<Formula>[] = [];
  private readonly theorems: DcecStatement<Formula>[] = [];

  constructor(namespace = new DcecNamespace()) {
    this.namespace = namespace;
  }

  addStatement(
    formula: Formula,
    options: { label?: string; isAxiom?: boolean; metadata?: Record<string, unknown> } = {},
  ): DcecStatement<Formula> {
    if (options.label !== undefined && this.statementLabels.has(options.label)) {
      throw new DcecNamespaceError(`Duplicate statement label '${options.label}'`, {
        symbol: options.label,
        operation: 'add_statement',
        suggestion: `Use a different label or remove the existing statement with label '${options.label}' first`,
      });
    }

    const statement: DcecStatement<Formula> = {
      formula,
      label: options.label,
      metadata: options.metadata ?? {},
    };
    this.statements.push(statement);
    if (options.label !== undefined) this.statementLabels.set(options.label, statement);
    if (options.isAxiom) this.axioms.push(statement);
    return statement;
  }

  addAxiom(
    formula: Formula,
    label?: string,
    metadata?: Record<string, unknown>,
  ): DcecStatement<Formula> {
    return this.addStatement(formula, { label, isAxiom: true, metadata });
  }

  addTheorem(formula: Formula, label?: string): DcecStatement<Formula> {
    const statement = this.addStatement(formula, { label, isAxiom: false });
    this.theorems.push(statement);
    return statement;
  }

  getStatement(label: string): DcecStatement<Formula> | undefined {
    return this.statementLabels.get(label);
  }

  getAllStatements(): DcecStatement<Formula>[] {
    return [...this.statements];
  }

  getAxioms(): DcecStatement<Formula>[] {
    return [...this.axioms];
  }

  getTheorems(): DcecStatement<Formula>[] {
    return [...this.theorems];
  }

  clear() {
    this.statements.length = 0;
    this.statementLabels.clear();
    this.axioms.length = 0;
    this.theorems.length = 0;
  }

  getStatistics(): DcecContainerStatistics {
    return {
      total_statements: this.statements.length,
      axioms: this.axioms.length,
      theorems: this.theorems.length,
      labeled_statements: this.statementLabels.size,
      namespace: this.namespace.getStatistics(),
    };
  }

  toString(): string {
    const stats = this.getStatistics();
    return `DCECContainer(statements=${stats.total_statements}, axioms=${stats.axioms}, theorems=${stats.theorems})`;
  }
}
