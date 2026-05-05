export type DcecParseArg = string | DcecParseToken;

export class DcecParseToken {
  readonly funcName: string;
  readonly args: DcecParseArg[];

  private depth?: number;
  private width?: number;
  private sExpression?: string;
  private fExpression?: string;

  constructor(funcName: string, args: DcecParseArg[]) {
    this.funcName = funcName;
    this.args = args;
  }

  depthOf(): number {
    if (this.depth !== undefined) return this.depth;
    const childDepths = this.args.filter(isDcecParseToken).map((arg) => arg.depthOf());
    this.depth = childDepths.length === 0 ? 1 : 1 + Math.max(...childDepths);
    return this.depth;
  }

  widthOf(): number {
    if (this.width !== undefined) return this.width;
    this.width = this.args.reduce(
      (sum, arg) => sum + (isDcecParseToken(arg) ? arg.widthOf() : 1),
      0,
    );
    return this.width;
  }

  createSExpression(): string {
    if (this.sExpression !== undefined) return this.sExpression;
    const args = this.args.map((arg) => (isDcecParseToken(arg) ? arg.createSExpression() : arg));
    this.sExpression = `(${[this.funcName, ...args].join(' ')})`;
    return this.sExpression;
  }

  createFExpression(): string {
    if (this.fExpression !== undefined) return this.fExpression;
    const args = this.args.map((arg) => (isDcecParseToken(arg) ? arg.createFExpression() : arg));
    this.fExpression = `${this.funcName}(${args.join(',')})`;
    return this.fExpression;
  }

  toString(): string {
    return this.createFExpression();
  }
}

export interface DcecPrefixOptions {
  atomics?: Record<string, string[]>;
}

export type DcecParseFormKind =
  | 'atom'
  | 'connective'
  | 'quantifier'
  | 'modal'
  | 'deontic'
  | 'unknown';

export interface DcecParsedForm {
  readonly kind: DcecParseFormKind;
  readonly token: DcecParseToken;
  readonly operator?: string;
  readonly predicate?: string;
  readonly variable?: string;
  readonly sort?: string;
  readonly arguments: readonly DcecParseArg[];
  readonly body?: DcecParseArg;
}

export const DCEC_PARSING_METADATA = {
  sourcePythonModule: 'logic/CEC/native/dcec_parsing.py',
  runtime: 'browser-native-typescript',
  browserNative: true,
  pythonRuntime: false,
  serverRuntime: false,
  supportedOperations: [
    'parse-token-rendering',
    'remove-comments',
    'functorize-symbols',
    'replace-synonyms',
    'prefix-logical-functions',
    'prefix-emdas',
    'form-classification',
  ],
} as const;

const DCEC_SYNONYMS: Record<string, string> = {
  ifAndOnlyIf: 'iff',
  if: 'implies',
  Time: 'Moment',
  forall: 'forAll',
  Forall: 'forAll',
  ForAll: 'forAll',
  Exists: 'exists',
};

const LOGICAL_KEYWORDS = ['not', 'and', 'or', 'xor', 'implies', 'iff'];
const ARITHMETIC_KEYWORDS = ['negate', 'exponent', 'multiply', 'divide', 'add', 'sub'];
const QUANTIFIER_ALIASES: Record<string, string> = {
  all: 'forAll',
  forall: 'forAll',
  forAll: 'forAll',
  ForAll: 'forAll',
  exists: 'exists',
  Exists: 'exists',
  exist: 'exists',
};
const MODAL_ALIASES: Record<string, string> = {
  B: 'B',
  belief: 'B',
  believes: 'B',
  K: 'K',
  knowledge: 'K',
  knows: 'K',
  I: 'I',
  intention: 'I',
  intends: 'I',
  D: 'D',
  desire: 'D',
  G: 'G',
  goal: 'G',
};
const DEONTIC_ALIASES: Record<string, string> = {
  O: 'O',
  obligation: 'O',
  obligatory: 'O',
  P: 'P',
  permission: 'P',
  permitted: 'P',
  F: 'F',
  prohibition: 'F',
  forbidden: 'F',
  S: 'S',
  supererogation: 'S',
  R: 'R',
  right: 'R',
  L: 'L',
  liberty: 'L',
};
const SYMBOL_REPLACEMENTS_IN_PYTHON_ORDER: Array<readonly [string, string]> = [
  ['^', 'exponent'],
  ['*', '*'],
  ['/', 'divide'],
  ['+', 'add'],
  ['<->', 'ifAndOnlyIf'],
  ['->', 'implies'],
  ['-', '-'],
  ['&', '&'],
  ['|', '|'],
  ['~', 'not'],
  ['>=', 'greaterOrEqual'],
  ['==', 'equals'],
  ['<=', 'lessOrEqual'],
  ['===', 'tautology'],
  ['=', 'equals'],
  ['>', 'greater'],
  ['<', 'less'],
];

