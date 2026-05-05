import { createLogicDevtoolsCommandAdapter, runLogicCli, runLogicDevtoolsCommand } from './cli';

describe('browser-native logic CLI adapter', () => {
  it('runs health and conversion commands locally', () => {
    expect(runLogicCli(['health'])).toMatchObject({
      ok: true,
      stdout: 'logic runtime: browser-native-typescript-wasm',
      runtime: { pythonRuntime: false, serverRuntime: false, serverCallsAllowed: false },
    });
    expect(
      runLogicCli([
        'convert',
        '--source',
        'All tenants are residents',
        '--from',
        'natural_language',
        '--to',
        'fol',
      ]),
    ).toMatchObject({
      ok: true,
      command: 'convert',
      data: { target_formula: '∀x (Tenants(x) → Residents(x))', serverCallsAllowed: false },
    });
  });

  it('proves formulas and compiles policies through browser-native APIs', () => {
    const proof = runLogicCli([
      'prove',
      '--logic',
      'cec',
      '--theorem',
      '(subject_to ada code)',
      '--axiom',
      '(subject_to ada code)',
    ]);
    const policy = runLogicCli(['policy', '--source', 'Tenants may use the community room.']);

    expect(proof).toMatchObject({
      ok: true,
      stdout: 'proved',
      data: { status: 'proved', method: 'bridge:cec-forward-chaining', pythonRuntime: false },
    });
    expect(policy).toMatchObject({
      ok: true,
      command: 'policy',
      data: { success: true, serverRuntime: false },
    });
    expect(policy.stdout).toContain('P[tenants:Agent]');
  });

  it('runs validation and structured devtools commands without Python or server fallbacks', () => {
    const adapter = createLogicDevtoolsCommandAdapter();
    const converted = adapter.run({
      command: 'convert',
      flags: {
        source: 'All auditors are reviewers',
        from: 'natural_language',
        to: 'fol',
      },
    });
    const validation = runLogicDevtoolsCommand({
      command: 'validate',
      flags: { 'fol-text': 'All tenants are protected.' },
    });

    expect(adapter).toMatchObject({
      browserNative: true,
      pythonRuntime: false,
      serverRuntime: false,
      commands: expect.arrayContaining(['health', 'convert', 'prove', 'policy', 'validate']),
    });
    expect(converted).toMatchObject({
      ok: true,
      command: 'convert',
      data: { target_formula: '∀x (Auditors(x) → Reviewers(x))', pythonRuntime: false },
    });
    expect(validation).toMatchObject({
      ok: true,
      command: 'validate',
      stdout: 'browser-native logic runtime valid',
      data: { valid: true, serverCallsAllowed: false, pythonRuntime: false },
    });
  });

  it('fails closed for legacy runtimes and malformed commands', () => {
    expect(runLogicCli(['python', '-m', 'ipfs_datasets_py.logic.cli'])).toMatchObject({
      ok: false,
      exitCode: 2,
      runtime: { pythonRuntime: false, serverRuntime: false, serverCallsAllowed: false },
    });
    expect(runLogicCli(['convert', '--source', 'http://localhost:8000/convert'])).toMatchObject({
      ok: false,
      exitCode: 2,
      stderr: expect.stringContaining('Runtime fallbacks are not available'),
    });
    expect(runLogicCli(['prove', '--theorem', 'P(a)'])).toMatchObject({
      ok: false,
      exitCode: 2,
      stderr: 'prove requires --theorem <formula> and at least one --axiom <formula>.',
    });
  });
});
