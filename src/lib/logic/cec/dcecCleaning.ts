const SYMBOL_REPLACEMENTS: Record<string, string> = {
  '<->': 'ifAndOnlyIf',
  '->': 'implies',
  '>=': 'greaterOrEqual',
  '<=': 'lessOrEqual',
  '===': 'tautology',
  '==': 'equals',
  '=': 'equals',
  '>': 'greater',
  '<': 'less',
  '^': 'exponent',
  '*': '*',
  '/': 'divide',
  '+': 'add',
  '-': '-',
  '&': '&',
  '|': '|',
  '~': 'not',
};

const DCEC_SYMBOLS = Object.keys(SYMBOL_REPLACEMENTS).sort(
  (left, right) => right.length - left.length,
);

const TOKEN_REPLACEMENTS: Record<string, string> = {
  '∀': 'forall',
  '∃': 'exists',
  '¬': 'not',
  '∧': 'and',
  '∨': 'or',
  '→': 'implies',
  '↔': 'ifAndOnlyIf',
  '≥': 'greaterOrEqual',
  '≤': 'lessOrEqual',
};

const TOKEN_ALIASES: Record<string, string> = {
  'if-and-only-if': 'ifAndOnlyIf',
  if_and_only_if: 'ifAndOnlyIf',
  greater_or_equal: 'greaterOrEqual',
  less_or_equal: 'lessOrEqual',
  true_: 'true',
  false_: 'false',
};

export interface DcecCleaningResult {
  cleaned: string;
  normalizedText: string;
  tokens: Array<string>;
  rejected: boolean;
  warnings: Array<string>;
}

export function stripDcecWhitespace(expression: string): string {
  let text = expression.trim();
  text = text.replaceAll('[', ' [').replaceAll(']', '] ');
  text = text.replaceAll(',', ' ');

  while (true) {
    const previousLength = text.length;
    text = text.replaceAll('  ', ' ').replaceAll('( ', '(').replaceAll(' )', ')');
    if (previousLength === text.length) {
      break;
    }
  }

  return text.replaceAll(')(', ') (').replaceAll(' ', ',');
}

export function stripDcecComments(expression: string): string {
  const commentIndex = expression.indexOf('#');
  return commentIndex === -1 ? expression : expression.slice(0, commentIndex);
}

export function removeDcecSemicolonComments(expression: string): string {
  const commentIndex = expression.indexOf(';');
  return commentIndex === -1 ? expression : expression.slice(0, commentIndex);
}

export function checkDcecParens(expression: string): boolean {
  let depth = 0;
  for (let index = 0; index < expression.length; index += 1) {
    const char = expression[index];
    if (char === '(') {
      depth += 1;
    } else if (char === ')') {
      depth -= 1;
      if (depth < 0) {
        return false;
      }
    }
  }
  return depth === 0;
}

export function getMatchingDcecCloseParen(input: string, openParenIndex = 0): number | undefined {
  if (openParenIndex < 0 || openParenIndex >= input.length || input[openParenIndex] !== '(') {
    return undefined;
  }

  let depth = 0;
  for (let index = openParenIndex; index < input.length; index += 1) {
    const char = input[index];
    if (char === '(') {
      depth += 1;
    } else if (char === ')') {
      depth -= 1;
      if (depth === 0) {
        return index;
      }
    }
  }

  return undefined;
}

export function consolidateDcecParens(expression: string): string {
  const text = `(${expression})`;
  const deleteIndexes = new Set<number>();
  let firstParen = 0;

  while (firstParen < text.length) {
    firstParen = text.indexOf('((', firstParen);
    if (firstParen === -1) {
      break;
    }

    const secondOpen = firstParen + 1;
    const firstClose = getMatchingDcecCloseParen(text, firstParen);
    const secondClose = getMatchingDcecCloseParen(text, secondOpen);
    if (firstClose !== undefined && secondClose !== undefined && firstClose === secondClose + 1) {
      deleteIndexes.add(firstParen);
      deleteIndexes.add(firstClose);
    }
    firstParen += 1;
  }

  let result = Array.from(text)
    .filter((_, index) => !deleteIndexes.has(index))
    .join('');
  if (result.includes(' ')) {
    const innerAtomPattern = /(?<![A-Za-z0-9_])\(([A-Za-z_][A-Za-z0-9_]*)\)(?![A-Za-z0-9_])/g;
    let previous: string | undefined;
    while (previous !== result) {
      previous = result;
      result = result.replace(innerAtomPattern, '$1');
    }
  }

  return result;
}

