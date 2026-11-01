"""Server-rendered English blog; HTMX enhances an ordinary GET search form."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
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
from blog.social import HEIGHT, WIDTH, card_content, card_path, page_card_path, page_cards, render_card

ROOT = Path(__file__).resolve().parents[1]
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
        "topic": "Topic",
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
    templates = Jinja2Templates(directory=str(ROOT / "blog" / "templates"))
    templates.env.filters["format_date"] = format_date
    asset_digest = hashlib.sha256()
    if assets.is_dir():
        for item in sorted(assets.rglob("*")):
            if item.is_file():
                asset_digest.update(item.relative_to(assets).as_posix().encode())
                asset_digest.update(item.read_bytes())
    asset_version = asset_digest.hexdigest()[:12]
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

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' https: data:; "
            "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if request.url.path.startswith(url("/static/")):
            response.headers["Cache-Control"] = (
                "public, max-age=31536000, immutable" if request.url.query else "public, max-age=3600"
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
            share_alt = f"{card.title} — {card.identity}"
            description = card.description
            data.update({"name": title, "url": absolute(route), "description": description, "image": share_image})
            if page_type != "home":
                data["@type"] = "WebPage"
        if page_type == "post":
            post = extra["post"]
            generated_image = not post.image
            share_image = post.image or absolute(card_path(post, store.config))
            if share_image.startswith("/") and not share_image.startswith("//"):
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
                "author": {"@type": "Person", "name": localized.get("author", "")},
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
            "asset_version": asset_version,
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
        return templates.TemplateResponse(
            request=request, name=template, context=data, status_code=status_code, headers=headers
        )

    @api.api_route("/healthz", methods=["GET", "HEAD"], include_in_schema=False)
    def health():
        return JSONResponse({"status": "ok"})

    @api.api_route("/favicon.svg", methods=["GET", "HEAD"], include_in_schema=False)
    def favicon():
        return Response((source / "favicon.svg").read_bytes(), media_type="image/svg+xml")

    @api.api_route(
        "/{route:path}", methods=["GET", "HEAD"], response_class=HTMLResponse, include_in_schema=False
    )
    def page(request: Request, route: str):
        path = "/" + route
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
                return RedirectResponse(url(path + "/"), status_code=308)
            data = context(request, lang, path, LABELS[lang]["notFound"], "error", noindex=True)
            return html(request, "error.html", data, 404)
        kind, value = entry
        if kind == "redirect":
            return RedirectResponse(
                url(value) + ("?" + request.url.query if request.url.query else ""), status_code=308
            )
        if kind == "feed":
            return Response(render_feed(store, value, absolute), media_type="application/rss+xml")
        if kind == "sitemap":
            return Response(render_sitemap(store, absolute), media_type="application/xml")
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
            posts = store.for_language(post.lang)
            index = posts.index(post)
            data = context(
                request,
                post.lang,
                path,
                post.title,
                "post",
                post.alternates,
                post.excerpt,
                post=post,
                previous_post=posts[index - 1] if index else None,
                next_post=posts[index + 1] if index + 1 < len(posts) else None,
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
            title = f"{LABELS[lang]['topic']}: {name}"
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
        urls.append(f"<url><loc>{escape(absolute(route))}</loc></url>")
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
