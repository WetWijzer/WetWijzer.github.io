import type { CecExpression } from './ast';
import { visitCecExpression } from './ast';

export type CecContextEntityType = 'agent' | 'object' | 'event' | 'time' | 'location' | 'property';

export interface CecContextEntityOptions {
  properties?: Record<string, unknown>;
  mentions?: number[];
}

export interface CecTemporalScope {
  label: string;
  start: number;
  end?: number;
  entityNames: string[];
}

export class CecContextEntity {
  readonly name: string;
  readonly entityType: CecContextEntityType;
  readonly properties: Record<string, unknown>;
  readonly mentions: number[];

  constructor(
    name: string,
    entityType: CecContextEntityType,
    options: CecContextEntityOptions = {},
  ) {
    if (!name.trim()) throw new Error('CEC context entity name cannot be empty');
    this.name = normalizeEntityName(name);
    this.entityType = entityType;
    this.properties = { ...(options.properties ?? {}) };
    this.mentions = [...(options.mentions ?? [])];
  }

  addMention(position: number): void {
    if (!Number.isInteger(position) || position < 0) {
      throw new Error('CEC context mention position must be a non-negative integer');
    }
    this.mentions.push(position);
  }

  mostRecentMention(): number | undefined {
    return this.mentions.length === 0 ? undefined : Math.max(...this.mentions);
  }

  merge(other: CecContextEntity): CecContextEntity {
    if (this.name !== other.name) throw new Error('Cannot merge different CEC context entities');
    return new CecContextEntity(this.name, this.entityType, {
      properties: { ...this.properties, ...other.properties },
      mentions: [...this.mentions, ...other.mentions],
    });
  }
}

export class CecContextState {
  readonly entities = new Map<string, CecContextEntity>();
  readonly bindings = new Map<string, string>();
  readonly temporalScopes: CecTemporalScope[] = [];
  focus?: CecContextEntity;
  readonly discourseHistory: string[] = [];
  position = 0;

  addEntity(entity: CecContextEntity): void {
    const existing = this.entities.get(entity.name);
    const merged = existing ? existing.merge(entity) : entity;
    this.entities.set(merged.name, merged);
  }

  getEntity(name: string): CecContextEntity | undefined {
    return this.entities.get(normalizeEntityName(name));
  }

  bindEntity(binding: string, entityName: string): void {
    if (!binding.trim()) throw new Error('CEC context binding name cannot be empty');
    const entity = this.getEntity(entityName);
    if (!entity) throw new Error(`Cannot bind unknown CEC context entity: ${entityName}`);
    this.bindings.set(normalizeEntityName(binding), entity.name);
  }

  getBinding(binding: string): CecContextEntity | undefined {
    const entityName = this.bindings.get(normalizeEntityName(binding));
    return entityName ? this.getEntity(entityName) : undefined;
  }

  setFocus(entity: CecContextEntity): void {
    const registered = this.getEntity(entity.name) ?? entity;
    this.focus = registered;
  }

  addUtterance(utterance: string): void {
    this.discourseHistory.push(utterance);
    this.position += 1;
  }

  pushTemporalScope(
    label: string,
    start = this.position,
    entityNames: string[] = [],
  ): CecTemporalScope {
    if (!label.trim()) throw new Error('CEC temporal scope label cannot be empty');
    if (!Number.isInteger(start) || start < 0)
      throw new Error('CEC temporal scope start must be a non-negative integer');
    const scope = {
      label: normalizeEntityName(label),
      start,
      entityNames: entityNames.map((name) => normalizeEntityName(name)).sort(),
    };
    this.temporalScopes.push(scope);
    return { ...scope, entityNames: [...scope.entityNames] };
  }

