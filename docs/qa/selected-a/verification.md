# Selected direction A — final local verification

29 October 2026. The user explicitly selected **A** after correcting an accidental B answer. The rejected blue/white checkpoint in `../verification.md` is historical evidence, not the selected visual identity. A is implemented in the actual FastAPI/Jinja application, including homepage, real article/index fixtures, topic pages, both About locales, unchanged German privacy content and 404.

## What changed

Wine `#281e2a` carries the opening and navigation. Bricolage Grotesque gives display/UI text its character. The offset paper `#eee9dc` reading plane exposes a citron `#e1ec93` edge; related edges recur at reading annotations. Source Serif 4 carries prose, with olive source links. Selected-A motion consists of brief arrow feedback and settling outline planes, plus quiet result/page transitions. Reduced motion removes decorative movement and smooth scrolling. No personal background from the private design brief appears in public copy or literal cultural motifs.

The site description now covers artificial intelligence broadly, software and agents. The favicon follows the layered-plane geometry. Existing About, privacy and post Markdown bytes are unchanged; both tracked translations remain drafts. No untracked user article was copied. No new article was published. No source archive or AI disclaimer was added.

## Technical and browser evidence

- **27 Python tests** and **8 original Node export-contract tests** passed; Ruff, static build, content validation and diff whitespace checks passed. Content validation reports0 public posts / 10 routes.
- `tests/browser_smoke.py` passed against selected-A runtime 8010 and temporary fixture 8011: index and bilingual articles at 320/390/768/1440px, long German title, HTMX document/focus retention, live count, reload/back, network failure with prior results retained, successful retry, native table semantics/focusable overflow, reduced motion, text spacing, skip link and native GET search with browser JavaScript fully disabled.
- Independent source review and five-capture inspection found no material fidelity/legibility issue. The first integration capture exposed missing reading foundations; the final stylesheet restores metadata spacing, TOC semantics/layout, code/table/media rules, pagination and print behavior. Final captures verify those corrections.
- The mechanical detector used a regex fallback because optional parser modules were unavailable. Its initial documentation advisories identified missing type/color inventory; DESIGN.md now describes actual source values. The complete follow-up report contains eight remaining type-ramp advisories and three regex warnings for 3px annotation lines in the contents rail, quotation and code. Those lines deliberately repeat the selected edge grammar on semantic reading elements; they are not card decorations. These diagnostics were reviewed rather than described as a clean detector pass. This tooling is supplementary, not an accessibility or design acceptance certificate.
- Contrast checks on paper: wine 13.23:1, muted 5.50:1 and olive 5.22:1. Header/controls and all page states remain subject to the rendered checks; no formal WCAG certification is claimed.

## Performance and assets

The final local mobile Lighthouse 13.0.1 run scored **98 Performance / 100 Accessibility / 100 Best Practices / 100 SEO**, with **LCP 1.9s, TBT 0ms and CLS 0**. [Exact environment and metrics](lighthouse-summary.json). An earlier run scored 99 / LCP 1.8s before the final punctuation subset. These are local lab observations, not production field Core Web Vitals or a guarantee for other hosts/devices.

Bricolage is local, 83,816 bytes, with the unused width axis fixed at 100 and variable weight/optical size retained. German characters, curly quotes, en/em dashes and Euro glyphs were checked in its cmap. CSS/preload/manifest/runtime bytes share SHA-256 `89c140b3bc41dfbf3156834945ad3eb817d1ec0090ce71674c941253e532569b`. The original OFL license matches upstream. Font source/conversion details are in `blog/static/ASSETS.md`. No external font/script origin or cookies are introduced.

## Container

Final selected-A image: `sha256:8c5ad44c778a99ea99c56b50fc0b2f60b93b82eb2392e114df5e616973c77e0d`.

Independent Docker smoke verified: nonroot runtime, health module exit 0, HEAD 200 with empty body, gzip/Vary for homepage/CSS/reading.css/HTMX, selected-A assets/license present, Bricolage runtime bytes/hash matching source and no QA assets. The earlier baseline separately verified `/me` mount behavior; A changes preserve routing. Temporary QA containers were stopped and removed.

## Final captures and reproduction

[Desktop home](screenshots/home-desktop.png), [mobile home](screenshots/home-mobile.png), [desktop article fixture](screenshots/article-desktop.png), [mobile article fixture](screenshots/article-mobile.png), [320px index fixture](screenshots/list-mobile.png).

The article/list captures contain explicitly labeled local QA content, never publication-source articles. The real homepage is correctly empty. Run:

```sh
uv sync --locked
uv run --locked uvicorn blog.main:app --host 127.0.0.1 --port 8000
# Separate terminal; owns and cleans up a temporary content directory:
uv run --locked python tests/serve_ui_fixture.py --port 8011
# Existing Chromium or a Playwright browser installation required:
uv run --isolated --no-project --with playwright==1.56.0 python tests/browser_smoke.py --base http://127.0.0.1:8000 --fixture http://127.0.0.1:8011
```

Use `--chromium /absolute/path/to/chromium` for an existing executable. The built-in test commands are in README. One upstream Starlette TestClient deprecation warning remains; all assertions pass.

## Publication boundary

This is a local implementation in the attached isolated worktree. No push, merge, hosting purchase, DNS change or public deployment occurred. GitHub Pages can serve HTMX and static fragments; it cannot execute FastAPI. The preserved Pages export intentionally omits server filtering. The full runtime needs a Python-capable host, with hosting/privacy wording reviewed after choosing that host.

Vendor note: the original OFL license texts contain upstream trailing whitespace. They are retained byte-for-byte; source whitespace checks exclude those vendored license files.
