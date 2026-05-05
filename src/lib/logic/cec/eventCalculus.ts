import type { CecExpression } from './ast';

export interface CecEventTerm {
  name: string;
  parameters: readonly unknown[];
}

export interface CecFluentTerm {
  name: string;
  parameters: readonly unknown[];
}

export interface CecEventCalculusStats {
  eventOccurrences: number;
  initiationRules: number;
  terminationRules: number;
  releaseRules: number;
  initiallyTrue: number;
  cachedHoldsAtQueries: number;
}

export interface CecTimelineEntry {
  time: number;
  holds: boolean;
}

export interface CecEventCalculusRuntimeMetadata {
  sourcePythonModule: 'logic/CEC/native/event_calculus.py';
  browserNative: true;
  pythonRuntime: false;
  serverDelegation: false;
  supportedPredicates: readonly CecEventCalculusPredicate[];
  supportedPythonApi: readonly string[];
}

export type CecEventCalculusPredicate =
  | 'happens'
  | 'initiates'
  | 'terminates'
  | 'releases'
  | 'releasedAt'
  | 'holdsAt'
  | 'clipped';

export const CEC_EVENT_CALCULUS_RUNTIME: CecEventCalculusRuntimeMetadata = {
  sourcePythonModule: 'logic/CEC/native/event_calculus.py',
  browserNative: true,
  pythonRuntime: false,
  serverDelegation: false,
  supportedPredicates: [
    'happens',
    'initiates',
    'terminates',
    'releases',
    'releasedAt',
    'holdsAt',
    'clipped',
  ],
  supportedPythonApi: [
    'Event',
    'Fluent',
    'TimePoint',
    'record_event',
    'add_initiation_rule',
    'add_termination_rule',
    'set_initially_true',
    'holds_at',
    'get_all_fluents_at',
    'get_timeline',
  ],
};

export class Event implements CecEventTerm {
  readonly name: string;
  readonly parameters: readonly unknown[];

  constructor(name: string, parameters: readonly unknown[] = []) {
    const term = createCecEventTerm(name, parameters);
    this.name = term.name;
    this.parameters = term.parameters;
  }

  toString(): string {
    return formatPythonTerm(this);
  }
}

export class Fluent implements CecFluentTerm {
  readonly name: string;
  readonly parameters: readonly unknown[];

  constructor(name: string, parameters: readonly unknown[] = []) {
    const term = createCecFluentTerm(name, parameters);
    this.name = term.name;
    this.parameters = term.parameters;
  }

  toString(): string {
    return formatPythonTerm(this);
  }
}

export class CecTimePoint {
  readonly value: number;

  constructor(value: number) {
    assertTime(value);
    this.value = value;
  }

  toString(): string {
    return `t${this.value}`;
  }
}

export class TimePoint extends CecTimePoint {
  toString(): string {
    return super.toString();
  }
}

export class CecEventCalculus {
  private readonly eventOccurrences = new Set<string>();
  private readonly initiationRules = new Set<string>();
  private readonly terminationRules = new Set<string>();
  private readonly releaseRules = new Set<string>();
  private readonly initiallyTrue = new Set<string>();
  private readonly holdsAtCache = new Map<string, boolean>();

  recordEvent(event: CecEventTerm | string, time: number): void {
    assertTime(time);
    this.eventOccurrences.add(eventOccurrenceKey(toEventTerm(event), time));
    this.clearCache();
  }

  record_event(event: CecEventTerm | string, time: number): void {
    this.recordEvent(event, time);
  }

  happens(event: CecEventTerm | string, time: number): boolean {
    assertTime(time);
    return this.eventOccurrences.has(eventOccurrenceKey(toEventTerm(event), time));
  }

  addInitiationRule(event: CecEventTerm | string, fluent: CecFluentTerm | string): void {
    this.initiationRules.add(ruleKey(toEventTerm(event), toFluentTerm(fluent)));
    this.clearCache();
  }

  add_initiation_rule(event: CecEventTerm | string, fluent: CecFluentTerm | string): void {
    this.addInitiationRule(event, fluent);
  }

  initiates(event: CecEventTerm | string, fluent: CecFluentTerm | string, time: number): boolean {
    assertTime(time);
    return (
      this.initiationRules.has(ruleKey(toEventTerm(event), toFluentTerm(fluent))) &&
      this.happens(event, time)
    );
  }

  addTerminationRule(event: CecEventTerm | string, fluent: CecFluentTerm | string): void {
    this.terminationRules.add(ruleKey(toEventTerm(event), toFluentTerm(fluent)));
    this.clearCache();
  }

  add_termination_rule(event: CecEventTerm | string, fluent: CecFluentTerm | string): void {
    this.addTerminationRule(event, fluent);
  }

