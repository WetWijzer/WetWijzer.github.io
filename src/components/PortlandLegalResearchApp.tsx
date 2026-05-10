import { FormEvent, KeyboardEvent, useEffect, useMemo, useState } from 'react';
import {
  CorpusEntity,
  CorpusRelationship,
  CorpusSection,
  GraphRagEvidence,
  PortlandCorpusManifest,
  SearchResult,
  getRelatedGraph,
  loadPortlandCorpus,
  searchCorpus,
} from '../lib/portlandCorpus';
import { clientEmbeddingWorkerService } from '../lib/clientEmbeddingWorkerService';
import { clientLLMWorkerService } from '../lib/clientLLMWorkerService';
import { answerWithGraphRag } from '../lib/portlandGraphRag';
import {
  LogicProofSummary,
  NormType,
  explainLogicProofSummary,
  getLogicProofForSection,
  getSimulatedCertificateWarning,
  loadLogicProofIndexes,
} from '../lib/portlandLogic';
import { formatTdfolFormula, parseTdfolFormula } from '../lib/logic/tdfol';
import { analyzeCecExpression, formatCecExpression, parseCecExpression, type CecAnalysis } from '../lib/logic/cec';

type LoadState = 'loading' | 'ready' | 'error';
type WorkspaceTab = 'section' | 'chat' | 'graph' | 'proof';

interface DirectoryTitle {
  number: string;
  label: string;
  sections: CorpusSection[];
  chapters: DirectoryChapter[];
}

interface DirectoryChapter {
  number: string;
  sections: CorpusSection[];
}

const EXAMPLE_QUERIES = [
  'notice requirements',
  'temporary administrative rules',
  'building permit appeal',
  'business license',
];
const INITIAL_RESULT_LIMIT = 6;
const RESULT_INCREMENT = 6;
const GRAPH_ENTITY_LIMIT = 14;
const GRAPH_RELATIONSHIP_LIMIT = 14;
const CHAT_PROMPTS = [
  'What does this section require?',
  'Who is affected by this section?',
  'What evidence supports this answer?',
];

const TITLE_LABELS: Record<string, string> = {
  '1': 'General Provisions',
  '2': 'Legislation & Elections',
  '3': 'Administration',
  '4': 'Original Art Murals',
  '5': 'Revenue and Finance',
  '6': 'Special Taxes',
  '7': 'Business Licenses',
  '9': 'Protected Sick Time',
  '10': 'Erosion and Sediment Control Regulations',
  '11': 'Trees',
  '12': 'Utility Operators',
  '13': 'Bees and Livestock',
  '14': 'Public Order and Police',
  '15': 'Emergency Code',
  '16': 'Vehicles and Traffic',
  '17': 'Public Improvements',
  '18': 'Noise Control',
  '19': 'Harbors',
  '20': 'Parks and Recreation',
  '21': 'Water',
  '22': 'Hearings Officer',
  '23': 'Civil Rights',
  '24': 'Building Regulations',
  '25': 'Plumbing Regulations',
  '26': 'Electrical Regulations',
  '27': 'Heating and Ventilating Regulations',
  '28': 'Floating Structures',
  '29': 'Property Maintenance Regulations',
  '30': 'Affordable Housing',
  '31': 'Fire Regulations',
  '32': 'Signs and Related Regulations',
  '33': 'Planning and Zoning',
  '34': 'Digital Justice',
  '35': 'Community Police Oversight Board',
};

export default function PortlandLegalResearchApp() {
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [sections, setSections] = useState<CorpusSection[]>([]);
  const [corpusManifest, setCorpusManifest] = useState<PortlandCorpusManifest | null>(null);
  const [query, setQuery] = useState('notice requirements');
  const [titleFilter, setTitleFilter] = useState('');
  const [chapterFilter, setChapterFilter] = useState('');
  const [normFilter, setNormFilter] = useState<NormType | ''>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [proofByCid, setProofByCid] = useState<Map<string, LogicProofSummary>>(new Map());
  const [selectedCid, setSelectedCid] = useState<string | null>(null);
  const [selectedProof, setSelectedProof] = useState<LogicProofSummary | null>(null);
  const [relatedEntities, setRelatedEntities] = useState<CorpusEntity[]>([]);
  const [relatedRelationships, setRelatedRelationships] = useState<CorpusRelationship[]>([]);
  const [isGraphLoading, setIsGraphLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('section');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatQuestion, setChatQuestion] = useState('What does the code say about notice requirements?');
  const [chatAnswer, setChatAnswer] = useState('');
  const [chatEvidence, setChatEvidence] = useState<GraphRagEvidence | null>(null);
  const [chatError, setChatError] = useState<string | null>(null);
  const [chatUsedLocalModel, setChatUsedLocalModel] = useState(false);
  const [chatGenerationSource, setChatGenerationSource] = useState<'local' | 'cloud' | 'retrieved'>('retrieved');
  const [chatGenerationWarning, setChatGenerationWarning] = useState<string | null>(null);
  const [isAnswering, setIsAnswering] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [corpus, logicIndexes] = await Promise.all([
          loadPortlandCorpus(),
          loadLogicProofIndexes(),
        ]);
        if (cancelled) return;
        setSections(corpus.sections);
        setCorpusManifest(corpus.manifest);
        setProofByCid(logicIndexes.proofByCid);
        setLoadState('ready');
      } catch (err) {
        if (cancelled) return;
        setLoadState('error');
        setError(err instanceof Error ? err.message : 'Unable to load Portland corpus');
      }
    }

    load();

    // Warm local inference in the background so cloud-first routing can
    // switch to local once throughput is proven, without blocking chat UX.
    clientLLMWorkerService.warmLocalModelInBackground();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (loadState !== 'ready') return;
    void runSearch(query, titleFilter, chapterFilter, normFilter);
    // Run the initial search once after corpus load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadState]);

  useEffect(() => {
    let cancelled = false;

    async function loadSelectedContext() {
      if (!selectedCid) {
        setRelatedEntities([]);
        setRelatedRelationships([]);
        setSelectedProof(null);
        setIsGraphLoading(false);
        return;
      }
      setIsGraphLoading(true);
      try {
        const [related, proof] = await Promise.all([
          getRelatedGraph(selectedCid, 1),
          getLogicProofForSection(selectedCid),
        ]);
        if (!cancelled) {
          setRelatedEntities(
            related.entities
              .filter((entity) => entity.id !== selectedCid)
              .sort((left, right) => left.type.localeCompare(right.type) || left.label.localeCompare(right.label))
              .slice(0, 28),
          );
          setRelatedRelationships(related.relationships.slice(0, 36));
          setSelectedProof(proof);
        }
      } catch (err) {
        if (!cancelled) {
          console.warn('Failed to load selected section context', err);
          setRelatedEntities([]);
          setRelatedRelationships([]);
          setSelectedProof(null);
        }
      } finally {
        if (!cancelled) {
          setIsGraphLoading(false);
        }
      }
    }

    loadSelectedContext();
    return () => {
      cancelled = true;
    };
  }, [selectedCid]);

  const directory = useMemo(() => buildDirectory(sections), [sections]);
  const selected = useMemo(() => {
    if (!selectedCid) return results[0]?.section || sections[0] || null;
    return results.find((result) => result.ipfs_cid === selectedCid)?.section
      || sections.find((section) => section.ipfs_cid === selectedCid)
      || null;
  }, [results, sections, selectedCid]);
  const visibleChapters = useMemo(
    () => directory.find((title) => title.number === titleFilter)?.chapters || [],
    [directory, titleFilter],
  );

  async function runSearch(
    nextQuery = query,
    nextTitleFilter = titleFilter,
    nextChapterFilter = chapterFilter,
    nextNormFilter: NormType | '' = normFilter,
  ) {
    if (!nextQuery.trim()) {
      const browsedSections = filterDirectorySections(sections, nextTitleFilter, nextChapterFilter).slice(0, 30);
      setResults(browsedSections.map(sectionToResult));
      setSelectedCid(browsedSections[0]?.ipfs_cid || null);
      return;
    }

    setIsSearching(true);
    setError(null);
    try {
      let queryEmbedding: Float32Array | undefined;
      let mode: 'hybrid' | 'keyword' = 'keyword';

      try {
        queryEmbedding = await clientEmbeddingWorkerService.generateEmbedding(nextQuery);
        mode = 'hybrid';
      } catch (err) {
        console.warn('Vector embedding unavailable, using keyword search', err);
      }

      const nextResults = await searchCorpus(
        nextQuery,
        { titleNumber: nextTitleFilter || undefined, limit: nextNormFilter || nextChapterFilter ? 140 : 40 },
        mode,
        queryEmbedding,
      );
      const filteredResults = nextResults.filter((result) => {
        if (nextChapterFilter && getChapterNumber(result.section) !== nextChapterFilter) {
          return false;
        }
        if (nextNormFilter && proofByCid.get(result.ipfs_cid)?.norm_type !== nextNormFilter) {
          return false;
        }
        return true;
      });
      const limitedResults = filteredResults.slice(0, 40);
      setResults(limitedResults);
      setSelectedCid(limitedResults[0]?.ipfs_cid || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsSearching(false);
    }
  }

  function selectDirectoryTitle(titleNumber: string) {
    const nextTitle = titleFilter === titleNumber ? '' : titleNumber;
    setTitleFilter(nextTitle);
    setChapterFilter('');
    setQuery('');
    void runSearch('', nextTitle, '', normFilter);
  }

  function selectDirectoryChapter(titleNumber: string, chapterNumber: string) {
    setTitleFilter(titleNumber);
    setChapterFilter(chapterNumber);
    setQuery('');
    void runSearch('', titleNumber, chapterNumber, normFilter);
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runSearch();
  }

  async function onAskQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await answerChatQuestion(null);
  }

  async function onAskSelectedQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await answerChatQuestion(selected?.ipfs_cid || null);
  }

  async function answerChatQuestion(contextCid: string | null) {
    if (!chatQuestion.trim()) return;

    setActiveTab('chat');
    setIsAnswering(true);
    setChatError(null);
    try {
      const response = await answerWithGraphRag(chatQuestion, { selectedCid: contextCid });
      setChatAnswer(response.answer);
      setChatEvidence(response.evidence);
      setChatUsedLocalModel(response.usedLocalModel);
      setChatGenerationSource(response.generationSource);
      setChatGenerationWarning(response.generationWarning || null);
    } catch (err) {
      setChatError(err instanceof Error ? err.message : 'Unable to answer that question.');
      setChatAnswer('');
      setChatEvidence(null);
      setChatUsedLocalModel(false);
      setChatGenerationSource('retrieved');
      setChatGenerationWarning(null);
    } finally {
      setIsAnswering(false);
    }
  }

  function jumpToWorkbench(tab: WorkspaceTab = 'chat') {
    setActiveTab(tab);
    window.requestAnimationFrame(() => {
      document.getElementById('research-workbench')?.scrollIntoView({ block: 'start' });
    });
  }

  function onMobileAskQuestion(event: FormEvent<HTMLFormElement>) {
    void onAskQuestion(event);
    if (chatQuestion.trim()) {
      jumpToWorkbench('chat');
    }
  }

  function onMobileSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTitleFilter('');
    setChapterFilter('');
    setNormFilter('');
    void runSearch(query, '', '', '');
    window.requestAnimationFrame(() => {
      document.getElementById('code-search')?.scrollIntoView({ block: 'start' });
    });
  }

  return (
    <main className="min-h-screen bg-[#f3f5ef] text-[#1f2933] font-system">
      <nav className="skip-links" aria-label="Skip links">
        <a href="#code-directory">Skip to code directory</a>
        <a href="#code-search">Skip to search</a>
        <a href="#research-workbench">Skip to selected section and research tools</a>
      </nav>
      <Header manifest={corpusManifest} sectionCount={sections.length} />

      <MobileFrontPanel
        searchQuery={query}
        question={chatQuestion}
        isSearching={isSearching}
        isAnswering={isAnswering}
        onSearchQueryChange={setQuery}
        onSearch={onMobileSearch}
        onQuestionChange={setChatQuestion}
        onAskQuestion={onMobileAskQuestion}
      />

      <div
        id="main-content"
        className="mx-auto grid max-w-[1520px] gap-3 px-3 py-3 sm:gap-4 sm:px-4 sm:py-4 lg:grid-cols-[300px_minmax(360px,480px)_1fr]"
      >
        <DirectoryPanel
          className="order-1 lg:order-none"
          directory={directory}
          selectedTitle={titleFilter}
          selectedChapter={chapterFilter}
          onSelectTitle={selectDirectoryTitle}
          onSelectChapter={selectDirectoryChapter}
        />

        <SearchPanel
          className="order-2 lg:order-none"
          query={query}
          titleFilter={titleFilter}
          chapterFilter={chapterFilter}
          normFilter={normFilter}
          directory={directory}
          visibleChapters={visibleChapters}
          results={results}
          selectedCid={selected?.ipfs_cid || null}
          proofByCid={proofByCid}
          loadState={loadState}
          isSearching={isSearching}
          error={error}
          chatQuestion={chatQuestion}
          isAnswering={isAnswering}
          onQueryChange={setQuery}
          onQuestionChange={setChatQuestion}
          onTitleChange={(value) => {
            setTitleFilter(value);
            setChapterFilter('');
            void runSearch(query, value, '', normFilter);
          }}
          onChapterChange={(value) => {
            setChapterFilter(value);
            void runSearch(query, titleFilter, value, normFilter);
          }}
          onNormChange={(value) => {
            setNormFilter(value);
            void runSearch(query, titleFilter, chapterFilter, value);
          }}
          onClearFilters={() => {
            setQuery('');
            setTitleFilter('');
            setChapterFilter('');
            setNormFilter('');
            void runSearch('', '', '', '');
          }}
          onSubmit={onSubmit}
          onAskQuestion={onAskQuestion}
          onSelectResult={(cid) => {
            setSelectedCid(cid);
            setActiveTab('section');
            if (window.matchMedia('(max-width: 1023px)').matches) {
              window.requestAnimationFrame(() => {
                const workbench = document.getElementById('research-workbench');
                const targetTop = workbench
                  ? window.scrollY + workbench.getBoundingClientRect().top
                  : window.scrollY;
                window.scrollTo({ left: 0, top: Math.max(targetTop, 0) });
                document.getElementById('panel-section')?.focus({ preventScroll: true });
                window.requestAnimationFrame(() => {
                  window.scrollTo({ left: 0, top: window.scrollY });
                });
              });
            }
          }}
          onExample={(example) => {
            setQuery(example);
            void runSearch(example, titleFilter, chapterFilter, normFilter);
          }}
        />

        <WorkspacePanel
          className="order-3 lg:order-none"
          selected={selected}
          proof={selectedProof}
          relatedEntities={relatedEntities}
          relatedRelationships={relatedRelationships}
          isGraphLoading={isGraphLoading}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          chatQuestion={chatQuestion}
          chatAnswer={chatAnswer}
          chatEvidence={chatEvidence}
          chatError={chatError}
          chatUsedLocalModel={chatUsedLocalModel}
          chatGenerationSource={chatGenerationSource}
          chatGenerationWarning={chatGenerationWarning}
          isAnswering={isAnswering}
          onQuestionChange={setChatQuestion}
          onAskQuestion={onAskSelectedQuestion}
        />
      </div>
    </main>
  );
}

