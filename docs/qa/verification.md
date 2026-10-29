# Initial technical checkpoint — 29 October 2026

**Visual status:** The user subsequently rejected the initial palette/composition as sterile and generic. The technical evidence below remains valid for that checkpoint; it does not establish visual acceptance. A broader identity exploration is now in progress.

The rewrite is local, in an isolated worktree based on `640ff81`. No push, merge, public deployment, domain change, new host or content publication occurred. The original checkout's untracked `src/posts/was-ist-ki.md` was not copied, staged or modified. Existing tracked Markdown/config/favicon bytes are unchanged. The two tracked article translations remain drafts. Current validation correctly reports **0 public posts / 10 routes**.

## Acceptance audit

| Requirement | Authoritative evidence | Result |
| --- | --- | --- |
| Real FastAPI + HTMX rewrite | `blog/main.py`, `blog/content.py`, templates, local HTMX; actual HTTP runtime and browser smoke | Implemented. Python is the single renderer. Node build delegates to it. |
| Requested writing source and broader research | `docs/research/editorial.md`, `docs/research/design.md`: 28 distinct original-source URLs | Inspected sources and dated findings; recommendations are distinguished from evidence. |
| Concrete editorial improvements | `docs/editorial-guide.md`: reader brief, explanation/investigation/tutorial outlines, claim ledger, editing, feedback, bilingual parity, corrections and publication checks | Implemented as a reusable writing workflow. No invented article or claimed human review. |
| Premium contemporary reading design and animation | `DESIGN.md`, templates/CSS, five screenshots below; independent visual review | Manrope/Source Serif, local assets, deliberate grid, accessible states, purposeful short transitions and reduced motion. No claim of an objectively universal visual trend. |
| Bilingual URL/feed/metadata/privacy contracts | Python fixtures and original Node tests, actual About pages | German/English routes, translations/fallbacks, RSS, sitemap, base path and privacy text preserved. |
| Safe content/draft isolation | Duplicate-key, YAML/JSON, raw HTML, invalid route/date/language/tag, draft/feed/sitemap tests | Drafts fail closed; no executable front matter. |
| Native GET and enhanced search | Real Chromium browser smoke: fragment marker preserved, focused field kept, live count, reload/back, native form with JavaScript disabled | Passed. |
| Error/empty states | Real empty homepage and no-result fixture; aborted request retained prior result and displayed recovery | Passed. |
| Responsive/accessibility | Browser at 320/390/768/1440px; text-spacing override; table semantics; keyboard skip link; reduced motion; contrast checks; axe and Lighthouse | Passed at tested scope. No physical-device or formal WCAG certification claimed. |
| Build/runtime/export | 27 Python tests, 8 original Node export tests, Ruff, build/content checks; Docker default and `/me` mount | Passed. Static export omits server-only search and HTMX. |
| No unintended publication or source changes | Git diff/status, unchanged source content, isolated worktree and no external writes | Confirmed. |

## Fresh command results

```sh
uv run --locked ruff check blog tests scripts/export.py scripts/check_content.py
uv run --locked pytest
node --test scripts/build.test.js
npm run build
uv run --locked python scripts/check_content.py
```

Ruff: all checks passed. Python: **27 passed**. Node: **8 passed**, no failures. Build: exit 0. Content: 0 public posts and 10 routes. Local interpreter Python 3.14.6; container Python 3.13 and CI configured for 3.12. One upstream Starlette TestClient deprecation warning remains (`anyio.abc.BlockingPortal` alias); it does not affect the runtime or passing assertions.

Independent code review reported Markdown-table regression, lost table semantics, rendered-HTML search, noindexed topic pages, duplicate-key draft ambiguity, timestamp loss and unsafe exporter targets. These were fixed. A final scoped review independently verified all reported fixes, with 11 relevant tests passing. The mechanical design detector ran in regex fallback mode because optional parser modules were unavailable; its empty findings are not treated as proof. Explicit contrast checks, browser inspection and accessibility scans supplement it.

## Browser checks and reproduction

Run the real site and the temporary fixture server in separate terminals:

```sh
uv run --locked uvicorn blog.main:app --host 127.0.0.1 --port 8000
uv run --locked python tests/serve_ui_fixture.py
```

The fixture server uses a temporary directory, labels all examples as local QA, and removes the directory on shutdown. It never writes into public `src/`.

With Chromium installed for Playwright:

```sh
uv run --isolated --no-project --with playwright==1.56.0 python tests/browser_smoke.py
```

Use `--chromium /absolute/path/to/chromium` for an existing browser, and `--screenshots /tmp/blog-qa` to change the capture directory. Verification used local Chromium 140, headless on macOS. The test passed:

- Index and bilingual article reflow at 320, 390, 768 and 1440px, including a long unbroken title.
- HTMX fragment updates, unchanged document marker, retained search focus, accessible result count, query reload and native back navigation.
- Simulated network failure with prior results retained, visible recovery and successful retry.
- Native table semantics and focusable code/table overflow; reduced motion; WCAG text-spacing override without page overflow.
- Skip link moves focus to main; existing professional About link remains.
- Browser JavaScript fully disabled: normal GET search returns the expected result.

Axe 4.10.3 scans on homepage and 320px article fixture reported no violations in their tested coverage. A later Lighthouse bundled axe 4.14.0 identified the language abbreviation/name mismatch; the accessible label now includes the visible EN/DE abbreviation, and the rerun passed that audit.

Final screenshots: [desktop home](screenshots/home-desktop.png), [mobile home](screenshots/home-mobile.png), [desktop article fixture](screenshots/article-desktop.png), [mobile article fixture](screenshots/article-mobile.png), [320px index fixture](screenshots/list-mobile.png). Final article captures confirm the initial long-title pagination overlap is resolved. They depict temporary QA content, not published writing.

## Performance

Local mobile Lighthouse 13.0.1 run: **97 Performance / 100 Accessibility / 100 Best Practices / 100 SEO**. LCP 1.7s, CLS 0. See [machine-readable summary](lighthouse-summary.json) for exact environment/metrics. This was a bounded local lab check before adding response compression; it is not production field data or evidence of real-user INP.

Container verification then confirmed gzip compression: HTML 4626→1681 bytes, CSS 16701→4639 bytes, HTMX 52182→17059 bytes. Fonts are local, versioned and cached; empty and About/privacy pages load no browser JavaScript. No third-party browser origins or cookies are introduced.

## Container

Final tested image: `sha256:f8e3faf58d6b769da18ae5b99cd58bda9e4f3f6e0a47c9884cd07e3b3a494f77`.

Nonroot runtime user `blog`; HTTP/HEAD and health passed. A separate `/me` configuration test confirmed prefixed homepage, assets, links and health probe. No temporary QA assets were present in the final image. QA containers were removed after checks.

## Hosting boundary

GitHub Pages serves HTML, CSS and JavaScript, including HTMX and static fragments. It cannot run FastAPI or dynamic server filtering. The preserved Pages workflow uses the same Python renderer for a static export and keeps native topic navigation. Deploying the full runtime requires a Python-capable host and a hosting/privacy review after choosing it. No public cutover was requested or performed.
