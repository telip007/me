"""Server-rendered English blog; HTMX enhances an ordinary GET search form."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote_from_bytes
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from blog.content import (
    FEED,
    HOME,
    LANGUAGES,
    TAG_PREFIX,
    ContentStore,
    date_value,
    format_date,
    load_content,
    normalize_base_path,
)
from blog.discovery import render_catalog, render_document, render_llms, wants_markdown
from blog.social import HEIGHT, WIDTH, card_content, card_path, page_card_path, page_cards, render_card

ROOT = Path(__file__).resolve().parents[1]
ICONS = {
    "favicon.svg": "image/svg+xml",
    "favicon.ico": "image/vnd.microsoft.icon",
    "apple-touch-icon.png": "image/png",
}
ENTRY_ID_CONFLICTS = {
    "writing", "writing-title", "posts", "topic",
    "article-search", "search-loading", "search-status", "search-error",
}
LABELS = {
    "en": {
        "notes": "Notes",
        "article": "Article",
        "articles": "Articles",
        "empty": "No posts yet.",
        "emptyDetail": "The first article will appear here when it is ready.",
        "readTime": "min read",
        "skip": "Skip to content",
        "navigation": "Main navigation",
        "footer": "Footer",
        "top": "Back to top ↑",
        "about": "About this blog",
        "articleNavigation": "Article navigation",
        "intro": "AI, LLMs & Agentic Engineering",
        "edition": "Observations from practice",
        "more": "About this blog",
        "topicPosts": "Articles about",
        "search": "Search articles",
        "searchPlaceholder": "Topic or keyword",
        "searchSubmit": "Search",
        "allTopics": "All topics",
        "clear": "Clear filters",
        "noResults": "No matching articles.",
        "noResultsDetail": "Try another keyword or select all topics.",
        "results": "Results",
        "contents": "On this page",
        "back": "All articles",
        "notFound": "This page could not be found.",
        "notFoundDetail": "The link may have changed. Find every article on the homepage.",
        "loading": "Loading articles …",
        "filter": "Filter",
        "privacy": "Privacy",
        "updated": "Updated",
    },
}


def csp_hash(content: bytes) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(content).digest()).decode() + "'"


def create_app(
    source_dir: str | Path | None = None,
    static_dir: str | Path | None = None,
    base_path: str | None = None,
    *,
    static_export: bool = False,
) -> FastAPI:
    source = Path(source_dir or ROOT / "src")
    assets = Path(static_dir or ROOT / "blog" / "static")
    store = load_content(source)
    prefix = normalize_base_path(store.config.get("basePath") if base_path is None else base_path)
    store.config["basePath"] = prefix
    host_aliases = frozenset(
        alias.strip().lower() for alias in os.getenv("BLOG_CANONICAL_HOST_ALIASES", "").split(",") if alias.strip()
    ) if not static_export else frozenset()
    templates = Jinja2Templates(directory=str(ROOT / "blog" / "templates"))
    templates.env.filters["format_date"] = format_date
    asset_versions = {
        item.relative_to(assets).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()[:12]
        for item in sorted(assets.rglob("*")) if item.is_file()
    }

    def asset_url(name: str) -> str:
        return f"{prefix}/static/{name}?v={asset_versions[name]}"

    def inline_css(name: str) -> str:
        # Only trusted repository CSS is embedded. Fonts must resolve from the document URL.
        css = (assets / name).read_text() if (assets / name).is_file() else ""
        return re.sub(
            r"url\('fonts/([^'?]+)(?:\?[^']*)?'\)",
            lambda match: f"url('{asset_url('fonts/' + match[1])}')",
            css,
        )

    styles = {"site": inline_css("site.css"), "reading": inline_css("reading.css")}
    style_hashes = " ".join(csp_hash(css.encode()) for css in styles.values())
    theme_boot = (ROOT / "blog/static/theme-boot.js").read_bytes()
    theme_hash = csp_hash(theme_boot)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None) if prefix else app
    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
    app.state.content = store
    app.state.base_path = prefix
    app.state.static_dir = assets
    app.state.source_dir = source
    app.state.static_export = static_export
    social_cards = {
        card_path(post, store.config): card_content(post, store.config)
        for post in store.posts if not post.image
    }
    site_cards = page_cards(store)
    site_card_paths = {route: page_card_path(route, card) for route, card in site_cards.items()}
    social_cards.update({site_card_paths[route]: card for route, card in site_cards.items()})
    app.state.social_cards = social_cards
    social_by_key = {path.rsplit("/", 1)[0]: path for path in social_cards}
    if assets.is_dir():
        api.mount("/static", StaticFiles(directory=assets), name="static")

    def url(path: str) -> str:
        return prefix + (path if path.startswith("/") else "/" + path)

    def absolute(path: str) -> str:
        return store.config["siteUrl"] + url(path)

    def preserve_query(request: Request, target: str) -> str:
        query = quote_from_bytes(request.scope["query_string"], safe="!$&'()*+,-./:;=?@_~%[]")
        return target + ("?" + query if query else "")

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        host = request.headers.get("host", "").partition(":")[0].lower().rstrip(".")
        if host in host_aliases and request.url.path != url("/healthz"):
            raw_path = quote_from_bytes(
                request.scope.get("raw_path", b""), safe="!$&'()*+,-./:;=@_~%"
            ) or request.url.path
            target = store.config["siteUrl"] + raw_path
            response = RedirectResponse(preserve_query(request, target), status_code=308)
        else:
            response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        # Fly terminates TLS before the app. Derive the policy from the configured
        # public HTTPS origin, not arbitrary forwarded headers. Browsers ignore HSTS over HTTP.
        if store.config["siteUrl"].startswith("https://"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; script-src 'self' {theme_hash}; style-src 'self' {style_hashes}; "
            "img-src 'self' https: data:; "
            "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if request.url.path.startswith(url("/static/")):
            name = request.url.path.removeprefix(url("/static/"))
            version = request.query_params.get("v")
            fingerprint_matches = version is not None and version == asset_versions.get(name)
            response.headers["Cache-Control"] = (
                "public, max-age=31536000, immutable"
                if response.status_code in {200, 304} and fingerprint_matches else "no-cache"
            )
        elif "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = "no-cache"
        return response

    def context(
        request: Request,
        lang: str,
        route: str,
        title: str,
        page_type: str,
        alternates: dict | None = None,
        description: str = "",
        **extra,
    ):
        localized = store.localized(lang)
        raw_alternates = alternates or {}
        about_address = absolute(store.about[lang].url)
        publisher = {
            "@type": "Person",
            "@id": about_address + "#publisher",
            "name": localized.get("author", "") or localized.get("siteTitle", ""),
            "url": about_address,
        }
        website_id = absolute(HOME[lang]) + "#website"
        data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": localized.get("siteTitle", ""),
            "url": absolute(HOME[lang]),
            "description": localized.get("siteDescription", ""),
            "inLanguage": lang,
        }
        share_image = None
        generated_image = False
        share_alt = ""
        if route in site_cards and page_type != "error":
            card = site_cards[route]
            share_image = absolute(site_card_paths[route])
            generated_image = True
            share_alt = f"{card.title} — {card.subtitle if card.home else card.identity}"
            description = card.description
            data.update({"name": title, "url": absolute(route), "description": description, "image": share_image})
            if page_type == "home":
                data.update({"@id": website_id, "publisher": publisher})
            else:
                data.update({"@type": "WebPage", "isPartOf": {"@id": website_id}})
                if absolute(route) == about_address:
                    data.update({"@type": "AboutPage", "mainEntity": publisher})
        if page_type == "post":
            post = extra["post"]
            generated_image = not post.image
            share_image = post.image or absolute(card_path(post, store.config))
            if share_image.startswith("/"):
                share_image = absolute(share_image)
            data = {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": post.title,
                "description": post.excerpt,
                "inLanguage": lang,
                "datePublished": post.date,
                "dateModified": post.updated,
                "mainEntityOfPage": {"@type": "WebPage", "@id": absolute(route)},
                "publisher": publisher,
                "isPartOf": {"@id": website_id},
                "keywords": post.tags,
            }
            data["image"] = share_image
            share_alt = f"{post.title} — {localized.get('siteTitle', '')}"
        localized_posts = store.for_language(lang)
        labels = LABELS[lang]
        return {
            "request": request,
            "config": localized,
            "labels": labels,
            "lang": lang,
            "page_type": page_type,
            "title": title,
            "document_title": (localized.get("siteSubtitle") or title) if page_type == "home" else title,
            "description": description or localized.get("siteDescription", ""),
            "canonical": absolute(route),
            "alternates": {key: absolute(value) for key, value in raw_alternates.items()},
            "home_url": url(HOME[lang]),
            "search_url": url(route),
            "about_url": url(store.about[lang].url),
            "feed_url": url(FEED[lang]),
            "privacy_url": url("/privacy/"),
            "articles_url": url("/articles/"),
            "tags_url": url("/tags/"),
            "sitemap_url": url("/sitemap.xml"),
            "base_path": prefix,
            "asset_url": asset_url,
            "styles": styles,
            "theme_boot": theme_boot.decode(),
            "entry_id": lambda slug: f"entry:{slug}" if slug in ENTRY_ID_CONFLICTS else slug,
            "llms_url": url("/llms.txt"),
            "catalog_url": url("/.well-known/ai-catalog.json"),
            "ard_url": url("/.well-known/ard.json"),
            "share_image": share_image,
            "share_alt": share_alt,
            "generated_image": generated_image,
            "share_width": WIDTH,
            "share_height": HEIGHT,
            "year": datetime.now(UTC).year,
            "static_export": static_export,
            "json_ld": json.dumps(data, ensure_ascii=False, indent=2).replace("<", "\\u003c"),
            "url": url,
            "tag_url": lambda tag: url(TAG_PREFIX[lang] + store.tags[lang][tag] + "/"),
            "all_posts": localized_posts,
            "tags": [
                {
                    "name": name,
                    "slug": value,
                    "url": url(TAG_PREFIX[lang] + value + "/"),
                    "count": sum(name in post.tags for post in localized_posts),
                }
                for name, value in sorted(store.tags[lang].items())
            ],
            "q": "",
            "tag": "",
            "noindex": False,
            **extra,
        }

    def html(request, template, data, status_code=200, headers=None):
        headers = dict(headers or {})
        if data["noindex"]:
            headers["X-Robots-Tag"] = "noindex, follow"
        if data["page_type"] == "home" and template != "_posts.html":
            headers["Link"] = f'<{absolute("/.well-known/ai-catalog.json")}>; rel="ai-catalog"'
        content = data.get("post") or data.get("page")
        markdown_available = content is None or content.markdown is not None
        if not static_export and status_code == 200 and markdown_available and data["canonical"] != absolute("/privacy/"):
            headers["Vary"] = ", ".join(filter(None, (headers.get("Vary"), "Accept")))
            if template != "_posts.html" and wants_markdown(request.headers.get("accept", "")):
                headers["Link"] = ", ".join(filter(None, (
                    headers.get("Link"), f'<{data["canonical"]}>; rel="canonical"'
                )))
                return Response(render_document(data, absolute), media_type="text/markdown", headers=headers)
        return templates.TemplateResponse(
            request=request, name=template, context=data, status_code=status_code, headers=headers
        )

    @api.api_route("/healthz", methods=["GET", "HEAD"], include_in_schema=False)
    def health():
        return JSONResponse({"status": "ok"})

    @api.api_route(
        "/{route:path}", methods=["GET", "HEAD"], response_class=HTMLResponse, include_in_schema=False
    )
    def page(request: Request, route: str):
        path = "/" + route
        if route in ICONS:
            icon = source / route
            # Alternate sources that predate the raster icons can use the site's defaults.
            if route != "favicon.svg" and not icon.is_file():
                icon = ROOT / "src" / route
            return FileResponse(icon, media_type=ICONS[route])
        card_route = path if path in social_cards else None
        if card_route is None and (match := re.fullmatch(r"(/social/(?:[a-z0-9-]+/)*[a-z0-9-]+)/[a-f0-9]{20}\.png", path)):
            # A crawler may have cached the previous HTML before an edit/deploy.
            # Only still-public pages qualify; stale URLs must never be immutable.
            card_route = social_by_key.get(match[1])
        if card_route:
            etag = '"' + card_route.rsplit("/", 1)[-1].removesuffix(".png") + '"'
            cache = "public, max-age=31536000, immutable" if card_route == path else "no-cache"
            headers = {"Cache-Control": cache, "ETag": etag}
            validators = [
                value.strip().removeprefix("W/")
                for value in request.headers.get("if-none-match", "").split(",")
            ]
            if etag in validators or "*" in validators:
                return Response(status_code=304, headers=headers)
            return Response(render_card(social_cards[card_route]), media_type="image/png", headers=headers)
        entry = store.routes.get(path)
        lang = "en"
        if entry is None:
            if not path.endswith("/") and path + "/" in store.routes:
                return RedirectResponse(preserve_query(request, url(path + "/")), status_code=308)
            data = context(request, lang, path, LABELS[lang]["notFound"], "error", noindex=True)
            return html(request, "error.html", data, 404)
        kind, value = entry
        if kind == "redirect":
            return RedirectResponse(
                preserve_query(request, url(value)), status_code=308
            )
        if kind == "feed":
            return Response(render_feed(store, value, absolute), media_type="application/rss+xml")
        if kind == "sitemap":
            return Response(render_sitemap(store, absolute), media_type="application/xml")
        if kind == "llms":
            return Response(
                render_llms(store, absolute, markdown_available=not static_export), media_type="text/plain"
            )
        if kind == "catalog":
            return JSONResponse(render_catalog(store, absolute), media_type="application/ai-catalog+json")
        if kind == "robots":
            return Response(
                f"User-agent: *\nAllow: /\nSitemap: {absolute('/sitemap.xml')}\n", media_type="text/plain"
            )
        if kind == "tags":
            data = context(request, "en", path, "Topics", "tag_index")
            return html(request, "tags.html", data)
        if kind in {"home", "articles"}:
            lang = value
            q = request.query_params.get("q", "").strip()[:200]
            tag = request.query_params.get("tag", "").strip()[:100]
            posts = store.for_language(lang)
            if q:
                needle = q.casefold()
                posts = [
                    post
                    for post in posts
                    if needle in " ".join([post.title, post.excerpt, post.search_text, *post.tags]).casefold()
                ]
            if tag:
                posts = [
                    post
                    for post in posts
                    if tag in post.tags or any(store.tags[lang][name] == tag for name in post.tags)
                ]
            data = context(
                request,
                lang,
                path,
                store.config.get("siteTitle", "") if kind == "home" else "Writing",
                "home" if kind == "home" else "articles",
                {},
                posts=posts,
                result_count=len(posts),
                q=q,
                tag=tag,
                noindex=bool(q or tag),
            )
            partial = (
                request.headers.get("HX-Request") == "true"
                and request.headers.get("HX-History-Restore-Request") != "true"
            )
            return html(
                request,
                "_posts.html" if partial else ("home.html" if kind == "home" else "articles.html"),
                data,
                headers={"Vary": "HX-Request, HX-History-Restore-Request"},
            )
        if kind == "post":
            post = value
            data = context(
                request,
                post.lang,
                path,
                post.title,
                "post",
                post.alternates,
                post.excerpt,
                post=post,
            )
            return html(request, "post.html", data)
        if kind == "tag":
            lang, name = value
            alternates = {
                code: TAG_PREFIX[code] + store.tags[code][name] + "/"
                for code in LANGUAGES
                if name in store.tags[code]
            }
            posts = [post for post in store.for_language(lang) if name in post.tags]
            title = site_cards[path].title
            data = context(
                request, lang, path, title, "tag", alternates, posts=posts, result_count=len(posts), tag=name
            )
            return html(request, "tag.html", data)
        page = value
        alternates = (
            {code: store.about[code].url for code in LANGUAGES} if page in store.about.values() else {}
        )
        data = context(
            request,
            page.lang,
            path,
            page.title,
            "page",
            alternates,
            page.description,
            content_html=page.html,
            page=page,
        )
        return html(request, "page.html", data)

    if prefix:
        app.mount(prefix, api)
    return app


def render_sitemap(store: ContentStore, absolute) -> str:
    urls = []
    for route, (kind, value) in store.routes.items():
        if kind not in {"home", "articles", "tags", "post", "page", "tag"}:
            continue
        lastmod = ""
        if kind == "post":
            updated = date_value(value.updated).isoformat() if "T" in value.updated else value.updated
            lastmod = f"<lastmod>{escape(updated)}</lastmod>"
        urls.append(f"<url><loc>{escape(absolute(route))}</loc>{lastmod}</url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "\n".join(urls)
        + "</urlset>"
    )


def render_feed(store: ContentStore, lang: str, absolute) -> str:
    config = store.localized(lang)
    items = []
    for post in store.for_language(lang):
        address = escape(absolute(post.url))
        items.append(
            f"<item><title>{escape(post.title)}</title><link>{address}</link><guid>{address}</guid>"
            f"<pubDate>{format_datetime(date_value(post.date))}</pubDate><description>{escape(post.excerpt)}</description></item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
        f"<title>{escape(config.get('siteTitle', ''))}</title><link>{escape(absolute(HOME[lang]))}</link>"
        f"<description>{escape(config.get('siteDescription', ''))}</description><language>{lang}</language>"
        + "\n".join(items)
        + "</channel></rss>"
    )


app = create_app()
