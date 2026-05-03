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
- `dist/posts/<slug>/index.html`
- `dist/about/index.html`
- `dist/tags/<tag>/index.html`
- `dist/rss.xml`
- `dist/sitemap.xml`
- `dist/robots.txt`
- `dist/styles.css`

## Notes

This setup intentionally avoids CMSs and heavy tooling. Add more posts by adding Markdown files; the build regenerates tags, post listings, next/previous navigation, RSS, sitemap and pages automatically.