  terminates(event: CecEventTerm | string, fluent: CecFluentTerm | string, time: number): boolean {
    assertTime(time);
    return (
      this.terminationRules.has(ruleKey(toEventTerm(event), toFluentTerm(fluent))) &&
      this.happens(event, time)
    );
  }

  addReleaseRule(event: CecEventTerm | string, fluent: CecFluentTerm | string): void {
    this.releaseRules.add(ruleKey(toEventTerm(event), toFluentTerm(fluent)));
    this.clearCache();
  }

  releases(event: CecEventTerm | string, fluent: CecFluentTerm | string, time: number): boolean {
    assertTime(time);
    return (
      this.releaseRules.has(ruleKey(toEventTerm(event), toFluentTerm(fluent))) &&
      this.happens(event, time)
    );
  }

  setInitiallyTrue(fluent: CecFluentTerm | string): void {
    this.initiallyTrue.add(termKey(toFluentTerm(fluent)));
    this.clearCache();
  }

  set_initially_true(fluent: CecFluentTerm | string): void {
    this.setInitiallyTrue(fluent);
  }

  releasedAt(fluent: CecFluentTerm | string, time: number): boolean {
    assertTime(time);
    const target = toFluentTerm(fluent);
    return this.eventEntries().some(({ event, time: eventTime }) => {
      return (
        eventTime < time &&
        this.releases(event, target, eventTime) &&
        !this.reinitiatedOrTerminated(eventTime, target, time)
      );
    });
  }

  clipped(t1: number, fluent: CecFluentTerm | string, t2: number): boolean {
    assertTime(t1);
    assertTime(t2);
    if (t1 >= t2) return false;

    const target = toFluentTerm(fluent);
    return this.eventEntries().some(({ event, time }) => {
      return t1 < time && time < t2 && this.terminates(event, target, time);
    });
  }

  holdsAt(fluent: CecFluentTerm | string, time: number): boolean {
    assertTime(time);
    const target = toFluentTerm(fluent);
    const cacheKey = `${termKey(target)}@${time}`;
    const cached = this.holdsAtCache.get(cacheKey);
    if (cached !== undefined) return cached;

    const result = this.computeHoldsAt(target, time);
    this.holdsAtCache.set(cacheKey, result);
    return result;
  }

  holds_at(fluent: CecFluentTerm | string, time: number): boolean {
    return this.holdsAt(fluent, time);
  }

  getAllFluentsAt(time: number): CecFluentTerm[] {
    assertTime(time);
    return [...this.knownFluentKeys()]
      .map(parseTermKey)
      .filter((fluent) => this.holdsAt(fluent, time))
      .sort(compareTerms);
  }

  get_all_fluents_at(time: number): Set<CecFluentTerm> {
    return new Set(this.getAllFluentsAt(time));
  }

  getTimeline(fluent: CecFluentTerm | string, maxTime: number): Array<CecTimelineEntry> {
    assertTime(maxTime);
    const timeline: Array<CecTimelineEntry> = [];
    let previous: boolean | undefined;

    for (let time = 0; time <= maxTime; time += 1) {
      const holds = this.holdsAt(fluent, time);
      if (holds !== previous) {
        timeline.push({ time, holds });
        previous = holds;
      }
    }

    return timeline;
  }

  get_timeline(fluent: CecFluentTerm | string, maxTime: number): Array<[number, boolean]> {
    return this.getTimeline(fluent, maxTime).map(({ time, holds }) => [time, holds]);
  }

  loadFact(expression: CecExpression): boolean {
    if (expression.kind !== 'application') return false;
    const predicate = normalizePredicate(expression.name);
    if (!predicate) return false;

    if (predicate === 'happens' && expression.args.length === 2) {
      this.recordEvent(
        termFromExpression(expression.args[0]),
        timeFromExpression(expression.args[1]),
      );
      return true;
    }
    if (predicate === 'initiates' && expression.args.length >= 2) {
      this.addInitiationRule(
        termFromExpression(expression.args[0]),
        termFromExpression(expression.args[1]),
      );
      return true;
    }
    if (predicate === 'terminates' && expression.args.length >= 2) {
      this.addTerminationRule(
        termFromExpression(expression.args[0]),
        termFromExpression(expression.args[1]),
      );
      return true;
    }
    if (predicate === 'releases' && expression.args.length >= 2) {
      this.addReleaseRule(
        termFromExpression(expression.args[0]),
        termFromExpression(expression.args[1]),
      );
      return true;
    }
    if (
      (predicate === 'holdsAt' || expression.name.toLowerCase() === 'initiallytrue') &&
      expression.args.length === 1
    ) {
      this.setInitiallyTrue(termFromExpression(expression.args[0]));
      return true;
    }

    return false;
  }

