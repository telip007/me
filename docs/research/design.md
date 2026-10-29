# Reading-first engineering blog: design research

Research checked **29 October 2026**. Scope: a bilingual personal publication by Talip Göksu about AI, LLMs, agents and practical software engineering. This document separates observations from design recommendations. It records a defensible contemporary direction, rather than claiming that any aesthetic is an objectively universal October 2026 trend. Sources are original publishers, standards bodies and platform documentation. No content, outcome, metrics or reader demand is invented.

## Direction

**A precise engineering publication with the presence of a design journal.** Use cool white, near-black ink, a single saturated cobalt accent, oversized tightly composed display typography and generous whitespace. Pair a wide, confident opening composition with a quiet, narrower article measure. Keep the author and subject immediately recognizable, then put real writing within reach. Make the page memorable through typography, grid and proportion; let interaction feedback communicate what changed.

This palette is a design decision, not a finding that blue improves reading or that big tech uniformly uses it. Its purpose is to give this publication a distinct, coherent visual voice. The incumbent `src/styles.css` uses an almost-black background, cream type, a serif display stack, an up-to-1680px frame and a near-full-viewport introduction. A replacement should retain existing content and routes while deliberately replacing that visual world. Avoid inheriting its very tight display line-height and letter-spacing without testing German titles and text enlargement.

A personal site has a different task and scale from a corporate engineering portal. It needs a short navigation, language choice, clear subject, actual articles, source links and subscription through RSS. It does not need product navigation, sales calls to action, fabricated article thumbnails, decorative dashboards, corporate claims or an AI chat interface.

## Contemporary publication observations

These observations come from the accessible HTML of the actual sites, checked on the research date. They establish content hierarchy and controls, not pixel-level screenshot analysis.

