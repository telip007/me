---
name: Talip Göksu — Engineering Blog
description: A reading-first bilingual technical publication with confident sans-serif titles and quiet serif prose.
colors:
  paper: "#fbfcff"
  surface: "#ffffff"
  ink: "#172238"
  muted: "#52617a"
  accent: "#234ee8"
  accent-soft: "#edf1ff"
  line: "#dce2ec"
  control-border: "#7d8ba3"
  search-surface: "#f1f4fa"
  error: "#a02035"
typography:
  display:
    fontFamily: "Manrope, Helvetica Neue, sans-serif"
    fontSize: "clamp(3.3rem, 7.4vw, 6rem)"
    fontWeight: 700
    lineHeight: 1.06
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Manrope, Helvetica Neue, sans-serif"
    fontSize: "clamp(2.65rem, 5.2vw, 4.7rem)"
    fontWeight: 700
    lineHeight: 1.16
    letterSpacing: "-0.04em"
  article-title:
    fontFamily: "Manrope, Helvetica Neue, sans-serif"
    fontSize: "clamp(1.4rem, 2.4vw, 2rem)"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.03em"
  prose:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "1.2rem"
    fontWeight: 400
    lineHeight: 1.8
  interface:
    fontFamily: "Manrope, Helvetica Neue, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  control: "5px"
  button: "6px"
  panel: "8px"
spacing:
  gutter: "clamp(1.25rem, 5vw, 5rem)"
  small: "1rem"
  medium: "1.5rem"
  section: "2rem"
components:
  primary-button:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.button}"
    padding: ".65rem 1.4rem"
  search-input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "48px"
---

# Design System: Talip Göksu

## Overview

**Creative North Star: “Modern technical paperback.”**

This is a professional personal publication about AI, language models and agentic engineering, read in German and English. Its identity comes from typographic scale, precise alignment and the contrast between confident sans-serif headings and unhurried serif reading. The surface feels open, cool and deliberate. Content and its evidence lead; ornament does not compete with them.

This document records the built Jinja templates, `blog/static/site.css` and `blog/static/site.js`, checked on 29 October 2026. `PRODUCT.md` owns product truth; [the research](docs/research/design.md) explains the source-informed decisions. These tokens describe implemented values, rather than a claim that one aesthetic is universally current. The public source presently has no published posts; article/list screenshots use temporary local fixtures, not new public writing.

**Key characteristics:**

- Cool paper, dark ink and a single assertive cobalt accent.
- Large, balanced display titles; narrow, comfortable long-form prose.
- Editorial rows and hairline divisions rather than a card collection.
- Native navigation and complete HTML, with small progressive enhancements.
- A layout that stacks naturally on narrow screens and accommodates both languages.

## Colors

### Primary

Cobalt is the active accent: identity mark, article links, arrows, focused controls, primary actions and selected navigation underline. Its pale companion supplies quiet hover feedback. Use it to identify a meaningful action, not to paint large decorative regions.

### Neutral

Cool paper is the shared background across home, article, topic, About, privacy and error pages. White identifies control interiors. Ink carries headings and prose; muted blue-gray carries excerpts and supporting metadata. Hairlines divide sections and article rows. Search has its own pale panel surface; control boundaries are stronger than decorative dividers. Error red identifies a failed request.

The checked primary text contrasts against paper are approximately 15.48:1 for ink, 6.11:1 for muted text and 6.15:1 for cobalt. This is token-level evidence, not a whole-site accessibility certification. Keep focus, visited/hover changes and any new surfaces independently readable.

**The accent rule.** Use cobalt for action and orientation. Do not invent a second brand accent to distinguish topics.

## Typography

Manrope is self-hosted for display and interface text. Source Serif 4 is self-hosted in regular and semibold for long-form reading and the short editorial statement. Fonts use `font-display: swap`; their license files live alongside assets. System monospace is reserved for code. Do not load font services from third-party origins.

The frontmatter records desktop roles. Responsive adjustments are intentional: the homepage title becomes `clamp(2.8rem, 10vw, 4rem)` below 700px; article titles become `clamp(2.1rem, 8vw, 3.5rem)`. Prose is 1.2rem with 1.8 line-height on large screens and 1.13rem on small screens. Article decks use a larger sans-serif voice to connect title and body. Supporting interface labels are smaller and quieter; input/select text remains 1rem, including mobile.

Section headings return to Manrope within serif prose. Titles use balanced wrapping where supported. Heading tracking is compact, but paragraphs retain normal spacing. Code preserves whitespace; long links and exceptionally long titles must wrap without widening the page. Pagination titles explicitly allow breaks anywhere to contain long German compounds.

**The reading rule.** A strong display title is not a reason to tighten body copy. Preserve the 68ch maximum prose measure and generous line spacing.

## Layout

The shared outer frame is centered, at most 1440px wide, with the fluid gutter in the token list. Thin rules establish shared horizontal alignments. The header places identity left and the small navigation right. At 700px and below, identity and navigation occupy separate rows; the language switch stays at the right edge of the second row.

