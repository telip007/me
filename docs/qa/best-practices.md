# FastAPI, HTMX and PageSpeed review — 1 November 2026

Scope: the existing English-only FastAPI/Jinja blog and supplied PageSpeed screenshots. This is an applicable-practices review, not a claim that every framework feature belongs in the project. The initial implementation was local on `codex/blog-best-practices` in `/Users/tag/.codex/worktrees/blog-best-practices/personal-blog`. The user subsequently authorized publication. The release candidate incorporates main through `2581d06`, preserving the published page share cards and homepage copy. Unrelated uncommitted articles remain outside this branch. Release verification is recorded separately in the shared Wiki.

## Implemented

- **Render-blocking requests:** `site.css` (12,569 bytes) and `reading.css` (11,516 bytes) are trusted local sources embedded by the shared renderer. Home includes only site CSS; other pages include reading CSS as well. This removes both blocking stylesheet fetches. Gzip remains enabled. Cost: CSS bytes travel with each HTML document instead of a separately cached CSS response. Keep this decision under review if styles grow substantially.
- **Font dependency chain:** local font references are resolved in the initial HTML, with real content fingerprints and the configured base path. Display font preload matches its CSS URL exactly. Prose pages also preload the regular reading font; unused semibold is not preloaded. `font-display: swap` remains in place.
- **CSP:** inline CSS is authorized using SHA-256 hashes of exactly the bytes rendered. No `unsafe-inline` or `unsafe-eval` was added. Only repository CSS enters the trusted style blocks; user metadata and Markdown cannot enter them.
- **Cache safety:** one-year immutable caching now requires a successful static response (200 or 304) with the matching per-file fingerprint. Arbitrary query strings, old fingerprints and missing files get `no-cache`. A fresh process loads content/asset versions at startup; deployed files must remain immutable during the process lifetime.
- **HTTPS/security:** HSTS `max-age=31536000` for configured HTTPS origins, including when TLS is terminated by Fly Proxy. Browsers ignore HSTS received over plain HTTP. No dependency on untrusted forwarded request headers, no subdomain-wide or preload commitment. Added `Cross-Origin-Opener-Policy: same-origin`. Existing nosniff, anti-framing, referrer, permissions and CSP protections remain.
- **Dependency security:** the runtime package audit initially reported 49 advisory records across Pillow 12.3.0 and Starlette 0.52.1 (some records alias the same issue; exploitability was not demonstrated). Updated only Pillow to 13.0.0 and Starlette to 1.3.1, the smallest release lines that clear the reported findings; FastAPI stays at 0.135.4. The refreshed lock file passes the current audit with no known vulnerabilities. Share-card URL fingerprints now include the Pillow version so a renderer upgrade cannot silently reuse a prior immutable URL.
- **HTMX:** explicit `historyRestoreAsHxRequest: false`, a 10-second timeout, no eval, no executable response scripts, same-origin requests, no localStorage history cache, and a finite delayed search with `hx-sync=this:replace`. Intentional replacement aborts no longer announce network failures. Dedicated HTTP/network/timeout events retain existing results and show recovery feedback.
- **Discovery:** `/llms.txt` provides a generated English Markdown overview using only the public content graph. `/.well-known/ai-catalog.json` lists real overview, writing, feed and sitemap resources with truthful MIME types. The same compatible manifest is also served at the current ARD discovery path `/.well-known/ard.json`. Head links and a robots `Agentmap` advertise them. The shared exporter includes all three files; they do not expose source files, drafts or excluded German material. These are emerging proposals, not proven search-ranking improvements.

## Existing practices retained

| Area | Evidence in the application |
| --- | --- |
| FastAPI concurrency | Synchronous rendering/file/Pillow work uses ordinary `def` endpoints, which FastAPI runs in its thread pool. No blocking work was moved into `async def` endpoints. |
| Startup/failure behavior | `create_app` validates the entire content graph before serving. Startup configuration and content are process snapshots. No disposable per-request client/database resource needs a lifespan manager. |
| API surface | Read-only GET/HEAD, deliberate 308 redirects, rendered 404, no public OpenAPI/admin/debug UI. No state-changing endpoint requiring sessions/CSRF was added. |
| Content safety | Non-executable front matter, duplicate-key rejection, raw HTML disabled, escaped Jinja text, protected JSON-LD and XML escaping. |
| Deployment | Locked dependencies, non-root image, health checks, warm Fly machine, HTTPS proxy, tests before automatic deployment. Single-machine availability limits remain documented. |
| Progressive enhancement | Native GET form and links work without JavaScript; server filtering, result announcements, loading/error feedback and stable input focus. |
| Cache/history | Full documents for direct/history requests; fragments for HTMX; Vary includes HX-Request, HX-History-Restore-Request and compression encoding. |
| Accessibility | Native labeled controls, landmarks, skip link, visible keyboard focus, no positive tabindex/focus trap, semantic table overflow wrappers, reduced motion. These code checks do not replace assistive-technology testing. |

