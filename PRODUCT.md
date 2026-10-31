# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

User-requested rewrite: FastAPI and HTMX, with Markdown as the content source. Jinja renders HTML. Fly.io hosts the FastAPI runtime; pushes to main run verification and deployment through GitHub Actions. Static export remains optional.

## Users

Inferred from the existing public copy: English-speaking software practitioners reading about AI, language models and agentic engineering. The homepage helps readers find a relevant article; article pages help them understand and check its evidence.

## Product Purpose

Talip Göksu's professional personal blog. Concrete examples, verifiable sources and open questions, as established in src/config.json and the About pages.

## Capabilities and Constraints

Publish English at the root, without a language switch. Preserve RSS, sitemap and professional About links; redirect old English/About/privacy URLs. Maintain an English privacy policy for Fly.io. No archive, database, CMS, tracking or cookies. No invented articles or personal experience. Drafts never appear publicly. The original checkout has an untracked user article that is outside this migration.

## Brand Commitments

Name: Talip Göksu. Understated, professional public voice with a distinctive, expressive visual identity. OpenAI, Vercel, Apple, Material 3 Expressive, Anthropic/Claude and Mistral are calibration references for the requested October 2026 research. Their identities inform original judgment; they are not templates to copy.

## Evidence on Hand

src/config.json, src/about.md, src/privacy.md and two tracked draft translations. The source currently contains no published articles. Use temporary fixtures to verify article layouts.

## Product Principles

- Reading and finding relevant writing come first.
- Technical claims need linked evidence; private context stays private.
- Legacy links redirect to existing English counterparts; German posts stay excluded.
- HTML remains usable without JavaScript.
- A local implementation is separate from a public deployment.

## Selected visual direction — 29 October 2026

The user rejected the first cool-white/cobalt implementation as sterile and resembling Bootstrap. After reviewing alternatives, they directly corrected an accidental B answer and explicitly selected **A: Argument in layers**. This correction is the selection authority. B and C remain unselected studies; the first blue/white treatment is superseded.

The selected system is grounded in [the A prototype](docs/design-exploration/a.html) and [its study stylesheet](docs/design-exploration/directions.css): a wine-colored opening, an offset paper reading plane and an exposed citron edge. The same edge becomes a reading annotation at smaller scale. Bricolage Grotesque carries display/interface text; Source Serif 4 carries long-form reading. [DESIGN.md](DESIGN.md) records the selected roles and implementation contract.

The subject is AI broadly, coding, technology and agentic engineering. Personal context supplied to inform design remains private; it must not become public biographical copy, terminology, affiliation claims or literal identity motifs. No public content is added to make a visual direction look complete.

Selected A is implemented in the actual FastAPI frontend. Local browser checks cover responsive reading, bilingual QA articles, HTMX/search history and recovery, keyboard/no-JavaScript use, table overflow, text spacing and reduced motion; [the verification record](docs/qa/selected-a/verification.md) records the evidence boundary. This describes the original local design checkpoint. The 31 October release changes About and privacy to English; posts remain drafts. The site description now reflects the broader AI/coding subject, and the favicon follows the selected identity. Local acceptance and Lighthouse lab results do not establish public deployment or production field performance.
