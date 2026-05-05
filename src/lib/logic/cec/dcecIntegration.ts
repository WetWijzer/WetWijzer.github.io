import { LogicParseError } from '../errors';
import {
  DcecAtomicFormula,
  DcecCognitiveFormula,
  DcecConnectiveFormula,
  DcecDeonticFormula,
  DcecFormula,
  DcecFunctionTerm,
  DcecTemporalFormula,
  DcecTerm,
  DcecVariableTerm,
} from './dcecCore';
import {
  checkDcecParens,
  consolidateDcecParens,
  functorizeDcecSymbols,
  removeDcecSemicolonComments,
  stripDcecComments,
  stripDcecWhitespace,
  tuckDcecFunctions,
} from './dcecCleaning';
import type { DcecNamespace } from './dcecNamespace';
import {
  DcecParseArg,
  DcecParseToken,
  isDcecParseToken,
  prefixDcecEmdas,
  prefixDcecLogicalFunctions,
  replaceDcecSynonyms,
} from './dcecParsing';
import {
  DcecCognitiveOperator,
  DcecDeonticOperator,
  DcecFunctionSymbol,
  DcecLogicalConnective,
  DcecPredicateSymbol,
  DcecSort,
  DcecTemporalOperator,
  DcecVariable,
} from './dcecTypes';

export interface ParseDcecStringOptions {
  namespace?: DcecNamespace;
}

export const DCEC_INTEGRATION_METADATA = {
  sourcePythonModule: 'logic/CEC/native/dcec_integration.py',
  runtime: 'browser-native-typescript',
  browserNative: true,
  pythonRuntime: false,
  serverRuntime: false,
  supportedConversions: [
    'string-to-token',
    'token-to-formula',
    'formula-to-token',
    'round-trip-validation',
  ],
} as const;

export interface DcecTokenConversionResult {
  readonly ok: boolean;
  readonly token?: DcecParseToken;
  readonly formula?: DcecFormula;
  readonly canonicalSExpression?: string;
  readonly canonicalFormula?: string;
  readonly errors: readonly string[];
  readonly metadata: typeof DCEC_INTEGRATION_METADATA;
}

export interface DcecRoundTripValidationResult extends DcecTokenConversionResult {
  readonly roundTripToken?: DcecParseToken;
  readonly roundTripFormula?: DcecFormula;
  readonly roundTripSExpression?: string;
  readonly roundTripFormulaText?: string;
}

export type DcecFormulaValidationResult =
  | { ok: true; errors: [] }
  | { ok: false; errors: string[] };

export type DcecIntegrationOperation =
  | 'parse'
  | 'convert'
  | 'roundTrip'
  | 'validate'
  | (string & {});

export interface DcecIntegrationRequest {
  readonly operation: DcecIntegrationOperation;
  readonly source?: string | DcecParseToken | DcecFormula;
  readonly formula?: DcecFormula;
  readonly options?: ParseDcecStringOptions;
}

export interface DcecIntegrationAdapter {
  readonly metadata: typeof DCEC_INTEGRATION_METADATA;
  readonly capabilities: readonly DcecIntegrationOperation[];
  parse(source: string, options?: ParseDcecStringOptions): DcecTokenConversionResult;
  convert(
    source: string | DcecParseToken | DcecFormula,
    options?: ParseDcecStringOptions,
  ): DcecTokenConversionResult;
  roundTrip(
    source: string | DcecParseToken | DcecFormula,
    options?: ParseDcecStringOptions,
  ): DcecRoundTripValidationResult;
  validate(formula: DcecFormula): DcecFormulaValidationResult;
  invoke(
    request: DcecIntegrationRequest,
  ): DcecTokenConversionResult | DcecRoundTripValidationResult | DcecFormulaValidationResult;
}

