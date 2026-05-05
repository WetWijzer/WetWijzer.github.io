import { LogicValidationError } from '../errors';
import { AUDIT_LOG_METADATA, AuditLogger, logProofAttempt, setAuditLogger } from './auditLog';
import {
  CircuitBreakerOpenError,
  getCircuitBreaker,
  LLMCircuitBreaker,
  resetAllCircuitBreakers,
} from './circuitBreaker';
import {
  INPUT_VALIDATION_METADATA,
  InputValidator,
  sanitizeInput,
  validateFormulaList,
  validateSafeInput,
  validateText,
} from './inputValidation';
import { RateLimitExceeded, RateLimiter, rateLimit, setRateLimiter } from './rateLimiting';

describe('logic security browser-native parity helpers', () => {
  afterEach(() => {
    setAuditLogger(undefined);
    setRateLimiter(undefined);
    resetAllCircuitBreakers();
  });

  it('validates text, formulas, and formula lists with Python-style errors', () => {
    const validator = new InputValidator();

    expect(validator.metadata).toEqual(INPUT_VALIDATION_METADATA);
    expect(validator.validateText('Legal text')).toBe('Legal text');
    expect(validator.validateFormula('P(x)')).toBe('P(x)');
    expect(validator.validateFormulaList(['P(x)', 'Q(y)'])).toEqual(['P(x)', 'Q(y)']);

    expect(() => validateText('')).toThrow(LogicValidationError);
    expect(() => validateText('bad\u0001text')).toThrow('control characters');
    expect(() => validateText('<script>alert(1)</script>')).toThrow('unsafe input pattern');
    expect(() => validateText('abcd', { maxLength: 3 })).toThrow('exceeds maximum length');
    expect(() => validateFormulaList('P(x)')).toThrow("'formulas' must be iterable");
    expect(() => validateFormulaList(['P(x)', ''])).toThrow("'formulas[1]' must not be empty.");
  });

  it('sanitizes browser-local input without server or Python runtime dependencies', () => {
    expect(INPUT_VALIDATION_METADATA).toMatchObject({
      sourcePythonModule: 'logic/security/input_validation.py',
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });

    expect(sanitizeInput('  <b>Permit</b>\u0000  ')).toEqual({
      value: '&lt;b&gt;Permit&lt;/b&gt;',
      changed: true,
      removed: ['control:0'],
    });
    expect(validateSafeInput('  Permit & deny  ')).toBe('Permit &amp; deny');
    expect(() => validateSafeInput('javascript:alert(1)')).toThrow('unsafe input pattern');
    expect(() => sanitizeInput(42)).toThrow(LogicValidationError);
  });

  it('rate limits by user with sliding-window reset and wrapper support', () => {
    let now = 0;
    const limiter = new RateLimiter(2, 10, () => now);

    limiter.checkRateLimit('ada');
    limiter.checkRateLimit('ada');
    expect(limiter.getRemaining('ada')).toBe(0);
    expect(() => limiter.checkRateLimit('ada')).toThrow(RateLimitExceeded);

    now = 11;
    expect(limiter.getRemaining('ada')).toBe(2);
    expect(
      limiter.wrap(
        (value: number) => value + 1,
        () => 'bob',
      )(1),
    ).toBe(2);

    setRateLimiter(new RateLimiter(1, 60, () => 0));
    const guarded = rateLimit(() => 'ok');
    expect(guarded()).toBe('ok');
    expect(() => guarded()).toThrow(RateLimitExceeded);
  });

  it('opens, half-opens, recovers, and reports circuit-breaker metrics', () => {
    let now = 0;
    const breaker = new LLMCircuitBreaker({
      failureThreshold: 2,
      successThreshold: 2,
      timeoutSeconds: 5,
      name: 'test',
      now: () => now,
    });

    expect(() =>
      breaker.call(() => {
        throw new Error('boom');
      }),
    ).toThrow('boom');
    expect(() =>
      breaker.call(() => {
        throw new Error('boom');
      }),
    ).toThrow('boom');
    expect(breaker.state).toBe('open');
    expect(() => breaker.call(() => 'blocked')).toThrow(CircuitBreakerOpenError);

    now = 6;
    expect(breaker.refreshState()).toBe('half_open');
    expect(breaker.call(() => 'first')).toBe('first');
    expect(breaker.state).toBe('half_open');
    expect(breaker.call(() => 'second')).toBe('second');
    expect(breaker.state).toBe('closed');
    expect(breaker.getStats()).toMatchObject({
      name: 'test',
      metrics: {
        total_calls: 4,
        successes: 2,
        failures: 2,
        state_transitions: 3,
      },
    });
  });

  it('uses fallback and global circuit-breaker registry', () => {
    const breaker = new LLMCircuitBreaker({
      failureThreshold: 1,
      fallback: () => 'fallback',
      name: 'fallback',
    });

    expect(() =>
      breaker.call(() => {
        throw new Error('fail');
      }),
    ).toThrow('fail');
    expect(breaker.call(() => 'blocked')).toBe('fallback');
    expect(getCircuitBreaker('shared')).toBe(getCircuitBreaker('shared'));
    expect(resetAllCircuitBreakers()).toBeGreaterThanOrEqual(1);
  });

  it('records in-memory audit events and JSON-lines export', () => {
    const logger = new AuditLogger(() => '2026-01-01T00:00:00.000Z');
    setAuditLogger(logger);

    logger.logSecurityEvent('ada', 'validation_error', 'low', 'Bad formula', { field: 'formula' });
    logger.logRateLimitExceeded('ada', 2, 60);
    logger.logValidationError('ada', 'formula', 'empty');
    logProofAttempt('ada', 'P('.repeat(80), 'browser-prover', false, 12, false, 'parse error');

    expect(logger.events).toHaveLength(4);
    expect(logger.events[3].details).toMatchObject({
      prover: 'browser-prover',
      duration_ms: 12,
      cached: false,
      error: 'parse error',
    });
    expect((logger.events[3].details?.formula as string).length).toBe(100);
    expect(logger.toJsonLines().split('\n')).toHaveLength(4);
  });

  it('ports audit_log.py metadata, listeners, filtering, and bounded memory storage', () => {
    const observed: Array<string> = [];
    const logger = new AuditLogger({
      now: () => '2026-01-01T00:00:00.000Z',
      maxEvents: 2,
      listeners: [(event) => observed.push(event.event_type)],
    });

    expect(logger.metadata).toEqual(AUDIT_LOG_METADATA);
    expect(logger.metadata).toMatchObject({
      sourcePythonModule: 'logic/security/audit_log.py',
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      storage: 'memory',
    });

    const unsubscribe = logger.addEventListener((event) =>
      observed.push(`extra:${event.event_type}`),
    );
    logger.logEvent(
      'proof_attempt',
      'ada',
      true,
      { prover: 'browser-prover' },
      { request_id: 'r1' },
    );
    unsubscribe();
    logger.logSecurityEvent('bob', 'validation_error', 'low', 'Bad formula');
    logger.logValidationError('ada', 'formula', 'empty');

    expect(logger.events.map((event) => event.event_type)).toEqual([
      'security.validation_error',
      'security.validation_error',
    ]);
    expect(observed).toEqual([
      'proof_attempt',
      'extra:proof_attempt',
      'security.validation_error',
      'security.validation_error',
    ]);
    expect(logger.getEvents({ userId: 'ada', limit: 1 })).toEqual([
      expect.objectContaining({
        event_type: 'security.validation_error',
        user_id: 'ada',
        success: false,
      }),
    ]);
    expect(JSON.parse(logger.toJson())).toHaveLength(2);
  });
});
