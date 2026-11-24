# Local browser assets

All browser assets are served by the site.

- `htmx.min.js`: HTMX 2.0.11 from [the release distribution](https://github.com/bigskysoftware/htmx/tree/v2.0.11/dist). Zero-clause BSD license in `htmx-LICENSE.txt`.
- `fonts/InriaSerif-{Regular,Bold,Italic}.woff2`: local Inria Serif faces from the approved editorial design. The regular and bold TTFs used by Pillow come from [Black Foundry’s Inria Serif sources](https://github.com/BlackFoundryCom/InriaFonts/tree/95a529cee87d8be884632644d3d37ad28512be28/fonts/InriaSerif/TTF). SIL OFL 1.1 in `fonts/InriaSerif-OFL.txt`.
- `fonts/MonaspaceNeon-Regular.woff2`: Monaspace Neon Regular from the approved editorial design. SIL OFL 1.1 in `fonts/MonaspaceNeon-OFL.txt`.
- The prior Bricolage Grotesque and Source Serif 4 files retain their bundled OFL licenses and their original paths for previously cached pages.
- The three root icons in `src/` share a small-scale drawing derived from the footer seal. The footer seal and its animation are local.

The site preloads Inria Serif Regular and Bold and Monaspace Neon Regular. Browser fonts use `font-display: optional`. The renderer fingerprints local font URLs and authorizes the embedded styles and theme bootstrap with exact CSP hashes.
