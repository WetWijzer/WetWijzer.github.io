import type { TdfolFormula } from './ast';
import { formatTdfolFormula } from './formatter';

export type TdfolModalLogicType = 'K' | 'T' | 'D' | 'S4' | 'S5';
export type TdfolCountermodelFormat = 'ascii' | 'dot' | 'json' | 'html' | 'compact-ascii';
export type TdfolCountermodelDemoFormat = TdfolCountermodelFormat | 'snapshot';

export interface TdfolCountermodelRenderOptions {
  includeDataScript?: boolean;
  includeLegend?: boolean;
  includeProperties?: boolean;
  includeValuation?: boolean;
}

export interface TdfolCountermodelWorldSnapshot {
  id: string;
  label: string;
  atoms: string[];
  is_initial: boolean;
  world_id: number;
}

export interface TdfolCountermodelRelationSnapshot {
  source: string;
  target: string;
  from: number;
  to: number;
}

export interface TdfolCountermodelVisualizerSnapshot {
  nodes: TdfolCountermodelWorldSnapshot[];
  links: TdfolCountermodelRelationSnapshot[];
  logic_type: TdfolModalLogicType;
  initial_world: number;
  num_worlds: number;
  num_relations: number;
  property_checks: { reflexive: boolean; symmetric: boolean; transitive: boolean; serial: boolean };
  expected_properties: string[];
}

export interface TdfolCountermodelDemoScenario {
  id: string;
  title: string;
  description: string;
  formula: string;
  logic_type: TdfolModalLogicType;
  countermodel: TdfolKripkeStructureJson;
  snapshot: TdfolCountermodelVisualizerSnapshot;
  rendered: Partial<Record<TdfolCountermodelDemoFormat, string>>;
}

export interface TdfolCountermodelDemoOptions {
  formats?: TdfolCountermodelDemoFormat[];
}

export interface TdfolTableauxWorldLike {
  id: number;
  formulas: TdfolFormula[];
  negatedFormulas?: TdfolFormula[];
}

export interface TdfolTableauxBranchLike {
  isClosed?: boolean;
  worlds: Record<number, TdfolTableauxWorldLike> | Map<number, TdfolTableauxWorldLike>;
  accessibility: Record<number, number[]> | Map<number, Iterable<number>>;
}

export interface TdfolKripkeStructureJson {
  worlds: number[];
  accessibility: Record<string, number[]>;
  valuation: Record<string, string[]>;
  initial_world: number;
  logic_type: TdfolModalLogicType;
}

export interface TdfolTableauxBranchExport {
  is_closed: boolean;
  worlds: Array<{
    id: number;
    formulas: string[];
    negated_formulas: string[];
  }>;
  accessibility: Array<{
    from: number;
    to: number;
    source: string;
    target: string;
  }>;
}

export interface TdfolTableauxCountermodelExport {
  formula: string;
  logic_type: TdfolModalLogicType;
  is_valid: false;
  proof_steps: string[];
  open_branch: TdfolTableauxBranchExport;
  countermodel: TdfolKripkeStructureJson;
  visualization: TdfolCountermodelVisualizerSnapshot;
  explanation: string[];
}

export class TdfolKripkeStructure {
  readonly worlds = new Set<number>();
  readonly accessibility = new Map<number, Set<number>>();
  readonly valuation = new Map<number, Set<string>>();
  initialWorld: number;
  logicType: TdfolModalLogicType;

  constructor(options: { initialWorld?: number; logicType?: TdfolModalLogicType } = {}) {
    this.initialWorld = options.initialWorld ?? 0;
    this.logicType = options.logicType ?? 'K';
  }

  addWorld(worldId: number): void {
    this.worlds.add(worldId);
    this.accessibility.set(worldId, this.accessibility.get(worldId) ?? new Set());
    this.valuation.set(worldId, this.valuation.get(worldId) ?? new Set());
  }

  addAccessibility(fromWorld: number, toWorld: number): void {
    this.addWorld(fromWorld);
    this.addWorld(toWorld);
    this.accessibility.get(fromWorld)?.add(toWorld);
  }

  setAtomTrue(worldId: number, atom: string): void {
    this.addWorld(worldId);
    this.valuation.get(worldId)?.add(atom);
  }

  isAtomTrue(worldId: number, atom: string): boolean {
    return this.valuation.get(worldId)?.has(atom) ?? false;
  }