export function isDcecParseToken(arg: DcecParseArg): arg is DcecParseToken {
  return arg instanceof DcecParseToken;
}

export function removeDcecParsingComments(expression: string): string {
  const index = expression.indexOf(';');
  return index === -1 ? expression : expression.slice(0, index);
}

export function functorizeDcecParsingSymbols(expression: string): string {
  let result = expression;
  for (const [symbol, replacement] of SYMBOL_REPLACEMENTS_IN_PYTHON_ORDER) {
    result = result.split(symbol).join(` ${replacement} `);
  }
  return result.split('( ').join('(');
}

export function replaceDcecSynonymsInPlace(args: DcecParseArg[]): void {
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (typeof arg === 'string') {
      args[index] = DCEC_SYNONYMS[arg] ?? arg;
    }
  }
}

export function replaceDcecSynonyms(args: DcecParseArg[]): DcecParseArg[] {
  return args.map((arg) => {
    if (typeof arg === 'string') {
      return DCEC_SYNONYMS[arg] ?? arg;
    }
    return new DcecParseToken(arg.funcName, replaceDcecSynonyms(arg.args));
  });
}

export function prefixDcecLogicalFunctions(
  args: DcecParseArg[],
  options: DcecPrefixOptions = {},
): DcecParseArg[] {
  return prefixDcecFunctions(args, LOGICAL_KEYWORDS, 'Boolean', options.atomics);
}

export function prefixDcecEmdas(
  args: DcecParseArg[],
  options: DcecPrefixOptions = {},
): DcecParseArg[] {
  return prefixDcecFunctions(args, ARITHMETIC_KEYWORDS, 'Numeric', options.atomics);
}

export function createDcecAtom(predicate: string, args: DcecParseArg[] = []): DcecParseToken {
  return new DcecParseToken(stripDcecTokenName(predicate), args);
}

export function createDcecConnective(operator: string, args: DcecParseArg[]): DcecParseToken {
  const normalized = normalizeDcecConnective(operator);
  return new DcecParseToken(normalized ?? operator, args);
}

export function createDcecQuantifier(
  quantifier: string,
  variable: string,
  body: DcecParseArg,
  sort = 'Entity',
): DcecParseToken {
  return new DcecParseToken(normalizeDcecQuantifier(quantifier) ?? quantifier, [
    stripDcecTokenName(variable),
    stripDcecTokenName(sort),
    body,
  ]);
}

export function createDcecModalForm(
  operator: string,
  agent: DcecParseArg,
  body: DcecParseArg,
): DcecParseToken {
  return new DcecParseToken(normalizeDcecModalOperator(operator) ?? operator, [agent, body]);
}

export function createDcecDeonticForm(
  operator: string,
  body: DcecParseArg,
  agent?: DcecParseArg,
): DcecParseToken {
  return new DcecParseToken(
    normalizeDcecDeonticOperator(operator) ?? operator,
    agent === undefined ? [body] : [agent, body],
  );
}

