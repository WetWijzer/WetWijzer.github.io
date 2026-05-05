export type CecGrammarCategory =
  | 'Utterance'
  | 'Sentence'
  | 'Boolean'
  | 'Cl'
  | 'Agent'
  | 'ActionType'
  | 'Event'
  | 'Moment'
  | 'Fluent'
  | 'Class'
  | 'Dom'
  | 'Entity'
  | 'Object'
  | 'Query'
  | 'NP'
  | 'VP'
  | 'N'
  | 'V'
  | 'A'
  | 'Adv'
  | 'Prep'
  | 'Det'
  | 'Conj';

export interface CecGrammarConfig {
  version: string;
  language: string;
  caseSensitive: boolean;
  allowContractions: boolean;
  defaultTense: string;
}

export interface CecGrammarOperatorData {
  word?: string;
  words?: string[];
  category?: string;
  pattern?: string;
  patterns?: string[];
  semantics?: Record<string, unknown>;
  examples?: string[];
}

export interface CecProductionRuleData {
  pattern: string;
  example?: string;
}

export interface CecGrammarData {
  config?: Partial<CecGrammarConfig> & {
    case_sensitive?: boolean;
    allow_contractions?: boolean;
    default_tense?: string;
  };
  connectives?: Record<string, CecGrammarOperatorData>;
  deontic?: Record<string, CecGrammarOperatorData>;
  cognitive?: Record<string, CecGrammarOperatorData>;
  temporal?: Record<string, CecGrammarOperatorData>;
  quantifiers?: Record<string, CecGrammarOperatorData>;
  production_rules?: Record<string, CecProductionRuleData[]>;
}

export interface CecGrammarArtifact {
  source: 'in-memory';
  runtime: 'browser-native';
  externalResourcePolicy: 'none';
  config: CecGrammarConfig;
  sections: Record<CecGrammarOperatorSection, Record<string, CecGrammarOperatorData>>;
  productionRules: Record<string, CecProductionRuleData[]>;
  allWords: string[];
}

export type CecSemanticFunction = (semanticValues: unknown[]) => unknown;
export type CecLinearizeFunction = (semanticValue: unknown) => string;
export type CecGrammarOperatorSection =
  | 'deontic'
  | 'cognitive'
  | 'temporal'
  | 'quantifiers'
  | 'connectives';
export type CecAmbiguityStrategy = 'first' | 'shortest' | 'most_specific';

export interface CecGrammarRuleOptions {
  name: string;
  category: CecGrammarCategory;
  constituents: CecGrammarCategory[];
  semanticFn: CecSemanticFunction;
  linearizeFn?: CecLinearizeFunction;
  sourcePattern?: string;
}

export interface CecGrammarValidationIssue {
  code: string;
  message: string;
  ruleName?: string;
  word?: string;
  pattern?: string;
}

export interface CecGrammarValidationResult {
  valid: boolean;
  issues: CecGrammarValidationIssue[];
}

export interface CecGrammarSetupResult {
  lexicalEntriesAdded: number;
  rulesAdded: number;
  validation: CecGrammarValidationResult;
}

export interface CecGrammarEngineOptions {
  startCategory?: CecGrammarCategory;
  caseSensitive?: boolean;
}

export class CecGrammarRule {
  readonly name: string;
  readonly category: CecGrammarCategory;
  readonly constituents: CecGrammarCategory[];
  readonly semanticFn: CecSemanticFunction;
  readonly linearizeFn?: CecLinearizeFunction;
  readonly sourcePattern?: string;

  constructor(options: CecGrammarRuleOptions) {
    this.name = options.name;
    this.category = options.category;
    this.constituents = [...options.constituents];
    this.semanticFn = options.semanticFn;
    this.linearizeFn = options.linearizeFn;
    this.sourcePattern = options.sourcePattern;
  }

  canApply(categories: CecGrammarCategory[]): boolean {
    return (
      categories.length === this.constituents.length &&
      categories.every((category, index) => category === this.constituents[index])
    );
  }

  applySemantics(semanticValues: unknown[]): unknown {
    return this.semanticFn(semanticValues);
  }