  getAccessibleWorlds(worldId: number): Set<number> {
    return new Set(this.accessibility.get(worldId) ?? []);
  }

  toDict(): TdfolKripkeStructureJson {
    return {
      worlds: [...this.worlds].sort((left, right) => left - right),
      accessibility: Object.fromEntries(
        [...this.accessibility.entries()]
          .sort(([left], [right]) => left - right)
          .map(([world, targets]) => [
            String(world),
            [...targets].sort((left, right) => left - right),
          ]),
      ),
      valuation: Object.fromEntries(
        [...this.valuation.entries()]
          .sort(([left], [right]) => left - right)
          .map(([world, atoms]) => [String(world), [...atoms].sort()]),
      ),
      initial_world: this.initialWorld,
      logic_type: this.logicType,
    };
  }

  toJson(indent = 2): string {
    return JSON.stringify(this.toDict(), null, indent);
  }
}

export class TdfolCounterModel {
  readonly formula: TdfolFormula;
  readonly kripke: TdfolKripkeStructure;
  readonly explanation: string[];

  constructor(formula: TdfolFormula, kripke: TdfolKripkeStructure, explanation: string[] = []) {
    this.formula = formula;
    this.kripke = kripke;
    this.explanation = explanation;
  }

  toString(): string {
    const lines = [
      `Countermodel for: ${formatTdfolFormula(this.formula)}`,
      `Logic: ${this.kripke.logicType}`,
      `Worlds: ${this.sortedWorlds()
        .map((world) => `w${world}`)
        .join(', ')}`,
      `Initial: w${this.kripke.initialWorld}`,
      '',
      'Valuation (true atoms):',
    ];

    for (const worldId of this.sortedWorlds()) {
      const atoms = this.sortedAtoms(worldId);
      lines.push(`  w${worldId}: ${atoms.length > 0 ? atoms.join(', ') : '(none)'}`);
    }

    lines.push('', 'Accessibility:');
    for (const worldId of this.sortedWorlds()) {
      const targets = [...this.kripke.getAccessibleWorlds(worldId)].sort(
        (left, right) => left - right,
      );
      if (targets.length > 0) {
        lines.push(`  w${worldId} -> ${targets.map((target) => `w${target}`).join(', ')}`);
      }
    }

    if (this.explanation.length > 0) {
      lines.push('', 'Explanation:', ...this.explanation.map((line) => `  ${line}`));
    }
    return lines.join('\n');
  }

  toAsciiArt(): string {
    const lines = [`Countermodel for: ${formatTdfolFormula(this.formula)}`, ''];
    for (const worldId of this.sortedWorlds()) {
      const atoms = this.sortedAtoms(worldId);
      const prefix = worldId === this.kripke.initialWorld ? '-> ' : '   ';
      lines.push(`${prefix}w${worldId}: {${atoms.length > 0 ? atoms.join(', ') : '∅'}}`);
      for (const target of [...this.kripke.getAccessibleWorlds(worldId)].sort(
        (left, right) => left - right,
      )) {
        lines.push(`   |-> w${target}`);
      }
    }
    return lines.join('\n');
  }

  toDot(): string {
    const lines = [
      'digraph Countermodel {',
      `  label="Countermodel for ${escapeDot(formatTdfolFormula(this.formula))}";`,
      '  labelloc="t";',
      '  node [shape=circle];',
      '',
    ];

    for (const worldId of this.sortedWorlds()) {
      const atomLabel = this.sortedAtoms(worldId).join('\\n') || '∅';
      const style =
        worldId === this.kripke.initialWorld ? ', style=filled, fillcolor=lightblue' : '';
      lines.push(`  w${worldId} [label="w${worldId}\\n${escapeDot(atomLabel)}"${style}];`);
    }

    lines.push('');
    for (const worldId of this.sortedWorlds()) {
      for (const target of [...this.kripke.getAccessibleWorlds(worldId)].sort(
        (left, right) => left - right,
      )) {
        lines.push(`  w${worldId} -> w${target};`);
      }
    }

    lines.push('}');
    return lines.join('\n');
  }

  toJson(indent = 2): string {
    return JSON.stringify(
      {
        formula: formatTdfolFormula(this.formula),
        kripke_structure: this.kripke.toDict(),
        explanation: this.explanation,
      },
      null,
      indent,
    );
  }

  private sortedWorlds(): number[] {
    return [...this.kripke.worlds].sort((left, right) => left - right);
  }

