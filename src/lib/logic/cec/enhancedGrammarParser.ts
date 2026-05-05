export const DcecGrammarCategory = {
  S: 'S',
  NP: 'NP',
  VP: 'VP',
  DEONTIC: 'Deontic',
  COGNITIVE: 'Cognitive',
  TEMPORAL: 'Temporal',
  AGENT: 'Agent',
  ACTION: 'Action',
  FLUENT: 'Fluent',
  N: 'N',
  V: 'V',
  ADJ: 'ADJ',
  ADV: 'ADV',
  DET: 'DET',
  MODAL: 'MODAL',
} as const;

export type DcecGrammarCategoryValue =
  (typeof DcecGrammarCategory)[keyof typeof DcecGrammarCategory];

export class DcecGrammarTerminal {
  readonly word: string;
  readonly category: DcecGrammarCategoryValue;

  constructor(word: string, category: DcecGrammarCategoryValue) {
    this.word = word;
    this.category = category;
  }

  toString(): string {
    return `${this.word}:${this.category}`;
  }

  key(): string {
    return `${this.word}:${this.category}`;
  }
}

export class DcecGrammarRule {
  readonly lhs: DcecGrammarCategoryValue;
  readonly rhs: DcecGrammarCategoryValue[];
  readonly semanticFn?: (...args: unknown[]) => unknown;

  constructor(
    lhs: DcecGrammarCategoryValue,
    rhs: DcecGrammarCategoryValue[],
    semanticFn?: (...args: unknown[]) => unknown,
  ) {
    this.lhs = lhs;
    this.rhs = [...rhs];
    this.semanticFn = semanticFn;
  }

  toString(): string {
    return `${this.lhs} -> ${this.rhs.join(' ')}`;
  }

  key(): string {
    return `${this.lhs}->${this.rhs.join(',')}`;
  }
}

export class DcecParseTree {
  readonly category: DcecGrammarCategoryValue;
  readonly children: DcecParseTree[];
  readonly terminal?: DcecGrammarTerminal;
  readonly semantics?: unknown;

  constructor(
    category: DcecGrammarCategoryValue,
    options: {
      children?: DcecParseTree[];
      terminal?: DcecGrammarTerminal;
      semantics?: unknown;
    } = {},
  ) {
    this.category = category;
    this.children = [...(options.children ?? [])];
    this.terminal = options.terminal;
    this.semantics = options.semantics;
  }

  isTerminal(): boolean {
    return this.terminal !== undefined;
  }

  toString(indent = 0): string {
    const prefix = '  '.repeat(indent);
    if (this.isTerminal()) return `${prefix}${this.category}: ${this.terminal!.word}`;
    const lines = [`${prefix}${this.category}`];
    for (const child of this.children) lines.push(child.toString(indent + 1));
    return lines.join('\n');
  }

  leaves(): string[] {
    if (this.isTerminal()) return [this.terminal!.word];
    return this.children.flatMap((child) => child.leaves());
  }
}

export class DcecEarleyState {
  readonly rule: DcecGrammarRule;
  readonly dotPos: number;
  readonly origin: number;
  readonly current: number;
  readonly tree?: DcecParseTree;
  readonly children: DcecParseTree[];

  constructor(
    rule: DcecGrammarRule,
    dotPos: number,
    origin: number,
    current: number,
    tree?: DcecParseTree,
    children: DcecParseTree[] = [],
  ) {
    this.rule = rule;
    this.dotPos = dotPos;
    this.origin = origin;
    this.current = current;
    this.tree = tree;
    this.children = [...children];
  }

  nextCategory(): DcecGrammarCategoryValue | undefined {
    return this.isComplete() ? undefined : this.rule.rhs[this.dotPos];
  }

  isComplete(): boolean {
    return this.dotPos >= this.rule.rhs.length;
  }

  advance(tree = this.tree, current = this.current): DcecEarleyState {
    const children = tree === undefined ? this.children : [...this.children, tree];
    return new DcecEarleyState(
      this.rule,
      this.dotPos + 1,
      this.origin,
      current,
      undefined,
      children,
    );
  }

