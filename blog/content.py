"""Validate the entire public content graph before exposing any route.

Only data-only YAML/JSON is accepted. Markdown HTML remains escaped, and drafts
are removed before routes, language counterparts, tags, or feeds are constructed.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from markdown_it import MarkdownIt
from markupsafe import Markup

LANGUAGES = ("en",)
HOME = {"en": "/"}
POST_PREFIX = {"en": "/articles/"}
TAG_PREFIX = {"en": "/tags/"}
FEED = {"en": "/rss.xml"}


class ContentError(ValueError):
    """Content cannot safely be published."""


def unique_pairs(pairs):
    mapping = {}
    for key, value in pairs:
        if key in mapping:
            raise ContentError(f"Duplicate metadata key: {key}")
        mapping[key] = value
    return mapping


class UniqueSafeLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        pairs = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise ContentError("Front matter keys must be strings")
            pairs.append((key, self.construct_object(value_node, deep=deep)))
        return unique_pairs(pairs)


def slug(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ContentError(f"Invalid {label}: {value}")
    return value


def tag_slug(value: str) -> str:
    value = value.lower().strip().translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}))
    return slug(re.sub(r"[^a-z0-9-]", "", re.sub(r"\s+", "-", value)), "tag slug")


def normalize_base_path(value: str | None) -> str:
    value = str(value or "").strip().strip("/")
    if not value:
        return ""
    if any(not re.fullmatch(r"[a-zA-Z0-9_-]+", part) for part in value.split("/")):
        raise ContentError("Invalid basePath")
    return "/" + value


def parse_matter(raw: str) -> tuple[dict, str]:
    raw = raw.lstrip("\ufeff")
    lines = raw.splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return {}, raw
    first = lines[0].strip()
    if first not in {"---", "---yaml", "---json"}:
        raise ContentError("Only YAML or JSON front matter is allowed")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ContentError("Unclosed front matter")
    try:
        value = (
            json.loads("".join(lines[1:end]), object_pairs_hook=unique_pairs)
            if first == "---json"
            else yaml.load("".join(lines[1:end]), Loader=UniqueSafeLoader)
        )
    except (ValueError, yaml.YAMLError) as exc:
        raise ContentError(f"Invalid front matter: {exc}") from exc
    if value is None:
        value = {}
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ContentError("Front matter must be a mapping with string keys")
    return value, "".join(lines[end + 1 :])


def parse_date(value: object, label: str) -> str:
    if not isinstance(value, (str, date, datetime)):
        raise ContentError(label)
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError as exc:
        raise ContentError(label) from exc
    return parsed.date().isoformat() if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)) else parsed.isoformat()


def date_value(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed


def format_date(value: str, lang: str = "en") -> str:
    parsed = date_value(value)
    return parsed.strftime("%d %b %Y")


def visible_text(html: str) -> str:
    class TextParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []

        def handle_data(self, data):
            self.parts.append(data)

    parser = TextParser()
    parser.feed(str(html))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def render_markdown(body: str) -> tuple[Markup, list[dict]]:
    md = MarkdownIt("default", {"html": False, "breaks": False, "linkify": True})
    tokens = md.parse(body)
    toc = []
    used = set()
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        inline = tokens[index + 1]
        title = "".join(
            child.content for child in (inline.children or []) if child.type in {"text", "code_inline"}
        )
        heading_id = re.sub(r"[^\w-]", "", re.sub(r"\s+", "-", title.lower()), flags=re.UNICODE) or "section"
        unique = heading_id
        suffix = 2
        while unique in used:
            unique = f"{heading_id}-{suffix}"
            suffix += 1
        used.add(unique)
        token.attrSet("id", unique)
        level = int(token.tag[1])
        if 2 <= level <= 3:
            toc.append({"id": unique, "title": title, "level": level})
    return Markup(md.renderer.render(tokens, md.options, {})), toc


@dataclass
class Post:
    slug: str
    lang: str
    title: str
    date: str
    updated: str
    tags: list[str]
    excerpt: str
    read_time: int
    html: Markup
    toc: list[dict]
    url: str
    translation_key: str | None = None
    image: str | None = None
    alternates: dict[str, str] = field(default_factory=dict)

    @property
    def search_text(self) -> str:
        return visible_text(self.html)

    @property
    def date_label(self) -> str:
        return format_date(self.date, self.lang)


@dataclass
class Page:
    title: str
    description: str
    url: str
    html: Markup
    lang: str


@dataclass
class ContentStore:
    config: dict
    posts: list[Post]
    about: dict[str, Page]
    privacy: Page
    tags: dict[str, dict[str, str]]
    routes: dict[str, tuple[str, object]]

    def localized(self, lang: str) -> dict:
        return {**self.config, "language": "en"}

    def for_language(self, lang: str) -> list[Post]:
        return sorted(
            (post for post in self.posts if post.lang == lang),
            key=lambda p: (-date_value(p.date).timestamp(), p.slug),
        )


def load_content(source_dir: str | Path) -> ContentStore:
    source = Path(source_dir)
    try:
        config = json.loads((source / "config.json").read_text())
    except (OSError, ValueError) as exc:
        raise ContentError(f"Invalid site configuration: {exc}") from exc
    if not isinstance(config, dict):
        raise ContentError("Site configuration must be an object")
    site_url = str(config.get("siteUrl", "")).rstrip("/")
    parsed_url = urlsplit(site_url)
    if (
        re.search(r"[\s<>\"'\\]", site_url)
        or parsed_url.username is not None
        or parsed_url.password is not None
        or parsed_url.scheme not in {"http", "https"}
        or not parsed_url.netloc
        or parsed_url.query
        or parsed_url.fragment
        or parsed_url.path
    ):
        raise ContentError("siteUrl must be an absolute HTTP(S) origin")
    config["siteUrl"] = site_url
    config["basePath"] = normalize_base_path(config.get("basePath"))
    about = {}
    routes = {}

    def add(route, kind, value):
        if route in routes:
            raise ContentError(f"Duplicate output route: {route}")
        routes[route] = (kind, value)

    def page(filename, lang, route, fallback):
        metadata, body = parse_matter((source / filename).read_text())
        html, _ = render_markdown(body)
        return Page(
            str(metadata.get("title", fallback)), str(metadata.get("description", "")), route, html, lang
        )

    for lang in LANGUAGES:
        filename = "about.md"
        metadata, _ = parse_matter((source / filename).read_text())
        about_slug = slug(metadata.get("slug", "about"), "about slug")
        about[lang] = page(
            filename,
            lang,
            f"{HOME[lang]}{about_slug}/",
            "About this blog",
        )
        add(HOME[lang], "home", lang)
        add(about[lang].url, "page", about[lang])
        add(FEED[lang], "feed", lang)
    privacy = page("privacy.md", "en", "/privacy/", "Privacy")
    add(privacy.url, "page", privacy)
    add("/articles/", "articles", "en")
    add("/tags/", "tags", "en")
    for legacy, target in {
        "/en/": "/",
        "/en/articles/": "/articles/",
        "/en/tags/": "/tags/",
        "/en/about/": "/about/",
        "/en/privacy/": "/privacy/",
        "/en/rss.xml": "/rss.xml",
        "/ueber-mich/": "/about/",
        "/datenschutz/": "/privacy/",
    }.items():
        add(legacy, "redirect", target)
    add("/sitemap.xml", "sitemap", None)
    add("/robots.txt", "robots", None)
    add("/llms.txt", "llms", None)
    add("/.well-known/ai-catalog.json", "catalog", None)
    add("/.well-known/ard.json", "catalog", None)
    posts = []
    pairs = {}
    tags = {lang: {} for lang in LANGUAGES}
    for path in sorted((source / "posts").glob("*.md")):
        meta, body = parse_matter(path.read_text())
        if "draft" in meta and not isinstance(meta["draft"], bool):
            raise ContentError(f"draft must be true or false: {path.name}")
        if meta.get("draft") is True:
            continue
        lang = meta.get("lang", "en")
        if lang == "de":
            continue
        if lang not in LANGUAGES:
            raise ContentError(f"Unsupported lang in {path.name}: {lang}")
        post_slug = slug(meta.get("slug", path.stem), "post slug")
        published = parse_date(
            meta.get("date", datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()),
            f"Valid date required: {path.name}",
        )
        updated = parse_date(meta.get("updated", published), f"Invalid updated date: {path.name}")
        if not isinstance(meta.get("tags", []), list) or any(
            not isinstance(tag, str) for tag in meta.get("tags", [])
        ):
            raise ContentError(f"tags must be an array of strings: {path.name}")
        post_tags = list(dict.fromkeys(tag.strip() for tag in meta.get("tags", []) if tag.strip()))
        html, toc = render_markdown(body)
        plain = re.sub(r"[#>*_`~\[\]()]", " ", re.sub(r"```[\s\S]*?```", " ", body))
        post = Post(
            post_slug,
            lang,
            str(meta.get("title", post_slug)),
            published,
            updated,
            post_tags,
            str(meta.get("excerpt", meta.get("description", visible_text(html)[:140]))),
            max(1, math.floor(len(plain.split()) / 220 + 0.5)),
            html,
            toc,
            f"{POST_PREFIX[lang]}{post_slug}/",
            image=str(meta["image"]) if meta.get("image") else None,
        )
        add(post.url, "post", post)
        add(f"/en/articles/{post_slug}/", "redirect", post.url)
        if "translationKey" in meta:
            key = slug(meta["translationKey"], "translationKey")
            if lang in pairs.setdefault(key, {}):
                raise ContentError(f"Duplicate translationKey {key} for {lang}")
            pairs[key][lang] = post
            post.translation_key = key
        posts.append(post)
        for tag in post_tags:
            tag_value = tag_slug(tag)
            if any(other != tag and value == tag_value for other, value in tags[lang].items()):
                raise ContentError(f"Tag slug collision: {tag}")
            tags[lang][tag] = tag_value
    for lang, language_tags in tags.items():
        for name, value in language_tags.items():
            add(f"{TAG_PREFIX[lang]}{value}/", "tag", (lang, name))
            add(f"/en/tags/{value}/", "redirect", f"{TAG_PREFIX[lang]}{value}/")
    return ContentStore(config, posts, about, privacy, tags, routes)
