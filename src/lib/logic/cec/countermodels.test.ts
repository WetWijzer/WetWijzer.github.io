import { parseCecExpression } from './parser';
import { proveCecModalFormula } from './modalTableaux';
import {
  CecCounterModel,
  CecCounterModelExtractor,
  CecCounterModelVisualizer,
  CecKripkeStructure,
  exportCecTableauxCountermodelData,
  extractCecCountermodel,
  visualizeCecCountermodel,
} from './countermodels';

describe('CEC countermodels', () => {
  it('models CEC Kripke worlds, accessibility, valuation, and JSON export', () => {
    const kripke = new CecKripkeStructure({ logicType: 'S4' });
    kripke.addWorld(0);
    kripke.addAccessibility(0, 1);
    kripke.setAtomTrue(1, '(P (enter agent code))');

    expect(kripke.getAccessibleWorlds(0)).toEqual(new Set([1]));
    expect(kripke.isAtomTrue(1, '(P (enter agent code))')).toBe(true);
    expect(kripke.toDict()).toEqual({
      worlds: [0, 1],
      accessibility: { '0': [1], '1': [] },
      valuation: { '0': [], '1': ['(P (enter agent code))'] },
      initial_world: 0,
      logic_type: 'S4',
    });
    expect(JSON.parse(kripke.toJson()).logic_type).toBe('S4');
  });

  it('extracts a CEC countermodel from an open modal tableaux branch', () => {
    const formula = parseCecExpression(
      '(implies (always (comply_with agent code)) (comply_with agent code))',
    );
    const result = proveCecModalFormula(formula, 'K');
    const countermodel = extractCecCountermodel(formula, result.openBranch!, 'K');

    expect(countermodel.kripke.logicType).toBe('K');
    expect(countermodel.kripke.worlds.has(0)).toBe(true);
    expect(countermodel.kripke.getAccessibleWorlds(0).size).toBe(0);
    expect(countermodel.explanation[0]).toContain('is not K-valid');
    expect(countermodel.explanation[0]).toContain('(comply_with agent code)');
  });

  it('extracts from plain branch-like objects', () => {
    const formula = parseCecExpression('(always (p x))');
    const branch = {
      isClosed: false,
      worlds: {
        0: { id: 0, formulas: [parseCecExpression('(q x)')] },
        1: { id: 1, formulas: [parseCecExpression('(p x)')] },
      },
      accessibility: { 0: [1] },
    };

    const countermodel = extractCecCountermodel(formula, branch, 'K');

    expect(countermodel.kripke.isAtomTrue(0, '(q x)')).toBe(true);
    expect(countermodel.kripke.isAtomTrue(1, '(p x)')).toBe(true);
  });

  it('rejects closed branches during extraction', () => {
    const extractor = new CecCounterModelExtractor();

    expect(() =>
      extractor.extract(parseCecExpression('(p x)'), {
        isClosed: true,
        worlds: {},
        accessibility: {},
      }),
    ).toThrow('Cannot extract CEC countermodel from closed branch');
  });

  it('renders CEC countermodels as text, DOT, JSON, ASCII, and HTML', () => {
    const formula = parseCecExpression('(p x)');
    const kripke = new CecKripkeStructure({ logicType: 'D' });
    kripke.addAccessibility(0, 1);
    kripke.setAtomTrue(0, '(q x)');
    const countermodel = new CecCounterModel(formula, kripke, ['(p x) fails at w0']);

    expect(countermodel.toString()).toContain('CEC countermodel for: (p x)');
    expect(countermodel.toAsciiArt()).toContain('-> w0: {(q x)}');
    expect(countermodel.toDot()).toContain('w0 -> w1;');
    expect(JSON.parse(countermodel.toJson()).kripke_structure.logic_type).toBe('D');
    expect(visualizeCecCountermodel(countermodel, 'compact-ascii')).toContain('CecKripke(D)');
    expect(visualizeCecCountermodel(countermodel, 'html')).toContain(
      '<script type="application/json" id="cec-kripke-data">',
    );
  });

  it('checks modal accessibility properties for CEC visualizer summaries', () => {
    const kripke = new CecKripkeStructure({ logicType: 'S5' });
    kripke.addAccessibility(0, 0);
    kripke.addAccessibility(0, 1);
    kripke.addAccessibility(1, 0);
    kripke.addAccessibility(1, 1);

    const visualizer = new CecCounterModelVisualizer(kripke);

    expect(visualizer.getPropertyChecks()).toEqual({
      reflexive: true,
      symmetric: true,
      transitive: true,
      serial: true,
    });
    expect(visualizer.renderLogicProperties()).toContain(
      'Expected for S5: Reflexive, Symmetric, Transitive',
    );
    expect(visualizer.renderAsciiEnhanced()).toContain('CEC Kripke Structure (Logic: S5)');
  });

  it('exports CEC modal tableaux open branches as serializable visualization data', () => {
    const formula = parseCecExpression(
      '(implies (always (comply_with agent code)) (comply_with agent code))',
    );
    const result = proveCecModalFormula(formula, 'K');

    expect(result.isValid).toBe(false);
    expect(result.openBranch).toBeDefined();

    const exported = exportCecTableauxCountermodelData(
      formula,
      result.openBranch!,
      'K',
      result.proofSteps,
    );

    expect(exported).toMatchObject({
      formula: '(implies (always (comply_with agent code)) (comply_with agent code))',
      logic_type: 'K',
      is_valid: false,
      countermodel: { worlds: [0], accessibility: { '0': [] }, logic_type: 'K' },
      visualization: { num_worlds: 1, num_relations: 0, expected_properties: [] },
    });
    expect(exported.open_branch.worlds[0].negated_formulas).toEqual(['(comply_with agent code)']);
    expect(JSON.parse(JSON.stringify(exported)).visualization.nodes[0].id).toBe('w0');
  });
});
