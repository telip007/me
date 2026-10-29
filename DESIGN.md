---
name: Talip Göksu — Argument in layers
description: A bilingual engineering publication with a wine opening, an offset paper
  reading plane and a citron annotation edge.
colors:
  wine: '#281e2a'
  paper: '#eee9dc'
  citron: '#e1ec93'
  opening-text: '#eee9dc'
  opening-muted: '#d9ccd9'
  opening-line: '#5b4b5e'
  reading-line: '#c9c3b5'
  code-surface: '#e4dfd2'
  control-surface: '#f5f0e6'
  reading-muted: '#655868'
  reading-accent: '#59652a'
  reading-accent-soft: '#e5e7c8'
  inline-code-table-head: '#e2ddcf'
  button-language-hover: '#48394b'
  language-border: '#a48fa6'
  input-border: '#8b7e8d'
  tag-underline: '#a99da9'
  scrollbar-thumb: '#8a748d'
  tap-highlight: '#a1aa6550'
  request-error: '#9a253c'
  plane-fallback-border: '#b49db6'
  plane-back-border: '#6e536f'
  plane-middle-border: '#ac8dad'
  print-paper: white
  print-ink: black
  print-rule: '#999'
typography:
  display:
    selector: .intro h1
    fontFamily: Bricolage Grotesque, Helvetica Neue, sans-serif
    fontSize: clamp(4.25rem, 8.9vw, 7.875rem)
    fontWeight: 650
    lineHeight: 0.99
    letterSpacing: -0.025em
    responsive:
      max1000px: clamp(4rem, 10vw, 6rem)
      max700px: clamp(3.1rem, 13vw, 4.8rem)
  interface:
    selector: body, input, select
    fontFamily: Bricolage Grotesque, Helvetica Neue, sans-serif
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.6
  identity:
    selector: .identity
    fontSize: 1.55rem
    fontWeight: 650
    lineHeight: 1.2
    responsive:
      max700px: 1.5rem
  navigation:
    selector: .site-nav
    fontSize: .94rem
    responsive:
      max700px: .84rem
  page-title:
    selector: .article-header h1, .page-prose h1, .error-state h1
    fontFamily: Bricolage Grotesque, Helvetica Neue, sans-serif
    fontSize: clamp(2.8rem, 5.6vw, 5.5rem)
    fontWeight: 650
    lineHeight: 1.06
    letterSpacing: -0.025em
    responsive:
      max520px: clamp(2.1rem, 8.8vw, 3rem)
      max520pxLineHeight: 1.1
      print: 28pt
  global-h1-fallback:
    selector: h1
    fontSize: clamp(2.7rem, 5.5vw, 5.5rem)
    fontWeight: 600
  topic-title:
    selector: .topic-page > h1
    fontSize: clamp(3rem, 6vw, 5.5rem)
    fontWeight: 650
    lineHeight: 1.06
    responsive:
      max520px: clamp(2.1rem, 8.8vw, 3rem)
  writing-heading:
    selector: .section-heading h2
    fontSize: 2.85rem
    fontWeight: 600
    responsive:
      max700px: 2.15rem
  list-title:
    selector: .row-copy h2, .row-copy h3
    fontSize: clamp(1.5rem, 2.5vw, 2.25rem)
    fontWeight: 600
    lineHeight: 1.2
    responsive:
      max700px: 1.65rem
  list-excerpt:
    selector: .row-copy > p
    fontSize: 1.05rem
    lineHeight: 1.7
    responsive:
      max700px: 1rem
  opening-description:
    selector: .intro-aside > p
    fontSize: 1.125rem
    lineHeight: 1.65
    responsive:
      max700px: 1rem
  article-deck:
    selector: .article-deck
    fontSize: clamp(1.15rem, 1.8vw, 1.4rem)
    lineHeight: 1.65
    responsive:
      max520px: 1.08rem
      print: 13pt
  prose:
    selector: .prose
    fontFamily: Source Serif 4, Georgia, serif
    fontSize: 1.25rem
    fontWeight: 400
    lineHeight: 1.8
    responsive:
      max520px: 1.13rem
      print: 11pt
      printLineHeight: 1.5
  prose-h1:
    selector: .prose h1
    fontSize: clamp(2.4rem, 5.6vw, 5.5rem)
    fontWeight: 650
    lineHeight: 1.06
  prose-h2:
    selector: .prose h2
    fontSize: clamp(1.5rem, 2.4vw, 1.9rem)
    fontWeight: 650
    lineHeight: 1.22
    responsive:
      max520px: 1.5rem
  prose-h3:
    selector: .prose h3
    fontSize: 1.35rem
    fontWeight: 650
    lineHeight: 1.22
    responsive:
      max520px: 1.2rem
  prose-h4:
    selector: .prose h4
    fontSize: 1.1rem
    fontWeight: 650
    lineHeight: 1.22
  editorial-statement:
    selector: .editorial-note p
    fontFamily: Source Serif 4, Georgia, serif
    fontSize: 1.65rem
    lineHeight: 1.3
    responsive:
      max700px: 1.5rem
  empty-title:
    selector: .empty-state h2, .empty-state h3
    fontSize: 1.55rem
    fontWeight: 500
    responsive:
      max700px: 1.4rem
  empty-description:
    selector: .empty-state p
    fontSize: 1rem
    lineHeight: 1.6
    responsive:
      max700px: .95rem
  metadata:
    selector: .row-meta, .article-meta
    fontSize: .8rem
    responsive:
      rowMax700px: .76rem
      articleMax520px: .75rem
  byline:
    selector: .article-byline
    fontSize: .85rem
    fontWeight: 600
    responsive:
      max520px: .8rem
  contents:
    selector: .contents
    fontSize: .8rem
    lineHeight: 1.6
    summarySize: .82rem
    summaryWeight: 650
  utility-copy:
    selector: feed/about/back links, footer, status, tags and captions
    fontFamily: Bricolage Grotesque, Helvetica Neue, sans-serif
    fontSizeRange: .76rem–.95rem
    actualSizes:
    - .76rem
    - .77rem
    - .78rem
    - .8rem
    - .82rem
    - .84rem
    - .85rem
    - .88rem
    - .9rem
    - .94rem
    - .95rem
  inline-code:
    selector: .prose code
    fontFamily: SFMono-Regular, Consolas, Liberation Mono, monospace
    fontSize: .78em
  code-block:
    selector: .prose pre
    fontFamily: SFMono-Regular, Consolas, Liberation Mono, monospace
    fontSize: .95rem
    lineHeight: 1.75
    responsive:
      max520px: .85rem
    nestedCodeSize: .9em
  table:
    selector: .prose table
    fontFamily: Bricolage Grotesque, Helvetica Neue, sans-serif
    fontSize: .9rem
    lineHeight: 1.6
  print-source-url:
    selector: .prose a[href^="http"]::after
    fontSize: 9pt
