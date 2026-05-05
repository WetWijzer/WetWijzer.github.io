import {
  compareLogicPublicApis,
  createPythonSurfaceReplacementPlan,
} from './pythonSurfaceReplacements';

describe('createPythonSurfaceReplacementPlan', () => {
  it('maps known Python API and CLI surfaces to browser-native replacements', () => {
    const plan = createPythonSurfaceReplacementPlan([
      'ipfs_datasets_py.logic_api',
      'ipfs_datasets_py.cli',
      'python -m ipfs_datasets_py',
    ]);

    expect(plan.browserNative).toBe(true);
    expect(plan.usesPythonRuntime).toBe(false);
    expect(plan.usesServerRuntime).toBe(false);
    expect(plan.rejectedSurfaces).toEqual([]);
    expect(plan.replacements.map((replacement) => replacement.replacementKind)).toEqual([
      'typescript-developer-script',
      'browser-devtools',
      'browser-devtools',
    ]);
    expect(
      plan.replacements.every(
        (replacement) =>
          replacement.browserNative &&
          !replacement.usesPythonRuntime &&
          !replacement.usesServerRuntime,
      ),
    ).toBe(true);
  });

  it('infers TypeScript developer script replacements for Python API module surfaces', () => {
    const plan = createPythonSurfaceReplacementPlan([
      ' ipfs_datasets_py.formal_logic.converter ',
      'ipfs_datasets_py.formal_logic.converter',
    ]);

    expect(plan.rejectedSurfaces).toEqual([]);
    expect(plan.replacements).toHaveLength(1);
    expect(plan.replacements[0]).toMatchObject({
      pythonSurface: 'ipfs_datasets_py.formal_logic.converter',
      surfaceKind: 'api',
      replacementKind: 'typescript-developer-script',
      replacementName: 'logic TypeScript module imports',
      browserNative: true,
      usesPythonRuntime: false,
      usesServerRuntime: false,
    });
  });

  it('fails closed for server, filesystem, subprocess, and raw Python fallbacks', () => {
    const plan = createPythonSurfaceReplacementPlan([
      'http://localhost:8000/convert',
      'file:///tmp/input.json',
      'subprocess:ipfs_datasets_py.cli',
      'scripts/export_logic.py',
      'python scripts/export_logic.py',
    ]);

    expect(plan.replacements).toEqual([]);
    expect(plan.rejectedSurfaces).toEqual([
      'http://localhost:8000/convert',
      'file:///tmp/input.json',
      'subprocess:ipfs_datasets_py.cli',
      'scripts/export_logic.py',
      'python scripts/export_logic.py',
    ]);
  });
});

describe('compareLogicPublicApis', () => {
  it('maps default Python logic APIs to browser-native TypeScript exports', () => {
    const report = compareLogicPublicApis();

    expect(report).toMatchObject({
      browserNative: true,
      usesPythonRuntime: false,
      usesServerRuntime: false,
    });
    expect(report.missingPythonApis).toEqual([]);
    expect(report.adapters.map((adapter) => adapter.pythonApi)).toEqual(
      expect.arrayContaining([
        'convert_text_to_fol',
        'run_logic_cli',
        'extract_ml_confidence_features',
      ]),
    );
    expect(report.adapters.every((adapter) => adapter.browserNative)).toBe(true);
  });

  it('reports missing Python public APIs without inventing server or Python fallbacks', () => {
    const report = compareLogicPublicApis(
      [{ pythonModule: 'logic/example.py', publicApis: ['known_api', 'missing_api'] }],
      [{ typescriptModule: 'src/lib/logic/example.ts', publicExports: ['known_api'] }],
    );

    expect(report.adapters).toHaveLength(1);
    expect(report.adapters[0]).toMatchObject({
      pythonApi: 'known_api',
      typescriptExport: 'known_api',
      browserNative: true,
    });
    expect(report.missingPythonApis).toEqual(['logic/example.py:missing_api']);
    expect(report.comparisons[0].coverageRatio).toBe(0.5);
  });
});
