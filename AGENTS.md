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

## Repository structure

- `src/config.json` — site metadata, author, canonical site URL, RSS/sitemap values.
- `src/about.md` — public About page content.
- `src/posts/*.md` — blog posts. There may be no posts yet; that is valid.
- `src/styles.css` — global styling for generated pages.
- `scripts/build.js` — the static site generator. It reads `src/`, clears `dist/`, then writes generated HTML, RSS, sitemap, robots, and CSS.
- `scripts/clean.js` — removes generated output.
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