  toString(): string {
    const before = this.rule.rhs.slice(0, this.dotPos).join(' ');
    const after = this.rule.rhs.slice(this.dotPos).join(' ');
    return `${this.rule.lhs} -> ${before} • ${after} (${this.origin}, ${this.current})`;
  }

  key(): string {
    const childKey = this.children.map((child) => child.toString()).join('|');
    return `${this.rule.key()}|${this.dotPos}|${this.origin}|${this.current}|${childKey}`;
  }
}

export interface DcecParseDiagnostic {
  readonly code: 'empty-input' | 'unknown-token' | 'incomplete-parse' | 'parse-complete';
  readonly message: string;
  readonly position?: number;
  readonly token?: string;
  readonly expected?: DcecGrammarCategoryValue[];
}

export interface DcecChartParserDiagnostics {
  readonly words: string[];
  readonly chartSizes: number[];
  readonly predictions: number;
  readonly scans: number;
  readonly completions: number;
  readonly diagnostics: DcecParseDiagnostic[];
}

export interface DcecParseResult {
  readonly alternatives: DcecParseTree[];
  readonly diagnostics: DcecChartParserDiagnostics;
}

export class DcecEnhancedGrammarParser {
  readonly rules: DcecGrammarRule[] = [];
  readonly lexicon = new Map<string, DcecGrammarTerminal[]>();
  startSymbol: DcecGrammarCategoryValue = DcecGrammarCategory.S;

  constructor() {
    this.initGrammar();
    this.initLexicon();
  }

  addRule(rule: DcecGrammarRule): void {
    this.rules.push(rule);
  }

  addLexicalEntry(word: string, category: DcecGrammarCategoryValue): void {
    this.addWords([word], category);
  }

  parse(sentence: string): DcecParseTree[] {
    return this.parseWithDiagnostics(sentence).alternatives;
  }

  parseWithDiagnostics(sentence: string): DcecParseResult {
    const words = sentence.toLowerCase().trim().split(/\s+/).filter(Boolean);
    const chart = Array.from(
      { length: words.length + 1 },
      () => new Map<string, DcecEarleyState>(),
    );
    const diagnostics: DcecParseDiagnostic[] = [];
    let predictions = 0;
    let scans = 0;
    let completions = 0;

    for (const rule of this.rules.filter((candidate) => candidate.lhs === this.startSymbol)) {
      this.addState(chart[0], new DcecEarleyState(rule, 0, 0, 0));
    }

    if (words.length === 0) {
      diagnostics.push({ code: 'empty-input', message: 'No input tokens were provided.' });
    }

    for (let position = 0; position <= words.length; position += 1) {
      let changed = true;
      while (changed) {
        changed = false;
        for (const state of [...chart[position].values()]) {
          const beforeSize = chart[position].size + (chart[position + 1]?.size ?? 0);
          if (state.isComplete()) completions += this.completer(chart, state, position);
          else if (this.isTerminalCategory(state.nextCategory())) {
            if (position < words.length)
              scans += this.scanner(chart, state, words[position], position);
          } else {
            predictions += this.predictor(chart, state, position);
          }
          const afterSize = chart[position].size + (chart[position + 1]?.size ?? 0);
          if (afterSize > beforeSize) changed = true;
        }
      }

      if (position < words.length && !this.lexicon.has(words[position])) {
        diagnostics.push({
          code: 'unknown-token',
          message: `No lexical entries matched token "${words[position]}".`,
          position,
          token: words[position],
          expected: this.expectedCategories(chart[position]),
        });
      }
    }

    const alternatives = [...chart[words.length].values()]
      .filter(
        (state) => state.rule.lhs === this.startSymbol && state.isComplete() && state.origin === 0,
      )
      .map((state) => this.buildTree(state))
      .filter((tree): tree is DcecParseTree => tree !== undefined);

    diagnostics.push(
      alternatives.length > 0
        ? {
            code: 'parse-complete',
            message: `${alternatives.length} parse alternative${alternatives.length === 1 ? '' : 's'} matched ${this.startSymbol}.`,
          }
        : {
            code: 'incomplete-parse',
            message: `No complete ${this.startSymbol} parse matched the full input.`,
            position: words.length,
            expected: this.expectedCategories(chart[Math.min(words.length, chart.length - 1)]),
          },
    );

    return {
      alternatives,
      diagnostics: {
        words,
        chartSizes: chart.map((cell) => cell.size),
        predictions,
        scans,
        completions,
        diagnostics,
      },
    };
  }