  linearize(semanticValue: unknown): string {
    return this.linearizeFn ? this.linearizeFn(semanticValue) : String(semanticValue);
  }
}

export interface CecLexicalEntryOptions {
  word: string;
  category: CecGrammarCategory;
  semantics: unknown;
  features?: Record<string, unknown>;
}

export class CecLexicalEntry {
  readonly word: string;
  readonly category: CecGrammarCategory;
  readonly semantics: unknown;
  readonly features: Record<string, unknown>;

  constructor(options: CecLexicalEntryOptions) {
    this.word = options.word;
    this.category = options.category;
    this.semantics = options.semantics;
    this.features = options.features ? { ...options.features } : {};
  }
}

export class CecParseNode {
  constructor(
    readonly category: CecGrammarCategory,
    readonly rule: CecGrammarRule | undefined,
    readonly children: CecParseNode[],
    readonly semantics: unknown,
    readonly span: [number, number],
  ) {}

  isLexical(): boolean {
    return this.rule === undefined && this.children.length === 0;
  }

  linearize(): string {
    if (this.isLexical()) return String(this.semantics);
    if (this.rule?.linearizeFn) return this.rule.linearize(this.semantics);
    return this.children.map((child) => child.linearize()).join(' ');
  }
}

export class CecGrammarLoader {
  private readonly grammarData: CecGrammarData;
  private readonly config: CecGrammarConfig;

  constructor(grammarData: CecGrammarData = DEFAULT_CEC_GRAMMAR) {
    this.grammarData = grammarData;
    const rawConfig = grammarData.config ?? {};
    this.config = {
      version: rawConfig.version ?? '1.0',
      language: rawConfig.language ?? 'en',
      caseSensitive: rawConfig.caseSensitive ?? rawConfig.case_sensitive ?? false,
      allowContractions: rawConfig.allowContractions ?? rawConfig.allow_contractions ?? true,
      defaultTense: rawConfig.defaultTense ?? rawConfig.default_tense ?? 'present',
    };
  }

  getConfig(): CecGrammarConfig {
    return { ...this.config };
  }

  getConnectives(): Record<string, CecGrammarOperatorData> {
    return this.grammarData.connectives ?? {};
  }

  getDeonticRules(): Record<string, CecGrammarOperatorData> {
    return this.grammarData.deontic ?? {};
  }

  getCognitiveRules(): Record<string, CecGrammarOperatorData> {
    return this.grammarData.cognitive ?? {};
  }

  getTemporalRules(): Record<string, CecGrammarOperatorData> {
    return this.grammarData.temporal ?? {};
  }

  getQuantifiers(): Record<string, CecGrammarOperatorData> {
    return this.grammarData.quantifiers ?? {};
  }

  getProductionRules(): Record<string, CecProductionRuleData[]> {
    return this.grammarData.production_rules ?? {};
  }

  getWordsForOperator(operatorType: CecGrammarOperatorSection, operatorName: string): string[] {
    const operatorData = this.grammarData[operatorType]?.[operatorName];
    if (!operatorData) return [];
    if (operatorData.words) return [...operatorData.words];
    if (operatorData.word !== undefined) return [operatorData.word];
    return [];
  }

  getSemantics(operatorType: keyof CecGrammarData, operatorName: string): Record<string, unknown> {
    const section = this.grammarData[operatorType];
    if (!section || Array.isArray(section)) return {};
    return (section as Record<string, CecGrammarOperatorData>)[operatorName]?.semantics ?? {};
  }

  getExamples(operatorType: keyof CecGrammarData, operatorName: string): string[] {
    const section = this.grammarData[operatorType];
    if (!section || Array.isArray(section)) return [];
    return (section as Record<string, CecGrammarOperatorData>)[operatorName]?.examples ?? [];
  }

  validate(): boolean {
    return this.validateDetailed().valid;
  }

  getAllWords(): string[] {
    const words: string[] = [];
    for (const connective of Object.values(this.getConnectives())) {
      if (connective.word) words.push(connective.word);
      if (connective.words) words.push(...connective.words);
    }
    for (const section of [
      this.getDeonticRules(),
      this.getCognitiveRules(),
      this.getTemporalRules(),
      this.getQuantifiers(),
    ]) {
      for (const operator of Object.values(section)) {
        if (operator.words) words.push(...operator.words);
        else if (operator.word) words.push(operator.word);
      }
    }
    return words;
  }