export function classifyDcecParseForm(token: DcecParseToken): DcecParsedForm {
  const connective = normalizeDcecConnective(token.funcName);
  if (connective) {
    return { kind: 'connective', token, operator: connective, arguments: token.args };
  }

  const quantifier = normalizeDcecQuantifier(token.funcName);
  if (quantifier) {
    const [variable, sortOrBody, maybeBody] = token.args;
    return {
      kind: 'quantifier',
      token,
      operator: quantifier,
      variable: typeof variable === 'string' ? stripDcecTokenName(variable) : undefined,
      sort: typeof maybeBody === 'undefined' ? undefined : String(sortOrBody),
      body: maybeBody ?? sortOrBody,
      arguments: token.args,
    };
  }

  const modal = normalizeDcecModalOperator(token.funcName);
  if (modal)
    return {
      kind: 'modal',
      token,
      operator: modal,
      body: token.args.at(-1),
      arguments: token.args,
    };

  const deontic = normalizeDcecDeonticOperator(token.funcName);
  if (deontic)
    return {
      kind: 'deontic',
      token,
      operator: deontic,
      body: token.args.at(-1),
      arguments: token.args,
    };

  if (/^[A-Za-z_][\w-]*$/.test(token.funcName)) {
    return { kind: 'atom', token, predicate: token.funcName, arguments: token.args };
  }
  return { kind: 'unknown', token, arguments: token.args };
}

function prefixDcecFunctions(
  inputArgs: DcecParseArg[],
  keywords: string[],
  atomicSort: string,
  atomics: Record<string, string[]> = {},
): DcecParseArg[] {
  let args = [...inputArgs];
  const [unaryKeyword] = keywords;

  if (args.length === 2 && args[0] === unaryKeyword) {
    const operand = args[1];
    if (typeof operand === 'string' && !keywords.includes(operand)) {
      addAtomicSort(atomics, operand, atomicSort);
      return [new DcecParseToken(unaryKeyword, [operand])];
    }
  }

  if (args.length < 3) return args;
  if (typeof args.at(-2) !== 'string' || !keywords.includes(args.at(-2) as string)) return args;

  for (const keyword of keywords) {
    while (args.includes(keyword)) {
      const index = args.indexOf(keyword);

      if (keyword === unaryKeyword) {
        const operand = args[index + 1];
        const token = new DcecParseToken(keyword, [operand]);
        if (typeof operand === 'string') {
          addAtomicSort(atomics, operand, atomicSort);
        }
        args = [...args.slice(0, index + 1), ...args.slice(index + 2)];
        args[index] = token;
        break;
      }

      const leftIndex = index - 1;
      const rightIndex = index + 1;
      if (leftIndex < 0) break;

      const left = args[leftIndex];
      const right = args[rightIndex];
      const token = new DcecParseToken(keyword, [left, right]);
      if (typeof left === 'string') addAtomicSort(atomics, left, atomicSort);
      if (typeof right === 'string') addAtomicSort(atomics, right, atomicSort);

      args = [...args.slice(0, leftIndex), ...args.slice(rightIndex)];
      args[leftIndex] = token;
    }
  }

  return args;
}

function addAtomicSort(atomics: Record<string, string[]>, name: string, sort: string) {
  if (atomics[name]) {
    atomics[name].push(sort);
  } else {
    atomics[name] = [sort];
  }
}

function normalizeDcecConnective(operator: string): string | undefined {
  const normalized = DCEC_SYNONYMS[operator] ?? operator;
  return LOGICAL_KEYWORDS.includes(normalized) ? normalized : undefined;
}

function normalizeDcecQuantifier(operator: string): string | undefined {
  return QUANTIFIER_ALIASES[operator] ?? QUANTIFIER_ALIASES[operator.toLowerCase()];
}

function normalizeDcecModalOperator(operator: string): string | undefined {
  return MODAL_ALIASES[operator] ?? MODAL_ALIASES[operator.toLowerCase()];
}

function normalizeDcecDeonticOperator(operator: string): string | undefined {
  return DEONTIC_ALIASES[operator] ?? DEONTIC_ALIASES[operator.toLowerCase()];
}

function stripDcecTokenName(value: string): string {
  return value.trim().replace(/^\(+|\)+$/g, '');
}
