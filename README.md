# Personal Blog (Static, Markdown-only)

This repository builds a tiny static personal blog with:

- Markdown posts in `src/posts/`
- front matter metadata via `--- ... ---`
- one Node build script (`scripts/build.js`)
- zero frontend framework and zero required client-side JS
- static output written to `dist/`

## Setup

```bash
npm install
npm run build
```

## Development

```bash
npm run dev
```

This runs the build script in watch mode and rebuilds on source changes.

## Publishing

Pushing to `main` deploys `dist/` to GitHub Pages through `.github/workflows/pages.yml`.

The current production URL is configured as `https://goeksu.me` with an empty `basePath` in `src/config.json`. If you move away from the custom domain, update both values before deploying.

## Clean output

```bash
npm run clean
```

## Content model

Create markdown posts in `src/posts/` with front matter:

```md
---
title: "Post title"
date: "2026-05-01"
tags: ["tag1", "tag2"]
excerpt: "Short intro for listing pages"
featured: true
slug: post-slug
---

Write your markdown content here.
```

### About page

Edit `src/about.md` in Markdown to change the about page.

## Configuration

Edit `src/config.json`:

- `siteTitle`
- `siteSubtitle`
- `siteDescription`
- `siteUrl` (used for canonical/feeds/sitemap)
- `author`
- `twitterHandle`

## Output

Build produces:

- `dist/index.html`
- `dist/texte/<slug>/index.html`
- `dist/ueber-mich/index.html`
- `dist/themen/<tag>/index.html`
- `dist/rss.xml`
- `dist/sitemap.xml`
- `dist/robots.txt`
- `dist/styles.css`

## Notes

This setup intentionally avoids CMSs and heavy tooling. Add more posts by adding Markdown files; the build regenerates tags, post listings, next/previous navigation, RSS, sitemap and pages automatically.

## License

Code in this repository is licensed under the MIT License. Writing, articles, and personal content under `src/about.md` and `src/posts/` are © Talip Göksu. All rights reserved unless stated otherwise.