  getArtifact(): CecGrammarArtifact {
    return {
      source: 'in-memory',
      runtime: 'browser-native',
      externalResourcePolicy: 'none',
      config: this.getConfig(),
      sections: {
        connectives: cloneOperatorSection(this.getConnectives()),
        deontic: cloneOperatorSection(this.getDeonticRules()),
        cognitive: cloneOperatorSection(this.getCognitiveRules()),
        temporal: cloneOperatorSection(this.getTemporalRules()),
        quantifiers: cloneOperatorSection(this.getQuantifiers()),
      },
      productionRules: cloneProductionRules(this.getProductionRules()),
      allWords: this.getAllWords(),
    };
  }

  validateDetailed(): CecGrammarValidationResult {
    const issues: CecGrammarValidationIssue[] = [];
    if (this.config.version.trim().length === 0) {
      issues.push({
        code: 'missing-config-version',
        message: 'CEC grammar config must include a non-empty version.',
      });
    }
    if (this.config.language.trim().length === 0) {
      issues.push({
        code: 'missing-config-language',
        message: 'CEC grammar config must include a non-empty language.',
      });
    }

    for (const section of REQUIRED_OPERATOR_SECTIONS) {
      if (!(section in this.grammarData)) {
        issues.push({
          code: 'missing-section',
          message: `CEC grammar is missing required ${section} section.`,
          ruleName: section,
        });
        continue;
      }
      const seenWords = new Set<string>();
      for (const [operatorName, operator] of Object.entries(this.grammarData[section] ?? {})) {
        const words = operator.words ?? (operator.word !== undefined ? [operator.word] : []);
        const patterns = operator.patterns ?? (operator.pattern ? [operator.pattern] : []);
        if (words.length === 0 && patterns.length === 0) {
          issues.push({
            code: 'missing-operator-surface',
            message: `Operator ${section}.${operatorName} must define words or patterns.`,
            ruleName: `${section}.${operatorName}`,
          });
        }
        for (const word of words) {
          const normalized = this.config.caseSensitive ? word : word.toLowerCase();
          if (word.trim().length === 0) {
            issues.push({
              code: 'empty-operator-word',
              message: `Operator ${section}.${operatorName} contains an empty word.`,
              ruleName: `${section}.${operatorName}`,
              word,
            });
          } else if (seenWords.has(normalized)) {
            issues.push({
              code: 'duplicate-operator-word',
              message: `Operator section ${section} contains duplicate word ${word}.`,
              ruleName: `${section}.${operatorName}`,
              word,
            });
          }
          seenWords.add(normalized);
        }
      }
    }

    for (const [groupName, rules] of Object.entries(this.getProductionRules())) {
      for (let index = 0; index < rules.length; index += 1) {
        const production = rules[index];
        if (production.pattern.trim().length === 0) {
          issues.push({
            code: 'empty-production-pattern',
            message: `Production ${groupName}.${index} must include a non-empty pattern.`,
            ruleName: `${groupName}.${index}`,
          });
        }
      }
    }

    return { valid: issues.length === 0, issues };
  }
}

export class CecGrammarEngine {
  readonly rules: CecGrammarRule[] = [];
  readonly lexicon = new Map<string, CecLexicalEntry[]>();
  readonly unsupportedProductionPatterns: CecGrammarValidationIssue[] = [];
  startCategory: CecGrammarCategory = 'Utterance';
  private readonly caseSensitive: boolean;
  private maxLexicalTokenLength = 1;

  constructor(options: CecGrammarEngineOptions = {}) {
    this.startCategory = options.startCategory ?? 'Utterance';
    this.caseSensitive = options.caseSensitive ?? false;
  }

  addRule(rule: CecGrammarRule): void {
    this.rules.push(rule);
  }

  addLexicalEntry(entry: CecLexicalEntry): void {
    const key = this.normalizeToken(entry.word);
    const entries = this.lexicon.get(key) ?? [];
    entries.push(entry);
    this.lexicon.set(key, entries);
    this.maxLexicalTokenLength = Math.max(
      this.maxLexicalTokenLength,
      key.split(/\s+/).filter(Boolean).length,
    );
  }