  private sortedAtoms(worldId: number): string[] {
    return [...(this.kripke.valuation.get(worldId) ?? [])].sort();
  }
}

export class TdfolCounterModelExtractor {
  readonly logicType: TdfolModalLogicType;

  constructor(logicType: TdfolModalLogicType = 'K') {
    this.logicType = logicType;
  }

  extract(formula: TdfolFormula, branch: TdfolTableauxBranchLike): TdfolCounterModel {
    if (branch.isClosed) {
      throw new Error('Cannot extract countermodel from closed branch');
    }

    const kripke = new TdfolKripkeStructure({ logicType: this.logicType });
    for (const [worldId, world] of normalizeWorldEntries(branch.worlds)) {
      kripke.addWorld(worldId);
      for (const atom of extractPositiveAtoms(world.formulas)) {
        kripke.setAtomTrue(worldId, atom);
      }
    }
    for (const [fromWorld, targets] of normalizeAccessibilityEntries(branch.accessibility)) {
      for (const target of targets) {
        kripke.addAccessibility(fromWorld, target);
      }
    }

    return new TdfolCounterModel(formula, kripke, this.generateExplanation(formula, kripke));
  }

  private generateExplanation(formula: TdfolFormula, kripke: TdfolKripkeStructure): string[] {
    const initialAtoms = [...(kripke.valuation.get(kripke.initialWorld) ?? [])].sort();
    const relations = [...kripke.accessibility.values()].reduce(
      (sum, targets) => sum + targets.size,
      0,
    );
    const lines = [
      `Formula '${formatTdfolFormula(formula)}' is not ${this.logicType}-valid`,
      `Countermodel has ${kripke.worlds.size} world(s)`,
      initialAtoms.length > 0
        ? `At initial world w${kripke.initialWorld}: ${initialAtoms.join(', ')} are true`
        : `At initial world w${kripke.initialWorld}: no atoms are true`,
      `Total accessibility relations: ${relations}`,
    ];

    const expected = expectedModalProperties(this.logicType);
    if (expected.length > 0) {
      lines.push(`${this.logicType} logic expects: ${expected.join(', ')}`);
    }
    return lines;
  }
}

export class TdfolCounterModelVisualizer {
  readonly kripke: TdfolKripkeStructure;

  constructor(kripke: TdfolKripkeStructure) {
    this.kripke = kripke;
  }

  renderAsciiEnhanced(style: 'expanded' | 'compact' = 'expanded'): string {
    return style === 'compact' ? this.renderCompactAscii() : this.renderExpandedAscii();
  }

  renderCompactAscii(): string {
    const relationCount = [...this.kripke.accessibility.values()].reduce(
      (sum, targets) => sum + targets.size,
      0,
    );
    const lines = [
      `Kripke(${this.kripke.logicType}) W=${this.kripke.worlds.size} R=${relationCount}`,
      '--------------------------------------------------',
    ];
    for (const worldId of [...this.kripke.worlds].sort((left, right) => left - right)) {
      const atoms = [...(this.kripke.valuation.get(worldId) ?? [])].sort().join(',') || '∅';
      const targets =
        [...this.kripke.getAccessibleWorlds(worldId)]
          .sort((left, right) => left - right)
          .map((target) => `w${target}`)
          .join(',') || '∅';
      lines.push(
        `${worldId === this.kripke.initialWorld ? '=>' : '*'} w${worldId}: {${atoms}} -> {${targets}}`,
      );
    }
    return lines.join('\n');
  }

  renderExpandedAscii(): string {
    const relationCount = [...this.kripke.accessibility.values()].reduce(
      (sum, targets) => sum + targets.size,
      0,
    );
    const header = `Kripke Structure (Logic: ${this.kripke.logicType})`;
    const info = `Worlds: ${this.kripke.worlds.size}, Relations: ${relationCount}`;
    const width = Math.max(header.length, info.length) + 4;
    const lines = [
      `+${'-'.repeat(width - 2)}+`,
      `| ${header.padEnd(width - 3)}|`,
      `| ${info.padEnd(width - 3)}|`,
      `+${'-'.repeat(width - 2)}+`,
      '',
    ];

    for (const worldId of [...this.kripke.worlds].sort((left, right) => left - right)) {
      const atoms = [...(this.kripke.valuation.get(worldId) ?? [])].sort();
      const targets = [...this.kripke.getAccessibleWorlds(worldId)].sort(
        (left, right) => left - right,
      );
      lines.push(
        `${worldId === this.kripke.initialWorld ? '->' : '  '} World w${worldId}${worldId === this.kripke.initialWorld ? ' (initial)' : ''}`,
      );
      lines.push(`| Atoms: ${atoms.length > 0 ? atoms.join(', ') : '∅ (none)'}`);
      lines.push(
        `| Accessible: ${targets.length > 0 ? targets.map((target) => `w${target}`).join(', ') : '(none)'}`,
      );
      lines.push('+----------------------------------------+');
    }

    lines.push('', this.renderLogicProperties());
    return lines.join('\n');
  }

