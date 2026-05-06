import { dcecAtom } from './dcecCore';
import {
  adaptCecValidationResult,
  CecConversionError,
  CecError,
  CecGrammarError,
  CecKnowledgeBaseError,
  CecNamespaceError,
  CecParsingError,
  CecProvingError,
  CecValidationError,
  createCecRecoveryMetadata,
  createFailClosedCecValidationResult,
  DcecError,
  DcecParsingError,
  formatCecOperationError,
  handleCecParseError,
  handleCecProofError,
  runCecValidationAdapter,
  safeCecCall,
  validateCecNotNone,
  validateCecType,
  validateDcecFormulaLike,
  withCecErrorContext,
} from './cecErrors';

describe('CEC native error parity helpers', () => {
  it('formats base CEC errors with context and suggestions', () => {
    const error = new CecError(
      'Operation failed',
      { formula: 'O(p)', operation: 'prove' },
      'Check formula syntax',
    );

    expect(error).toBeInstanceOf(DcecError);
    expect(error.message).toContain('formula=O(p)');
    expect(error.message).toContain('operation=prove');
    expect(error.message).toContain('Check formula syntax');
    expect(error.context).toEqual({ formula: 'O(p)', operation: 'prove' });
  });

  it('models Python-specific CEC exception constructors', () => {
    const parse = new CecParsingError('Invalid operator', 'O((p)', 4, 'closing parenthesis', 'Add )');
    const proof = new CecProvingError('Rule failed', 'O(p)', 3, 'modus_ponens');
    const conversion = new CecConversionError('No pattern matched', 'agent must act', 'en', 'obligation');
    const validation = new CecValidationError('Invalid sort', 'unknown', 'Sort', 'defined sort');
    const namespace = new CecNamespaceError('Symbol not found', 'predicate_p', 'lookup');
    const grammar = new CecGrammarError('Grammar failed', 'obligation_rule', 'must act');
    const kb = new CecKnowledgeBaseError('Formula exists', 'add', 'f123');

    expect(parse).toBeInstanceOf(DcecParsingError);
    expect(parse.context).toMatchObject({ expression: 'O((p)', position: 4, expected: 'closing parenthesis' });
    expect(proof.context).toMatchObject({ formula: 'O(p)', proof_step: 3, rule: 'modus_ponens' });
    expect(conversion.context).toMatchObject({ text: 'agent must act', language: 'en', pattern: 'obligation' });
    expect(validation.context).toMatchObject({ value: 'unknown', expected_type: 'Sort', constraint: 'defined sort' });
    expect(namespace.context).toMatchObject({ symbol: 'predicate_p', operation: 'lookup' });
    expect(grammar.context).toMatchObject({ rule: 'obligation_rule', input_text: 'must act' });
    expect(kb.context).toMatchObject({ operation: 'add', formula_id: 'f123' });
  });

  it('wraps proof and parse operations with default return behavior', () => {
    const proof = handleCecProofError(() => {
      throw new Error('boom');
    }, { defaultReturn: 'failed' });
    const parse = handleCecParseError(() => {
      throw new Error('bad input');
    }, { defaultReturn: null });

    expect(proof()).toBe('failed');
    expect(parse()).toBeNull();
  });

  it('rethrows wrapped proof and parse errors with operation context', () => {
    const proof = handleCecProofError(() => {
      throw new Error('boom');
    }, { reraise: true, context: 'Modal proof' });
    const parse = handleCecParseError(() => {
      throw new Error('bad input');
    }, { reraise: true, context: 'Temporal parsing' });

    expect(() => proof()).toThrow(CecProvingError);
    expect(() => proof()).toThrow('Modal proof');
    expect(() => parse()).toThrow(CecParsingError);
    expect(() => parse()).toThrow('Temporal parsing');
  });

  it('adds generic context and safely calls fallible functions', () => {
    const wrapped = withCecErrorContext(() => {
      throw new Error('invalid formula');
    }, 'Formula validation');
    const logMessages: string[] = [];
    const logger = {
      error(message?: unknown): void {
        logMessages.push(String(message));
      },
      debug(message?: unknown): void {
        logMessages.push(String(message));
      },
    };
    const result = safeCecCall(() => {
      throw new Error('optional failure');
    }, [], [], logger);

    expect(() => wrapped()).toThrow('Formula validation');
    expect(result).toEqual([]);
    expect(logMessages.some((message) => message.includes('optional failure'))).toBe(true);
    expect(logMessages.length).toBeGreaterThan(1);
  });

  it('formats operation errors and validates common input patterns', () => {
    expect(formatCecOperationError(new Error('missing premise'), 'theorem proving', {
      formula: 'p',
      prover: 'modal',
    })).toContain('Details: formula=p, prover=modal');

    expect(() => validateCecNotNone(undefined, 'formula')).toThrow(CecValidationError);
    expect(() => validateCecType(7, 'string', 'agent')).toThrow(CecValidationError);
    expect(() => validateDcecFormulaLike(undefined)).toThrow(CecValidationError);
    expect(() => validateDcecFormulaLike(undefined, true)).not.toThrow();
    expect(() => validateDcecFormulaLike(dcecAtom('p'))).not.toThrow();
  });

  it('creates fail-closed recovery metadata for CEC validation failures', () => {
    const error = new CecValidationError(
      'Invalid CEC value',
      'agent',
      'Formula',
      'DCEC formula-like object',
      'Pass a parsed formula',
    );
    const recovery = createCecRecoveryMetadata(error, 'validateFormula', { formula: 'agent' });
    const result = createFailClosedCecValidationResult(error, 'validateFormula', { formula: 'agent' });

    expect(recovery.metadata.sourcePythonModule).toBe('logic/CEC/native/error_handling.py');
    expect(recovery.errorKind).toBe('validation');
    expect(recovery.failClosed).toBe(true);
    expect(recovery.context).toMatchObject({
      formula: 'agent',
      value: 'agent',
      expected_type: 'Formula',
    });
    expect(result).toMatchObject({
      ok: false,
      valid: false,
      metadata: { recoveryPolicy: 'fail-closed' },
    });
    expect(result.recovery?.suggestion).toBe('Pass a parsed formula');
    expect(result.errors[0]).toContain('validateFormula failed closed');
  });

  it('adapts validation results and catches thrown validation operations', () => {
    expect(adaptCecValidationResult({ valid: true, warnings: ['normalized'] })).toMatchObject({
      ok: true,
      valid: true,
      warnings: ['normalized'],
    });

    expect(adaptCecValidationResult({ ok: false, errors: ['bad arity'] })).toMatchObject({
      ok: false,
      valid: false,
      errors: ['bad arity'],
    });

    const thrown = runCecValidationAdapter('namespace.validate', () => {
      throw new CecNamespaceError('Duplicate symbol', 'Happens', 'register');
    });

    expect(thrown.ok).toBe(false);
    expect(thrown.recovery?.errorKind).toBe('namespace');
    expect(thrown.recovery?.context).toMatchObject({ symbol: 'Happens', operation: 'register' });
    expect(thrown.errors[0]).toContain('namespace.validate failed closed');
  });
});
