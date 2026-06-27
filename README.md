# WetWijzer

WetWijzer is a Netherlands-focused legal information and search site. It is a thin React frontend over the published Dutch legal corpus, BM25 index, vector index, and JSON-LD knowledge graph, with cited evidence, CID lookup, graph context, and law status metadata.

WetWijzer is not legal advice. Laws and articles may be labeled `current`, `historical`, `repealed`, `superseded`, or `unknown` based on parsed official metadata. Always verify the official text, version, and legal effect on [wetten.overheid.nl](https://wetten.overheid.nl/).

## Data Sources

The site is configured around official Dutch government sources and the published JusticeDAO Netherlands dataset stack:

| Purpose | Dataset |
| --- | --- |
| Normalized laws and articles | [`justicedao/ipfs_netherlands_laws`](https://huggingface.co/datasets/justicedao/ipfs_netherlands_laws) |
| Vector index | [`justicedao/ipfs_netherlands_laws_vector_index`](https://huggingface.co/datasets/justicedao/ipfs_netherlands_laws_vector_index) |
| BM25 index | [`justicedao/ipfs_netherlands_laws_bm25_index`](https://huggingface.co/datasets/justicedao/ipfs_netherlands_laws_bm25_index) |
| JSON-LD knowledge graph | [`justicedao/ipfs_netherlands_laws_knowledge_graph`](https://huggingface.co/datasets/justicedao/ipfs_netherlands_laws_knowledge_graph) |

Official source references include:

- [wetten.overheid.nl](https://wetten.overheid.nl/)
- Official BWB/SRU metadata where available
- Official `/informatie` pages for law status and version metadata

The currently referenced published corpus is a quality-audited partial Dutch corpus, not a claimed full Dutch corpus. Project metadata records the audited package size as 4,999 laws, 89,737 articles, and 94,736 CID rows. The browser queries the published Hugging Face datasets through a provider abstraction and keeps a small deterministic sample cache only for local development, tests, and offline fallback.

## Features

- Browse Dutch laws and article groups.
- Search by law, article, citation, CID, status, or topic.
- Layer BM25 retrieval, vector reranking, and knowledge graph context through the data provider layer.
- Ask local corpus questions with cited evidence.
- Inspect related knowledge graph nodes and edges.
- Display law status/version fields inherited by article records.
- Display deterministic CIDs, law CIDs, and `ipfs://` identifiers without requiring an IPFS daemon.
- Link back to the official text on `wetten.overheid.nl`.

## Development

Install dependencies:

```bash
npm install
```

Generate or validate the browser-ready Netherlands sample cache:

```bash
npm run prepare:netherlands-corpus
npm run validate:netherlands-corpus
```

Run the app locally:

```bash
npm run dev
```

Build and test:

```bash
npm run build
npm test
```

Deployment notes for GitHub Pages live in [docs/GITHUB_PAGES_DEPLOYMENT.md](docs/GITHUB_PAGES_DEPLOYMENT.md).

## Runtime Data Layout

WetWijzer uses provider interfaces in `src/lib/netherlandsCorpus.ts` for corpus loading, search, graph traversal, and CID lookup. The default provider queries Hugging Face Dataset Viewer APIs for the published Netherlands dataset stack. The bundled static files are intentionally small sample/fallback artifacts, not the production source of truth.

Static sample artifacts live under:

```text
public/corpus/netherlands/current/
```

The manifest at `public/corpus/netherlands/current/artifacts.manifest.json` records the Hugging Face dataset stack and the browser sample artifact list. Playwright tests force the static sample with `WETWIJZER_DATA_PROVIDER=static` in `localStorage`; normal browser sessions use the Hugging Face provider with sample fallback. Builds can also set `VITE_WETWIJZER_DATA_PROVIDER=static` or `VITE_WETWIJZER_DATA_PROVIDER=huggingface`. Do not hardcode Hugging Face tokens or private credentials into this repository.

## Legal Notice

WetWijzer provides legal information and retrieval tooling only. It does not determine legal validity, does not replace official publication, and does not provide legal advice. Users should verify official Dutch law text and metadata on `wetten.overheid.nl` and consult a qualified legal professional for advice.