spacing:
  gutter: clamp(1.5rem, 5.2vw, 5rem)
  reading-measure: 68ch
shapes:
  reading-plane: offset with one rounded leading corner
  signature: three offset outlined planes
  annotation: a narrow exposed edge beside reading navigation
status: implemented
---

# Design system: Argument in layers

## Selection and status

The user explicitly selected **A** after correcting an accidental B response. The selected reference is [A: Argument in layers](docs/design-exploration/a.html), with the `.layers` rules in [directions.css](docs/design-exploration/directions.css). The first cool-white/cobalt design was rejected as sterile; B and C are unselected alternatives.

The selected direction is implemented in the FastAPI frontend as of 29 October 2026. The code-derived token inventory below records the current runtime styles rather than the rejected design or prototype-only values. Local functional and visual checks cover the selected-A integration; their scope and artifacts belong in [the verification record](docs/qa/selected-a/verification.md). This is not public deployment or accessibility certification. [PRODUCT.md](PRODUCT.md) owns product truth and publication constraints.

Source inspection confirms the core palette and Bricolage/Source Serif font roles in `blog/static/site.css`, the real homepage plane/outlined mark in `blog/templates/home.html`, and the reading-plane/annotation treatment in `blog/static/reading.css`. `base.html` preloads Bricolage and loads the two stylesheets in that order. This is source evidence, not a rendered QA result.

## The distinctive rule

**An offset plane becomes an exposed edge, then a reading annotation.**

The wine opening establishes a strong first-screen identity. A paper reading plane enters with a horizontal offset and one rounded leading corner; a narrow citron edge is exposed beneath it. Three outlined planes echo this relationship at a different scale. On article pages, the edge becomes a compact section/contents annotation rather than another oversized hero.

This rule carries character through home, lists, articles, About, privacy and recovery states. It is an original graphic system, not a diagram of a real agent architecture or a claim about an experiment. Decorative shapes stay outside the accessibility tree. No private biographical or identity motif is encoded in them.

## Color roles

| Token | Value | Role and boundary |
| --- | --- | --- |
| Wine | `#281e2a` | Opening field, primary reading text and dark controls. |
| Paper | `#eee9dc` | Main reading plane and long-form surface, including About and privacy. |
| Citron | `#e1ec93` | Exposed layer, an important action surface on wine and a small orientation signal. Never pale body-link text on paper. |
| Opening text | `#eee9dc` | Main text and navigation on wine. |
| Opening muted | `#d9ccd9` | Supporting opening description. |
| Opening line | `#5b4b5e` | Quiet divisions on the dark field; not a required control boundary or focus indicator. |
| Reading line | `#c9c3b5` | Quiet section/list divisions on paper. |
| Code surface | `#e4dfd2` | A small material change inside the reading plane, with wine text and local overflow. |
| Control surface | `#f5f0e6` | Light control interiors. |
| Reading muted | `#655868` | Secondary text on paper. |
| Reading accent | `#59652a` | Dark olive links, annotations and focus on the reading plane. This darker relative of citron keeps pale signal color out of reading text. |
| Reading accent soft | `#e5e7c8` | Quiet selected/hover surface within the light plane. |

