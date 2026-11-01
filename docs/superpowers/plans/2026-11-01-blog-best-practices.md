# FastAPI, HTMX and PageSpeed implementation

User brief: audit the existing English blog against current official FastAPI/HTMX guidance, implement applicable PageSpeed suggestions, and include llms.txt and AI Catalog discovery. Preserve design, GET fallback, privacy and static export. No deployment requested.

## Task 1: Harden delivery and discovery

Files: blog/main.py, blog/content.py, blog/templates/base.html, blog/static/site.js, tests/test_blog.py, tests/browser_smoke.py, docs/qa/best-practices.md.

1. Add regression coverage for render-blocking CSS removal, CSP hashes, font discovery/base paths, cache validation, HSTS/COOP, HTMX configuration, public-only discovery and export. Run tests and observe failures.
2. Inline the small trusted stylesheets by page type, rewrite local font URLs with verified content fingerprints, authorize only the exact styles with CSP hashes, preload reading font only on prose pages. Keep source CSS and static compatibility files.
3. Use immutable cache only for successful static responses with a matching fingerprint. Add one-year HSTS for configured HTTPS origins (no unverified subdomain coverage), COOP same-origin. Keep sync rendering in FastAPI's thread pool; no database/lifespan framework is needed for immutable startup content.
4. Set HTMX historyRestoreAsHxRequest=false and finite timeout, preserve last results on failures, avoid errors for replaced/aborted requests. Keep eval/scripts disabled and same-origin requests.
5. Generate /llms.txt and /.well-known/ai-catalog.json (also current ARD discovery path) from public content only. Discover through head links/robots; preserve base paths and export. List only real read-only documents with honest MIME types.
6. Run Python and Node suites, Ruff, content check and build. Browser smoke includes keyboard, no-JS, network failures, latest-search wins, responsive pages and CSP. Compare local mobile Lighthouse before/after using identical settings if browser use is permitted. Record evidence and compatibility limitations.
7. Resolve package-audit findings with the smallest compatible dependency updates; include Pillow in immutable social-card versioning, run Python 3.12/3.14 and Linux image checks.
8. Review whole diff independently, fix material findings, update Wiki, then leave local changes reviewable without publishing.

Execution note: Browser work was stopped at the user's request; full visual/Lighthouse validation is pending. Main checkout acquired independent share-card test changes during execution, so implementation remains on its isolated branch.

Review focus: stale/arbitrary asset versions and 304s; CSP inline bytes and subpath fonts; search replacement races and history; draft/German isolation on every discovery surface; static export with dot-directory catalog. Trusted Types must not be enabled with an unsafe pass-through policy for HTMX's HTML sinks. No artificial MCP/WebMCP capabilities.