export function parseDcecExpressionToToken(
  expression: string,
  options: ParseDcecStringOptions = {},
): DcecParseToken | undefined {
  if (!expression.trim()) return undefined;

  const raw = expression.trim();
  const notMatch = /^not\s+(.+)$/s.exec(raw);
  if (notMatch) {
    const subToken = parseDcecExpressionToToken(notMatch[1], options);
    return subToken === undefined ? undefined : new DcecParseToken('not', [subToken]);
  }

  let text = stripDcecComments(removeDcecSemicolonComments(expression));
  text = stripDcecWhitespace(text);
  if (!checkDcecParens(text)) {
    throw new LogicParseError(`Unbalanced parentheses in: ${text}`, { expression });
  }
  text = consolidateDcecParens(text);
  text = functorizeDcecSymbols(text);
  text = tuckDcecFunctions(text);
  text = stripDcecWhitespace(text);

  if (text.startsWith('(') && text.endsWith(')')) {
    return parseDcecCommaToken(text);
  }

  let args = replaceDcecSynonyms(text.split(',').filter((arg) => arg.length > 0));
  const atomics: Record<string, string[]> = {};
  args = prefixDcecLogicalFunctions(args, { atomics });
  args = prefixDcecEmdas(args, { atomics });

  if (args.length === 1 && isDcecParseToken(args[0])) return args[0];
  if (args.length > 1) return new DcecParseToken('and', args);
  if (args.length === 1 && typeof args[0] === 'string')
    return new DcecParseToken('atomic', [stripTokenParens(args[0])]);
  return undefined;
}

export function tokenToDcecFormula(
  token: DcecParseToken,
  options: ParseDcecStringOptions & { variables?: Map<string, DcecVariable> } = {},
): DcecFormula | undefined {
  const variables = options.variables ?? new Map<string, DcecVariable>();
  const funcName = stripTokenParens(token.funcName).toLowerCase();

  if (funcName === 'atomic') {
    const predicateName = token.args.find((arg): arg is string => typeof arg === 'string');
    return predicateName
      ? new DcecAtomicFormula(new DcecPredicateSymbol(stripTokenParens(predicateName), []), [])
      : undefined;
  }

  if (funcName === 'and' && token.args.length >= 2) {
    const formulas = token.args
      .map((arg) => argToDcecFormula(arg, options.namespace, variables))
      .filter(isDcecFormula);
    return formulas.length >= 2
      ? new DcecConnectiveFormula(DcecLogicalConnective.AND, formulas)
      : undefined;
  }
  if (funcName === 'or' && token.args.length >= 2) {
    const formulas = token.args
      .map((arg) => argToDcecFormula(arg, options.namespace, variables))
      .filter(isDcecFormula);
    return formulas.length >= 2
      ? new DcecConnectiveFormula(DcecLogicalConnective.OR, formulas)
      : undefined;
  }
  if (funcName === 'not' && token.args.length === 1) {
    const formula = argToDcecFormula(token.args[0], options.namespace, variables);
    return formula ? new DcecConnectiveFormula(DcecLogicalConnective.NOT, [formula]) : undefined;
  }
  if (funcName === 'implies' && token.args.length === 2) {
    const left = argToDcecFormula(token.args[0], options.namespace, variables);
    const right = argToDcecFormula(token.args[1], options.namespace, variables);
    return left && right
      ? new DcecConnectiveFormula(DcecLogicalConnective.IMPLIES, [left, right])
      : undefined;
  }
  if ((funcName === 'iff' || funcName === 'ifandonlyif') && token.args.length === 2) {
    const left = argToDcecFormula(token.args[0], options.namespace, variables);
    const right = argToDcecFormula(token.args[1], options.namespace, variables);
    return left && right
      ? new DcecConnectiveFormula(DcecLogicalConnective.BICONDITIONAL, [left, right])
      : undefined;
  }
  if (funcName === 'o' && token.args.length >= 1) {
    const formula = argToDcecFormula(
      token.args[token.args.length - 1],
      options.namespace,
      variables,
    );
    return formula ? new DcecDeonticFormula(DcecDeonticOperator.OBLIGATION, formula) : undefined;
  }
  if (funcName === 'p' && token.args.length >= 1) {
    const formula = argToDcecFormula(
      token.args[token.args.length - 1],
      options.namespace,
      variables,
    );
    return formula ? new DcecDeonticFormula(DcecDeonticOperator.PERMISSION, formula) : undefined;
  }
  if (funcName === 'f' && token.args.length >= 1) {
    const formula = argToDcecFormula(
      token.args[token.args.length - 1],
      options.namespace,
      variables,
    );
    return formula ? new DcecDeonticFormula(DcecDeonticOperator.PROHIBITION, formula) : undefined;
  }

  if ((funcName === 'b' || funcName === 'k' || funcName === 'i') && token.args.length >= 1) {
    const agentArg = token.args.length >= 2 ? token.args[0] : 'agent';
    const formula = argToDcecFormula(
      token.args[token.args.length - 1],
      options.namespace,
      variables,
    );
    if (!formula) return undefined;
    const operator =
      funcName === 'b'
        ? DcecCognitiveOperator.BELIEF
        : funcName === 'k'
          ? DcecCognitiveOperator.KNOWLEDGE
          : DcecCognitiveOperator.INTENTION;
    return new DcecCognitiveFormula(operator, makeAgentTerm(String(agentArg), variables), formula);
  }

  if (['always', 'box', '□'].includes(funcName) && token.args.length >= 1) {
    const formula = argToDcecFormula(
      token.args[token.args.length - 1],
      options.namespace,
      variables,
    );
    return formula ? new DcecTemporalFormula(DcecTemporalOperator.ALWAYS, formula) : undefined;
  }
  if (['eventually', 'diamond', '◊'].includes(funcName) && token.args.length >= 1) {
    const formula = argToDcecFormula(
      token.args[token.args.length - 1],
      options.namespace,
      variables,
    );
    return formula ? new DcecTemporalFormula(DcecTemporalOperator.EVENTUALLY, formula) : undefined;
  }
  if (['next', 'x'].includes(funcName) && token.args.length >= 1) {
    const formula = argToDcecFormula(
      token.args[token.args.length - 1],
      options.namespace,
      variables,
    );
    return formula ? new DcecTemporalFormula(DcecTemporalOperator.NEXT, formula) : undefined;
  }

  return tokenToAtomicFormula(token, options.namespace, variables);
}

