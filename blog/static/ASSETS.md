# Local browser assets

No asset is loaded from a third-party origin at runtime.

- `htmx.min.js`: HTMX **2.0.11**, vendored from https://github.com/bigskysoftware/htmx/tree/v2.0.11/dist . Zero-clause BSD license in htmx-LICENSE.txt. The maintained 2.x release is deliberately pinned; the project does not require 4.x APIs. Upgrade by reviewing release notes and rerunning fragment/history/browser tests.
- `fonts/Manrope.woff2`: Manrope variable font, SIL OFL 1.1. Original https://github.com/google/fonts/tree/main/ofl/manrope . Converted from Manrope[wght].ttf and subset to U+0000–024F with FontTools; includes German and English characters. License in fonts/Manrope-OFL.txt. No renamed reserved font name.
- `fonts/SourceSerif4-Regular.woff2` and `SourceSerif4-Semibold.woff2`: Adobe Source Serif 4, SIL OFL 1.1. Original https://github.com/adobe-fonts/source-serif/tree/release/WOFF2/TTF . License in fonts/SourceSerif4-OFL.md.
- `site.css`, `site.js`, and geometric identity mark: original project implementation.

Retrieved 2026-10-29. Fonts use `font-display: swap`; only the primary display font is preloaded. Decorative page transitions are progressive enhancement and disabled for reduced motion.