function Header({
  manifest,
  sectionCount,
}: {
  manifest: PortlandCorpusManifest | null;
  sectionCount: number;
}) {
  const dataSummary = manifest
    ? `${sectionCount.toLocaleString()} sections · ${manifest.artifacts.length} artifacts · refreshed ${formatDate(manifest.generatedAt)}`
    : 'Loading latest Portland code dataset';

  return (
    <header className="border-b border-[#d3d8cf] bg-[#fbfcf8]">
      <div className="mx-auto flex max-w-[1520px] flex-col gap-3 px-3 py-3 sm:gap-4 sm:px-4 sm:py-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#4f6f52] sm:text-sm sm:tracking-[0.18em]">
            Portland, Oregon
          </p>
          <h1 className="mt-1 text-xl font-semibold tracking-normal text-[#172026] sm:text-4xl">
            City Code Research Directory
          </h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[#43534d] sm:hidden">
            Search the Portland code with graph, proof, and chat tools.
          </p>
          <p className="mt-2 hidden max-w-3xl text-base leading-7 text-[#43534d] sm:block">
            Browse Titles, Chapters, and Sections like the official code directory, with client-side
            chat, graph search, knowledge graph context, and logic proofs layered in.
          </p>
          <p aria-label="Loaded corpus version" className="mt-2 text-sm font-semibold text-[#24594f]">
            {dataSummary}
          </p>
        </div>
      </div>
    </header>
  );
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  });
}