The first three values are the selected core palette. Supporting values now describe the implemented control and reading states. The YAML also inventories secondary literals: hover wine, control borders, underline/scrollbar shades, translucent tap feedback, request-error red, the three outlined-plane borders and print-only colors. The plane fallback border is a base declaration overridden by the three individual plane rules; it is documented as such, not promoted to a new brand token. These are role assignments, not a claim that every literal is a separate semantic design token. Local checks do not establish whole-site accessibility certification. Body links remain visibly underlined and dark enough to read. Citron is an edge or surface, not a universal accent painted onto every word, icon and control. Do not revive cobalt or introduce unrelated gradients.

## Typography

**Bricolage Grotesque** carries display and interface text. Its character appears in the name, title composition, navigation and section headings. Keep font-family aliases, preload URLs and CSS coherent. Self-host licensed assets with `font-display: swap`; retain provenance and licenses. The active selected-A templates use Bricolage rather than Manrope.

**Source Serif 4** carries long-form reading. Existing regular/semibold assets can be reused. The study's Georgia body and Instrument Serif statement are prototype treatments; the selected integration uses Source Serif 4. System monospace is reserved for code, not ornamental labels.

The live stylesheet currently defines the opening title as `clamp(4.25rem, 8.9vw, 7.875rem)` with `-.025em` tracking. Article titles use `clamp(2.8rem, 5.6vw, 5.5rem)` with their own narrow-screen adjustment. `reading.css` defines 1.25rem/1.8 prose with a 68ch maximum, reducing to 1.13rem below 520px. The YAML records the main type ramp, responsive replacements, utility range and print roles from the two active stylesheets. No CSS was changed to silence an inventory detector. Captured rendering checks exercise the large display treatment and long German titles; they do not establish every possible content length or device.

## Layout, shape and interaction

The opening holds an author masthead, compact native navigation, a large subject title and a concise description. The plane illustration remains secondary to the words. Narrow screens stack title/description, simplify decoration and reduce the reading-plane offset so it does not consume the text width.

The paper transition is a substantial surface with one distinctive corner. Article entries stay a continuous editorial list. The real empty state is a valid composition; no fabricated articles, counts or featured story fills it. Article pages reuse the wine/paper relationship at smaller scale. Their contents marker translates the exposed edge into an annotation. About, privacy, topics and errors share the same materials and alignment logic.

Radius is structural: the reading-plane corner, outlined signature and circular action affordance have separate jobs. Code/controls use quiet practical rounding. Depth comes from the visible offset rather than repeated shadows or blurred panels.

The A study's circular action affordance advances its arrow on deliberate hover, and its outlined planes can subtly settle from rotation. Integrate only motion that supports response or orientation. Every state remains understandable with reduced motion; remove decorative movement and smooth scrolling while keeping selection and result text visible. No looping diagrams, paragraph reveals, custom cursors or scroll hijacking.

## Implementation contract

- Apply A to the actual Jinja templates and `blog/static/` assets. Exploration review navigation and the layout-only sample article never enter public templates or live source.
- Preserve the wine → offset paper → citron annotation relationship across routes. Do not repeat the full homepage hero above every article.
- Use Bricolage for display/UI and Source Serif 4 for reading; keep font loading local, versioned and aligned with the active preload.
- Preserve complete server-rendered HTML, native links, labeled GET search enhanced with HTMX, focused-form preservation, accessible request status and error recovery. Static exports omit runtime-only controls.
- Preserve draft exclusion, real published translations, canonical URLs, RSS, sitemap and base-path behavior. German URLs and English routes under `/en/` remain intact.
- Preserve professional About links and the existing German privacy content. English links continue identifying that privacy page as German.
- Keep code/table overflow local and keyboard reachable, native table semantics intact, long titles/URLs contained, and focus visible against each surface.
- Keep the understated public voice. Add no invented experience, private context, identity motifs, archive, tracking, CMS, chat widget or blanket disclosure.
- Coordinate the opening stylesheet with the reading stylesheet. Later rules must not silently restore the old palette, fonts or hero structure.

## Local verification

The selected-A browser pass covers 320, 390, 768 and 1440px viewports; the real empty index; bilingual QA articles; HTMX search and back navigation; failed-request recovery; no-JavaScript submission; skip-link focus; local table overflow; text-spacing overrides; and reduced motion. QA articles stay outside the live publication source. The source posts, About pages and privacy text are unchanged; the configuration description now reflects the broader AI/coding subject and the favicon follows the selected identity.

The local Lighthouse run reports 99 performance, 100 accessibility, 100 best practices and 100 SEO, with LCP 1.8s and CLS 0. These are lab results for the measured route/environment, not production Core Web Vitals, field performance or blanket accessibility certification. See [selected-A verification](docs/qa/selected-a/verification.md) for the commands, captures and scope.

Selection proves direction; a screenshot proves its captured state; tests prove their covered contracts. Public deployment and physical-device/assistive-technology certification are separate and are not claimed here.