  validateGrammar(): [boolean, string[]] {
    const issues: string[] = [];
    if (!this.rules.some((rule) => rule.lhs === this.startSymbol)) {
      issues.push(`No rules for start symbol ${this.startSymbol}`);
    }

    const reachable = new Set<DcecGrammarCategoryValue>([this.startSymbol]);
    let changed = true;
    while (changed) {
      changed = false;
      for (const rule of this.rules) {
        if (!reachable.has(rule.lhs)) continue;
        for (const category of rule.rhs) {
          if (!reachable.has(category)) {
            reachable.add(category);
            changed = true;
          }
        }
      }
    }

    const allRuleCategories = new Set(this.rules.map((rule) => rule.lhs));
    const unreachable = [...allRuleCategories].filter((category) => !reachable.has(category));
    if (unreachable.length > 0) issues.push(`Unreachable categories: ${unreachable.join(',')}`);

    const productive = new Set<DcecGrammarCategoryValue>();
    for (const terminals of this.lexicon.values()) {
      for (const terminal of terminals) productive.add(terminal.category);
    }
    changed = true;
    while (changed) {
      changed = false;
      for (const rule of this.rules) {
        if (rule.rhs.every((category) => productive.has(category)) && !productive.has(rule.lhs)) {
          productive.add(rule.lhs);
          changed = true;
        }
      }
    }
    const unproductive = [...allRuleCategories].filter((category) => !productive.has(category));
    if (unproductive.length > 0) issues.push(`Unproductive categories: ${unproductive.join(',')}`);

    return [issues.length === 0, issues];
  }

  private predictor(
    chart: Array<Map<string, DcecEarleyState>>,
    state: DcecEarleyState,
    position: number,
  ): number {
    const next = state.nextCategory();
    if (!next) return 0;
    let added = 0;
    for (const rule of this.rules) {
      if (
        rule.lhs === next &&
        this.addState(chart[position], new DcecEarleyState(rule, 0, position, position))
      )
        added += 1;
    }
    return added;
  }

  private scanner(
    chart: Array<Map<string, DcecEarleyState>>,
    state: DcecEarleyState,
    word: string,
    position: number,
  ): number {
    const next = state.nextCategory();
    if (!next) return 0;
    let added = 0;
    for (const terminal of this.lexicon.get(word) ?? []) {
      if (terminal.category === next) {
        const tree = new DcecParseTree(next, { terminal });
        if (this.addState(chart[position + 1], state.advance(tree, position + 1))) added += 1;
      }
    }
    return added;
  }

  private completer(
    chart: Array<Map<string, DcecEarleyState>>,
    completed: DcecEarleyState,
    position: number,
  ): number {
    let added = 0;
    const completedTree = this.buildTree(completed);
    if (!completedTree) return 0;
    for (const state of [...chart[completed.origin].values()]) {
      if (state.nextCategory() === completed.rule.lhs) {
        if (this.addState(chart[position], state.advance(completedTree, position))) added += 1;
      }
    }
    return added;
  }

  private buildTree(state: DcecEarleyState): DcecParseTree | undefined {
    return state.tree ?? new DcecParseTree(state.rule.lhs, { children: state.children });
  }

  private isTerminalCategory(category?: DcecGrammarCategoryValue): boolean {
    if (!category) return false;
    return [...this.lexicon.values()].some((terminals) =>
      terminals.some((terminal) => terminal.category === category),
    );
  }

  private expectedCategories(chartCell: Map<string, DcecEarleyState>): DcecGrammarCategoryValue[] {
    return [
      ...new Set(
        [...chartCell.values()]
          .map((state) => state.nextCategory())
          .filter(Boolean) as DcecGrammarCategoryValue[],
      ),
    ].sort();
  }