export function parseDcecString(
  expression: string,
  options: ParseDcecStringOptions = {},
): DcecFormula | undefined {
  const normalized = expression.replace(/\bnot\s+(?!\()(\w+)/g, 'not($1)');
  const token = parseDcecExpressionToToken(normalized, options);
  return token === undefined ? undefined : tokenToDcecFormula(token, options);
}

export function formulaToDcecToken(formula: DcecFormula): DcecParseToken {
  if (formula instanceof DcecAtomicFormula) {
    if (formula.arguments.length === 0)
      return new DcecParseToken('atomic', [formula.predicate.name]);
    return new DcecParseToken(formula.predicate.name, formula.arguments.map(termToDcecTokenArg));
  }
  if (formula instanceof DcecConnectiveFormula) {
    return new DcecParseToken(formula.connective, formula.formulas.map(formulaToDcecToken));
  }
  if (formula instanceof DcecDeonticFormula) {
    return new DcecParseToken(formula.operator, [formulaToDcecToken(formula.formula)]);
  }
  if (formula instanceof DcecCognitiveFormula) {
    return new DcecParseToken(formula.operator, [
      termToDcecTokenArg(formula.agent),
      formulaToDcecToken(formula.formula),
    ]);
  }
  if (formula instanceof DcecTemporalFormula) {
    const args: DcecParseArg[] = [formulaToDcecToken(formula.formula)];
    if (formula.time) args.unshift(termToDcecTokenArg(formula.time));
    return new DcecParseToken(formula.operator, args);
  }
  throw new LogicParseError('Unsupported DCEC formula conversion target', {
    formula: String(formula),
  });
}

export function convertDcecInputToToken(
  source: string | DcecParseToken | DcecFormula,
  options: ParseDcecStringOptions = {},
): DcecTokenConversionResult {
  try {
    const token =
      source instanceof DcecParseToken
        ? source
        : typeof source === 'string'
          ? parseDcecExpressionToToken(source, options)
          : formulaToDcecToken(source);
    if (!token) {
      return {
        ok: false,
        errors: ['DCEC input did not produce a parse token.'],
        metadata: DCEC_INTEGRATION_METADATA,
      };
    }
    const formula = tokenToDcecFormula(token, options);
    if (!formula) {
      return {
        ok: false,
        token,
        errors: ['DCEC token did not produce a formula.'],
        metadata: DCEC_INTEGRATION_METADATA,
      };
    }
    return {
      ok: true,
      token,
      formula,
      canonicalSExpression: token.createSExpression(),
      canonicalFormula: formula.toString(),
      errors: [],
      metadata: DCEC_INTEGRATION_METADATA,
    };
  } catch (error) {
    return {
      ok: false,
      errors: [error instanceof Error ? error.message : 'Unknown DCEC token conversion error'],
      metadata: DCEC_INTEGRATION_METADATA,
    };
  }
}

export function validateDcecRoundTrip(
  source: string | DcecParseToken | DcecFormula,
  options: ParseDcecStringOptions = {},
): DcecRoundTripValidationResult {
  const converted = convertDcecInputToToken(source, options);
  if (!converted.ok || !converted.token || !converted.formula) return converted;
  const roundTripToken = formulaToDcecToken(converted.formula);
  const roundTripFormula = tokenToDcecFormula(roundTripToken, options);
  if (!roundTripFormula) {
    return {
      ...converted,
      ok: false,
      roundTripToken,
      roundTripSExpression: roundTripToken.createSExpression(),
      errors: ['DCEC formula-to-token output did not convert back to a formula.'],
    };
  }
  const roundTripFormulaText = roundTripFormula.toString();
  const ok = converted.canonicalFormula === roundTripFormulaText;
  return {
    ...converted,
    ok,
    roundTripToken,
    roundTripFormula,
    roundTripSExpression: roundTripToken.createSExpression(),
    roundTripFormulaText,
    errors: ok
      ? []
      : [`DCEC round-trip mismatch: ${converted.canonicalFormula} !== ${roundTripFormulaText}`],
  };
}

export function validateDcecFormula(formula: DcecFormula): DcecFormulaValidationResult {
  try {
    // Construction already performs arity validation; this recursive pass is a browser-native guard.
    formula.getFreeVariables();
    formula.toString();
    return { ok: true, errors: [] };
  } catch (error) {
    return {
      ok: false,
      errors: [error instanceof Error ? error.message : 'Unknown DCEC formula validation error'],
    };
  }
}

export function createBrowserNativeDcecIntegrationAdapter(): DcecIntegrationAdapter {
  return {
    metadata: DCEC_INTEGRATION_METADATA,
    capabilities: ['parse', 'convert', 'roundTrip', 'validate'],
    parse(source: string, options: ParseDcecStringOptions = {}): DcecTokenConversionResult {
      return convertDcecInputToToken(source, options);
    },
    convert(
      source: string | DcecParseToken | DcecFormula,
      options: ParseDcecStringOptions = {},
    ): DcecTokenConversionResult {
      return convertDcecInputToToken(source, options);
    },
    roundTrip(
      source: string | DcecParseToken | DcecFormula,
      options: ParseDcecStringOptions = {},
    ): DcecRoundTripValidationResult {
      return validateDcecRoundTrip(source, options);
    },
    validate(formula: DcecFormula): DcecFormulaValidationResult {
      return validateDcecFormula(formula);
    },
    invoke(
      request: DcecIntegrationRequest,
    ): DcecTokenConversionResult | DcecRoundTripValidationResult | DcecFormulaValidationResult {
      if (request.operation === 'validate') {
        return request.formula
          ? validateDcecFormula(request.formula)
          : { ok: false, errors: ['DCEC validate operation requires a formula.'] };
      }
      if (
        request.operation !== 'parse' &&
        request.operation !== 'convert' &&
        request.operation !== 'roundTrip'
      ) {
        return {
          ok: false,
          errors: [`Unsupported browser-native DCEC integration operation: ${request.operation}`],
          metadata: DCEC_INTEGRATION_METADATA,
        };
      }
      if (request.source === undefined) {
        return {
          ok: false,
          errors: [`DCEC ${request.operation} operation requires a source.`],
          metadata: DCEC_INTEGRATION_METADATA,
        };
      }
      if (request.operation === 'parse' || request.operation === 'convert') {
        return convertDcecInputToToken(request.source, request.options);
      }
      if (request.operation === 'roundTrip') {
        return validateDcecRoundTrip(request.source, request.options);
      }
      return convertDcecInputToToken(request.source, request.options);
    },
  };
}

function parseDcecCommaToken(source: string): DcecParseToken {
  let inner = stripOuterParens(source.trim());
  while (isSingleWrappedExpression(inner)) {
    inner = stripOuterParens(inner.trim());
  }
  const parts = splitTopLevelCommaArgs(inner);
  if (parts.length === 0) throw new LogicParseError('Empty DCEC token expression', { source });

  const maybeInfixArgs = replaceDcecSynonyms(parts);
  const atomics: Record<string, string[]> = {};
  const logicalArgs = prefixDcecLogicalFunctions(maybeInfixArgs, { atomics });
  const emdasArgs = prefixDcecEmdas(logicalArgs, { atomics });
  if (emdasArgs.length === 1 && isDcecParseToken(emdasArgs[0])) return emdasArgs[0];

  const [funcName, ...rawArgs] = parts;
  return new DcecParseToken(stripTokenParens(funcName), rawArgs.map(parseCommaArg));
}

function parseCommaArg(source: string): DcecParseArg {
  const trimmed = source.trim();
  if (trimmed.startsWith('(') && trimmed.endsWith(')')) {
    const inner = stripOuterParens(trimmed);
    if (!splitTopLevelCommaArgs(inner).slice(1).length) return stripTokenParens(inner);
    return parseDcecCommaToken(trimmed);
  }
  return stripTokenParens(trimmed);
}

function splitTopLevelCommaArgs(source: string): string[] {
  const parts: string[] = [];
  let depth = 0;
  let start = 0;
  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    if (char === '(') depth += 1;
    if (char === ')') depth -= 1;
    if (char === ',' && depth === 0) {
      parts.push(source.slice(start, index).trim());
      start = index + 1;
    }
  }
  parts.push(source.slice(start).trim());
  return parts.filter((part) => part.length > 0);
}

