import { BrowserNativeLogicBridge, createBrowserNativeLogicBridge } from './bridge';
import { createBrowserNativeCecBridge } from './cecBridge';
import {
  createBrowserNativeBaseProverBridge,
  createBrowserNativeIntegrationBridgesBaseProverBridge,
} from './baseProverBridge';
import type { BrowserNativeCoqProofResult } from './coqProverBridge';
import {
  createBrowserNativeCvc5ProverBridge,
  type BrowserNativeCvc5ProofResult,
} from './cvc5ProverBridge';
import { createBrowserNativeExternalProversBridge } from './externalProversBridge';
import {
  createBrowserNativeLeanProverBridge,
  type BrowserNativeLeanProofResult,
} from './leanProverBridge';
import {
  BrowserNativeProverRouter,
  createBrowserNativeEProverAdapter,
  createBrowserNativeProverRouter,
  get_prover_backend_mixin_backends,
  select_prover_backend_mixin,
  type BrowserNativeProofAdapter,
  type EProverCompatibilityResult,
} from './proverAdapters';
import { createBrowserNativeProverInstaller } from './proverInstaller';
import {
  createBrowserNativeSymbolicAiProverBridge,
  type BrowserNativeSymbolicAiProofResult,
} from './symbolicAiProverBridge';
import { SymbolicFOLBridge, createBrowserNativeRootSymbolicFOLBridge } from './symbolicFolBridge';
import { createBrowserNativeSymbolicFOLConverterBridge } from './converters/symbolicFolBridge';
import {
  convertTdfolToCec,
  createBrowserNativeTdfolCecBridge,
  proveTdfolWithCec,
  validateTdfolCecBridgeInput,
} from './tdfolCecBridge';
import {
  createBrowserNativeTdfolGrammarBridge,
  parseTdfolGrammarBridgeInput,
  validateTdfolGrammarBridgeInput,
} from './tdfolGrammarBridge';
import {
  convertTdfolToShadowProver,
  createBrowserNativeTdfolShadowProverBridge,
  proveTdfolWithShadowProver,
  validateTdfolShadowProverBridgeInput,
} from './tdfolShadowProverBridge';
import {
  createBrowserNativeZ3ProverBridge,
  type BrowserNativeZ3ProofResult,
} from './z3ProverBridge';

