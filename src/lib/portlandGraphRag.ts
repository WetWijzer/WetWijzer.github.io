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

export interface GraphRagAnswer {
  question: string;
  answer: string;
  evidence: GraphRagEvidence;
  logicEvidence: LogicEvidenceItem[];
  usedLocalModel: boolean;
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
        generationWarning: 'Local LLM generation was disabled for this browser session.',
      };
    }

    const { clientLLMWorkerService } = await import('./clientLLMWorkerService');
    const rawAnswer = await clientLLMWorkerService.generateText(prompt, 220);
    const candidateAnswer = cleanModelAnswer(rawAnswer);
    const answer = isGroundedAnswer(candidateAnswer)
      ? candidateAnswer
      : buildEvidenceSummary(evidence.sections);
    return {
      question: trimmedQuestion,
      answer,
      evidence,
      logicEvidence,
      usedLocalModel: answer === candidateAnswer,
      generationWarning: answer === candidateAnswer
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
    .map((result, index) => {
      const section = result.section;
      const citation = result.citation || section.identifier;
      const logic = logicByCid.get(result.ipfs_cid);
      const logicBlock = logic
        ? `
Generated logic metadata:
- Norm: ${logic.normType} (${logic.normOperator})
- Temporal scope: ${logic.temporalScope}
- Parse status: ${logic.parseStatus}
- Certificate: ${logic.certificateStatus}
- Caveat: ${logic.caveats[0] || 'Machine-generated candidate formalization.'}`
        : '\nGenerated logic metadata: unavailable for this evidence item.';
      return `[${index + 1}] ${citation}
Title: ${section.title}
Source: ${section.source_url}
${index === 0 && sectionScoped ? 'Full selected section text' : 'Excerpt'}: ${cleanCorpusExcerpt(index === 0 && sectionScoped ? section.text.slice(0, 5000) : result.snippet || section.text.slice(0, 900))}${logicBlock}`;
    })
    .join('\n\n');
  const graphContext = buildGraphContext(evidence.entities, evidence.relationships);

  return `You answer simple questions about the Portland City Code using only the evidence below.
This is legal information, not legal advice.
Generated logic metadata is machine-created support material, not the official law text.
${sectionScoped ? 'The first evidence item is the selected statute the user is reading. Use it as the primary context before relying on related statutes.' : 'The evidence was retrieved from the full local corpus for the user question.'}
If the evidence does not answer the question, say that the local corpus evidence is insufficient.
Keep the answer concise.
Every factual sentence must cite at least one evidence number like [1] or [2].

Question: ${question}

Evidence:
${sectionEvidence}

Knowledge graph context:
${graphContext}

Answer:`;
}

function buildGraphContext(entities: CorpusEntity[], relationships: CorpusRelationship[]) {
  const entityLabels = new Map(entities.map((entity) => [entity.id, `${entity.label} (${formatGraphType(entity.type)})`]));
  const entityLines = entities
    .slice(0, 16)
    .map((entity) => `- ${entityLabels.get(entity.id)}`)
    .join('\n') || '- None retrieved.';
  const relationshipLines = relationships
    .slice(0, 16)
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
