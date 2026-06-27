# WetWijzer Architecture

WetWijzer is a static Vite/React site for Netherlands legal information search. It preserves the useful generic browser functionality from the fork while replacing the old jurisdiction-specific corpus with Dutch law metadata and Hugging Face backed dataset access.

## Application Flow

1. `src/main.tsx` mounts `src/AppStatic.tsx`.
2. `src/AppStatic.tsx` renders `src/components/WetWijzerLegalResearchApp.tsx`.
3. `loadWetWijzerCorpus()` uses provider interfaces from `src/lib/netherlandsCorpus.ts`.
4. The default provider queries Hugging Face Dataset Viewer APIs for the CID-indexed corpus, BM25 rows, vector rows, and JSON-LD graph rows.
5. The static provider reads the small deterministic sample cache from `public/corpus/netherlands/current/` when forced by configuration or when remote access fails.
6. The search panel layers BM25-style keyword search, vector reranking metadata, and graph expansion where available.
7. The chat panel builds cited answers from retrieved evidence.
8. The graph panel displays related JSON-LD-derived entities and relationships.
9. Article rows carry inherited law status fields such as `law_status`, `is_current`, `valid_from`, `valid_to`, `status_source`, and `status_confidence`.

## Data Stack

The production dataset stack is published on Hugging Face:

- `justicedao/ipfs_netherlands_laws`
- `justicedao/ipfs_netherlands_laws_vector_index`
- `justicedao/ipfs_netherlands_laws_bm25_index`
- `justicedao/ipfs_netherlands_laws_knowledge_graph`

The browser requests paginated Dataset Viewer rows and search results. It does not download the full corpus. The browser bundle includes a small deterministic sample cache so the static app can build, test, and fall back cleanly when Hugging Face access is unavailable. The manifest records the Hugging Face dataset IDs and the current project metadata.

## Source Semantics

WetWijzer uses official Dutch government source references:

- `wetten.overheid.nl`
- official BWB/SRU metadata
- official `/informatie` pages when available

Status labels are metadata parsed from official sources. A status of `unknown` means the site could not determine a normalized status from the available metadata; it should not be treated as a guess.

## Build

The site is built with Vite:

```bash
npm install
npm run prepare:netherlands-corpus
npm run build
npm test
```

No Hugging Face tokens or other private credentials are required for the static build.

Deployment details for GitHub Pages are documented in `docs/GITHUB_PAGES_DEPLOYMENT.md`.