function argToDcecFormula(
  arg: DcecParseArg,
  namespace: DcecNamespace | undefined,
  variables: Map<string, DcecVariable>,
): DcecFormula | undefined {
  if (isDcecParseToken(arg)) return tokenToDcecFormula(arg, { namespace, variables });
  const cleanArg = stripTokenParens(arg);
  return cleanArg ? new DcecAtomicFormula(new DcecPredicateSymbol(cleanArg, []), []) : undefined;
}

function tokenToAtomicFormula(
  token: DcecParseToken,
  namespace: DcecNamespace | undefined,
  variables: Map<string, DcecVariable>,
): DcecFormula {
  const terms = token.args
    .filter((arg): arg is string => typeof arg === 'string')
    .map((arg) => makeObjectTerm(stripTokenParens(arg), namespace, variables));
  const objectSort = namespace?.getSort('Object') ?? new DcecSort('Object');
  return new DcecAtomicFormula(
    new DcecPredicateSymbol(
      stripTokenParens(token.funcName),
      terms.map(() => objectSort),
    ),
    terms,
  );
}

function termToDcecTokenArg(term: DcecTerm): string {
  if (term instanceof DcecVariableTerm) return term.variable.name;
  return term.arguments.length === 0
    ? term.functionSymbol.name
    : `${term.functionSymbol.name}(${term.arguments.map(termToDcecTokenArg).join(',')})`;
}

