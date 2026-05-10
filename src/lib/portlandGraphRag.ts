import { clientEmbeddingWorkerService } from './clientEmbeddingWorkerService';
import {
  CorpusEntity,
  CorpusRelationship,
  GraphRagEvidence,
  SearchResult,
  buildGraphRagEvidence,
  buildSectionGraphRagEvidence,
} from './portlandCorpus';
import {
  buildLogicEvidenceForSearchResults,
  type LogicEvidenceItem,
} from './portlandLogic';
import { LLM_CONFIG } from './llmConfig';

export interface GraphRagAnswer {
  question: string;
  answer: string;
  evidence: GraphRagEvidence;
  logicEvidence: LogicEvidenceItem[];
  usedLocalModel: boolean;
  generationSource: 'local' | 'cloud' | 'retrieved';
  generationWarning?: string;
}

export async function answerWithGraphRag(
  question: string,
  options: { selectedCid?: string | null } = {},
): Promise<GraphRagAnswer> {
  const trimmedQuestion = question.trim();
  if (!trimmedQuestion) {
    throw new Error('Question is required');
  }

  let queryEmbedding: Float32Array | undefined;
  try {
    queryEmbedding = await clientEmbeddingWorkerService.generateEmbedding(trimmedQuestion);
  } catch (error) {
    console.warn('GraphRAG embedding unavailable, retrieving with keyword search only', error);
  }

  const evidence = options.selectedCid
    ? await buildSectionGraphRagEvidence(options.selectedCid, trimmedQuestion, queryEmbedding, 5)
    : await buildGraphRagEvidence(trimmedQuestion, queryEmbedding, 5);
  const logicEvidence = await buildLogicEvidenceForSearchResults(evidence.sections);
  if (evidence.sections.length === 0) {
    return {
      question: trimmedQuestion,
      answer:
        'I could not find a relevant Portland City Code section in the local corpus for that question.',
      evidence,
      logicEvidence,
      usedLocalModel: false,
      generationSource: 'retrieved',
      generationWarning: 'No relevant local corpus evidence was found, so no generation was attempted.',
    };
  }

  const prompt = buildGraphRagPrompt(trimmedQuestion, evidence, logicEvidence, Boolean(options.selectedCid));

  try {
    if (shouldSkipLocalModelForBrowserTest()) {
      return {
        question: trimmedQuestion,
        answer: buildEvidenceSummary(evidence.sections),
        evidence,
        logicEvidence,
        usedLocalModel: false,
        generationSource: 'retrieved',
        generationWarning: 'Local LLM generation was disabled for this browser session.',
      };
    }

    const { clientLLMWorkerService } = await import('./clientLLMWorkerService');
    const rawAnswer = await clientLLMWorkerService.generateText(prompt, 96);
    const modelSource = clientLLMWorkerService.getLastGenerationSource();
    const candidateAnswer = cleanModelAnswer(rawAnswer);
    const answerIsGrounded = isGroundedAnswer(candidateAnswer);
    const answer = answerIsGrounded
      ? candidateAnswer
      : buildEvidenceSummary(evidence.sections);

    const generationSource: 'local' | 'cloud' | 'retrieved' = answerIsGrounded
      ? (modelSource === 'cloud' ? 'cloud' : 'local')
      : 'retrieved';

    return {
      question: trimmedQuestion,
      answer,
      evidence,
      logicEvidence,
      usedLocalModel: generationSource === 'local',
      generationSource,
      generationWarning: answerIsGrounded
        ? undefined
        : 'The model response was not sufficiently citation-grounded, so the app returned retrieved evidence instead.',
    };
  } catch (error) {
    const generationWarning = error instanceof Error ? error.message : String(error);
    console.warn('GraphRAG generation failed, using evidence summary', error);
    return {
      question: trimmedQuestion,
      answer: `${buildEvidenceSummary(evidence.sections)}\n\nGeneration status: ${generationWarning}`,
      evidence,
      logicEvidence,
      usedLocalModel: false,
      generationSource: 'retrieved',
      generationWarning,
    };
  }
}

function shouldSkipLocalModelForBrowserTest() {
  if (typeof window === 'undefined') {
    return false;
  }
  return window.localStorage.getItem('PORTLAND_DISABLE_LOCAL_LLM') === 'true';
}