  addLexicalEntries(entries: Array<CecLexicalEntry | CecLexicalEntryOptions>): void {
    for (const entry of entries) {
      this.addLexicalEntry(entry instanceof CecLexicalEntry ? entry : new CecLexicalEntry(entry));
    }
  }

  addRules(rules: Array<CecGrammarRule | CecGrammarRuleOptions>): void {
    for (const rule of rules) {
      this.addRule(rule instanceof CecGrammarRule ? rule : new CecGrammarRule(rule));
    }
  }

  setupFromLoader(
    loader: CecGrammarLoader = createDefaultCecGrammarLoader(),
  ): CecGrammarSetupResult {
    let lexicalEntriesAdded = 0;
    let rulesAdded = 0;
    lexicalEntriesAdded += this.addOperatorEntries(
      'connectives',
      loader.getConnectives(),
      () => 'Conj',
    );
    lexicalEntriesAdded += this.addOperatorEntries('deontic', loader.getDeonticRules(), () => 'V');
    lexicalEntriesAdded += this.addOperatorEntries(
      'cognitive',
      loader.getCognitiveRules(),
      () => 'V',
    );
    lexicalEntriesAdded += this.addOperatorEntries(
      'temporal',
      loader.getTemporalRules(),
      (operator) => (operator.category === 'PREPOSITION' ? 'Prep' : 'Adv'),
    );
    lexicalEntriesAdded += this.addOperatorEntries(
      'quantifiers',
      loader.getQuantifiers(),
      () => 'Det',
    );

    const defaultRules: CecGrammarRuleOptions[] = [
      {
        name: 'CecPythonDeonticUtterance',
        category: 'Utterance',
        constituents: ['Agent', 'V', 'ActionType'],
        semanticFn: ([agent, modality, action]) => ({
          type: 'deontic',
          agent,
          modality: operatorName(modality),
          action,
        }),
      },
      {
        name: 'CecPythonCognitiveUtterance',
        category: 'Utterance',
        constituents: ['Agent', 'V', 'Fluent'],
        semanticFn: ([agent, operator, proposition]) => ({
          type: 'cognitive',
          agent,
          operator: operatorName(operator),
          proposition,
        }),
      },
      {
        name: 'CecPythonTemporalUtterance',
        category: 'Utterance',
        constituents: ['Adv', 'Utterance'],
        semanticFn: ([temporal, proposition]) => ({
          type: 'temporal',
          operator: operatorName(temporal),
          proposition,
        }),
      },
      {
        name: 'CecPythonCompoundUtterance',
        category: 'Utterance',
        constituents: ['Utterance', 'Conj', 'Utterance'],
        semanticFn: ([left, connective, right]) => ({
          type: 'compound',
          connective: operatorName(connective),
          left,
          right,
        }),
      },
      {
        name: 'CecPythonQuantifiedEntity',
        category: 'Entity',
        constituents: ['Det', 'N'],
        semanticFn: ([quantifier, noun]) => ({
          type: 'quantified_entity',
          quantifier: operatorName(quantifier),
          noun,
        }),
      },
      {
        name: 'CecPythonEntityUtterance',
        category: 'Utterance',
        constituents: ['Entity'],
        semanticFn: ([entity]) => entity,
      },
    ];

    for (const rule of defaultRules) {
      if (this.rules.some((candidate) => candidate.name === rule.name)) continue;
      this.addRule(new CecGrammarRule(rule));
      rulesAdded += 1;
    }
    const compiled = this.addProductionRules(loader.getProductionRules());
    rulesAdded += compiled.added;
    this.unsupportedProductionPatterns.push(...compiled.unsupported);

    return { lexicalEntriesAdded, rulesAdded, validation: this.validateGrammar() };
  }

