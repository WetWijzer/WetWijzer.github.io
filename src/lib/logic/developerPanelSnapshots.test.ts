import { buildLogicDeveloperPanelSnapshot } from './developerPanelSnapshots';
import { createBrowserTelemetryCollector } from './browserTelemetry';
import { ProofCache } from './proofCache';
import { ZKPProver, ZKPVerifier } from './zkp';

describe('logic developer panel snapshots', () => {
  it('collects live parse, proof, cache, ML/NLP, and ZKP inspection state locally', () => {
    const cache = new ProofCache({ maxSize: 5, ttlMs: 1000, now: () => 250 });
    cache.set(
      'TenantProtected(alice)',
      { status: 'proved', theorem: 'TenantProtected(alice)', steps: [], method: 'direct' },
      ['Tenant(alice)'],
      'tdfol',
    );
    cache.get('TenantProtected(alice)', ['Tenant(alice)'], 'tdfol');
    const telemetry = createBrowserTelemetryCollector({ now: () => 475 });
    telemetry.increment('logic.parse.requests', 1, { panel: 'developer' });
    telemetry.gauge('proof.cache.entries', 1);
    telemetry.timing('proof.search.ms', 1201, { engine: 'tdfol' });

    const snapshot = buildLogicDeveloperPanelSnapshot({
      parseText: 'All tenants must receive notice and some landlords comply.',
      proofResult: {
        status: 'proved',
        theorem: 'TenantProtected(alice)',
        method: 'tdfol-forward-chaining',
        steps: [{ id: 's1', rule: 'Axiom', premises: [], conclusion: 'TenantProtected(alice)' }],
      },
      proofCache: cache,
      zkpProver: new ZKPProver({ backend: 'simulated', securityLevel: 128 }),
      zkpVerifier: new ZKPVerifier({ backend: 'simulated', securityLevel: 128 }),
      telemetry,
      nowMs: 500,
    });

    expect(snapshot).toMatchObject({
      generatedAtMs: 500,
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      parse: {
        quantifierCount: 2,
        operatorCount: 1,
        nlpProvider: 'deterministic-token-classifier',
        nlpBackend: 'typescript-token-classifier',
      },
      proof: { status: 'proved', theorem: 'TenantProtected(alice)', stepCount: 1 },
      cache: { available: true, entryCount: 1, expiredEntryCount: 0 },
      mlNlp: {
        model: { serverCallsAllowed: false, pythonRuntimeAllowed: false },
        nlp: { pythonSpacy: false, serverCallsAllowed: false },
      },
      zkp: {
        prover: { backend: 'simulated', securityLevel: 128, enableCaching: true },
        verifier: { backend: 'simulated', securityLevel: 128 },
      },
      liveInspection: {
        generatedAtMs: 475,
        refreshMode: 'pull-snapshot',
        inspectableSections: ['parse', 'proof', 'cache', 'mlNlp', 'zkp', 'telemetry'],
        telemetry: {
          metricCount: 3,
          eventCount: 3,
          serverCallsAllowed: false,
        },
        warnings: ['proof.search.ms exceeded 1000ms'],
        serverCallsAllowed: false,
        pythonRuntimeAllowed: false,
      },
      runtime: { mode: 'browser_native', serverCallsAllowed: false },
    });
    expect(snapshot.liveInspection.telemetry.counters.map((metric) => metric.name)).toEqual([
      'logic.parse.requests',
    ]);
    expect(snapshot.liveInspection.telemetry.gauges.map((metric) => metric.name)).toEqual([
      'proof.cache.entries',
    ]);
    expect(snapshot.liveInspection.telemetry.timings.map((metric) => metric.name)).toEqual([
      'proof.search.ms',
    ]);
    expect(snapshot.cache.hottestEntries[0]).toMatchObject({
      formulaString: 'TenantProtected(alice)',
      hitCount: 1,
      proverName: 'tdfol',
    });
    expect(snapshot.parse.predicateCandidates).toEqual([
      'tenants',
      'receive',
      'notice',
      'landlords',
      'comply',
    ]);
  });
});