| Original source | Observed pattern | Application here |
| --- | --- | --- |
| [Stripe Dev Blog: Engineering](https://stripe.dev/blog/topic/engineering) | Dated engineering entries expose short summaries, author names and topics. The topic filter includes AI, infrastructure and developer productivity. Its visible latest engineering entry is dated 19 October 2026. | Give each real post a useful excerpt, explicit publication date and navigable topics. Treat the article list as editorial content, not a uniform collection of decorative cards. Preserve the small site's scale instead of reproducing Stripe's many filters. |
| [Spotify Engineering](https://engineering.atspotify.com/) | Entries pair dates, descriptive titles, concise opening summaries and categories; the category control follows the lead item. The visible lead is dated 16 October 2026. | Let the headline explain the technical subject and the excerpt explain why to read. Place discovery near the articles. A row can be visually rich through type alone. |
| [Engineering at Meta](https://engineering.fb.com/) | A lead set is followed by a clearly labeled latest sequence with category/date metadata and a load-more action. RSS remains available in its footer. Entries visible through 29 October 2026. | Distinguish a genuine featured post from the chronological list only when editorial metadata actually identifies one. Keep RSS findable. Use an honest empty state when there is no published writing. |
| [Vercel Engineering](https://vercel.com/blog/category/engineering) | A category heading, search, featured section, then ordinary posts provide multiple paths into the same publication. The source includes a specific no-results message and recovery suggestion. | Provide an article search with meaningful status and clear reset. It must work as a normal URL/form and may be enhanced with HTMX. Do not borrow the product mega-navigation. |

Synthesis: the repeatable useful pattern is **orientation → meaningful article choice → comfortable reading → continued discovery**. The visual recommendation above is our interpretation of this task, not a copied brand system.

## Typography, composition and links

[GOV.UK's layout guidance](https://design-system.service.gov.uk/styles/layout/) starts from one column on small screens and recommends avoiding more than roughly 75 characters per line on ordinary text pages. Apply this as an article width around `65–72ch`, with a wider outer frame for navigation and article indexes. Keep code and genuinely two-dimensional tables independently scrollable. Do not squeeze article prose into a wide desktop grid merely because space exists.

[GOV.UK paragraphs](https://design-system.service.gov.uk/styles/paragraphs/) uses 19px body text and a distinct introductory paragraph. Adopt roughly 18–20px prose, a comfortable line-height near 1.65–1.75 and an optional larger deck below the title. These exact values are our implementation choices and require rendering checks; the source does not mandate this site's font or line-height. Metadata should remain comfortably readable rather than becoming 10px ornament. Distinguish title, deck, publication metadata, section headings and prose through scale and spacing before adding more colors.

[GOV.UK links](https://design-system.service.gov.uk/styles/links/) uses blue underlined links and cautions against opening new tabs unexpectedly. Keep article source links visibly underlined in their resting state and describe their destination. Navigation can use a quieter treatment because its context establishes function. Give visited article links a coherent visited color where useful. Do not replace descriptive link text with repeated “click here” labels or external-link icons on every citation.

Avoid third-party font requests; retain reliable German diacritics and use a system mono stack only for code. The final implementation deliberately chooses self-hosted Manrope for display/UI and Adobe Source Serif 4 for reading, with local fallback stacks, font-display: swap and one display-font preload. This adds approximately 185KB of local font payload (before HTTP compression), trading a small download for a consistent typographic identity; only fonts used by a page are fetched. This is a design judgment, not a standard requirement. Text must paint immediately. [Google's CSS/Web Vitals guidance](https://web.dev/articles/css-web-vitals) identifies font-delayed rendering and font metric changes as sources of poor loading experience and layout shift. Reserve explicit dimensions for images and avoid injecting decorative elements above already rendered prose.

For bilingual layouts, test actual long German compounds and existing English titles. Use `text-wrap: balance` as an enhancement for display headings; use `overflow-wrap` on long URLs and titles where necessary. Keep dates locale-aware and specify the document language. A language switch should link to the actual translation where it exists and otherwise to a clearly identified locale landing page. Never invent an alternate-language article URL.

## Motion and interaction

[IBM Carbon's motion foundation](https://www.carbondesignsystem.com/building-blocks/foundations/motion/overview), updated 12 August 2026, distinguishes productive motion from occasional expressive motion. It puts efficiency, feedback and unobtrusiveness first. It lists 110ms for fades, 150ms for short movements and 240ms for expansion or system communication. Apply one compact motion vocabulary: roughly 120–160ms for link/arrow/control feedback and around 180–240ms for a filtered-result change. Carbon's productive curve `cubic-bezier(0.2, 0, 0.38, 0.9)` is a useful starting point. Final values are design choices.

Motion should answer a reader's question: “Did my search apply?”, “Is this link interactive?”, “What changed?” A small underline/arrow movement and restrained result fade are sufficient. Keep content readable immediately. Avoid hiding articles until an intersection observer runs, perpetual hero motion, parallax, custom cursors, scroll hijacking and repeated entrance animation on every paragraph.

[Google's animation guide](https://web.dev/articles/animations-guide) recommends `transform` and `opacity` and warns against properties that trigger layout or paint. Use these for the few animated elements. Do not transition `all`, paragraph widths, margins or large shadow effects. A hover treatment may move its arrow two pixels; it should not lift a full article row and disturb the reading plane.

[MDN's reduced-motion reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) documents the user's request to remove, reduce or replace nonessential motion and the discomfort caused by large scaling/panning. Under `prefers-reduced-motion: reduce`, remove decorative transforms, entry animations and smooth scrolling; preserve immediate visible state changes. Detect the same setting before any optional scripted transition.

[Chrome's View Transitions overview](https://developer.chrome.com/docs/web-platform/view-transitions/) describes smoother changes between document states. Treat such transitions as optional enhancement, never a prerequisite for navigation. A short fade may enhance list updates if supported, but native links, focus, back/forward navigation and a reduced-motion path take priority. Do not claim universal support without checking the specific same-document/cross-document feature and browser versions. HTMX does not require View Transitions to make this design work.

## Accessibility requirements that shape the design

| Original source | Consequence for implementation and verification |
| --- | --- |
| [W3C WCAG 2.2: Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | Normal informative text requires at least 4.5:1 contrast; qualifying large text at least 3:1. Verify primary, muted, link, hover and focus colors against their real backgrounds. Thin pale labels are still informative text. |
| [W3C: Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) | At 320 CSS pixels wide, ordinary vertical content must work without two-dimensional scrolling. Check narrow viewports and 400% zoom. Permit local overflow for code/tables that require two dimensions, not the whole page. |
| [W3C: Text Spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) | Users must be able to override line-height to 1.5, paragraph spacing to 2em, letter spacing to .12em and word spacing to .16em without losing functionality/content. These are override-resilience test values, not mandated defaults. Avoid fixed-height title or metadata containers. |
| [W3C: Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | Pointer targets generally need 24×24 CSS pixels or the specified spacing/other exceptions. Aim for roughly 44px control height for comfortable mobile use. The latter is our usability target, not this AA criterion's numeric minimum. |
| [W3C: Focus Not Obscured (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) | Focus cannot be entirely hidden by author-created content. Use a visible focus ring, skip link and sensible DOM order. If sticky navigation is introduced, account for it with scroll padding and test keyboard traversal. |

Search/filter updates need a concise accessible result count/status. Preserve an obvious field label and submission path. Avoid replacing the focused input during an HTMX update; make ordinary links independently operable. An empty result view should identify that no matching articles were found and offer a reset. A total no-posts state must remain honest and calm.

## Performance and acceptance evidence

[Google's Web Vitals overview](https://web.dev/articles/vitals), last updated 31 October 2024 at the checked source, defines good thresholds of **LCP ≤2.5s, INP ≤200ms and CLS ≤0.1**, assessed at the 75th percentile, separately for mobile and desktop. These are field targets; a single Lighthouse run does not prove production Core Web Vitals.

For this implementation: render main text in the original HTML; keep CSS compact and local; avoid external font/script connections; load only the local enhancement needed for interaction; reserve image space; cache static assets intentionally. Motion must not cause layout shifts. The pure-HTML response must remain useful if JavaScript is unavailable.

Before calling the design complete, gather a bounded batch of evidence:

1. Desktop and mobile captures of the homepage, actual article, article list/search, About and empty/no-result state. Use real bilingual text, with no filler posts created in the publication source.
2. Viewport checks at 320px, around 390px, tablet and a wide desktop. Verify that menus, language choice, title and metadata remain legible; local code/table overflow must not overflow the page.
3. Keyboard traversal, visible focus, a working skip link, semantic headings and labeled forms. Search and navigation must work without JavaScript.
4. Reduced-motion capture/check and text-spacing/zoom resilience. Verify that article content is never initially hidden by an animation.
5. Automated contrast/accessibility scan plus manual checks for meaning and focus behavior. A clean scan is evidence at its coverage, not blanket accessibility certification.
6. A local performance report with environment stated. Keep production field targets explicitly unverified until real traffic measurements exist.

The strongest version of this site is fast, typographically confident and editorially credible. The actual writing and its evidence remain the centerpiece; the design makes them easier to find, understand and remember.
