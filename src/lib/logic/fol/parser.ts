import { normalizePredicateName } from '../normalization';
import { getLogicRuntimeCapabilities } from '../runtimeCapabilities';
import type { LogicValidationResult } from '../types';
import { createValidationResult } from '../validation';
import { extractBrowserNativeFolNlp, type BrowserNativeFolNlpExtraction } from './browserNativeNlp';

export interface FolTokenMatch {
  type: string;
  symbol: string;
  text: string;
  index: number;
}

export interface FolParseResult {
  formula: string;
  quantifiers: FolTokenMatch[];
  operators: FolTokenMatch[];
  validation: LogicValidationResult;
  nlp: BrowserNativeFolNlpExtraction;
  capabilities: {
    nlpUnavailable: boolean;
    browserNativeMlConfidence: boolean;
    localModelArtifactLoading: boolean;
    mlUnavailable: boolean;
    serverCallsAllowed: false;
  };
}

export interface FolParserMetadata {
  parser: 'browser-native-fol-parser';
  sourcePythonModule: 'logic/fol/utils/fol_parser.py';
  browserNative: true;
  pythonRuntime: false;
  serverCallsAllowed: false;
  runtimeDependencies: Array<string>;
}

export interface FolParserClause {
  text: string;
  formula: string;
  quantifiers: FolTokenMatch[];
  operators: FolTokenMatch[];
  validation: LogicValidationResult;
}

export interface FolUtilityParseOptions {
  splitSentences?: boolean;
  failOnInvalid?: boolean;
}

export interface FolUtilityParseResult {
  success: boolean;
  formula: string;
  clauses: Array<FolParserClause>;
  quantifiers: Array<FolTokenMatch>;
  operators: Array<FolTokenMatch>;
  validation: LogicValidationResult;
  metadata: FolParserMetadata;
  warnings: Array<string>;
}

export const FOL_PARSER_METADATA: FolParserMetadata = {
  parser: 'browser-native-fol-parser',
  sourcePythonModule: 'logic/fol/utils/fol_parser.py',
  browserNative: true,
  pythonRuntime: false,
  serverCallsAllowed: false,
  runtimeDependencies: [],
};

const UNIVERSAL_PATTERNS = [
  /\b(?:all|every|each)\s+(\w+)/gi,
  /\bno\s+(\w+)/gi,
  /\b(?:any|everything|everyone)\b/gi,
  /\bfor\s+all\s+(\w+)/gi,
];

const EXISTENTIAL_PATTERNS = [
  /\b(?:some|there (?:is|are|exists?))\s+(\w+)/gi,
  /\b(?:something|someone|at least one)\b/gi,
  /\bthere (?:is|are) (?:a|an|some)\s+(\w+)/gi,
];

const OPERATOR_PATTERNS: Array<{ type: string; symbol: string; pattern: RegExp }> = [
  { type: 'conjunction', symbol: '∧', pattern: /\band\b/gi },
  { type: 'disjunction', symbol: '∨', pattern: /\bor\b/gi },
  { type: 'implication', symbol: '→', pattern: /\bif\s+.+?\s+then\b/gi },
  { type: 'implication', symbol: '→', pattern: /\bimplies?\b/gi },
  { type: 'implication', symbol: '→', pattern: /\btherefore\b/gi },
  { type: 'negation', symbol: '¬', pattern: /\b(?:not|no|none|never|nothing)\b/gi },
];

export function parseFolText(text: string): FolParseResult {
  const normalized = text.trim();
  const nlp = extractBrowserNativeFolNlp(normalized);
  const quantifiers = parseFolQuantifiers(normalized);
  const operators = parseFolOperators(normalized);
  const formula = buildFolFormula(normalized, quantifiers, operators);
  const capabilities = getLogicRuntimeCapabilities().fol;

  return {
    formula,
    quantifiers,
    operators,
    validation: validateFolSyntax(formula),
    nlp,
    capabilities: {
      nlpUnavailable: !(capabilities.nlpStatus === 'complete' && capabilities.browserNativeNlp),
      browserNativeMlConfidence: capabilities.browserNativeMlConfidence,
      localModelArtifactLoading: capabilities.localModelArtifactLoading,
      mlUnavailable: false,
      serverCallsAllowed: false,
    },
  };
}

export function parseFolUtilityText(
  text: string,
  options: FolUtilityParseOptions = {},
): FolUtilityParseResult {
  const normalized = text.trim();
  if (!normalized) {
    const validation = validateFolSyntax('');
    return {
      success: false,
      formula: '',
      clauses: [],
      quantifiers: [],
      operators: [],
      validation,
      metadata: FOL_PARSER_METADATA,
      warnings: ['empty_input'],
    };
  }

  const clauseTexts =
    options.splitSentences === false ? [normalized] : splitFolSentences(normalized);
  const clauses = clauseTexts.map((clauseText) => {
    const quantifiers = parseFolQuantifiers(clauseText);
    const operators = parseFolOperators(clauseText);
    const formula = buildFolFormula(clauseText, quantifiers, operators);
    return {
      text: clauseText,
      formula,
      quantifiers,
      operators,
      validation: validateFolSyntax(formula),
    };
  });
  const formula = clauses.map((clause) => `(${clause.formula})`).join(' ∧ ');
  const validation = validateFolSyntax(formula);
  const invalidClauses = clauses.filter((clause) => !clause.validation.valid).length;
  const warnings = invalidClauses > 0 ? [`invalid_clause_count:${invalidClauses}`] : [];

  return {
    success: validation.valid && (!options.failOnInvalid || invalidClauses === 0),
    formula,
    clauses,
    quantifiers: parseFolQuantifiers(normalized),
    operators: parseFolOperators(normalized),
    validation,
    metadata: FOL_PARSER_METADATA,
    warnings,
  };
}

