# FastAPI and HTMX Implementation Plan

> **For agentic workers:** Use parallel ownership for backend, editorial research and design research; root integrates frontend and validates the complete application.

**Goal:** Deliver the complete research-informed FastAPI + HTMX rewrite while preserving content and URL contracts.

**Architecture:** Python content repository and Jinja rendering are shared by FastAPI and the optional static exporter. HTMX filters HTML fragments; normal GET is the fallback.

**Tech Stack:** FastAPI, Jinja2, markdown-it-py, PyYAML, HTMX, CSS, minimal browser JS.

**Spec:** docs/superpowers/specs/2026-10-29-blog-design.md

## Global constraints

- Preserve all existing DE/EN URL, privacy, draft and public-persona contracts.
- Keep untracked user content in the original checkout untouched.
- No public deployment, invented articles, analytics, database or blanket AI notices.

## Review focus

- Draft-only and empty content must produce usable pages and empty valid feeds.
- Query/history combinations must not cache a fragment as a full page.
- Untrusted strings must remain escaped across HTML, attributes, JSON-LD and XML.
- Long code/tables/links must remain usable at narrow widths.
- Static export must not expose controls that require a backend.

## Tasks

- [x] Backend agent: write failing fixture tests; implement content parsing, URL/translation registry, FastAPI routes, filtered fragments, feeds/sitemap, export, dependency lock and Docker runtime. Run pytest.
- [x] Editorial researcher: inspect requested source and additional originals; write source matrix and actionable editorial guide.
- [x] Design researcher: inspect original engineering blogs and platform/design standards; write source-to-decision matrix.
- [x] Root: create Jinja shell/list/article/page/error templates, responsive CSS, local fonts/HTMX, accessible request states and purposeful motion. Test through real fixture browser pages.
- [x] Root: replace legacy build implementation with Python command wrapper; preserve npm command interface and update workflow/README/AGENTS to actual architecture.
- [x] Independent review: audit implementation and research against spec; fix substantive issues, run fresh tests/build/browser checks.
- [x] Record verified results and durable findings using the shared wiki helper; completion audit against every acceptance item.

## Visual revision after user review

- [x] Record rejection of initial blue/white direction and preserve privacy of contextual brief.
- [x] Broaden original-source identity research beyond the supplied references.
- [x] Build three materially different visual systems and reading treatments.
- [x] Resolve the visual direction with user feedback: direct correction confirms A.
- [x] Carry the selected system through all routes and repeat relevant browser checks.
- [x] Update final documentation/wiki with the selected A implementation and verified evidence before completion.