  closeTemporalScope(label: string, end = this.position): CecTemporalScope | undefined {
    if (!Number.isInteger(end) || end < 0)
      throw new Error('CEC temporal scope end must be a non-negative integer');
    const normalized = normalizeEntityName(label);
    const scope = [...this.temporalScopes]
      .reverse()
      .find((candidate) => candidate.label === normalized && candidate.end === undefined);
    if (!scope) return undefined;
    scope.end = end;
    return { ...scope, entityNames: [...scope.entityNames] };
  }

  snapshot(): CecContextSnapshot {
    return {
      entities: [...this.entities.values()]
        .map((entity) => ({
          name: entity.name,
          entityType: entity.entityType,
          properties: { ...entity.properties },
          mentions: [...entity.mentions],
        }))
        .sort((left, right) => left.name.localeCompare(right.name)),
      bindings: [...this.bindings.entries()].sort(([left], [right]) => left.localeCompare(right)),
      temporalScopes: this.temporalScopes.map((scope) => ({
        ...scope,
        entityNames: [...scope.entityNames],
      })),
      focus: this.focus?.name,
      discourseHistory: [...this.discourseHistory],
      position: this.position,
    };
  }

  restore(snapshot: CecContextSnapshot): void {
    this.entities.clear();
    this.bindings.clear();
    this.temporalScopes.splice(0, this.temporalScopes.length);
    this.discourseHistory.splice(0, this.discourseHistory.length);

    for (const entity of snapshot.entities) {
      this.addEntity(
        new CecContextEntity(entity.name, entity.entityType, {
          properties: entity.properties,
          mentions: entity.mentions,
        }),
      );
    }
    for (const [binding, entityName] of snapshot.bindings ?? []) {
      if (this.getEntity(entityName))
        this.bindings.set(normalizeEntityName(binding), normalizeEntityName(entityName));
    }
    this.temporalScopes.push(
      ...(snapshot.temporalScopes ?? []).map((scope) => ({
        label: normalizeEntityName(scope.label),
        start: scope.start,
        end: scope.end,
        entityNames: [...scope.entityNames].map((name) => normalizeEntityName(name)).sort(),
      })),
    );
    this.discourseHistory.push(...snapshot.discourseHistory);
    this.position = snapshot.position;
    this.focus = snapshot.focus ? this.getEntity(snapshot.focus) : undefined;
  }
}

export interface CecContextSnapshot {
  entities: Array<{
    name: string;
    entityType: CecContextEntityType;
    properties: Record<string, unknown>;
    mentions: number[];
  }>;
  bindings?: Array<[string, string]>;
  temporalScopes?: CecTemporalScope[];
  focus?: string;
  discourseHistory: string[];
  position: number;
}

export class CecContextManager {
  private state = new CecContextState();
  readonly pronounMappings = new Map<string, CecContextEntityType>([
    ['he', 'agent'],
    ['she', 'agent'],
    ['they', 'agent'],
    ['it', 'object'],
    ['this', 'object'],
    ['that', 'object'],
  ]);

  processUtterance(utterance: string): CecContextState {
    this.state.addUtterance(utterance);

    for (const entity of this.extractEntities(utterance)) {
      entity.addMention(this.state.position);
      this.state.addEntity(entity);
      const registered = this.state.getEntity(entity.name);
      if (registered) this.state.setFocus(registered);
    }

    return this.state;
  }

  ingestExpression(expression: CecExpression, position = this.state.position + 1): CecContextState {
    if (!Number.isInteger(position) || position < 0)
      throw new Error('CEC context position must be a non-negative integer');

    visitCecExpression(expression, (node) => {
      if (node.kind === 'application') {
        const event = new CecContextEntity(node.name, 'event', {
          properties: { arity: node.args.length },
        });
        event.addMention(position);
        this.state.addEntity(event);
        this.state.setFocus(this.state.getEntity(event.name) ?? event);
      }
      if (node.kind === 'atom') {
        const entity = new CecContextEntity(node.name, inferEntityType(node.name));
        entity.addMention(position);
        this.state.addEntity(entity);
      }
    });

    this.state.position = Math.max(this.state.position, position);
    return this.state;
  }