  renderLogicProperties(): string {
    const checks = this.getPropertyChecks();
    const lines = [
      `Modal Logic Properties (${this.kripke.logicType}):`,
      `  ${checks.reflexive ? '✓' : '✗'} Reflexive: ${checks.reflexive}`,
      `  ${checks.symmetric ? '✓' : '✗'} Symmetric: ${checks.symmetric}`,
      `  ${checks.transitive ? '✓' : '✗'} Transitive: ${checks.transitive}`,
      `  ${checks.serial ? '✓' : '✗'} Serial: ${checks.serial}`,
    ];
    const expected = expectedModalProperties(this.kripke.logicType);
    if (expected.length > 0) {
      lines.push('', `Expected for ${this.kripke.logicType}: ${expected.join(', ')}`);
    }
    return lines.join('\n');
  }

  getPropertyChecks(): {
    reflexive: boolean;
    symmetric: boolean;
    transitive: boolean;
    serial: boolean;
  } {
    return {
      reflexive: this.isReflexive(),
      symmetric: this.isSymmetric(),
      transitive: this.isTransitive(),
      serial: this.isSerial(),
    };
  }

  toDataSnapshot(
    options: TdfolCountermodelRenderOptions = {},
  ): TdfolCountermodelVisualizerSnapshot {
    const includeValuation = options.includeValuation ?? true;
    const nodes = [...this.kripke.worlds]
      .sort((left, right) => left - right)
      .map((worldId) => ({
        id: `w${worldId}`,
        label: `w${worldId}`,
        atoms: includeValuation ? [...(this.kripke.valuation.get(worldId) ?? [])].sort() : [],
        is_initial: worldId === this.kripke.initialWorld,
        world_id: worldId,
      }));
    const links = [...this.kripke.accessibility.entries()]
      .sort(([left], [right]) => left - right)
      .flatMap(([from, targets]) =>
        [...targets]
          .sort((left, right) => left - right)
          .map((to) => ({ source: `w${from}`, target: `w${to}`, from, to })),
      );
    return {
      nodes,
      links,
      logic_type: this.kripke.logicType,
      initial_world: this.kripke.initialWorld,
      num_worlds: nodes.length,
      num_relations: links.length,
      property_checks: this.getPropertyChecks(),
      expected_properties: expectedModalProperties(this.kripke.logicType),
    };
  }