  parse(text: string): CecParseNode[] {
    const tokens = this.tokenize(text);
    const count = tokens.length;
    if (count === 0) return [];
    const chart: CecParseNode[][][] = Array.from({ length: count + 1 }, () =>
      Array.from({ length: count + 1 }, () => []),
    );

    tokens.forEach((token, index) => {
      for (const entry of this.lexicon.get(token) ?? []) {
        chart[index][index + 1].push(
          new CecParseNode(entry.category, undefined, [], entry.semantics, [index, index + 1]),
        );
      }
      this.closeUnaryCell(chart[index][index + 1], index, index + 1);
    });

    for (let length = 1; length <= count; length += 1) {
      for (let start = 0; start <= count - length; start += 1) {
        const end = start + length;
        this.closeUnaryCell(chart[start][end], start, end);
        for (const rule of this.rules.filter((candidate) => candidate.constituents.length >= 2)) {
          for (const children of this.findRuleChildren(rule, start, end, chart)) {
            const node = new CecParseNode(
              rule.category,
              rule,
              children,
              rule.applySemantics(children.map((child) => child.semantics)),
              [start, end],
            );
            if (!hasEquivalentParse(chart[start][end], node)) {
              chart[start][end].push(node);
              this.closeUnaryCell(chart[start][end], start, end);
            }
          }
        }
      }
    }

    return chart[0][count].filter((node) => node.category === this.startCategory);
  }

  validateGrammar(): CecGrammarValidationResult {
    const issues: CecGrammarValidationIssue[] = [];
    const lexicalCategories = new Set<CecGrammarCategory>();
    for (const entries of this.lexicon.values()) {
      for (const entry of entries) {
        if (entry.word.trim().length === 0) {
          issues.push({
            code: 'empty-lexical-word',
            message: 'Lexical entries must have a non-empty word.',
            word: entry.word,
          });
        }
        lexicalCategories.add(entry.category);
      }
    }

    const reachableCategories = new Set<CecGrammarCategory>(lexicalCategories);
    let changed = true;
    while (changed) {
      changed = false;
      for (const rule of this.rules) {
        if (rule.constituents.length === 0) continue;
        if (reachableCategories.has(rule.category)) continue;
        if (rule.constituents.every((category) => reachableCategories.has(category))) {
          reachableCategories.add(rule.category);
          changed = true;
        }
      }
    }

    for (const rule of this.rules) {
      if (rule.name.trim().length === 0) {
        issues.push({
          code: 'empty-rule-name',
          message: 'Grammar rules must have a non-empty name.',
        });
      }
      if (rule.constituents.length === 0) {
        issues.push({
          code: 'empty-constituents',
          message: 'Grammar rules must consume at least one constituent.',
          ruleName: rule.name,
        });
      }
      const missing = rule.constituents.filter((category) => !reachableCategories.has(category));
      if (missing.length > 0) {
        issues.push({
          code: 'unreachable-constituent',
          message: `Rule ${rule.name} references unavailable constituent categories: ${missing.join(', ')}`,
          ruleName: rule.name,
        });
      }
    }
    if (!reachableCategories.has(this.startCategory)) {
      issues.push({
        code: 'unreachable-start-category',
        message: `Start category ${this.startCategory} is not derivable from the current lexicon and rules.`,
      });
    }

    return { valid: issues.length === 0, issues };
  }

  private addProductionRules(productions: Record<string, CecProductionRuleData[]>): {
    added: number;
    unsupported: CecGrammarValidationIssue[];
  } {
    let added = 0;
    const unsupported: CecGrammarValidationIssue[] = [];
    for (const [groupName, rules] of Object.entries(productions)) {
      for (let index = 0; index < rules.length; index += 1) {
        const production = rules[index];
        const compiled = compileProductionPattern(groupName, index, production.pattern);
        if (!compiled) {
          unsupported.push({
            code: 'unsupported-production-pattern',
            message: `Production pattern ${production.pattern} is not supported by the browser-native grammar engine.`,
            ruleName: `${groupName}.${index}`,
            pattern: production.pattern,
          });
          continue;
        }
        if (this.rules.some((candidate) => candidate.name === compiled.name)) continue;
        this.addRule(
          new CecGrammarRule({
            name: compiled.name,
            category: compiled.category,
            constituents: compiled.constituents,
            sourcePattern: production.pattern,
            semanticFn: (values) => ({
              type: 'production',
              group: groupName,
              pattern: production.pattern,
              values,
            }),
          }),
        );
        added += 1;
      }
    }
    return { added, unsupported };
  }

