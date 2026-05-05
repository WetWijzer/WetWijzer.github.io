import type { CecExpression } from './ast';
import { formatCecExpression } from './formatter';
import type { CecModalLogicType } from './modalTableaux';

export type CecCountermodelFormat = 'ascii' | 'dot' | 'json' | 'html' | 'compact-ascii';

export interface CecCountermodelWorldSnapshot {
  id: string;
  label: string;
  atoms: string[];
  is_initial: boolean;
  world_id: number;
}

export interface CecCountermodelRelationSnapshot {
  source: string;
  target: string;
  from: number;
  to: number;
}

export interface CecCountermodelVisualizerSnapshot {
  nodes: CecCountermodelWorldSnapshot[];
  links: CecCountermodelRelationSnapshot[];
  logic_type: CecModalLogicType;
  initial_world: number;
  num_worlds: number;
  num_relations: number;
  property_checks: { reflexive: boolean; symmetric: boolean; transitive: boolean; serial: boolean };
  expected_properties: string[];
}

export interface CecTableauxWorldLike {
  id: number;
  formulas: CecExpression[];
  negatedFormulas?: CecExpression[];
}

export interface CecTableauxBranchLike {
  isClosed?: boolean;
  worlds: Record<number, CecTableauxWorldLike> | Map<number, CecTableauxWorldLike>;
  accessibility: Record<number, number[]> | Map<number, Iterable<number>>;
}

export interface CecKripkeStructureJson {
  worlds: number[];
  accessibility: Record<string, number[]>;
  valuation: Record<string, string[]>;
  initial_world: number;
  logic_type: CecModalLogicType;
}

export interface CecTableauxBranchExport {
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

export interface CecTableauxCountermodelExport {
  formula: string;
  logic_type: CecModalLogicType;
  is_valid: false;
  proof_steps: string[];
  open_branch: CecTableauxBranchExport;
  countermodel: CecKripkeStructureJson;
  visualization: CecCountermodelVisualizerSnapshot;
  explanation: string[];
}

export class CecKripkeStructure {
  readonly worlds = new Set<number>();
  readonly accessibility = new Map<number, Set<number>>();
  readonly valuation = new Map<number, Set<string>>();
  initialWorld: number;
  logicType: CecModalLogicType;