function makeAgentTerm(
  value: string,
  variables: Map<string, DcecVariable>,
): DcecVariableTerm | DcecFunctionTerm {
  const cleanValue = stripTokenParens(value);
  const agentSort = new DcecSort('Agent');
  if (/^[a-z]/.test(cleanValue)) {
    if (!variables.has(cleanValue))
      variables.set(cleanValue, new DcecVariable(cleanValue, agentSort));
    return new DcecVariableTerm(variables.get(cleanValue)!);
  }
  return new DcecFunctionTerm(new DcecFunctionSymbol(cleanValue, [], agentSort), []);
}

function makeObjectTerm(
  value: string,
  namespace: DcecNamespace | undefined,
  variables: Map<string, DcecVariable>,
): DcecVariableTerm | DcecFunctionTerm {
  const objectSort = namespace?.getSort('Object') ?? new DcecSort('Object');
  if (/^[a-z]/.test(value)) {
    if (!variables.has(value)) variables.set(value, new DcecVariable(value, objectSort));
    return new DcecVariableTerm(variables.get(value)!);
  }
  return new DcecFunctionTerm(new DcecFunctionSymbol(value, [], objectSort), []);
}

function stripOuterParens(source: string): string {
  return source.slice(1, -1);
}

function isSingleWrappedExpression(source: string): boolean {
  const trimmed = source.trim();
  if (!trimmed.startsWith('(') || !trimmed.endsWith(')')) return false;
  let depth = 0;
  for (let index = 0; index < trimmed.length; index += 1) {
    if (trimmed[index] === '(') depth += 1;
    if (trimmed[index] === ')') depth -= 1;
    if (depth === 0 && index < trimmed.length - 1) return false;
  }
  return depth === 0;
}

function stripTokenParens(source: string): string {
  let result = source.trim();
  while (result.startsWith('(') && result.endsWith(')') && checkDcecParens(result.slice(1, -1))) {
    result = result.slice(1, -1).trim();
  }
  return result;
}

function isDcecFormula(formula: DcecFormula | undefined): formula is DcecFormula {
  return formula !== undefined;
}
