# Local browser assets

No asset is loaded from a third-party origin at runtime.

- `htmx.min.js`: HTMX **2.0.11**, vendored from https://github.com/bigskysoftware/htmx/tree/v2.0.11/dist . Zero-clause BSD license in htmx-LICENSE.txt. The maintained 2.x release is deliberately pinned; the project does not require 4.x APIs. Upgrade by reviewing release notes and rerunning fragment/history/browser tests.
- `fonts/BricolageGrotesque.woff2`: Bricolage Grotesque variable font, SIL OFL 1.1. Original https://github.com/google/fonts/tree/main/ofl/bricolagegrotesque . Converted from BricolageGrotesque[opsz,wdth,wght].ttf and subset to U+0000–024F, U+2000–206F and U+20AC with FontTools, with the unused width axis fixed at its default 100; weight and optical-size axes remain variable. Includes German and English characters. License in fonts/BricolageGrotesque-OFL.txt. The user selected this expressive type voice in direction A.
- `fonts/SourceSerif4-Regular.woff2` and `SourceSerif4-Semibold.woff2`: Adobe Source Serif 4, SIL OFL 1.1. Original https://github.com/adobe-fonts/source-serif/tree/release/WOFF2/TTF . License in fonts/SourceSerif4-OFL.md.
- `site.css`, `reading.css`, `site.js`, and geometric identity mark: original project implementation.
- `fonts/BricolageGrotesque-Social.ttf`: derived from the same licensed local WOFF2 using FontTools, with weight 650 and optical size 48 fixed. Used by Pillow for automatic share cards; no external font request or browser process is needed. The existing Bricolage OFL license applies.

Retrieved 2026-10-29. Fonts use `font-display: swap`; only the primary display font is preloaded. Decorative page transitions are progressive enhancement and disabled for reduced motion.

Bricolage source TTF SHA-256: `413e7357809ddd12fd80a96a8a396de0e401638d4acd3cb3e37532f0472ac682`; production WOFF2 SHA-256: `89c140b3bc41dfbf3156834945ad3eb817d1ec0090ce71674c941253e532569b`. Source retrieved again to retain typographic punctuation.