  private addOperatorEntries(
    section: CecGrammarOperatorSection,
    operators: Record<string, CecGrammarOperatorData>,
    categoryFor: (operator: CecGrammarOperatorData) => CecGrammarCategory,
  ): number {
    let added = 0;
    for (const [name, operator] of Object.entries(operators)) {
      const words = operator.words ?? (operator.word !== undefined ? [operator.word] : []);
      for (const word of words) {
        const entry = new CecLexicalEntry({
          word,
          category: categoryFor(operator),
          semantics: { ...(operator.semantics ?? {}), section, name, word },
          features: { section, name },
        });
        const key = this.normalizeToken(word);
        const duplicate = (this.lexicon.get(key) ?? []).some(
          (candidate) =>
            candidate.category === entry.category &&
            JSON.stringify(candidate.semantics) === JSON.stringify(entry.semantics),
        );
        if (duplicate) continue;
        this.addLexicalEntry(entry);
        added += 1;
      }
    }
    return added;
  }

  private closeUnaryCell(cell: CecParseNode[], start: number, end: number): void {
    let changed = true;
    while (changed) {
      changed = false;
      for (const rule of this.rules.filter((candidate) => candidate.constituents.length === 1)) {
        for (const child of [...cell]) {
          if (!rule.canApply([child.category])) continue;
          const semantics = rule.applySemantics([child.semantics]);
          const node = new CecParseNode(rule.category, rule, [child], semantics, [start, end]);
          if (!hasEquivalentParse(cell, node)) {
            cell.push(node);
            changed = true;
          }
        }
      }
    }
  }

  private findRuleChildren(
    rule: CecGrammarRule,
    start: number,
    end: number,
    chart: CecParseNode[][][],
  ): Array<CecParseNode[]> {
    const collect = (constituentIndex: number, offset: number): Array<CecParseNode[]> => {
      if (constituentIndex === rule.constituents.length) {
        return offset === end ? [[]] : [];
      }
      const expectedCategory = rule.constituents[constituentIndex];
      const remaining = rule.constituents.length - constituentIndex - 1;
      const sequences: Array<CecParseNode[]> = [];
      for (let nextEnd = offset + 1; nextEnd <= end - remaining; nextEnd += 1) {
        for (const node of chart[offset][nextEnd]) {
          if (node.category !== expectedCategory) continue;
          for (const suffix of collect(constituentIndex + 1, nextEnd)) {
            sequences.push([node, ...suffix]);
          }
        }
      }
      return sequences;
    };

    return collect(0, start);
  }

  linearize(semanticValue: unknown, category: CecGrammarCategory): string {
    for (const rule of this.rules) {
      if (rule.category !== category || !rule.linearizeFn) continue;
      try {
        return rule.linearizeFn(semanticValue);
      } catch {
        // Try the next rule, mirroring the Python engine's fallback behavior.
      }
    }
    return String(semanticValue);
  }

  resolveAmbiguity(
    parses: CecParseNode[],
    strategy: CecAmbiguityStrategy = 'first',
  ): CecParseNode | undefined {
    if (parses.length === 0) return undefined;
    if (strategy === 'shortest') return minParseNodeBy(parses, countParseNodes);
    if (strategy === 'most_specific') return maxParseNodeBy(parses, specificityScore);
    return parses[0];
  }

  protected tokenize(text: string): string[] {
    const rawTokens = text
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map((token) => this.normalizeToken(token));
    const tokens: string[] = [];
    let index = 0;
    while (index < rawTokens.length) {
      let matched = '';
      const maxWidth = Math.min(this.maxLexicalTokenLength, rawTokens.length - index);
      for (let width = maxWidth; width >= 1; width -= 1) {
        const candidate = rawTokens.slice(index, index + width).join(' ');
        if (this.lexicon.has(candidate)) {
          matched = candidate;
          break;
        }
      }
      if (matched.length > 0) {
        tokens.push(matched);
        index += matched.split(/\s+/).filter(Boolean).length;
      } else {
        tokens.push(rawTokens[index]);
        index += 1;
      }
    }
    return tokens;
  }