export const parse_fol_text = parseFolUtilityText;

export function parseFolQuantifiers(text: string): FolTokenMatch[] {
  const matches: FolTokenMatch[] = [];
  for (const pattern of UNIVERSAL_PATTERNS) {
    for (const match of text.matchAll(pattern)) {
      matches.push({
        type: 'universal',
        symbol: '∀',
        text: match[0],
        index: match.index ?? 0,
      });
    }
  }
  for (const pattern of EXISTENTIAL_PATTERNS) {
    for (const match of text.matchAll(pattern)) {
      matches.push({
        type: 'existential',
        symbol: '∃',
        text: match[0],
        index: match.index ?? 0,
      });
    }
  }
  return matches.sort((left, right) => left.index - right.index);
}

export function parseFolOperators(text: string): FolTokenMatch[] {
  const matches: FolTokenMatch[] = [];
  for (const { type, symbol, pattern } of OPERATOR_PATTERNS) {
    for (const match of text.matchAll(pattern)) {
      matches.push({
        type,
        symbol,
        text: match[0],
        index: match.index ?? 0,
      });
    }
  }
  return matches.sort((left, right) => left.index - right.index);
}

export function buildFolFormula(
  text: string,
  quantifiers = parseFolQuantifiers(text),
  operators = parseFolOperators(text),
): string {
  const implication = text.match(/\bif\s+(.+?)\s+then\s+(.+)$/i);
  if (implication) {
    return `∀x (${parseSimplePredicate(implication[1])} → ${parseSimplePredicate(implication[2])})`;
  }

  const allRelation = text.match(
    /\b(?:all|every|each)\s+(\w+)\s+(?:are|is|must be|shall be)\s+(\w+)/i,
  );
  if (allRelation) {
    return `∀x (${toPredicateName(allRelation[1])}(x) → ${toPredicateName(allRelation[2])}(x))`;
  }

  const noRelation = text.match(
    /\b(?:no|none)\s+(\w+)\s+(?:are|is|may be|must be|shall be)\s+(\w+)/i,
  );
  if (noRelation) {
    return `∀x (${toPredicateName(noRelation[1])}(x) → ¬${toPredicateName(noRelation[2])}(x))`;
  }

  const someRelation = text.match(/\b(?:some|there (?:is|are))\s+(\w+)\s+(?:are|is)?\s*(\w+)?/i);
  if (someRelation) {
    const subject = toPredicateName(someRelation[1]);
    const predicate = someRelation[2] ? toPredicateName(someRelation[2]) : subject;
    return `∃x (${subject}(x) ∧ ${predicate}(x))`;
  }

  const predicate = parseSimplePredicate(text);
  if (quantifiers.some((match) => match.type === 'universal')) {
    return `∀x ${predicate}`;
  }
  if (quantifiers.some((match) => match.type === 'existential')) {
    return `∃x ${predicate}`;
  }
  if (operators.some((match) => match.type === 'negation')) {
    return `¬${predicate}`;
  }
  return predicate;
}

function splitFolSentences(text: string): Array<string> {
  return text
    .split(/[.!?]+/g)
    .map((sentence) => sentence.trim())
    .filter(Boolean);
}

export function parseSimplePredicate(text: string): string {
  const words = text
    .trim()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(Boolean);
  const candidate = words.length > 1 ? words[words.length - 1] : words[0];
  return `${toPredicateName(candidate || 'P')}(x)`;
}

export function validateFolSyntax(formula: string): LogicValidationResult {
  const issues = [];
  if (!formula || typeof formula !== 'string') {
    issues.push({ severity: 'error' as const, message: 'Formula is empty or not a string' });
    return createValidationResult(issues);
  }

  let balance = 0;
  for (const char of formula) {
    if (char === '(') {
      balance += 1;
    } else if (char === ')') {
      balance -= 1;
      if (balance < 0) {
        issues.push({ severity: 'error' as const, message: 'Unmatched closing parenthesis' });
        break;
      }
    }
  }
  if (balance !== 0) {
    issues.push({ severity: 'error' as const, message: 'Unbalanced parentheses' });
  }

  if (/[∀∃]/.test(formula) && !/[∀∃][a-z]/.test(formula)) {
    issues.push({ severity: 'error' as const, message: 'Quantifier missing variable' });
  }

  if (!/[A-Z][A-Za-z0-9_]*\([^)]*\)/.test(formula) && formula !== '⊤' && formula !== '⊥') {
    issues.push({ severity: 'error' as const, message: 'No valid predicate found' });
  }

  return createValidationResult(issues);
}

function toPredicateName(value: string): string {
  return normalizePredicateName(value)
    .split('_')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join('');
}
