# AGENTS.md

Project-specific guidance for future agent sessions working on this repository.

## Project overview

- This is a tiny static personal blog for Talip Göksu.
- Content is written in Markdown under `src/` and compiled to plain static HTML in `dist/`.
- There is intentionally no frontend framework, CMS, admin UI, database, or required client-side JavaScript.
- Keep the site simple, fast, readable, and easy to reason about.

## Important privacy/persona rule

- Do not publish private background notes, CV excerpts, email addresses, family details, nutrition/faith details, or other personal context unless the user explicitly asks for that exact information to appear publicly.
- Use private persona context only to shape tone and direction.
- Public copy should remain professional, understated, and intentional.

## Commands

- Install dependencies: `npm install`
- Build site: `npm run build`
- Watch during development: `npm run dev`
- Clean generated output: `npm run clean`

Run `npm run build` after changing source content, templates, styles, or config.

## Publishing

- GitHub Pages deployment is configured in `.github/workflows/pages.yml`.
- Pushes to `main` build the site and deploy the generated `dist/` artifact.
- The repository is published with the GitHub Pages custom domain `goeksu.me`.
- Keep `src/config.json` `siteUrl` and `basePath` in sync. With the custom domain, `basePath` should remain empty. Use `/me` only if the site is moved back to `https://telip007.github.io/me`.

## Repository structure

- `src/config.json` — site metadata, author, canonical site URL, RSS/sitemap values.
- `src/about.md` — public About page content.
- `src/datenschutz.md` — privacy notice (Datenschutzerklärung), rendered to `/datenschutz/` and linked in the footer. Keep it in sync with the actual setup (GitHub Pages hosting, no tracking, no cookies).
- `src/posts/*.md` — blog posts. There may be no posts yet; that is valid.
- `src/styles.css` — global styling for generated pages.
- `scripts/build.js` — the static site generator. It reads `src/`, clears `dist/`, then writes generated HTML, RSS, sitemap, robots, and CSS.
- `scripts/clean.js` — removes generated output.
- `src/favicon.svg` — source favicon copied into generated output.
- `.github/workflows/pages.yml` — GitHub Pages build/deploy workflow.
- `dist/` — generated static output. Do not manually edit files here; change `src/` or `scripts/build.js` and rebuild.

## Content conventions

- Posts use front matter with fields like `title`, `date`, `tags`, `excerpt`, `featured`, and `slug`.
- No archive page is currently desired. Do not reintroduce `/archive/` or Archive navigation unless requested.
- Stub/example posts were removed. Do not add placeholder content as if it were real writing.
- If there are no posts, the homepage should gracefully show `No posts yet.`

## Implementation conventions

- Prefer straightforward Node.js and plain HTML generation over adding dependencies.
- Keep generated markup semantic and accessible.
- Escape public text before injecting it into templates.
- Keep RSS, sitemap, metadata, and navigation consistent when changing routes.
- Avoid exposing implementation-only details on public pages unless they are part of the intended editorial voice.

## Git and generated files

- `node_modules/`, `.DS_Store`, logs, and local env files should not be committed.
- `dist/` is generated output. It is currently ignored; rebuild locally when needed.
- Do not commit secrets or private notes.

## Bilingual editorial workflow

- Preserve German URLs. English lives under `/en/`, with `/en/articles/`, `/en/tags/`, `/en/about/` and `/en/rss.xml`.
- Posts use `lang: de|en`, a shared `translationKey`, a locale-specific `slug` and explicit `date`. Missing `lang` remains German.
- Keep unpublished material in `drafts/` or mark it with the boolean `draft: true`. Drafts must not leak into feeds, sitemap, navigation or alternate-language metadata. Future dates are not a publishing gate.
- Never include an unrelated untracked user post in a publication commit. Inspect git status and stage only the files explicitly part of the task.
- About pages are `src/about.md` and `src/about.en.md`. Preserve current public professional links unless asked to remove them. Keep the existing `/datenschutz/` text intact; English links explicitly say it is German.
- AI assistance is disclosed. Do not claim Talip personally wrote or reviewed each article when work is autonomous. Talip retains responsibility for direction and operation.
- Ground article claims in linked sources. Original setup/experiment claims require actual evidence. No invented experience, measurements, quotes or citations. New sources and user-supplied topics still require editorial checks.
- Front matter must remain non-executable YAML or JSON. Do not enable JavaScript parsing or raw Markdown HTML.
- Run `node --test scripts/build.test.js` and `npm run build` after generator or content-model changes. Tests use temporary fixtures; do not create example articles in the live source directory.
