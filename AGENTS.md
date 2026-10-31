# AGENTS.md

Project-specific guidance for future agent sessions working on this repository.

## Project overview

- This is a small English-only Markdown personal blog for Talip Göksu, served with FastAPI and progressively enhanced with HTMX.
- Content is written in Markdown under `src/`. Python/Jinja renders runtime HTML and an optional static export in `dist/`.
- There is no frontend SPA, CMS, admin UI, database, tracking, or required client-side JavaScript. HTMX enhances an ordinary GET search form.
- Keep the site simple, fast, readable, and easy to reason about.

## Important privacy/persona rule

- Do not publish private background notes, CV excerpts, email addresses, family details, nutrition/faith details, or other personal context unless the user explicitly asks for that exact information to appear publicly.
- Use private persona context only to shape tone and direction.
- Public copy should remain professional, understated, and intentional.

## Commands

- Install locked dependencies: `uv sync --locked` (Python 3.12+).
- Run application: `uv run --locked uvicorn blog.main:app --host 127.0.0.1 --port 8000`.
- Watch development: `npm run dev`.
- Python tests: `uv run --locked pytest`.
- Full compatibility suite: `npm test`.
- Lint: `uv run --locked ruff check blog tests scripts/export.py scripts/check_content.py`.
- Validate content: `uv run --locked python scripts/check_content.py`.
- Build static export: `npm run build` or `uv run --locked python scripts/export.py`.
- Clean generated output: `npm run clean`.

Run Python tests, `node --test scripts/build.test.js`, and `npm run build` after source, template, route or content-model changes. Use temporary fixtures for article layout checks. Never add example articles to the live source directory.

## Publishing

- Fly.io is the primary FastAPI runtime. The deployment workflow builds and deploys on pushes to `main`; GitHub Pages is no longer the production runtime.
- Preserve the custom domain `goeksu.me`. Keep `src/config.json` `siteUrl` set to its HTTPS origin and `basePath` empty for production.
- Static export remains an optional local compatibility artifact. It omits dynamic search controls and must not be confused with the live FastAPI deployment.
- Verify the actual deployed application, custom-domain certificate and public routes when making a release claim.

## Repository structure

- `src/config.json` — site metadata, author, canonical site URL, RSS/sitemap values.
- `src/about.md` — public About page content.
- `src/privacy.md` — English privacy notice, rendered to `/privacy/` and linked in the footer. Keep it in sync with the actual Fly.io hosting and data handling; no tracking or application cookies.
- `src/posts/*.md` — blog posts. There may be no posts yet; that is valid.
- `blog/static/site.css` — responsive styling shared by runtime and export; local fonts/licenses live in `blog/static/fonts/`.
- `blog/content.py` — safe content parsing, Markdown rendering and route validation.
- `blog/main.py` — FastAPI application factory, Jinja responses, search, feeds and metadata.
- `blog/templates/` — shared HTML templates.
- `blog/export.py` — static export using the same application renderer.
- `scripts/build.js` — Node compatibility wrapper around the Python exporter; do not recreate a second renderer.
- `docs/editorial-guide.md` and `docs/research/` — writing policy and source-backed research.
- `scripts/clean.js` — removes generated output.
- `src/favicon.svg` — source favicon copied into generated output.
- `fly.toml`, `Dockerfile` and the deployment workflow — Fly.io runtime and main-branch delivery configuration.
- `dist/` — generated static output. Do not manually edit files here; change `src/` or `scripts/build.js` and rebuild.

## Content conventions

- Posts use front matter with fields like `title`, `date`, `tags`, `excerpt`, `featured`, and `slug`.
- No archive page is currently desired. Do not reintroduce `/archive/` or Archive navigation unless requested.
- Stub/example posts were removed. Do not add placeholder content as if it were real writing.
- If there are no posts, the homepage should gracefully show `No posts yet.`

## Implementation conventions

- Prefer straightforward Python, Jinja HTML and progressive HTMX over a client-side framework. Keep dependencies deliberate and locked with uv.
- Search must keep an ordinary GET fallback; static export omits controls requiring the server.
- Preserve full-document history responses, HTMX cache variation, local assets, keyboard access and reduced motion.
- Keep generated markup semantic and accessible.
- Escape public text before injecting it into templates.
- Keep RSS, sitemap, metadata, and navigation consistent when changing routes. Validate the content graph before serving or replacing export output.
- Avoid exposing implementation-only details on public pages unless they are part of the intended editorial voice.

## Git and generated files

- `node_modules/`, `.DS_Store`, logs, and local env files should not be committed.
- `dist/` is generated output. It is currently ignored; rebuild locally when needed.
- Do not commit secrets or private notes.

## English-only editorial workflow

- The public site is English-only. Canonical routes are `/`, `/articles/`, `/articles/<slug>/`, `/tags/`, `/tags/<tag>/`, `/about/`, `/privacy/` and `/rss.xml`.
- Posts may use `lang: en`; omitted `lang` defaults to English. Files explicitly marked `lang: de` remain local and are excluded from every public page, search result, tag, feed, sitemap and redirect target. Do not translate or publish them automatically.
- Preserve old `/en/` counterparts as permanent redirects to existing canonical English routes. `/ueber-mich/` redirects to `/about/`, and `/datenschutz/` to `/privacy/`. Never generate public German content or language-switch navigation.
- Keep unpublished material in `drafts/` or mark it with boolean `draft: true`. Drafts must never leak. Future dates are not a publishing gate.
- Never include an unrelated untracked user post in a publication commit. Inspect git status and stage only files explicitly part of the task.
- The public About source is `src/about.md`. Preserve its professional links unless asked to remove them. Privacy is `src/privacy.md`; keep the hosting details accurate.
- Do not add blanket AI-creation notices to individual articles or shared templates, replacement disclaimers, or a central disclosure page. Preserve substantive AI content, sources and factual evidence limits. Do not claim Talip personally wrote or reviewed autonomous articles. Talip retains responsibility for direction and operation.
- Ground article claims in linked sources. Original setup/experiment claims require actual evidence. No invented experience, measurements, quotes or citations. New sources and user-supplied topics still require editorial checks.
- Front matter must remain non-executable YAML or JSON. Reject duplicate metadata keys. Do not enable JavaScript parsing or raw Markdown HTML.
- Run Python tests, `node --test scripts/build.test.js` and `npm run build` after route or content-model changes. Tests use temporary fixtures; never create example articles in live sources.
