import {
  CEC_EVENT_CALCULUS_RUNTIME,
  CecEventCalculus,
  CecTimePoint,
  Event,
  Fluent,
  TimePoint,
  createCecEventTerm,
  createCecFluentTerm,
  event,
  fluent,
  fluentsAt,
  happens,
  holds,
  initiates,
  terminates,
  timeline,
} from './eventCalculus';
import { parseCecExpression } from './parser';

describe('CEC event calculus', () => {
  it('records event occurrences and evaluates initiation/termination rules', () => {
    const ec = new CecEventCalculus();
    const turnOn = createCecEventTerm('turn_on_light');
    const turnOff = createCecEventTerm('turn_off_light');
    const lightOn = createCecFluentTerm('light_on');

    ec.addInitiationRule(turnOn, lightOn);
    ec.addTerminationRule(turnOff, lightOn);
    ec.recordEvent(turnOn, 2);
    ec.recordEvent(turnOff, 5);

    expect(ec.happens(turnOn, 2)).toBe(true);
    expect(ec.happens(turnOn, 3)).toBe(false);
    expect(ec.initiates(turnOn, lightOn, 2)).toBe(true);
    expect(ec.terminates(turnOff, lightOn, 5)).toBe(true);
  });

  it('exports Python-style event calculus helper queries', () => {
    const ec = new CecEventCalculus();
    const approve = event('approve', 'permit-17');
    const revoke = event('revoke', 'permit-17');
    const active = fluent('active', 'permit-17');

    ec.addInitiationRule(approve, active);
    ec.addTerminationRule(revoke, active);
    ec.recordEvent(approve, 1);
    ec.recordEvent(revoke, 4);

    expect(approve).toEqual(createCecEventTerm('approve', ['permit-17']));
    expect(active).toEqual(createCecFluentTerm('active', ['permit-17']));
    expect(happens(ec, approve, 1)).toBe(true);
    expect(initiates(ec, approve, active, 1)).toBe(true);
    expect(holds(ec, active, 2)).toBe(true);
    expect(terminates(ec, revoke, active, 4)).toBe(true);
    expect(fluentsAt(ec, 2)).toEqual([active]);
    expect(timeline(ec, active, 5)).toEqual([
      { time: 0, holds: false },
      { time: 2, holds: true },
      { time: 5, holds: false },
    ]);
  });

  it('exposes Python event_calculus.py constructors and snake_case API aliases', () => {
    const ec = new CecEventCalculus();
    const approve = new Event('approve', ['permit-17']);
    const revoke = new Event('revoke', ['permit-17']);
    const active = new Fluent('active', ['permit-17']);

    ec.add_initiation_rule(approve, active);
    ec.add_termination_rule(revoke, active);
    ec.record_event(approve, 1);
    ec.record_event(revoke, 4);

    expect(String(approve)).toBe('approve(permit-17)');
    expect(String(active)).toBe('active(permit-17)');
    expect(ec.holds_at(active, 2)).toBe(true);
    expect(ec.holds_at(active, 5)).toBe(false);
    expect([...ec.get_all_fluents_at(2)]).toEqual([createCecFluentTerm('active', ['permit-17'])]);
    expect(ec.get_timeline(active, 5)).toEqual([
      [0, false],
      [2, true],
      [5, false],
    ]);
    expect(new TimePoint(3).toString()).toBe('t3');
  });

  it('implements Python-compatible discrete HoldsAt and Clipped semantics', () => {
    const ec = new CecEventCalculus();
    ec.addInitiationRule('turn_on', 'light_on');
    ec.addTerminationRule('turn_off', 'light_on');
    ec.recordEvent('turn_on', 2);
    ec.recordEvent('turn_off', 5);

    expect(ec.holdsAt('light_on', 1)).toBe(false);
    expect(ec.holdsAt('light_on', 2)).toBe(false);
    expect(ec.holdsAt('light_on', 3)).toBe(true);
    expect(ec.holdsAt('light_on', 5)).toBe(true);
    expect(ec.holdsAt('light_on', 6)).toBe(false);
    expect(ec.clipped(3, 'light_on', 7)).toBe(true);
  });

  it('supports initially true fluents, all-fluent queries, and change timelines', () => {
    const ec = new CecEventCalculus();
    ec.setInitiallyTrue('door_closed');
    ec.addTerminationRule('open_door', 'door_closed');
    ec.recordEvent('open_door', 3);

    expect(ec.holdsAt('door_closed', 0)).toBe(true);
    expect(ec.holdsAt('door_closed', 4)).toBe(false);
    expect(ec.getAllFluentsAt(2)).toEqual([createCecFluentTerm('door_closed')]);
    expect(ec.getTimeline('door_closed', 5)).toEqual([
      { time: 0, holds: true },
      { time: 4, holds: false },
    ]);
  });

  it('supports release rules as explicit inertia breaks', () => {
    const ec = new CecEventCalculus();
    ec.setInitiallyTrue('permit_active');
    ec.addReleaseRule('suspend_permit', 'permit_active');
    ec.addInitiationRule('reinstate_permit', 'permit_active');
    ec.recordEvent('suspend_permit', 2);

    expect(ec.releases('suspend_permit', 'permit_active', 2)).toBe(true);
    expect(ec.releasedAt('permit_active', 3)).toBe(true);
    expect(ec.holdsAt('permit_active', 3)).toBe(false);

    ec.recordEvent('reinstate_permit', 5);
    expect(ec.releasedAt('permit_active', 6)).toBe(false);
    expect(ec.holdsAt('permit_active', 6)).toBe(true);
  });

  it('loads and evaluates CEC event-calculus predicates from parsed expressions', () => {
    const ec = new CecEventCalculus();
    [
      '(Initiates (turn_on light) (on light))',
      '(Terminates (turn_off light) (on light))',
      '(Happens (turn_on light) 2)',
      '(Happens (turn_off light) 5)',
    ].forEach((source) => expect(ec.loadFact(parseCecExpression(source))).toBe(true));

    expect(ec.evaluatePredicate(parseCecExpression('(HoldsAt (on light) 3)'))).toBe(true);
    expect(ec.evaluatePredicate(parseCecExpression('(Clipped 3 (on light) 7)'))).toBe(true);
    expect(ec.evaluatePredicate(parseCecExpression('(Happens (turn_on light) t2)'))).toBe(true);
    expect(
      ec.evaluatePredicate(parseCecExpression('(not (HoldsAt (on light) 3))')),
    ).toBeUndefined();
  });

  it('reports statistics, clears state, and validates time values', () => {
    const ec = new CecEventCalculus();
    ec.addInitiationRule('turn_on', 'light_on');
    ec.recordEvent('turn_on', 1);
    ec.holdsAt('light_on', 2);

    expect(ec.getStatistics()).toMatchObject({
      eventOccurrences: 1,
      initiationRules: 1,
      cachedHoldsAtQueries: 1,
    });

    expect(new CecTimePoint(3).toString()).toBe('t3');
    expect(() => ec.recordEvent('bad_time', -1)).toThrow('non-negative integer');
    expect(() => new CecTimePoint(1.5)).toThrow('non-negative integer');

    ec.clear();
    expect(ec.getStatistics()).toMatchObject({
      eventOccurrences: 0,
      initiationRules: 0,
      cachedHoldsAtQueries: 0,
    });
  });

  it('reports browser-native parity metadata for the Python event calculus module', () => {
    expect(CEC_EVENT_CALCULUS_RUNTIME).toMatchObject({
      sourcePythonModule: 'logic/CEC/native/event_calculus.py',
      browserNative: true,
      pythonRuntime: false,
      serverDelegation: false,
    });
    expect(CEC_EVENT_CALCULUS_RUNTIME.supportedPythonApi).toContain('record_event');
    expect(CEC_EVENT_CALCULUS_RUNTIME.supportedPredicates).toContain('holdsAt');
  });
});