  resolveReference(reference: string): CecContextEntity | undefined {
    const normalized = normalizeEntityName(reference);
    const direct = this.state.getEntity(normalized);
    if (direct) return direct;
    const bound = this.state.getBinding(normalized);
    if (bound) return bound;

    const entityType = this.pronounMappings.get(normalized);
    return entityType ? this.findAntecedent(entityType) : undefined;
  }

  resolvePronouns(text: string): Map<string, CecContextEntity> {
    const resolutions = new Map<string, CecContextEntity>();
    for (const word of tokenize(text)) {
      const entityType = this.pronounMappings.get(word);
      if (!entityType) continue;
      const antecedent = this.findAntecedent(entityType);
      if (antecedent) resolutions.set(word, antecedent);
    }
    return resolutions;
  }

  getContextState(): CecContextState {
    return this.state;
  }

  bindEntity(binding: string, entityName: string): void {
    this.state.bindEntity(binding, entityName);
  }

  pushTemporalScope(
    label: string,
    start = this.state.position,
    entityNames: string[] = [],
  ): CecTemporalScope {
    return this.state.pushTemporalScope(label, start, entityNames);
  }

  closeTemporalScope(label: string, end = this.state.position): CecTemporalScope | undefined {
    return this.state.closeTemporalScope(label, end);
  }

  getTemporalScopes(): CecTemporalScope[] {
    return this.state.temporalScopes.map((scope) => ({
      ...scope,
      entityNames: [...scope.entityNames],
    }));
  }

  snapshot(): CecContextSnapshot {
    return this.state.snapshot();
  }

  restore(snapshot: CecContextSnapshot): CecContextState {
    this.state.restore(snapshot);
    return this.state;
  }

  rollback(snapshot: CecContextSnapshot): CecContextState {
    return this.restore(snapshot);
  }

  mergeSnapshot(snapshot: CecContextSnapshot): CecContextState {
    for (const entity of [...snapshot.entities].sort((left, right) =>
      left.name.localeCompare(right.name),
    )) {
      this.state.addEntity(
        new CecContextEntity(entity.name, entity.entityType, {
          properties: entity.properties,
          mentions: entity.mentions,
        }),
      );
    }
    for (const utterance of snapshot.discourseHistory) {
      if (!this.state.discourseHistory.includes(utterance))
        this.state.discourseHistory.push(utterance);
    }
    for (const scope of snapshot.temporalScopes ?? []) {
      this.state.temporalScopes.push({
        label: normalizeEntityName(scope.label),
        start: scope.start,
        end: scope.end,
        entityNames: [...scope.entityNames].map((name) => normalizeEntityName(name)).sort(),
      });
    }
    for (const [binding, entityName] of snapshot.bindings ?? []) {
      if (this.state.getEntity(entityName))
        this.state.bindings.set(normalizeEntityName(binding), normalizeEntityName(entityName));
    }
    this.state.position = Math.max(this.state.position, snapshot.position);
    if (snapshot.focus) {
      const focus = this.state.getEntity(snapshot.focus);
      if (focus) this.state.setFocus(focus);
    }
    return this.state;
  }

  resetContext(): void {
    this.state = new CecContextState();
  }

  getDiscourseHistory(): string[] {
    return [...this.state.discourseHistory];
  }

  getActiveEntities(): CecContextEntity[] {
    return [...this.state.entities.values()].sort((left, right) =>
      left.name.localeCompare(right.name),
    );
  }

  getFocusedEntity(): CecContextEntity | undefined {
    return this.state.focus;
  }

  private extractEntities(utterance: string): CecContextEntity[] {
    const entities: CecContextEntity[] = [];
    for (const word of tokenize(utterance)) {
      const entityType = LEXICAL_ENTITY_TYPES.get(word);
      if (entityType) entities.push(new CecContextEntity(word, entityType));
    }
    return entities;
  }