function MobileFrontPanel({
  searchQuery,
  question,
  isSearching,
  isAnswering,
  onSearchQueryChange,
  onSearch,
  onQuestionChange,
  onAskQuestion,
}: {
  searchQuery: string;
  question: string;
  isSearching: boolean;
  isAnswering: boolean;
  onSearchQueryChange: (query: string) => void;
  onSearch: (event: FormEvent<HTMLFormElement>) => void;
  onQuestionChange: (question: string) => void;
  onAskQuestion: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const [mode, setMode] = useState<'search' | 'chat'>('search');

  return (
    <section className="mx-auto max-w-[1520px] px-3 pt-3 lg:hidden" aria-label="Mobile quick actions">
      <div className="rounded-md border border-[#d8dfd3] bg-white shadow-sm">
        <div className="grid grid-cols-2 border-b border-[#e1e6dc]" role="group" aria-label="Choose quick action">
          <button
            type="button"
            aria-label="Show search"
            aria-pressed={mode === 'search'}
            onClick={() => setMode('search')}
            className={`flex min-h-11 items-center justify-center rounded-tl-md px-3 text-sm font-semibold ${
              mode === 'search' ? 'bg-[#24594f] text-white' : 'text-[#24594f] hover:bg-[#f3f6ef]'
            }`}
          >
            Search
          </button>
          <button
            type="button"
            aria-label="Show chat"
            aria-pressed={mode === 'chat'}
            onClick={() => setMode('chat')}
            className={`flex min-h-11 items-center justify-center rounded-tr-md border-l border-[#e1e6dc] px-3 text-sm font-semibold ${
              mode === 'chat' ? 'bg-[#24594f] text-white' : 'text-[#24594f] hover:bg-[#f3f6ef]'
            }`}
          >
            Chat
          </button>
        </div>
        <div className="p-3">
          {mode === 'search' && (
          <form onSubmit={onSearch} aria-label="Search all Portland City Code from the front panel">
            <div>
              <label htmlFor="mobile-front-search" className="mb-1 block text-sm font-semibold text-[#26343a]">
                Search all Portland City Code
              </label>
              <span className="grid grid-cols-[minmax(0,1fr)_86px] gap-2">
                <input
                  id="mobile-front-search"
                  value={searchQuery}
                  onChange={(event) => onSearchQueryChange(event.target.value)}
                  className="min-h-11 w-full rounded-md border border-[#8fa08a] bg-white px-3 text-base text-[#172026] shadow-sm"
                  placeholder="notice requirements"
                />
                <button
                  type="submit"
                  disabled={isSearching}
                  className="min-h-11 rounded-md bg-[#24594f] px-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d473f] disabled:cursor-not-allowed disabled:bg-[#8aa19b]"
                >
                  {isSearching ? '...' : 'Search'}
                </button>
              </span>
            </div>
          </form>
          )}
          {mode === 'chat' && (
            <form onSubmit={onAskQuestion} aria-label="Ask all Portland City Code from the front panel">
              <div>
                <label htmlFor="mobile-front-chat" className="mb-1 block text-sm font-semibold text-[#26343a]">
                  Ask all Portland City Code
                </label>
                <span className="grid grid-cols-[minmax(0,1fr)_76px] gap-2">
                  <textarea
                    id="mobile-front-chat"
                    value={question}
                    onChange={(event) => onQuestionChange(event.target.value)}
                    rows={2}
                    className="min-h-[4.5rem] w-full resize-none rounded-md border border-[#8fa08a] bg-white px-3 py-2 text-base text-[#172026] shadow-sm"
                    placeholder="What notice is required?"
                  />
                  <button
                    type="submit"
                    disabled={isAnswering}
                    className="min-h-[4.5rem] rounded-md bg-[#24594f] px-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d473f] disabled:cursor-not-allowed disabled:bg-[#8aa19b]"
                  >
                    {isAnswering ? '...' : 'Ask'}
                  </button>
                </span>
                <div className="mt-3 grid gap-2" aria-label="Mobile suggested chat questions">
                  {CHAT_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => onQuestionChange(prompt)}
                      className="min-h-11 rounded-md border border-[#8fa08a] bg-[#f7faf4] px-3 py-2 text-left text-sm font-semibold text-[#24594f]"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </form>
          )}
          {mode === 'chat' && (
            <nav className="mt-3 grid grid-cols-2 gap-2" aria-label="Mobile page shortcuts">
              <a
                href="#code-directory"
                className="flex min-h-11 items-center justify-center rounded-md border border-[#8fa08a] bg-[#f7faf4] px-3 text-sm font-semibold text-[#24594f]"
              >
                Browse titles
              </a>
              <a
                href="#code-search"
                className="flex min-h-11 items-center justify-center rounded-md border border-[#8fa08a] bg-[#f7faf4] px-3 text-sm font-semibold text-[#24594f]"
              >
                View results
              </a>
            </nav>
          )}
        </div>
      </div>
    </section>
  );
}

function DirectoryPanel({
  className = '',
  directory,
  selectedTitle,
  selectedChapter,
  onSelectTitle,
  onSelectChapter,
}: {
  className?: string;
  directory: DirectoryTitle[];
  selectedTitle: string;
  selectedChapter: string;
  onSelectTitle: (titleNumber: string) => void;
  onSelectChapter: (titleNumber: string, chapterNumber: string) => void;
}) {
  const totalChapters = directory.reduce((count, title) => count + title.chapters.length, 0);
  const totalSections = directory.reduce((count, title) => count + title.sections.length, 0);

  return (
    <section
      id="code-directory"
      aria-labelledby="code-directory-heading"
      className={`min-w-0 rounded-md border border-[#d8dfd3] bg-white shadow-sm lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)] lg:overflow-auto ${className}`}
    >
      <div className="border-b border-[#e1e6dc] px-4 py-4">
        <h2 id="code-directory-heading" className="text-lg font-semibold text-[#172026]">
          City Code
        </h2>
        <p className="mt-1 text-sm leading-6 text-[#4f615b]">
          {directory.length} titles · {totalChapters.toLocaleString()} chapters · {totalSections.toLocaleString()} sections
        </p>
        <p className="mt-1 text-sm leading-6 text-[#4f615b]">
          Choose a title to browse chapters and narrow the code manually.
        </p>
      </div>
      <details className="group lg:hidden" open>
        <summary className="flex min-h-11 cursor-pointer items-center justify-between gap-3 px-4 py-3 text-sm font-semibold text-[#24594f]">
          Browse titles
          <span className="text-xs uppercase tracking-wide text-[#607068]">
            <span className="group-open:hidden">Expand</span>
            <span className="hidden group-open:inline">Collapse</span>
          </span>
        </summary>
        <nav aria-label="City Code mobile" className="max-h-[36vh] overflow-auto border-t border-[#edf1e8]">
          <DirectoryList
            directory={directory}
            selectedTitle={selectedTitle}
            selectedChapter={selectedChapter}
            onSelectTitle={onSelectTitle}
            onSelectChapter={onSelectChapter}
            idPrefix="mobile"
          />
        </nav>
      </details>
      <nav aria-label="City Code" className="hidden lg:block">
        <DirectoryList
          directory={directory}
          selectedTitle={selectedTitle}
          selectedChapter={selectedChapter}
          onSelectTitle={onSelectTitle}
          onSelectChapter={onSelectChapter}
          idPrefix="desktop"
        />
      </nav>
    </section>
  );
}

function DirectoryList({
  directory,
  selectedTitle,
  selectedChapter,
  onSelectTitle,
  onSelectChapter,
  idPrefix,
}: {
  directory: DirectoryTitle[];
  selectedTitle: string;
  selectedChapter: string;
  onSelectTitle: (titleNumber: string) => void;
  onSelectChapter: (titleNumber: string, chapterNumber: string) => void;
  idPrefix: string;
}) {
  return (
    <ul className="divide-y divide-[#edf1e8]">
      {directory.map((title) => (
        <li key={title.number} className="px-3 py-2">
          <button
            type="button"
            onClick={() => onSelectTitle(title.number)}
            aria-expanded={selectedTitle === title.number}
            aria-controls={`${idPrefix}-title-${title.number}-chapters`}
            className={`min-h-12 w-full rounded-md px-3 py-2 text-left transition ${
              selectedTitle === title.number ? 'bg-[#e8f0e8]' : 'hover:bg-[#f6f8f3]'
            }`}
          >
            <div className="text-sm font-semibold text-[#24594f]">Title {title.number}</div>
            <div className="mt-0.5 text-sm leading-5 text-[#26343a]">{title.label}</div>
            <div className="mt-1 text-xs text-[#66756f]">
              {title.chapters.length} chapters · {title.sections.length} sections
            </div>
          </button>
          {selectedTitle === title.number && (
            <ul id={`${idPrefix}-title-${title.number}-chapters`} className="mt-2 space-y-1 pl-3">
              {title.chapters.slice(0, 30).map((chapter) => (
                <li key={chapter.number}>
                  <button
                    type="button"
                    onClick={() => onSelectChapter(title.number, chapter.number)}
                    aria-current={selectedChapter === chapter.number ? 'true' : undefined}
                    className={`block min-h-11 w-full rounded-md px-3 py-2 text-left text-sm ${
                      selectedChapter === chapter.number
                        ? 'bg-[#24594f] text-white'
                        : 'text-[#394a4f] hover:bg-[#f2f5ee]'
                    }`}
                  >
                    Chapter {chapter.number}
                    <span className="ml-2 text-xs opacity-75">({chapter.sections.length})</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </li>
      ))}
    </ul>
  );
}

function SearchPanel({
  className = '',
  query,
  titleFilter,
  chapterFilter,
  normFilter,
  directory,
  visibleChapters,
  results,
  selectedCid,
  proofByCid,
  loadState,
  isSearching,
  error,
  chatQuestion,
  isAnswering,
  onQueryChange,
  onQuestionChange,
  onTitleChange,
  onChapterChange,
  onNormChange,
  onClearFilters,
  onSubmit,
  onAskQuestion,
  onSelectResult,
  onExample,
}: {
  className?: string;
  query: string;
  titleFilter: string;
  chapterFilter: string;
  normFilter: NormType | '';
  directory: DirectoryTitle[];
  visibleChapters: DirectoryChapter[];
  results: SearchResult[];
  selectedCid: string | null;
  proofByCid: Map<string, LogicProofSummary>;
  loadState: LoadState;
  isSearching: boolean;
  error: string | null;
  chatQuestion: string;
  isAnswering: boolean;
  onQueryChange: (query: string) => void;
  onQuestionChange: (question: string) => void;
  onTitleChange: (title: string) => void;
  onChapterChange: (chapter: string) => void;
  onNormChange: (norm: NormType | '') => void;
  onClearFilters: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onAskQuestion: (event: FormEvent<HTMLFormElement>) => void;
  onSelectResult: (cid: string) => void;
  onExample: (query: string) => void;
}) {
  const [resultLimit, setResultLimit] = useState(INITIAL_RESULT_LIMIT);
  const [desktopMode, setDesktopMode] = useState<'search' | 'chat'>('search');
  const selectedIndex = results.findIndex((result) => result.ipfs_cid === selectedCid);
  const visibleLimit = Math.max(resultLimit, selectedIndex >= 0 ? selectedIndex + 1 : INITIAL_RESULT_LIMIT);
  const visibleResults = results.slice(0, visibleLimit);
  const hiddenResultCount = Math.max(results.length - visibleResults.length, 0);
  const activeFilters = buildActiveFilterChips(query, titleFilter, chapterFilter, normFilter, directory);
  const resultStatus =
    loadState === 'ready'
      ? hiddenResultCount > 0
        ? `${results.length} matches, showing ${visibleResults.length}`
        : `${results.length} matches`
      : 'Loading corpus';

  useEffect(() => {
    setResultLimit(INITIAL_RESULT_LIMIT);
  }, [results]);

  return (
    <section
      id="code-search"
      aria-labelledby="code-search-heading"
      className={`min-w-0 rounded-md border border-[#d8dfd3] bg-[#fbfcf8] shadow-sm ${className}`}
    >
      <div className="border-b border-[#e1e6dc] px-4 py-3 sm:py-4">
        <h2 id="code-search-heading" className="text-lg font-semibold text-[#172026]">
          Search and Chat
        </h2>
        <p className="mt-1 hidden text-sm leading-6 text-[#4f615b] sm:block">
          Search the code directly, or ask a plain-language question across the full Portland City Code.
        </p>
      </div>

      <div className="hidden border-b border-[#e1e6dc] bg-white px-4 py-3 sm:block" role="tablist" aria-label="Choose search or chat">
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            role="tab"
            aria-selected={desktopMode === 'search'}
            aria-controls="desktop-search-panel"
            onClick={() => setDesktopMode('search')}
            className={`min-h-11 rounded-md px-3 text-sm font-semibold ${
              desktopMode === 'search'
                ? 'bg-[#24594f] text-white'
                : 'border border-[#8fa08a] bg-[#f7faf4] text-[#24594f] hover:bg-[#f3f6ef]'
            }`}
          >
            Search code
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={desktopMode === 'chat'}
            aria-controls="desktop-chat-panel"
            onClick={() => setDesktopMode('chat')}
            className={`min-h-11 rounded-md px-3 text-sm font-semibold ${
              desktopMode === 'chat'
                ? 'bg-[#24594f] text-white'
                : 'border border-[#8fa08a] bg-[#f7faf4] text-[#24594f] hover:bg-[#f3f6ef]'
            }`}
          >
            Chat with code
          </button>
        </div>
      </div>

      <form
        id="desktop-search-panel"
        onSubmit={onSubmit}
        className={`grid gap-2 border-b border-[#e1e6dc] px-4 py-3 sm:gap-3 sm:py-4 ${desktopMode === 'search' ? 'sm:grid' : 'sm:hidden'}`}
        aria-label="Search and filter code sections"
      >
        <label className="hidden sm:block">
          <span className="mb-1 block text-sm font-semibold text-[#26343a]">Search Portland City Code</span>
          <input
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            aria-describedby="search-help"
            className="h-12 w-full rounded-md border border-[#8fa08a] bg-white px-4 text-base text-[#172026] shadow-sm transition"
            placeholder="Search code sections"
          />
          <span id="search-help" className="sr-only sm:not-sr-only sm:mt-1 sm:block sm:text-sm sm:leading-6 sm:text-[#4f615b]">
            Search by words, citation, topic, or a plain-language question.
          </span>
        </label>

        <details className="group rounded-md border border-[#dce3d6] bg-white sm:hidden">
          <summary className="flex min-h-11 cursor-pointer items-center justify-between gap-3 px-3 py-2 text-sm font-semibold text-[#24594f]">
            Filters and examples
            <span className="text-xs uppercase tracking-wide text-[#607068]">
              <span className="group-open:hidden">Expand</span>
              <span className="hidden group-open:inline">Collapse</span>
            </span>
          </summary>
          <div className="grid gap-3 border-t border-[#edf1e8] px-3 py-3">
            <FilterControls
              titleFilter={titleFilter}
              chapterFilter={chapterFilter}
              normFilter={normFilter}
              directory={directory}
              visibleChapters={visibleChapters}
              onTitleChange={onTitleChange}
              onChapterChange={onChapterChange}
              onNormChange={onNormChange}
            />
            <ExampleSearches onExample={onExample} />
          </div>
        </details>

        <div className="hidden gap-3 sm:grid">
          <div className="grid gap-3 sm:grid-cols-2">
            <FilterControls
              titleFilter={titleFilter}
              chapterFilter={chapterFilter}
              normFilter={normFilter}
              directory={directory}
              visibleChapters={visibleChapters}
              onTitleChange={onTitleChange}
              onChapterChange={onChapterChange}
              onNormChange={onNormChange}
              includeNorm={false}
            />
          </div>
          <div className="grid gap-3 sm:grid-cols-[1fr_120px]">
            <FilterControls
              titleFilter={titleFilter}
              chapterFilter={chapterFilter}
              normFilter={normFilter}
              directory={directory}
              visibleChapters={visibleChapters}
              onTitleChange={onTitleChange}
              onChapterChange={onChapterChange}
              onNormChange={onNormChange}
              includeTitle={false}
              includeChapter={false}
            />
            <button
              type="submit"
              disabled={loadState !== 'ready' || isSearching}
              aria-describedby="search-status"
              className="min-h-11 rounded-md bg-[#24594f] px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d473f] disabled:cursor-not-allowed disabled:bg-[#8aa19b]"
            >
              {isSearching ? 'Searching' : 'Search'}
            </button>
          </div>
          <ExampleSearches onExample={onExample} />
        </div>

        <div className="hidden">
          <button
            type="submit"
            disabled={loadState !== 'ready' || isSearching}
            aria-describedby="search-status"
            className="min-h-11 w-full rounded-md bg-[#24594f] px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d473f] disabled:cursor-not-allowed disabled:bg-[#8aa19b]"
          >
            {isSearching ? 'Searching' : 'Search'}
          </button>
        </div>
      </form>

      <section
        id="desktop-chat-panel"
        className={`border-b border-[#e1e6dc] px-4 py-4 ${desktopMode === 'chat' ? 'hidden sm:block' : 'hidden'}`}
        aria-label="Chat with Portland City Code"
      >
        <div className="mb-2">
          <h3 className="text-base font-semibold text-[#172026]">Chat with all Portland City Code</h3>
          <p className="mt-1 text-sm leading-6 text-[#4f615b]">
            Ask the full local corpus. The answer opens in Code Chat with cited Portland City Code evidence.
          </p>
        </div>
        <form onSubmit={onAskQuestion} className="grid gap-2" aria-label="Desktop corpus chat">
          <label>
            <span className="mb-1 block text-sm font-semibold text-[#26343a]">Ask all Portland City Code</span>
            <textarea
              value={chatQuestion}
              onChange={(event) => onQuestionChange(event.target.value)}
              rows={3}
              className="min-h-[6rem] w-full resize-none rounded-md border border-[#8fa08a] bg-white px-3 py-2 text-base text-[#172026] shadow-sm"
              placeholder="What does the code say about noise complaints?"
            />
          </label>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="submit"
              disabled={isAnswering}
              className="min-h-11 rounded-md bg-[#24594f] px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d473f] disabled:cursor-not-allowed disabled:bg-[#8aa19b]"
            >
              {isAnswering ? 'Asking' : 'Ask'}
            </button>
            {CHAT_PROMPTS.slice(0, 2).map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => onQuestionChange(prompt)}
                className="min-h-11 rounded-md border border-[#8fa08a] bg-white px-3 py-2 text-left text-sm font-semibold text-[#24594f] hover:bg-[#f3f6ef]"
              >
                {prompt}
              </button>
            ))}
          </div>
        </form>
      </section>

      <div className="px-4 py-3 sm:py-4">
        <div className="mb-3 grid gap-3">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-base font-semibold text-[#172026]">Results</h3>
            <span id="search-status" role="status" aria-live="polite" className="text-sm text-[#4f615b]">
              {resultStatus}
            </span>
          </div>
          <div
            className="flex flex-wrap items-center gap-2 rounded-md border border-[#dce3d6] bg-white px-3 py-2"
            aria-label="Current search filters"
          >
            <span className="text-xs font-semibold uppercase tracking-wide text-[#607068]">Active</span>
            {activeFilters.length > 0 ? (
              activeFilters.map((filter) => (
                <span
                  key={filter}
                  className="rounded-md bg-[#eef2ea] px-2 py-1 text-xs font-semibold text-[#394a4f]"
                >
                  {filter}
                </span>
              ))
            ) : (
              <span className="text-sm text-[#4f615b]">All titles and norms</span>
            )}
            {activeFilters.length > 0 && (
              <button
                type="button"
                onClick={onClearFilters}
                className="ml-auto min-h-9 rounded-md border border-[#8fa08a] px-3 text-xs font-semibold text-[#24594f] hover:bg-[#f3f6ef]"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="mb-3 rounded-md border border-[#d89b82] bg-[#fff4ef] px-3 py-2 text-sm text-[#8a3b22]">
            {error}
          </div>
        )}
        {loadState === 'loading' && <EmptyState title="Loading Portland code corpus" />}
        {loadState === 'error' && <EmptyState title="Corpus assets could not be loaded" />}
        {loadState === 'ready' && results.length === 0 && <EmptyState title="No matching sections" />}

        <div
          className="space-y-3"
          aria-label={`Search results${hiddenResultCount > 0 ? ` showing top ${visibleResults.length} of ${results.length}` : ''}`}
        >
          {visibleResults.map((result) => (
            <ResultCard
              key={result.ipfs_cid}
              result={result}
              proof={proofByCid.get(result.ipfs_cid) || null}
              selected={selectedCid === result.ipfs_cid}
              onSelect={() => onSelectResult(result.ipfs_cid)}
            />
          ))}
        </div>
        {hiddenResultCount > 0 && (
          <div className="mt-3 rounded-md border border-[#dce3d6] bg-white px-3 py-3">
            <p className="text-sm leading-6 text-[#4f615b]">
              Showing {visibleResults.length} strong matches. Refine the search or filters to narrow the remaining{' '}
              {hiddenResultCount.toLocaleString()} results.
            </p>
            <button
              type="button"
              onClick={() => setResultLimit((current) => Math.min(current + RESULT_INCREMENT, results.length))}
              className="mt-2 min-h-11 rounded-md border border-[#8fa08a] px-3 text-sm font-semibold text-[#24594f] hover:bg-[#f3f6ef]"
            >
              Show {Math.min(RESULT_INCREMENT, hiddenResultCount)} more results
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

function WorkspacePanel({
  className = '',
  selected,
  proof,
  relatedEntities,
  relatedRelationships,
  isGraphLoading,
  activeTab,
  setActiveTab,
  chatQuestion,
  chatAnswer,
  chatEvidence,
  chatError,
  chatUsedLocalModel,
  chatGenerationSource,
  chatGenerationWarning,
  isAnswering,
  onQuestionChange,
  onAskQuestion,
}: {
  className?: string;
  selected: CorpusSection | null;
  proof: LogicProofSummary | null;
  relatedEntities: CorpusEntity[];
  relatedRelationships: CorpusRelationship[];
  isGraphLoading: boolean;
  activeTab: WorkspaceTab;
  setActiveTab: (tab: WorkspaceTab) => void;
  chatQuestion: string;
  chatAnswer: string;
  chatEvidence: GraphRagEvidence | null;
  chatError: string | null;
  chatUsedLocalModel: boolean;
  chatGenerationSource: 'local' | 'cloud' | 'retrieved';
  chatGenerationWarning: string | null;
  isAnswering: boolean;
  onQuestionChange: (question: string) => void;
  onAskQuestion: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const tabs: Array<{ tab: WorkspaceTab; label: string; shortLabel: string }> = [
    { tab: 'section', label: 'Section', shortLabel: 'Section' },
    { tab: 'chat', label: 'Chat', shortLabel: 'Chat' },
    { tab: 'graph', label: 'Knowledge Graph', shortLabel: 'Graph' },
    { tab: 'proof', label: 'Logic Proofs', shortLabel: 'Proofs' },
  ];
  const activeIndex = tabs.findIndex((item) => item.tab === activeTab);

  function onTabKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
      return;
    }
    event.preventDefault();
    const lastIndex = tabs.length - 1;
    const nextIndex =
      event.key === 'Home'
        ? 0
        : event.key === 'End'
          ? lastIndex
          : event.key === 'ArrowRight'
            ? (activeIndex + 1) % tabs.length
            : (activeIndex - 1 + tabs.length) % tabs.length;
    const nextTab = tabs[nextIndex].tab;
    setActiveTab(nextTab);
    window.requestAnimationFrame(() => {
      document.getElementById(`tab-${nextTab}`)?.focus();
    });
  }

  function openTab(tab: WorkspaceTab) {
    setActiveTab(tab);
    window.requestAnimationFrame(() => {
      document.getElementById(`panel-${tab}`)?.focus();
    });
  }

  return (
    <section
      id="research-workbench"
      aria-labelledby="research-workbench-heading"
      className={`min-w-0 self-start rounded-md border border-[#d8dfd3] bg-white shadow-sm ${className}`}
    >
      <div className="border-b border-[#e1e6dc] px-4 pt-3 sm:pt-4">
        <h2 id="research-workbench-heading" className="sr-only">
          Selected section and research tools
        </h2>
        <div className="flex gap-1.5 overflow-x-auto pb-px sm:gap-2" role="tablist" aria-label="Research workspace panels">
          <a
            href="#code-search"
            aria-label="Back to results"
            className="inline-flex min-h-11 shrink-0 items-center rounded-t-md border border-b-0 border-[#d8dfd3] bg-white px-2 py-2 text-xs font-semibold text-[#24594f] hover:bg-[#f3f6ef] sm:px-3 sm:text-sm lg:hidden"
          >
            Results
          </a>
          {tabs.map(({ tab, label, shortLabel }) => (
            <button
              id={`tab-${tab}`}
              key={tab}
              type="button"
              role="tab"
              aria-label={label}
              aria-selected={activeTab === tab}
              aria-controls={`panel-${tab}`}
              tabIndex={activeTab === tab ? 0 : -1}
              onClick={() => setActiveTab(tab as WorkspaceTab)}
              onKeyDown={onTabKeyDown}
              title={label}
              className={`min-h-11 shrink-0 rounded-t-md border border-b-0 px-2 py-2 text-xs font-semibold sm:px-3 sm:text-sm ${
                activeTab === tab
                  ? 'border-[#d8dfd3] bg-white text-[#24594f]'
                  : 'border-transparent bg-[#eef2ea] text-[#596861] hover:text-[#24594f]'
              }`}
            >
              <span className="sm:hidden">{shortLabel}</span>
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="min-h-[420px] lg:min-h-[560px]" aria-live="polite">
        {!selected && <EmptyState title="Select a section" />}
        {selected && activeTab === 'section' && (
          <div id="panel-section" role="tabpanel" aria-labelledby="tab-section" tabIndex={0}>
            <SectionReader
              section={selected}
              onOpenChat={() => openTab('chat')}
              onOpenGraph={() => openTab('graph')}
              onOpenProof={() => openTab('proof')}
            />
          </div>
        )}
        {selected && activeTab === 'chat' && (
          <div id="panel-chat" role="tabpanel" aria-labelledby="tab-chat" tabIndex={0}>
          <GraphRagChat
            question={chatQuestion}
            answer={chatAnswer}
            evidence={chatEvidence}
            error={chatError}
            generationWarning={chatGenerationWarning}
            usedLocalModel={chatUsedLocalModel}
            generationSource={chatGenerationSource}
            isAnswering={isAnswering}
              onQuestionChange={onQuestionChange}
              onSubmit={onAskQuestion}
            />
          </div>
        )}
        {selected && activeTab === 'graph' && (
          <div id="panel-graph" role="tabpanel" aria-labelledby="tab-graph" tabIndex={0}>
            <GraphPanel entities={relatedEntities} relationships={relatedRelationships} isLoading={isGraphLoading} />
          </div>
        )}
        {selected && activeTab === 'proof' && (
          <div id="panel-proof" role="tabpanel" aria-labelledby="tab-proof" tabIndex={0}>
            <ProofPanel proof={proof} />
          </div>
        )}
      </div>
    </section>
  );
}

function FilterControls({
  titleFilter,
  chapterFilter,
  normFilter,
  directory,
  visibleChapters,
  onTitleChange,
  onChapterChange,
  onNormChange,
  includeTitle = true,
  includeChapter = true,
  includeNorm = true,
}: {
  titleFilter: string;
  chapterFilter: string;
  normFilter: NormType | '';
  directory: DirectoryTitle[];
  visibleChapters: DirectoryChapter[];
  onTitleChange: (title: string) => void;
  onChapterChange: (chapter: string) => void;
  onNormChange: (norm: NormType | '') => void;
  includeTitle?: boolean;
  includeChapter?: boolean;
  includeNorm?: boolean;
}) {
  return (
    <>
      {includeTitle && (
        <Select value={titleFilter} onChange={onTitleChange} label="Title">
          <option value="">All titles</option>
          {directory.map((title) => (
            <option key={title.number} value={title.number}>
              Title {title.number}
            </option>
          ))}
        </Select>
      )}
      {includeChapter && (
        <Select value={chapterFilter} onChange={onChapterChange} label="Chapter" disabled={!titleFilter}>
          <option value="">All chapters</option>
          {visibleChapters.map((chapter) => (
            <option key={chapter.number} value={chapter.number}>
              Chapter {chapter.number}
            </option>
          ))}
        </Select>
      )}
      {includeNorm && (
        <Select value={normFilter} onChange={(value) => onNormChange(value as NormType | '')} label="Norm">
          <option value="">All norms</option>
          <option value="obligation">Obligations</option>
          <option value="permission">Permissions</option>
          <option value="prohibition">Prohibitions</option>
          <option value="unknown">Unknown norms</option>
        </Select>
      )}
    </>
  );
}

function ExampleSearches({ onExample }: { onExample: (query: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2" aria-label="Example searches">
      {EXAMPLE_QUERIES.map((example) => (
        <button
          key={example}
          type="button"
          onClick={() => onExample(example)}
          className="min-h-11 max-w-full rounded-md border border-[#aab8a4] bg-white px-3 py-2 text-left text-sm text-[#30413f] hover:border-[#49635a]"
        >
          {example}
        </button>
      ))}
    </div>
  );
}

function Select({
  value,
  onChange,
  label,
  disabled,
  children,
}: {
  value: string;
  onChange: (value: string) => void;
  label: string;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-[#607068]">{label}</span>
      <select
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-11 w-full rounded-md border border-[#8fa08a] bg-white px-3 text-sm text-[#172026] shadow-sm transition disabled:bg-[#eef2ea]"
      >
        {children}
      </select>
    </label>
  );
}

function ResultCard({
  result,
  proof,
  selected,
  onSelect,
}: {
  result: SearchResult;
  proof: LogicProofSummary | null;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      aria-label={`Select ${result.citation}: ${result.section.title}`}
      className={`block min-h-12 w-full rounded-md border bg-white p-4 text-left shadow-sm transition hover:border-[#49635a] ${
        selected ? 'border-[#24594f] ring-2 ring-[#24594f]/15' : 'border-[#dde3d8]'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-[#24594f]">{result.citation}</p>
          <h3 className="mt-1 text-base font-semibold leading-snug text-[#172026] [overflow-wrap:anywhere]">
            {result.section.title}
          </h3>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-2">
          <span
            className={`rounded-md px-2 py-1 text-xs font-semibold ${
              selected ? 'bg-[#24594f] text-white' : 'border border-[#8fa08a] bg-white text-[#24594f]'
            }`}
          >
            {selected ? 'Selected' : 'Open section'}
          </span>
        </div>
      </div>

      <ResultSnippet snippet={result.snippet} />
    </button>
  );
}

function ResultSnippet({ snippet }: { snippet: string }) {
  const cleaned = cleanCorpusSnippet(snippet);
  const clauseMatch = cleaned.match(/(?:^|\s)([A-Z])\.\s+/);

  if (!clauseMatch || clauseMatch.index === undefined) {
    return (
      <div className="mt-3 text-sm leading-6 text-[#52615c]" aria-label="Structured result preview">
        <p className="line-clamp-3 [overflow-wrap:anywhere]">{cleaned}</p>
      </div>
    );
  }

  const clauseLabel = clauseMatch[1];
  const contentStart = clauseMatch.index + clauseMatch[0].length;
  const previewText = cleaned.slice(contentStart).trim();
  const structured = splitNumberedSubparts(previewText);

  return (
    <div className="mt-3 grid gap-1 text-sm leading-6 text-[#52615c]" aria-label="Structured result preview">
      <span className="w-fit rounded-md border border-[#d4ddd0] bg-[#f8faf5] px-2 py-0.5 text-xs font-semibold text-[#53655f]">
        {clauseLabel}.
      </span>
      {structured ? (
        <>
          {structured.preface && <p className="line-clamp-2 [overflow-wrap:anywhere]">{structured.preface}</p>}
          <ol className="list-decimal space-y-0.5 pl-5 marker:font-semibold marker:text-[#24594f]" aria-label="Preview requirements">
            {structured.items.slice(0, 2).map((item, index) => (
              <li key={`${index}-${item.slice(0, 20)}`} className="line-clamp-2 [overflow-wrap:anywhere]">
                {item}
              </li>
            ))}
          </ol>
        </>
      ) : (
        <p className="line-clamp-3 [overflow-wrap:anywhere]">{previewText || cleaned}</p>
      )}
    </div>
  );
}

function formatNormOperatorForBadge(operator: string) {
  const normalized = operator.toUpperCase();
  if (normalized === 'O') return 'required';
  if (normalized === 'P') return 'allowed';
  if (normalized === 'F') return 'forbidden';
  return operator;
}

function formatProofStatusForBadge(status: string) {
  if (status === 'success') return 'proof ok';
  if (status === 'warning') return 'needs review';
  if (status === 'error') return 'proof error';
  return status.replace(/_/g, ' ');
}

function formatResultNormOperatorForBadge(operator: string) {
  return formatNormOperatorForBadge(operator)
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatResultProofStatusForBadge(status: string) {
  if (status === 'success') return 'Proof OK';
  return formatProofStatusForBadge(status)
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNormOperatorForDisplay(operator: string) {
  const normalized = operator.toUpperCase();
  if (normalized === 'O') return 'Required (O)';
  if (normalized === 'P') return 'Allowed (P)';
  if (normalized === 'F') return 'Forbidden (F)';
  return operator || 'Unknown';
}

function formatNormTypeForDisplay(norm: string) {
  if (!norm) return 'Unknown';
  return norm
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatLogicStatusForDisplay(status: string) {
  if (status === 'success') return 'Success';
  if (status === 'warning') return 'Needs review';
  if (status === 'error') return 'Error';
  return formatNormTypeForDisplay(status);
}

function formatSectionRefsForDisplay(refs: string[]) {
  if (refs.length === 0) return 'None';
  return refs.map(formatSectionRefForDisplay).join(', ');
}

function formatSectionRefForDisplay(ref: string) {
  const normalized = ref.replace(/^portland_city_code_?/i, '').replace(/_/g, '.');
  if (!normalized) return ref;
  return `Portland City Code ${normalized}`;
}

function formatDeonticOperatorsForDisplay(operators: string[]) {
  if (operators.length === 0) return 'None';
  return operators.map(formatNormOperatorForDisplay).join(', ');
}

function buildActiveFilterChips(
  query: string,
  titleFilter: string,
  chapterFilter: string,
  normFilter: NormType | '',
  directory: DirectoryTitle[],
) {
  const chips: string[] = [];
  const trimmedQuery = query.trim();
  const title = directory.find((item) => item.number === titleFilter);
  if (trimmedQuery) chips.push(`"${trimmedQuery}"`);
  if (title) chips.push(`Title ${title.number}`);
  if (chapterFilter) chips.push(`Chapter ${chapterFilter}`);
  if (normFilter) chips.push(formatNormTypeLabel(normFilter));
  return chips;
}

function formatNormTypeLabel(norm: NormType) {
  if (norm === 'obligation') return 'Obligations';
  if (norm === 'permission') return 'Permissions';
  if (norm === 'prohibition') return 'Prohibitions';
  return 'Unknown norms';
}

function GraphRagChat({
  question,
  answer,
  evidence,
  error,
  generationWarning,
  usedLocalModel,
  generationSource,
  isAnswering,
  onQuestionChange,
  onSubmit,
}: {
  question: string;
  answer: string;
  evidence: GraphRagEvidence | null;
  error: string | null;
  generationWarning: string | null;
  usedLocalModel: boolean;
  generationSource: 'local' | 'cloud' | 'retrieved';
  isAnswering: boolean;
  onQuestionChange: (question: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const evidenceSections = evidence?.sections.slice(0, 5) || [];
  const topCitation = evidenceSections[0]?.citation || 'None yet';
  const [cloudConfigured, setCloudConfigured] = useState(false);
  const [cloudBaseUrl, setCloudBaseUrl] = useState('');
  const [localProven, setLocalProven] = useState(false);
  const [performanceProven, setPerformanceProven] = useState(false);
  const [tokensPerSecond, setTokensPerSecond] = useState<number | null>(null);

  useEffect(() => {
    const refresh = () => {
      const cloud = clientLLMWorkerService.getCloudFallbackStatus();
      const status = clientLLMWorkerService.getStatus();
      setCloudConfigured(cloud.configured);
      setCloudBaseUrl(cloud.baseUrl);
      setLocalProven(status.localHealth.proven);
      setPerformanceProven(status.localHealth.performanceProven);
      setTokensPerSecond(status.localHealth.lastMeasuredTokensPerSecond ?? null);
    };

    const onDiagnostic = () => refresh();
    refresh();
    window.addEventListener('clientLLMServiceDiagnostic', onDiagnostic as EventListener);
    return () => {
      window.removeEventListener('clientLLMServiceDiagnostic', onDiagnostic as EventListener);
    };
  }, []);

  const routeLabel = !cloudConfigured
    ? 'Local only'
    : !localProven
      ? 'Proxy first (warming local)'
      : !performanceProven
        ? 'Proxy first (benchmarking local speed)'
        : 'Local ready';

  return (
    <div className="px-4 py-4 sm:px-5 sm:py-5">
      <div className="mb-4">
        <h2 className="text-xl font-semibold tracking-normal text-[#172026]">Code Chat</h2>
        <p className="mt-1 text-base leading-7 text-[#4f615b]">Ask questions grounded in local Portland City Code evidence.</p>
        <div className="mt-2 flex flex-wrap items-center gap-2" aria-label="Inference routing status">
          <span className="rounded-md border border-[#cdd8cb] bg-white px-2 py-1 text-xs font-semibold text-[#24594f]">
            {routeLabel}
          </span>
          {tokensPerSecond !== null && (
            <span className="rounded-md border border-[#d8dfd3] bg-[#f7faf4] px-2 py-1 text-xs font-semibold text-[#4f615b]">
              Local speed {tokensPerSecond.toFixed(1)} tok/s
            </span>
          )}
          {cloudConfigured && (
            <span className="rounded-md border border-[#d8dfd3] bg-[#f7faf4] px-2 py-1 text-xs text-[#4f615b]">
              Proxy {cloudBaseUrl}
            </span>
          )}
        </div>
      </div>
      <form onSubmit={onSubmit} className="grid gap-3 md:grid-cols-[1fr_112px]">
        <label className="block">
          <span className="mb-1 block text-sm font-semibold text-[#26343a]">Question</span>
          <input
            value={question}
            onChange={(event) => onQuestionChange(event.target.value)}
            aria-describedby="chat-help"
            className="min-h-11 w-full rounded-md border border-[#8fa08a] bg-white px-3 text-sm text-[#172026] shadow-sm transition"
            placeholder="Ask about the Portland City Code"
          />
          <span id="chat-help" className="mt-1 block text-sm leading-6 text-[#4f615b]">
            Answers are informational and cite retrieved code sections.
          </span>
        </label>
        <button
          type="submit"
          disabled={isAnswering}
          className="min-h-11 rounded-md bg-[#24594f] px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d473f] disabled:cursor-not-allowed disabled:bg-[#8aa19b] md:mt-6 md:self-start"
        >
          {isAnswering ? 'Asking' : 'Ask'}
        </button>
      </form>

      {error && (
        <div role="alert" className="mt-4 rounded-md border border-[#d89b82] bg-[#fff4ef] px-3 py-2 text-sm text-[#8a3b22]">
          {error}
        </div>
      )}
      {generationWarning && (
        <div role="status" className="mt-4 rounded-md border border-[#d8c27a] bg-[#fff9df] px-3 py-2 text-sm text-[#71551b]">
          {generationWarning}
        </div>
      )}
      {answer && (
        <div className="mt-4 grid gap-2 sm:grid-cols-3" aria-label="Chat response summary">
          <ChatSummaryMetric label="Sources found" value={evidenceSections.length.toLocaleString()} />
          <ChatSummaryMetric
            label="Answer basis"
            value={generationSource === 'local' ? 'Local model' : generationSource === 'cloud' ? 'Proxy model' : 'Retrieved code'}
          />
          <ChatSummaryMetric label="Top citation" value={topCitation} />
        </div>
      )}
      {answer && (
        <div
          className="mt-4 rounded-md border border-[#dce3d6] bg-[#f8faf5] px-4 py-4"
          aria-label="Chat answer"
          aria-live="polite"
        >
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-[#607068]">Answer with citations</h3>
          <CitedAnswer text={answer} />
        </div>
      )}
      {!answer && !error && (
        <div className="mt-4" aria-label="Chat empty state">
          <ChatPromptStarters onQuestionChange={onQuestionChange} />
        </div>
      )}
      {evidenceSections.length > 0 && (
        <div className="mt-4" aria-label="Chat evidence">
          <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-[#607068]">Evidence</h3>
          <div className="mt-2 grid gap-2">
            {evidenceSections.map((result, index) => (
              <a
                key={result.ipfs_cid}
                href={result.section.source_url}
                target="_blank"
                rel="noreferrer"
                className="grid gap-1 rounded-md border border-[#dce3d6] bg-white px-3 py-2 text-sm hover:border-[#7a9487] sm:grid-cols-[1fr_auto] sm:items-center"
              >
                <span className="min-w-0">
                  <span className="font-semibold text-[#24594f]">[{index + 1}] {result.citation}</span>
                  <span className="ml-2 text-[#394a4f] [overflow-wrap:anywhere]">{result.section.title}</span>
                </span>
                <span className="text-xs font-semibold uppercase tracking-wide text-[#607068]">Official source</span>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ChatPromptStarters({ onQuestionChange }: { onQuestionChange: (question: string) => void }) {
  return (
    <div className="rounded-md border border-dashed border-[#aebba9] bg-white/70 px-4 py-5" role="status">
      <p className="text-center text-sm font-semibold text-[#26343a]">No answer yet</p>
      <div className="mt-3 flex flex-wrap justify-center gap-2" aria-label="Suggested chat questions">
        {CHAT_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onQuestionChange(prompt)}
            className="min-h-11 rounded-md border border-[#8fa08a] bg-white px-3 py-2 text-sm font-semibold text-[#24594f] hover:bg-[#f3f6ef]"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}

function CitedAnswer({ text }: { text: string }) {
  const blocks = text.split(/\n{2,}/).map((block) => block.trim()).filter(Boolean);
  const citationBlocks = blocks
    .map((block) => {
      const match = block.match(/^\[(\d+)\]\s*(.+)$/s);
      return match ? { number: match[1], text: match[2].trim() } : null;
    })
    .filter((block): block is { number: string; text: string } => Boolean(block));
  const introBlocks = blocks.filter((block) => !/^\[\d+\]\s*/.test(block) && !/^Review\b/i.test(block));
  const noteBlocks = blocks.filter((block) => /^Review\b/i.test(block));

  if (citationBlocks.length === 0) {
    return <div className="whitespace-pre-wrap text-sm leading-6 text-[#26343a] [overflow-wrap:anywhere]">{text}</div>;
  }

  return (
    <div className="grid gap-3 text-sm leading-6 text-[#26343a]" aria-label="Cited answer sections">
      {introBlocks.map((block, index) => (
        <p key={`intro-${index}`} className="[overflow-wrap:anywhere]">{block}</p>
      ))}
      <ol className="grid gap-3 list-decimal pl-5 marker:font-semibold marker:text-[#24594f]" aria-label="Cited answer citations">
        {citationBlocks.map((block) => (
          <li key={block.number} className="[overflow-wrap:anywhere]">{block.text}</li>
        ))}
      </ol>
      {noteBlocks.map((block, index) => (
        <p key={`note-${index}`} className="rounded-md border border-[#d6c28e] bg-[#fff9e8] px-3 py-2 text-[#735b18] [overflow-wrap:anywhere]">
          {block}
        </p>
      ))}
    </div>
  );
}

function ChatSummaryMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-[#dce3d6] bg-white px-3 py-3">
      <div className="text-xs font-semibold uppercase tracking-wide text-[#607068]">{label}</div>
      <div className="mt-1 text-sm font-semibold leading-5 text-[#172026] [overflow-wrap:anywhere]">{value}</div>
    </div>
  );
}

function GraphPanel({
  entities,
  relationships,
  isLoading,
}: {
  entities: CorpusEntity[];
  relationships: CorpusRelationship[];
  isLoading: boolean;
}) {
  const usefulRelationships = relationships.filter((relationship) => {
    return formatGraphNodeLabel(relationship.source) !== formatGraphNodeLabel(relationship.target);
  });
  const visibleEntities = entities.slice(0, GRAPH_ENTITY_LIMIT);
  const hiddenEntityCount = Math.max(entities.length - visibleEntities.length, 0);
  const visibleRelationships = usefulRelationships.slice(0, GRAPH_RELATIONSHIP_LIMIT);
  const hiddenRelationshipCount = Math.max(usefulRelationships.length - visibleRelationships.length, 0);
  const topEntityType = isLoading ? 'Loading graph data' : getTopGraphTypeLabel(entities.map((entity) => entity.type));
  const topRelationshipType = isLoading
    ? 'Loading graph data'
    : getTopGraphTypeLabel(usefulRelationships.map((relationship) => relationship.type));
  const entityValue = isLoading ? '...' : entities.length.toLocaleString();
  const relationshipValue = isLoading ? '...' : usefulRelationships.length.toLocaleString();
  const entityTypeCounts = summarizeGraphTypes(entities.map((entity) => entity.type));
  const relationshipTypeCounts = summarizeGraphTypes(usefulRelationships.map((relationship) => relationship.type));

  return (
    <div className="px-4 py-4 sm:px-5 sm:py-5">
      <div className="mb-4">
        <h2 className="text-xl font-semibold tracking-normal text-[#172026]">Knowledge Graph</h2>
        <p className="mt-1 text-sm leading-6 text-[#4f615b]">
          Local entities and relationships connected to the selected code section.
        </p>
      </div>
      <div className="mb-5 grid gap-2 sm:grid-cols-3" aria-label="Graph context summary">
        <GraphSummaryMetric label="Entities" value={entityValue} detail={topEntityType} />
        <GraphSummaryMetric label="Relationships" value={relationshipValue} detail={topRelationshipType} />
        <GraphSummaryMetric label="Neighborhood" value="1 hop" detail="This section" />
      </div>

      <div className="mb-5 grid gap-3 lg:grid-cols-2" aria-label="Graph type summaries">
        <GraphTypeSummary title="Entity types" items={entityTypeCounts} emptyLabel={isLoading ? 'Loading entity types' : 'No entity types'} />
        <GraphTypeSummary title="Relationship types" items={relationshipTypeCounts} emptyLabel={isLoading ? 'Loading relationship types' : 'No relationship types'} />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <div>
          <h3 className="text-lg font-semibold tracking-normal text-[#172026]">Entities</h3>
          <div className="mt-3 grid gap-2" role="list" aria-label="Related knowledge graph entities">
            {isLoading && entities.length === 0 && <EmptyState title="Loading graph entities" />}
            {!isLoading && entities.length === 0 && <EmptyState title="No related entities loaded" />}
            {visibleEntities.map((entity) => (
              <div key={entity.id} role="listitem" className="rounded-md border border-[#dce3d6] bg-[#fbfcf8] px-3 py-2">
                <div className="text-xs font-semibold uppercase tracking-wide text-[#5f7469]">{formatGraphTypeLabel(entity.type)}</div>
                <div className="mt-1 text-sm font-medium leading-5 text-[#223035] [overflow-wrap:anywhere]">
                  {formatGraphValueLabel(entity.label)}
                </div>
              </div>
            ))}
          </div>
          {hiddenEntityCount > 0 && (
            <p className="mt-3 rounded-md border border-[#dce3d6] bg-white px-3 py-2 text-sm leading-6 text-[#4f615b]">
              Showing {visibleEntities.length} of {entities.length} related entities.
            </p>
          )}
        </div>
        <div>
          <h3 className="text-lg font-semibold tracking-normal text-[#172026]">Relationships</h3>
          <div className="mt-3 grid gap-2" role="list" aria-label="Knowledge graph relationships">
            {isLoading && relationships.length === 0 && <EmptyState title="Loading graph relationships" />}
            {!isLoading && relationships.length === 0 && <EmptyState title="No relationships loaded" />}
            {visibleRelationships.map((relationship) => (
              <div key={relationship.id} role="listitem" className="rounded-md border border-[#dce3d6] bg-white px-3 py-2">
                <div className="text-xs font-semibold uppercase tracking-wide text-[#5f7469]">
                  {formatGraphTypeLabel(relationship.type)}
                </div>
                <div className="mt-1 text-sm leading-5 text-[#52615c] [overflow-wrap:anywhere]">
                  {formatGraphNodeLabel(relationship.source)} → {formatGraphNodeLabel(relationship.target)}
                </div>
              </div>
            ))}
          </div>
          {hiddenRelationshipCount > 0 && (
            <p className="mt-3 rounded-md border border-[#dce3d6] bg-white px-3 py-2 text-sm leading-6 text-[#4f615b]">
              Showing {visibleRelationships.length} of {usefulRelationships.length} graph relationships.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function GraphTypeSummary({
  title,
  items,
  emptyLabel,
}: {
  title: string;
  items: Array<{ label: string; count: number }>;
  emptyLabel: string;
}) {
  return (
    <section className="rounded-md border border-[#dce3d6] bg-[#fbfcf8] px-3 py-3" aria-label={title}>
      <h3 className="text-xs font-semibold uppercase tracking-wide text-[#607068]">{title}</h3>
      {items.length > 0 ? (
        <ul className="mt-2 flex flex-wrap gap-2" aria-label={`${title} summary`}>
          {items.slice(0, 5).map((item) => (
            <li key={item.label} className="rounded-md border border-[#d4ddd0] bg-white px-2 py-1 text-sm leading-5 text-[#26343a]">
              <span className="font-semibold text-[#24594f]">{item.count}</span>{' '}
              <span>{item.label}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm leading-6 text-[#4f615b]">{emptyLabel}</p>
      )}
    </section>
  );
}

function GraphSummaryMetric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-md border border-[#dce3d6] bg-[#fbfcf8] px-3 py-3">
      <div className="text-xs font-semibold uppercase tracking-wide text-[#607068]">{label}</div>
      <div className="mt-1 text-lg font-semibold text-[#172026]">{value}</div>
      <div className="mt-0.5 text-sm leading-5 text-[#4f615b] [overflow-wrap:anywhere]">{detail}</div>
    </div>
  );
}

function summarizeGraphTypes(types: string[]) {
  const counts = new Map<string, number>();
  for (const type of types) {
    const label = formatGraphTypeLabel(type);
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .map(([label, count]) => ({ label, count }));
}

function getTopGraphTypeLabel(types: string[]) {
  if (types.length === 0) return 'No graph data';
  const counts = new Map<string, number>();
  for (const type of types) {
    counts.set(type, (counts.get(type) || 0) + 1);
  }
  const [topType] = [...counts.entries()].sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))[0];
  return formatGraphTypeLabel(topType);
}

function formatGraphTypeLabel(type: string) {
  const withoutTechnicalSuffix = type.replace(/_cid$/i, '');
  return withoutTechnicalSuffix
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatGraphNodeLabel(nodeId: string) {
  if (nodeId.startsWith('bafk')) return 'This section';
  const [prefix, value] = nodeId.split(':');
  if (!value) return nodeId;
  if (prefix === 'portland_code_title') return `Title ${value}`;
  if (prefix === 'portland_code_chapter') return `Chapter ${value}`;
  if (prefix === 'portland_code_section') return `Section ${value.replace(/_/g, '.')}`;
  if (prefix === 'municipal_actor') return formatGraphValueLabel(value);
  if (prefix === 'municipal_subject') return formatGraphValueLabel(value);
  if (prefix === 'ordinance') return `Ordinance ${value}`;
  if (prefix === 'jurisdiction') return value;
  return formatGraphValueLabel(value);
}

function formatGraphValueLabel(value: string) {
  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function SectionReader({
  section,
  onOpenChat,
  onOpenGraph,
  onOpenProof,
}: {
  section: CorpusSection;
  onOpenChat: () => void;
  onOpenGraph: () => void;
  onOpenProof: () => void;
}) {
  const paragraphs = section.text.split(/\n{2,}/).map(cleanSectionParagraph).filter(Boolean);
  const blocks = paragraphs.flatMap(splitLegalClauses);
  const subsectionCount = blocks.filter((block) => block.label).length;
  const codeNoteCount = blocks.filter((block) => !block.label).length;
  const plainSummary = summarizeSectionForAtAGlance(blocks, section);
  const chapterNumber = getChapterNumber(section);

  return (
    <article aria-labelledby="selected-section-heading">
      <div className="border-b border-[#e1e6dc] px-4 py-4 sm:px-5">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <p className="text-sm font-semibold text-[#24594f]">
              {section.bluebook_citation || section.official_cite || section.identifier}
            </p>
            <h2 id="selected-section-heading" className="mt-1 text-xl font-semibold tracking-normal text-[#172026] [overflow-wrap:anywhere] sm:text-2xl">{section.title}</h2>
          </div>
          <a
            href={section.source_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex min-h-11 items-center justify-center whitespace-nowrap rounded-md border border-[#8fa08a] px-4 text-sm font-semibold text-[#24594f] hover:bg-[#f3f6ef]"
          >
            Official source<span className="sr-only"> for {section.identifier}</span>
          </a>
        </div>
      </div>
      <div className="max-w-prose px-4 py-4 sm:px-5 sm:py-5">
        <section className="mb-4 rounded-md border border-[#dce3d6] bg-white px-3 py-3 sm:px-4" aria-label="Research actions">
          <div className="text-xs font-semibold uppercase tracking-wide text-[#607068]">Research this section</div>
          <div className="mt-2 grid gap-2 sm:grid-cols-3">
            <button
              type="button"
              onClick={onOpenChat}
              className="min-h-11 rounded-md bg-[#24594f] px-3 py-2 text-sm font-semibold text-white hover:bg-[#1d473f]"
            >
              Ask about it
            </button>
            <button
              type="button"
              onClick={onOpenGraph}
              className="min-h-11 rounded-md border border-[#8fa08a] bg-[#f7faf4] px-3 py-2 text-sm font-semibold text-[#24594f] hover:bg-[#f3f6ef]"
            >
              Related code
            </button>
            <button
              type="button"
              onClick={onOpenProof}
              className="min-h-11 rounded-md border border-[#8fa08a] bg-[#f7faf4] px-3 py-2 text-sm font-semibold text-[#24594f] hover:bg-[#f3f6ef]"
            >
              Proof details
            </button>
          </div>
        </section>
        <div className="mb-4 grid grid-cols-3 gap-2" aria-label="Section overview">
          <SectionOverviewMetric label="Subsections" value={subsectionCount.toLocaleString()} />
          <SectionOverviewMetric label="Code notes" value={codeNoteCount.toLocaleString()} />
          <SectionOverviewMetric label="Source" value="Official code" />
        </div>
        <section
          className="mb-4 rounded-md border border-[#dce3d6] bg-[#f8faf5] px-3 py-3 sm:px-4"
          aria-label="Section at a glance"
        >
          <div className="grid gap-3 lg:grid-cols-[minmax(0,1.4fr)_minmax(180px,0.9fr)]">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-[#607068]">At a glance</div>
              <p className="mt-2 text-sm leading-6 text-[#26343a] [overflow-wrap:anywhere]">{plainSummary}</p>
            </div>
            <dl className="grid grid-cols-2 gap-2 text-sm lg:grid-cols-1" aria-label="Citation details">
              <AtAGlanceFact label="Citation" value={section.bluebook_citation || section.official_cite || section.identifier} />
              <AtAGlanceFact label="Chapter" value={chapterNumber ? `Chapter ${chapterNumber}` : 'Not listed'} />
            </dl>
          </div>
        </section>
        <div className="grid gap-3" aria-label="Section text">
          {blocks.map((block, index) => (
            block.label ? (
              <section
                key={`${block.label}-${index}`}
                aria-label={`Subsection ${block.label}`}
                className="rounded-md border border-[#dce3d6] bg-[#fbfcf8] px-3 py-3 sm:px-4"
              >
                <div className="grid grid-cols-[2rem_minmax(0,1fr)] gap-2">
                  <div className="pt-0.5 text-base font-semibold leading-7 text-[#24594f]" aria-hidden="true">
                    {block.label}.
                  </div>
                  <LegalTextBlock text={block.text} />
                </div>
              </section>
            ) : (
              <aside
                key={`paragraph-${index}`}
                className="rounded-md border border-[#d6c28e] bg-[#fff9e8] px-3 py-3 sm:px-4"
                aria-label="Code note"
              >
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#735b18]">
                  Code note
                </div>
                <p className="text-base leading-7 text-[#26343a] [overflow-wrap:anywhere]">{block.text}</p>
              </aside>
            )
          ))}
        </div>
      </div>
    </article>
  );
}

function LegalTextBlock({ text }: { text: string }) {
  const outline = parseLegalOutline(text, ['number', 'lower-alpha', 'roman']);

  if (!outline) {
    return <p className="text-base leading-7 text-[#26343a] [overflow-wrap:anywhere]">{text}</p>;
  }

  return (
    <div className="text-base leading-7 text-[#26343a] [overflow-wrap:anywhere]">
      {outline.preface && <p>{outline.preface}</p>}
      <LegalOutlineList nodes={outline.nodes} className={outline.preface ? 'mt-3' : ''} />
    </div>
  );
}

function LegalOutlineList({
  nodes,
  className = '',
  depth = 1,
}: {
  nodes: LegalOutlineNode[];
  className?: string;
  depth?: number;
}) {
  return (
    <ol className={`grid gap-2 ${className}`} aria-label="Numbered legal requirements" data-outline-depth={depth}>
      {nodes.map((node) => (
        <li
          key={`${node.marker}-${node.text.slice(0, 24)}`}
          className="grid grid-cols-[2rem_minmax(0,1fr)] gap-2"
          data-outline-marker={node.marker}
        >
          <span className="font-semibold text-[#24594f]" aria-hidden="true">{node.marker}</span>
          <div>
            {node.text && <p>{node.text}</p>}
            {node.children.length > 0 && (
              <LegalOutlineList nodes={node.children} className="mt-2 border-l border-[#d4ddd0] pl-3" depth={depth + 1} />
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}

function AtAGlanceFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md border border-[#d4ddd0] bg-white px-2 py-2">
      <dt className="text-[0.62rem] font-semibold uppercase tracking-wide text-[#607068]">{label}</dt>
      <dd className="mt-1 text-xs font-semibold leading-5 text-[#172026] [overflow-wrap:anywhere]">{value}</dd>
    </div>
  );
}

function SectionOverviewMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md border border-[#dce3d6] bg-white px-2 py-2 sm:px-3 sm:py-3">
      <div className="text-[0.62rem] font-semibold uppercase tracking-wide text-[#607068] sm:text-xs">{label}</div>
      <div className="mt-1 text-xs font-semibold leading-5 text-[#172026] [overflow-wrap:anywhere] sm:text-sm">{value}</div>
    </div>
  );
}

function ProofPanel({ proof }: { proof: LogicProofSummary | null }) {
  if (!proof) {
    return <div className="px-4 py-4 sm:px-5 sm:py-5"><EmptyState title="No proof summary loaded" /></div>;
  }

  const certificateWarning = getSimulatedCertificateWarning(proof);
  const tdfolParse = parseTdfolForDisplay(proof.deontic_temporal_fol);
  const dcecParse = parseCecForDisplay(proof.deontic_cognitive_event_calculus);
  const dcecStructureAvailable = Boolean(dcecParse.analysis);
  const explanation = explainLogicProofSummary(proof);

  return (
    <div className="px-4 py-4 sm:px-5 sm:py-5">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-normal text-[#172026]">Logic Proof Explorer</h2>
          <p className="mt-1 text-sm text-[#607068]">{proof.formalization_scope}</p>
        </div>
        <span className="rounded-md bg-[#eef2ea] px-3 py-1.5 text-xs font-semibold text-[#4d625b]">
          {formatNormTypeForDisplay(proof.norm_type)}
        </span>
      </div>

      <div className="mt-4 rounded-md border border-[#dce3d6] bg-[#f8faf5] px-4 py-4">
        <div className="text-xs font-semibold uppercase tracking-wide text-[#607068]">Plain meaning</div>
        <p className="mt-2 text-sm leading-6 text-[#26343a] [overflow-wrap:anywhere]">{explanation.plainLanguage}</p>
        <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2" aria-label="Proof plain meaning details">
          <LogicFact label="Time scope" value={explanation.temporalScope} />
          <LogicFact label="Verification" value={certificateWarning ? 'Simulated certificate' : explanation.certificateStatus} />
        </dl>
      </div>

      <ProofReadingGuide proof={proof} explanation={explanation} certificateWarning={certificateWarning} />

      <div className="mt-4 grid grid-cols-2 gap-2 text-xs xl:grid-cols-5" aria-label="Logic proof status metrics">
        <ProofMetric label="Effect" value={formatResultNormOperatorForBadge(proof.norm_operator)} />
        <ProofMetric label="FOL" value={formatLogicStatusForDisplay(proof.fol_status)} />
        <ProofMetric label="Deontic" value={formatLogicStatusForDisplay(proof.deontic_status)} />
        <ProofMetric label="TDFOL parse" value={tdfolParse.ok ? 'Valid' : 'Check'} />
        <ProofMetric label="DCEC parse" value={dcecParse.ok ? 'Valid' : dcecStructureAvailable ? 'Structured' : 'Check'} />
      </div>

      {certificateWarning && (
        <div className="mt-4 rounded-md border border-[#d6c28e] bg-[#fff9e8] px-3 py-2 text-sm leading-6 text-[#735b18]">
          {certificateWarning}
        </div>
      )}

      {!tdfolParse.ok && (
        <div className="mt-4 rounded-md border border-[#d89b82] bg-[#fff4ef] px-3 py-2 text-sm leading-6 text-[#8a3b22]">
          {tdfolParse.error}
        </div>
      )}
      {!dcecParse.ok && !dcecStructureAvailable && (
        <div className="mt-4 rounded-md border border-[#d89b82] bg-[#fff4ef] px-3 py-2 text-sm leading-6 text-[#8a3b22]">
          {dcecParse.error}
        </div>
      )}

      {dcecParse.analysis && (
        <div
          className="mt-4 rounded-md border border-[#dce3d6] bg-white px-4 py-4"
          aria-label="DCEC structure summary"
        >
          <div className="text-xs font-semibold uppercase tracking-wide text-[#607068]">DCEC structure</div>
          <dl className="mt-3 grid gap-3 text-sm min-[520px]:grid-cols-2">
            <LogicFact label="Predicates" value={dcecParse.analysis.predicates.join(', ') || 'None'} />
            <LogicFact label="Section refs" value={formatSectionRefsForDisplay(dcecParse.analysis.sectionRefs)} />
            <LogicFact label="Deontic" value={formatDeonticOperatorsForDisplay(dcecParse.analysis.deonticOperators)} />
            <LogicFact label="Temporal" value={dcecParse.analysis.temporalOperators.join(', ') || 'None'} />
          </dl>
        </div>
      )}

      <FormulaBlock label="TDFOL" value={tdfolParse.formatted || proof.deontic_temporal_fol} />
      <FormulaBlock label="DCEC" value={dcecParse.formatted || proof.deontic_cognitive_event_calculus} />
      <FormulaBlock label="Frame Logic" value={proof.frame_logic_ergo} />
      <FormulaBlock label="Certificate" value={`${proof.zkp_backend}: ${proof.zkp_security_note}`} />
    </div>
  );
}

function ProofReadingGuide({
  proof,
  explanation,
  certificateWarning,
}: {
  proof: LogicProofSummary;
  explanation: ReturnType<typeof explainLogicProofSummary>;
  certificateWarning: string | null;
}) {
  const normLabel = formatNormTypeForDisplay(proof.norm_type).toLowerCase();
  const operatorLabel = formatNormOperatorForDisplay(proof.norm_operator);
  const verificationLabel = certificateWarning ? 'Simulated certificate' : 'Certificate metadata';

  return (
    <section className="mt-4 rounded-md border border-[#dce3d6] bg-[#fbfcf8] px-4 py-4" aria-label="Proof reading guide">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-[#607068]">How to read this proof</h3>
      <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-3">
        <LogicFact label="Code effect" value={`${operatorLabel} ${normLabel}`} />
        <LogicFact label="Time scope" value={explanation.temporalScope} />
        <LogicFact label="Verification" value={verificationLabel} />
      </dl>
    </section>
  );
}

function EmptyState({ title }: { title: string }) {
  return (
    <div className="rounded-md border border-dashed border-[#aebba9] bg-white/70 px-4 py-8 text-center text-sm text-[#4f615b]" role="status">
      {title}
    </div>
  );
}

function ProofMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-[#f4f7f0] px-2 py-2">
      <div className="uppercase tracking-wide text-[#6d7b74]">{label}</div>
      <div className="mt-1 font-semibold text-[#26343a] [overflow-wrap:anywhere]">{value}</div>
    </div>
  );
}

function LogicFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs font-semibold uppercase tracking-wide text-[#6d7b74]">{label}</dt>
      <dd className="mt-1 text-sm leading-6 text-[#26343a] [overflow-wrap:anywhere]">{value}</dd>
    </div>
  );
}

function FormulaBlock({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <details className="mt-4 rounded-md border border-[#dce3d6] bg-[#fbfcf8]">
      <summary className="min-h-11 cursor-pointer px-3 py-3 text-xs font-semibold uppercase tracking-wide text-[#4f615b]">
        {label}
      </summary>
      <pre className="max-h-56 overflow-auto whitespace-pre-wrap border-t border-[#dce3d6] px-3 py-3 text-xs leading-5 text-[#26343a] [overflow-wrap:anywhere]">
        {value}
      </pre>
    </details>
  );
}

function cleanSectionParagraph(paragraph: string) {
  return paragraph
    .trim()
    .replace(/^Label:\s*City code section\s*/i, '')
    .replace(/^Label:\s*/i, '')
    .replace(/\s+([A-Z])\s+\./g, ' $1.');
}

function summarizeSectionForAtAGlance(blocks: Array<{ label?: string; text: string }>, section: CorpusSection) {
  const firstLegalBlock = blocks.find((block) => block.label) || blocks[0];
  const sourceText = firstLegalBlock?.text || section.text || section.title;
  const structured = splitNumberedSubparts(sourceText);
  const candidate = structured?.preface || sourceText;
  const cleaned = candidate
    .replace(/\s+/g, ' ')
    .replace(/\b\d+\.\s+/g, '')
    .trim();
  if (cleaned.length <= 180) {
    return cleaned;
  }
  return `${cleaned.slice(0, 177).replace(/\s+\S*$/, '')}...`;
}

type LegalMarkerKind = 'upper' | 'number' | 'lower-alpha' | 'roman';

interface LegalOutlineNode {
  marker: string;
  text: string;
  children: LegalOutlineNode[];
}

interface LegalOutline {
  preface: string;
  nodes: LegalOutlineNode[];
}

interface LegalMarkerMatch {
  marker: string;
  index: number;
  contentStart: number;
}

function splitLegalClauses(paragraph: string): Array<{ label?: string; text: string }> {
  const matches = findOrderedMarkers(paragraph, 'upper');
  if (matches.length < 2) {
    return [{ text: paragraph }];
  }

  const blocks: Array<{ label?: string; text: string }> = [];
  const firstMatchIndex = matches[0].index;
  const preface = paragraph.slice(0, firstMatchIndex).trim();
  if (preface) {
    blocks.push({ text: preface });
  }

  matches.forEach((match, index) => {
    const start = match.contentStart;
    const nextStart = matches[index + 1]?.index ?? paragraph.length;
    const text = paragraph.slice(start, nextStart).trim();
    if (text) {
      blocks.push({ label: match.marker.replace(/\.$/, ''), text });
    }
  });

  return blocks;
}

function parseLegalOutline(text: string, markerKinds: LegalMarkerKind[]): LegalOutline | null {
  const [kind, ...childKinds] = markerKinds;
  if (!kind) return null;
  const matches = findOrderedMarkers(text, kind);
  if (matches.length < 2) {
    return parseLegalOutline(text, childKinds);
  }

  const preface = text.slice(0, matches[0].index).trim().replace(/[:;]\s*$/, ':');
  const nodes = matches.map((match, index) => {
    const nextStart = matches[index + 1]?.index ?? text.length;
    const rawContent = text
      .slice(match.contentStart, nextStart)
      .trim()
      .replace(/^and\s+/i, '')
      .replace(/;\s*$/g, '')
      .trim();
    const childOutline = parseLegalOutline(rawContent, childKinds);
    return {
      marker: match.marker,
      text: childOutline ? childOutline.preface : rawContent,
      children: childOutline?.nodes || [],
    };
  });

  return { preface, nodes };
}

function findOrderedMarkers(text: string, kind: LegalMarkerKind): LegalMarkerMatch[] {
  const candidates = findMarkerCandidates(text, kind);
  if (candidates.length < 2) {
    return [];
  }

  let best: LegalMarkerMatch[] = [];
  for (let start = 0; start < candidates.length; start += 1) {
    const sequence: LegalMarkerMatch[] = [];
    let expected = markerOrdinal(candidates[start].marker, kind);
    if (expected === null) continue;

    for (let index = start; index < candidates.length; index += 1) {
      const candidate = candidates[index];
      const ordinal = markerOrdinal(candidate.marker, kind);
      if (ordinal === expected) {
        sequence.push(candidate);
        expected += 1;
      } else if (sequence.length > 0 && ordinal !== null && ordinal < expected) {
        break;
      }
    }

    if (sequence.length > best.length) {
      best = sequence;
    }
  }

  return best.length >= 2 ? best : [];
}

function findMarkerCandidates(text: string, kind: LegalMarkerKind): LegalMarkerMatch[] {
  const pattern =
    kind === 'upper'
      ? /(?:^|\s)([A-Z])\.\s+(?=\S)/g
      : kind === 'number'
        ? /(?:^|\s)(\d+)\.\s+(?=\S)/g
        : kind === 'lower-alpha'
          ? /(?:^|\s)(?:\(([a-z])\)|([a-z])\.)\s+(?=\S)/g
          : /(?:^|\s)\((i{1,3}|iv|v|vi{0,3}|ix|x)\)\s+(?=\S)/g;

  return [...text.matchAll(pattern)].map((match) => {
    const rawMarker = match[1] || match[2] || '';
    const markerStartInMatch = match[0].indexOf(match[1] ? rawMarker : `(${rawMarker})`);
    const index = (match.index ?? 0) + markerStartInMatch;
    const display = match[0].includes(`(${rawMarker})`) ? `(${rawMarker})` : `${rawMarker}.`;
    const contentStart = index + display.length + (text.slice(index + display.length).match(/^\s+/)?.[0].length || 0);
    return { marker: display, index, contentStart };
  });
}

function markerOrdinal(marker: string, kind: LegalMarkerKind): number | null {
  const normalized = marker.replace(/[().]/g, '');
  if (kind === 'upper') return normalized.charCodeAt(0) - 64;
  if (kind === 'number') return Number.parseInt(normalized, 10);
  if (kind === 'lower-alpha') return /^[a-z]$/.test(normalized) ? normalized.charCodeAt(0) - 96 : null;
  return romanOrdinal(normalized);
}

function romanOrdinal(value: string): number | null {
  const numerals: Record<string, number> = {
    i: 1,
    ii: 2,
    iii: 3,
    iv: 4,
    v: 5,
    vi: 6,
    vii: 7,
    viii: 8,
    ix: 9,
    x: 10,
  };
  return numerals[value] || null;
}

function splitNumberedSubparts(text: string): { preface: string; items: string[] } | null {
  const matches = [...text.matchAll(/(?<prefix>^|[:;]\s+(?:and\s+)?|\.\s+(?:and\s+)?)(?<number>\d+)\.\s+(?=[A-Z(])/g)]
    .map((match) => {
      const number = match.groups?.number || '';
      const numberIndex = (match.index ?? 0) + match[0].lastIndexOf(`${number}.`);
      const contentStart = numberIndex + `${number}.`.length;
      return {
        numberIndex,
        contentStart: contentStart + (text.slice(contentStart).match(/^\s+/)?.[0].length || 0),
      };
    });

  if (matches.length < 2) {
    return null;
  }

  const preface = text.slice(0, matches[0].numberIndex).trim().replace(/[:;]\s*$/, ':');
  const items = matches
    .map((match, index) => {
      const nextStart = matches[index + 1]?.numberIndex ?? text.length;
      return text
        .slice(match.contentStart, nextStart)
        .trim()
        .replace(/^and\s+/i, '')
        .replace(/;\s*$/g, '')
        .trim();
    })
    .filter(Boolean);

  return items.length >= 2 ? { preface, items } : null;
}

function cleanCorpusSnippet(snippet: string) {
  return snippet
    .trim()
    .replace(/^(\.\.\.)?\s*Label:\s*City code section\s*/i, '$1')
    .replace(/^(\.\.\.)?\s*Label:\s*/i, '$1');
}

function parseTdfolForDisplay(source: string): { ok: boolean; formatted?: string; error?: string } {
  if (!source) {
    return { ok: false, error: 'No TDFOL formula available.' };
  }
  try {
    return { ok: true, formatted: formatTdfolFormula(parseTdfolFormula(source)) };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : 'Unable to parse TDFOL formula.',
    };
  }
}

function parseCecForDisplay(source: string): {
  ok: boolean;
  formatted?: string;
  analysis?: CecAnalysis;
  error?: string;
} {
  if (!source) {
    return { ok: false, error: 'No DCEC formula available.' };
  }
  try {
    const expression = parseCecExpression(source);
    return {
      ok: true,
      formatted: formatCecExpression(expression),
      analysis: analyzeCecExpression(expression),
    };
  } catch (error) {
    const analysis = analyzeCecSource(source);
    return {
      ok: false,
      analysis,
      error: error instanceof Error ? error.message : 'Unable to parse DCEC formula.',
    };
  }
}

function analyzeCecSource(source: string): CecAnalysis {
  const predicates = new Set<string>();
  const atoms = new Set<string>();
  const sectionRefs = new Set<string>();
  const deonticOperators: CecAnalysis['deonticOperators'] = [];
  const temporalOperators: CecAnalysis['temporalOperators'] = [];
  const quantifiers: CecAnalysis['quantifiers'] = [];
  const tokenMatches = [...source.matchAll(/[A-Za-z_][A-Za-z0-9_]*/g)];

  for (const match of tokenMatches) {
    const token = match[0];
    const nextCharIndex = (match.index || 0) + token.length;
    if (/^portland_city_code_/i.test(token)) {
      sectionRefs.add(token);
    }
    if (token === 'O' || token === 'P' || token === 'F') {
      deonticOperators.push(token);
    }
    if (token === 'always' || token === 'eventually' || token === 'next') {
      temporalOperators.push(token);
    }
    if (token === 'forall' || token === 'exists') {
      quantifiers.push(token);
    }
    atoms.add(token);
    if (source.slice(nextCharIndex).trimStart().startsWith('(')) {
      predicates.add(token);
    }
  }

  return {
    predicates: [...predicates].sort(),
    atoms: [...atoms].sort(),
    sectionRefs: [...sectionRefs].sort(),
    quantifiers,
    deonticOperators,
    temporalOperators,
    maxDepth: Math.max(1, Math.min(99, (source.match(/\(/g) || []).length)),
    nodeCount: tokenMatches.length,
  };
}

function buildDirectory(sections: CorpusSection[]): DirectoryTitle[] {
  const byTitle = new Map<string, CorpusSection[]>();
  for (const section of sections) {
    const titleNumber = section.title_number || getTitleNumber(section) || 'Other';
    byTitle.set(titleNumber, [...(byTitle.get(titleNumber) || []), section]);
  }

  return [...byTitle.entries()]
    .sort(([left], [right]) => Number(left) - Number(right))
    .map(([number, titleSections]) => {
      const byChapter = new Map<string, CorpusSection[]>();
      for (const section of titleSections) {
        const chapter = getChapterNumber(section) || number;
        byChapter.set(chapter, [...(byChapter.get(chapter) || []), section]);
      }
      const chapters = [...byChapter.entries()]
        .sort(([left], [right]) => compareCodeNumbers(left, right))
        .map(([chapterNumber, chapterSections]) => ({
          number: chapterNumber,
          sections: chapterSections.sort(compareSections),
        }));
      return {
        number,
        label: TITLE_LABELS[number] || `Title ${number}`,
        sections: titleSections.sort(compareSections),
        chapters,
      };
    });
}

function filterDirectorySections(sections: CorpusSection[], titleFilter: string, chapterFilter: string) {
  return sections
    .filter((section) => !titleFilter || (section.title_number || getTitleNumber(section)) === titleFilter)
    .filter((section) => !chapterFilter || getChapterNumber(section) === chapterFilter)
    .sort(compareSections);
}

function sectionToResult(section: CorpusSection): SearchResult {
  return {
    ipfs_cid: section.ipfs_cid,
    section,
    score: 0,
    scoreParts: { keyword: 0, vector: 0, title: 0, citation: 0 },
    snippet: section.text.replace(/\s+/g, ' ').slice(0, 320),
    citation: section.bluebook_citation || section.official_cite || section.identifier,
  };
}

function getTitleNumber(section: CorpusSection) {
  return getCodeParts(section).title;
}

function getChapterNumber(section: CorpusSection) {
  return getCodeParts(section).chapter;
}

function getCodeParts(section: CorpusSection) {
  const source = section.identifier || section.title || '';
  const match = source.match(/Portland City Code\s+(\d+)(?:[A-Z])?\.(\d+[A-Z]?)/i)
    || source.match(/^(\d+)(?:[A-Z])?\.(\d+[A-Z]?)/);
  if (!match) {
    return { title: section.title_number || '', chapter: '' };
  }
  return { title: match[1], chapter: `${match[1]}.${match[2]}` };
}

function compareSections(left: CorpusSection, right: CorpusSection) {
  return compareCodeNumbers(left.identifier || left.title, right.identifier || right.title);
}

function compareCodeNumbers(left: string, right: string) {
  const leftParts = (left.match(/\d+[A-Z]?/gi) || []).map(normalizeCodePart);
  const rightParts = (right.match(/\d+[A-Z]?/gi) || []).map(normalizeCodePart);
  const length = Math.max(leftParts.length, rightParts.length);
  for (let index = 0; index < length; index += 1) {
    const leftValue = leftParts[index] || '';
    const rightValue = rightParts[index] || '';
    if (leftValue !== rightValue) {
      return leftValue.localeCompare(rightValue, undefined, { numeric: true });
    }
  }
  return left.localeCompare(right);
}

function normalizeCodePart(value: string) {
  return value.toUpperCase();
}
