# Personal blog

A small bilingual static blog about AI, LLMs and agentic engineering. Markdown in `src/` becomes plain HTML in `dist/`. No frontend framework, CMS or required browser JavaScript.

## Build and test

```sh
npm ci
npm run build
node --test scripts/build.test.js
npm run dev
```

The tests build temporary fixture sites. They cover language routes, translation links, draft exclusion, metadata, feeds, privacy links and unsafe front matter. `npm run dev` watches source files. `npm run clean` removes generated output.

## Content

Published articles live in `src/posts/*.md`. Each translation is a separate file:

```yaml
---
title: "A concrete article title"
date: "2026-10-14"
lang: en
translationKey: stable-topic-key
slug: english-article-slug
tags: [LLM]
excerpt: "A short description of the article."
draft: true
---
```

- `lang` is `de` or `en`; omitted means German for compatibility.
- Both versions share `translationKey`, but have their own title, excerpt, tags and slug. There can be only one published article per language and key.
- Slugs and translation keys use lowercase letters, digits and hyphens.
- `draft: true` excludes a file from **all** production pages, feeds, sitemap and translation links. The flag must be a YAML boolean, not a quoted string. `drafts/` and other directories outside `src/posts/` are never built.
- New articles should always set `date`. Undated legacy files use their file modification date; this is a compatibility fallback, not a publication schedule. Future dates do not schedule or hide articles: use `draft: true` until publication.
- YAML and JSON front matter are supported. Executable front-matter languages are rejected before parsing. Raw HTML in article Markdown is disabled.
- A language switch opens the corresponding published translation, or the other language’s homepage. Only real counterparts receive `hreflang` links. Tag pages pair only when the tag label is identical in both languages.

DE URLs remain `/`, `/texte/<slug>/`, `/themen/<tag>/`, `/ueber-mich/`, `/rss.xml`. English uses `/en/`, `/en/articles/<slug>/`, `/en/tags/<tag>/`, `/en/about/`, `/en/rss.xml`. `/about/` still redirects to the German About page. One sitemap lists both languages.

## Editorial practice

The blog uses AI assistance for research, drafting, translation and editorial checks. Talip Göksu is responsible for its direction and operation. Publication must not be described as a personal review by Talip unless that review actually happened.

Use primary sources where possible, link claims to the supporting passage and distinguish source reports from our own observations. Coverage can include new research, useful work by practitioners and our own agent setup, but claims about that setup need actual local evidence. Do not invent experiments, benchmark results or personal experience. Reader-supplied topics can enter the same research and review process. Expand the source list when useful; free access and a famous author do not by themselves establish reliability. Keep corrections visible and avoid confident claims that the evidence does not support.

Drafts are prepared and checked before being promoted into `src/posts/`. Publication is separate from generation; do not publish unrelated local files or a user’s untracked drafts as part of a source change.

## About, privacy and configuration

Edit `src/about.md` and `src/about.en.md` for the two About pages. The existing German privacy notice remains at `/datenschutz/`; English pages explicitly label its link “Privacy (German)”. Its legal wording is not automatically translated or expanded.

`src/config.json` contains shared metadata and English overrides in `locales.en`. `siteUrl` is the origin (`https://goeksu.me`), and `basePath` is empty on the custom domain. For a repository subpath, use an origin such as `https://telip007.github.io` with `basePath: "/me"`; do not include the subpath twice.

## Publishing

Pushes to `main` deploy the generated artifact through `.github/workflows/pages.yml`. Build and test first. Do not edit or commit `dist/`, `node_modules/`, credentials or private notes. The generator rejects duplicate routes and invalid article metadata before replacing output.

Code is MIT-licensed. Articles and personal content are © Talip Göksu, all rights reserved unless stated otherwise.