  private findAntecedent(entityType: CecContextEntityType): CecContextEntity | undefined {
    if (this.state.focus?.entityType === entityType) return this.state.focus;

    const candidates = [...this.state.entities.values()].filter((entity) => {
      return entity.entityType === entityType && entity.mostRecentMention() !== undefined;
    });
    candidates.sort(
      (left, right) => (right.mostRecentMention() ?? 0) - (left.mostRecentMention() ?? 0),
    );
    return candidates[0];
  }
}

export class CecAnaphoraResolver {
  private readonly resolutionHistory: Array<Map<string, CecContextEntity>> = [];

  constructor(private readonly contextManager: CecContextManager) {}

  resolveAnaphora(text: string): Map<string, CecContextEntity> {
    const resolutions = this.contextManager.resolvePronouns(text);
    this.resolutionHistory.push(new Map(resolutions));
    return resolutions;
  }

  getResolutionHistory(): Array<Map<string, CecContextEntity>> {
    return this.resolutionHistory.map((entry) => new Map(entry));
  }
}

export class CecDiscourseAnalyzer {
  segments: string[][] = [];

  segmentDiscourse(utterances: string[]): string[][] {
    if (utterances.length === 0) {
      this.segments = [];
      return [];
    }

    const segments: string[][] = [];
    let currentSegment = [utterances[0]];
    for (let index = 1; index < utterances.length; index += 1) {
      if (isTopicShift(utterances[index])) {
        segments.push(currentSegment);
        currentSegment = [utterances[index]];
      } else {
        currentSegment.push(utterances[index]);
      }
    }
    segments.push(currentSegment);
    this.segments = segments;
    return segments;
  }

  analyzeCoherence(utterances: string[]): number {
    if (utterances.length < 2) return 1;

    let totalOverlap = 0;
    for (let index = 0; index < utterances.length - 1; index += 1) {
      const left = new Set(tokenize(utterances[index]));
      const right = new Set(tokenize(utterances[index + 1]));
      totalOverlap += [...left].filter((word) => right.has(word)).length;
    }

    return Math.min(1, totalOverlap / (utterances.length - 1) / 3);
  }
}

const LEXICAL_ENTITY_TYPES = new Map<string, CecContextEntityType>([
  ['alice', 'agent'],
  ['bob', 'agent'],
  ['charlie', 'agent'],
  ['agent', 'agent'],
  ['person', 'agent'],
  ['tenant', 'agent'],
  ['landlord', 'agent'],
  ['applicant', 'agent'],
  ['inspector', 'agent'],
  ['door', 'object'],
  ['light', 'object'],
  ['window', 'object'],
  ['object', 'object'],
  ['permit', 'object'],
  ['notice', 'object'],
  ['property', 'property'],
  ['hearing', 'event'],
  ['inspection', 'event'],
  ['deadline', 'time'],
]);

function inferEntityType(value: string): CecContextEntityType {
  const normalized = normalizeEntityName(value);
  const lexical = LEXICAL_ENTITY_TYPES.get(normalized);
  if (lexical) return lexical;
  if (/^t\d+$/i.test(value) || /^\d+$/.test(value)) return 'time';
  if (/^(permit|notice|door|light|window|document|record)/i.test(value)) return 'object';
  if (/^(open|close|pay|send|receive|inspect|approve|deny|turn|happen)/i.test(value))
    return 'event';
  return /^[A-Z]/.test(value) ? 'agent' : 'object';
}

function isTopicShift(utterance: string): boolean {
  const words = new Set(tokenize(utterance));
  return ['however', 'but', 'meanwhile', 'next', 'then'].some((marker) => words.has(marker));
}

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .split(/\s+/)
    .map((word) => word.replace(/^[^\w]+|[^\w]+$/g, ''))
    .filter(Boolean);
}

function normalizeEntityName(name: string): string {
  return name
    .trim()
    .replace(/^[^\w]+|[^\w]+$/g, '')
    .toLowerCase();
}
