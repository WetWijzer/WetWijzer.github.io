import {
  CecAnaphoraResolver,
  CecContextEntity,
  CecContextManager,
  CecDiscourseAnalyzer,
} from './contextManager';
import { parseCecExpression } from './parser';

describe('CEC context manager', () => {
  it('tracks utterance history, entities, mentions, and focus', () => {
    const manager = new CecContextManager();

    manager.processUtterance('Alice opens the door.');
    manager.processUtterance('Bob sees the light.');

    expect(manager.getDiscourseHistory()).toEqual(['Alice opens the door.', 'Bob sees the light.']);
    expect(manager.getActiveEntities().map((entity) => [entity.name, entity.entityType])).toEqual([
      ['alice', 'agent'],
      ['bob', 'agent'],
      ['door', 'object'],
      ['light', 'object'],
    ]);
    expect(manager.getContextState().getEntity('alice')?.mentions).toEqual([1]);
    expect(manager.getFocusedEntity()?.name).toBe('light');
  });

  it('resolves direct references and pronouns by focus or most recent compatible antecedent', () => {
    const manager = new CecContextManager();
    manager.processUtterance('Alice opens the door.');
    manager.processUtterance('Bob closes the window.');

    expect(manager.resolveReference('Alice')?.name).toBe('alice');
    expect(manager.resolveReference('he')?.name).toBe('bob');
    expect(manager.resolveReference('it')?.name).toBe('window');

    const resolutions = manager.resolvePronouns('He closes it.');
    expect(resolutions.get('he')?.name).toBe('bob');
    expect(resolutions.get('it')?.name).toBe('window');
  });

  it('merges repeated entities without losing properties or mention history', () => {
    const entity = new CecContextEntity('Permit', 'object', { properties: { status: 'active' } });
    entity.addMention(1);

    const updated = new CecContextEntity('permit', 'object', { properties: { section: '33.110' } });
    updated.addMention(3);

    const merged = entity.merge(updated);
    expect(merged.name).toBe('permit');
    expect(merged.properties).toEqual({ status: 'active', section: '33.110' });
    expect(merged.mentions).toEqual([1, 3]);
    expect(merged.mostRecentMention()).toBe(3);
  });

  it('records anaphora resolution history', () => {
    const manager = new CecContextManager();
    manager.processUtterance('The tenant receives the notice.');
    const resolver = new CecAnaphoraResolver(manager);

    const resolutions = resolver.resolveAnaphora('They appeal it.');

    expect(resolutions.get('they')?.name).toBe('tenant');
    expect(resolutions.get('it')?.name).toBe('notice');
    expect(resolver.getResolutionHistory()).toHaveLength(1);
  });

  it('ingests parsed CEC expressions into the same context state', () => {
    const manager = new CecContextManager();
    manager.ingestExpression(parseCecExpression('(Happens (inspect inspector permit) t3)'));

    expect(manager.getContextState().position).toBe(1);
    expect(manager.getContextState().getEntity('happens')?.entityType).toBe('event');
    expect(manager.getContextState().getEntity('inspect')?.entityType).toBe('event');
    expect(manager.getContextState().getEntity('inspector')?.entityType).toBe('agent');
    expect(manager.getContextState().getEntity('permit')?.entityType).toBe('object');
    expect(manager.getContextState().getEntity('t3')?.entityType).toBe('time');
  });

  it('captures bindings and temporal scopes in restorable context snapshots', () => {
    const manager = new CecContextManager();
    manager.processUtterance('The tenant receives the notice.');
    manager.bindEntity('actor', 'tenant');
    manager.pushTemporalScope('appeal window', 1, ['tenant', 'notice']);
    const snapshot = manager.snapshot();

    manager.processUtterance('Bob checks the permit.');
    manager.closeTemporalScope('appeal window', 2);
    manager.rollback(snapshot);

    expect(manager.resolveReference('actor')?.name).toBe('tenant');
    expect(manager.resolveReference('bob')).toBeUndefined();
    expect(manager.getTemporalScopes()).toEqual([
      { label: 'appeal window', start: 1, entityNames: ['notice', 'tenant'] },
    ]);
    expect(manager.snapshot()).toEqual(snapshot);
  });

  it('merges context snapshots deterministically without losing bindings or temporal scopes', () => {
    const base = new CecContextManager();
    base.processUtterance('Alice opens the door.');

    const branch = new CecContextManager();
    branch.processUtterance('The tenant receives the notice.');
    branch.bindEntity('respondent', 'tenant');
    branch.pushTemporalScope('notice period', 1, ['notice', 'tenant']);

    base.mergeSnapshot(branch.snapshot());

    expect(base.getActiveEntities().map((entity) => entity.name)).toEqual([
      'alice',
      'door',
      'notice',
      'tenant',
    ]);
    expect(base.resolveReference('respondent')?.name).toBe('tenant');
    expect(base.getTemporalScopes()).toEqual([
      { label: 'notice period', start: 1, entityNames: ['notice', 'tenant'] },
    ]);
    expect(base.snapshot().entities.map((entity) => entity.name)).toEqual([
      'alice',
      'door',
      'notice',
      'tenant',
    ]);
  });

  it('segments discourse and scores coherence with Python-style heuristics', () => {
    const analyzer = new CecDiscourseAnalyzer();
    const utterances = [
      'Alice opens the door',
      'Alice closes the door',
      'However Bob checks the permit',
      'Bob files the permit',
    ];

    expect(analyzer.segmentDiscourse(utterances)).toEqual([
      ['Alice opens the door', 'Alice closes the door'],
      ['However Bob checks the permit', 'Bob files the permit'],
    ]);
    expect(
      analyzer.analyzeCoherence(['permit notice', 'permit appeal', 'appeal notice']),
    ).toBeCloseTo(1 / 3);
  });

  it('resets context and validates entity mention positions', () => {
    const manager = new CecContextManager();
    manager.processUtterance('Alice opens the door.');
    manager.resetContext();

    expect(manager.getActiveEntities()).toEqual([]);
    expect(manager.getDiscourseHistory()).toEqual([]);
    expect(() => new CecContextEntity('', 'agent')).toThrow('cannot be empty');
    expect(() => new CecContextEntity('alice', 'agent').addMention(-1)).toThrow(
      'non-negative integer',
    );
  });
});
