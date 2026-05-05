import { convertLegalTextToDeontic } from './deontic';
import { parseFolText } from './fol';
import { predictMLConfidence } from './mlConfidence';
import { getLogicRuntimeCapabilities } from './runtimeCapabilities';

export function validateBrowserNativeLogicRuntime(
  options: { folText?: string; deonticText?: string } = {},
) {
  const capabilities = getLogicRuntimeCapabilities();
  const folText = options.folText ?? 'All tenants are protected and some landlords must comply.';
  const deonticText = options.deonticText ?? 'The landlord must provide notice before entry.';
  const firstFol = parseFolText(folText);
  const secondFol = parseFolText(folText);
  const quantifiers = firstFol.quantifiers.map((quantifier) => quantifier.symbol);
  const operators = firstFol.operators.map((operator) => operator.symbol);
  const entities = { nouns: firstFol.nlp.predicateCandidates };
  const deterministicScore = predictMLConfidence(
    folText,
    firstFol.formula,
    entities,
    quantifiers,
    operators,
  );
  const repeatedScore = predictMLConfidence(
    folText,
    firstFol.formula,
    entities,
    quantifiers,
    operators,
  );
  const deontic = convertLegalTextToDeontic(deonticText);
  const failures = [
    capabilities.serverCallsAllowed === false ? '' : 'runtime_server_calls_allowed',
    capabilities.mode === 'browser_native' ? '' : 'runtime_not_browser_native',
    capabilities.fol.nlpUnavailable ? 'fol_nlp_unavailable' : '',
    capabilities.fol.mlUnavailable ? 'fol_ml_unavailable' : '',
    firstFol.nlp.pythonSpacy ? 'fol_python_spacy_enabled' : '',
    firstFol.nlp.serverCallsAllowed === false ? '' : 'fol_nlp_server_calls_allowed',
    firstFol.capabilities.serverCallsAllowed === false ? '' : 'fol_server_calls_allowed',
    sameStrings(firstFol.nlp.predicateCandidates, secondFol.nlp.predicateCandidates)
      ? ''
      : 'fol_nlp_not_deterministic',
    deterministicScore === repeatedScore ? '' : 'ml_score_not_deterministic',
    deontic.capabilities.serverCallsAllowed === false ? '' : 'deontic_server_calls_allowed',
    deontic.capabilities.mlUnavailable ? 'deontic_ml_unavailable' : '',
  ].filter(Boolean);

  return {
    valid: failures.length === 0,
    failures,
    runtime: {
      mode: capabilities.mode,
      serverCallsAllowed: false,
      mlConfidenceSource: capabilities.fol.mlConfidenceSource,
      mlConfidenceModelLoaded: capabilities.fol.mlConfidenceModelLoaded,
    },
    nlp: {
      provider: firstFol.nlp.provider,
      backend: firstFol.nlp.backend,
      pythonSpacy: false,
      serverCallsAllowed: false,
      predicateCandidates: firstFol.nlp.predicateCandidates,
      repeatedPredicateCandidates: secondFol.nlp.predicateCandidates,
    },
    ml: {
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
      deterministicScore,
      repeatedScore,
      source: capabilities.fol.mlConfidenceSource,
    },
    deontic: {
      success: deontic.success,
      formulas: deontic.formulas,
      browserNativeMlConfidence: deontic.capabilities.browserNativeMlConfidence,
      serverCallsAllowed: false,
    },
  };
}

function sameStrings(left: Array<string>, right: Array<string>): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}
