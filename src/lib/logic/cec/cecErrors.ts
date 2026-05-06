import {
  LogicConversionError,
  LogicError,
  LogicErrorContext,
  LogicParseError,
  LogicProofError,
  LogicValidationError,
} from '../errors';

export type CecErrorContext = LogicErrorContext;

export const CEC_ERROR_HANDLING_METADATA = {
  sourcePythonModule: 'logic/CEC/native/error_handling.py',
  runtime: 'browser-native-typescript',
  browserNative: true,
  pythonRuntime: false,
  serverRuntime: false,
  recoveryPolicy: 'fail-closed',
} as const;

export type CecErrorKind =
  | 'cec'
  | 'conversion'
  | 'grammar'
  | 'knowledge-base'
  | 'namespace'
  | 'parse'
  | 'proof'
  | 'validation'
  | 'unknown';

export interface CecRecoveryMetadata {
  readonly metadata: typeof CEC_ERROR_HANDLING_METADATA;
  readonly operation: string;
  readonly errorKind: CecErrorKind;
  readonly errorName: string;
  readonly message: string;
  readonly context: CecErrorContext;
  readonly suggestion?: string;
  readonly recovered: false;
  readonly failClosed: true;
}

export interface CecValidationAdapterResult {
  readonly ok: boolean;
  readonly valid: boolean;
  readonly errors: readonly string[];
  readonly warnings: readonly string[];
  readonly metadata: typeof CEC_ERROR_HANDLING_METADATA;
  readonly recovery?: CecRecoveryMetadata;
}

export class CecError extends LogicError {
  readonly suggestion?: string;

  constructor(message: string, context: CecErrorContext = {}, suggestion?: string) {
    super(formatCecErrorMessage(message, context, suggestion), context);
    this.suggestion = suggestion;
  }
}

export class CecParsingError extends LogicParseError {
  readonly suggestion?: string;

  constructor(
    message: string,
    expression?: string,
    position?: number,
    expected?: string,
    suggestion?: string,
  ) {
    const context: CecErrorContext = {};
    if (expression !== undefined) context.expression = expression;
    if (position !== undefined) context.position = position;
    if (expected !== undefined) context.expected = expected;
    super(formatCecErrorMessage(message, context, suggestion), context);
    this.suggestion = suggestion;
  }
}

export class CecProvingError extends LogicProofError {
  readonly suggestion?: string;

  constructor(
    message: string,
    formula?: string,
    proofStep?: number,
    rule?: string,
    suggestion?: string,
  ) {
    const context: CecErrorContext = {};
    if (formula !== undefined) context.formula = formula;
    if (proofStep !== undefined) context.proof_step = proofStep;
    if (rule !== undefined) context.rule = rule;
    super(formatCecErrorMessage(message, context, suggestion), context);
    this.suggestion = suggestion;
  }
}

export class CecConversionError extends LogicConversionError {
  readonly suggestion?: string;

  constructor(
    message: string,
    text?: string,
    language = 'en',
    pattern?: string,
    suggestion?: string,
  ) {
    const context: CecErrorContext = { language };
    if (text !== undefined) context.text = text;
    if (pattern !== undefined) context.pattern = pattern;
    super(formatCecErrorMessage(message, context, suggestion), context);
    this.suggestion = suggestion;
  }
}

export class CecValidationError extends LogicValidationError {
  readonly suggestion?: string;

  constructor(
    message: string,
    value?: unknown,
    expectedType?: string,
    constraint?: string,
    suggestion?: string,
  ) {
    const context: CecErrorContext = {};
    if (value !== undefined) context.value = String(value);
    if (expectedType !== undefined) context.expected_type = expectedType;
    if (constraint !== undefined) context.constraint = constraint;
    super(formatCecErrorMessage(message, context, suggestion), context);
    this.suggestion = suggestion;
  }
}

export class CecNamespaceError extends CecError {
  constructor(message: string, symbol?: string, operation?: string, suggestion?: string) {
    const context: CecErrorContext = {};
    if (symbol !== undefined) context.symbol = symbol;
    if (operation !== undefined) context.operation = operation;
    super(message, context, suggestion);
  }
}

export class CecGrammarError extends CecError {
  constructor(message: string, rule?: string, inputText?: string, suggestion?: string) {
    const context: CecErrorContext = {};
    if (rule !== undefined) context.rule = rule;
    if (inputText !== undefined) context.input_text = inputText;
    super(message, context, suggestion);
  }
}

