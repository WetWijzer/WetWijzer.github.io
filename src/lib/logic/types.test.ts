import {
  BRIDGE_CAPABILITIES,
  BridgeConfig,
  BridgeMetadata,
  COMMON_TYPES_PORT_METADATA,
  FORMULA_TYPE_VALUES,
  LOGIC_OPERATOR_SYMBOLS,
  QUANTIFIER_SYMBOLS,
  complexityMetricsToDict,
  createComplexityMetrics,
  formulaProtocolComplexity,
  formulaProtocolToString,
  getLogicOperatorSymbol,
  getQuantifierSymbol,
  isCommonLogicOperator,
  isFormulaType,
  isQuantifier,
  FOLConversionResultType,
  FOL_TYPES_PORT_METADATA,
  FOLFormulaType,
  LogicBridgeConversionResult,
  PredicateExtractionType,
  PredicateType,
  ProverRecommendation,
  TranslationResultType,
  AbstractLogicFormulaType,
  BRIDGE_TYPES_PORT_METADATA,
  bridgeConfigFromDict,
  bridgeConversionResultFromDict,
  bridgeMetadataFromDict,
  folConversionResultTypeFromDict,
  folFormulaTypeFromDict,
  predicateExtractionTypeFromDict,
  predicateTypeFromDict,
  proverRecommendationFromDict,
  validateBridgeTypesPort,
  validateFolTypesPort,
} from './types';