## Screenshot items requiring interpretation

The ten accessibility rows are **manual checks**, not ten failed automatic audits. No new controls were invented to satisfy them. Code and existing regression coverage support labels, roles, landmarks and focus behavior. This session's complete responsive/keyboard/screen-reader assessment is still pending.

The WebMCP form/tool/schema rows are **not applicable** to this read-only blog. No tools or remote actions are advertised. llms.txt and AI Catalog were also initially not applicable, and were added at the user's request.

**Trusted Types enforcement remains open.** HTMX 2.x parses and swaps HTML using protected DOM sinks. Enabling `require-trusted-types-for 'script'` without an integrated, tested sanitizing policy would break search; an identity/pass-through policy would only silence the audit. The existing CSP, no-eval/script configuration, server escaping and HTML-disabled Markdown remain active. The change does not claim to pass every Lighthouse security recommendation.

## Verification and limits

- Baseline: 33 Python tests passed before changes.
- Four new Python regressions failed on the original implementation (CSS links, absent HSTS, implicit HTMX history config, absent discovery endpoints), then passed after the changes.
- The new abort-feedback Node regression failed before the JS correction; all four feedback tests then passed.
- Final checks: 38 Python tests under Python 3.12 and 3.14, 12 Node tests (8 export + 4 feedback), Ruff, content validation and static build pass.
- Linux production image built successfully with Python 3.13; a non-root (UID 10001) container with a 256 MB limit returned 200 for homepage, health, writing, llms.txt, both catalogs, RSS and sitemap. This is local image validation, not deployment.
- Tests report two upstream deprecation warnings (Starlette TestClient/httpx and anyio BlockingPortal); no warnings are suppressed. No application test failed.
- An independent read-only review found no substantive findings in delivery/discovery changes. Actual crawler adoption, browser-dependent checks and deployment were outside that review. A schema-valid catalog with no representativeQueries remains a catalog listing, not demonstrated ARD search discovery.
- Both generated catalogs validated with `jsonschema` Draft 2020-12 + format checks against the AI Catalog schema and pinned ARD `ArdManifest` schema. Validation used temporary tooling, with no validator runtime dependency added. The separately described Pillow/Starlette security updates do change the dependency lock.
- Before the browser restriction, one limited headless check confirmed that both inline style blocks were accepted (114 + 78 CSS rules), local fonts loaded, and one HTMX search preserved input focus and announced `1 article`. This was not a full browser acceptance run.
- The user then requested no browser use. The task-owned headless browser was stopped. No subsequent browser work, visual QA or Lighthouse run was performed. An earlier Lighthouse launch failed before obtaining a report because its launcher could not locate Chrome. No PageSpeed score, measured 300 ms saving, field CWV improvement or full accessibility certification is claimed.
- Public HTTPS readback still showed the previous stylesheet links and headers. At the initial audit checkpoint, this confirmed that the new implementation had not yet been released.

## Publication preparation

After the user authorized publication, main through `2581d06` was merged without conflicts. The combined candidate passes 41 Python tests under 3.12 and 3.14, 12 Node tests, Ruff, content validation, export and a rebuilt Linux image smoke with exact CSP hashes and generated cards for all canonical public pages. Browser/Lighthouse checks remain suspended.

## Primary references

- [Pillow 13 security release](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html), [Starlette security advisories](https://github.com/Kludex/starlette/security/advisories) and [PyPI FastAPI dependency metadata](https://pypi.org/pypi/fastapi/0.135.4/json).
- [FastAPI async guidance](https://fastapi.tiangolo.com/async/): ordinary def endpoints for synchronous libraries.
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/): process startup, memory and replication tradeoffs.
- [HTMX documentation](https://htmx.org/docs/): caching, history, security, synchronization and configuration. Project keeps the reviewed local 2.0.11 build.
- [Chrome: render-blocking requests](https://developer.chrome.com/docs/performance/insights/render-blocking).
- [Chrome: network dependency tree](https://developer.chrome.com/docs/performance/insights/network-dependency-tree).
- [MDN: HSTS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security) and [COOP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy).
- [llms.txt v2 proposal](https://llmstxt.org/), [AI Catalog draft](https://ai-catalog.io/spec/) and [ARD v0.91](https://agenticresourcediscovery.org/spec/).
- [AI Catalog schema](https://github.com/ards-project/ard-spec/blob/main/spec/schemas/ai-catalog.schema.json), [pinned ARD schema](https://github.com/ards-project/ard-spec/blob/f073b1ea9b01a5f068d0b0986426f2ea49fa30b2/spec/schemas/ard-entry.schema.json), [Lighthouse ARD validator provenance](https://github.com/GoogleChrome/lighthouse/blob/main/third-party/ard/README.md).