  toHtmlString(options: TdfolCountermodelRenderOptions = {}): string {
    const includeDataScript = options.includeDataScript ?? true;
    const includeLegend = options.includeLegend ?? true;
    const includeProperties = options.includeProperties ?? true;
    const data = this.toDataSnapshot(options);
    const dataScript = includeDataScript
      ? `<script type="application/json" id="kripke-data">${escapeHtml(JSON.stringify(data))}</script>`
      : '';
    const properties = includeProperties
      ? `<section class="properties"><h2>Modal Properties</h2><pre>${escapeHtml(this.renderLogicProperties())}</pre></section>`
      : '';
    const legend = includeLegend
      ? '<aside class="legend"><strong>Legend</strong><div>Highlighted world: initial evaluation point</div><div>Arrows: accessibility relation</div></aside>'
      : '';
    return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Kripke Structure - ${escapeHtml(this.kripke.logicType)}</title><style>body{font-family:system-ui,sans-serif;margin:24px}.world{border:1px solid #999;border-radius:6px;padding:8px;margin:8px 0}.initial{border-color:#0a7;background:#eefaf4}.edge{color:#555}.legend{border-left:4px solid #888;padding-left:12px}.properties pre{white-space:pre-wrap}</style></head><body><h1>Kripke Structure (${escapeHtml(this.kripke.logicType)})</h1>${dataScript}${legend}${data.nodes.map((node) => `<section class="world${node.is_initial ? ' initial' : ''}"><strong>${escapeHtml(node.label)}</strong><div>Atoms: ${escapeHtml(node.atoms.join(', ') || '∅')}</div></section>`).join('')}<h2>Accessibility</h2>${data.links.map((link) => `<div class="edge">${escapeHtml(link.source)} -> ${escapeHtml(link.target)}</div>`).join('') || '<div class="edge">(none)</div>'}${properties}</body></html>`;
  }

  private isReflexive(): boolean {
    return [...this.kripke.worlds].every((world) =>
      this.kripke.getAccessibleWorlds(world).has(world),
    );
  }

  private isSymmetric(): boolean {
    return [...this.kripke.worlds].every((from) =>
      [...this.kripke.getAccessibleWorlds(from)].every((to) =>
        this.kripke.getAccessibleWorlds(to).has(from),
      ),
    );
  }

  private isTransitive(): boolean {
    return [...this.kripke.worlds].every((first) =>
      [...this.kripke.getAccessibleWorlds(first)].every((second) =>
        [...this.kripke.getAccessibleWorlds(second)].every((third) =>
          this.kripke.getAccessibleWorlds(first).has(third),
        ),
      ),
    );
  }

  private isSerial(): boolean {
    return [...this.kripke.worlds].every(
      (world) => this.kripke.getAccessibleWorlds(world).size > 0,
    );
  }
}

export function extractTdfolCountermodel(
  formula: TdfolFormula,
  branch: TdfolTableauxBranchLike,
  logicType: TdfolModalLogicType = 'K',
): TdfolCounterModel {
  return new TdfolCounterModelExtractor(logicType).extract(formula, branch);
}

export function visualizeTdfolCountermodel(
  countermodel: TdfolCounterModel,
  format: TdfolCountermodelFormat = 'ascii',
): string {
  if (format === 'ascii') return countermodel.toAsciiArt();
  if (format === 'dot') return countermodel.toDot();
  if (format === 'json') return countermodel.toJson();
  const visualizer = new TdfolCounterModelVisualizer(countermodel.kripke);
  if (format === 'html') return visualizer.toHtmlString();
  if (format === 'compact-ascii') return visualizer.renderAsciiEnhanced('compact');
  throw new Error(`Unsupported countermodel format: ${format}`);
}

export function createTdfolCountermodelVisualizerDemo(
  options: TdfolCountermodelDemoOptions = {},
): TdfolCountermodelDemoScenario[] {
  const formats = options.formats ?? ['compact-ascii', 'json', 'html', 'snapshot'];
  return buildDemoCountermodels().map(({ id, title, description, countermodel }) => {
    const visualizer = new TdfolCounterModelVisualizer(countermodel.kripke);
    const snapshot = visualizer.toDataSnapshot();
    const rendered = Object.fromEntries(
      formats.map((format): [TdfolCountermodelDemoFormat, string] => [
        format,
        format === 'snapshot'
          ? JSON.stringify(snapshot, null, 2)
          : visualizeTdfolCountermodel(countermodel, format),
      ]),
    ) as Partial<Record<TdfolCountermodelDemoFormat, string>>;

    return {
      id,
      title,
      description,
      formula: formatTdfolFormula(countermodel.formula),
      logic_type: countermodel.kripke.logicType,
      countermodel: countermodel.kripke.toDict(),
      snapshot,
      rendered,
    };
  });
}

export function exportTdfolTableauxCountermodelData(
  formula: TdfolFormula,
  branch: TdfolTableauxBranchLike,
  logicType: TdfolModalLogicType = 'K',
  proofSteps: string[] = [],
): TdfolTableauxCountermodelExport {
  const countermodel = extractTdfolCountermodel(formula, branch, logicType);
  const visualizer = new TdfolCounterModelVisualizer(countermodel.kripke);
  return {
    formula: formatTdfolFormula(formula),
    logic_type: logicType,
    is_valid: false,
    proof_steps: [...proofSteps],
    open_branch: serializeTdfolBranch(branch),
    countermodel: countermodel.kripke.toDict(),
    visualization: visualizer.toDataSnapshot(),
    explanation: [...countermodel.explanation],
  };
}

function buildDemoCountermodels(): Array<{
  id: string;
  title: string;
  description: string;
  countermodel: TdfolCounterModel;
}> {
  const tCounterexample = new TdfolKripkeStructure({ logicType: 'T' });
  tCounterexample.addAccessibility(0, 1);
  tCounterexample.setAtomTrue(1, 'Compliant(a)');

  const dWitness = new TdfolKripkeStructure({ logicType: 'D' });
  dWitness.addAccessibility(0, 1);
  dWitness.addAccessibility(1, 1);
  dWitness.setAtomTrue(1, 'Permitted(a)');

  return [
    {
      id: 'non-reflexive-t-countermodel',
      title: 'T countermodel for necessary implication',
      description:
        'A non-reflexive initial world demonstrates why box Compliant(a) does not force Compliant(a) outside reflexive frames.',
      countermodel: new TdfolCounterModel(
        makeUnaryFormula('ALWAYS', makePredicateFormula('Compliant', 'a')),
        tCounterexample,
        ['w0 reaches w1, but w0 is not reflexive and Compliant(a) is false at w0.'],
      ),
    },
    {
      id: 'serial-d-visualization',
      title: 'D serial countermodel visualization',
      description:
        'A serial frame shows the visualizer legend, property checks, valuation, and accessibility export used by browser demos.',
      countermodel: new TdfolCounterModel(
        makeUnaryFormula('EVENTUALLY', makePredicateFormula('Permitted', 'a')),
        dWitness,
        [
          'Every world has at least one successor, so the D serial property is visible in the snapshot.',
        ],
      ),
    },
  ];
}

function extractPositiveAtoms(formulas: TdfolFormula[]): Set<string> {
  const atoms = new Set<string>();
  for (const formula of formulas) {
    if (formula.kind === 'predicate') {
      atoms.add(formatTdfolFormula(formula));
    }
  }
  return atoms;
}

function normalizeWorldEntries(
  worlds: TdfolTableauxBranchLike['worlds'],
): Array<[number, TdfolTableauxWorldLike]> {
  return isMapLike(worlds)
    ? [...worlds.entries()].sort(([left], [right]) => left - right)
    : Object.entries(worlds)
        .map(([key, value]): [number, TdfolTableauxWorldLike] => [Number(key), value])
        .sort(([left], [right]) => left - right);
}

function normalizeAccessibilityEntries(
  accessibility: TdfolTableauxBranchLike['accessibility'],
): Array<[number, number[]]> {
  return isMapLike(accessibility)
    ? [...accessibility.entries()]
        .map(([key, value]): [number, number[]] => [key, [...value]])
        .sort(([left], [right]) => left - right)
    : Object.entries(accessibility)
        .map(([key, value]): [number, number[]] => [Number(key), value])
        .sort(([left], [right]) => left - right);
}

function serializeTdfolBranch(branch: TdfolTableauxBranchLike): TdfolTableauxBranchExport {
  const worlds = normalizeWorldEntries(branch.worlds).map(([worldId, world]) => ({
    id: worldId,
    formulas: world.formulas.map((formula) => formatTdfolFormula(formula)).sort(),
    negated_formulas: (world.negatedFormulas ?? [])
      .map((formula) => formatTdfolFormula(formula))
      .sort(),
  }));
  const accessibility = normalizeAccessibilityEntries(branch.accessibility).flatMap(
    ([from, targets]) =>
      [...targets]
        .sort((left, right) => left - right)
        .map((to) => ({ from, to, source: `w${from}`, target: `w${to}` })),
  );
  return { is_closed: branch.isClosed ?? false, worlds, accessibility };
}

function isMapLike<Key, Value>(value: unknown): value is Map<Key, Value> {
  return Object.prototype.toString.call(value) === '[object Map]';
}

function expectedModalProperties(logicType: TdfolModalLogicType): string[] {
  if (logicType === 'T') return ['Reflexive'];
  if (logicType === 'D') return ['Serial'];
  if (logicType === 'S4') return ['Reflexive', 'Transitive'];
  if (logicType === 'S5') return ['Reflexive', 'Symmetric', 'Transitive'];
  return [];
}

function escapeDot(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function makePredicateFormula(name: string, constantName: string): TdfolFormula {
  return {
    kind: 'predicate',
    name,
    args: [{ kind: 'constant', name: constantName }],
  };
}

function makeUnaryFormula(
  operator: 'ALWAYS' | 'EVENTUALLY' | 'NEXT',
  formula: TdfolFormula,
): TdfolFormula {
  return { kind: 'temporal', operator, formula };
}
