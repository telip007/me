# Personal blog

Talip Göksu's bilingual Markdown blog, rewritten in **FastAPI, Jinja and HTMX**. Python validates the public content graph and renders both HTTP pages and the optional static export. There is no database, CMS, account system, tracking or required browser JavaScript.

## Run locally

Install Python 3.12+ and [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
uv sync --locked
uv run --locked uvicorn blog.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. `npm run dev` is a convenience command with automatic reload for Python, Markdown, configuration, templates and browser assets. Production loads and validates content once at startup; restart the process after changing content. Invalid published metadata fails startup rather than serving a partial publication.

```sh
uv run --locked pytest
uv run --locked ruff check blog tests scripts/export.py scripts/check_content.py
uv run --locked python scripts/check_content.py
uv run --locked python scripts/export.py
```

The existing Node command interface is preserved: `npm test` runs the Python suite and the original export contract tests; `npm run build` exports to `dist/`; `npm run clean` removes it. Node has no runtime dependencies and is optional for running FastAPI.

## Architecture

- `blog/content.py`: data-only front matter, Markdown rendering, heading anchors/contents, validated route and translation registry.
- `blog/main.py`: application factory, localized pages, GET search/topic filtering, RSS/sitemap/robots, health endpoint and response policies.
- `blog/export.py`: static export through the same application rendering path.
- `blog/templates/`: semantic Jinja shell, index/results, article, topic, page and 404 templates.
- `blog/static/`: responsive CSS, local HTMX, minimal interaction helpers and licensed self-hosted fonts. See [asset provenance](blog/static/ASSETS.md).
- `src/`: original Markdown, site configuration and favicon. No template code in content.
- `tests/`: isolated temporary fixture sites, never example posts in publication sources.
- `scripts/build.js`: compatibility wrapper, **not a second generator**.

Search enhances an ordinary GET form. HTMX replaces only the result list, preserves the focused input, updates an accessible count and uses a URL that also works without JavaScript. The backend varies responses on HTMX headers and returns full HTML for history restoration. No boosted navigation or browser history snapshots. Search failures leave the previous results visible with a recovery message. Article navigation, source links, language changes and RSS remain native links.

## Content and language URLs

Published articles live in `src/posts/*.md`; translations are separate files:

```yaml
---
title: "A concrete article title"
date: "2026-10-29"
lang: en
translationKey: stable-topic-key
slug: english-article-slug
tags: [LLM]
excerpt: "The specific question this article answers."
draft: true
---
```

This is a documentation example, not a published article.

- `lang` is `de` or `en`; omitted means German. Shared `translationKey`, separate titles/excerpts/slugs. At most one published counterpart per language and key.
- Set an explicit date on new articles. Future dates do not schedule publication: use boolean `draft: true` until ready.
- `draft: true` excludes a file from pages, search, tags, translation links, feeds and sitemap. `drafts/` is never read. Quoted/nonboolean draft flags are rejected.
- YAML/JSON are data only. Executable front matter is rejected and raw Markdown HTML is escaped. Duplicate routes and ambiguous metadata fail before export replaces the previous output.
- The language switch opens a published counterpart, or the other language's homepage. Only actual counterparts receive alternate-language metadata. Tag translations pair only when labels match exactly.
- `updated` records a substantive correction, not a cosmetic change. Use `featured` only as editorial data; the design does not manufacture a featured article.

| German | English |
| --- | --- |
| `/` | `/en/` |
| `/texte/<slug>/` | `/en/articles/<slug>/` |
| `/themen/<tag>/` | `/en/tags/<tag>/` |
| `/ueber-mich/` | `/en/about/` |
| `/rss.xml` | `/en/rss.xml` |

`/about/` redirects to the German About page. One sitemap contains both languages. There is no archive. An empty index is valid; no unfinished article is published to fill a design.

## Writing and design research

Read the [editorial guide](docs/editorial-guide.md) before drafting or publishing. It includes reader briefs, explanation/investigation/tutorial outlines, a claim ledger, editing passes, feedback prompts, translation parity and publication checks. It applies the requested Pragmatic Engineer article alongside Google, Microsoft, Julia Evans, Diátaxis and MDN; it does not impose boilerplate article sections.

The selected visual direction A uses a wine opening, an offset paper reading plane, citron edges and Bricolage typography. The initial blue/white direction was rejected; the [working studies](docs/design-exploration/README.md) and [broader identity research](docs/research/expressive-design.md) preserve that decision.

The source-linked [editorial research](docs/research/editorial.md) and [design research](docs/research/design.md) record findings checked on 29 October 2026, including original engineering blogs and platform standards. [DESIGN.md](DESIGN.md) records implementation decisions. Primary sources support factual claims; original experiments require actual artifacts. Do not invent experience, measurements, quotes, human review or citations. Keep private notes outside public copy. Do not add blanket AI notices to articles or shared templates. Existing About copy is preserved.

## Configuration and privacy

`src/config.json` contains site metadata, public author and English overrides in `locales.en`. `siteUrl` is an HTTP(S) origin; `basePath` is empty for `https://goeksu.me`. A repository subpath uses origin `https://telip007.github.io` and `basePath: "/me"`. FastAPI mounts the same prefix for runtime URLs; the exporter writes paths appropriate to the hosting root.

The existing German privacy notice at `/datenschutz/` is preserved. English links label it “Privacy (German)”. No cookies, analytics, third-party font requests or external script CDNs are introduced. The privacy notice currently describes **GitHub Pages**. Before a public FastAPI host cutover, choose the host, review its actual data processing and update that hosting text accordingly. A local runtime does not establish a new public host or alter the current published notice.

## Runtime deployment and static compatibility

FastAPI is the primary runtime. A container definition is included:

```sh
docker build -t personal-blog .
docker run --rm -p 8000:8000 personal-blog
```

Run behind your chosen HTTPS reverse proxy. The image runs as a non-root user; use its health endpoint for readiness. Keep credentials and private drafts out of the image/build context. Do not grant forwarded-header trust to arbitrary public clients. The application does not need a database, outbound browser services or writable persistent storage.

**GitHub Pages cannot run FastAPI.** The existing Pages workflow therefore remains an explicit static compatibility path: it installs the locked Python dependencies, runs tests, and exports the same rendered routes to `dist/`. Static pages omit dynamic search controls and HTMX; topics and native navigation continue working. A push to `main` still publishes that export. Hosting the full HTMX search experience requires deploying the ASGI application to a Python-capable host. This task does not perform that cutover or publish changes.

Do not commit `dist/`, `.venv/`, private source material or credentials. The original untracked user article is deliberately outside this rewrite.

Code is MIT-licensed. Articles and personal content are © Talip Göksu, all rights reserved unless stated otherwise. Vendored fonts and HTMX retain their own included licenses.

Final selected-A verification and screenshots: [verification report](docs/qa/selected-a/verification.md). The earlier blue/white report records a rejected design checkpoint.