  constructor(options: { initialWorld?: number; logicType?: CecModalLogicType } = {}) {
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

  toDict(): CecKripkeStructureJson {
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

export class CecCounterModel {
  readonly formula: CecExpression;
  readonly kripke: CecKripkeStructure;
  readonly explanation: string[];

  constructor(formula: CecExpression, kripke: CecKripkeStructure, explanation: string[] = []) {
    this.formula = formula;
    this.kripke = kripke;
    this.explanation = explanation;
  }

  toString(): string {
    const lines = [
      `CEC countermodel for: ${formatCecExpression(this.formula)}`,
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
      if (targets.length > 0)
        lines.push(`  w${worldId} -> ${targets.map((target) => `w${target}`).join(', ')}`);
    }

    if (this.explanation.length > 0) {
      lines.push('', 'Explanation:', ...this.explanation.map((line) => `  ${line}`));
    }
    return lines.join('\n');
  }

  toAsciiArt(): string {
    const lines = [`CEC countermodel for: ${formatCecExpression(this.formula)}`, ''];
    for (const worldId of this.sortedWorlds()) {
      const atoms = this.sortedAtoms(worldId);
      const prefix = worldId === this.kripke.initialWorld ? '-> ' : '   ';
      lines.push(`${prefix}w${worldId}: {${atoms.length > 0 ? atoms.join(', ') : 'none'}}`);
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
      'digraph CecCountermodel {',
      `  label="CEC countermodel for ${escapeDot(formatCecExpression(this.formula))}";`,
      '  labelloc="t";',
      '  node [shape=circle];',
      '',
    ];

    for (const worldId of this.sortedWorlds()) {
      const atomLabel = this.sortedAtoms(worldId).join('\\n') || 'none';
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
        formula: formatCecExpression(this.formula),
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

export class CecCounterModelExtractor {
  readonly logicType: CecModalLogicType;

  constructor(logicType: CecModalLogicType = 'K') {
    this.logicType = logicType;
  }

  extract(formula: CecExpression, branch: CecTableauxBranchLike): CecCounterModel {
    if (branch.isClosed) throw new Error('Cannot extract CEC countermodel from closed branch');

    const kripke = new CecKripkeStructure({ logicType: this.logicType });
    for (const [worldId, world] of normalizeWorldEntries(branch.worlds)) {
      kripke.addWorld(worldId);
      for (const atom of extractPositiveAtoms(world.formulas)) {
        kripke.setAtomTrue(worldId, atom);
      }
    }
    for (const [fromWorld, targets] of normalizeAccessibilityEntries(branch.accessibility)) {
      for (const target of targets) kripke.addAccessibility(fromWorld, target);
    }

    return new CecCounterModel(formula, kripke, this.generateExplanation(formula, kripke));
  }

  private generateExplanation(formula: CecExpression, kripke: CecKripkeStructure): string[] {
    const initialAtoms = [...(kripke.valuation.get(kripke.initialWorld) ?? [])].sort();
    const relations = [...kripke.accessibility.values()].reduce(
      (sum, targets) => sum + targets.size,
      0,
    );
    const lines = [
      `CEC formula '${formatCecExpression(formula)}' is not ${this.logicType}-valid`,
      `Countermodel has ${kripke.worlds.size} world(s)`,
      initialAtoms.length > 0
        ? `At initial world w${kripke.initialWorld}: ${initialAtoms.join(', ')} are true`
        : `At initial world w${kripke.initialWorld}: no atoms are true`,
      `Total accessibility relations: ${relations}`,
    ];

    const expected = expectedModalProperties(this.logicType);
    if (expected.length > 0) lines.push(`${this.logicType} logic expects: ${expected.join(', ')}`);
    return lines;
  }
}

export class CecCounterModelVisualizer {
  readonly kripke: CecKripkeStructure;

  constructor(kripke: CecKripkeStructure) {
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
      `CecKripke(${this.kripke.logicType}) W=${this.kripke.worlds.size} R=${relationCount}`,
      '--------------------------------------------------',
    ];
    for (const worldId of [...this.kripke.worlds].sort((left, right) => left - right)) {
      const atoms = [...(this.kripke.valuation.get(worldId) ?? [])].sort().join(',') || 'none';
      const targets =
        [...this.kripke.getAccessibleWorlds(worldId)]
          .sort((left, right) => left - right)
          .map((target) => `w${target}`)
          .join(',') || 'none';
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
    const header = `CEC Kripke Structure (Logic: ${this.kripke.logicType})`;
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
      lines.push(`| Atoms: ${atoms.length > 0 ? atoms.join(', ') : 'none'}`);
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
      `  ${checks.reflexive ? 'yes' : 'no'} Reflexive: ${checks.reflexive}`,
      `  ${checks.symmetric ? 'yes' : 'no'} Symmetric: ${checks.symmetric}`,
      `  ${checks.transitive ? 'yes' : 'no'} Transitive: ${checks.transitive}`,
      `  ${checks.serial ? 'yes' : 'no'} Serial: ${checks.serial}`,
    ];
    const expected = expectedModalProperties(this.kripke.logicType);
    if (expected.length > 0)
      lines.push('', `Expected for ${this.kripke.logicType}: ${expected.join(', ')}`);
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

  toDataSnapshot(): CecCountermodelVisualizerSnapshot {
    const nodes = [...this.kripke.worlds]
      .sort((left, right) => left - right)
      .map((worldId) => ({
        id: `w${worldId}`,
        label: `w${worldId}`,
        atoms: [...(this.kripke.valuation.get(worldId) ?? [])].sort(),
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

  toHtmlString(): string {
    const data = this.toDataSnapshot();
    const nodes = data.nodes;
    const links = data.links;
    return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>CEC Kripke Structure - ${escapeHtml(this.kripke.logicType)}</title><style>body{font-family:system-ui,sans-serif;margin:24px}.world{border:1px solid #999;border-radius:6px;padding:8px;margin:8px 0}.initial{border-color:#0a7;background:#eefaf4}.edge{color:#555}</style></head><body><h1>CEC Kripke Structure (${escapeHtml(this.kripke.logicType)})</h1><script type="application/json" id="cec-kripke-data">${escapeHtml(JSON.stringify(data))}</script>${nodes.map((node) => `<section class="world${node.is_initial ? ' initial' : ''}"><strong>${escapeHtml(node.label)}</strong><div>Atoms: ${escapeHtml(node.atoms.join(', ') || 'none')}</div></section>`).join('')}<h2>Accessibility</h2>${links.map((link) => `<div class="edge">${escapeHtml(link.source)} -> ${escapeHtml(link.target)}</div>`).join('') || '<div class="edge">(none)</div>'}</body></html>`;
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

export function extractCecCountermodel(
  formula: CecExpression,
  branch: CecTableauxBranchLike,
  logicType: CecModalLogicType = 'K',
): CecCounterModel {
  return new CecCounterModelExtractor(logicType).extract(formula, branch);
}

export function visualizeCecCountermodel(
  countermodel: CecCounterModel,
  format: CecCountermodelFormat = 'ascii',
): string {
  if (format === 'ascii') return countermodel.toAsciiArt();
  if (format === 'dot') return countermodel.toDot();
  if (format === 'json') return countermodel.toJson();
  const visualizer = new CecCounterModelVisualizer(countermodel.kripke);
  if (format === 'html') return visualizer.toHtmlString();
  if (format === 'compact-ascii') return visualizer.renderAsciiEnhanced('compact');
  throw new Error(`Unsupported CEC countermodel format: ${format}`);
}

export function exportCecTableauxCountermodelData(
  formula: CecExpression,
  branch: CecTableauxBranchLike,
  logicType: CecModalLogicType = 'K',
  proofSteps: string[] = [],
): CecTableauxCountermodelExport {
  const countermodel = extractCecCountermodel(formula, branch, logicType);
  const visualizer = new CecCounterModelVisualizer(countermodel.kripke);
  return {
    formula: formatCecExpression(formula),
    logic_type: logicType,
    is_valid: false,
    proof_steps: [...proofSteps],
    open_branch: serializeCecBranch(branch),
    countermodel: countermodel.kripke.toDict(),
    visualization: visualizer.toDataSnapshot(),
    explanation: [...countermodel.explanation],
  };
}

function extractPositiveAtoms(formulas: CecExpression[]): Set<string> {
  const atoms = new Set<string>();
  for (const formula of formulas) {
    if (formula.kind === 'atom' || formula.kind === 'application')
      atoms.add(formatCecExpression(formula));
  }
  return atoms;
}

function normalizeWorldEntries(
  worlds: CecTableauxBranchLike['worlds'],
): Array<[number, CecTableauxWorldLike]> {
  return isMapLike<number, CecTableauxWorldLike>(worlds)
    ? [...worlds.entries()].sort(([left], [right]) => left - right)
    : Object.entries(worlds)
        .map(([key, value]): [number, CecTableauxWorldLike] => [Number(key), value])
        .sort(([left], [right]) => left - right);
}

function normalizeAccessibilityEntries(
  accessibility: CecTableauxBranchLike['accessibility'],
): Array<[number, number[]]> {
  return isMapLike<number, Iterable<number>>(accessibility)
    ? [...accessibility.entries()]
        .map(([key, value]): [number, number[]] => [key, [...value]])
        .sort(([left], [right]) => left - right)
    : Object.entries(accessibility)
        .map(([key, value]): [number, number[]] => [Number(key), value])
        .sort(([left], [right]) => left - right);
}

function serializeCecBranch(branch: CecTableauxBranchLike): CecTableauxBranchExport {
  const worlds = normalizeWorldEntries(branch.worlds).map(([worldId, world]) => ({
    id: worldId,
    formulas: world.formulas.map((formula) => formatCecExpression(formula)).sort(),
    negated_formulas: (world.negatedFormulas ?? [])
      .map((formula) => formatCecExpression(formula))
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

function expectedModalProperties(logicType: CecModalLogicType): string[] {
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