describe('logic shared type parity helpers', () => {
  it('exposes common_types.py enum values and browser-native metadata', () => {
    expect(COMMON_TYPES_PORT_METADATA).toEqual({
      sourcePythonModule: 'logic/types/common_types.py',
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      runtimeDependencies: [],
    });
    expect(LOGIC_OPERATOR_SYMBOLS).toMatchObject({
      AND: '∧',
      OR: '∨',
      NOT: '¬',
      IMPLIES: '→',
      IFF: '↔',
      EXISTS: '∃',
      FORALL: '∀',
    });
    expect(QUANTIFIER_SYMBOLS).toMatchObject({
      UNIVERSAL: '∀',
      EXISTENTIAL: '∃',
    });
    expect(FORMULA_TYPE_VALUES).toMatchObject({
      FOL: 'first_order_logic',
      MODAL: 'modal_logic',
      TEMPORAL: 'temporal_logic',
      DEONTIC: 'deontic_logic',
      MIXED: 'mixed_logic',
    });
    expect(isCommonLogicOperator('XOR')).toBe(false);
    expect(isCommonLogicOperator('FORALL')).toBe(true);
    expect(isQuantifier('UNIVERSAL')).toBe(true);
    expect(isFormulaType('first_order_logic')).toBe(true);
    expect(getLogicOperatorSymbol('EXISTS')).toBe('∃');
    expect(getQuantifierSymbol('EXISTENTIAL')).toBe('∃');
  });

  it('serializes complexity metrics using Python-compatible field names', () => {
    const metrics = createComplexityMetrics({
      quantifierDepth: 2,
      nestingLevel: 3,
      operatorCount: 4,
      variableCount: 5,
      predicateCount: 6,
      complexityScore: 7.9,
    });

    expect(complexityMetricsToDict(metrics)).toEqual({
      quantifier_depth: 2,
      nesting_level: 3,
      operator_count: 4,
      variable_count: 5,
      predicate_count: 6,
      complexity_score: 7,
    });
  });

  it('supports Python protocol method names without runtime bridges', () => {
    const formula = {
      to_string: () => '∀x Tenant(x)',
      get_complexity: () =>
        createComplexityMetrics({
          quantifierDepth: 1,
          predicateCount: 1,
          complexityScore: 12,
        }),
    };

    expect(formulaProtocolToString(formula)).toBe('∀x Tenant(x)');
    expect(complexityMetricsToDict(formulaProtocolComplexity(formula))).toMatchObject({
      quantifier_depth: 1,
      predicate_count: 1,
      complexity_score: 12,
    });
  });

  it('models bridge metadata, config, conversion results, and recommendations', () => {
    const metadata = new BridgeMetadata(
      'tdfol-cec',
      '1.0',
      'CEC',
      [BRIDGE_CAPABILITIES.BIDIRECTIONAL_CONVERSION, BRIDGE_CAPABILITIES.RULE_EXTRACTION],
      false,
      'Browser-native bridge',
    );
    const result = new LogicBridgeConversionResult(
      'partial',
      'O(Pay(x))',
      '(obligatory (pay x))',
      'tdfol',
      'cec',
      0.8,
      ['temporal projection omitted'],
      { browser_native: true },
    );
    const config = new BridgeConfig('tdfol-cec', 'CEC', 10, 1, true, 30, { mode: 'local' });
    const recommendations = [
      new ProverRecommendation('slow', 0.4, ['fallback']),
      new ProverRecommendation('fast', 0.9, ['native']),
    ].sort((left, right) => left.compare(right));

    expect(metadata.supportsCapability('rule_extraction')).toBe(true);
    expect(metadata.toDict()).toMatchObject({
      target_system: 'CEC',
      requires_external_prover: false,
    });
    expect(result.isSuccessful()).toBe(false);
    expect(result.hasWarnings()).toBe(true);
    expect(result.toDict()).toMatchObject({ status: 'partial', source_format: 'tdfol' });
    expect(config.getSetting('mode')).toBe('local');
    expect(config.toDict()).toMatchObject({ max_retries: 1, cache_ttl: 30 });
    expect(recommendations.map((item) => item.proverName)).toEqual(['fast', 'slow']);
  });

  it('hydrates and validates bridge_types.py dict-compatible browser-native records', () => {
    expect(BRIDGE_TYPES_PORT_METADATA.sourcePythonModule).toBe('logic/types/bridge_types.py');
    expect(
      bridgeMetadataFromDict({
        name: 'browser-native-logic-bridge',
        version: '0.1.0-ts',
        target_system: 'typescript-wasm-browser',
        capabilities: ['bidirectional', 'rule_extraction', 'server_rpc'],
        requires_external_prover: false,
        description: 'Local deterministic bridge',
      }).toDict(),
    ).toMatchObject({
      target_system: 'typescript-wasm-browser',
      capabilities: ['bidirectional', 'rule_extraction'],
      requires_external_prover: false,
    });
    expect(
      bridgeConversionResultFromDict({
        status: 'success',
        source_formula: 'P(x)',
        target_formula: '(P x)',
        source_format: 'fol',
        target_format: 'cec',
        metadata: { server_calls_allowed: false },
      }).toDict(),
    ).toMatchObject({ status: 'success', source_formula: 'P(x)', confidence: 1 });
    expect(
      bridgeConfigFromDict({
        name: 'local',
        target_system: 'cec',
        max_retries: 2,
        enable_caching: false,
        custom_settings: { wasm: true },
      }).toDict(),
    ).toMatchObject({ max_retries: 2, enable_caching: false, custom_settings: { wasm: true } });
    expect(
      proverRecommendationFromDict({
        prover_name: 'cec-local',
        confidence: 0.92,
        reasons: ['browser native'],
        estimated_time: 12,
      }).toDict(),
    ).toEqual({
      prover_name: 'cec-local',
      confidence: 0.92,
      reasons: ['browser native'],
      estimated_time: 12,
    });
    expect(
      validateBridgeTypesPort({
        capabilities: ['parallel'],
        status: 'partial',
        server_calls_allowed: false,
        python_runtime_allowed: false,
      }),
    ).toMatchObject({ valid: true, metadata: BRIDGE_TYPES_PORT_METADATA });
    expect(
      validateBridgeTypesPort({
        capabilities: ['server_rpc'],
        status: 'remote',
        server_calls_allowed: true,
      }),
    ).toMatchObject({ valid: false });
  });

  it('models FOL type dataclasses and predicate extraction helpers', () => {
    const tenant = new PredicateType('Tenant', 1, 'entity');
    const pays = new PredicateType('PaysRent', 2, 'action');
    const formula = new FOLFormulaType(
      '∀x Tenant(x)',
      [tenant, pays],
      ['FORALL'],
      ['AND'],
      ['x'],
      undefined,
      0.91,
    );
    const conversion = new FOLConversionResultType(
      'All tenants pay rent',
      formula,
      'tptp',
      'fof(rule, axiom, ...).',
      0.91,
    );
    const extraction = new PredicateExtractionType(
      'All tenants pay rent',
      { entity: [tenant], action: [pays] },
      2,
      0.87,
    );

    expect(tenant.toString()).toBe('Tenant(x0)');
    expect(pays.toString()).toBe('PaysRent(x0, x1)');
    expect(formula.getPredicateNames()).toEqual(['Tenant', 'PaysRent']);
    expect(formula.hasQuantifiers()).toBe(true);
    expect(conversion.isHighConfidence()).toBe(true);
    expect(extraction.getAllPredicates()).toEqual([tenant, pays]);
  });

  it('hydrates fol_types.py dict-compatible records without server or Python dependencies', () => {
    expect(FOL_TYPES_PORT_METADATA.sourcePythonModule).toBe('logic/types/fol_types.py');
    expect(FOL_TYPES_PORT_METADATA.runtimeDependencies).toEqual([]);

    const predicate = predicateTypeFromDict({ name: 'Tenant', arity: 1, category: 'entity' });
    const formula = folFormulaTypeFromDict({
      formula_string: '∀x (Tenant(x) → PaysRent(x))',
      predicates: [predicate.toDict(), { name: 'PaysRent', arity: 1, category: 'action' }],
      quantifiers: ['FORALL', 'INVALID'],
      operators: ['IMPLIES', 'XOR', 'REMOTE_CALL'],
      variables: ['x'],
      complexity: { quantifier_depth: 1, complexity_score: 7.8 },
      confidence: 0.93,
      metadata: { source: 'fixture' },
    });
    const conversion = folConversionResultTypeFromDict({
      source_text: 'All tenants pay rent',
      fol_formula: formula.toDict(),
      output_format: 'tptp',
      formatted_output: 'fof(rule, axiom, (! [X] : (tenant(X) => paysrent(X)))).',
      confidence: 0.93,
      warnings: ['normalized predicate names'],
      metadata: { browser_native: true },
    });
    const extraction = predicateExtractionTypeFromDict({
      text: 'All tenants pay rent',
      predicates_by_category: {
        entity: [predicate.toDict()],
        action: [{ name: 'PaysRent', arity: 1, category: 'action' }],
      },
      total_predicates: 2,
      confidence: 0.88,
    });

    expect(predicate.toDict()).toMatchObject({ category: 'entity' });
    expect(formula.getPredicateNames()).toEqual(['Tenant', 'PaysRent']);
    expect(formula.operators).toEqual(['IMPLIES', 'XOR']);
    expect(formula.toDict()).toMatchObject({
      formula_string: '∀x (Tenant(x) → PaysRent(x))',
      complexity: { quantifier_depth: 1, complexity_score: 7 },
      metadata: { source: 'fixture' },
    });
    expect(conversion.toDict()).toMatchObject({
      source_text: 'All tenants pay rent',
      output_format: 'tptp',
      confidence: 0.93,
      metadata: { browser_native: true },
    });
    expect(extraction.getAllPredicates().map((item) => item.name)).toEqual(['Tenant', 'PaysRent']);
    expect(extraction.toDict()).toMatchObject({ total_predicates: 2, confidence: 0.88 });
    expect(validateFolTypesPort({ output_format: 'json', category: 'relation' })).toMatchObject({
      valid: true,
      metadata: FOL_TYPES_PORT_METADATA,
    });
    expect(
      validateFolTypesPort({
        output_format: 'remote',
        category: 'server',
        server_calls_allowed: true,
        python_runtime_allowed: true,
      }),
    ).toMatchObject({ valid: false });
  });

  it('serializes translation result and abstract formula shapes', () => {
    const translation = new TranslationResultType(
      'z3',
      '(assert P)',
      false,
      0.4,
      ['unsupported modal'],
      ['projection'],
      { local: true },
      ['prelude'],
    );
    const abstract = new AbstractLogicFormulaType(
      'deontic_logic',
      ['O', '→'],
      [['x', 'Agent']],
      [['∀', 'x', 'Agent']],
      ['ComplyWith(x, code)'],
      { root: 'obligation' },
      'formula-1',
    );

    expect(translation.toDict()).toEqual({
      target: 'z3',
      translated_formula: '(assert P)',
      success: false,
      confidence: 0.4,
      errors: ['unsupported modal'],
      warnings: ['projection'],
      metadata: { local: true },
      dependencies: ['prelude'],
    });
    expect(abstract.toDict()).toMatchObject({
      formula_type: 'deontic_logic',
      source_formula_id: 'formula-1',
      logical_structure: { root: 'obligation' },
    });
  });
});
