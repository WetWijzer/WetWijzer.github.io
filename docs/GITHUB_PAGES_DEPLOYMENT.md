# WetWijzer GitHub Pages Deployment

WetWijzer is deployable as a static Vite site at the root GitHub Pages URL:

```text
https://wetwijzer.github.io/
```

The site is a frontend over the published Netherlands legal corpus. Deploying the site does not rebuild, upload, or mutate the legal corpus.

## Build

Use Node 20 or newer.

```bash
npm ci --legacy-peer-deps
npm run validate:netherlands-corpus
npm run build
```

Preview the production build locally:

```bash
npx vite preview --host 127.0.0.1 --port 5173
```

## GitHub Pages Compatibility

- `vite.config.ts` uses `base: '/'`, which is correct for the root `WetWijzer.github.io` Pages site.
- `public/.nojekyll` is included so GitHub Pages serves hashed Vite assets and static corpus sample files as-is.
- `public/404.html` redirects unknown paths back to `/` for the single-page app.
- Static sample assets are served from `/corpus/netherlands/current/`.
- The deployed app does not need Hugging Face tokens or private secrets.

If WetWijzer is ever deployed under a project path instead of the root Pages domain, update `base`, static asset paths, and the 404 redirect together.

## Provider Modes

Default production mode uses the Hugging Face Dataset Viewer APIs:

```bash
VITE_WETWIJZER_DATA_PROVIDER=huggingface npm run build
```

Static fallback mode uses only the small bundled sample cache:

```bash
VITE_WETWIJZER_DATA_PROVIDER=static npm run build
```

At runtime, browser localStorage can override the build-time mode for debugging:

```js
localStorage.setItem('WETWIJZER_DATA_PROVIDER', 'static');
location.reload();
```

```js
localStorage.setItem('WETWIJZER_DATA_PROVIDER', 'huggingface');
location.reload();
```

Clear the override:

```js
localStorage.removeItem('WETWIJZER_DATA_PROVIDER');
location.reload();
```

## Hugging Face Data Access

WetWijzer reads small pages from these public datasets:

- `justicedao/ipfs_netherlands_laws`
- `justicedao/ipfs_netherlands_laws_vector_index`
- `justicedao/ipfs_netherlands_laws_bm25_index`
- `justicedao/ipfs_netherlands_laws_knowledge_graph`

The browser should request Dataset Viewer endpoints such as:

```text
https://datasets-server.huggingface.co/size?dataset=justicedao/ipfs_netherlands_laws
https://datasets-server.huggingface.co/search?dataset=justicedao/ipfs_netherlands_laws&config=articles&split=train&query=Wetboek
```

The provider requests paginated rows and search results. It should not download the full corpus.

## Debugging HF Or Network Failures

1. Open browser developer tools and check the Network tab for `datasets-server.huggingface.co`.
2. Confirm requests are CORS-enabled and return HTTP 200.
3. Check the console for `WetWijzer remote ... unavailable; using bundled sample ...` warnings.
4. If Hugging Face search indexes are temporarily loading, retry after a minute or force static mode.
5. Verify the header. It should show either `Provider: Hugging Face datasets` or `Provider: local sample fallback`.

Fallback behavior is expected: if the manifest, search, CID lookup, or graph lookup fails remotely, WetWijzer keeps the interface usable with the bundled sample cache.

## GitHub Actions

`.github/workflows/deploy.yml` builds and deploys `dist/` to GitHub Pages on `main`.

The workflow:

- installs dependencies with `npm ci --legacy-peer-deps`
- validates the sample corpus
- builds with `npm run build`
- defaults to the Hugging Face provider
- disables OpenRouter by default so no proxy or secret is required for static deployment

Optional repository variables:

```text
VITE_WETWIJZER_DATA_PROVIDER=huggingface|static
VITE_OPENROUTER_ENABLED=false|true
VITE_OPENROUTER_BASE_URL=https://your-proxy.example/api/openrouter
```

Do not store Hugging Face tokens in the frontend.