describe('BrowserNativeLogicBridge', () => {
  it('reports local browser-native metadata and supported routes', () => {
    const bridge = createBrowserNativeLogicBridge();

    expect(bridge.metadata.requiresExternalProver).toBe(false);
    expect(bridge.metadata.toDict()).toMatchObject({
      target_system: 'typescript-wasm-browser',
      requires_external_prover: false,
    });
    expect(bridge.supportsConversion('legal_text', 'deontic')).toBe(true);
    expect(bridge.supportsConversion('fol', 'cec')).toBe(true);
    expect(bridge.supportsConversion('tdfol', 'cec')).toBe(true);
    expect(bridge.listRoutes().length).toBeGreaterThan(10);
  });

  it('routes legal text to FOL and deontic converters without server calls', () => {
    const bridge = new BrowserNativeLogicBridge({
      fol: { useNlp: true, useMl: true },
      deontic: { useMl: true },
    });

    const fol = bridge.convert({
      source: 'All tenants are residents',
      sourceFormat: 'legal_text',
      targetFormat: 'fol',
    });
    const deontic = bridge.convert('Tenants must maintain exits.', 'legal_text', 'deontic');

    expect(fol.status).toBe('partial');
    expect(fol.targetFormula).toBe('∀x (Tenants(x) → Residents(x))');
    expect(fol.metadata).toMatchObject({
      routed_to: 'FOLConverter',
      server_calls_allowed: false,
      browser_native_ml_confidence: true,
    });
    expect(deontic.status).toBe('success');
    expect(deontic.targetFormula).toContain('O(');
    expect(deontic.metadata).toMatchObject({
      routed_to: 'DeonticConverter',
      server_calls_allowed: false,
    });
  });

  it('routes TDFOL and CEC conversions through local parser/formatter cores', () => {
    const bridge = createBrowserNativeLogicBridge();

    const folToCec = bridge.convert('∀x (Tenant(x) → Resident(x))', 'fol', 'cec');
    const tdfolToCec = bridge.convert('forall x. O(Comply(x))', 'tdfol', 'cec');
    const cecToJson = bridge.convert('(O (Comply ada))', 'cec', 'json');

    expect(folToCec).toMatchObject({
      status: 'success',
      targetFormula: '(forall x (implies (Tenant x) (Resident x)))',
      sourceFormat: 'fol',
      targetFormat: 'cec',
      metadata: {
        projection: 'deterministic-fol-to-cec',
        server_calls_allowed: false,
      },
    });
    expect(tdfolToCec).toMatchObject({
      status: 'success',
      targetFormula: '(forall x (O (Comply x)))',
      sourceFormat: 'tdfol',
      targetFormat: 'cec',
    });
    expect(tdfolToCec.metadata).toMatchObject({
      routed_to: 'convertTdfolFormula',
      server_calls_allowed: false,
    });
    expect(JSON.parse(cecToJson.targetFormula)).toMatchObject({
      kind: 'unary',
      operator: 'O',
    });
  });

  it('ports top-level tdfol_cec_bridge.py conversion and proof delegation without external fallbacks', () => {
    const bridge = createBrowserNativeTdfolCecBridge();
    const converted = bridge.convert('forall x. always(O(Comply(x)))');
    const invalid = bridge.validate('always(');
    const result = bridge.prove({
      theorem: 'F(Enter(x))',
      axioms: ['O(not Enter(x))'],
    });

    expect(converted).toMatchObject({
      status: 'success',
      source: '∀x (□(O(Comply(x))))',
      cecText: '(forall x (always (O (Comply x))))',
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_cec_bridge.py',
        legacySourcePythonModules: ['logic/integration/bridges/tdfol_cec_bridge.py'],
        browserNative: true,
        serverCallsAllowed: false,
        pythonRuntime: false,
        failClosed: true,
      },
    });
    expect(invalid).toMatchObject({ valid: false, metadata: { serverCallsAllowed: false } });
    expect(invalid.warnings).toContain(
      'TDFOL to CEC bridge failed closed without external fallback.',
    );
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'F(Enter(x))',
      method: 'tdfol_cec_bridge:cec_delegate:local',
      cecTheorem: '(F (Enter x))',
      cecAxioms: ['(O (not (Enter x)))'],
      cecTheorems: [],
      sourcePythonModule: 'logic/integration/tdfol_cec_bridge.py',
      legacySourcePythonModules: ['logic/integration/bridges/tdfol_cec_bridge.py'],
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
    expect(result.steps.map((step) => step.rule)).toContain('CecDeonticProhibitionEquivalence');
  });

  it('exposes top-level tdfol_cec_bridge.py functional helpers for browser callers', () => {
    const converted = convertTdfolToCec('P(Inspect(Ada))');
    const validation = validateTdfolCecBridgeInput('P(Inspect(Ada))');
    const result = proveTdfolWithCec({
      theorem: 'P(Inspect(Ada))',
      axioms: ['P(Inspect(Ada))'],
      theorems: ['O(Log(Ada))'],
    });

    expect(converted).toMatchObject({
      status: 'success',
      cecText: '(P (Inspect Ada))',
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_cec_bridge.py',
        serverCallsAllowed: false,
        pythonRuntime: false,
      },
    });
    expect(validation).toMatchObject({ valid: true, errors: [], warnings: [] });
    expect(result).toMatchObject({
      status: 'proved',
      cecAxioms: ['(P (Inspect Ada))'],
      cecTheorems: ['(O (Log Ada))'],
      sourcePythonModule: 'logic/integration/tdfol_cec_bridge.py',
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
  });

  it('ports cec_bridge.py through local CEC parsing, validation, and proof search', () => {
    const bridge = createBrowserNativeCecBridge({ maxSteps: 4, maxDerivedExpressions: 25 });
    const converted = bridge.convert('(implies p q)', 'json');
    const invalid = bridge.validate('(implies p');
    const result = bridge.prove({
      theorem: 'q',
      axioms: ['p', '(implies p q)'],
    });

    expect(converted).toMatchObject({
      status: 'success',
      source: '(implies p q)',
      target: 'json',
      metadata: {
        sourcePythonModule: 'logic/integration/cec_bridge.py',
        browserNative: true,
        serverCallsAllowed: false,
        pythonRuntime: false,
        failClosed: true,
      },
    });
    expect(JSON.parse(converted.output)).toMatchObject({ kind: 'binary', operator: 'implies' });
    expect(invalid).toMatchObject({
      valid: false,
      metadata: { serverCallsAllowed: false, pythonRuntime: false },
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'q',
      method: 'cec_bridge:cec-forward-chaining',
      sourcePythonModule: 'logic/integration/cec_bridge.py',
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
    expect(result.steps.map((step) => step.rule)).toContain('CecModusPonens');
  });

  it('ports tdfol_grammar_bridge.py with deterministic browser-native grammar parsing', () => {
    const bridge = createBrowserNativeTdfolGrammarBridge();
    const controlled = bridge.parse('Always Alice must file appeal.');
    const direct = bridge.parse({ source: 'forall x. O(FileAppeal(x))', inputKind: 'tdfol' });
    const invalid = bridge.validate('Alice might file appeal');

    expect(controlled).toMatchObject({
      status: 'success',
      formulaText: 'O(□(File_appeal(alice)))',
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_grammar_bridge.py',
        legacySourcePythonModules: ['logic/integration/bridges/tdfol_grammar_bridge.py'],
        browserNative: true,
        serverCallsAllowed: false,
        pythonRuntime: false,
        failClosed: true,
      },
      grammarTrace: ['controlled_english:normalize', 'temporal:always', 'modal:obligation'],
    });
    expect(direct).toMatchObject({
      status: 'success',
      inputKind: 'tdfol',
      formulaText: '∀x (O(FileAppeal(x)))',
      grammarTrace: ['tdfol:parser'],
    });
    expect(invalid).toMatchObject({
      valid: false,
      metadata: { serverCallsAllowed: false, pythonRuntime: false },
    });
  });

  it('exposes top-level tdfol_grammar_bridge.py functional helpers without runtime fallback', () => {
    const controlled = parseTdfolGrammarBridgeInput('Eventually Alice may file appeal');
    const direct = parseTdfolGrammarBridgeInput({
      source: 'P(FileAppeal(Alice))',
      inputKind: 'tdfol',
    });
    const invalid = validateTdfolGrammarBridgeInput('Alice might file appeal');

    expect(controlled).toMatchObject({
      status: 'success',
      inputKind: 'controlled_english',
      formulaText: 'P(◊(File_appeal(alice)))',
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_grammar_bridge.py',
        legacySourcePythonModules: ['logic/integration/bridges/tdfol_grammar_bridge.py'],
        serverCallsAllowed: false,
        pythonRuntime: false,
      },
      grammarTrace: ['controlled_english:normalize', 'temporal:eventually', 'modal:permission'],
    });
    expect(direct).toMatchObject({
      status: 'success',
      formulaText: 'P(FileAppeal(Alice))',
      grammarTrace: ['tdfol:parser'],
    });
    expect(invalid).toMatchObject({
      valid: false,
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_grammar_bridge.py',
        serverCallsAllowed: false,
        pythonRuntime: false,
        failClosed: true,
      },
    });
  });

  it('ports tdfol_shadowprover_bridge.py through the browser-native CEC ShadowProver', () => {
    const bridge = createBrowserNativeTdfolShadowProverBridge();
    const converted = bridge.convert('always(O(Comply(Ada)))');
    const result = bridge.prove({
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
      logic: 'K',
    });
    const unsupported = bridge.prove({
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
      logic: 'LP',
    });

    expect(converted).toMatchObject({
      status: 'success',
      source: '□(O(Comply(Ada)))',
      shadowFormula: '(always (O (Comply Ada)))',
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_shadowprover_bridge.py',
        legacySourcePythonModules: ['logic/integration/bridges/tdfol_shadowprover_bridge.py'],
        browserNative: true,
        serverCallsAllowed: false,
        pythonRuntime: false,
        failClosed: true,
      },
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'tdfol_shadowprover_bridge:direct-assumption',
      cecTheorem: '(Resident Ada)',
      shadowLogic: 'K',
      shadowProofStatus: 'success',
      sourcePythonModule: 'logic/integration/tdfol_shadowprover_bridge.py',
      legacySourcePythonModules: ['logic/integration/bridges/tdfol_shadowprover_bridge.py'],
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
    expect(unsupported).toMatchObject({
      status: 'error',
      method: 'tdfol_shadowprover_bridge:fail_closed',
      shadowLogic: 'LP',
      shadowProofStatus: 'error',
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
  });

  it('exposes top-level tdfol_shadowprover_bridge.py helpers without external fallbacks', () => {
    const converted = convertTdfolToShadowProver('P(Inspect(Ada))');
    const validation = validateTdfolShadowProverBridgeInput('P(Inspect(Ada))');
    const invalid = validateTdfolShadowProverBridgeInput('always(');
    const result = proveTdfolWithShadowProver({
      theorem: 'P(Inspect(Ada))',
      axioms: ['P(Inspect(Ada))'],
      logic: 'S4',
    });

    expect(converted).toMatchObject({
      status: 'success',
      shadowFormula: '(P (Inspect Ada))',
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_shadowprover_bridge.py',
        legacySourcePythonModules: ['logic/integration/bridges/tdfol_shadowprover_bridge.py'],
        serverCallsAllowed: false,
        pythonRuntime: false,
        failClosed: true,
      },
    });
    expect(validation).toMatchObject({
      valid: true,
      errors: [],
      warnings: [],
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_shadowprover_bridge.py',
        serverCallsAllowed: false,
        pythonRuntime: false,
      },
    });
    expect(invalid).toMatchObject({
      valid: false,
      metadata: {
        sourcePythonModule: 'logic/integration/tdfol_shadowprover_bridge.py',
        serverCallsAllowed: false,
        pythonRuntime: false,
        failClosed: true,
      },
    });
    expect(invalid.warnings).toContain(
      'TDFOL ShadowProver bridge failed closed without external fallback.',
    );
    expect(result).toMatchObject({
      status: 'proved',
      method: 'tdfol_shadowprover_bridge:direct-assumption',
      cecTheorem: '(P (Inspect Ada))',
      shadowLogic: 'S4',
      shadowProofStatus: 'success',
      sourcePythonModule: 'logic/integration/tdfol_shadowprover_bridge.py',
      legacySourcePythonModules: ['logic/integration/bridges/tdfol_shadowprover_bridge.py'],
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
  });

  it('proves TDFOL and CEC requests using local proof engines', () => {
    const bridge = createBrowserNativeLogicBridge();

    const tdfol = bridge.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    });
    const cec = bridge.prove({
      logic: 'cec',
      theorem: '(subject_to ada code)',
      axioms: ['(subject_to ada code)'],
    });

    expect(tdfol).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'bridge:tdfol-forward-chaining',
    });
    expect(cec).toMatchObject({
      status: 'proved',
      theorem: '(subject_to ada code)',
      method: 'bridge:cec-forward-chaining',
    });
    expect(tdfol.timeMs).toEqual(expect.any(Number));
    expect(cec.timeMs).toEqual(expect.any(Number));
  });

  it('exposes browser-local prover adapter contracts for TDFOL, CEC, and DCEC', () => {
    const router = createBrowserNativeProverRouter();
    const adapters = router.listAdapters();

    expect(router.getMetadata()).toMatchObject({
      sourcePythonModule: 'logic/external_provers/prover_router.py',
      backendMixinSourcePythonModule: 'logic/integration/reasoning/_prover_backend_mixin.py',
      runtime: 'typescript-wasm-browser',
      serverCallsAllowed: false,
      pythonRuntime: false,
      subprocessAllowed: false,
      rpcAllowed: false,
      routingStrategy: 'first-supported-local-adapter',
      failClosed: true,
      adapterCount: 3,
    });
    expect(adapters.map((adapter) => adapter.logic)).toEqual(['tdfol', 'cec', 'dcec']);
    expect(adapters.every((adapter) => adapter.runtime === 'typescript-wasm-browser')).toBe(true);
    expect(adapters.every((adapter) => adapter.requiresExternalProver === false)).toBe(true);
    expect(router.supports('tdfol')).toBe(true);
    expect(router.supports('dcec')).toBe(true);
  });

  it('ports reasoning prover backend mixin selection without runtime bridges', () => {
    const router = createBrowserNativeProverRouter({ includeEProverCompatibilityAdapter: true });
    const backends = get_prover_backend_mixin_backends();

    expect(router.getBackendMixinMetadata()).toMatchObject({
      sourcePythonModule: 'logic/integration/reasoning/_prover_backend_mixin.py',
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      subprocessAllowed: false,
      rpcAllowed: false,
      runtimeDependencies: [],
    });
    expect(backends.map((backend) => backend.name)).toEqual(
      expect.arrayContaining(['local', 'tdfol', 'cec', 'dcec', 'e-prover', 'z3', 'external']),
    );
    expect(select_prover_backend_mixin('cec')).toMatchObject({
      name: 'cec',
      available: true,
      adapterName: 'local-cec-forward-prover',
      runtimeDependencies: [],
    });
    expect(router.selectBackend('tdfol', 'z3')).toMatchObject({
      name: 'z3',
      available: false,
      browserNative: true,
      failureMode: 'fail_closed',
      adapterName: null,
      runtimeDependencies: [],
    });
  });

  it('routes proof requests through local browser adapters without external prover delegation', () => {
    const router = createBrowserNativeProverRouter();

    const tdfol = router.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    });
    const dcec = router.prove({
      logic: 'dcec',
      theorem: '(P (always (comply_with ada code)))',
      axioms: ['(P (always (comply_with ada code)))'],
    });

    expect(tdfol).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'adapter:local-tdfol-forward-prover:tdfol-forward-chaining',
    });
    expect(dcec).toMatchObject({
      status: 'proved',
      theorem: '(P (always (comply_with ada code)))',
      method: 'adapter:local-dcec-forward-prover:cec-forward-chaining',
    });
    expect(tdfol.timeMs).toEqual(expect.any(Number));
    expect(dcec.timeMs).toEqual(expect.any(Number));
  });

  it('ports prover_router.py route planning and preferred local adapter selection', () => {
    const router = createBrowserNativeProverRouter({ includeEProverCompatibilityAdapter: true });

    const defaultRoute = router.planRoute({ logic: 'tdfol' });
    const eProverRoute = router.planRoute({ logic: 'tdfol', preferredProverFamily: 'e-prover' });
    const eProverResult = router.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
      preferredProverFamily: 'e-prover',
    }) as EProverCompatibilityResult;

    expect(defaultRoute).toMatchObject({
      sourcePythonModule: 'logic/external_provers/prover_router.py',
      logic: 'tdfol',
      selectedAdapter: { name: 'local-tdfol-forward-prover', proverFamily: 'local' },
      blockers: [],
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
    expect(eProverRoute.selectedAdapter).toMatchObject({
      name: 'browser-native-e-prover-adapter',
      proverFamily: 'e-prover',
    });
    expect(eProverRoute.candidates.map((candidate) => candidate.name)).toEqual([
      'local-tdfol-forward-prover',
      'browser-native-e-prover-adapter',
    ]);
    expect(eProverResult).toMatchObject({
      status: 'proved',
      method: 'adapter:browser-native-e-prover-adapter:e-prover-compatible:tdfol-forward-chaining',
    });
  });

  it('fails closed for unsupported prover_router.py routes without Python or RPC fallback', () => {
    const router = createBrowserNativeProverRouter();
    const route = router.planRoute({ logic: 'cec', preferredProverFamily: 'e-prover' });

    expect(route).toMatchObject({
      sourcePythonModule: 'logic/external_provers/prover_router.py',
      selectedAdapter: null,
      blockers: ['unsupported_preferred_prover_family:e-prover'],
      serverCallsAllowed: false,
      pythonRuntime: false,
    });
    expect(() =>
      router.prove({
        logic: 'cec',
        theorem: '(subject_to ada code)',
        axioms: ['(subject_to ada code)'],
        preferredProverFamily: 'e-prover',
      }),
    ).toThrow(
      'Unsupported browser-native proof route: unsupported_preferred_prover_family:e-prover',
    );
  });

  it('ports the E prover adapter as a browser-native fail-closed TDFOL compatibility adapter', () => {
    const adapter = createBrowserNativeEProverAdapter();
    const result = adapter.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    }) as EProverCompatibilityResult;

    expect(adapter.metadata).toMatchObject({
      logic: 'tdfol',
      name: 'browser-native-e-prover-adapter',
      runtime: 'typescript-wasm-browser',
      requiresExternalProver: false,
      proverFamily: 'e-prover',
    });
    expect(adapter.supports('cec')).toBe(false);
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'e-prover-compatible:tdfol-forward-chaining',
    });
    expect(result.eProver).toMatchObject({
      adapter: 'browser-native-e-prover-adapter',
      externalBinaryAllowed: false,
      serverCallsAllowed: false,
      command: null,
      statusMapping: 'Theorem',
    });
    expect(result.eProver.tptpProblem).toContain('fof(tdfol_formula, axiom, resident(ada)).');
    expect(result.eProver.tptpProblem).toContain(
      'fof(tdfol_conjecture, conjecture, resident(ada)).',
    );
  });

  it('ports the CVC5 prover bridge as browser-native SMT-LIB compatibility metadata', () => {
    const adapter = createBrowserNativeCvc5ProverBridge();
    const result = adapter.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    }) as BrowserNativeCvc5ProofResult;

    expect(adapter.metadata).toMatchObject({
      logic: 'tdfol',
      name: 'browser-native-cvc5-prover-bridge',
      runtime: 'typescript-wasm-browser',
      requiresExternalProver: false,
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'cvc5-compatible:tdfol-forward-chaining',
    });
    expect(result.cvc5).toMatchObject({
      sourcePythonModule: 'logic/external_provers/smt/cvc5_prover_bridge.py',
      externalBinaryAllowed: false,
      serverCallsAllowed: false,
      pythonRuntime: false,
      command: null,
      checkSatStatus: 'unsat',
      isValid: true,
      isUnsat: true,
    });
    expect(result.cvc5.smtLib).toContain('(assert (Resident Ada))');
    expect(result.cvc5.smtLib).toContain('(assert (not (Resident Ada)))');
    expect(result.cvc5.smtLib).toContain('(check-sat)');
  });

  it('ports the Z3 prover bridge as browser-native SMT-LIB compatibility metadata', () => {
    const adapter = createBrowserNativeZ3ProverBridge();
    const result = adapter.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    }) as BrowserNativeZ3ProofResult;

    expect(adapter.metadata).toMatchObject({
      logic: 'tdfol',
      name: 'browser-native-z3-prover-bridge',
      runtime: 'typescript-wasm-browser',
      requiresExternalProver: false,
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'z3-compatible:tdfol-forward-chaining',
    });
    expect(result.z3).toMatchObject({
      sourcePythonModule: 'logic/external_provers/smt/z3_prover_bridge.py',
      externalBinaryAllowed: false,
      serverCallsAllowed: false,
      pythonRuntime: false,
      command: null,
      checkSatStatus: 'unsat',
      isValid: true,
      isUnsat: true,
    });
    expect(result.z3.smtLib).toContain('(assert (Resident Ada))');
    expect(result.z3.smtLib).toContain('(assert (not (Resident Ada)))');
    expect(result.z3.smtLib).toContain('(check-sat)');
  });

  it('can expose the E prover compatibility adapter through the local router without server calls', () => {
    const router = createBrowserNativeProverRouter({ includeEProverCompatibilityAdapter: true });
    const adapters = router.listAdapters();

    expect(adapters.map((adapter) => adapter.name)).toContain('browser-native-e-prover-adapter');
    expect(adapters.every((adapter) => adapter.requiresExternalProver === false)).toBe(true);
  });

  it('ports the Lean prover bridge as a browser-native TDFOL compatibility adapter', () => {
    const adapter = createBrowserNativeLeanProverBridge();
    const result = adapter.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    }) as BrowserNativeLeanProofResult;

    expect(adapter.metadata).toMatchObject({
      logic: 'tdfol',
      name: 'browser-native-lean-prover-bridge',
      runtime: 'typescript-wasm-browser',
      requiresExternalProver: false,
    });
    expect(adapter.supports('cec')).toBe(false);
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'lean-compatible:tdfol-forward-chaining',
    });
    expect(result.lean).toMatchObject({
      adapter: 'browser-native-lean-prover-bridge',
      externalBinaryAllowed: false,
      serverCallsAllowed: false,
      pythonRuntime: false,
      command: null,
      leanVersion: null,
      statusMapping: 'proved',
    });
    expect(result.lean.theoremDeclaration).toContain('axiom h1 : (Resident Ada)');
    expect(result.lean.theoremDeclaration).toContain('theorem target : (Resident Ada)');
  });

  it('ports the SymbolicAI neural prover bridge without Python or service calls', () => {
    const adapter = createBrowserNativeSymbolicAiProverBridge();
    const result = adapter.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    }) as BrowserNativeSymbolicAiProofResult;

    expect(adapter.metadata).toMatchObject({
      logic: 'tdfol',
      name: 'browser-native-symbolicai-prover-bridge',
      runtime: 'typescript-wasm-browser',
      requiresExternalProver: false,
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'symbolicai-compatible:tdfol-forward-chaining',
    });
    expect(result.symbolicAi).toMatchObject({
      adapter: 'browser-native-symbolicai-prover-bridge',
      externalPackageAllowed: false,
      serverCallsAllowed: false,
      pythonRuntime: false,
      neuralRuntime: 'deterministic-local-tdfol',
      confidence: 1,
      premiseOverlap: 1,
      statusMapping: 'success',
    });
    expect(result.symbolicAi.symbolicProgram).toContain('premise_1: Resident(Ada)');
    expect(result.symbolicAi.symbolicProgram).toContain('target: Resident(Ada)');
  });

  it('ports integration/bridges/symbolic_fol_bridge.py as a browser-native FOL bridge', () => {
    const bridge = new SymbolicFOLBridge();

    const symbol = bridge.create_semantic_symbol('All tenants are residents');
    const result = bridge.semantic_to_fol(symbol);
    const cached = bridge.convert_to_fol('All tenants are residents');

    expect(symbol).toEqual({ value: 'All tenants are residents', semantic: true });
    expect(result).toMatchObject({
      fol_formula: '∀x (Tenants(x) → Residents(x))',
      confidence: 0.8,
      fallback_used: false,
      reasoning_steps: [
        "Processing: 'All tenants are residents'",
        'Pattern-based conversion succeeded',
      ],
    });
    expect(result.components).toMatchObject({
      quantifiers: ['all'],
      predicates: ['are'],
      entities: ['tenants', 'residents'],
      confidence: 0.6,
    });
    expect(cached).toBe(result);
    expect(bridge.validate_fol_formula(result.fol_formula)).toMatchObject({
      valid: true,
      structure: { has_quantifiers: true, predicate_count: 2 },
    });
    expect(bridge.get_stats()).toMatchObject({
      sourcePythonModule: 'logic/integration/bridges/symbolic_fol_bridge.py',
      runtime: 'typescript-wasm-browser',
      symbolic_ai_available: false,
      serverCallsAllowed: false,
      pythonRuntime: false,
      cache_size: 1,
    });
  });

  it('fails closed to deterministic local SymbolicFOL fallback without SymbolicAI calls', () => {
    const bridge = new SymbolicFOLBridge();
    const result = bridge.convert_to_fol('Tenant uses archive records', 'tptp');

    expect(result).toMatchObject({
      fol_formula: 'fof(statement, axiom, Statement(Tenant_uses_archive_records)).',
      confidence: 0.5,
      fallback_used: true,
      errors: [],
    });
    expect(() => bridge.create_semantic_symbol('7')).toThrow('Text cannot be empty');
  });

  it('ports integration/converters/symbolic_fol_bridge.py with converter-scoped metadata', () => {
    const bridge = createBrowserNativeSymbolicFOLConverterBridge();

    const directRelation = bridge.convert_to_fol('Alice loves Bob');
    const implication = bridge.convert_to_fol(
      'If all tenants are residents then some tenants are protected',
    );

    expect(directRelation).toMatchObject({
      fol_formula: 'Love(Alice, Bob)',
      confidence: 0.8,
      fallback_used: false,
    });
    expect(implication).toMatchObject({
      fol_formula: '(∀x (Tenants(x) → Residents(x)) → ∃x (Tenants(x) ∧ Protected(x)))',
      fallback_used: false,
    });
    expect(bridge.get_statistics()).toMatchObject({
      sourcePythonModule: 'logic/integration/converters/symbolic_fol_bridge.py',
      source_python_module: 'logic/integration/converters/symbolic_fol_bridge.py',
      serverCallsAllowed: false,
      pythonRuntime: false,
      cache_size: 2,
    });
  });

  it('ports integration/symbolic_fol_bridge.py with root-module metadata and local caching', () => {
    const bridge = createBrowserNativeRootSymbolicFOLBridge({ confidenceThreshold: 0.6 });

    const result = bridge.convert_to_fol(
      'If all tenants are residents then some tenants are protected',
    );
    const cached = bridge.semantic_to_fol(
      bridge.create_semantic_symbol('If all tenants are residents then some tenants are protected'),
    );
    const stats = bridge.get_statistics();

    expect(result).toMatchObject({
      fol_formula: '(∀x (Tenants(x) → Residents(x)) → ∃x (Tenants(x) ∧ Protected(x)))',
      confidence: 0.8,
      fallback_used: false,
      errors: [],
    });
    expect(cached).toBe(result);
    expect(stats).toMatchObject({
      sourcePythonModule: 'logic/integration/symbolic_fol_bridge.py',
      source_python_module: 'logic/integration/symbolic_fol_bridge.py',
      runtime: 'typescript-wasm-browser',
      serverCallsAllowed: false,
      pythonRuntime: false,
      symbolic_ai_available: false,
      fallback_available: true,
      confidence_threshold: 0.6,
      cache_size: 1,
      total_conversions: 1,
    });
  });

  it('accepts injectable browser-native prover adapters for bridge contract tests', () => {
    const adapter: BrowserNativeProofAdapter = {
      metadata: {
        logic: 'tdfol',
        name: 'test-local-adapter',
        runtime: 'typescript-wasm-browser',
        requiresExternalProver: false,
      },
      supports: (logic) => logic === 'tdfol',
      prove: (request) => ({
        status: 'proved',
        theorem: request.theorem,
        steps: [],
        method: 'injected-local-proof',
      }),
    };
    const router = new BrowserNativeProverRouter([adapter]);

    const result = router.prove({ logic: 'tdfol', theorem: 'opaque theorem', axioms: [] });

    expect(router.listAdapters()).toEqual([adapter.metadata]);
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'opaque theorem',
      method: 'adapter:test-local-adapter:injected-local-proof',
    });
  });

  it('ports base_prover_bridge.py as a browser-native fail-closed adapter wrapper', () => {
    const adapter: BrowserNativeProofAdapter = {
      metadata: {
        logic: 'tdfol',
        name: 'base-test-local-adapter',
        runtime: 'typescript-wasm-browser',
        requiresExternalProver: false,
      },
      supports: (logic) => logic === 'tdfol',
      prove: (request) => ({
        status: 'proved',
        theorem: request.theorem,
        steps: [],
        method: 'local-proof',
      }),
    };
    const bridge = createBrowserNativeBaseProverBridge(adapter);

    const validation = bridge.validateRequest({
      logic: 'tdfol',
      theorem: '  Resident(Ada)  ',
      axioms: [' Resident(Ada) ', ''],
    });
    const result = bridge.prove({
      logic: 'tdfol',
      theorem: '  Resident(Ada)  ',
      axioms: [' Resident(Ada) ', ''],
    });

    expect(bridge.getMetadata()).toMatchObject({
      sourcePythonModule: 'logic/integration/base_prover_bridge.py',
      runtime: 'typescript-wasm-browser',
      serverCallsAllowed: false,
      pythonRuntime: false,
      subprocessAllowed: false,
      rpcAllowed: false,
      externalProverAllowed: false,
      failClosed: true,
      supportedLogics: ['tdfol'],
      name: 'base-test-local-adapter',
    });
    expect(bridge.getProverInfo()).toMatchObject({
      available: true,
      requiresExternalProver: false,
      sourcePythonModule: 'logic/integration/base_prover_bridge.py',
    });
    expect(validation.normalizedRequest).toMatchObject({
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'base-prover-bridge:base-test-local-adapter:local-proof',
    });
    expect(() => bridge.prove({ logic: 'cec', theorem: 'p', axioms: [] })).toThrow(
      'Invalid browser-native proof request: unsupported logic: cec',
    );
  });

  it('ports integration/bridges/base_prover_bridge.py as a browser-native local adapter base', () => {
    const adapter: BrowserNativeProofAdapter = {
      metadata: {
        logic: 'dcec',
        name: 'nested-base-test-adapter',
        runtime: 'typescript-wasm-browser',
        requiresExternalProver: false,
      },
      supports: (logic) => logic === 'dcec',
      prove: (request) => ({
        status: 'proved',
        theorem: request.theorem,
        steps: [],
        method: 'local-dcec-proof',
      }),
    };
    const bridge = createBrowserNativeIntegrationBridgesBaseProverBridge(adapter);

    const result = bridge.prove({
      logic: 'dcec',
      theorem: '  (P (always (comply_with ada code)))  ',
      axioms: [' (P (always (comply_with ada code))) '],
      maxSteps: 20,
    });

    expect(bridge.getMetadata()).toMatchObject({
      sourcePythonModule: 'logic/integration/bridges/base_prover_bridge.py',
      runtime: 'typescript-wasm-browser',
      serverCallsAllowed: false,
      pythonRuntime: false,
      subprocessAllowed: false,
      rpcAllowed: false,
      externalProverAllowed: false,
      failClosed: true,
      supportedLogics: ['dcec'],
    });
    expect(bridge.getProverInfo()).toMatchObject({
      available: true,
      requiresExternalProver: false,
      sourcePythonModule: 'logic/integration/bridges/base_prover_bridge.py',
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: '(P (always (comply_with ada code)))',
      method: 'integration-bridges-base-prover-bridge:nested-base-test-adapter:local-dcec-proof',
    });
    expect(() => bridge.prove({ logic: 'dcec', theorem: 'p', axioms: [], maxSteps: 0 })).toThrow(
      'Invalid browser-native proof request: maxSteps must be positive',
    );
  });

  it('ports integration/bridges/external_provers.py as a browser-native prover facade', () => {
    const bridge = createBrowserNativeExternalProversBridge();
    const result = bridge.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
      prover: 'z3',
    }) as BrowserNativeZ3ProofResult;

    expect(bridge.metadata).toMatchObject({
      sourcePythonModule: 'logic/integration/bridges/external_provers.py',
      runtime: 'typescript-wasm-browser',
      serverCallsAllowed: false,
      pythonRuntime: false,
      subprocessAllowed: false,
      rpcAllowed: false,
      filesystemAllowed: false,
      failClosed: true,
    });
    expect(result).toMatchObject({
      status: 'proved',
      theorem: 'Resident(Ada)',
      method: 'integration-external-provers:z3:z3-compatible:tdfol-forward-chaining',
    });
    expect(result.z3.serverCallsAllowed).toBe(false);
    expect(bridge.supports('auto', 'dcec')).toBe(true);
    expect(bridge.supports('lean', 'cec')).toBe(false);
  });

  it('routes coq through its local adapter and fails closed for bridge names without local WASM adapters', () => {
    const bridge = createBrowserNativeExternalProversBridge();
    const result = bridge.prove({
      logic: 'tdfol',
      theorem: 'Resident(Ada)',
      axioms: ['Resident(Ada)'],
      prover: 'coq',
    }) as BrowserNativeCoqProofResult;

    expect(bridge.getProverInfo('coq')).toMatchObject({
      name: 'coq',
      available: true,
      requiresExternalProver: false,
      supportedLogics: ['tdfol'],
    });
    expect(result.method).toBe(
      'integration-external-provers:coq:coq-compatible:tdfol-forward-chaining',
    );
    expect(result.coq.serverCallsAllowed).toBe(false);
    expect(result.coq.wasmRuntime).toBe('not-bundled');
    expect(result.coq.coqWasmAvailable).toBe(false);
    expect(bridge.supports('coq', 'cec')).toBe(false);
    expect(() =>
      bridge.prove({
        logic: 'tdfol',
        theorem: 'Resident(Ada)',
        axioms: ['Resident(Ada)'],
        prover: 'vampire',
      }),
    ).toThrow('no Python, subprocess, RPC, or server fallback is available');
  });

  it('ports prover_installer.py as a browser-native local adapter catalog', () => {
    const installer = createBrowserNativeProverInstaller();
    const eProverPlan = installer.planInstall('e-prover');

    expect(installer.metadata.sourcePythonModule).toBe(
      'logic/integration/bridges/prover_installer.py',
    );
    expect(installer.metadata).toMatchObject({
      runtime: 'typescript-wasm-browser',
      serverCallsAllowed: false,
      pythonRuntime: false,
      subprocessAllowed: false,
      filesystemAllowed: false,
      packageManagerAllowed: false,
    });
    expect(eProverPlan).toMatchObject({
      status: 'already-local',
      target: {
        name: 'e-prover',
        available: true,
        installableInBrowser: false,
        localAdapter: 'browser-native-e-prover-adapter',
        supportedLogics: ['tdfol'],
      },
    });
    expect(eProverPlan.target.blockedOperations).toContain('subprocess');
  });

  it('fails closed for prover_installer.py targets without bundled browser adapters', () => {
    const installer = createBrowserNativeProverInstaller();
    const coqPlan = installer.planInstall('coq');

    expect(coqPlan).toMatchObject({
      status: 'blocked',
      target: {
        name: 'coq',
        available: false,
        installableInBrowser: false,
        localAdapter: null,
      },
    });
    expect(() => installer.install('coq')).toThrow('coq cannot be installed from browser code');
  });

  it('returns explicit unsupported conversion results for missing local routes', () => {
    const bridge = createBrowserNativeLogicBridge();
    const result = bridge.convert('Resident(Ada)', 'fol', 'deontic');

    expect(result).toMatchObject({
      status: 'unsupported',
      targetFormula: '',
      warnings: ['Unsupported browser-native conversion route: fol -> deontic'],
    });
    expect(result.metadata).toMatchObject({ server_calls_allowed: false });
  });
});