The homepage introduces the subject with a broad title and a narrower mission column. At 1000px and below, this becomes one column; at 700px, the description and About link stack. The article area follows without requiring a full-viewport hero. Search sits immediately before the article list when published content exists in the dynamic runtime. Article rows use a 175px metadata column plus flexible text at desktop, becoming a single column on mobile. Topic pages reuse the same row pattern under their topic heading.

Article headers are wider than the reading body. The reading area has a 200px contents rail and flexible prose at large widths, a 165px rail below 1000px, and a stacked contents block above prose below 700px. The rail is sticky with its own bounded vertical overflow on desktop; it is static on mobile. Without contents, the body uses a single reading region. Standalone About/privacy pages use the same prose treatment with a quiet desktop offset that disappears on narrower screens.

Footer content uses the outer grid, collapses into stacked groups below 1000px and wraps its links. Error pages retain the shared identity/navigation/footer and give the recovery action a clear reading order.

Code and wide tables scroll locally. They must never create page-level horizontal scrolling. With JavaScript, tables receive a scroll wrapper that preserves native table semantics; overflow regions gain keyboard focus only when needed. Without JavaScript, the CSS table overflow treatment remains available. Treat keyboard access in each supported browser as a verification task rather than assuming identical browser behavior.

## Elevation & Depth

The design is flat. There is no shadow vocabulary. Depth comes from whitespace, type hierarchy, the difference between paper and pale control surfaces, and restrained borders. Do not introduce floating cards, blurred glass, gradients or large shadows into article layouts.

## Shapes

Most content is unboxed. Controls use small rounded corners; search and code panels use the larger panel radius. The language switch is circular. Tags are plain underlined text with generous hit height, not colored pills. Inline icons are simple strokes; the compact cobalt identity mark is the recurring graphic signature.

## Components

**Navigation and identity.** Keep the name and mark together as a home link. Writing and About remain the main choices. The current section has an underline, and the language control names its destination language. Footer links expose RSS, GitHub, privacy and a back-to-top action. The English privacy link explicitly identifies the German page.

**Article list.** Present a real title, excerpt, publication date, reading time and topic links. An arrow supports the title link without becoming a separate unlabeled control. Use real content only. The empty index says there are no posts yet; no decorative sample article, fabricated count or fake featured story fills the gap.

**Search and topic filter.** Use visible labels, a standard search input, select and submit button. Normal GET submission works without JavaScript. HTMX replaces the results region while preserving the focused form and provides loading feedback, an accessible result-count status and a request error with recovery guidance. No-results copy suggests another term or all topics and provides a reset link. Static exports omit runtime search controls.

**Article reading.** The title/deck/metadata/byline establish the reading context before prose. A native `details` contents panel supplies linked headings. Body links stay visibly underlined. Code, tables, blockquotes, lists and images use the same measure and spacing language. Previous/next article navigation wraps long titles and always offers all writing.

**Focus and targets.** The global focus indicator is a three-pixel cobalt outline with five-pixel offset. A skip link becomes visible on focus and moves to main content. Navigation, tags and contents targets have at least 44px minimum hit height; primary controls are 48px. Do not remove focus feedback for aesthetic reasons.

**Motion.** Intentional navigation underlines expand in 160ms using the implemented easing curve `cubic-bezier(.16,1,.3,1)`. The result region has a brief opacity transition; supported same-origin document transitions use a 120ms duration. Content is visible without animation. Reduced-motion settings remove animations, transitions and smooth scrolling. There are no loops, scroll reveals, custom cursors or parallax.

**Print.** Printing removes navigation, footer, contents rail, search and pagination. It uses black on white, 11pt prose, a clear article title and visible URLs after external source links. Code wraps for paper. Print is a reading adaptation, not a screenshot of the desktop chrome.

## Do's and Don'ts

- Do preserve the distinction between display typography, interface labels and reading prose.
- Do check actual German and English copy at narrow widths, increased spacing and zoom.
- Do keep links, forms and source material useful without client JavaScript.
- Do use temporary fixtures outside the live publication source for layout verification.
- Do treat the documented local appearance separately from deployment, field performance and assistive-technology certification.
- Don't invent public articles, experiments, author experience or metrics to make a layout look complete.
- Don't expose private background context or implementation-only details as editorial content.
- Don't add an archive, corporate mega-navigation, CMS controls, tracking, chat widget or new disclosure banner as a design embellishment.
- Don't hide prose behind entry animations or make motion necessary to understand a state.
- Don't promote one screenshot review into a claim that every route, browser or accessibility mode has been verified.

## Final asset-loading refinement

HTMX and its configuration load only on runtime homepages with published writing and a search form. The reading-helper script loads on article pages and searchable runtime homepages. Empty and ordinary About/privacy pages ship without browser scripts. Font URLs include content versions for immutable caching; the primary font preload uses the same URL as CSS. The visible language abbreviation is included in its accessible name. Final recaptures in docs/qa/screenshots verify pagination wrapping after the initial review finding.