export class CecKnowledgeBaseError extends CecError {
  constructor(message: string, operation?: string, formulaId?: string, suggestion?: string) {
    const context: CecErrorContext = {};
    if (operation !== undefined) context.operation = operation;
    if (formulaId !== undefined) context.formula_id = formulaId;
    super(message, context, suggestion);
  }
}

export const DcecParsingError = CecParsingError;
export const DcecError = CecError;

export interface ErrorHandlerOptions<TDefault = unknown> {
  defaultReturn?: TDefault;
  reraise?: boolean;
  context?: string;
}

export function handleCecProofError<TArgs extends unknown[], TResult, TDefault = undefined>(
  fn: (...args: TArgs) => TResult,
  options: ErrorHandlerOptions<TDefault> = {},
): (...args: TArgs) => TResult | TDefault {
  const { defaultReturn, reraise = false, context } = options;
  return (...args: TArgs) => {
    try {
      return fn(...args);
    } catch (error) {
      if (!reraise) return defaultReturn as TDefault;
      if (error instanceof CecProvingError || error instanceof LogicProofError) {
        throw new CecProvingError(prefixContext(error.message, context), undefined, undefined, undefined, error instanceof CecProvingError ? error.suggestion : undefined);
      }
      if (error instanceof LogicError || error instanceof Error) {
        throw new CecProvingError(prefixContext(`Proof failed: ${error.message}`, context));
      }
      throw new CecProvingError(prefixContext('Proof failed: unknown error', context));
    }
  };
}

export function handleCecParseError<TArgs extends unknown[], TResult, TDefault = undefined>(
  fn: (...args: TArgs) => TResult,
  options: ErrorHandlerOptions<TDefault> = {},
): (...args: TArgs) => TResult | TDefault {
  const { defaultReturn, reraise = false, context } = options;
  return (...args: TArgs) => {
    try {
      return fn(...args);
    } catch (error) {
      if (!reraise) return defaultReturn as TDefault;
      if (error instanceof CecParsingError || error instanceof LogicParseError) {
        throw new CecParsingError(prefixContext(error.message, context));
      }
      if (error instanceof LogicError || error instanceof Error) {
        throw new CecParsingError(prefixContext(`Parse failed: ${error.message}`, context));
      }
      throw new CecParsingError(prefixContext('Parse failed: unknown error', context));
    }
  };
}

export function withCecErrorContext<TArgs extends unknown[], TResult>(
  fn: (...args: TArgs) => TResult,
  context: string,
): (...args: TArgs) => TResult {
  return (...args: TArgs) => {
    try {
      return fn(...args);
    } catch (error) {
      if (error instanceof CecError) {
        throw new CecError(prefixContext(error.message, context), error.context, error.suggestion);
      }
      if (error instanceof LogicError || error instanceof Error) {
        throw new CecError(prefixContext(error.message, context));
      }
      throw new CecError(`${context}: unknown error`);
    }
  };
}

export function safeCecCall<TArgs extends unknown[], TResult, TDefault = undefined>(
  fn: (...args: TArgs) => TResult,
  args: TArgs,
  defaultReturn?: TDefault,
  logger?: Pick<Console, 'error' | 'debug'>,
): TResult | TDefault {
  try {
    return fn(...args);
  } catch (error) {
    if (logger) {
      logger.error(`Error in ${fn.name || 'anonymous'}: ${error instanceof Error ? error.message : String(error)}`);
      logger.debug(error instanceof Error && error.stack ? error.stack : String(error));
    }
    return defaultReturn as TDefault;
  }
}

export function createCecRecoveryMetadata(
  error: unknown,
  operation: string,
  context: CecErrorContext = {},
): CecRecoveryMetadata {
  const logicError = error instanceof LogicError ? error : undefined;
  const standardError = error instanceof Error ? error : undefined;
  return {
    metadata: CEC_ERROR_HANDLING_METADATA,
    operation,
    errorKind: classifyCecError(error),
    errorName: standardError?.name ?? 'UnknownError',
    message: standardError?.message ?? String(error),
    context: { ...context, ...(logicError?.context ?? {}) },
    suggestion: readCecSuggestion(error),
    recovered: false,
    failClosed: true,
  };
}

