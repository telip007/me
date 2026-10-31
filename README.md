# Personal blog

Talip Göksu's English-only Markdown blog, rewritten in **FastAPI, Jinja and HTMX**. Python validates the public content graph and renders both HTTP pages and the optional static export. There is no database, CMS, account system, tracking or required browser JavaScript.

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

- `blog/content.py`: data-only front matter, Markdown rendering, heading anchors/contents, validated route registry.
- `blog/main.py`: application factory, canonical English pages, GET search/topic filtering, RSS/sitemap/robots, health endpoint and response policies.
- `blog/export.py`: static export through the same application rendering path.
- `blog/templates/`: semantic Jinja shell, index/results, article, topic, page and 404 templates.
- `blog/static/`: responsive CSS, local HTMX, minimal interaction helpers and licensed self-hosted fonts. See [asset provenance](blog/static/ASSETS.md).
- `src/`: original Markdown, site configuration and favicon. No template code in content.
- `tests/`: isolated temporary fixture sites, never example posts in publication sources.
- `scripts/build.js`: compatibility wrapper, **not a second generator**.

Search enhances an ordinary GET form. HTMX replaces only the result list, preserves the focused input, updates an accessible count and uses a URL that also works without JavaScript. The backend varies responses on HTMX headers and returns full HTML for history restoration. No boosted navigation or browser history snapshots. Search failures leave the previous results visible with a recovery message. Article navigation, source links and RSS remain native links.

## Content and canonical URLs

Published articles live in `src/posts/*.md`:

```yaml
---
title: "A concrete article title"
date: "2026-10-31"
lang: en
slug: concrete-article-slug
tags: [AI]
excerpt: "The specific question this article answers."
draft: true
---
```

This is a documentation example, not a published article.

- The public site is English-only. Omitted `lang` means English. Explicit `lang: de` files are retained locally and excluded from all public surfaces; no automatic translation or publication occurs.
- Set an explicit date on new articles. Future dates do not schedule publication: use boolean `draft: true` until ready.
- Drafts are excluded from pages, search, tags, redirects, feeds and sitemap. `drafts/` is never read. Quoted/nonboolean draft flags and duplicate metadata keys are rejected.
- YAML/JSON are data only. Executable front matter is rejected and raw Markdown HTML is escaped. Duplicate routes and ambiguous metadata fail before export replaces previous output.
- `updated` records a substantive correction, not a cosmetic change. Use `featured` only as editorial data; the design does not manufacture a featured article.

| Route | Purpose |
| --- | --- |
| `/` | Publication homepage |
| `/articles/` | Article index |
| `/articles/<slug>/` | Article |
| `/tags/` | Topic index |
| `/tags/<tag>/` | Articles for one topic |
| `/about/` | About this blog |
| `/privacy/` | English privacy notice |
| `/rss.xml` | English RSS feed |

Existing `/en/` routes redirect permanently to their canonical English counterparts when the target exists. `/ueber-mich/` redirects to `/about/`; `/datenschutz/` redirects to `/privacy/`. Redirects do not expose excluded articles. The sitemap lists canonical pages only. There is no language switch and no archive. An empty index is valid; no unfinished article is published to fill a design.

## Writing and design research

Read the [editorial guide](docs/editorial-guide.md) before drafting or publishing. It includes reader briefs, explanation/investigation/tutorial outlines, a claim ledger, editing passes, feedback prompts and publication checks. It applies the requested Pragmatic Engineer article alongside Google, Microsoft, Julia Evans, Diátaxis and MDN; it does not impose boilerplate article sections.

The selected visual direction A uses a wine opening, an offset paper reading plane, citron edges and Bricolage typography. The initial blue/white direction was rejected; the [working studies](docs/design-exploration/README.md) and [broader identity research](docs/research/expressive-design.md) preserve that decision.

The source-linked [editorial research](docs/research/editorial.md) and [design research](docs/research/design.md) record findings checked on 29 October 2026, including original engineering blogs and platform standards. [DESIGN.md](DESIGN.md) records implementation decisions. Primary sources support factual claims; original experiments require actual artifacts. Do not invent experience, measurements, quotes, human review or citations. Keep private notes outside public copy. Do not add blanket AI notices to articles or shared templates. Existing About copy is preserved.

## Configuration and privacy

`src/config.json` contains the English site metadata and public author. `siteUrl` is an HTTP(S) origin; `basePath` is empty for `https://goeksu.me`. A local subpath can still use an explicit base path. FastAPI mounts the same prefix for runtime URLs; the exporter writes paths appropriate to the hosting root.

The English privacy notice is maintained in `src/privacy.md` at `/privacy/` and describes the actual runtime hosting. No application cookies, analytics, third-party font requests or external script CDNs are introduced. Hosting access logs and infrastructure data handling must remain accurately described when deployment configuration changes.

## Runtime deployment and static compatibility

FastAPI is the primary runtime. A container definition is included:

```sh
docker build -t personal-blog .
docker run --rm -p 8000:8000 personal-blog
```

Fly.io is the production runtime target. `fly.toml`, the Docker image and the main-branch deployment workflow define delivery. A push to `main` deploys the FastAPI application, including server-rendered HTMX search. Keep the custom domain and its TLS certificate attached to the intended application. Confirm live responses separately from a local build or a successful deployment command.

The image runs as a non-root user. Its health probe follows the configured base path. The application requires no database, outbound browser services or writable persistent storage. Keep credentials and private drafts out of build context; do not trust arbitrary forwarded headers from public clients.

The optional static export uses the same renderer and omits dynamic search controls and HTMX; topic links and native navigation still work. It is a compatibility artifact, not the production hosting path. GitHub Pages cannot execute FastAPI.

Do not commit `dist/`, `.venv/`, private source material or credentials. The original untracked user article is deliberately outside this rewrite.

Code is MIT-licensed. Articles and personal content are © Talip Göksu, all rights reserved unless stated otherwise. Vendored fonts and HTMX retain their own included licenses.

Final selected-A verification and screenshots: [verification report](docs/qa/selected-a/verification.md). The earlier blue/white report records a rejected design checkpoint.