  evaluatePredicate(expression: CecExpression): boolean | undefined {
    if (expression.kind !== 'application') return undefined;
    const predicate = normalizePredicate(expression.name);
    if (!predicate) return undefined;

    if (predicate === 'happens' && expression.args.length === 2) {
      return this.happens(
        termFromExpression(expression.args[0]),
        timeFromExpression(expression.args[1]),
      );
    }
    if (predicate === 'initiates' && expression.args.length >= 3) {
      return this.initiates(
        termFromExpression(expression.args[0]),
        termFromExpression(expression.args[1]),
        timeFromExpression(expression.args[2]),
      );
    }
    if (predicate === 'terminates' && expression.args.length >= 3) {
      return this.terminates(
        termFromExpression(expression.args[0]),
        termFromExpression(expression.args[1]),
        timeFromExpression(expression.args[2]),
      );
    }
    if (predicate === 'releases' && expression.args.length >= 3) {
      return this.releases(
        termFromExpression(expression.args[0]),
        termFromExpression(expression.args[1]),
        timeFromExpression(expression.args[2]),
      );
    }
    if (predicate === 'releasedAt' && expression.args.length === 2) {
      return this.releasedAt(
        termFromExpression(expression.args[0]),
        timeFromExpression(expression.args[1]),
      );
    }
    if (predicate === 'holdsAt' && expression.args.length === 2) {
      return this.holdsAt(
        termFromExpression(expression.args[0]),
        timeFromExpression(expression.args[1]),
      );
    }
    if (predicate === 'clipped' && expression.args.length === 3) {
      return this.clipped(
        timeFromExpression(expression.args[0]),
        termFromExpression(expression.args[1]),
        timeFromExpression(expression.args[2]),
      );
    }

    return undefined;
  }

  clear(): void {
    this.eventOccurrences.clear();
    this.initiationRules.clear();
    this.terminationRules.clear();
    this.releaseRules.clear();
    this.initiallyTrue.clear();
    this.clearCache();
  }

  getStatistics(): CecEventCalculusStats {
    return {
      eventOccurrences: this.eventOccurrences.size,
      initiationRules: this.initiationRules.size,
      terminationRules: this.terminationRules.size,
      releaseRules: this.releaseRules.size,
      initiallyTrue: this.initiallyTrue.size,
      cachedHoldsAtQueries: this.holdsAtCache.size,
    };
  }

  private computeHoldsAt(fluent: CecFluentTerm, time: number): boolean {
    const initiationTimes = this.eventEntries()
      .filter(
        ({ event, time: eventTime }) =>
          eventTime < time && this.initiates(event, fluent, eventTime),
      )
      .map(({ time: eventTime }) => eventTime);

    if (this.initiallyTrue.has(termKey(fluent))) initiationTimes.push(0);
    if (initiationTimes.length === 0) return false;

    const mostRecentInitiation = Math.max(...initiationTimes);
    if (this.releasedAt(fluent, time)) return false;
    return !this.clipped(mostRecentInitiation, fluent, time);
  }

  private reinitiatedOrTerminated(
    fromTime: number,
    fluent: CecFluentTerm,
    toTime: number,
  ): boolean {
    return this.eventEntries().some(({ event, time }) => {
      return (
        fromTime < time &&
        time < toTime &&
        (this.initiates(event, fluent, time) || this.terminates(event, fluent, time))
      );
    });
  }

  private knownFluentKeys(): Set<string> {
    const fluents = new Set(this.initiallyTrue);
    for (const key of [...this.initiationRules, ...this.terminationRules, ...this.releaseRules]) {
      fluents.add(key.slice(key.indexOf('->') + 2));
    }
    return fluents;
  }

  private eventEntries(): Array<{ event: CecEventTerm; time: number }> {
    return [...this.eventOccurrences].map((key) => {
      const separator = key.lastIndexOf('@');
      return {
        event: parseTermKey(key.slice(0, separator)),
        time: Number(key.slice(separator + 1)),
      };
    });
  }

  private clearCache(): void {
    this.holdsAtCache.clear();
  }
}

export function createCecEventTerm(
  name: string,
  parameters: readonly unknown[] = [],
): CecEventTerm {
  return createTerm(name, parameters);
}

export function createCecFluentTerm(
  name: string,
  parameters: readonly unknown[] = [],
): CecFluentTerm {
  return createTerm(name, parameters);
}

export function event(name: string, ...parameters: Array<unknown>): CecEventTerm {
  return createCecEventTerm(name, parameters);
}

