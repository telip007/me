# FastAPI and HTMX blog rewrite

User request: replace the Node static generator with FastAPI + HTMX, strengthen editorial practice from the Pragmatic Engineer article and other original sources, and research a premium engineering-blog design as of October 2026. Parallel implementation and research are authorized.

## Product and reader

Talip Göksu writes about AI, LLMs and agentic engineering in German and English. Preserve public professional identity and source content. No invented experience, measurements, articles, AI disclosure banners, new archive, CMS or tracking. The original untracked article is outside scope. The two tracked posts are drafts; an empty index is correct.

## Architecture

Markdown stays in src; safe YAML/JSON front matter; Markdown raw HTML remains disabled. Python content loading validates metadata and routes before serving or exporting. FastAPI renders Jinja templates. HTMX progressively enhances GET search/topic filtering with HTML fragments. Real links/forms work without JS. No boosted navigation: ordinary navigation keeps native focus, metadata and history behavior. Search requests carry no history snapshots. Full-document history restores never receive a fragment.

Preserve every German/English route, translation fallback, RSS, sitemap, canonical URL, /about/ redirect and basePath behavior. Do not rewrite the privacy notice. FastAPI is the primary runtime; static export uses the same renderer for optional GitHub Pages compatibility, without nonfunctional search controls. A production host cutover is separate and not performed here.

## Visual direction (implementation judgment)

Read mode. Seven grounded directions considered: engineering notebook, conference proceedings, digital publication, code-review commentary, science journal, modern technical paperback, and field guide. The direction-seed assigned candidate six: modern technical paperback. Its identifiable mechanism is the contrast between confident grotesk titles and quiet serif long-form reading, with the publication's subject immediately visible. Developer-console panels, dance notation, draped textiles, editing rails and dense data art reduce clarity for this small reading surface; keep their discipline in alignment, controlled density and purposeful motion, without adopting their motifs.

Palette: cool white #fbfcff, white #ffffff, ink #172238, secondary #52617a, line #dce2ec, cobalt #234ee8. Manrope display/UI; Source Serif 4 reading text; system mono only for code. Typography is the memorable element, not decorative animation. Headline max 6rem, tight but legible tracking. Content width about 68ch. Large screens: broad title plus compact subject/mission column; article body with optional sticky contents rail. Mobile: stack in reading order, wrap nav, reserve no empty rail. No fake featured stories.

One authored motion: short underline expansion on intentional navigation plus brief opacity feedback on refreshed search results. Optional same-origin page transitions only where supported and with reduced motion respected. Every state is visible without animation. No automatic looping movement. Keyboard focus visible, touch targets at least 44px, skip link, high contrast, selected-topic text state, live result count, recovery on failed requests, print styles and horizontal overflow containment.

## Editorial deliverables

Source-linked research matrices, editorial guide with concrete topic/reader promise, primary-source evidence, reproducible original work, explanation structure, editing, feedback, translation parity, corrections and publication checklist. Do not rewrite existing factual About/privacy copy.

## Acceptance

- FastAPI serves real pages and HTMX filtering; ordinary GET/no-JS and static export remain useful.
- Meaningful tests cover draft isolation, languages/translation, metadata and XML escaping, unsafe front matter/raw HTML, routes/base path, query fragments/history, TOC and malformed content.
- Existing Node command interface delegates to Python; no competing Node renderer remains.
- Self-host assets and font licenses; no third-party browser requests or cookies.
- Browser verification covers desktop/mobile, article fixtures, empty index, search, keyboard/no-JS/reduced motion; generated examples never enter live src.
- Documentation covers setup, test/build, Docker/runtime, hosting boundary, editing and research decisions.