  private normalizeToken(token: string): string {
    return this.caseSensitive ? token : token.toLowerCase();
  }
}

export function createDefaultCecGrammarLoader(): CecGrammarLoader {
  return new CecGrammarLoader(DEFAULT_CEC_GRAMMAR);
}

export function createDefaultCecGrammarEngine(): CecGrammarEngine {
  const loader = createDefaultCecGrammarLoader();
  const engine = new CecGrammarEngine({ caseSensitive: loader.getConfig().caseSensitive });
  engine.setupFromLoader(loader);
  return engine;
}

function hasEquivalentParse(nodes: CecParseNode[], candidate: CecParseNode): boolean {
  return nodes.some(
    (node) =>
      node.category === candidate.category &&
      node.span[0] === candidate.span[0] &&
      node.span[1] === candidate.span[1] &&
      JSON.stringify(node.semantics) === JSON.stringify(candidate.semantics),
  );
}

function operatorName(value: unknown): unknown {
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    if (typeof record.operator === 'string') return record.operator;
    if (typeof record.connective === 'string') return record.connective;
    if (typeof record.name === 'string') return record.name;
  }
  return value;
}

function countParseNodes(node: CecParseNode): number {
  return 1 + node.children.reduce((total, child) => total + countParseNodes(child), 0);
}

function specificityScore(node: CecParseNode): number {
  if (node.isLexical()) {
    const scores: Partial<Record<CecGrammarCategory, number>> = {
      Agent: 5,
      ActionType: 4,
      Fluent: 3,
      N: 2,
      V: 2,
    };
    return scores[node.category] ?? 1;
  }
  return node.children.reduce((total, child) => total + specificityScore(child), 0);
}

function minParseNodeBy(
  items: CecParseNode[],
  scorer: (item: CecParseNode) => number,
): CecParseNode {
  return items.reduce((best, item) => (scorer(item) < scorer(best) ? item : best));
}

function maxParseNodeBy(
  items: CecParseNode[],
  scorer: (item: CecParseNode) => number,
): CecParseNode {
  return items.reduce((best, item) => (scorer(item) > scorer(best) ? item : best));
}

interface CompiledProductionPattern {
  name: string;
  category: CecGrammarCategory;
  constituents: CecGrammarCategory[];
}

const PRODUCTION_CATEGORY_MAP: Record<string, CecGrammarCategory> = {
  subject: 'Agent',
  agent: 'Agent',
  modal: 'V',
  verb: 'ActionType',
  object: 'Object',
  sentence: 'Utterance',
  connective: 'Conj',
};

const PRODUCTION_RESULT_CATEGORY: Record<string, CecGrammarCategory> = {
  sentence: 'Utterance',
  compound: 'Utterance',
};

const REQUIRED_OPERATOR_SECTIONS: CecGrammarOperatorSection[] = [
  'connectives',
  'deontic',
  'cognitive',
  'temporal',
  'quantifiers',
];

function cloneOperatorSection(
  section: Record<string, CecGrammarOperatorData>,
): Record<string, CecGrammarOperatorData> {
  const clone: Record<string, CecGrammarOperatorData> = {};
  for (const [name, operator] of Object.entries(section)) {
    clone[name] = {
      ...operator,
      words: operator.words ? [...operator.words] : undefined,
      patterns: operator.patterns ? [...operator.patterns] : undefined,
      semantics: operator.semantics ? { ...operator.semantics } : undefined,
      examples: operator.examples ? [...operator.examples] : undefined,
    };
  }
  return clone;
}

function cloneProductionRules(
  productionRules: Record<string, CecProductionRuleData[]>,
): Record<string, CecProductionRuleData[]> {
  const clone: Record<string, CecProductionRuleData[]> = {};
  for (const [groupName, rules] of Object.entries(productionRules)) {
    clone[groupName] = rules.map((rule) => ({ ...rule }));
  }
  return clone;
}

