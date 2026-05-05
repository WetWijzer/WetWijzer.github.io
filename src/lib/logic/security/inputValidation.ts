import { LogicValidationError } from '../errors';

export const MAX_TEXT_LENGTH = 10000;
export const INPUT_VALIDATION_METADATA = {
  sourcePythonModule: 'logic/security/input_validation.py',
  browserNative: true,
  serverCallsAllowed: false,
  pythonRuntimeAllowed: false,
  deterministic: true,
} as const;

export interface TextValidationOptions {
  readonly maxLength?: number;
  readonly allowHtml?: boolean;
  readonly allowControlCharacters?: boolean;
}

export interface SanitizedInput {
  readonly value: string;
  readonly changed: boolean;
  readonly removed: Array<string>;
}

interface UnsafePattern {
  readonly name: string;
  readonly pattern: RegExp;
}

const CONTROL_CHARACTER_PATTERN = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g;
const HTML_ESCAPE_PATTERN = /[&<>"']/g;
const HTML_ESCAPES: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};
const UNSAFE_INPUT_PATTERNS: Array<UnsafePattern> = [
  { name: 'script_tag', pattern: /<\s*\/?\s*script\b/i },
  { name: 'javascript_url', pattern: /\bjavascript\s*:/i },
  { name: 'html_event_handler', pattern: /\bon[a-z]+\s*=/i },
  { name: 'data_html_url', pattern: /\bdata\s*:\s*text\/html/i },
];

export function validateText(
  text: unknown,
  options: TextValidationOptions = {},
): asserts text is string {
  const maxLength = options.maxLength ?? MAX_TEXT_LENGTH;
  if (typeof text !== 'string') {
    throw new LogicValidationError(`'text' must be a string, got ${typeof text}`, {
      field: 'text',
      type: typeof text,
    });
  }
  if (!text.trim()) {
    throw new LogicValidationError("'text' must not be empty.", { field: 'text' });
  }
  if (!options.allowControlCharacters && CONTROL_CHARACTER_PATTERN.test(text)) {
    CONTROL_CHARACTER_PATTERN.lastIndex = 0;
    throw new LogicValidationError("'text' contains control characters.", { field: 'text' });
  }
  if (text.length > maxLength) {
    throw new LogicValidationError(
      `'text' exceeds maximum length of ${maxLength} characters (got ${text.length}).`,
      {
        field: 'text',
        length: text.length,
        max: maxLength,
      },
    );
  }
  if (!options.allowHtml) {
    const unsafe = findUnsafeInputPattern(text);
    if (unsafe) {
      throw new LogicValidationError(`'text' contains unsafe input pattern '${unsafe}'.`, {
        field: 'text',
        pattern: unsafe,
      });
    }
  }
}

export function sanitizeInput(input: unknown, options: TextValidationOptions = {}): SanitizedInput {
  if (typeof input !== 'string') {
    throw new LogicValidationError(`'input' must be a string, got ${typeof input}`, {
      field: 'input',
      type: typeof input,
    });
  }

  const normalized = input.normalize('NFKC');
  const removed: Array<string> = [];
  const withoutControls = normalized.replace(CONTROL_CHARACTER_PATTERN, (character) => {
    removed.push(`control:${character.charCodeAt(0)}`);
    return '';
  });
  const value = options.allowHtml ? withoutControls.trim() : escapeHtml(withoutControls.trim());
  validateText(value, { ...options, allowHtml: true });

  return {
    value,
    changed: value !== input,
    removed,
  };
}

export function validateSafeInput(input: unknown, options: TextValidationOptions = {}): string {
  if (typeof input === 'string' && !options.allowHtml) {
    const rawUnsafe = findUnsafeInputPattern(input);
    if (rawUnsafe) {
      throw new LogicValidationError(`'input' contains unsafe input pattern '${rawUnsafe}'.`, {
        field: 'input',
        pattern: rawUnsafe,
      });
    }
  }
  const sanitized = sanitizeInput(input, options);
  const unsafe = findUnsafeInputPattern(sanitized.value);
  if (unsafe && !options.allowHtml) {
    throw new LogicValidationError(`'input' contains unsafe input pattern '${unsafe}'.`, {
      field: 'input',
      pattern: unsafe,
    });
  }
  return sanitized.value;
}

export function validateFormula(formula: unknown): asserts formula is string {
  validateFormulaString(formula, 'formula');
}

export function validateFormulaList(formulas: unknown): string[] {
  if (!isIterable(formulas) || typeof formulas === 'string') {
    throw new LogicValidationError(`'formulas' must be iterable, got ${typeof formulas}`, {
      field: 'formulas',
      type: typeof formulas,
    });
  }
  const values = [...formulas] as unknown[];
  values.forEach((formula, index) => validateFormulaString(formula, `formulas[${index}]`));
  return values as string[];
}

export class InputValidator {
  readonly metadata = INPUT_VALIDATION_METADATA;

  validateText(text: unknown, options: TextValidationOptions = {}): string {
    validateText(text, options);
    return text;
  }

  validateFormula(formula: unknown): string {
    validateFormula(formula);
    return formula;
  }

  validateFormulaList(formulas: unknown): string[] {
    return validateFormulaList(formulas);
  }

  sanitizeInput(input: unknown, options: TextValidationOptions = {}): SanitizedInput {
    return sanitizeInput(input, options);
  }

  validateSafeInput(input: unknown, options: TextValidationOptions = {}): string {
    return validateSafeInput(input, options);
  }
}

function validateFormulaString(formula: unknown, fieldName: string): asserts formula is string {
  if (typeof formula !== 'string') {
    throw new LogicValidationError(`'${fieldName}' must be a string, got ${typeof formula}`, {
      field: fieldName,
      type: typeof formula,
    });
  }
  if (!formula.trim()) {
    throw new LogicValidationError(`'${fieldName}' must not be empty.`, { field: fieldName });
  }
  if (formula.includes('\0')) {
    throw new LogicValidationError(`'${fieldName}' contains null bytes.`, { field: fieldName });
  }
}

function isIterable(value: unknown): value is Iterable<unknown> {
  return Boolean(value && typeof (value as Iterable<unknown>)[Symbol.iterator] === 'function');
}

function findUnsafeInputPattern(value: string): string | undefined {
  return UNSAFE_INPUT_PATTERNS.find((candidate) => candidate.pattern.test(value))?.name;
}

function escapeHtml(value: string): string {
  return value.replace(HTML_ESCAPE_PATTERN, (character) => HTML_ESCAPES[character] ?? character);
}