  private addState(chartCell: Map<string, DcecEarleyState>, state: DcecEarleyState): boolean {
    if (chartCell.has(state.key())) return false;
    chartCell.set(state.key(), state);
    return true;
  }

  private initGrammar(): void {
    this.rules.push(
      new DcecGrammarRule(DcecGrammarCategory.S, [DcecGrammarCategory.NP, DcecGrammarCategory.VP]),
      new DcecGrammarRule(DcecGrammarCategory.S, [DcecGrammarCategory.DEONTIC]),
      new DcecGrammarRule(DcecGrammarCategory.S, [DcecGrammarCategory.COGNITIVE]),
      new DcecGrammarRule(DcecGrammarCategory.S, [DcecGrammarCategory.TEMPORAL]),
      new DcecGrammarRule(DcecGrammarCategory.NP, [DcecGrammarCategory.DET, DcecGrammarCategory.N]),
      new DcecGrammarRule(DcecGrammarCategory.NP, [DcecGrammarCategory.N]),
      new DcecGrammarRule(DcecGrammarCategory.NP, [DcecGrammarCategory.AGENT]),
      new DcecGrammarRule(DcecGrammarCategory.VP, [DcecGrammarCategory.V]),
      new DcecGrammarRule(DcecGrammarCategory.VP, [DcecGrammarCategory.V, DcecGrammarCategory.NP]),
      new DcecGrammarRule(DcecGrammarCategory.VP, [
        DcecGrammarCategory.MODAL,
        DcecGrammarCategory.V,
      ]),
      new DcecGrammarRule(DcecGrammarCategory.VP, [DcecGrammarCategory.ACTION]),
      new DcecGrammarRule(DcecGrammarCategory.DEONTIC, [
        DcecGrammarCategory.AGENT,
        DcecGrammarCategory.MODAL,
        DcecGrammarCategory.ACTION,
      ]),
      new DcecGrammarRule(DcecGrammarCategory.DEONTIC, [
        DcecGrammarCategory.MODAL,
        DcecGrammarCategory.ACTION,
      ]),
      new DcecGrammarRule(DcecGrammarCategory.COGNITIVE, [
        DcecGrammarCategory.AGENT,
        DcecGrammarCategory.V,
        DcecGrammarCategory.S,
      ]),
      new DcecGrammarRule(DcecGrammarCategory.COGNITIVE, [
        DcecGrammarCategory.AGENT,
        DcecGrammarCategory.V,
        DcecGrammarCategory.FLUENT,
      ]),
      new DcecGrammarRule(DcecGrammarCategory.TEMPORAL, [
        DcecGrammarCategory.ADV,
        DcecGrammarCategory.S,
      ]),
      new DcecGrammarRule(DcecGrammarCategory.TEMPORAL, [
        DcecGrammarCategory.ADV,
        DcecGrammarCategory.FLUENT,
      ]),
    );
  }

  private initLexicon(): void {
    this.addWords(['the', 'a', 'an'], DcecGrammarCategory.DET);
    this.addWords(['agent', 'person', 'robot', 'system'], DcecGrammarCategory.N);
    this.addWords(['alice', 'bob', 'charlie'], DcecGrammarCategory.AGENT);
    this.addWords(['run', 'walk', 'think', 'believe', 'know'], DcecGrammarCategory.V);
    this.addWords(['open', 'close', 'move', 'stop'], DcecGrammarCategory.ACTION);
    this.addWords(['must', 'should', 'may', 'can', 'must_not'], DcecGrammarCategory.MODAL);
    this.addWords(['always', 'eventually', 'never', 'sometimes'], DcecGrammarCategory.ADV);
    this.addWords(['door_open', 'light_on', 'running'], DcecGrammarCategory.FLUENT);
  }

  private addWords(words: string[], category: DcecGrammarCategoryValue): void {
    for (const word of words) {
      const terminals = this.lexicon.get(word) ?? [];
      terminals.push(new DcecGrammarTerminal(word, category));
      this.lexicon.set(word, terminals);
    }
  }
}

export function createDcecEnhancedGrammarParser(): DcecEnhancedGrammarParser {
  return new DcecEnhancedGrammarParser();
}
