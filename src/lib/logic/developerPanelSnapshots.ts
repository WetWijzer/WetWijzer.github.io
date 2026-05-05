import { parseFolText } from './fol';
import { getMLConfidenceArtifactCacheState, getMLConfidenceModelState } from './mlConfidence';
import type { BrowserDeveloperPanelSummary } from './browserTelemetry';
import type { ProofCacheSnapshotEntry, ProofCacheStats } from './proofCache';
import { getLogicRuntimeCapabilities } from './runtimeCapabilities';
import type { ProofResult } from './types';
import type { ZKPProverStats, ZKPVerifierStats } from './zkp';

export interface LogicDeveloperPanelProofCacheLike {
  getStats(): ProofCacheStats;
  snapshot(): Array<ProofCacheSnapshotEntry<unknown>>;
}

export interface LogicDeveloperPanelZkpProverLike {
  readonly backend?: string;
  readonly securityLevel?: number;
  readonly security_level?: number;
  readonly enableCaching?: boolean;
  readonly enable_caching?: boolean;
  getStats(): ZKPProverStats;
}

export interface LogicDeveloperPanelZkpVerifierLike {
  readonly backend?: string;
  readonly securityLevel?: number;
  readonly security_level?: number;
  getStats(): ZKPVerifierStats;
}

export interface LogicDeveloperPanelTelemetryLike {
  developerPanelSummary(): BrowserDeveloperPanelSummary;
}

export interface LogicDeveloperPanelSnapshotOptions {
  parseText?: string;
  proofResult?: ProofResult;
  proofCache?: LogicDeveloperPanelProofCacheLike;
  zkpProver?: LogicDeveloperPanelZkpProverLike;
  zkpVerifier?: LogicDeveloperPanelZkpVerifierLike;
  telemetry?: LogicDeveloperPanelTelemetryLike;
  telemetrySummary?: BrowserDeveloperPanelSummary;
  nowMs?: number;
}

const DEFAULT_PARSE_TEXT = 'All tenants must receive notice and some landlords comply.';

export function buildLogicDeveloperPanelSnapshot(options: LogicDeveloperPanelSnapshotOptions = {}) {
  const input = options.parseText ?? DEFAULT_PARSE_TEXT;
  const parsed = parseFolText(input);
  const runtime = getLogicRuntimeCapabilities();
  const cacheEntries = options.proofCache?.snapshot() ?? [];
  const proof = options.proofResult;
  const telemetrySummary = options.telemetrySummary ?? options.telemetry?.developerPanelSummary();
  const cacheStats = options.proofCache?.getStats();
  const cachePanel = {
    available: options.proofCache !== undefined,
    stats: cacheStats,
    entryCount: cacheEntries.length,
    expiredEntryCount: cacheEntries.filter((entry) => entry.expired).length,
    hottestEntries: topCacheEntries(cacheEntries),
  };
  const proofPanel = {
    status: proof?.status ?? 'not-run',
    theorem: proof?.theorem,
    method: proof?.method,
    stepCount: proof?.steps.length ?? 0,
    error: proof?.error,
    serverCallsAllowed: false,
  };
  const telemetryPanel = telemetrySummary
    ? {
        generatedAtMs: telemetrySummary.generatedAtMs,
        metricCount: telemetrySummary.metricCount,
        eventCount: telemetrySummary.eventCount,
        counters: telemetrySummary.counters,
        gauges: telemetrySummary.gauges,
        timings: telemetrySummary.timings,
        warnings: [...telemetrySummary.warnings],
        serverCallsAllowed: false,
      }
    : {
        generatedAtMs: undefined,
        metricCount: 0,
        eventCount: 0,
        counters: [],
        gauges: [],
        timings: [],
        warnings: [],
        serverCallsAllowed: false,
      };

  return {
    generatedAtMs: options.nowMs ?? Date.now(),
    browserNative: true,
    serverCallsAllowed: false,
    pythonRuntimeAllowed: false,
    parse: {
      input,
      formula: parsed.formula,
      valid: parsed.validation.valid,
      quantifierCount: parsed.quantifiers.length,
      operatorCount: parsed.operators.length,
      predicateCandidates: [...parsed.nlp.predicateCandidates],
      nlpProvider: parsed.nlp.provider,
      nlpBackend: parsed.nlp.backend,
      serverCallsAllowed: false,
    },
    proof: proofPanel,
    cache: cachePanel,
    mlNlp: {
      model: getMLConfidenceModelState(),
      artifactCache: getMLConfidenceArtifactCacheState(),
      nlp: {
        provider: parsed.nlp.provider,
        backend: parsed.nlp.backend,
        tokenCount: parsed.nlp.metadata.tokenCount,
        predicateCandidateCount: parsed.nlp.metadata.predicateCandidateCount,
        pythonSpacy: false,
        serverCallsAllowed: false,
      },
    },
    zkp: {
      capability: runtime.proving,
      prover: options.zkpProver
        ? {
            backend: options.zkpProver.backend,
            securityLevel: options.zkpProver.securityLevel ?? options.zkpProver.security_level,
            enableCaching: options.zkpProver.enableCaching ?? options.zkpProver.enable_caching,
            stats: options.zkpProver.getStats(),
          }
        : undefined,
      verifier: options.zkpVerifier
        ? {
            backend: options.zkpVerifier.backend,
            securityLevel: options.zkpVerifier.securityLevel ?? options.zkpVerifier.security_level,
            stats: options.zkpVerifier.getStats(),
          }
        : undefined,
    },
    liveInspection: {
      generatedAtMs: telemetryPanel.generatedAtMs,
      refreshMode: 'pull-snapshot',
      inspectableSections: ['parse', 'proof', 'cache', 'mlNlp', 'zkp', 'telemetry'],
      telemetry: telemetryPanel,
      warnings: [
        ...telemetryPanel.warnings,
        ...panelWarnings(proofPanel, cachePanel.expiredEntryCount),
      ],
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    },
    runtime,
  };
}

function topCacheEntries(entries: Array<ProofCacheSnapshotEntry<unknown>>) {
  return entries
    .map((entry) => ({
      cid: entry.cid,
      proverName: entry.proverName,
      formulaString: entry.formulaString,
      hitCount: entry.hitCount,
      ageMs: entry.ageMs,
      expired: entry.expired,
    }))
    .sort((left, right) => right.hitCount - left.hitCount)
    .slice(0, 5);
}

function panelWarnings(
  proof: { status: string; error?: string },
  expiredEntryCount: number,
): Array<string> {
  const warnings: Array<string> = [];
  if (proof.status === 'error' && proof.error) {
    warnings.push('proof error: ' + proof.error);
  }
  if (expiredEntryCount > 0) {
    warnings.push('proof cache has ' + expiredEntryCount + ' expired entries');
  }
  return warnings;
}