export function createFailClosedCecValidationResult(
  error: unknown,
  operation: string,
  context: CecErrorContext = {},
): CecValidationAdapterResult {
  const recovery = createCecRecoveryMetadata(error, operation, context);
  return {
    ok: false,
    valid: false,
    errors: [`${operation} failed closed: ${recovery.message}`],
    warnings: [],
    metadata: CEC_ERROR_HANDLING_METADATA,
    recovery,
  };
}

export function adaptCecValidationResult(
  value: unknown,
  operation = 'validate',
): CecValidationAdapterResult {
  if (!isRecord(value)) {
    return createFailClosedCecValidationResult(
      new CecValidationError('CEC validation adapter expected an object result'),
      operation,
    );
  }
  const ok = typeof value.ok === 'boolean'
    ? value.ok
    : typeof value.valid === 'boolean'
      ? value.valid
      : false;
  const errors = toStringList(value.errors);
  return {
    ok,
    valid: ok,
    errors: ok ? errors : errors.length > 0 ? errors : ['CEC validation failed without diagnostics.'],
    warnings: toStringList(value.warnings),
    metadata: CEC_ERROR_HANDLING_METADATA,
  };
}

export function runCecValidationAdapter<TResult>(
  operation: string,
  fn: () => TResult,
): CecValidationAdapterResult {
  try {
    return adaptCecValidationResult(fn(), operation);
  } catch (error) {
    return createFailClosedCecValidationResult(error, operation);
  }
}

export function formatCecOperationError(error: unknown, operation: string, details: Record<string, unknown> = {}): string {
  const message = error instanceof Error ? error.message : String(error);
  let formatted = `Error during ${operation}: ${message}`;
  const detailEntries = Object.entries(details);
  if (detailEntries.length > 0) {
    formatted += `\nDetails: ${detailEntries.map(([key, value]) => `${key}=${String(value)}`).join(', ')}`;
  }
  return formatted;
}

export function validateCecNotNone(value: unknown, name: string): void {
  if (value === null || value === undefined) {
    throw new CecValidationError(`${name} cannot be None`);
  }
}

export function validateCecType(value: unknown, expectedType: 'string' | 'number' | 'boolean' | 'object' | 'function', name: string): void {
  if (typeof value !== expectedType) {
    throw new CecValidationError(`${name} must be of type ${expectedType}, got ${typeof value}`);
  }
}

export function validateDcecFormulaLike(formula: unknown, allowNone = false): void {
  if (formula === null || formula === undefined) {
    if (!allowNone) throw new CecValidationError('formula cannot be None');
    return;
  }
  if (
    typeof formula !== 'object'
    || typeof (formula as { toString?: unknown }).toString !== 'function'
    || typeof (formula as { getFreeVariables?: unknown }).getFreeVariables !== 'function'
    || typeof (formula as { substitute?: unknown }).substitute !== 'function'
  ) {
    throw new CecValidationError('formula must be a DCEC formula-like object');
  }
}

function formatCecErrorMessage(message: string, context: CecErrorContext, suggestion?: string): string {
  let fullMessage = message;
  const entries = Object.entries(context).filter(([, value]) => value !== undefined);
  if (entries.length > 0) {
    fullMessage += ` [Context: ${entries.map(([key, value]) => `${key}=${String(value)}`).join(', ')}]`;
  }
  if (suggestion) {
    fullMessage += ` [Suggestion: ${suggestion}]`;
  }
  return fullMessage;
}

function prefixContext(message: string, context?: string): string {
  return context ? `${context}: ${message}` : message;
}

function classifyCecError(error: unknown): CecErrorKind {
  if (error instanceof CecParsingError || error instanceof LogicParseError) return 'parse';
  if (error instanceof CecProvingError || error instanceof LogicProofError) return 'proof';
  if (error instanceof CecConversionError || error instanceof LogicConversionError) return 'conversion';
  if (error instanceof CecValidationError || error instanceof LogicValidationError) return 'validation';
  if (error instanceof CecNamespaceError) return 'namespace';
  if (error instanceof CecGrammarError) return 'grammar';
  if (error instanceof CecKnowledgeBaseError) return 'knowledge-base';
  if (error instanceof CecError) return 'cec';
  return 'unknown';
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function toStringList(value: unknown): readonly string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === 'string')
    : [];
}

function readCecSuggestion(error: unknown): string | undefined {
  if (!isRecord(error)) return undefined;
  return typeof error.suggestion === 'string' ? error.suggestion : undefined;
}