function compileProductionPattern(
  groupName: string,
  index: number,
  pattern: string,
): CompiledProductionPattern | undefined {
  const matches = [...pattern.matchAll(/\{([a-z_]+)\}/g)];
  if (matches.length === 0) return undefined;
  const rebuilt = matches.map((match) => match[0]).join(' ');
  if (rebuilt !== pattern.trim()) return undefined;
  const constituents: CecGrammarCategory[] = [];
  for (const match of matches) {
    const category = PRODUCTION_CATEGORY_MAP[match[1]];
    if (!category) return undefined;
    constituents.push(category);
  }
  const category = PRODUCTION_RESULT_CATEGORY[groupName];
  if (!category) return undefined;
  return {
    name: `CecPythonProduction:${groupName}:${index}`,
    category,
    constituents,
  };
}

export const DEFAULT_CEC_GRAMMAR: CecGrammarData = {
  connectives: {
    and: {
      word: 'and',
      category: 'CONJUNCTION',
      semantics: { type: 'and', connective: 'AND' },
      examples: ['Alice loves Bob and Carol'],
    },
    or: {
      word: 'or',
      category: 'CONJUNCTION',
      semantics: { type: 'or', connective: 'OR' },
      examples: ['Alice or Bob will go'],
    },
    not: {
      word: 'not',
      category: 'ADVERB',
      semantics: { type: 'not', connective: 'NOT' },
      examples: ['It is not raining'],
    },
    if_then: {
      patterns: ['if {P} then {Q}', '{P} implies {Q}'],
      semantics: { type: 'implies', connective: 'IMPLIES' },
    },
  },
  deontic: {
    obligation: {
      words: ['must', 'obligated', 'should', 'required'],
      category: 'VERB',
      semantics: { type: 'deontic', operator: 'obligated' },
    },
    permission: {
      words: ['may', 'permitted', 'allowed', 'can'],
      category: 'VERB',
      semantics: { type: 'deontic', operator: 'permitted' },
    },
    prohibition: {
      words: ['forbidden', 'prohibited', 'must not'],
      category: 'VERB',
      semantics: { type: 'deontic', operator: 'forbidden' },
    },
  },
  cognitive: {
    belief: {
      words: ['believes', 'think', 'assume'],
      category: 'VERB',
      semantics: { type: 'cognitive', operator: 'belief' },
    },
    knowledge: {
      words: ['knows', 'aware'],
      category: 'VERB',
      semantics: { type: 'cognitive', operator: 'knowledge' },
    },
    intention: {
      words: ['intends', 'plans', 'wants'],
      category: 'VERB',
      semantics: { type: 'cognitive', operator: 'intention' },
    },
    desire: {
      words: ['desires', 'wishes', 'hopes'],
      category: 'VERB',
      semantics: { type: 'cognitive', operator: 'desire' },
    },
  },
  temporal: {
    always: {
      words: ['always', 'necessarily', 'invariably'],
      category: 'ADVERB',
      semantics: { type: 'temporal', operator: 'always' },
    },
    eventually: {
      words: ['eventually', 'sometime', 'ultimately'],
      category: 'ADVERB',
      semantics: { type: 'temporal', operator: 'eventually' },
    },
    next: {
      words: ['next', 'immediately'],
      category: 'ADVERB',
      semantics: { type: 'temporal', operator: 'next' },
    },
    until: {
      words: ['until'],
      category: 'PREPOSITION',
      semantics: { type: 'temporal', operator: 'until' },
    },
  },
  quantifiers: {
    universal: {
      words: ['all', 'every', 'each'],
      category: 'DETERMINER',
      semantics: { type: 'quantifier', operator: 'forall' },
    },
    existential: {
      words: ['some', 'a', 'an', 'exists'],
      category: 'DETERMINER',
      semantics: { type: 'quantifier', operator: 'exists' },
    },
  },
  production_rules: {
    sentence: [
      { pattern: '{subject} {verb} {object}', example: 'Alice loves Bob' },
      { pattern: '{agent} {modal} {verb} {object}', example: 'Alice must go home' },
    ],
    compound: [
      { pattern: '{sentence} {connective} {sentence}', example: 'Alice goes and Bob stays' },
      {
        pattern: 'if {condition} then {consequence}',
        example: 'if it rains then the ground is wet',
      },
    ],
  },
  config: {
    version: '1.0',
    language: 'en',
    caseSensitive: false,
    allowContractions: true,
    defaultTense: 'present',
  },
};