export function fluent(name: string, ...parameters: Array<unknown>): CecFluentTerm {
  return createCecFluentTerm(name, parameters);
}

export function happens(
  calculus: CecEventCalculus,
  targetEvent: CecEventTerm | string,
  time: number,
): boolean {
  return calculus.happens(targetEvent, time);
}

export function holds(
  calculus: CecEventCalculus,
  targetFluent: CecFluentTerm | string,
  time: number,
): boolean {
  return calculus.holdsAt(targetFluent, time);
}

export function initiates(
  calculus: CecEventCalculus,
  targetEvent: CecEventTerm | string,
  targetFluent: CecFluentTerm | string,
  time: number,
): boolean {
  return calculus.initiates(targetEvent, targetFluent, time);
}

export function terminates(
  calculus: CecEventCalculus,
  targetEvent: CecEventTerm | string,
  targetFluent: CecFluentTerm | string,
  time: number,
): boolean {
  return calculus.terminates(targetEvent, targetFluent, time);
}

export function fluentsAt(calculus: CecEventCalculus, time: number): Array<CecFluentTerm> {
  return calculus.getAllFluentsAt(time);
}

export function timeline(
  calculus: CecEventCalculus,
  targetFluent: CecFluentTerm | string,
  maxTime: number,
): Array<CecTimelineEntry> {
  return calculus.getTimeline(targetFluent, maxTime);
}

function createTerm(name: string, parameters: readonly unknown[]): CecEventTerm {
  if (!name.trim()) throw new Error('CEC event calculus term name cannot be empty');
  return { name, parameters: [...parameters] };
}

function toEventTerm(event: CecEventTerm | string): CecEventTerm {
  return typeof event === 'string' ? createCecEventTerm(event) : event;
}

function toFluentTerm(fluent: CecFluentTerm | string): CecFluentTerm {
  return typeof fluent === 'string' ? createCecFluentTerm(fluent) : fluent;
}

function termKey(term: CecEventTerm | CecFluentTerm): string {
  if (term.parameters.length === 0) return term.name;
  return `${term.name}(${term.parameters.map(String).join(',')})`;
}

function formatPythonTerm(term: CecEventTerm | CecFluentTerm): string {
  if (term.parameters.length === 0) return term.name;
  return `${term.name}(${term.parameters.map(String).join(', ')})`;
}

function eventOccurrenceKey(event: CecEventTerm, time: number): string {
  return `${termKey(event)}@${time}`;
}

function ruleKey(event: CecEventTerm, fluent: CecFluentTerm): string {
  return `${termKey(event)}->${termKey(fluent)}`;
}

function parseTermKey(key: string): CecFluentTerm {
  const open = key.indexOf('(');
  if (open === -1 || !key.endsWith(')')) return createCecFluentTerm(key);
  const rawParameters = key.slice(open + 1, -1);
  return createCecFluentTerm(key.slice(0, open), rawParameters ? rawParameters.split(',') : []);
}

function compareTerms(left: CecFluentTerm, right: CecFluentTerm): number {
  return termKey(left).localeCompare(termKey(right));
}

function normalizePredicate(name: string): CecEventCalculusPredicate | undefined {
  const normalized = name.toLowerCase();
  if (normalized === 'happens') return 'happens';
  if (normalized === 'initiates') return 'initiates';
  if (normalized === 'terminates') return 'terminates';
  if (normalized === 'releases') return 'releases';
  if (normalized === 'releasedat') return 'releasedAt';
  if (normalized === 'holdsat') return 'holdsAt';
  if (normalized === 'clipped') return 'clipped';
  return undefined;
}

function termFromExpression(expression: CecExpression): CecEventTerm {
  if (expression.kind === 'atom') return createCecEventTerm(expression.name);
  if (expression.kind === 'application') {
    return createCecEventTerm(expression.name, expression.args.map(parameterFromExpression));
  }
  throw new Error('CEC event calculus term must be an atom or application');
}

function parameterFromExpression(expression: CecExpression): unknown {
  if (expression.kind === 'atom') return expression.name;
  if (expression.kind === 'application')
    return `${expression.name}(${expression.args.map(parameterFromExpression).join(',')})`;
  throw new Error('CEC event calculus parameter must be atomic');
}

function timeFromExpression(expression: CecExpression): number {
  if (expression.kind !== 'atom') throw new Error('CEC event calculus time must be an atom');
  const value = expression.name.startsWith('t')
    ? Number(expression.name.slice(1))
    : Number(expression.name);
  assertTime(value);
  return value;
}

function assertTime(time: number): void {
  if (!Number.isInteger(time) || time < 0)
    throw new Error('CEC event calculus time must be a non-negative integer');
}
