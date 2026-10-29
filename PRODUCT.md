# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

User-requested rewrite: FastAPI and HTMX, with Markdown as the content source. Jinja renders HTML. The existing GitHub Pages destination can use a static export; server filtering requires the FastAPI runtime.

## Users

Inferred from the existing public copy: German- and English-speaking software practitioners reading about AI, language models and agentic engineering. The homepage helps readers find a relevant article; article pages help them understand and check its evidence.

## Product Purpose

Talip Göksu's professional personal blog. Concrete examples, verifiable sources and open questions, as established in src/config.json and the About pages.

## Capabilities and Constraints

Preserve German routes, English translations, RSS, sitemap, professional About links and German privacy text. No archive, database, CMS, tracking or cookies. No invented articles or personal experience. Drafts never appear publicly. The original checkout has an untracked user article that is outside this migration.

## Brand Commitments

Name: Talip Göksu. Understated, professional public voice. The user asks for a thoroughly researched, high-quality technology-blog design as of October 2026. No specific palette or reference site was supplied; the visual proposal remains an implementation judgment.

## Evidence on Hand

src/config.json, src/about.md, src/about.en.md, src/datenschutz.md and two tracked draft translations. The source currently contains no published articles. Use temporary fixtures to verify article layouts.

## Product Principles

- Reading and finding relevant writing come first.
- Technical claims need linked evidence; private context stays private.
- Language changes preserve the reading context where a published counterpart exists.
- HTML remains usable without JavaScript.
- A local implementation is separate from a public deployment.