function buildGraphRagPrompt(
  question: string,
  evidence: GraphRagEvidence,
  logicEvidence: LogicEvidenceItem[],
  sectionScoped: boolean,
) {
  const logicByCid = new Map(logicEvidence.map((item) => [item.ipfs_cid, item]));
  const sectionEvidence = evidence.sections
    .slice(0, sectionScoped ? 3 : 3)
    .map((result, index) => {
      const section = result.section;
      const citation = result.citation || section.identifier;
      const logic = logicByCid.get(result.ipfs_cid);
      const logicBlock = logic
        ? `\nLogic: ${logic.normType} ${logic.normOperator}; ${logic.parseStatus}; ${logic.certificateStatus}.`
        : '';
      const excerptLimit = index === 0 && sectionScoped ? 700 : 420;
      const excerptSource = index === 0 && sectionScoped
        ? section.text
        : result.snippet || section.text;
      return `[${index + 1}] ${citation}
Title: ${section.title}
Source: ${section.source_url}
Excerpt: ${truncateText(cleanCorpusExcerpt(excerptSource), excerptLimit)}${logicBlock}`;
    })
    .join('\n\n');
  const graphContext = buildGraphContext(evidence.entities, evidence.relationships);

  const prompt = `You answer questions about Portland City Code using only the evidence below.
This is legal information, not legal advice.
${sectionScoped ? 'The first evidence item is the selected statute the user is reading. Use it as the primary context before relying on related statutes.' : 'The evidence was retrieved from the full local corpus for the user question.'}
If the evidence is insufficient, say so. Keep the answer under 5 sentences.
Every factual sentence must cite an evidence number like [1] or [2].

Question: ${question}

Evidence:
${sectionEvidence}

Knowledge graph context:
${graphContext}

Answer:`;

  return truncateGraphRagPrompt(prompt);
}

function buildGraphContext(entities: CorpusEntity[], relationships: CorpusRelationship[]) {
  const entityLabels = new Map(entities.map((entity) => [entity.id, `${entity.label} (${formatGraphType(entity.type)})`]));
  const entityLines = entities
    .slice(0, 6)
    .map((entity) => `- ${entityLabels.get(entity.id)}`)
    .join('\n') || '- None retrieved.';
  const relationshipLines = relationships
    .slice(0, 6)
    .map((relationship) => {
      const source = entityLabels.get(relationship.source) || relationship.source;
      const target = entityLabels.get(relationship.target) || relationship.target;
      return `- ${source} ${formatGraphType(relationship.type)} ${target}`;
    })
    .join('\n') || '- None retrieved.';
  return `Entities:\n${entityLines}\nRelationships:\n${relationshipLines}`;
}

function formatGraphType(type: string) {
  return type
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function cleanModelAnswer(answer: string) {
  return answer
    .replace(/<\|[^>]+?\|>/g, '')
    .replace(/^answer:\s*/i, '')
    .trim();
}

function isGroundedAnswer(answer: string) {
  if (!answer || answer.length < 24) {
    return false;
  }
  return /\[[1-5]\]/.test(answer);
}

function buildEvidenceSummary(sections: SearchResult[]) {
  const topSections = sections.slice(0, 3);
  const lead = topSections
    .map((result, index) => {
      const section = result.section;
      return `[${index + 1}] ${result.citation}: ${section.title}. ${cleanCorpusExcerpt(result.snippet)}`;
    })
    .join('\n\n');

  return `The strongest local corpus matches are:\n\n${lead}\n\nReview the cited Portland City Code sections before relying on this information.`;
}

function cleanCorpusExcerpt(excerpt: string) {
  return excerpt
    .replace(/\s+/g, ' ')
    .replace(/(^|\.\.\.|\s)Label:\s*City code section\s*/gi, '$1')
    .replace(/(^|\.\.\.|\s)Label:\s*/gi, '$1')
    .trim();
}

function truncateText(text: string, maxChars: number) {
  if (text.length <= maxChars) {
    return text;
  }
  return `${text.slice(0, maxChars).replace(/\s+\S*$/, '').trim()} ...`;
}

function truncateGraphRagPrompt(prompt: string) {
  if (prompt.length <= LLM_CONFIG.LOCAL_MAX_PROMPT_CHARS) {
    return prompt;
  }

  const answerMarker = '\n\nAnswer:';
  const answerIndex = prompt.lastIndexOf(answerMarker);
  if (answerIndex === -1) {
    return truncateText(prompt, LLM_CONFIG.LOCAL_MAX_PROMPT_CHARS);
  }

  const reservedTail = prompt.slice(answerIndex);
  const headBudget = Math.max(1200, LLM_CONFIG.LOCAL_MAX_PROMPT_CHARS - reservedTail.length);
  return `${truncateText(prompt.slice(0, answerIndex), headBudget)}${reservedTail}`;
}