export function tuckDcecFunctions(expression: string): string {
  let result = '';
  let index = 0;

  while (index < expression.length) {
    const char = expression[index];
    if (isIdentifierStart(char)) {
      const nameStart = index;
      index += 1;
      while (index < expression.length && isIdentifierPart(expression[index])) {
        index += 1;
      }

      const name = expression.slice(nameStart, index);
      if (index < expression.length && expression[index] === '(') {
        const closeParen = getMatchingDcecCloseParen(expression, index);
        if (closeParen !== undefined) {
          const args = tuckFunctionArguments(expression.slice(index + 1, closeParen));
          if (name === 'not' || name === 'negate') {
            result += `(${name},(${args}))`;
          } else {
            result += `(${name},${args})`;
          }
          index = closeParen + 1;
          continue;
        }
      }

      result += name;
      continue;
    }

    result += char;
    index += 1;
  }

  return result.replaceAll('``', '`').replaceAll(',,', ',').replaceAll('`', ' ');
}

export function functorizeDcecSymbols(expression: string): string {
  let result = '';
  let index = 0;

  while (index < expression.length) {
    const symbol = DCEC_SYMBOLS.find((candidate) => expression.startsWith(candidate, index));
    if (symbol !== undefined) {
      result += ` ${SYMBOL_REPLACEMENTS[symbol]} `;
      index += symbol.length;
    } else {
      result += expression[index];
      index += 1;
    }
  }

  return result.replaceAll('( ', '(');
}

export function normalizeDcecText(expression: string): string {
  let text = expression.normalize('NFKC');
  text = removeDcecSemicolonComments(stripDcecComments(text));
  text = text
    .replace(/[“”]/g, '"')
    .replace(/[‘’]/g, "'")
    .replace(/[‐‑‒–—−]/g, '-')
    .replace(/\s+/g, ' ')
    .trim();

  for (const [from, to] of Object.entries(TOKEN_REPLACEMENTS)) {
    text = text.replaceAll(from, ` ${to} `);
  }

  return text
    .replace(/\biff\b/gi, ' ifAndOnlyIf ')
    .replace(/\bimplies\b/gi, ' implies ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function cleanupDcecTokens(expression: string): Array<string> {
  const normalized = normalizeDcecText(expression);
  if (normalized.length === 0) {
    return [];
  }

  const tokens =
    normalized.match(/[A-Za-z_][A-Za-z0-9_-]*|\d+(?:\.\d+)?|<->|->|>=|<=|==|[()[\],~^*/+=<>|-]/g) ??
    [];
  return tokens
    .map((token) => TOKEN_ALIASES[token] ?? token)
    .filter((token) => token.trim().length > 0 && token !== ',,');
}

export function cleanDcecLegalText(expression: string): DcecCleaningResult {
  const normalizedText = normalizeDcecText(expression);
  const warnings: Array<string> = [];

  if (normalizedText.length === 0) {
    return { cleaned: '', normalizedText, tokens: [], rejected: true, warnings: ['empty-input'] };
  }

  if (!checkDcecParens(normalizedText)) {
    return {
      cleaned: '',
      normalizedText,
      tokens: cleanupDcecTokens(normalizedText),
      rejected: true,
      warnings: ['unbalanced-parentheses'],
    };
  }

  const tokens = cleanupDcecTokens(normalizedText);
  const cleaned = cleanDcecExpression(renderDcecTokensForCleaning(tokens));
  if (cleaned.length === 0) {
    warnings.push('empty-cleaned-expression');
  }

  return { cleaned, normalizedText, tokens, rejected: cleaned.length === 0, warnings };
}

export function cleanDcecExpression(expression: string): string {
  const uncommented = normalizeDcecText(expression);
  if (uncommented.length === 0 || !checkDcecParens(uncommented)) {
    return '';
  }

  const functorized = functorizeDcecSymbols(uncommented);
  const tucked = tuckDcecFunctions(functorized);
  return consolidateDcecParens(stripDcecWhitespace(tucked));
}

function tuckFunctionArguments(input: string): string {
  const tucked = tuckDcecFunctions(input);
  const parts = splitTopLevelArguments(tucked);
  return parts.length === 0 ? tucked.trim() : parts.join(',');
}

function splitTopLevelArguments(input: string): Array<string> {
  const parts: Array<string> = [];
  let depth = 0;
  let start = 0;

  for (let index = 0; index < input.length; index += 1) {
    const char = input[index];
    if (char === '(') {
      depth += 1;
    } else if (char === ')') {
      depth -= 1;
    } else if (char === ',' && depth === 0) {
      parts.push(input.slice(start, index).trim());
      start = index + 1;
    }
  }

  const finalPart = input.slice(start).trim();
  if (finalPart.length > 0) {
    parts.push(finalPart);
  }
  return parts;
}

function renderDcecTokensForCleaning(tokens: Array<string>): string {
  let result = '';

  for (const token of tokens) {
    if (token === '(' || token === '[') {
      result = result.trimEnd() + token;
    } else if (token === ')' || token === ']' || token === ',') {
      result += token;
    } else {
      result += `${result.length === 0 || result.endsWith('(') || result.endsWith('[') ? '' : ' '}${token}`;
    }
  }

  return result;
}

function isIdentifierStart(value: string | undefined): boolean {
  return value !== undefined && /[A-Za-z_]/.test(value);
}

function isIdentifierPart(value: string | undefined): boolean {
  return value !== undefined && /[A-Za-z0-9_]/.test(value);
}
